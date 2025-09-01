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

#include "CKKSTypes.hpp"
#include "EVI/Basic.cuh"
#include "EVI/CKKSTypes.hpp"
#include "EVI/Context.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/Type.hpp"
#include "utils/Exceptions.hpp"
#include "utils/span.hpp"

#include <cstdint>
#include <functional>
#include <optional>
#include <string>
#include <utility>
#include <vector>

#ifdef BUILD_WITH_HEAAN
#include "Cleaner/Cleaner.hpp"
#include "HEaaN/Ciphertext.hpp"
#include "HEaaN/Decryptor.hpp"
#include "HEaaN/Message.hpp"
#include "HEaaN/ParameterPreset.hpp"
#endif

namespace evi {

/** @defgroup DecryptorAPI Decryptor API
 *  @brief Decryptor class for decrypting ciphertexts
 *
 * `Decryptor` is the main interface for decrypting ciphertexts such as `SearchResult` and `Query`
 * using a given EVI context and secret key.
 *
 * Example usage:
 * @code
 *   auto ctx = evi::makeContext(preset, DeviceType::GPU, 4096, EvalMode::RMP);
 *   auto dec = evi::makeDecryptor(ctx);
 *   auto msg = dec->decrypt(searchResultCipher, secretKey);
 * @endcode
 *
 * When compiled with `BUILD_WITH_HEAAN`, it can also decrypt HEaaN ciphertexts.
 *
 * @{
 */

/** @ingroup DecryptorAPI
 * @class DecryptorImpl
 * @brief Internal implementation of Decryptor
 *
 * Normally, you don’t need to use this class directly.
 * Instead, create a `Decryptor` using @ref makeDecryptor() and call its APIs.
 *
 * `DecryptorImpl` contains the actual decryption logic for:
 * - `SearchResult` ciphertexts
 * - `Query` ciphertexts
 * - (Optional) HEaaN ciphertexts when `BUILD_WITH_HEAAN` is enabled
 */
class DecryptorImpl {
public:
    /**
     * @brief Construct a decryptor from an EVI context
     *
     * @param context EVI context used for key initialization and selecting the operation device
     */
    explicit DecryptorImpl(const evi::Context &context);

    /**
     * @brief Decrypt a SearchResult ciphertext using a provided EVI secret key
     *
     * @param ctxt The SearchResult ciphertext
     * @param key  EVI secret key used for decryption
     * @param is_score If true, interprets the result as a score
     * @param scale Optional scaling factor to adjust the decrypted value
     * @return Message containing the decrypted result
     */
    Message decrypt(const SearchResult ctxt, const evi::SecretKey &key, bool is_score,
                    std::optional<double> scale = std::nullopt);

    /**
     * @brief Decrypt a SearchResult ciphertext by loading the EVI secret key from a file
     *
     * @param ctxt      The SearchResult ciphertext
     * @param key_path  Path to the EVI secret key file
     * @param is_score  If true, reorders the decrypted values for score interpretation
     *                  if false, returns the raw decrypted data
     * @param scale     Optional scaling factor to adjust the decrypted value
     * @return Message  Containing the decrypted result
     */
    Message decrypt(const SearchResult ctxt, const std::string &key_path, bool is_score,
                    std::optional<double> scale = std::nullopt);

    /**
     * @brief Decrypt a Query ciphertext using a provided EVI secret key
     *
     * @param ctxt      The Query ciphertext
     * @param key       Secret key used for decryption
     * @param scale     Optional scaling factor to adjust the decrypted value
     * @return Message  Containing the decrypted result
     */
    Message decrypt(const Query ctxt, const evi::SecretKey &key, std::optional<double> scale = std::nullopt);

    Message decrypt(const int idx, const Query ctxt, const evi::SecretKey &key,
                    std::optional<double> scale = std::nullopt);

    /**
     * @brief Decrypt a Query ciphertext by loading the secret EVI key from a file
     *
     * @param ctxt      The Query ciphertext
     * @param key_path  Path to the secret key file
     * @param scale     Optional scaling factor to adjust the decrypted value
     * @return Message  Containing the decrypted result
     */
    Message decrypt(const Query ctxt, const std::string &key_path, std::optional<double> scale = std::nullopt);

#ifdef BUILD_WITH_HEAAN

    explicit DecryptorImpl(const std::string &path);
    void decrypt(const HEaaN::Ciphertext &ctxt, HEaaN::Message &dmsg);

    std::optional<HEaaN::Context> heaan_context_;
    std::shared_ptr<HEaaN::Decryptor> heaan_dec_;
    std::shared_ptr<HEaaN::SecretKey> heaan_sk_;
    std::shared_ptr<HEaaN::Cleaner> heaan_cleaner_;

    std::shared_ptr<HEaaN::Cleaner> getCleaner() {
        return heaan_cleaner_;
    }

    HEaaN::Context &getHEaaNContext() {
        return heaan_context_.value();
    }

#endif

private:
    const evi::Context context_;
};

using Decryptor = std::shared_ptr<DecryptorImpl>;

/**
 * @brief Factory function to create a decryptor from an EVI context
 *
 * Creates a Decryptor instance bound to the given encryption context.
 *
 * @param context EVI context used for key initialization and selecting the operation device
 * @return Shared pointer to a DecryptorImpl instance
 */
Decryptor makeDecryptor(const evi::Context &context);

#ifdef BUILD_WITH_HEAAN
/**
 * @brief Factory function to create a HEaaN-compatible decryptor from a secret key path
 *
 * Available only when compiled with `BUILD_WITH_HEAAN`.
 *
 * @param path Path to the HEaaN secret key file
 * @return Shared pointer to a DecryptorImpl instance
 */
Decryptor makeDecryptor(const std::string &path);
#endif

/** @} */ // end of DecryptorAPI

} // namespace evi
