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
#include "EVI/CKKSTypes.hpp"
#include "EVI/Context.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/NTT.hpp"
#include "EVI/Type.hpp"

#ifdef BUILD_WITH_HEAAN
#include "Cleaner/EvaluationResource.hpp"
#include "utils/Utils.hpp"
#endif

#include "utils/Exceptions.hpp"
#include "utils/Sampler.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace evi {

/** @defgroup KeyGenAPI KeyGeneration API
 *  @brief KeyGenerator class for generating secret, encryption, and evaluation keys
 *
 * `KeyGenerator` is the main class for generating all homomorphic encryption keys in EVI.
 *
 * This API provides:
 *  - Secret key generation
 *  - Encryption key generation
 *  - Evaluation key generation
 *
 * Example usage:
 *
 * @{
 */

/**
 * @brief Key generation interface for EVI
 *
 * Defines core key generation operations for homomorphic encryption:
 * secret keys, encryption keys, relinearization keys, modulus packing keys,
 * and special switching keys used in advanced ciphertext operations.
 */
class KeyGeneratorInterface {
public:
    virtual ~KeyGeneratorInterface() = default;

    /**
     * @brief Generate a secret key
     *
     * @param sec_coeff (optional) Pointer to user-provided coefficients for deterministic key generation.
     *                  If not provided, a random secret key will be generated.
     * @return The generated SecretKey
     */
    virtual SecretKey genSecKey(std::optional<const int *> sec_coeff = std::nullopt) = 0;

    /**
     * @brief Generate an encryption key based on the given secret key
     *
     * @param seckey The secret key from which the encryption key is derived
     */
    virtual void genEncKey(const SecretKey &seckey) = 0;

    /**
     * @brief Generate a relinearization key
     *
     * Generates the key required for ciphertext multiplication operations
     * to keep the ciphertext size manageable after homomorphic multiplication.
     *
     * @param seckey The secret key used to derive the relinearization key
     */
    virtual void genRelinKey(const SecretKey &seckey) = 0;

    /**
     * @brief Generate a modulus packing key
     *
     * Generates the key required for modulus packing (modulus switching) operations.
     *
     * @param seckey The secret key used to derive the modulus packing key
     */
    virtual void genModPackKey(const SecretKey &seckey) = 0;

    /**
     * @brief Generate public keys (encryption key + evaluation keys) from a secret key
     *
     * @param seckey The secret key used to derive the public keys
     */
    virtual void genPubKeys(const SecretKey &seckey) = 0;

    /**
     * @brief Get a reference to the KeyPack containing the generated keys
     *
     * @return Reference to the KeyPack
     */
    virtual KeyPack &getKeyPack() = 0;

    /**
     * @brief Generate a Shared A switching key
     *
     * Shared A uses the A-part of the secret key as a common component
     * to optimize modulus packing operations.
     *
     * @param sec_from The original secret key
     * @param sec_to   The target secret keys
     */
    virtual void genSharedASwitchKey(const evi::SecretKey &sec_from, const std::vector<evi::SecretKey> &sec_to) = 0;

    /**
     * @brief Generate a Shared A additive switching key
     *
     * Similar to genSharedASwitchKey, but specialized for additive secret sharing.
     *
     * @param sec_from The original secret key
     * @param sec_to   The target secret keys
     */
    virtual void genAdditiveSharedASwitchKey(const evi::SecretKey &sec_from,
                                             const std::vector<evi::SecretKey> &sec_to) = 0;

    /**
     * @brief Generate a Shared A modulus packing key
     *
     * Enables more efficient modulus packing using Shared A optimization.
     *
     * @param sec_from The original secret key
     * @param sec_to   The target secret keys
     */
    virtual void genSharedAModPackKey(const evi::SecretKey &sec_from, const std::vector<evi::SecretKey> &sec_to) = 0;

    /**
     * @brief Generate a Shared A modulus packing key for CC queries
     *
     * CC (Ciphertext-on-Ciphertext) queries over a ciphertext DB
     * require a restricted Shared A key for efficient modulus packing.
     *
     * @param sec_from The original secret key
     * @param sec_to   The target secret keys
     */
    virtual void genCCSharedAModPackKey(const evi::SecretKey &sec_from, const std::vector<evi::SecretKey> &sec_to) = 0;

    /**
     * @brief Generate multi-secret keys required for Shared-A operations
     *
     * @return A vector of generated SecretKeys
     */
    virtual std::vector<SecretKey> genMultiSecKey() = 0;

    /**
     * @brief Generate a general switching key
     *
     * Allows converting a ciphertext encrypted under `sec_from`
     * into a ciphertext under a set of `sec_to` keys.
     *
     * @param sec_from The original secret key
     * @param sec_to   The target secret keys
     */
    virtual void genSwitchKey(const evi::SecretKey &sec_from, const std::vector<evi::SecretKey> &sec_to) = 0;
};

/** @cond INTERNAL_IMPL */
template <EvalMode M>
class KeyGeneratorImpl : public KeyGeneratorInterface {
public:
    KeyGeneratorImpl(const evi::Context &context, evi::KeyPack &pack,
                     std::optional<std::vector<u8>> seed = std::nullopt);
    KeyGeneratorImpl(const evi::Context &context, std::optional<std::vector<u8>> seed = std::nullopt);

    KeyGeneratorImpl() = delete;
    ~KeyGeneratorImpl() override = default;

    SecretKey genSecKey(std::optional<const int *> sec_coeff = std::nullopt) override;
    void genEncKey(const evi::SecretKey &sec_key) override;
    void genRelinKey(const evi::SecretKey &sec_key) override;
    void genModPackKey(const evi::SecretKey &sec_key) override;
    void genPubKeys(const evi::SecretKey &sec_key) override;

    void genSharedASwitchKey(const evi::SecretKey &sec_from, const std::vector<evi::SecretKey> &sec_to) override;
    void genAdditiveSharedASwitchKey(const evi::SecretKey &sec_from,
                                     const std::vector<evi::SecretKey> &sec_to) override;
    void genSharedAModPackKey(const evi::SecretKey &sec_from, const std::vector<evi::SecretKey> &sec_to) override;
    void genCCSharedAModPackKey(const evi::SecretKey &sec_from, const std::vector<evi::SecretKey> &sec_to) override;
    std::vector<SecretKey> genMultiSecKey() override;
    void genSwitchKey(const evi::SecretKey &sec_from, const std::vector<evi::SecretKey> &sec_to) override;

    evi::KeyPack &getKeyPack() {
        return pack_;
    }

private:
    void genSecKeyFromCoeff(evi::SecretKey &sec_key, const int *sec_coeff);
    void genSwitchingKey(const evi::SecretKey &sec_key, span<u64> from_s, span<u64> out_a_q, span<u64> out_a_p,
                         span<u64> out_b_q, span<u64> out_b_p);
    const evi::Context context_;
    evi::KeyPack pack_;

    std::shared_ptr<evi::KeyPack> gen_pack_;

    evi::RandomSampler sampler_;
};
/** @endcond */

/**
 * @brief MultiKeyGenerator manages multi-dimensional key generation
 *
 * It provides key generation, storage, and loading for scenarios
 * involving multiple contexts, ranks, and key packing configurations.
 */
class MultiKeyGenerator final {
public:
    /**
     * @brief MultiKeyGenerator constructor
     *
     * @param context EVI context used for key initialization and selecting the operation device
     * @param store_path Path where generated keys are stored
     * @param sInfo Stores the encryption state of secret keys when saved to disk
     */
    MultiKeyGenerator(std::vector<Context> &context, const std::string &store_path, SealInfo &sInfo,
                      std::optional<std::vector<u8>> seed = std::nullopt);
    ~MultiKeyGenerator() = default;

    /**
     * @brief Generate and store the full key set
     *
     * Generates keys for all contexts and stores them under the specified store_path
     *
     * @return The generated secret key
     */
    evi::SecretKey generate_keys();

    /**
     * @brief Generate only the secret key
     *
     * @return The generated secret key
     */
    evi::SecretKey generate_sec_key();

    /**
     * @brief Generate and store keys from an existing secret key file
     *
     * @param sec_key_path Path to the secret key
     */
    void generate_keys_from_sec_key(const std::string &sec_key_path);

    /**
     * @brief Generate a public key from an existing secret key
     *
     * @param sec_key The secret key from which the public key is derived
     */
    void generate_pub_key(evi::SecretKey sec_key);

    /**
     * @brief Generate keys required for bootstrapping (Only for QF0, QF1)
     */
    void generate_eval_key();

    /**
     * @brief Generate and store a special FR secret key
     *
     * @return The stored secret key
     */
    evi::SecretKey save_fr_sec_key();

    /**
     * @brief Return the KeyPack
     *
     * @return Reference to the KeyPack
     */
    evi::KeyPack &get_key_pack() {
        return heaan_fr_keypack_[0];
    }

    /**
     * @brief Check whether the generated keys exist in the store_path
     *
     * @return true if all files exist, false otherwise
     */
    bool checkFileExist();

private:
#ifdef BUILD_WITH_HEAAN
    HEaaN::Context heaan_context_hi_;
    HEaaN::Context heaan_context_;

    HEaaN::EvaluationResource heaan_eval_resource_;

    std::unique_ptr<HEaaN::SecretKey> heaan_sk_hi_;
    std::unique_ptr<HEaaN::SecretKey> heaan_sk_;

    HEaaN::Context heaan_context_clean_;

#endif

    std::vector<evi::Context> heaan_fr_context_;
    std::vector<evi::KeyPack> heaan_fr_keypack_;

    std::shared_ptr<SealInfo> sInfo_;
    std::optional<TEEWrapper> teew_;

    std::shared_ptr<alea_state> as_;

    std::vector<int> rank_list_;
    std::vector<std::pair<int, int>> inner_rank_list_;
    evi::ParameterPreset preset_;
    std::filesystem::path store_path_;

    void initialize();

    bool save_all_keys(evi::SecretKey sec_key);
    void save_enc_key();
    void save_eval_key();

    void save_fr_sec_key(evi::SecretKey sec_key);

    bool save_sec_keys();
#ifdef BUILD_WITH_HEAAN
    bool save_sec_key16();
    bool save_sec_key12();
    bool save_sec_key16_sealed();
    bool save_sec_key12_sealed();
#endif

    void adjustRankList(std::vector<int> &rank_list);
};

using KeyGenerator = std::shared_ptr<KeyGeneratorInterface>;

/**
 * @brief Factory function to create a KeyGenerator.
 *
 * Creates a `KeyGenerator` bound to the given encryption context.
 *
 * @param context EVI context used for key initialization and selecting the operation device
 * @param pack    KeyPack where the generated keys will be stored
 * @param seed    (optional) PRNG seed for deterministic key generation
 *
 * @return A `KeyGenerator` instance for generating secret/public/evaluation keys
 */
KeyGenerator makeKeyGenerator(const Context &context, KeyPack &pack,
                              std::optional<std::vector<u8>> seed = std::nullopt);

/**
 * @brief Alternative factory function to create a KeyGenerator.
 *
 * Creates a `KeyGenerator` without an external KeyPack.
 *
 * @param context EVI context used for key initialization and selecting the operation device
 * @param seed    (optional) PRNG seed for deterministic key generation
 *
 * @return A `KeyGenerator` instance for generating secret/public/evaluation keys
 */
KeyGenerator makeKeyGenerator(const Context &context, std::optional<std::vector<u8>> seed = std::nullopt);

/** @} */ // end of KeyGenAPI

} // namespace evi
