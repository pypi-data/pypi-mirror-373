#ifndef ALEA_ALEA_H
#define ALEA_ALEA_H

/**
 * @file alea.h
 * @brief Public API for the ALEA cryptographically secure random number
 * generator library.
 *
 * This header defines the interface for the ALEA random number generator (RNG)
 * library, providing functions for initialization, reseeding, random number
 * generation, and sampling from various distributions. The API supports
 * generating random bytes, 32-bit and 64-bit integers (optionally within a
 * specified range), as well as sampling arrays of integers with specific
 * properties such as Hamming weight, centered binomial, and discrete Gaussian
 * distributions.
 *
 * The ALEA library is designed for cryptographic and statistical applications
 * requiring high-quality randomness. It supports multiple algorithm variants
 * (e.g., SHAKE128, SHAKE256) and allows for flexible seeding and state
 * management.
 *
 * @note All functions that operate on an `alea_state` require the state to be
 * properly initialized using `alea_init`. After use, resources should be
 * released with `alea_free`.
 *
 * @section Return Codes
 * The `alea_return` enumeration defines possible return values for ALEA
 * functions, indicating the status of the operation (success, generic error,
 * not implemented, or free error).
 *
 * @section Thread Safety
 * Unless otherwise specified, the ALEA API is not guaranteed to be thread-safe.
 * Each thread should use its own `alea_state` instance.
 *
 * @section Usage Example
 * @code
 * uint8_t seed[ALEA_SEED_SIZE_SHAKE128] = { ... };
 * alea_state *state = alea_init(seed, ALEA_ALGORITHM_SHAKE128);
 * if (state) {
 *     uint64_t rnd = alea_get_random_uint64(state);
 *     alea_free(state);
 * }
 * @endcode
 */

#include "alea/algorithms.h"

#include <stddef.h>
#include <stdint.h>

#if defined(_WIN32) || defined(_WIN64)
#ifdef ALEA_EXPORTS
#define ALEA_API __declspec(dllexport)
#else
#define ALEA_API __declspec(dllimport)
#endif
#else
#define ALEA_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @enum `alea_return`
 * @brief Return codes used by the ALEA library functions.
 *
 * This enumeration defines the possible return values for ALEA library
 * functions, indicating the status of the operation.
 *
 * @var `ALEA_RETURN_OK`
 *      The operation completed successfully.
 * @var `ALEA_RETURN_BAD_GENERIC`
 *      A generic error occurred during the operation.
 * @var `ALEA_RETURN_BAD_NOT_IMPLEMENTED`
 *      The requested operation is not implemented.
 * @var `ALEA_RETURN_BAD_MALLOC_FAILURE`
 *      An error occurred during memory allocation (malloc failure).
 * @var `ALEA_RETURN_BAD_FREE`
 *      An error occurred during a free or deallocation operation.
 */
typedef enum {
  ALEA_RETURN_OK,
  ALEA_RETURN_BAD_GENERIC,
  ALEA_RETURN_BAD_NOT_IMPLEMENTED,
  ALEA_RETURN_BAD_MALLOC_FAILURE,
  ALEA_RETURN_BAD_FREE,
} alea_return;

#ifndef ALEA_STATE_IMPLEMENTATION
typedef void alea_state;
#endif

#define ALEA_SEED_SIZE_SHAKE128 32 // bytes
#define ALEA_SEED_SIZE_SHAKE256 64 // bytes

/**
 * @brief Initializes a new ALEA random number generator state.
 *
 * This function creates and initializes an ALEA RNG state using the provided
 * seed and algorithm.
 *
 * @param seed Pointer to the seed data used for initialization.
 * @param algorithm The ALEA algorithm variant to use. See algorithms.h for
 * available algorithms.
 * The seed size must match the expected size for the specified algorithm:
 * - `ALEA_ALGORITHM_SHAKE128`: 32 bytes
 * - `ALEA_ALGORITHM_SHAKE256`: 64 bytes
 * @return Pointer to the initialized alea_state structure, or `NULL` on
 * failure.
 */
ALEA_API alea_state *alea_init(const uint8_t *const seed,
                               const alea_algo algorithm);

/**
 * @brief Frees the resources associated with the given alea_state.
 *
 * This function releases any memory or resources allocated for the specified
 * `alea_state`. After calling this function, the state pointer should not be
 * used unless it is reinitialized.
 *
 * @param state Pointer to the `alea_state` to be freed.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_free(alea_state *state);

/**
 * @brief Reseeds the ALEA RNG state with a new seed.
 *
 * This function updates the internal state of the ALEA RNG with a new seed.
 * The seed size must match the expected size for the specified algorithm:
 * - `ALEA_ALGORITHM_SHAKE128`: 32 bytes
 * - `ALEA_ALGORITHM_SHAKE256`: 64 bytes
 *
 * @param state Pointer to the `alea_state` to be reseeded.
 * @param seed Pointer to the new seed data.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_reseed(alea_state *state, const uint8_t *const seed);

/**
 * @brief Generates random bytes and stores them in the provided destination
 * buffer.
 *
 * This function fills the `dst` buffer with `dst_len` random bytes generated
 * by the ALEA RNG state.
 *
 * @param state Pointer to the `alea_state` used for random number generation.
 * @param dst Pointer to the destination buffer where random bytes will be
 * stored.
 * @param dst_len The number of random bytes to generate and store in `dst`.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_get_random_bytes(alea_state *state,
                                           uint8_t *const dst,
                                           const size_t dst_len);

/**
 * @brief Generates a random 64-bit unsigned integer.
 *
 * This function retrieves a random 64-bit unsigned integer from the ALEA RNG
 * state.
 *
 * @param state Pointer to the `alea_state` used for random number generation.
 * @return A random 64-bit unsigned integer.
 */
ALEA_API uint64_t alea_get_random_uint64(alea_state *state);

/**
 * @brief Generates a random 32-bit unsigned integer.
 *
 * This function retrieves a random 32-bit unsigned integer from the ALEA RNG
 * state.
 *
 * @param state Pointer to the `alea_state` used for random number generation.
 * @return A random 32-bit unsigned integer.
 */
ALEA_API uint32_t alea_get_random_uint32(alea_state *state);

/**
 * @brief Generates a random 64-bit unsigned integer within a specified range.
 *
 * This function retrieves a random 64-bit unsigned integer from the ALEA RNG
 * state, ensuring that the value is within the interval [0, `range`).
 *
 * @param state Pointer to the `alea_state` used for random number generation.
 * @param range The upper limit of the range (exclusive).
 * @return A random 64-bit unsigned integer in the range [0, `range`).
 */
ALEA_API uint64_t alea_get_random_uint64_in_range(alea_state *state,
                                                  const uint64_t range);

/**
 * @brief Generates a random 32-bit unsigned integer within a specified range.
 *
 * This function retrieves a random 32-bit unsigned integer from the ALEA RNG
 * state, ensuring that the value is within the interval [0, `range`).
 *
 * @param state Pointer to the `alea_state` used for random number generation.
 * @param range The upper limit of the range (exclusive).
 * @return A random 32-bit unsigned integer in the range [0, `range`).
 */
ALEA_API uint32_t alea_get_random_uint32_in_range(alea_state *state,
                                                  const uint32_t range);

/**
 * @brief Generates an array of random 64-bit unsigned integers.
 *
 * This function fills the `dst` array with `dst_len` random 64-bit unsigned
 * integers generated by the ALEA RNG state.
 *
 * @details A reference implementation of this function would be:
 * ```c
 * for (size_t i = 0; i < dst_len; ++i) {
 *     dst[i] = alea_get_random_uint64(state);
 * }
 * ```
 *
 * @param state Pointer to the `alea_state` used for random number generation.
 * @param dst Pointer to the destination array where random integers will be
 * stored.
 * @param dst_len The number of random integers to generate and store in `dst`.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_get_random_uint64_array(alea_state *state,
                                                  uint64_t *const dst,
                                                  const size_t dst_len);

/**
 * @brief Generates an array of random 32-bit unsigned integers.
 *
 * This function fills the `dst` array with `dst_len` random 32-bit unsigned
 * integers generated by the ALEA RNG state.
 *
 * @details A reference implementation of this function would be:
 * ```c
 * for (size_t i = 0; i < dst_len; ++i) {
 *     dst[i] = alea_get_random_uint32(state);
 * }
 * ```
 *
 * @param state Pointer to the `alea_state` used for random number generation.
 * @param dst Pointer to the destination array where random integers will be
 * stored.
 * @param dst_len The number of random integers to generate and store in `dst`.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_get_random_uint32_array(alea_state *state,
                                                  uint32_t *const dst,
                                                  const size_t dst_len);

/**
 * @brief Fills an array with random 64-bit unsigned integers within a specified
 * range.
 *
 * This function generates random numbers using the provided alea_state and
 * stores them in the destination array. Each generated number will be in the
 * range [0, range).
 *
 * @details A reference implementation of this function would be:
 * ```c
 * for (size_t i = 0; i < dst_len; ++i) {
 *     dst[i] = alea_get_random_uint64_in_range(state, range);
 * }
 * ```
 *
 * @param state Pointer to the `alea_state` structure used for random number
 * generation.
 * @param dst Pointer to the destination array where random numbers will be
 * stored.
 * @param dst_len Number of elements to fill in the destination array.
 * @param range Upper bound (exclusive) for the generated random numbers.
 * @return An `alea_return` value indicating success or failure of the
 * operation.
 */
ALEA_API alea_return alea_get_random_uint64_array_in_range(
    alea_state *state, uint64_t *const dst, const size_t dst_len,
    const uint64_t range);

/**
 * @brief Fills an array with random 32-bit unsigned integers within a specified
 * range.
 *
 * This function generates random numbers using the provided alea_state and
 * writes them into the destination array. Each generated number will be in the
 * range [0, range).
 *
 *
 * @details A reference implementation of this function would be:
 * ```c
 * for (size_t i = 0; i < dst_len; ++i) {
 *     dst[i] = alea_get_random_uint32_in_range(state, range);
 * }
 * ```
 *
 * @param state Pointer to the `alea_state` structure used for random number
 * generation.
 * @param dst Pointer to the destination array where random numbers will be
 * stored.
 * @param dst_len Number of random numbers to generate (length of the
 * destination array).
 * @param range The exclusive upper bound for generated random numbers. Each
 * number will be in [0, range).
 * @return An `alea_return` value indicating success or failure of the
 * operation.
 */
ALEA_API alea_return alea_get_random_uint32_array_in_range(
    alea_state *state, uint32_t *const dst, const size_t dst_len,
    const uint32_t range);

/**
 * @brief Fills an array with random 64-bit integers of specified Hamming
 * weight.
 *
 * This function generates random 64-bit integers where each integer contains
 * exactly `hwt` nonzero entries, with the nonzero values being either 1 or -1
 * (equidistributed), and the remaining entries are zero. The positions and
 * signs of the nonzero values are chosen uniformly at random.
 *
 * @param state Pointer to the `alea_state` structure representing the RNG
 * state.
 * @param dst Pointer to the destination array where random integers will be
 * stored.
 * @param dst_len The number of 64-bit integers to generate and store in the
 * destination array.
 * @param hwt The Hamming weight (number of nonzero entries set to ±1) for each
 * integer.
 * @return An `alea_return` code indicating success or failure of the
 * operation.
 */
ALEA_API alea_return alea_sample_hwt_int64_array(alea_state *state,
                                                 int64_t *const dst,
                                                 const size_t dst_len,
                                                 const int hwt);

/**
 * @brief Fills an array with random 32-bit integers of specified Hamming
 * weight.
 *
 * This function generates random 32-bit integers where each integer contains
 * exactly `hwt` nonzero entries, with the nonzero values being either 1 or -1
 * (equidistributed), and the remaining entries are zero. The positions and
 * signs of the nonzero values are chosen uniformly at random.
 *
 * @param state Pointer to the `alea_state` structure representing the RNG
 * state.
 * @param dst Pointer to the destination array where random integers will be
 * stored.
 * @param dst_len The number of 32-bit integers to generate and store in the
 * destination array.
 * @param hwt The Hamming weight (number of nonzero entries set to ±1) for each
 * integer.
 * @return An `alea_return` code indicating success or failure of the
 * operation.
 */
ALEA_API alea_return alea_sample_hwt_int32_array(alea_state *state,
                                                 int32_t *const dst,
                                                 const size_t dst_len,
                                                 const int hwt);

/**
 * @brief Fills the destination array with random 64-bit integers sampled from a
 * centered binomial distribution.
 *
 * This function generates `dst_len` random 64-bit integers, each sampled from a
 * centered binomial distribution (CBD). The results are written to the array
 * pointed to by `dst`. The function uses the provided `state` for random number
 * generation.
 *
 * @details A _centered binomial distribution_ (CBD) is a binomial distribution
 * that is symmetric around its mean. Essentially, this can be understood as
 * a binomial distribution with a probability of success p = 0.5, i.e., coin
 * tosses. As the number of flips increases, the distribution approaches a
 * normal distribution.
 *
 * In this function, we sample integers from the binomial distribution Bin(2 *
 * n, 0.5), shifted to have a mean of zero, where n is `cbd_num_flips`. The
 * resulting integers will be in the range [-n, n]. For large n, the
 * distribution approaches a normal distribution with mean zero and standard
 * deviation sqrt(n/2). For example, if `cbd_num_flips` is 21, the function will
 * generate integers approximately from the normal distribution with mean 0 and
 * standard deviation 3.24.
 *
 * Algorithmically, this can be implemented by sampling from two independent
 * binomial distributions Bin(n, 0.5) and subtracting the second sample from the
 * first.
 *
 * @param state Pointer to the `alea_state` structure representing the RNG
 * state.
 * @param dst Pointer to the destination array where the sampled integers will
 * be stored.
 * @param dst_len Number of elements to generate and store in the destination
 * array.
 * @param cbd_num_flips The number of coin flips in a single instance. As
 * discussed in the details section, we sample from two such instances and
 * subtract one from the other. This effectively gives us a centered binomial
 * distribution with mean zero and a range approximately from `-cbd_num_flips`
 * to `cbd_num_flips`.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_sample_cbd_int64_array(alea_state *state,
                                                 int64_t *const dst,
                                                 const size_t dst_len,
                                                 const size_t cbd_num_flips);

/**
 * @brief Fills the destination array with random 32-bit integers sampled from a
 * centered binomial distribution.
 *
 * This function generates `dst_len` random 32-bit integers, each sampled from a
 * centered binomial distribution (CBD). The results are written to the array
 * pointed to by `dst`. The function uses the provided `state` for random number
 * generation.
 *
 * @details A _centered binomial distribution_ (CBD) is a binomial distribution
 * that is symmetric around its mean. Essentially, this can be understood as
 * a binomial distribution with a probability of success p = 0.5, i.e., coin
 * tosses. As the number of flips increases, the distribution approaches a
 * normal distribution.
 *
 * In this function, we sample integers from the binomial distribution Bin(2 *
 * n, 0.5), shifted to have a mean of zero, where n is `cbd_num_flips`. The
 * resulting integers will be in the range [-n, n]. For large n, the
 * distribution approaches a normal distribution with mean zero and standard
 * deviation sqrt(n/2). For example, if `cbd_num_flips` is 21, the function will
 * generate integers approximately from the normal distribution with mean 0 and
 * standard deviation 3.24.
 *
 * Algorithmically, this can be implemented by sampling from two independent
 * binomial distributions Bin(n, 0.5) and subtracting the second sample from the
 * first.
 *
 * @param state Pointer to the `alea_state` structure representing the RNG
 * state.
 * @param dst Pointer to the destination array where the sampled integers will
 * be stored.
 * @param dst_len Number of elements to generate and store in the destination
 * array.
 * @param cbd_num_flips The number of coin flips in a single instance. As
 * discussed in the details section, we sample from two such instances and
 * subtract one from the other. This effectively gives us a centered binomial
 * distribution with mean zero and a range approximately from `-cbd_num_flips`
 * to `cbd_num_flips`.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_sample_cbd_int32_array(alea_state *state,
                                                 int32_t *const dst,
                                                 const size_t dst_len,
                                                 const size_t cbd_num_flips);

/**
 * @brief Fills the destination array with random 64-bit integers sampled from a
 * rounded Gaussian (normal) distribution.
 *
 * This function generates `dst_len` random 64-bit integers, each sampled from a
 * rounded Gaussian distribution with mean zero and the specified standard
 * deviation (`stdev`). The results are written to the array pointed to by
 * `dst`. The function uses the provided `state` for random number generation.
 *
 * @param state Pointer to the `alea_state` structure representing the RNG
 * state.
 * @param dst Pointer to the destination array where the sampled integers will
 * be stored.
 * @param dst_len Number of elements to generate and store in the destination
 * array.
 * @param stdev Standard deviation of the Gaussian distribution.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_sample_gaussian_int64_array(alea_state *state,
                                                      int64_t *const dst,
                                                      const size_t dst_len,
                                                      const double stdev);

/**
 * @brief Fills the destination array with random 32-bit integers sampled from a
 * rounded Gaussian (normal) distribution.
 *
 * This function generates `dst_len` random 32-bit integers, each sampled from a
 * rounded Gaussian distribution with mean zero and the specified standard
 * deviation (`stdev`). The results are written to the array pointed to by
 * `dst`. The function uses the provided `state` for random number generation.
 *
 * @param state Pointer to the `alea_state` structure representing the RNG
 * state.
 * @param dst Pointer to the destination array where the sampled integers will
 * be stored.
 * @param dst_len Number of elements to generate and store in the destination
 * array.
 * @param stdev Standard deviation of the Gaussian distribution.
 * @return An `alea_return` code indicating success or failure of the operation.
 */
ALEA_API alea_return alea_sample_gaussian_int32_array(alea_state *state,
                                                      int32_t *const dst,
                                                      const size_t dst_len,
                                                      const double stdev);

/**
  * @brief Generates a key using the HMAC-based Key Derivation Function (HKDF).
  *
  * This function implements the HKDF algorithm as defined in RFC 5869, using
  * HMAC with SHA-256 as the underlying pseudorandom function (PRF).
  * @param ikm Pointer to the input key material (IKM).
  * @param ikm_len Length of the input key material in bytes.
  * @param salt Pointer to the optional salt value. If NULL, a default salt is used.
  * @param salt_len Length of the salt in bytes. If 0, a default salt is used.
  * @param info Pointer to the optional context and application-specific information.
  * @param info_len Length of the info in bytes. If 0, no info is used.
  * @param okm Pointer to the output key material (OKM) buffer.
  * @param okm_len Length of the output key material in bytes. 
  * Must be less than or equal to 255 * SHA3_256_OUTLEN = 8160.
  * @return An `alea_return` code indicating success or failure of the operation.
*/
ALEA_API alea_return alea_hkdf(const uint8_t *ikm, size_t ikm_len,
                              const uint8_t *salt, size_t salt_len,
                              const uint8_t *info, size_t info_len,
                              uint8_t *okm, size_t okm_len);

#ifdef __cplusplus
}
#endif
#endif // ALEA_ALEA_H
