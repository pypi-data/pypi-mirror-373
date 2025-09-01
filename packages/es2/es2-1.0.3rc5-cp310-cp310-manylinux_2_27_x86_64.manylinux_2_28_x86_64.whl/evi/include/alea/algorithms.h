#ifndef ALEA_ALGORITHMS_H
#define ALEA_ALGORITHMS_H

/**
 * @file algorithms.h
 * @brief Header file defining the supported cryptographic algorithms for ALEA.
 *
 * This file contains the enumeration of cryptographic algorithms that can be
 * used with the ALEA library. It is included in the main header file `alea.h`.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @enum `alea_algo`
 * @brief Enumeration of supported ALEA cryptographic algorithms.
 * This enum defines the available algorithms for use in the ALEA library.
 *
 * @var `ALEA_ALGORITHM_SHAKE128`
 *      Use the SHAKE128 extendable-output function.
 * @var `ALEA_ALGORITHM_SHAKE256`
 *      Use the SHAKE256 extendable-output function.
 */
typedef enum {
  ALEA_ALGORITHM_SHAKE128,
  ALEA_ALGORITHM_SHAKE256,
} alea_algo;

#ifdef __cplusplus
}
#endif

#endif // ALEA_ALGORITHMS_H
