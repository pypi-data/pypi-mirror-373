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

template <u64 prime, u64 two_prime, u64 two_to_64, u64 two_to_64_shoup, u64 barr_out>
__global__ static void tensorCC(const u64 *ctxt_input_a, const u64 *ctxt_input_b, const u64 *ctxt_db_a,
                                const u64 *ctxt_db_b, u64 *ctxt_out_a, u64 *ctxt_out_b, u64 *ctxt_out_c,
                                const u32 pad_rank_) {
    u32 idx = (blockIdx.x << LOG_TENSOR_X_DIM) + threadIdx.x;
    u64 input_a = ctxt_input_a[idx];
    u64 input_b = ctxt_input_b[idx];

    for (u32 i = threadIdx.y; i < pad_rank_; i += blockDim.y) {
        u32 db_idx = (i << LOG_DEGREE) + idx;
        u64 db_a = ctxt_db_a[db_idx];
        u64 db_b = ctxt_db_b[db_idx];
        ctxt_out_a[db_idx] = mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, input_a, db_a);
        u64 temp = mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, input_a, db_b) +
                   mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, input_b, db_a);
        reduceModFactor(prime, two_prime, temp);
        ctxt_out_b[db_idx] = temp;
        ctxt_out_c[db_idx] = mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, input_b, db_b);
    }
}

template <u64 prime, u64 two_prime, u64 two_to_64, u64 two_to_64_shoup, u64 barr_out>
__global__ static void tensorCCAdd(const u64 *ctxt_input_a, const u64 *ctxt_input_b, const u64 *ctxt_db_a,
                                   const u64 *ctxt_db_b, u64 *ctxt_out_a, u64 *ctxt_out_b, u64 *ctxt_out_c,
                                   const u32 pad_rank_) {
    u32 idx = (blockIdx.x << LOG_TENSOR_X_DIM) + threadIdx.x;
    u64 input_a = ctxt_input_a[idx];
    u64 input_b = ctxt_input_b[idx];

    for (u32 i = threadIdx.y; i < pad_rank_; i += blockDim.y) {
        u32 db_idx = (i << LOG_DEGREE) + idx;
        u64 db_a = ctxt_db_a[db_idx];
        u64 db_b = ctxt_db_b[db_idx];
        ctxt_out_a[db_idx] += mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, input_a, db_a);
        reduceModFactor(prime, two_prime, ctxt_out_a[db_idx]);
        u64 temp = mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, input_a, db_b) +
                   mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, input_b, db_a);
        reduceModFactor(prime, two_prime, temp);
        ctxt_out_b[db_idx] += temp;
        reduceModFactor(prime, two_prime, ctxt_out_b[db_idx]);
        ctxt_out_c[db_idx] += mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, input_b, db_b);
        reduceModFactor(prime, two_prime, ctxt_out_c[db_idx]);
    }
}

template <u64 prime, u64 two_prime, u64 two_to_64, u64 two_to_64_shoup, u64 barr_out>
__global__ static void tensorPC(const u64 *plaintext, const u64 *ctxt_db_a, const u64 *ctxt_db_b, u64 *ctxt_out_a,
                                u64 *ctxt_out_b, const u32 pad_rank_) {
    u32 idx = (blockIdx.x << LOG_TENSOR_X_DIM) + threadIdx.x;
    u64 plain = plaintext[idx];

    for (u32 i = threadIdx.y; i < pad_rank_; i += blockDim.y) {
        u32 db_idx = (i << LOG_DEGREE) + idx;
        u64 db_a = ctxt_db_a[db_idx];
        u64 db_b = ctxt_db_b[db_idx];
        ctxt_out_a[db_idx] = mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, plain, db_a);
        ctxt_out_b[db_idx] = mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, plain, db_b);
    }
}

template <u64 prime, u64 two_prime, u64 two_to_64, u64 two_to_64_shoup, u64 barr_out>
__global__ static void tensorPCAdd(const u64 *plaintext, const u64 *ctxt_db_a, const u64 *ctxt_db_b, u64 *ctxt_out_a,
                                   u64 *ctxt_out_b, const u32 pad_rank_) {
    u32 idx = (blockIdx.x << LOG_TENSOR_X_DIM) + threadIdx.x;
    u64 plain = plaintext[idx];

    for (u32 i = threadIdx.y; i < pad_rank_; i += blockDim.y) {
        u32 db_idx = (i << LOG_DEGREE) + idx;
        u64 db_a = ctxt_db_a[db_idx];
        u64 db_b = ctxt_db_b[db_idx];
        ctxt_out_a[db_idx] += mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, plain, db_a);
        reduceModFactor(prime, two_prime, ctxt_out_a[db_idx]);
        ctxt_out_b[db_idx] += mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, plain, db_b);
        reduceModFactor(prime, two_prime, ctxt_out_b[db_idx]);
    }
}

template <u64 prime, u64 two_prime, u64 two_to_64, u64 two_to_64_shoup, u64 barr_out>
__global__ static void tensorCP(const u64 *ptxt_db_q, const u64 *ctxt_input_a, const u64 *ctxt_input_b, u64 *ctxt_out_a,
                                u64 *ctxt_out_b, const u32 pad_rank_) {
    u32 idx = (blockIdx.x << LOG_TENSOR_X_DIM) + threadIdx.x;
    u64 input_a = ctxt_input_a[idx];
    u64 input_b = ctxt_input_b[idx];

    for (u32 i = threadIdx.y; i < pad_rank_; i += blockDim.y) {
        u32 db_idx = (i << LOG_DEGREE) + idx;
        u64 ptxt_db = ptxt_db_q[db_idx];
        ctxt_out_a[db_idx] = mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, ptxt_db, input_a);
        ctxt_out_b[db_idx] = mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, ptxt_db, input_b);
    }
}

template <u64 prime, u64 two_prime, u64 two_to_64, u64 two_to_64_shoup, u64 barr_out>
__global__ static void tensorCPAdd(const u64 *ptxt_db_q, const u64 *ctxt_input_a, const u64 *ctxt_input_b,
                                   u64 *ctxt_out_a, u64 *ctxt_out_b, const u32 pad_rank_) {
    u32 idx = (blockIdx.x << LOG_TENSOR_X_DIM) + threadIdx.x;
    u64 input_a = ctxt_input_a[idx];
    u64 input_b = ctxt_input_b[idx];

    for (u32 i = threadIdx.y; i < pad_rank_; i += blockDim.y) {
        u32 db_idx = (i << LOG_DEGREE) + idx;
        u64 ptxt_db = ptxt_db_q[db_idx];
        ctxt_out_a[db_idx] += mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, ptxt_db, input_a);
        reduceModFactor(prime, two_prime, ctxt_out_a[db_idx]);
        ctxt_out_b[db_idx] += mulMod(prime, two_prime, two_to_64, two_to_64_shoup, barr_out, ptxt_db, input_b);
        reduceModFactor(prime, two_prime, ctxt_out_b[db_idx]);
    }
}

template <u64 prime_q, u64 prime_p>
static void __global__ batchElementMultKeyKernel(const u64 *key_a_q, const u64 *key_a_p, const u64 *key_b_q,
                                                 const u64 *key_b_p, const u64 *op_a_q, const u64 *op_a_p, u64 *a_q,
                                                 u64 *a_p, u64 *b_q, u64 *b_p, const u32 pad_rank_) {
    const u64 idx = blockIdx.x * blockDim.x + threadIdx.x;
    const u64 key_a_q_value = key_a_q[idx];
    const u64 key_b_q_value = key_b_q[idx];
    const u64 key_a_p_value = key_a_p[idx];
    const u64 key_b_p_value = key_b_p[idx];
    const u64 key_a_q_shoup = divide128By64Lo(key_a_q_value, 0, prime_q);
    const u64 key_b_q_shoup = divide128By64Lo(key_b_q_value, 0, prime_q);
    const u64 key_a_p_shoup = divide128By64Lo(key_a_p_value, 0, prime_p);
    const u64 key_b_p_shoup = divide128By64Lo(key_b_p_value, 0, prime_p);
    for (u32 i = 0; i < (pad_rank_ << LOG_DEGREE); i += DEGREE) {
        u64 value = op_a_q[idx + i];
        a_q[idx + i] = mulModLazy(value, key_a_q[idx], key_a_q_shoup, prime_q);
        a_q[idx + i] = a_q[idx + i] >= prime_q ? a_q[idx + i] - prime_q : a_q[idx + i];
        b_q[idx + i] = mulModLazy(value, key_b_q[idx], key_b_q_shoup, prime_q);
        b_q[idx + i] = b_q[idx + i] >= prime_q ? b_q[idx + i] - prime_q : b_q[idx + i];
        value = op_a_p[idx + i];
        a_p[idx + i] = mulModLazy(value, key_a_p[idx], key_a_p_shoup, prime_p);
        a_p[idx + i] = a_p[idx + i] >= prime_p ? a_p[idx + i] - prime_p : a_p[idx + i];
        b_p[idx + i] = mulModLazy(value, key_b_p[idx], key_b_p_shoup, prime_p);
        b_p[idx + i] = b_p[idx + i] >= prime_p ? b_p[idx + i] - prime_p : b_p[idx + i];
    }
}

template <u64 prime_q, u64 two_prime_q, u64 two_to_64_q, u64 two_to_shoup_q, u64 barr_out_q, u64 prime_p,
          u64 two_prime_p, u64 two_to_64_p, u64 two_to_shoup_p, u64 barr_out_p>
static void __global__ multKeyBatchKernel(const u64 *key_a_q, const u64 *key_a_p, const u64 *key_b_q,
                                          const u64 *key_b_p, const u64 *op_a_q, const u64 *op_a_p, u64 *a_q, u64 *a_p,
                                          u64 *b_q, u64 *b_p, const u32 pad_rank_) {
    const u32 idx = blockIdx.x * blockDim.x + threadIdx.x;
    u64 value = op_a_q[idx];
    u64 a_q_value = mulMod<4>(prime_q, two_prime_q, two_to_64_q, two_to_shoup_q, barr_out_q, value, key_a_q[idx]);
    u64 b_q_value = mulMod<4>(prime_q, two_prime_q, two_to_64_q, two_to_shoup_q, barr_out_q, value, key_b_q[idx]);
    value = op_a_p[idx];
    u64 a_p_value = mulMod<4>(prime_p, two_prime_p, two_to_64_p, two_to_shoup_p, barr_out_p, value, key_a_p[idx]);
    u64 b_p_value = mulMod<4>(prime_p, two_prime_p, two_to_64_p, two_to_shoup_p, barr_out_p, value, key_b_p[idx]);
    for (u32 i = 1; i < pad_rank_; ++i) {
        value = op_a_q[idx + (i << LOG_DEGREE)];
        a_q_value += mulMod<4>(prime_q, two_prime_q, two_to_64_q, two_to_shoup_q, barr_out_q, value,
                               key_a_q[idx + (i << LOG_DEGREE)]);
        b_q_value += mulMod<4>(prime_q, two_prime_q, two_to_64_q, two_to_shoup_q, barr_out_q, value,
                               key_b_q[idx + (i << LOG_DEGREE)]);
        value = op_a_p[idx + (i << LOG_DEGREE)];
        a_p_value += mulMod<4>(prime_p, two_prime_p, two_to_64_p, two_to_shoup_p, barr_out_p, value,
                               key_a_p[idx + (i << LOG_DEGREE)]);
        b_p_value += mulMod<4>(prime_p, two_prime_p, two_to_64_p, two_to_shoup_p, barr_out_p, value,
                               key_b_p[idx + (i << LOG_DEGREE)]);
        if ((i & 31) == 0) {
            a_q_value = reduceBarrett(prime_q, barr_out_q, a_q_value);
            a_p_value = reduceBarrett(prime_p, barr_out_p, a_p_value);
            b_q_value = reduceBarrett(prime_q, barr_out_q, b_q_value);
            b_p_value = reduceBarrett(prime_p, barr_out_p, b_p_value);
        }
    }
    a_q[idx] = reduceBarrett(prime_q, barr_out_q, a_q_value);
    a_p[idx] = reduceBarrett(prime_p, barr_out_p, a_p_value);
    b_q[idx] = reduceBarrett(prime_q, barr_out_q, b_q_value);
    b_p[idx] = reduceBarrett(prime_p, barr_out_p, b_p_value);
}

template <u64 mod_in, u64 mod_out, u64 barr_out>
static void __global__ normalizeModKernel(const u64 *input, u64 *out) {
    constexpr u64 HALF_MOD = mod_in >> 1;
    constexpr bool IS_SMALL_PRIME = HALF_MOD <= mod_out;
    constexpr u64 DIFF = mod_out - (IS_SMALL_PRIME ? mod_in : reduceBarrett(mod_out, barr_out, mod_in));

    const u64 idx = blockIdx.x * blockDim.x + threadIdx.x;
    u64 temp = input[idx];
    if (temp > HALF_MOD)
        temp += DIFF;
    if constexpr (!IS_SMALL_PRIME)
        temp = reduceBarrett(mod_out, barr_out, temp);
    out[idx] = temp;
}

__global__ static void transposeAKernel(const u64 *a_in, u64 *a_out, const u32 log_rank) {
    __shared__ u64 tile[TILE_DIM][TILE_DIM];

    u32 x = blockIdx.x * TILE_DIM + threadIdx.x;
    u32 y = blockIdx.y * TILE_DIM + threadIdx.y;

    for (u32 i = 0; i < TILE_DIM; i += BLOCK_ROWS) {
        tile[threadIdx.y + i][threadIdx.x] = a_in[((y + i) << LOG_DEGREE) + (blockIdx.z << log_rank) + x];
    }
    __syncthreads();

    x = blockIdx.y * TILE_DIM + threadIdx.x;
    y = blockIdx.x * TILE_DIM + threadIdx.y;
    for (u32 i = 0; i < TILE_DIM; i += BLOCK_ROWS)
        a_out[((y + i) << LOG_DEGREE) + (blockIdx.z << log_rank) + x] = tile[threadIdx.x][threadIdx.y + i];
}

__global__ static void transposeBKernel(const u64 *b_in, u64 *b_out, const u32 rank_) {
    b_out[blockIdx.x * rank_ + (threadIdx.x + blockIdx.y * MAX_NUM_THREADS)] =
        b_in[(threadIdx.x + blockIdx.y * MAX_NUM_THREADS) * DEGREE + blockIdx.x * rank_ + rank_ - 1];
}

template <u64 prime_p, u64 prime_q, u64 barr_out, u64 two_prime_q, u64 prod_inv>
__global__ static void rescaleKernel(const u64 *op, u64 *out) {
    constexpr u64 HALF_MOD = prime_p >> 1;
    constexpr bool IS_SMALL_PRIME = HALF_MOD <= prime_q;
    constexpr u64 DIFF = prime_q - (IS_SMALL_PRIME ? prime_p : reduceBarrett(prime_q, barr_out, prime_p));
    constexpr u64 APPROX_QUOTIENT = divide128By64Lo(prod_inv, 0, prime_q);

    const u64 idx = blockIdx.x * blockDim.x + threadIdx.x;
    u64 temp = op[idx];

    // normalize mod
    if (temp > HALF_MOD)
        temp += DIFF;
    if constexpr (!IS_SMALL_PRIME)
        temp = reduceBarrett(prime_q, barr_out, temp);

    // sub and const mult inv_prime_p
    temp = temp >= two_prime_q ? temp - two_prime_q : temp;
    temp = temp >= prime_q ? temp - prime_q : temp;
    temp = prime_q - temp + out[idx];
    temp = temp >= prime_q ? temp - prime_q : temp;
    temp = mulModLazy(temp, prod_inv, APPROX_QUOTIENT, prime_q);
    out[idx] = temp >= prime_q ? temp - prime_q : temp;
}

// used in IVF
template <u64 prime_q, u64 prime_p, u64 two_prime_q, u64 two_prime_p, u64 two_to_64_q, u64 two_to_64_p,
          u64 two_to_64_shoup_q, u64 two_to_64_shoup_p, u64 barr_out_q, u64 barr_out_p>
__global__ static void batchTensorPC(const u64 *plain_q, const u64 *plain_p, u64 **in, u64 *ctxt_out_a_q,
                                     u64 *ctxt_out_a_p, u64 *ctxt_out_b_q, u64 *ctxt_out_b_p) {
    u32 idx = (blockIdx.x << LOG_TENSOR_X_DIM) + threadIdx.x;
    u32 res_idx = (blockIdx.y << LOG_DEGREE) + idx;
    u32 y_idx = blockIdx.y << 2;
    u64 p_q = plain_q[idx];
    u64 p_p = plain_p[idx];

    u64 db_a_q = in[y_idx][idx];
    u64 db_b_q = in[y_idx + 2][idx];
    ctxt_out_a_q[res_idx] = mulMod(prime_q, two_prime_q, two_to_64_q, two_to_64_shoup_q, barr_out_q, p_q, db_a_q);
    ctxt_out_b_q[res_idx] = mulMod(prime_q, two_prime_q, two_to_64_q, two_to_64_shoup_q, barr_out_q, p_q, db_b_q);

    u64 db_a_p = in[y_idx + 1][idx];
    u64 db_b_p = in[y_idx + 3][idx];
    ctxt_out_a_p[res_idx] = mulMod(prime_p, two_prime_p, two_to_64_p, two_to_64_shoup_p, barr_out_p, p_p, db_a_p);
    ctxt_out_b_p[res_idx] = mulMod(prime_p, two_prime_p, two_to_64_p, two_to_64_shoup_p, barr_out_p, p_p, db_b_p);
}

template <u64 prime_q, u64 prime_p, u64 two_prime_q, u64 two_prime_p, u64 two_to_64_q, u64 two_to_64_p,
          u64 two_to_64_shoup_q, u64 two_to_64_shoup_p, u64 barr_out_q, u64 barr_out_p>
__global__ static void ShiftAddTensor(const u64 *ptxt_q, const u64 *ptxt_p, u64 **in1, u64 **in2,
                                      const u64 *shift_q_gpu, const u64 *shift_p_gpu, u64 *out_a_q, u64 *out_a_p,
                                      u64 *out_b_q, u64 *out_b_p, const u64 *shift) {
    u32 idx = blockIdx.x * blockDim.x + threadIdx.x;
    u32 res_idx = (blockIdx.y << LOG_DEGREE) + idx;
    u32 to_shift = shift[blockIdx.y];
    u32 shift_idx = (to_shift << LOG_DEGREE) + idx;
    u32 y_idx = blockIdx.y << 2;

    // Q part
    u64 in_a = in2[y_idx][idx];
    u64 in_b = in2[y_idx + 2][idx];
    u64 shift_q = shift_q_gpu[shift_idx];

    u64 temp_a = mulMod(prime_q, two_prime_q, two_to_64_q, two_to_64_shoup_q, barr_out_q, in_a, shift_q);
    u64 temp_b = mulMod(prime_q, two_prime_q, two_to_64_q, two_to_64_shoup_q, barr_out_q, in_b, shift_q);
    u64 sum_a = in1[y_idx][idx] + temp_a;
    u64 sum_b = in1[y_idx + 2][idx] + temp_b;

    u64 s_a = sum_a >= prime_q ? sum_a - prime_q : sum_a;
    u64 s_b = sum_b >= prime_q ? sum_b - prime_q : sum_b;

    u64 plain_q = ptxt_q[idx];
    out_a_q[res_idx] = mulMod(prime_q, two_prime_q, two_to_64_q, two_to_64_shoup_q, barr_out_q, plain_q, s_a);
    out_b_q[res_idx] = mulMod(prime_q, two_prime_q, two_to_64_q, two_to_64_shoup_q, barr_out_q, plain_q, s_b);

    // P part
    u64 in_a_p = in2[y_idx + 1][idx];
    u64 in_b_p = in2[y_idx + 3][idx];
    u64 shift_p = shift_p_gpu[shift_idx];
    u64 temp_a_p = mulMod(prime_p, two_prime_p, two_to_64_p, two_to_64_shoup_p, barr_out_p, in_a_p, shift_p);
    u64 temp_b_p = mulMod(prime_p, two_prime_p, two_to_64_p, two_to_64_shoup_p, barr_out_p, in_b_p, shift_p);
    u64 sum_a_p = in1[y_idx + 1][idx] + temp_a_p;
    u64 sum_b_p = in1[y_idx + 3][idx] + temp_b_p;

    u64 s_a_p = sum_a_p >= prime_q ? sum_a_p - prime_q : sum_a_p;
    u64 s_b_p = sum_b_p >= prime_q ? sum_b_p - prime_q : sum_b_p;
    u64 plain_p = ptxt_p[idx];
    out_a_p[res_idx] = mulMod(prime_p, two_prime_p, two_to_64_p, two_to_64_shoup_p, barr_out_p, plain_p, s_a_p);
    out_b_p[res_idx] = mulMod(prime_p, two_prime_p, two_to_64_p, two_to_64_shoup_p, barr_out_p, plain_p, s_b_p);
}

} // namespace evi
