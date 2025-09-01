#pragma once

#include <memory>
#include <stdint.h>

#include <array>
#include <cstddef>
#include <functional>
#include <optional>
#include <vector>

#include "EVI/Const.hpp"
#include "EVI/Type.hpp"
#include "utils/Enums.hpp"
#include "utils/Exceptions.hpp"
#include "utils/span.hpp"

#ifdef BUILD_WITH_HEAAN
#include "HEaaN/Ciphertext.hpp"
#endif

namespace evi {

#define LEVEL1 1
/** @brief Message type for float values */
using Message = std::vector<float>;
/** @brief Raw pointer to 32-bit polynomial coefficients */
using Coefficients = int *;

#define alignment_byte 256
template <typename T, std::size_t N>
struct alignas(alignment_byte) AlignedArray : public std::array<T, N> {};

/** @brief 256-byte aligned polynomial buffer with 64-bit coefficients */
using s_poly = AlignedArray<i64, DEGREE>;
/** @brief 256-byte aligned polynomial buffer with 64-bit coefficients */
using poly = AlignedArray<u64, DEGREE>;

/** @brief 64-bit polynomial coefficient vector aligned to 256 bytes */
using polyvec = std::vector<u64, AlignedAllocator<u64, alignment_byte>>;
/** @brief 128-bit polynomial coefficient vector aligned to 256 bytes */
using polyvec128 = std::vector<u128, AlignedAllocator<u128, alignment_byte>>;
/** @brief Raw pointer to 64-bit unsigned polynomial coefficients */
using polydata = u64 *;

/**
 * @class IQuery
 * @brief Abstract interface for item or query data in EVI operation
 *
 * Defines the structure of an encoded query, including polynomial data,
 * metadata (dimension, degree, encoding type), and serialization methods.
 */
struct IQuery {
public:
    /** @brief Query dimension optimized for internal operations */
    u64 dim;
    /** @brief User-specified dimension for display */
    u64 show_dim;
    /** @brief Polynomial degree */
    u64 degree;
    /** @brief Total item count in query */
    u64 n;
    /** @brief Encoding type indicating ITEM or QUERY format */
    EncodeType encodeType;

    /** @brief Serialize this query into a byte buffer */
    virtual void serializeTo(std::vector<u8> &buf) const = 0;
    /** @brief Restore this query from a serialized byte buffer */
    virtual void deserializeFrom(const std::vector<u8> &buf) = 0;
    /** @brief Serialize this query into an output stream */
    virtual void serializeTo(std::ostream &stream) const = 0;
    /** @brief Restore this query from a serialized input stream */
    virtual void deserializeFrom(std::istream &stream) = 0;

    /**
     * @brief Access polynomial data from the index.
     * Retrieves a mutable reference to the polynomial buffer based on position and level:
     * - (0, 0): b_q (mod Q part of b)
     * - (0, 1): b_p (mod P part of b)
     * - (1, 0): a_q (mod Q part of a)
     * - (1, 1): a_p (mod P part of a)
     * @return Mutable reference to the selected polynomial buffer
     */
    virtual poly &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) = 0;
    /** @return Const reference to the selected polynomial buffer */
    virtual const poly &getPoly(const int pos, const int level,
                                std::optional<const int> index = std::nullopt) const = 0;

    /** @return Pointer to the polynomial coefficient data buffer */
    virtual polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) = 0;
    /** @return Const pointer to the polynomial coefficient data buffer */
    virtual polydata getPolyData(const int pos, const int level,
                                 std::optional<const int> index = std::nullopt) const = 0;

    /** @return Mutable reference to the full 128-bit polynomial vector buffer */
    virtual polyvec128 &getPoly() = 0;
    /** @return Pointer to the 128-bit polynomial coefficient data buffer */
    virtual u128 *getPolyData() = 0;

    /** @return Reference to the data type (e.g., CIPHER, PLAIN, SERIALIZED_CIPHER, SERIALIZED_PLAIN,) */
    virtual DataType &getDataType() = 0;
    /** @return current polynomial level of the query */
    virtual int &getLevel() = 0;
};

template <DataType T>
struct SingleBlock : IQuery {
public:
    SingleBlock(const int level);
    SingleBlock(const poly &a_q);
    SingleBlock(const poly &a_q, const poly &b_q);
    SingleBlock(const poly &a_q, const poly &a_p, const poly &b_q, const poly &b_p);

    SingleBlock(std::istream &stream);
    SingleBlock(std::vector<u8> &buf);

    poly &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) override;
    const poly &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) const override;
    polydata getPolyData(const int pos, const int leve, std::optional<const int> index = std::nullopt) override;
    polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) const override;

    void serializeTo(std::vector<u8> &buf) const override;
    void deserializeFrom(const std::vector<u8> &buf) override;
    void serializeTo(std::ostream &stream) const override;
    void deserializeFrom(std::istream &stream) override;

    DataType &getDataType() override {
        return dtype;
    }
    int &getLevel() override {
        return level_;
    }

    // For SerializedQuery instantiaton
    [[noreturn]] polyvec128 &getPoly() override {
        throw InvalidAccessError("Not compatible type to access to 128-bit array");
    }
    [[noreturn]] u128 *getPolyData() override {
        throw InvalidAccessError("Not compatible type to access to 128-bit array");
    }

private:
    DataType dtype;
    int level_;
    poly b_q_;
    poly b_p_;
    poly a_q_;
    poly a_p_;
};

template <DataType T>
struct SerializedSingleQuery : IQuery {
    SerializedSingleQuery(polyvec128 &ptxt);

    [[noreturn]] poly &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    [[noreturn]] const poly &getPoly(const int pos, const int level,
                                     std::optional<const int> index = std::nullopt) const override {

        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    [[noreturn]] polydata getPolyData(const int pos, const int leve,
                                      std::optional<const int> index = std::nullopt) override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    [[noreturn]] polydata getPolyData(const int pos, const int level,
                                      std::optional<const int> index = std::nullopt) const override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }

    polyvec128 &getPoly() override;
    u128 *getPolyData() override;

    // TODO!!!!!!
    void serializeTo(std::vector<u8> &buf) const override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    void deserializeFrom(const std::vector<u8> &buf) override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    void serializeTo(std::ostream &stream) const override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    void deserializeFrom(std::istream &stream) override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }

    DataType &getDataType() override {
        return dtype;
    }
    int &getLevel() override {
        return level_;
    }

private:
    DataType dtype;
    int level_;
    polyvec128 ptxt;
};

using SingleQuery = std::shared_ptr<IQuery>;
using Query = std::vector<SingleQuery>;

struct IData {
public:
    u64 dim;
    u64 degree;
    u64 n;

    virtual polyvec &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) = 0;
    virtual const polyvec &getPoly(const int pos, const int level,
                                   std::optional<const int> index = std::nullopt) const = 0;
    virtual polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) = 0;
    virtual polydata getPolyData(const int pos, const int level,
                                 std::optional<const int> index = std::nullopt) const = 0;

    virtual void serializeTo(std::vector<u8> &buf) const = 0;
    virtual void deserializeFrom(const std::vector<u8> &buf) = 0;
    virtual void serializeTo(std::ostream &stream) const = 0;
    virtual void deserializeFrom(std::istream &stream) = 0;

    virtual void setSize(const int size, std::optional<int> = std::nullopt) = 0;

    virtual DataType &getDataType() = 0;
    virtual int &getLevel() = 0;
};

template <DataType T>
struct Matrix : public IData {
public:
    Matrix(const int level);
    Matrix(polyvec q);
    Matrix(polyvec a_q, polyvec b_q);
    Matrix(polyvec a_q, polyvec a_p, polyvec b_q, polyvec b_p);

    polyvec &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) override;
    polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) override;
    const polyvec &getPoly(const int pos, const int level,
                           std::optional<const int> index = std::nullopt) const override;
    polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) const override;

    void serializeTo(std::vector<u8> &buf) const override;
    void deserializeFrom(const std::vector<u8> &buf) override;
    void serializeTo(std::ostream &stream) const override;
    void deserializeFrom(std::istream &stream) override;

    void setSize(const int size, std::optional<int> = std::nullopt) override;
    DataType &getDataType() override {
        return dtype;
    }
    int &getLevel() override {
        return level_;
    }

private:
    DataType dtype;
    int level_;
    polyvec a_q_;
    polyvec a_p_;
    polyvec b_q_;
    polyvec b_p_;
};

struct IPSearchResult {
    std::shared_ptr<IData> ip_;
#ifdef BUILD_WITH_HEAAN
    std::vector<HEaaN::Ciphertext> qf_;
#endif
};

// using DataState = std::vector<std::shared_ptr<IData>>;
using SearchResult = std::shared_ptr<IPSearchResult>;
using DataState = std::shared_ptr<IData>;
using Blob = std::vector<DataState>;

struct VariadicKeyType : std::shared_ptr<Matrix<DataType::CIPHER>> {
    VariadicKeyType() : std::shared_ptr<Matrix<DataType::CIPHER>>(std::make_shared<Matrix<DataType::CIPHER>>(LEVEL1)) {}
    VariadicKeyType(const VariadicKeyType &to_copy) : std::shared_ptr<Matrix<DataType::CIPHER>>(to_copy) {}
};

struct FixedKeyType : std::shared_ptr<SingleBlock<DataType::CIPHER>> {
    FixedKeyType()
        : std::shared_ptr<SingleBlock<DataType::CIPHER>>(std::make_shared<SingleBlock<DataType::CIPHER>>(LEVEL1)) {}
    FixedKeyType(const FixedKeyType &to_copy) : std::shared_ptr<SingleBlock<DataType::CIPHER>>(to_copy) {}
};

template <DataType T>
struct PolyData {
    void setSize(const int size);
    int getSize() const;
    polydata &getPolyData(const int pos, const int level, std::optional<int> idx = std::nullopt);

private:
    std::vector<polydata> a_q;
    std::vector<polydata> a_p;
    std::vector<polydata> b_q;
    std::vector<polydata> b_p;
};

template <DataType T>
using DeviceData = std::shared_ptr<PolyData<T>>;

} // namespace evi
