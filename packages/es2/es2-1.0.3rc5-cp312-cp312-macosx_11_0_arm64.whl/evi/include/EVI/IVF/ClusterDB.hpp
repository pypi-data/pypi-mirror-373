#pragma once
#include "HEaaNFR/CKKSTypes.hpp"
#include "HEaaNFR/Database.hpp"

#ifdef BUILD_WITH_HEAAN
#include "HEaaN/Ciphertext.hpp"
#endif

#include <algorithm>
#include <cstdint>
#include <deque>
#include <iostream>
#include <map>
#include <memory>
#include <utility>
#include <vector>

namespace HEaaNFR {

typedef struct MergedIndex {
    uint64_t total_n;
    uint64_t num_ctxt;
    std::set<std::pair<uint64_t, uint64_t>> indices;
} MergedIndex;

typedef struct SearchResult {
    std::vector<u64> total_n;
    std::vector<bool> bitset;
    std::vector<int> indices;
    std::shared_ptr<HEaaNFR::Ciphertext> cipher;
} SearchResult;

#ifdef BUILD_WITH_HEAAN
typedef struct SearchResultHEaaN {
    std::vector<int> total_n;
    std::vector<bool> bitset;
    std::vector<int> indices;
    std::vector<HEaaN::Ciphertext> cipher;
} SearchResultHEaaN;
#endif

typedef std::deque<MergedIndex> IndexQueue;
typedef std::map<u64, IndexQueue> QueueMap;

class CPUClusterDB {

public:
    CPUClusterDB() = delete;
    CPUClusterDB(const Context &context, const std::shared_ptr<HEaaNFR::Ciphertext> items);
    CPUClusterDB(const Context &context, const std::vector<std::shared_ptr<HEaaNFR::Ciphertext>> &items);
    // CPUClusterDB(const Context &context, std::vector<HEaaNFR::Database> &items);
    CPUClusterDB(const Context &context, const u32 rank);

    ~CPUClusterDB() = default;

    void store(const char *dir_path);
    void serializeTo(std::ostream &stream);
    void deserializeFrom(std::istream &stream);
    void addDatabase(const Database &ctxt);
    void append(const std::shared_ptr<SingleCiphertext> item, const int index);

    // TODO
    void load(const char *dir_path);
    u64 getItemCount(const int index) const;
    u64 getMaxId(const int index) const;
    std::vector<u64> &getSizeList();
    std::vector<u64> getSelectedSize(const std::vector<u64> &index) const;
    std::vector<u64> getNumCtxtList(const std::vector<u64> &index) const;
    u64 getNumCtxt(const u64 index) const;

    u64 getItemCount() const {
        return num_total_n_;
    }

    int getLevel() {
        return 1;
    }

    u64 getPadRank() const {
        return pad_dim_;
    }

    const Database &getDatabase(int index) const {
        return db_ctxt_[index];
    }

    QueueMap initIndexQueue(const std::vector<u64> &index) const;
    void mergeIndexQueue(QueueMap &index_queue) const;
    QueueMap mergeQueue(QueueMap &index_queue) const;

    std::unordered_map<u64, u64> getBitsetOffset(const std::vector<u64> &index) const;

    const Context context_;

    const std::vector<std::vector<u64>> &getOrderChanger() const {
        return order_changer;
    }
    void setOrderChanger(const std::vector<std::vector<u64>> &changer) {
        order_changer = changer;
    }

private:
    u64 dim_;
    u64 pad_dim_;
    u64 items_per_ctxt_;
    u64 num_total_n_ = 0;
    u64 max_key;
    std::vector<Database> db_ctxt_;
    std::vector<u64> size_list_;
    std::vector<std::vector<u64>> order_changer;
    std::unordered_map<u64, u64> idx_positions;
};
void bitset_change(const CPUClusterDB &db, const QueueMap &indexQueue, const std::vector<u64> &indices,
                   const bool *bitset, bool *bitset_out);
class ClusterDB {
public:
    ClusterDB() = delete;
    ClusterDB(const Context &context, const std::shared_ptr<HEaaNFR::Ciphertext> items);
    ClusterDB(const Context &context, const std::vector<std::shared_ptr<HEaaNFR::Ciphertext>> &items);
    // CPUClusterDB(const Context &context, std::vector<HEaaNFR::Database> &items);
    ClusterDB(const Context &context, const u32 rank);
    ~ClusterDB() = default;

    void store(const char *dir_path);
    void serializeTo(std::ostream &stream);
    void deserializeFrom(std::istream &stream);
    void addDatabase(const Shard &ctxt);
    void append(const std::shared_ptr<SingleCiphertext> item, const int index);
    // GPU Mem implementation
    void loadToGpu(int device_id);
    void loadCtxtGpu();
    void releaseCiphertextGPU();
    void appendCtxtToGPU(const int index);
    void appendCtxtGPU();
    void appendItemGPU();
    void appendItemGPU(const int index);
    void appendItemGPUAll();
    // TODO
    void load(const char *dir_path);
    u64 getItemCount(const int index) const;
    u64 getMaxId(const int index) const;
    std::vector<u64> &getSizeList();
    std::vector<u64> getSelectedSize(const std::vector<u64> &index) const;
    std::vector<u64> getNumCtxtList(const std::vector<u64> &index) const;
    u64 getNumCtxt(const u64 index) const;

    u64 getItemCount() const {
        return num_total_n_;
    }

    int getLevel() {
        return 1;
    }

    u64 getPadRank() const {
        return pad_dim_;
    }

    const Shard &getDatabase(int index) const {
        return db_ctxt_[index];
    }

    QueueMap initIndexQueue(const std::vector<u64> &index) const;
    void mergeIndexQueue(QueueMap &index_queue) const;
    QueueMap mergeQueue(QueueMap &index_queue) const;
    std::unordered_map<u64, u64> getBitsetOffset(const std::vector<u64> &index) const;

    const Context context_;

    const std::vector<std::vector<u64>> &getOrderChanger() const {
        return order_changer;
    }

private:
    u64 dim_;
    u64 pad_dim_;
    u64 items_per_ctxt_;
    u64 num_total_n_ = 0;
    u64 max_key = 0;
    std::vector<Shard> db_ctxt_;
    std::vector<u64> size_list_;
    std::vector<std::vector<u64>> order_changer;
    std::unordered_map<u64, u64> idx_positions;
    //(cluster_id, index in cluster the cluster) -> index in the Clusterbase.
};
void bitset_change(const ClusterDB &db, const QueueMap &indexQueue, const std::vector<u64> &indices, const bool *bitset,
                   bool *bitset_out);
} // namespace HEaaNFR
