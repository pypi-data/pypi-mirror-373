////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2024, CryptoLab Inc. All rights reserved.                    //
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

#include "EVI/Type.hpp"

#include "EVI/CKKSTypes.hpp"
#include "EVI/Context.hpp"
#include "EVI/IndexImpl.hpp"
#include "EVI/KeyPack.hpp"
#include "utils/CheckMacros.hpp"
#include "utils/CudaUtils.hpp"
#include "utils/Enums.hpp"
#include "utils/Exceptions.hpp"
#include <cstdint>
#include <iostream>
#include <memory>
#include <optional>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <variant>
#include <vector>

namespace evi {

/** @defgroup IndexAPI Index API
 *  @brief Index class for managing plaintext and ciphertext data indexing
 *
 * `Index` is the core data management component for homomorphic encryption.
 * It stores and organizes plaintext and ciphertext data for evaluation,
 * supports batch operations, and can run on both CPU and GPU.
 *
 * This API provides:
 *  - Efficient storage and retrieval of indexed data
 *  - Disk-based save/load operations for large datasets
 *  - Optional GPU loading for accelerated queries
 *
 * Example usage:
 * @code
 *   auto context = evi::makeContext(preset, DeviceType::GPU, 4096, EvalMode::RMP);
 *   auto index = evi::makeIndex(context, DataType::CIPHER);
 *   index->store("index_dir/");
 *   index->load("index_dir/");
 * @endcode
 */

/** @ingroup IndexAPI
 * @brief Internal index interface for homomorphic encryption
 *
 * Defines the abstract interface for managing indexed data:
 * - Supports loading and storing data to disk
 * - Provides serialization and deserialization for streams
 * - Allows data retrieval, batch management, and GPU memory handling
 */
class IndexImpl {
public:
    virtual ~IndexImpl() = default;

    /** @brief Set index data, performing Shared-A key switching if needed */
    virtual void setData(Blob data, std::optional<KeyPack> = std::nullopt) = 0;
    // virtual void setData(std::vector<DataState> data) = 0;
    /** @brief Save index metadata and polynomial data to a directory */
    virtual void store(const std::string &dir_path) = 0;
    /** @brief Load index metadata and polynomial data from a directory */
    virtual void load(const std::string &dir_path) = 0;

    /** @brief Serialize index metadata and polynomial data to an output stream */
    virtual void serializeTo(std::ostream &stream) = 0;
    /** @brief Deserialize index metadata and polynomial data from an input stream */
    virtual void deserializeFrom(std::istream &stream) = 0;

    /**
     * @brief Get polynomial data from the index.
     * Returns polynomial data based on position and level:
     * - (0, 0): returns b_q (mod Q part of b)
     * - (0, 1): returns b_p (mod P part of b)
     * - (1, 0): returns a_q (mod Q part of a)
     * - (1, 1): returns a_p (mod P part of a)
     */
    virtual polydata getPolyData(const int pos, const int level, std::optional<int> vec_idx = std::nullopt,
                                 std::optional<int> idx = std::nullopt) = 0;

    /** @brief Get batch indices for the specified GPU device ID */
    virtual std::vector<int> &getBatchListOfDeviceId(const int device_id) const = 0;

    /** @brief Check if the index is loaded into GPU memory for the given device ID */
    virtual bool isLoadedToGPU(const int device_id) const = 0;

    /** @return total item count in the index */
    virtual u32 getItemCount() const = 0;

    /** @return data type of the index (e.g., CIPHER, PLAIN, SERIALIZED_CIPHER, SERIALIZED_PLAIN) */
    virtual const DataType &getDataType() const = 0;

    /** @brief Append a single query item to the index for later evaluation. */
    virtual void append(const Query item) = 0;

    virtual std::vector<u64> batchAdd(const std::vector<Query> &items) = 0;

    virtual u32 getPoorIndex() const = 0;

    /** @return current polynomial level of the index */
    virtual int getLevel() const = 0;
    /** @return padded rank aligned to the nearest power of two */
    virtual u32 getPadRank() const = 0;
    /** @return user-specified rank for display */
    virtual u32 getShowRank() const = 0;
};

/// @cond INTERNAL
template <DeviceType D, DataType T, EvalMode M>
class IndexAdapter : public IndexImpl {
    using EvalImpl = std::conditional_t<!(CHECK_RMP(M)), std::shared_ptr<IndexBase<D, T, M>>,
                                        std::vector<std::shared_ptr<IndexBase<D, T, M>>>>;
    EvalImpl impl_;
    u32 show_rank_;
    u32 num_impl_;
    u32 num_db_;
    const DataType dtype_;

    // void toSharedA(Evalimpl) const override;

public:
    IndexAdapter(const evi::Context &context);

    void setData(Blob data, std::optional<KeyPack> = std::nullopt) override;
    // void setData(std::vector<DataState> data) override;
    void store(const std::string &dir_path) override;
    void load(const std::string &dir_path) override;
    void serializeTo(std::ostream &stream) override;
    void deserializeFrom(std::istream &stream) override;
    polydata getPolyData(const int pos, const int level, std::optional<int> vec_idx = std::nullopt,
                         std::optional<int> idx = std::nullopt) override;

    void append(const Query item) override;
    std::vector<u64> batchAdd(const std::vector<Query> &items) override;

    bool isLoadedToGPU(const int device_id) const override;
    std::vector<int> &getBatchListOfDeviceId(const int device_id) const override;
    const DataType &getDataType() const override;

    u32 getPoorIndex() const override;
    u32 getItemCount() const override;
    int getLevel() const override;
    u32 getPadRank() const override;
    u32 getShowRank() const override {
        return show_rank_;
    }

    // void append(const std::vector<Query> items) override;
};
/// @endcond

using Index = std::shared_ptr<IndexImpl>;

/**
 * @brief Factory function to create an Index instance.
 *
 * Initializes an Index with the given homomorphic context and data type.
 *
 * @param context   EVI context used for key initialization and selecting the operation device
 * @param dtype     Data type of the index, defaulting to DataType::CIPHER.
 * @return          Shared pointer to the initialized Index
 */
Index makeIndex(const Context &context, evi::DataType dtype = DataType::CIPHER);

} // namespace evi
