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

#include "Const.hpp"
#include "EVI/Basic.cuh"
#include "EVI/CKKSTypes.hpp"
#include "EVI/NTT.hpp"
#include "EVI/Type.hpp"
#include "utils/Enums.hpp"

#include <array>
#include <cstdint>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace evi {

struct ConstantPreset {
    virtual u64 getPrimeQ() const = 0;
    virtual u64 getPrimeP() const = 0;
    virtual u64 getPsiQ() const = 0;
    virtual u64 getPsiP() const = 0;
    virtual u64 getTwoPrimeQ() const = 0;
    virtual u64 getTwoPrimeP() const = 0;
    virtual u64 getHalfPrimeQ() const = 0;
    virtual u64 getHalfPrimeP() const = 0;
    virtual u64 getTwoTo64Q() const = 0;
    virtual u64 getTwoTo64P() const = 0;
    virtual u64 getTwoTo64ShoupQ() const = 0;
    virtual u64 getTwoTo64ShoupP() const = 0;

    virtual u64 getBarrRatioQ() const = 0;
    virtual u64 getBarrRatioP() const = 0;
    virtual u64 getPModQ() const = 0;
    virtual u64 getModDownProdInverseModEnd() const = 0;
    virtual u64 getInvDegreeQ() const = 0;
    virtual u64 getInvDegreeP() const = 0;
    virtual u64 getInvDegreeShoupQ() const = 0;
    virtual u64 getInvDegreeShoupP() const = 0;

    virtual u32 getHW() const = 0;
    virtual double getScaleFactor() const = 0;

    virtual ParameterPreset getPreset() const = 0;
};

struct IPBase : ConstantPreset {
public:
    IPBase() = default;
    ~IPBase() = default;

    u64 getPrimeQ() const override {
        return PRIME_Q;
    }
    u64 getPrimeP() const override {
        return PRIME_P;
    }
    u64 getPsiQ() const override {
        return PSI_Q;
    }
    u64 getPsiP() const override {
        return PSI_P;
    }

    u64 getTwoPrimeQ() const override {
        return TWO_PRIME_Q;
    }
    u64 getTwoPrimeP() const override {
        return TWO_PRIME_P;
    }
    u64 getHalfPrimeQ() const override {
        return HALF_PRIME_Q;
    }
    u64 getHalfPrimeP() const override {
        return HALF_PRIME_P;
    }
    u64 getTwoTo64Q() const override {
        return TWO_TO_64_Q;
    }
    u64 getTwoTo64P() const override {
        return TWO_TO_64_P;
    }
    u64 getTwoTo64ShoupQ() const override {
        return TWO_TO_64_SHOUP_Q;
    }
    u64 getTwoTo64ShoupP() const override {
        return TWO_TO_64_SHOUP_P;
    }
    u64 getBarrRatioQ() const override {
        return BARRETT_RATIO_FOR_U64_Q;
    }
    u64 getBarrRatioP() const override {
        return BARRETT_RATIO_FOR_U64_P;
    }
    u64 getPModQ() const override {
        return PMOD_Q;
    }
    u64 getModDownProdInverseModEnd() const override {
        return MOD_DOWN_PROD_INVERSE_MOD_END;
    }
    u64 getInvDegreeQ() const override {
        return INV_DEGREE_Q;
    }
    u64 getInvDegreeP() const override {
        return INV_DEGREE_P;
    }
    u64 getInvDegreeShoupQ() const override {
        return INV_DEGREE_SHOUP_Q;
    }
    u64 getInvDegreeShoupP() const override {
        return INV_DEGREE_SHOUP_P;
    }

    u32 getHW() const override {
        return HAMMING_WEIGHT;
    }

    double getScaleFactor() const override {
        return SCALE_FACTOR;
    }

    ParameterPreset getPreset() const override {
        return preset;
    }

    static constexpr u64 PRIME_Q = 288230376147386369;
    static constexpr u64 PSI_Q = 9464160453373;

    static constexpr u64 PRIME_P = 2251799810670593;
    static constexpr u64 PSI_P = 254746317487;

    static constexpr u64 TWO_PRIME_Q = PRIME_Q << 1;
    static constexpr u64 TWO_PRIME_P = PRIME_P << 1;
    static constexpr u64 HALF_PRIME_Q = PRIME_Q >> 1;
    static constexpr u64 HALF_PRIME_P = PRIME_P >> 1;
    static constexpr u64 TWO_TO_64_Q = powModSimple(2, 64, PRIME_Q);
    static constexpr u64 TWO_TO_64_P = powModSimple(2, 64, PRIME_P);
    static constexpr u64 TWO_TO_64_SHOUP_Q = divide128By64Lo(TWO_TO_64_Q, 0, PRIME_Q);
    static constexpr u64 TWO_TO_64_SHOUP_P = divide128By64Lo(TWO_TO_64_P, 0, PRIME_P);
    static constexpr u64 BARRETT_RATIO_FOR_U64_Q = divide128By64Lo(1, 0, PRIME_Q);
    static constexpr u64 BARRETT_RATIO_FOR_U64_P = divide128By64Lo(1, 0, PRIME_P);
    static constexpr u64 PMOD_Q = reduceBarrett(PRIME_Q, BARRETT_RATIO_FOR_U64_Q, PRIME_P);
    static constexpr u64 MOD_DOWN_PROD_INVERSE_MOD_END = powModSimple(PRIME_P, PRIME_Q - 2, PRIME_Q);
    static constexpr u64 INV_DEGREE_Q = powModSimple(DEGREE, PRIME_Q - 2, PRIME_Q);
    static constexpr u64 INV_DEGREE_P = powModSimple(DEGREE, PRIME_P - 2, PRIME_P);
    static constexpr u64 INV_DEGREE_SHOUP_Q = divide128By64Lo(INV_DEGREE_Q, 0, PRIME_Q);
    static constexpr u64 INV_DEGREE_SHOUP_P = divide128By64Lo(INV_DEGREE_P, 0, PRIME_P);

    static constexpr u32 HAMMING_WEIGHT = 2730;
    static constexpr double SCALE_FACTOR = 25.0;
    static constexpr ParameterPreset preset = ParameterPreset::IP0;
};

struct QFBase : ConstantPreset {
public:
    QFBase() = default;
    ~QFBase() = default;

    u64 getPrimeQ() const override {
        return PRIME_Q;
    }
    u64 getPrimeP() const override {
        return PRIME_P;
    }
    u64 getPsiQ() const override {
        return PSI_Q;
    }
    u64 getPsiP() const override {
        return PSI_P;
    }

    u64 getTwoPrimeQ() const override {
        return TWO_PRIME_Q;
    }
    u64 getTwoPrimeP() const override {
        return TWO_PRIME_P;
    }
    u64 getHalfPrimeQ() const override {
        return HALF_PRIME_Q;
    }
    u64 getHalfPrimeP() const override {
        return HALF_PRIME_P;
    }
    u64 getTwoTo64Q() const override {
        return TWO_TO_64_Q;
    }
    u64 getTwoTo64P() const override {
        return TWO_TO_64_P;
    }
    u64 getTwoTo64ShoupQ() const override {
        return TWO_TO_64_SHOUP_Q;
    }
    u64 getTwoTo64ShoupP() const override {
        return TWO_TO_64_SHOUP_P;
    }
    u64 getBarrRatioQ() const override {
        return BARRETT_RATIO_FOR_U64_Q;
    }
    u64 getBarrRatioP() const override {
        return BARRETT_RATIO_FOR_U64_P;
    }
    u64 getPModQ() const override {
        return PMOD_Q;
    }
    u64 getModDownProdInverseModEnd() const override {
        return MOD_DOWN_PROD_INVERSE_MOD_END;
    }
    u64 getInvDegreeQ() const override {
        return INV_DEGREE_Q;
    }
    u64 getInvDegreeP() const override {
        return INV_DEGREE_P;
    }
    u64 getInvDegreeShoupQ() const override {
        return INV_DEGREE_SHOUP_Q;
    }
    u64 getInvDegreeShoupP() const override {
        return INV_DEGREE_SHOUP_P;
    }

    u32 getHW() const override {
        return HAMMING_WEIGHT;
    }

    double getScaleFactor() const override {
        return SCALE_FACTOR;
    }
    ParameterPreset getPreset() const override {
        return preset;
    }

    static constexpr u64 PRIME_Q = 288230376135196673;
    static constexpr u64 PRIME_P = 2251799810670593;
    static constexpr u64 PSI_Q = 60193018759093;
    static constexpr u64 PSI_P = 254746317487;

    static constexpr u64 TWO_PRIME_Q = PRIME_Q << 1;
    static constexpr u64 TWO_PRIME_P = PRIME_P << 1;
    static constexpr u64 HALF_PRIME_Q = PRIME_Q >> 1;
    static constexpr u64 HALF_PRIME_P = PRIME_P >> 1;
    static constexpr u64 TWO_TO_64_Q = powModSimple(2, 64, PRIME_Q);
    static constexpr u64 TWO_TO_64_P = powModSimple(2, 64, PRIME_P);
    static constexpr u64 TWO_TO_64_SHOUP_Q = divide128By64Lo(TWO_TO_64_Q, 0, PRIME_Q);
    static constexpr u64 TWO_TO_64_SHOUP_P = divide128By64Lo(TWO_TO_64_P, 0, PRIME_P);
    static constexpr u64 BARRETT_RATIO_FOR_U64_Q = divide128By64Lo(1, 0, PRIME_Q);
    static constexpr u64 BARRETT_RATIO_FOR_U64_P = divide128By64Lo(1, 0, PRIME_P);
    static constexpr u64 PMOD_Q = reduceBarrett(PRIME_Q, BARRETT_RATIO_FOR_U64_Q, PRIME_P);
    static constexpr u64 MOD_DOWN_PROD_INVERSE_MOD_END = powModSimple(PRIME_P, PRIME_Q - 2, PRIME_Q);
    static constexpr u64 INV_DEGREE_Q = powModSimple(DEGREE, PRIME_Q - 2, PRIME_Q);
    static constexpr u64 INV_DEGREE_P = powModSimple(DEGREE, PRIME_P - 2, PRIME_P);
    static constexpr u64 INV_DEGREE_SHOUP_Q = divide128By64Lo(INV_DEGREE_Q, 0, PRIME_Q);
    static constexpr u64 INV_DEGREE_SHOUP_P = divide128By64Lo(INV_DEGREE_P, 0, PRIME_P);

    static constexpr u32 HAMMING_WEIGHT = 2730;
    static constexpr double SCALE_FACTOR = 25.0;
    static constexpr ParameterPreset preset = ParameterPreset::QF0;
};

struct RuntimeParam : ConstantPreset {
public:
    RuntimeParam(u64 prime_q, u64 prime_p, u64 psi_q, u64 psi_p, double scale_factor, u32 hw) {
        PRIME_Q = prime_q;
        PRIME_P = prime_p;
        PSI_Q = psi_q;
        PSI_P = psi_p;

        TWO_PRIME_Q = PRIME_Q << 1;
        TWO_PRIME_P = PRIME_P << 1;
        HALF_PRIME_Q = PRIME_Q >> 1;
        HALF_PRIME_P = PRIME_P >> 1;
        TWO_TO_64_Q = powModSimple(2, 64, PRIME_Q);
        TWO_TO_64_P = powModSimple(2, 64, PRIME_P);
        TWO_TO_64_SHOUP_Q = divide128By64Lo(TWO_TO_64_Q, 0, PRIME_Q);
        TWO_TO_64_SHOUP_P = divide128By64Lo(TWO_TO_64_P, 0, PRIME_P);
        BARRETT_RATIO_FOR_U64_Q = divide128By64Lo(1, 0, PRIME_Q);
        BARRETT_RATIO_FOR_U64_P = divide128By64Lo(1, 0, PRIME_P);
        PMOD_Q = reduceBarrett(PRIME_Q, BARRETT_RATIO_FOR_U64_Q, PRIME_P);
        MOD_DOWN_PROD_INVERSE_MOD_END = powModSimple(PRIME_P, PRIME_Q - 2, PRIME_Q);
        INV_DEGREE_Q = powModSimple(DEGREE, PRIME_Q - 2, PRIME_Q);
        INV_DEGREE_P = powModSimple(DEGREE, PRIME_P - 2, PRIME_P);
        INV_DEGREE_SHOUP_Q = divide128By64Lo(INV_DEGREE_Q, 0, PRIME_Q);
        INV_DEGREE_SHOUP_P = divide128By64Lo(INV_DEGREE_P, 0, PRIME_P);

        SCALE_FACTOR = scale_factor;
        HAMMING_WEIGHT = hw;
        preset = ParameterPreset::RUNTIME;
    }
    ~RuntimeParam() = default;

    u64 getPrimeQ() const override {
        return PRIME_Q;
    }
    u64 getPrimeP() const override {
        return PRIME_P;
    }
    u64 getPsiQ() const override {
        return PSI_Q;
    }
    u64 getPsiP() const override {
        return PSI_P;
    }

    u64 getTwoPrimeQ() const override {
        return TWO_PRIME_Q;
    }
    u64 getTwoPrimeP() const override {
        return TWO_PRIME_P;
    }
    u64 getHalfPrimeQ() const override {
        return HALF_PRIME_Q;
    }
    u64 getHalfPrimeP() const override {
        return HALF_PRIME_P;
    }
    u64 getTwoTo64Q() const override {
        return TWO_TO_64_Q;
    }
    u64 getTwoTo64P() const override {
        return TWO_TO_64_P;
    }
    u64 getTwoTo64ShoupQ() const override {
        return TWO_TO_64_SHOUP_Q;
    }
    u64 getTwoTo64ShoupP() const override {
        return TWO_TO_64_SHOUP_P;
    }
    u64 getBarrRatioQ() const override {
        return BARRETT_RATIO_FOR_U64_Q;
    }
    u64 getBarrRatioP() const override {
        return BARRETT_RATIO_FOR_U64_P;
    }
    u64 getPModQ() const override {
        return PMOD_Q;
    }
    u64 getModDownProdInverseModEnd() const override {
        return MOD_DOWN_PROD_INVERSE_MOD_END;
    }
    u64 getInvDegreeQ() const override {
        return INV_DEGREE_Q;
    }
    u64 getInvDegreeP() const override {
        return INV_DEGREE_P;
    }
    u64 getInvDegreeShoupQ() const override {
        return INV_DEGREE_SHOUP_Q;
    }
    u64 getInvDegreeShoupP() const override {
        return INV_DEGREE_SHOUP_P;
    }

    u32 getHW() const override {
        return HAMMING_WEIGHT;
    }

    double getScaleFactor() const override {
        return SCALE_FACTOR;
    }

    ParameterPreset getPreset() const override {
        return preset;
    }
    u64 PRIME_Q;
    u64 PRIME_P;
    u64 PSI_Q;
    u64 PSI_P;

    u64 TWO_PRIME_Q;
    u64 TWO_PRIME_P;
    u64 HALF_PRIME_Q;
    u64 HALF_PRIME_P;
    u64 TWO_TO_64_Q;
    u64 TWO_TO_64_P;
    u64 TWO_TO_64_SHOUP_Q;
    u64 TWO_TO_64_SHOUP_P;
    u64 BARRETT_RATIO_FOR_U64_Q;
    u64 BARRETT_RATIO_FOR_U64_P;
    u64 PMOD_Q;
    u64 MOD_DOWN_PROD_INVERSE_MOD_END;
    u64 INV_DEGREE_Q;
    u64 INV_DEGREE_P;
    u64 INV_DEGREE_SHOUP_Q;
    u64 INV_DEGREE_SHOUP_P;

    u32 HAMMING_WEIGHT;
    double SCALE_FACTOR;
    ParameterPreset preset;
};

using Parameter = std::shared_ptr<evi::ConstantPreset>;

Parameter setPreset(evi::ParameterPreset name);
Parameter setPreset(evi::ParameterPreset name, u64 prime_q, u64 prime_p, u64 psi_q, u64 psi_p, double scale_factor,
                    u32 hw);

} // namespace evi
