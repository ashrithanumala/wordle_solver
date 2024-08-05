#ifndef CUCKOO_H
#define CUCKOO_H

#include <vector>
#include <string>   // For std::string
#include <cstdint>  // For uint8_t

class CuckooFilter {
public:
    CuckooFilter(size_t bucket_count, size_t bucket_size)
        : bucket_count(bucket_count), bucket_size(bucket_size) {
        table.resize(bucket_count);
        for (auto& bucket : table) {
            bucket.resize(bucket_size, false);
        }
    }

    CuckooFilter() : CuckooFilter(20000, 8) {} // Default constructor

    bool insert(char item) {
        std::string item_str(1, item); // Convert char to string
        return insert(item_str);
    }

    bool contains(char item) const {
        std::string item_str(1, item); // Convert char to string
        return contains(item_str);
    }

    bool insert(const std::string& item) {
        size_t hash1 = hash(item, 0);
        size_t hash2 = hash(item, 1);

        if (!insert_at(hash1, item)) {
            if (!insert_at(hash2, item)) {
                return false; // Failed to insert
            }
        }

        return true;
    }

private:
    size_t bucket_count;
    size_t bucket_size;
    std::vector<std::vector<bool>> table;

    size_t hash(const std::string& item, size_t seed) const {
        size_t hash = seed;
        for (char c : item) {
            hash = hash * 31 + static_cast<unsigned char>(c);
        }
        return hash % bucket_count;
    }

    bool contains(const std::string& item) const {
        size_t hash1 = hash(item, 0);
        size_t hash2 = hash(item, 1);
        return contains_at(hash1, item) || contains_at(hash2, item);
    }

    bool insert_at(size_t hash, const std::string& item) {
        auto& bucket = table[hash];
        for (size_t i = 0; i < bucket_size; ++i) {
            if (!bucket[i]) {
                bucket[i] = true;
                return true;
            }
        }
        return false;
    }

    bool contains_at(size_t hash, const std::string& item) const {
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
