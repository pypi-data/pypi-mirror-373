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

namespace evi {
constexpr u32 LOG_DEGREE = 12;
constexpr u32 HAMMING_WEIGHT = 2730;
constexpr u32 HW_REJ_BIT_SIZE = 12;
constexpr u32 CBD_COIN_SIZE = 21;
constexpr u32 SEED_MIN_SIZE = 64; // For alea shake256
constexpr u32 SEED_MAX_SIZE = 256;
constexpr u32 SHAKE256_RATE = 136;
constexpr u32 PRNG_BUF_SIZE = SHAKE256_RATE * 80;
constexpr u32 BIT_MAX_LEN = 64;

constexpr int MIN_CONTEXT_SIZE_LOG = 5;
constexpr int MAX_CONTEXT_SIZE_LOG = 12;
constexpr int MIN_CONTEXT_SIZE = 1 << MIN_CONTEXT_SIZE_LOG;
constexpr int MAX_CONTEXT_SIZE = 1 << MAX_CONTEXT_SIZE_LOG;
constexpr int NUM_CONTEXT = MAX_CONTEXT_SIZE_LOG - MIN_CONTEXT_SIZE_LOG + 1;

constexpr double GAUSSIAN_ERROR_STDEV = 3.2;

constexpr u32 DEGREE = 1LU << LOG_DEGREE;
constexpr u32 TWO_DEGREE = DEGREE << 1;
constexpr u64 U64_DEGREE{sizeof(u64) << LOG_DEGREE};

constexpr u32 MAX_NUM_THREADS = 1U << 10;
constexpr u32 LOG_TENSOR_X_DIM = 5;
constexpr u32 LOG_TENSOR_Y_DIM = 3;

static constexpr u32 LOG_TILE_DIM = 5;
static constexpr u32 TILE_DIM = 1U << LOG_TILE_DIM;
static constexpr u32 BLOCK_ROWS = 8;

constexpr static u32 LOG_THREAD_NTT_SIZE = 3;
constexpr static u32 LOG_FIRST_RADIX = 6;
constexpr static u32 LOG_THREAD_N = 6;
constexpr static u32 PAD = 4;

constexpr static u32 FIRST_RADIX = 1U << LOG_FIRST_RADIX;
constexpr static u32 THREAD_NTT_SIZE = 1U << LOG_THREAD_NTT_SIZE;
constexpr static u32 THREAD_N = 1U << LOG_THREAD_N;
constexpr static u32 FIRST_PER_THREAD_RADIX = FIRST_RADIX >> LOG_THREAD_NTT_SIZE;
constexpr static u32 DEGREE_PER_SIZE = DEGREE >> LOG_THREAD_NTT_SIZE;
constexpr static u32 LOG_SECOND_RADIX = LOG_DEGREE - LOG_FIRST_RADIX;
constexpr static u32 SECOND_RADIX = 1U << LOG_SECOND_RADIX;
constexpr static u32 SECOND_PER_THREAD_RADIX = SECOND_RADIX >> LOG_THREAD_NTT_SIZE;

constexpr int AES256_KEY_SIZE = 32;
constexpr int AES256_IV_SIZE = 12;
constexpr int AES256_TAG_SIZE = 16;
constexpr int AES256_GCM_OUT_SIZE = 62;
} // namespace evi
