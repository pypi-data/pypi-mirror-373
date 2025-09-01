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
#include "EVI/Const.hpp"
#include "EVI/Context.hpp"
#include "EVI/NTT.hpp"
#include "EVI/Type.hpp"
#include "utils/crypto/TEEWrapper.hpp"

#include "utils/Enums.hpp"
#include "utils/Exceptions.hpp"
#include "utils/SealInfo.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace evi {

namespace fs = std::filesystem;

/** @defgroup SecretKeyAPI SecretKey API
 *  @brief SecretKey class for managing secret key data
 *
 * `SecretKey` is the private key management component for homomorphic encryption.
 * It manages secret key coefficients and supports multiple storage modes for enhanced security.
 *
 * This API provides:
 *  - Serialization and deserialization of secret key data
 *  - Loading and saving secret keys from files or streams
 *  - Provide key data protection using AES encryption
 *
 * Example usage:
 * @code
 *   auto context = evi::makeContext(preset, DeviceType::GPU, 4096, EvalMode::RMP);
 *   auto seckey = evi::makeSecKey(context);
 *   seckey->saveSecKey("keys/FRSecKey.bin");
 * @endcode
 */

struct SecretKeyData {
    SecretKeyData(const evi::Context &context);
    SecretKeyData(const std::string &path, std::optional<SealInfo> sInfo = std::nullopt);

    void loadSecKey(const std::string &dir_path);
    void saveSecKey(const std::string &dir_path) const;

    void loadSealedSecKey(const std::string &dir_path);
    void saveSealedSecKey(const std::string &dir_path);

    void serialize(std::ostream &os) const;
    void deserialize(std::istream &is);

    evi::ParameterPreset preset_;

    s_poly sec_coeff_;
    poly sec_key_q_;
    poly sec_key_p_;

    bool sec_loaded_;

    std::optional<SealInfo> sInfo_;
    std::optional<TEEWrapper> teew_;
};

/** @defgroup KeyPackAPI KeyPack API
 *  @brief KeyPack class for managing encryption and evaluation keys
 *
 * `KeyPack` is the key management component for homomorphic encryption.
 * It manages encryption keys, evaluation keys (modpack key, relin key).
 *
 * This API provides:
 *  - Key generation and storage for homomorphic encryption
 *  - Serialization and deserialization of key data
 *  - Loading and saving keys from files or streams
 *
 * Example usage:
 * @code
 *   auto context = evi::makeContext(preset, DeviceType::GPU, 4096, EvalMode::RMP);
 *   auto keypack = evi::makeKeyPack(context);
 *   keypack->save("keys/");
 *   keypack->loadEvalKeyFile("EvalKey.bin");
 * @endcode
 */

/** @ingroup KeyPackAPI
 * @brief Internal structure for managing key data in homomorphic encryption
 *
 * Handles all keys required for homomorphic operations:
 * - Enables loading and saving keys from files or streams
 * - Provides key data serialization and deserialization
 */
struct KeyPackData {
public:
    KeyPackData() = delete;

    /**
     * @brief Construct KeyPackData for a given homomorphic context.
     *
     * Initializes a KeyPackData associated with the provided context.
     *
     * @param context    EVI context used for key initialization and selecting the operation device
     */
    KeyPackData(const evi::Context &context);

    /**
     * @brief Construct KeyPackData from a serialized input stream.
     *
     * Initializes a KeyPackData by deserializing key data from the given input stream.
     *
     * @param context    EVI context used for key initialization and selecting the operation device
     * @param in         Input stream containing serialized KeyPack data
     */
    KeyPackData(const evi::Context &context, std::istream &in);

    /**
     * @brief Construct KeyPackData by loading keys from a directory.
     *
     * Initializes a KeyPackData by reading key files from the specified directory.
     *
     * @param context    EVI context used for key initialization and selecting the operation device
     * @param dir_path   Directory path containing key files
     */
    KeyPackData(const evi::Context &context, std::string &dir_path);
    ~KeyPackData() = default;

    void serialize(std::ostream &os) const;
    void deserialize(std::istream &is);

    void saveEncKeyFile(const std::string &path) const;
    void getEncKeyBuffer(std::ostream &os) const;
    void saveEvalKeyFile(const std::string &path) const;
    void getEvalKeyBuffer(std::ostream &os) const;
    void saveModPackKeyFile(const std::string &path) const;
    void getModPackKeyBuffer(std::ostream &os) const;
    void saveRelinKeyFile(const std::string &path) const;
    void getRelinKeyBuffer(std::ostream &os) const;

    void loadEncKeyFile(const std::string &path);
    void loadEncKeyBuffer(std::istream &is);
    void loadEvalKeyFile(const std::string &path);
    void loadEvalKeyBuffer(std::istream &is);
    void loadRelinKeyFile(const std::string &path);
    void loadRelinKeyBuffer(std::istream &is);
    void loadModPackKeyFile(const std::string &path);
    void loadModPackKeyBuffer(std::istream &is);

    void save(const std::string &path);

    FixedKeyType encKey;
    FixedKeyType relinKey;

    VariadicKeyType modPackKey;
    VariadicKeyType sharedAModPackKey;
    VariadicKeyType CCSharedAModPackKey;
    VariadicKeyType switchKey;
    VariadicKeyType sharedAKey;
    VariadicKeyType reverseSwitchKey;
    std::vector<VariadicKeyType> additiveSharedAKey;

    int num_shared_secret;

    bool shared_a_key_loaded_;
    bool shared_a_mod_pack_loaded_;
    bool cc_shared_a_mod_pack_loaded_;
    bool enc_loaded_;
    bool eval_loaded_;

    const evi::Context context_;
};

using KeyPack = std::shared_ptr<KeyPackData>;
using SecretKey = std::shared_ptr<SecretKeyData>;

/**
 * @brief Factory function to create a KeyPack instance.
 *
 * Initializes a KeyPack with the given homomorphic context.
 *
 * @param context    EVI context used for key initialization and selecting the operation device
 * @return Shared pointer to the initialized KeyPack
 */
KeyPack makeKeyPack(const evi::Context &context);

/**
 * @brief Factory function to create a KeyPack instance from a serialized input stream.
 *
 * Initializes a KeyPack by deserializing key data from the given input stream.
 *
 * @param context    EVI context used for key initialization and selecting the operation device
 * @param in         Input stream containing serialized KeyPack data
 * @return Shared pointer to the initialized KeyPack
 */
KeyPack makeKeyPack(const evi::Context &context, std::istream &in);

/**
 * @brief Factory function to create a KeyPack instance from a directory path.
 *
 * Initializes a KeyPack by loading key files from the specified directory.
 *
 * @param context    EVI context used for key initialization and selecting the operation device
 * @param dir_path   Directory path containing key files
 * @return Shared pointer to the initialized KeyPack
 */
KeyPack makeKeyPack(const evi::Context &context, std::string &dir_path);

/**
 * @brief Factory function to create a SecretKey for a given homomorphic context.
 *
 * Initializes a SecretKey associated with the provided context.
 *
 * @param context    EVI context used for key initialization and selecting the operation device
 * @return Shared pointer to the initialized SecretKey
 */
SecretKey makeSecKey(const evi::Context &context);

/**
 * @brief Factory function to create a SecretKey by loading from a specified path.
 *
 * Initializes a SecretKey by reading key data from the given file.
 *
 * @param path       File path containing the secret key data
 * @return Shared pointer to the initialized SecretKey
 */
SecretKey makeSecKey(const std::string &path, std::optional<SealInfo> sInfo = std::nullopt);

/** @defgroup MultiSecretKeyAPI MultiSecretKey API
 *  @brief MultiSecretKey for managing multiple secret keys in Shared-A operations
 *
 * `MultiSecretKey` is a collection of secret keys used for **Shared-A key switching**,
 * a method that improves the efficiency of certain homomorphic operations.
 *
 * This API provides:
 * - Manages multiple secret keys for optimized key switching in Shared-A operations
 *
 */
using MultiSecretKey = std::vector<std::shared_ptr<SecretKeyData>>;

} // namespace evi
