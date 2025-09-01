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

#include "EVI/Context.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/Type.hpp"
#include "utils/CheckMacros.hpp"
#include "utils/Enums.hpp"
#include "utils/Exceptions.hpp"

#include <cstdint>
#include <iostream>
#include <memory>
#include <utility>
#include <vector>

namespace evi {

struct ComputeBufferInterface {
public:
    virtual ~ComputeBufferInterface() = default;
    virtual void loadQuery(const Query query) = 0;
    virtual const Context getContext() const = 0;

    virtual polydata getTempData(const int pos) = 0;
    virtual polydata getCtxtTempData(const int pos) = 0;
    virtual polydata getPackData(const int pos) = 0;

    virtual polydata getUpData(const int pos, const int level) = 0;
    virtual polydata getCtxtInputData(const int pos, const int level) = 0;
    virtual polydata getPtxtInputData(const int pos, const int level) = 0;

    virtual polydata getData(std::string_view var_name) = 0;
    virtual polyvec128 &getData128(std::string_view var_name) = 0;

private:
    virtual void initializeComputeBuffer() = 0;
    virtual void freeComputeBuffer() = 0;
};

template <DeviceType D, EvalMode M>
struct ComputeBufferBase;

template <EvalMode M>
struct ComputeBufferBase<DeviceType::CPU, M> : ComputeBufferInterface {
public:
    ComputeBufferBase(const evi::Context &context);
    // ~ComputeBufferBase() = default;
    ~ComputeBufferBase() override;

    void loadQuery(const Query query) override;
    // void loadPlaintext(const std::shared_ptr<SinglePlaintext> query) override;
    // void loadCiphertext(const std::shared_ptr<SingleCiphertext> query) override;

    polydata getData(std::string_view var_name) override;

    polydata getTempData(const int pos) override;
    polydata getCtxtTempData(const int pos) override;
    polydata getPackData(const int pos) override;

    polydata getUpData(const int pos, const int level) override;
    polydata getCtxtInputData(const int pos, const int level) override;
    polydata getPtxtInputData(const int pos, const int level) override;

    polyvec128 &getData128(std::string_view var_name) override;
    const Context getContext() const override {
        return context_;
    }

private:
    void initializeComputeBuffer() override;
    [[noreturn]] void freeComputeBuffer() override {
        throw NotSupportedError("Not supported to Release CPU buffer ");
    };
    const evi::Context context_;

    polyvec ctxt_temp_a;
    polyvec ctxt_temp_b;
    polyvec ctxt_temp_c;
    polyvec ctxt_temp_d;
    polyvec ctxt_pack_a;
    polyvec ctxt_pack_b;

    polyvec temp_a;
    poly temp_b;
    poly temp_c;
    poly temp_d;
    poly up_a_q;
    poly up_a_p;
    poly up_b_q;
    poly up_b_p;

    poly b_p;
    poly a_p;

    poly ctxt_input_a;
    poly ctxt_input_b;
    poly ctxt_input_a_p;
    poly ctxt_input_b_p;
    poly ptxt_input_q;
    poly ptxt_input_p;

    u32 inner_rank_;
    u32 num_input_cipher_;

    // EvalMode::HERS
    std::vector<Query> inputs;

    polyvec128 mult_sum_tmp1;
    polyvec128 mult_sum_tmp2;

    polyvec temp_ntt1;
    polyvec temp_ntt2;
    polyvec128 res_128;
};

template <EvalMode M>
struct ComputeBufferBase<DeviceType::GPU, M> : public ComputeBufferInterface {
public:
    ComputeBufferBase(const evi::Context &context);
    ~ComputeBufferBase() override;

    void loadQuery(const Query query) override;

    polydata getTempData(const int pos) override;
    polydata getCtxtTempData(const int pos) override;
    polydata getPackData(const int pos) override;
    polydata getUpData(const int pos, const int level) override;
    polydata getCtxtInputData(const int pos, const int level) override;
    polydata getPtxtInputData(const int pos, const int level) override;

    polyvec128 &getData128(std::string_view var_name) override {
        throw InvalidInputError("No such variable exists in buffer");
    }
    [[noreturn]] polydata getData(std::string_view var_name) override {
        throw InvalidInputError("No such variable exists in buffer");
    }

    const Context getContext() const override {
        return context_;
    }

    int device_id_;

private:
    void initializeComputeBuffer() override;
    void freeComputeBuffer() override;
    const evi::Context context_;
    // read only
    polydata ctxt_input_a_q;
    polydata ctxt_input_a_p;
    polydata ctxt_input_b_q;
    polydata ctxt_input_b_p;
    polydata ptxt_input_q;
    polydata ptxt_input_p;

    // writables
    polydata ctxt_temp_a;
    polydata ctxt_temp_b;
    polydata ctxt_temp_c;
    polydata ctxt_pack_a;
    polydata ctxt_pack_b;
    polydata up_a_q;
    polydata up_a_p;
    polydata up_b_q;
    polydata up_b_p;
    polydata temp_a;
    polydata temp_b;

    u32 inner_rank_;
    u32 num_input_cipher_;
};

using ComputeBuffer = std::shared_ptr<ComputeBufferInterface>;

ComputeBuffer createComputeBuffer(const evi::Context &context);

} // namespace evi
