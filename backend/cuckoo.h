// NO LONGER USING THIS FILE
#ifndef CUCKOO_H
#define CUCKOO_H

#include <vector>
#include <string>
#include <cstdint>
#include <bit>

class CuckooFilter {
public:
    CuckooFilter(size_t bucket_count, size_t bucket_size)
        : m_bucketCount(bucket_count), 
          m_bucketSize(bucket_size), 
          m_table(bucket_count, std::vector<uint8_t>(bucket_size, 0)) {}
          
    CuckooFilter() : CuckooFilter(20000, 8) {}

    bool insert(char item) {
        std::string item_str(1, item);
        return insert(item_str);
    }

    bool contains(char item) const {
        std::string item_str(1, item);
        return contains(item_str);
    }

    bool insert(const std::string& item) {
        size_t hash1 = computeHash(item, 0);
        size_t hash2 = computeHash(item, 1);

        if (!insertAtBucket(hash1, item)) {
            if (!insertAtBucket(hash2, item)) {
                return false;
            }
        }
        return true;
    }

private:
    size_t m_bucketCount;
    size_t m_bucketSize;
    std::vector<std::vector<uint8_t>> m_table;

    size_t computeHash(const std::string& item, size_t seed) const {
        size_t hash = seed;
        for (char c : item) {
            hash = ((hash << 5) + hash) + static_cast<unsigned char>(c);
        }
        return hash % m_bucketCount;
    }

    bool contains(const std::string& item) const {
        size_t hash1 = computeHash(item, 0);
        size_t hash2 = computeHash(item, 1);
        return containsAtBucket(hash1, item) || containsAtBucket(hash2, item);
    }

    bool insertAtBucket(size_t hash, const std::string& item) {
        auto& bucket = m_table[hash];
        for (size_t i = 0; i < m_bucketSize; ++i) {
            if (bucket[i] == 0) {
                bucket[i] = 1;
                return true;
            }
        }
        return false;
    }

    bool containsAtBucket(size_t hash, const std::string& item) const {
        const auto& bucket = m_table[hash];
        for (size_t i = 0; i < m_bucketSize; ++i) {
            if (bucket[i] != 0) {
                return true;
            }
        }
        return false;
    }
};

#endif // CUCKOO_H