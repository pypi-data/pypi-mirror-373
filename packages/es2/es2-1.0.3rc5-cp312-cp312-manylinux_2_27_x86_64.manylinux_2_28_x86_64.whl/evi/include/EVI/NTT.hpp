////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2021-2023 Crypto Lab Inc.                                    //
//                                                                            //
// - This file is part of HEaaN homomorphic encryption library.               //
// - HEaaN cannot be copied and/or distributed without the express permission //
//  of Crypto Lab Inc.                                                        //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

#pragma once

#include "CKKSTypes.hpp"
#include "EVI/Type.hpp"
#include <cstdint>
#include <set>
#include <vector>

namespace evi {

namespace utils {
void findPrimeFactors(std::set<u64> &s, u64 n);
u64 findPrimitiveRoot(u64 prime);

bool isPrime(const u64 n);
std::vector<u64> seekPrimes(const u64 center, const u64 gap, u64 number, const bool only_smaller);
} // namespace utils
//
class NTT {
public:
    NTT() = default;
    NTT(u64 degree, u64 prime);
    NTT(u64 degree, u64 prime, u64 degree_mini);

    template <int OutputModFactor = 1> // possible value: 1, 2, 4
    void computeForward(u64 *op) const;
    template <int OutputModFactor = 1>
    void computeForward(u64 *op, const u64 pad_rank) const;

    template <int OutputModFactor = 1> // possible value: 1, 2
    void computeBackward(u64 *op) const;

    template <int OutputModFactor = 1> // possible value: 1, 2
    void computeBackward(u64 *op, u64 fullmod) const;

private:
    u64 prime_;
    u64 two_prime_;
    u64 degree_;

    // roots of unity (bit reversed)
    polyvec psi_rev_;
    polyvec psi_inv_rev_;
    polyvec psi_rev_shoup_;
    polyvec psi_inv_rev_shoup_;

    // variables for last step of backward NTT
    u64 degree_inv_;
    u64 degree_inv_barrett_;
    u64 degree_inv_w_;
    u64 degree_inv_w_barrett_;

    void computeForwardNativeSingleStep(u64 *op, const u64 t) const;
    void computeForwardNativeSingleStep1(u64 *op, const u64 t, const u64 pad_rank) const;
    void computeBackwardNativeSingleStep(u64 *op, const u64 t) const;
    void computeBackwardNativeSingleStep1(u64 *op, const u64 t, const u64 fullmod) const;
    void computeBackwardNativeSingleStep2(u64 *op, const u64 t, const u64 fullmod) const;
    void computeBackwardNativeLast(u64 *op) const;
    void computeBackwardNativeLast(u64 *op, u64 fullmod) const;
};
} // namespace evi
