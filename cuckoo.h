#ifndef CUCKOO_H
#define CUCKOO_H

#include <vector>
#include <cstdint> // For uint8_t

class CuckooFilter {
public:
    CuckooFilter(size_t bucket_count, size_t bucket_size)
        : bucket_count(bucket_count), bucket_size(bucket_size) {
        table.resize(bucket_count);
        for (auto& bucket : table) {
            bucket.resize(bucket_size, false);
        }
    }

    CuckooFilter() : CuckooFilter(1000, 4) {} // Default constructor

    bool insert(size_t item) {
        // Example hash functions (you should use better hash functions)
        size_t hash1 = hash(item, 0);
        size_t hash2 = hash(item, 1);

        if (!insert_at(hash1, item)) {
            if (!insert_at(hash2, item)) {
                return false; // Failed to insert
            }
        }

        return true;
    }

    bool contains(size_t item) const {
        size_t hash1 = hash(item, 0);
        size_t hash2 = hash(item, 1);
        return contains_at(hash1, item) || contains_at(hash2, item);
    }

private:
    size_t bucket_count;
    size_t bucket_size;
    std::vector<std::vector<bool>> table;

    size_t hash(size_t item, size_t seed) const {
        size_t hash = seed;
        hash = hash * 31 + item;
        return hash % bucket_count;
    }

    bool insert_at(size_t hash, size_t item) {
        auto& bucket = table[hash];
        for (size_t i = 0; i < bucket_size; ++i) {
            if (!bucket[i]) {
                bucket[i] = true;
                return true;
            }
        }
        return false;
    }

    bool contains_at(size_t hash, size_t item) const {
        const auto& bucket = table[hash];
        for (size_t i = 0; i < bucket_size; ++i) {
            if (bucket[i]) {
                return true;
            }
        }
        return false;
    }
};

#endif // CUCKOO_H
