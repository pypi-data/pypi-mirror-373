////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2024, CryptoLab Inc. All rights reserved.                    //
//                                                                            //
// This software and/or source code may be commercially used and/or           //
// disseminated only with the written permission of CryptoLab Inc,            //
// or in accordance with the terms and conditions stipulated in the           //
// agreement/contract under which the software and/or source code has been    //
// supplied by CryptoLab Inc. Any unauthorized commercial use and/or          //
// dissemination of this file is strictly prohibited and will constitute      //
// an infringement of copyright.                                              //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////
#pragma once

#include "EVI/Basic.cuh"
#include "EVI/Const.hpp"
#include "utils/CheckMacros.hpp"

#include <cuda_runtime_api.h>

namespace evi {

static void revertOrderCpy(u64 *dst, const u64 *src) {

    const u64 *curr_ptr = src + 1;
    for (u64 size_to_copy = DEGREE / 2; size_to_copy > 0; size_to_copy /= 2) {
        CUDACHECK(cudaMemcpyAsync(dst + size_to_copy, curr_ptr, size_to_copy * sizeof(u64), cudaMemcpyHostToDevice));
        curr_ptr += size_to_copy;
    }
    cudaDeviceSynchronize();
}

static void setTwiddleFactor(const u64 prime, const u64 psi, u64 *w_gpu, u64 *w_shoup_gpu, u64 *inv_w_gpu,
                             u64 *inv_w_shoup_gpu) {
    {
        u64 w_factor[DEGREE], w_shoup[DEGREE], inv_w[DEGREE], inv_w_shoup[DEGREE], tmp_inv_w[DEGREE];
        auto mult_with_barr = [](u64 x, u64 y, u64 y_barr, u64 prime) {
            u64 res = mulModLazy(x, y, y_barr, prime);
            return res >= prime ? res - prime : res;
        };
        u64 psi_square = mulModSimple(psi, psi, prime);
        u64 psi_square_barr = divide128By64Lo(psi_square, 0, prime);
        u64 psi_inv = powModSimple(psi, prime - 2, prime);
        w_factor[0] = 1;
        tmp_inv_w[0] = 1;

        u64 idx = 0;
        u64 previdx = 0;
        u64 max_digits = LOG_DEGREE;
        u64 psi_barr = divide128By64Lo(psi, 0, prime);
        u64 psi_inv_barr = divide128By64Lo(psi_inv, 0, prime);
        for (u64 i = 1; i < DEGREE; ++i) {
            idx = bitReverse(i, max_digits);
            w_factor[idx] = mult_with_barr(w_factor[previdx], psi, psi_barr, prime);
            tmp_inv_w[idx] = mult_with_barr(tmp_inv_w[previdx], psi_inv, psi_inv_barr, prime);
            previdx = idx;
        }
        inv_w[0] = tmp_inv_w[0];
        idx = 1;
        for (u64 m = (DEGREE >> 1); m > 0; m >>= 1) {
            for (u64 i = 0; i < m; i++) {
                inv_w[idx] = tmp_inv_w[m + i];
                idx++;
            }
        }
        for (u64 i = 0; i < DEGREE; ++i) {
            w_shoup[i] = divide128By64Lo(w_factor[i], 0, prime);
            inv_w_shoup[i] = divide128By64Lo(inv_w[i], 0, prime);
        }
        CUDACHECK(cudaMemcpyAsync(w_gpu, w_factor, U64_DEGREE, cudaMemcpyHostToDevice));
        CUDACHECK(cudaMemcpyAsync(w_shoup_gpu, w_shoup, U64_DEGREE, cudaMemcpyHostToDevice));

        revertOrderCpy(inv_w_gpu, inv_w);
        revertOrderCpy(inv_w_shoup_gpu, inv_w_shoup);
    }
}

// Assumes input a, b < 4p. Outputs a, b < 4p.
__device__ __inline__ static void buttNttLocal(u64 &a, u64 &b, const u64 w, const u64 w_shoup, const u64 p,
                                               const u64 two_p) {
    u64 large_u = mulModLazy(b, w, w_shoup, p);
    if (a >= two_p)
        a -= two_p;
    b = a + (two_p - large_u);
    a += large_u;
}

template <u32 size, u32 step>
__device__ __inline__ static void buttNttBlock(u64 *local, const u64 *large_w, const u64 *large_w_shoup, const u64 idx,
                                               const u64 p1, const u64 p2) {
#pragma unroll
    for (u32 i = step; i > 0; --i) {
#pragma unroll
        for (u32 j = 0; j < (size >> i); ++j) {
#pragma unroll
            for (u32 k = 0; k < (1U << (i - 1)); ++k) {
                buttNttLocal(local[j * (1U << i) + k], local[j * (1U << i) + k + (1U << (i - 1))],
                             large_w[(idx << (step - i)) + j], large_w_shoup[(idx << (step - i)) + j], p1, p2);
            }
        }
    }
}

template <u64 prime, u64 two_prime, u32 tail>
__global__ static void nttPhase1Kernel(const u64 *input, u64 *out, const u64 *large_w, const u64 *large_w_shoup) {
    extern __shared__ u64 temp[]; // NOLINT
    const u32 &poly_idx = blockIdx.x;
    const u32 degree_idx = blockIdx.y * blockDim.x + threadIdx.x;
    u64 local[THREAD_NTT_SIZE];
    size_t idx = poly_idx * DEGREE + DEGREE_PER_SIZE / FIRST_PER_THREAD_RADIX * threadIdx.x +
                 degree_idx / FIRST_PER_THREAD_RADIX;
    input += idx;
    out += idx;
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        local[j] = input[DEGREE_PER_SIZE * j]; // NOLINT
    }
    __syncthreads();
    buttNttBlock<THREAD_NTT_SIZE, LOG_THREAD_NTT_SIZE>(local, large_w, large_w_shoup, 1, prime, two_prime);
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        temp[threadIdx.x + FIRST_PER_THREAD_RADIX * j] = local[j];
    }
    __syncthreads();
#pragma unroll
    for (u32 j = THREAD_NTT_SIZE, k = FIRST_PER_THREAD_RADIX; j <= FIRST_PER_THREAD_RADIX;
         j <<= LOG_THREAD_NTT_SIZE, k >>= LOG_THREAD_NTT_SIZE) {
        u32 m_idx = threadIdx.x / (k >> LOG_THREAD_NTT_SIZE);
        u32 t_idx = threadIdx.x & ((k >> LOG_THREAD_NTT_SIZE) - 1);
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            local[l] = temp[m_idx * k + t_idx + (k >> LOG_THREAD_NTT_SIZE) * l];
        }
        buttNttBlock<THREAD_NTT_SIZE, LOG_THREAD_NTT_SIZE>(local, large_w, large_w_shoup, j + m_idx, prime, two_prime);
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            temp[m_idx * k + t_idx + (k >> LOG_THREAD_NTT_SIZE) * l] = local[l];
        }
        __syncthreads();
    }
    if constexpr (tail > 0) {
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            local[l] = temp[(threadIdx.x << LOG_THREAD_NTT_SIZE) + l];
        }
        buttNttBlock<THREAD_NTT_SIZE, tail>(local, large_w, large_w_shoup,
                                            (FIRST_PER_THREAD_RADIX + threadIdx.x) << (LOG_THREAD_NTT_SIZE - tail),
                                            prime, two_prime);
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            temp[(threadIdx.x << LOG_THREAD_NTT_SIZE) + l] = local[l];
        }
        __syncthreads();
    }
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        out[DEGREE_PER_SIZE * j] = // NOLINT
            temp[threadIdx.x + FIRST_PER_THREAD_RADIX * j];
    }
}

template <u64 prime, u64 two_prime, u32 tail>
__global__ static void nttPhase2Kernel(u64 *op, const u64 *large_w, const u64 *large_w_shoup) {
    extern __shared__ u64 temp[]; // NOLINT
    const u32 &poly_idx = blockIdx.x;

    const u32 degree_idx = blockIdx.y * blockDim.x + threadIdx.x;

    constexpr u32 T = DEGREE / FIRST_RADIX;
    // i'th block
    const u32 m_idx = degree_idx / (T >> LOG_THREAD_NTT_SIZE);
    const u32 t_idx = degree_idx % (T >> LOG_THREAD_NTT_SIZE);

    u64 *a_np = op + poly_idx * DEGREE + m_idx * T + t_idx;
    u64 local[THREAD_NTT_SIZE];
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        local[j] = a_np[(T >> LOG_THREAD_NTT_SIZE) * j]; // NOLINT
    }
    const u32 tw_idx = FIRST_RADIX + m_idx;
    buttNttBlock<THREAD_NTT_SIZE, LOG_THREAD_NTT_SIZE>(local, large_w, large_w_shoup, tw_idx, prime, two_prime);
    const u32 set = (threadIdx.x / SECOND_PER_THREAD_RADIX) << LOG_THREAD_NTT_SIZE;
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        temp[set * SECOND_PER_THREAD_RADIX + t_idx + (T >> LOG_THREAD_NTT_SIZE) * j] = local[j];
    }
    __syncthreads();
#pragma unroll
    for (u32 j = THREAD_NTT_SIZE, k = T >> LOG_THREAD_NTT_SIZE; j <= (T >> LOG_THREAD_NTT_SIZE);
         j <<= LOG_THREAD_NTT_SIZE, k >>= LOG_THREAD_NTT_SIZE) {
        u32 m_idx2 = t_idx / (k >> LOG_THREAD_NTT_SIZE);
        u32 t_idx2 = t_idx & ((k >> LOG_THREAD_NTT_SIZE) - 1);
        for (u32 l = 0; l < THREAD_NTT_SIZE; l++) {
            local[l] = temp[set * SECOND_PER_THREAD_RADIX + m_idx2 * k + t_idx2 + (k >> LOG_THREAD_NTT_SIZE) * l];
        }
        buttNttBlock<THREAD_NTT_SIZE, LOG_THREAD_NTT_SIZE>(local, large_w, large_w_shoup, j * tw_idx + m_idx2, prime,
                                                           two_prime);
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            temp[set * SECOND_PER_THREAD_RADIX + m_idx2 * k + t_idx2 + (k >> LOG_THREAD_NTT_SIZE) * l] = local[l];
        }
        __syncthreads();
    }
    if constexpr (tail > 0) {
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            local[l] = temp[set * SECOND_PER_THREAD_RADIX + (t_idx << LOG_THREAD_NTT_SIZE) + l];
        }
        buttNttBlock<THREAD_NTT_SIZE, tail>(local, large_w, large_w_shoup,
                                            (T * tw_idx + (t_idx << LOG_THREAD_NTT_SIZE)) >> tail, prime, two_prime);
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            temp[set * SECOND_PER_THREAD_RADIX + (t_idx << LOG_THREAD_NTT_SIZE) + l] = local[l];
        }
        __syncthreads();
    }
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        local[j] = temp[set * SECOND_PER_THREAD_RADIX + t_idx + static_cast<size_t>((T >> LOG_THREAD_NTT_SIZE) * j)];
        local[j] = local[j] >= two_prime ? local[j] - two_prime : local[j];
        a_np[(T >> LOG_THREAD_NTT_SIZE) * j] = // NOLINT
            local[j] >= prime ? local[j] - prime : local[j];
    }
}

template <u64 prime, u64 two_prime, u64 prod_inv, u32 tail>
__global__ static void modDownKernel(u64 *op, u64 *poly_q, const u64 *large_w, const u64 *large_w_shoup) {
    extern __shared__ u64 temp[]; // NOLINT
    const u32 &poly_idx = blockIdx.x;

    const u32 degree_idx = blockIdx.y * blockDim.x + threadIdx.x;

    constexpr u32 T = DEGREE / FIRST_RADIX;
    // i'th block
    const u32 m_idx = degree_idx / (T >> LOG_THREAD_NTT_SIZE);
    const u32 t_idx = degree_idx & ((T >> LOG_THREAD_NTT_SIZE) - 1);

    u64 *a_np = op + poly_idx * DEGREE + m_idx * T + t_idx;
    u64 local[THREAD_NTT_SIZE];
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        local[j] = a_np[(T >> LOG_THREAD_NTT_SIZE) * j]; // NOLINT
    }
    const u32 tw_idx = FIRST_RADIX + m_idx;
    buttNttBlock<THREAD_NTT_SIZE, LOG_THREAD_NTT_SIZE>(local, large_w, large_w_shoup, tw_idx, prime, two_prime);
    const u32 set = (threadIdx.x / SECOND_PER_THREAD_RADIX) << LOG_THREAD_NTT_SIZE;
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        temp[set * SECOND_PER_THREAD_RADIX + t_idx + (T >> LOG_THREAD_NTT_SIZE) * j] = local[j];
    }
    __syncthreads();
#pragma unroll
    for (u32 j = THREAD_NTT_SIZE, k = T >> LOG_THREAD_NTT_SIZE; j <= (T >> LOG_THREAD_NTT_SIZE);
         j <<= LOG_THREAD_NTT_SIZE, k >>= LOG_THREAD_NTT_SIZE) {
        u32 m_idx2 = t_idx / (k >> LOG_THREAD_NTT_SIZE);
        u32 t_idx2 = t_idx & ((k >> LOG_THREAD_NTT_SIZE) - 1);
        for (u32 l = 0; l < THREAD_NTT_SIZE; l++) {
            local[l] = temp[set * SECOND_PER_THREAD_RADIX + m_idx2 * k + t_idx2 + (k >> LOG_THREAD_NTT_SIZE) * l];
        }
        buttNttBlock<THREAD_NTT_SIZE, LOG_THREAD_NTT_SIZE>(local, large_w, large_w_shoup, j * tw_idx + m_idx2, prime,
                                                           two_prime);
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            temp[set * SECOND_PER_THREAD_RADIX + m_idx2 * k + t_idx2 + (k >> LOG_THREAD_NTT_SIZE) * l] = local[l];
        }
        __syncthreads();
    }
    if constexpr (tail > 0) {
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            local[l] = temp[set * SECOND_PER_THREAD_RADIX + (t_idx << LOG_THREAD_NTT_SIZE) + l];
        }
        buttNttBlock<THREAD_NTT_SIZE, tail>(local, large_w, large_w_shoup,
                                            (T * tw_idx + (t_idx << LOG_THREAD_NTT_SIZE)) >> tail, prime, two_prime);
        for (u32 l = 0; l < THREAD_NTT_SIZE; ++l) {
            temp[set * SECOND_PER_THREAD_RADIX + (t_idx << LOG_THREAD_NTT_SIZE) + l] = local[l];
        }
        __syncthreads();
    }
    constexpr u64 APPROX_QUOTIENT = divide128By64Lo(prod_inv, 0, prime);
    for (u32 j = 0; j < THREAD_NTT_SIZE; ++j) {
        u32 idx = poly_idx * DEGREE + m_idx * T + t_idx + (T >> LOG_THREAD_NTT_SIZE) * j;
        local[j] = temp[set * SECOND_PER_THREAD_RADIX + t_idx + static_cast<size_t>((T >> LOG_THREAD_NTT_SIZE) * j)];
        local[j] = local[j] >= two_prime ? local[j] - two_prime : local[j];
        local[j] = local[j] >= prime ? local[j] - prime : local[j];
        local[j] = prime - local[j] + poly_q[idx];
        local[j] = local[j] >= prime ? local[j] - prime : local[j];
        local[j] = mulModLazy(local[j], prod_inv, APPROX_QUOTIENT, prime);
        poly_q[idx] = local[j] >= prime ? local[j] - prime : local[j];
    }
}

// Assumes input a, b < 2p. Outputs a, b < 2p.
__device__ __inline__ static void buttInttLocal(u64 &x, u64 &y, const u64 w, const u64 w_shoup, const u64 p,
                                                const u64 two_p) {
    u64 tx = x + y;
    u64 ty = x + two_p - y;
    x = tx >= two_p ? tx - two_p : tx;
    y = mulModLazy(ty, w, w_shoup, p);
}

template <int Radix>
__device__ __inline__ static void buttIntt8Block(u64 *local, const u64 *large_w, const u64 *large_w_shoup,
                                                 const u32 idx, const u64 p1, const u64 p2) {
    if constexpr (Radix == 8) {
        const u32 idx4 = idx << 2;
        buttInttLocal(local[0], local[1], large_w[idx4], large_w_shoup[idx4], p1, p2);
        buttInttLocal(local[2], local[3], large_w[idx4 + 1], large_w_shoup[idx4 + 1], p1, p2);
        buttInttLocal(local[4], local[5], large_w[idx4 + 2], large_w_shoup[idx4 + 2], p1, p2);
        buttInttLocal(local[6], local[7], large_w[idx4 + 3], large_w_shoup[idx4 + 3], p1, p2);
    }

    if constexpr (Radix >= 4) {
        const u32 idx2 = idx << 1;
        buttInttLocal(local[0], local[2], large_w[idx2], large_w_shoup[idx2], p1, p2);
        buttInttLocal(local[1], local[3], large_w[idx2], large_w_shoup[idx2], p1, p2);
        buttInttLocal(local[4], local[6], large_w[idx2 + 1], large_w_shoup[idx2 + 1], p1, p2);
        buttInttLocal(local[5], local[7], large_w[idx2 + 1], large_w_shoup[idx2 + 1], p1, p2);
    }

    buttInttLocal(local[0], local[4], large_w[idx], large_w_shoup[idx], p1, p2);
    buttInttLocal(local[1], local[5], large_w[idx], large_w_shoup[idx], p1, p2);
    buttInttLocal(local[2], local[6], large_w[idx], large_w_shoup[idx], p1, p2);
    buttInttLocal(local[3], local[7], large_w[idx], large_w_shoup[idx], p1, p2);
}

template <u64 prime, u64 two_prime>
__global__ static void inttPhase2Kernel(const u64 *in, u64 *out, const u64 *large_w_inv, const u64 *large_w_inv_shoup) {
    extern __shared__ u64 temp[]; // NOLINT
    const u32 idx = blockIdx.y * blockDim.x + threadIdx.x;
    u32 set = threadIdx.x / SECOND_PER_THREAD_RADIX;
    // size of a block
    u64 local[8];
    u32 t = DEGREE / 2 / FIRST_RADIX;
    // i'th block
    u32 m_idx = idx / (t / 4);
    u32 t_idx = idx % (t / 4);
    // base address
    u32 degree_init = 2 * m_idx * t + t_idx + (blockIdx.x << LOG_DEGREE);
    const u64 *in_addr = in + degree_init;
    u64 *out_addr = out + degree_init;
    __syncthreads();
    for (u32 j = 0; j < 8; j++) {
        temp[set * 8 * SECOND_PER_THREAD_RADIX + t_idx + t / 4 * j] = in_addr[t / 4 * j];
    }
    __syncthreads();
    for (u32 l = 0; l < 8; l++) {
        local[l] = temp[set * 8 * SECOND_PER_THREAD_RADIX + 8 * t_idx + l];
    }
    const u32 tw_idx = FIRST_RADIX + m_idx;
    buttIntt8Block<8>(local, large_w_inv, large_w_inv_shoup, (t / 4) * tw_idx + t_idx, prime, two_prime);
    u32 tail = 0;
    __syncthreads();
    for (u32 l = 0; l < 8; l++) {
        temp[set * 8 * SECOND_PER_THREAD_RADIX + 8 * t_idx + l] = local[l];
    }
    __syncthreads();
#pragma unroll
    for (u32 j = t / 32, k = 32; j > 0; j >>= 3, k *= 8) {
        u32 m_idx2 = t_idx / (k / 4);
        u32 t_idx2 = t_idx % (k / 4);
        for (u32 l = 0; l < 8; l++) {
            local[l] = temp[set * 8 * SECOND_PER_THREAD_RADIX + 2 * m_idx2 * k + t_idx2 + (k / 4) * l];
        }
        buttIntt8Block<8>(local, large_w_inv, large_w_inv_shoup, j * tw_idx + m_idx2, prime, two_prime);
        for (u32 l = 0; l < 8; l++) {
            temp[set * 8 * SECOND_PER_THREAD_RADIX + 2 * m_idx2 * k + t_idx2 + (k / 4) * l] = local[l];
        }
        if (j == 2)
            tail = 1;
        if (j == 4)
            tail = 2;
        __syncthreads();
    }
    if constexpr (SECOND_PER_THREAD_RADIX == 4)
        tail = 2;
    else if constexpr (SECOND_PER_THREAD_RADIX == 2)
        tail = 1;
    if (tail == 1) {
        for (u32 j = 0; j < 8; j++) {
            local[j] = temp[set * 8 * SECOND_PER_THREAD_RADIX + t_idx + t / 4 * j];
        }
        buttIntt8Block<2>(local, large_w_inv, large_w_inv_shoup, tw_idx, prime, two_prime);
    } else if (tail == 2) {
        for (u32 j = 0; j < 8; j++) {
            local[j] = temp[set * 8 * SECOND_PER_THREAD_RADIX + t_idx + t / 4 * j];
        }
        buttIntt8Block<4>(local, large_w_inv, large_w_inv_shoup, tw_idx, prime, two_prime);
    }
    for (u32 j = 0; j < 8; j++) {
        out_addr[t / 4 * j] = local[j];
    }
}

template <u64 prime, u64 two_prime, u64 inv_degree, u64 inv_degree_shoup>
__global__ static void inttPhase1Kernel(u64 *in, const u64 *large_w_inv, const u64 *large_w_inv_shoup) {
    extern __shared__ u64 temp[]; // NOLINT
    const u32 &poly_idx = blockIdx.x;
    const u32 i = blockIdx.y * blockDim.x + threadIdx.x;

    const u32 warp_mod = threadIdx.x % PAD;
    const u32 warp_id = threadIdx.x / PAD;
    // size of a block
    u64 local[8];
    // i'th block
    const u32 m_idx = i / (DEGREE / 8);
    const u32 t_idx = i % (DEGREE / 8);
    u32 large_n_init = DEGREE / FIRST_PER_THREAD_RADIX * warp_id + warp_mod +
                       PAD * (t_idx / (FIRST_PER_THREAD_RADIX * PAD)) + (poly_idx << LOG_DEGREE);
    for (u32 j = 0; j < 8; j++) {
        local[j] = *(in + large_n_init + static_cast<size_t>(DEGREE / 8 / FIRST_PER_THREAD_RADIX * j));
    }
    const u32 eradix = 8 * FIRST_PER_THREAD_RADIX;
    const u32 tw_idx = 1 + m_idx;
    buttIntt8Block<8>(local, large_w_inv, large_w_inv_shoup, FIRST_PER_THREAD_RADIX * tw_idx + warp_id, prime,
                      two_prime);
    for (u32 j = 0; j < 8; ++j) {
        temp[warp_mod * (eradix + PAD) + 8 * warp_id + j] = local[j];
    }
    u32 tail = 0;
    __syncthreads();
#pragma unroll
    for (u32 j = FIRST_PER_THREAD_RADIX / 8, k = 32; j > 0; j >>= 3, k *= 8) {
        u32 m_idx2 = warp_id / (k / 4);
        u32 t_idx2 = warp_id % (k / 4);
        for (u32 l = 0; l < 8; ++l) {
            local[l] = temp[(eradix + PAD) * warp_mod + 2 * m_idx2 * k + t_idx2 + (k / 4) * l];
        }
        buttIntt8Block<8>(local, large_w_inv, large_w_inv_shoup, j * tw_idx + m_idx2, prime, two_prime);
        for (u32 l = 0; l < 8; ++l) {
            temp[(eradix + PAD) * warp_mod + 2 * m_idx2 * k + t_idx2 + (k / 4) * l] = local[l];
        }
        if (j == 2)
            tail = 1;
        if (j == 4)
            tail = 2;
        __syncthreads();
    }
    if constexpr (FIRST_PER_THREAD_RADIX == 4)
        tail = 2;
    else if constexpr (FIRST_PER_THREAD_RADIX == 2)
        tail = 1;
    for (u32 l = 0; l < 8; ++l) {
        local[l] = temp[warp_mod * (eradix + PAD) + warp_id + FIRST_PER_THREAD_RADIX * l];
    }
    if (tail == 1)
        buttIntt8Block<2>(local, large_w_inv, large_w_inv_shoup, tw_idx, prime, two_prime);
    else if (tail == 2)
        buttIntt8Block<4>(local, large_w_inv, large_w_inv_shoup, tw_idx, prime, two_prime);
    for (u32 j = 0; j < 8; ++j) {
        local[j] = mulModLazy(local[j], inv_degree, inv_degree_shoup, prime);
        local[j] = local[j] >= prime ? local[j] - prime : local[j];
    }

    large_n_init = DEGREE / 8 / FIRST_PER_THREAD_RADIX * warp_id + warp_mod +
                   PAD * (t_idx / (FIRST_PER_THREAD_RADIX * PAD)) + (poly_idx << LOG_DEGREE);
    for (u32 j = 0; j < 8; ++j) {
        in[large_n_init + static_cast<size_t>(DEGREE / 8 * j)] = local[j];
    }
}

template <u64 prime>
static void __global__ addKernel(u64 *res, const u64 *op_1, const u64 *op_2) {
    const u64 idx = blockIdx.x * blockDim.x + threadIdx.x;
    res[idx] = op_1[idx] + op_2[idx];
    if (res[idx] >= prime)
        res[idx] -= prime;
}

} // namespace evi
