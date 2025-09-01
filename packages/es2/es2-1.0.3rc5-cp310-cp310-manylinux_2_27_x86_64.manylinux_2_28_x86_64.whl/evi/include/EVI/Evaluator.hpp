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

#include "EVI/CKKSTypes.hpp"
#include "EVI/ComputeBuffer.hpp"
#include "EVI/Context.hpp"
#include "EVI/Index.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/NTT.hpp"
#include "EVI/Processor.hpp"
#include "EVI/Type.hpp"
#include "utils/Exceptions.hpp"

#ifdef BUILD_WITH_HEAAN
#include "HEaaN/Ciphertext.hpp"
#include "HEaaN/Message.hpp"
#endif

#ifdef ENABLE_IVF
#include "evi/IVF/ClusterDB.hpp"
#endif

#include <functional>

#ifdef __CUDACC__
#include <cuda_runtime.h>
#endif

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <type_traits>
#include <utility>
#include <variant>
#include <vector>

namespace evi {

/** @ingroup EvaluatorAPI
 * @brief Internal evaluator interface for homomorphic evaluation
 *
 * Defines the abstract interface for loading evaluation keys,
 * performing homomorphic queries, and managing GPU/CPU resources.
 */
class EvaluatorImpl {
public:
    virtual ~EvaluatorImpl() = default;

    /**
     * @brief Load evaluation key from a KeyPack object.
     * @param keypack The KeyPack containing evaluation keys.
     */
    virtual void loadEvalKey(const evi::KeyPack &keypack) = 0;

    /**
     * @brief Load evaluation key from an input stream.
     * @param stream Input stream containing serialized keys.
     */
    virtual void loadEvalKey(std::istream &stream) = 0;

    /**
     * @brief Load evaluation key from a file path.
     * @param path Path to the evaluation key file.
     */
    virtual void loadEvalKey(const std::string &path) = 0;

    /**
     * @brief Perform a homomorphic search query.
     *
     * @param index Encrypted index.
     * @param query Encrypted query.
     * @param ip_only If true, performs only inner product computation.
     * @param buffer Optional compute buffer for temporary storage.
     * @return SearchResult The result of the homomorphic search.
     */
    virtual SearchResult search(const Index &index, const Query query, bool ip_only = true,
                                std::optional<ComputeBuffer> buffer = std::nullopt) = 0;
};
/** @} */ // end of EvaluatorAPI

template <DeviceType D, EvalMode M>
class Evaluator;

template <EvalMode M>
class Evaluator<DeviceType::CPU, M> : public EvaluatorImpl {
public:
    Evaluator(const ComputeBuffer &buffer);
    Evaluator(const evi::Context &context, std::optional<bool> buffer_alloc = std::nullopt);

    void loadEvalKey(const evi::KeyPack &pack) override;
    void loadEvalKey(std::istream &stream) override;
    void loadEvalKey(const std::string &path) override;

    // void loadSharedAKey(const evi::KeyPack &keypack);
    // void loadCCSharedAKey(const evi::KeyPack &keypack);

    SearchResult search(const Index &db, const Query query, bool ip_only = true,
                        std::optional<ComputeBuffer> buffer = std::nullopt) override;

    ~Evaluator() = default;

    // std::shared_ptr<evi::Ciphertext> PCSearchQ(evi::Database &db, const std::shared_ptr<SinglePlaintext>
    // query,
    //                                                bool ntt_out);
    // std::shared_ptr<evi::Ciphertext> PCSearchQMS(evi::DatabaseSharedA &db,
    //                                                  const std::shared_ptr<SinglePlaintext> query, bool ntt_out);
    //
    // std::shared_ptr<evi::Ciphertext> PCSearchQP(evi::Database &db, const std::shared_ptr<SinglePlaintext>
    // query,
    //                                                 bool ntt_out);
    //
    // std::shared_ptr<evi::Ciphertext> CPSearchQ(evi::Plaintextbase &db,
    //                                                const std::shared_ptr<SingleCiphertext> query, bool ntt_out);
    //
    // std::shared_ptr<evi::Ciphertext> CPSearchQP(evi::Plaintextbase &db,
    //                                                 const std::shared_ptr<SingleCiphertext> query, bool ntt_out);

protected:
    ComputeBuffer buf;

    SearchResult DO_Base_IP(const Index &db, const Query query, ComputeBuffer buffer);

    SearchResult DO_RMP_IP(const Index &db, const Query query, ComputeBuffer buffer);

    SearchResult DO_SHARED_A_IP(const Index &db, const Query query, ComputeBuffer buffer);

    SearchResult DO_RMP_SHARED_A_IP(const Index &db, const Query query, ComputeBuffer buffer);

    void initialize(const u32 rank);
    void release();

    void tensorMadQ(const span<u64> op1_a, const span<u64> op1_b, const span<u64> op2_a, const span<u64> op2_b,
                    span<u64> res_a, span<u64> res_b, span<u64> res_c);
    void tensorModQ(const span<u64> op1_a, const span<u64> op1_b, const span<u64> op2_a, const span<u64> op2_b,
                    span<u64> res_a, span<u64> res_b, span<u64> res_c);

    void tensorModP(const span<u64> op1_a, const span<u64> op1_b, const span<u64> op2_a, const span<u64> op2_b,
                    span<u64> res_a, span<u64> res_b, span<u64> res_c);

    void rescale(const span<u64> in, span<u64> out, u64 mod_in, u64 mod_out, u64 barr_out, u64 two_mod_out,
                 u64 prod_inv);

    void relinearize(const span<u64> op_a, const span<u64> op_b, const span<u64> op_c, span<u64> res_a,
                     span<u64> res_b);
    void relinearizeParallel(evi::span<u64>, evi::span<u64>, evi::span<u64>, evi::span<u64>, evi::span<u64>,
                             evi::span<u64>, evi::span<u64>);

    FixedKeyType relinKey;
    VariadicKeyType modPackKey;

    VariadicKeyType sharedAModPackKey;
    VariadicKeyType CCSharedAModPackKey;
    // polyvec shared_a_mod_pack_keys_a_q_;
    // polyvec shared_a_mod_pack_keys_a_p_;
    // polyvec shared_a_mod_pack_keys_b_q_;
    // polyvec shared_a_mod_pack_keys_b_p_;
    // polyvec cc_shared_a_mod_pack_keys_a_q_;
    // polyvec cc_shared_a_mod_pack_keys_a_p_;
    // polyvec cc_shared_a_mod_pack_keys_b_q_;
    // polyvec cc_shared_a_mod_pack_keys_b_p_;

    u32 log_pad_rank_;
    u32 rank_;
    u32 pad_rank_;
    u32 inner_rank_;
    u32 num_input_cipher_;
    u32 templates_per_degree_;
    bool key_loaded_;
};

template <EvalMode M>
class Evaluator<DeviceType::GPU, M> : public EvaluatorImpl {
public:
    Evaluator(const evi::Context &context, std::optional<bool> buffer_alloc = std::nullopt);
    Evaluator(const ComputeBuffer &buffer);
    ~Evaluator() override;

    void loadEvalKey(const evi::KeyPack &keypack) override;
    void loadEvalKey(std::istream &stream) override;
    void loadEvalKey(const std::string &path) override;

    SearchResult search(const Index &db, const Query query, bool ip_only = true,
                        std::optional<ComputeBuffer> buff = std::nullopt) override;

    // #ifdef BUILD_WITH_HEAAN
    //     template <BatchType T>
    //     void CCSearch(evi::HEDatabase<T> &db, const std::shared_ptr<SingleCiphertext> query,
    //                   std::vector<HEaaN::Ciphertext> &heaan_ctxt, const HEaaN::Context &heaan_context,
    //                   std::shared_ptr<GPUComputeBuffer> buff);
    //
    //     template <BatchType T>
    //     void PCSearchQP(evi::HEDatabase<T> &db, const std::shared_ptr<SinglePlaintext> query,
    //                     std::vector<HEaaN::Ciphertext> &heaan_ctxt, const HEaaN::Context &heaan_context);
    //     template <BatchType T>
    //     void PCSearchQP(evi::HEDatabase<T> &db, const std::shared_ptr<SinglePlaintext> query,
    //                     std::vector<HEaaN::Ciphertext> &heaan_ctxt, const HEaaN::Context &heaan_context,
    //                     std::shared_ptr<GPUComputeBuffer> buff);
    // #endif
    //
    // #ifdef ENABLE_IVF
    //     std::shared_ptr<Ciphertext> mergedIndexSearch(const ClusterDB &db, const
    //     std::shared_ptr<SingleCiphertext> query,
    //                                                   const std::vector<u64> &indices);
    // #ifdef BUILD_WITH_HEAAN
    //     void mergedIndexSearch(const ClusterDB &db, const std::shared_ptr<SinglePlaintext> query,
    //                            std::vector<HEaaN::Ciphertext> &heaan_ctxt, const std::vector<u64> &indices,
    //                            const HEaaN::Context &heaan_context, std::shared_ptr<GPUComputeBuffer> buff);
    //     void innerMergedIndexSearchQP(const ClusterDB &db, const QueueMap &indexQueue,
    //                                   std::vector<HEaaN::Ciphertext> &heaan_ctxt, const HEaaN::Context
    //                                   &heaan_context, std::shared_ptr<GPUComputeBuffer> buff, const u64
    //                                   num_batch);
    //
    //     void innerMergedIndexSearchQP(std::shared_ptr<SearchResultHEaaN> res,
    //     std::vector<std::shared_ptr<ClusterDB>> &db,
    //                                   const std::vector<std::shared_ptr<SinglePlaintext>> query,
    //                                   const std::vector<std::vector<u64>> &indices,
    //                                   const std::vector<std::vector<bool>> &ref, bool ntt_out,
    //                                   std::shared_ptr<GPUComputeBuffer> buff, const HEaaN::Context
    //                                   &heaan_context);
    //     std::shared_ptr<SearchResultHEaaN> mergedIndexSearch(std::vector<std::shared_ptr<ClusterDB>> &db,
    //                                                          const std::vector<std::shared_ptr<SinglePlaintext>>
    //                                                          query, const std::vector<std::vector<u64>> &indices,
    //                                                          const std::vector<std::vector<bool>> &bitset, bool
    //                                                          ntt_out, std::shared_ptr<GPUComputeBuffer> buff,
    //                                                          const HEaaN::Context &heaan_context);
    //
    // #endif
    //
    //     std::shared_ptr<Ciphertext> mergedIndexSearch(std::vector<ClusterDB> &db,
    //                                                   const std::shared_ptr<SingleCiphertext> query,
    //                                                   const std::vector<std::vector<u64>> &indices);
    //
    //     std::shared_ptr<Ciphertext> mergedIndexSearch(const ClusterDB &db, const std::shared_ptr<SinglePlaintext>
    //     query,
    //                                                   const std::vector<u64> &indices, bool ntt_out);
    //
    //     std::shared_ptr<Ciphertext> mergedIndexSearch(std::vector<ClusterDB> &db,
    //                                                   const std::shared_ptr<SinglePlaintext> query,
    //                                                   const std::vector<std::vector<u64>> &indices, bool
    //                                                   ntt_out);
    //
    //     std::shared_ptr<SearchResult> mergedIndexSearch(std::vector<ClusterDB> &db,
    //                                                     const std::vector<std::shared_ptr<SinglePlaintext>>
    //                                                     query, const std::vector<std::vector<u64>> &indices,
    //                                                     const std::vector<std::vector<bool>> &ref, bool ntt_out);
    //
    //     // Ciphertext Lv0
    //     void innerMergedIndexSearch(const ClusterDB &db, const QueueMap &indexQueue, u64 *ctxt_out_a, u64
    //     *ctxt_out_b,
    //                                 const u64 num_batch);
    //
    //     void innerMergedIndexSearch(std::vector<ClusterDB> &db, std::vector<QueueMap> &indexQueue, u64
    //     *ctxt_out_a,
    //                                 u64 *ctxt_out_b, const u64 num_batch);
    //
    //     // Plaintext Lv0
    //     void innerMergedIndexSearchQ(const ClusterDB &db, const QueueMap &indexQueue, u64 *ctxt_out_a, u64
    //     *ctxt_out_b,
    //                                  bool ntt_out, const u64 num_batch);
    //
    //     void innerMergedIndexSearchQ(std::vector<ClusterDB> &db, std::vector<QueueMap> &indexQueue, u64
    //     *ctxt_out_a,
    //                                  u64 *ctxt_out_b, bool ntt_out, const u64 num_batch);
    //
    //     // Plaintext Lv1
    //     void innerMergedIndexSearchQP(const ClusterDB &db, const QueueMap &indexQueue, u64 *ctxt_out_a, u64
    //     *ctxt_out_b,
    //                                   bool ntt_out, const u64 num_batch);
    //
    //     void innerMergedIndexSearchQP(std::vector<ClusterDB> &db, std::vector<QueueMap> &indexQueue, u64
    //     *ctxt_out_a,
    //                                   u64 *ctxt_out_b, bool ntt_out, const u64 num_batch);
    //
    //     void innerMergedIndexSearchQP(std::shared_ptr<SearchResult> res, std::vector<ClusterDB> &db,
    //                                   const std::vector<std::shared_ptr<SinglePlaintext>> query,
    //                                   const std::vector<std::vector<u64>> &indices,
    //                                   const std::vector<std::vector<bool>> &ref, bool ntt_out);
    // #endif

    u32 getRank() const;
    int getCurrentDevice() const;

protected:
    ComputeBuffer buf;
    const evi::HEProcessor proc;

    void initialize(const u32 rank);
    void release();

    void modDownGpu(u64 *poly_q, u64 *poly_p);
    void relinearize(ComputeBuffer buf, const u64 *in_a, const u64 *in_b, const u64 *in_c, u64 *out_a, u64 *out_b);
    void doRescaleAndModPack(ComputeBuffer buf, const u64 *a_q, const u64 *a_p, const u64 *b_q, const u64 *b_p,
                             u64 *res_a, u64 *res_b, bool ntt_out);
    void doModPack(ComputeBuffer buf, const u64 *a_q, const u64 *b_q, u64 *res_a, u64 *res_b, bool ntt_out);

    u64 *relin_key_a_q_gpu_;
    u64 *relin_key_a_p_gpu_;
    u64 *relin_key_b_q_gpu_;
    u64 *relin_key_b_p_gpu_;
    u64 *mod_pack_keys_a_q_gpu_;
    u64 *mod_pack_keys_a_p_gpu_;
    u64 *mod_pack_keys_b_q_gpu_;
    u64 *mod_pack_keys_b_p_gpu_;

    u64 **rest_;
    u64 **shf_;
    u64 **full_;
    u64 *shift_list;

    u32 log_pad_rank_;
    u32 rank_;
    u32 pad_rank_;
    u32 inner_rank_;
    u32 num_input_cipher_;
    u32 templates_per_degree_;

    int device_id_;
    bool key_loaded_;
};

using HomEvaluator = std::shared_ptr<EvaluatorImpl>;

/**
 * @brief Factory function to create a homomorphic evaluator from an encryption context
 *
 * Initializes a CPU or GPU evaluator depending on the context device type.
 * Loads required parameters for homomorphic search.
 *
 * @param context EVI context used for key initialization and selecting the operation device
 * @return HomEvaluator Shared pointer to a CPU/GPU evaluator
 */
HomEvaluator createHomEvaluator(const evi::Context &context);

/**
 * @brief Factory function to create a homomorphic evaluator from an existing compute buffer
 *
 * Creates an evaluator using a preallocated buffer for improved performance.
 *
 * @param buf Preallocated compute buffer
 * @return HomEvaluator Shared pointer to a CPU/GPU evaluator
 */
HomEvaluator createHomEvaluator(const ComputeBuffer &buf);

} // namespace evi
