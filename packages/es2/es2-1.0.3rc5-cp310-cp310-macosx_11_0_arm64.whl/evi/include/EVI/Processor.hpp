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

#include "EVI/CKKSTypes.hpp"
#include "EVI/ComputeBuffer.hpp"
#include "EVI/Context.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/NTT.hpp"
#include "EVI/Type.hpp"
#include "utils/Enums.hpp"
#include "utils/Exceptions.hpp"

#include <functional>

#ifdef __CUDACC__
#include <cuda_runtime.h>
#endif

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <type_traits>
#include <utility>
#include <variant>
#include <vector>

namespace evi {

class ProcessorImpl {
public:
    virtual ~ProcessorImpl() = default;

    virtual void rescale(const u64 *in, u64 *out, const u32 num_ctxt) = 0;

    virtual void normalizeModUp(const u64 *input, u64 *out, const u32 size) = 0;
    virtual void normalizeModDown(const u64 *input, u64 *out, const u32 size) = 0;
    virtual void tensorPCModQ(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a, u64 *out_b,
                              const u32 num_ctxt) = 0;
    virtual void tensorPCModP(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a, u64 *out_b,
                              const u32 num_ctxt) = 0;
    virtual void tensorCPModQ(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a,
                              u64 *out_b, const u32 num_ctxt) = 0;
    virtual void tensorCPModP(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a,
                              u64 *out_b, const u32 num_ctxt) = 0;
    virtual void tensorCCModQ(const u64 *query_ctxt_a, const u64 *query_ctxt_b, const u64 *db_ctxt_a,
                              const u64 *db_ctxt_b, u64 *out_a, u64 *out_b, u64 *out_c, const u32 num_ctxt) = 0;
    virtual void tensorPCAddModQ(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a,
                                 u64 *out_b, const u32 num_ctxt) = 0;
    virtual void tensorCPAddModQ(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a,
                                 u64 *out_b, const u32 num_ctxt) = 0;
    virtual void tensorCCAddModQ(const u64 *query_ctxt_a, const u64 *query_ctxt_b, const u64 *db_ctxt_a,
                                 const u64 *db_ctxt_b, u64 *out_a, u64 *out_b, u64 *out_c, const u32 num_ctxt) = 0;

    virtual void multRelinKey(const u64 *op_a_q, const u64 *op_a_p, u64 *a_q, u64 *a_p, u64 *b_q, u64 *b_p,
                              const u64 *key_a_q, const u64 *key_a_p, const u64 *key_b_q, const u64 *key_b_p,
                              const u32 size) = 0;
    virtual void multModPackKey(const u64 *op_a_q, const u64 *op_a_p, u64 *a_q, u64 *a_p, u64 *b_q, u64 *b_p,
                                const u64 *key_a_q, const u64 *key_a_p, const u64 *key_b_q, const u64 *key_b_p,
                                const u32 size) = 0;
    virtual void batchTensorPCPQ(const u64 *plain_q, const u64 *plain_p, u64 **in, u64 *ctxt_out_a_p, u64 *ctxt_out_a_q,
                                 u64 *ctxt_out_b_p, u64 *ctxt_out_b_q, const u32 num_ctxt) = 0;
};

template <evi::ParameterPreset T>
class GPUProcessorImpl : public ProcessorImpl {
public:
    GPUProcessorImpl() = default;
    ~GPUProcessorImpl() = default;

    void rescale(const u64 *in, u64 *out, const u32 num_ctxt);
    void normalizeModUp(const u64 *input, u64 *out, const u32 size);
    void normalizeModDown(const u64 *input, u64 *out, const u32 size);
    void tensorPCModQ(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a, u64 *out_b,
                      const u32 num_ctxt);
    void tensorPCModP(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a, u64 *out_b,
                      const u32 num_ctxt);
    void tensorCPModQ(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a, u64 *out_b,
                      const u32 num_ctxt);
    void tensorCPModP(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a, u64 *out_b,
                      const u32 num_ctxt);
    void tensorCCModQ(const u64 *query_ctxt_a, const u64 *query_ctxt_b, const u64 *db_ctxt_a, const u64 *db_ctxt_b,
                      u64 *out_a, u64 *out_b, u64 *out_c, const u32 num_ctxt);
    void tensorPCAddModQ(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a, u64 *out_b,
                         const u32 num_ctxt);
    void tensorCPAddModQ(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a, u64 *out_b,
                         const u32 num_ctxt);
    void tensorCCAddModQ(const u64 *query_ctxt_a, const u64 *query_ctxt_b, const u64 *db_ctxt_a, const u64 *db_ctxt_b,
                         u64 *out_a, u64 *out_b, u64 *out_c, const u32 num_ctxt);

    void multRelinKey(const u64 *op_a_q, const u64 *op_a_p, u64 *a_q, u64 *a_p, u64 *b_q, u64 *b_p, const u64 *key_a_q,
                      const u64 *key_a_p, const u64 *key_b_q, const u64 *key_b_p, const u32 size);
    void multModPackKey(const u64 *op_a_q, const u64 *op_a_p, u64 *a_q, u64 *a_p, u64 *b_q, u64 *b_p,
                        const u64 *key_a_q, const u64 *key_a_p, const u64 *key_b_q, const u64 *key_b_p, const u32 size);
    void batchTensorPCPQ(const u64 *plain_q, const u64 *plain_p, u64 **in, u64 *ctxt_out_a_p, u64 *ctxt_out_a_q,
                         u64 *ctxt_out_b_p, u64 *ctxt_out_b_q, const u32 num_ctxt);
};

template <evi::ParameterPreset T>
class CPUProcessorImpl : public ProcessorImpl {
public:
    CPUProcessorImpl() = default;
    ~CPUProcessorImpl() = default;

    void rescale(const u64 *in, u64 *out, const u32 num_ctxt);
    void normalizeModUp(const u64 *input, u64 *out, const u32 size);
    void normalizeModDown(const u64 *input, u64 *out, const u32 size);
    void tensorPCModQ(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a, u64 *out_b,
                      const u32 num_ctxt);
    void tensorPCModP(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a, u64 *out_b,
                      const u32 num_ctxt);
    void tensorCPModQ(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a, u64 *out_b,
                      const u32 num_ctxt);
    void tensorCPModP(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a, u64 *out_b,
                      const u32 num_ctxt);
    void tensorCCModQ(const u64 *query_ctxt_a, const u64 *query_ctxt_b, const u64 *db_ctxt_a, const u64 *db_ctxt_b,
                      u64 *out_a, u64 *out_b, u64 *out_c, const u32 num_ctxt);
    void tensorPCAddModQ(const u64 *query_ptxt, const u64 *db_ctxt_a, const u64 *db_ctxt_b, u64 *out_a, u64 *out_b,
                         const u32 num_ctxt);
    void tensorCPAddModQ(const u64 *db_ptxt, const u64 *query_ctxt_a, const u64 *query_ctxt_b, u64 *out_a, u64 *out_b,
                         const u32 num_ctxt);
    void tensorCCAddModQ(const u64 *query_ctxt_a, const u64 *query_ctxt_b, const u64 *db_ctxt_a, const u64 *db_ctxt_b,
                         u64 *out_a, u64 *out_b, u64 *out_c, const u32 num_ctxt);

    void multRelinKey(const u64 *op_a_q, const u64 *op_a_p, u64 *a_q, u64 *a_p, u64 *b_q, u64 *b_p, const u64 *key_a_q,
                      const u64 *key_a_p, const u64 *key_b_q, const u64 *key_b_p, const u32 size);
    void multModPackKey(const u64 *op_a_q, const u64 *op_a_p, u64 *a_q, u64 *a_p, u64 *b_q, u64 *b_p,
                        const u64 *key_a_q, const u64 *key_a_p, const u64 *key_b_q, const u64 *key_b_p, const u32 size);
    // TODO Fix
    void batchTensorPCPQ(const u64 *plain_q, const u64 *plain_p, u64 **in, u64 *ctxt_out_a_p, u64 *ctxt_out_a_q,
                         u64 *ctxt_out_b_p, u64 *ctxt_out_b_q, const u32 num_ctxt) {
        // throw evi::Exception(evi::ErrorCode::NOT_FOUND_ERROR, "batchTensorPC is not implemented for
        // CPUProcessorImpl");
        std::cout << "1" << std::endl;
    };
};

using HEProcessor = std::shared_ptr<ProcessorImpl>;
HEProcessor initProcessor(evi::DeviceType device, evi::ParameterPreset preset);

} // namespace evi
