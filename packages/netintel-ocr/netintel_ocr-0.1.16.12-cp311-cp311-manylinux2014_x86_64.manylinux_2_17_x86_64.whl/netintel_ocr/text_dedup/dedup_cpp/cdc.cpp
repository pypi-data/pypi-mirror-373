#include <vector>
#include <string>
#include <cstdint>
#include <unordered_set>
#include <cstring>

#ifdef USE_OPENMP
#include <omp.h>
#endif

class CDC {
private:
    size_t chunk_size;
    size_t window_size;
    uint64_t prime;
    uint64_t mask;
    
    // Simple xxHash-like hash function
    uint64_t hash_bytes(const uint8_t* data, size_t len) {
        uint64_t h = 0x1234567890ABCDEF;
        for (size_t i = 0; i < len; ++i) {
            h ^= data[i];
            h *= prime;
            h = (h << 31) | (h >> 33);
        }
        return h;
    }
    
public:
    CDC(size_t chunk_size = 1024) 
        : chunk_size(chunk_size),
          window_size(48),
          prime(1099511628211ULL),
          mask((1ULL << 13) - 1) {}
    
    std::vector<std::vector<uint8_t>> chunk(const std::vector<uint8_t>& data) {
        std::vector<std::vector<uint8_t>> chunks;
        size_t pos = 0;
        
        while (pos < data.size()) {
            size_t chunk_end = std::min(pos + chunk_size * 2, data.size());
            size_t chunk_start = pos;
            
            // Rolling hash for content-defined boundary
            if (pos + window_size < data.size()) {
                uint64_t h = 0;
                
                // Initial window hash
                for (size_t i = 0; i < window_size; ++i) {
                    h = (h * prime) ^ data[pos + i];
                }
                
                // Roll the hash
                for (size_t i = pos + window_size; i < chunk_end; ++i) {
                    h = (h * prime) ^ data[i];
                    if ((h & mask) == 0) {
                        chunk_end = i + 1;
                        break;
                    }
                }
            }
            
            // Create chunk
            chunks.emplace_back(data.begin() + chunk_start, data.begin() + chunk_end);
            pos = chunk_end;
        }
        
        return chunks;
    }
    
    std::pair<std::vector<std::vector<uint8_t>>, double> 
    deduplicate(const std::vector<std::vector<uint8_t>>& chunks) {
        std::vector<std::vector<uint8_t>> unique_chunks;
        std::unordered_set<uint64_t> seen_hashes;
        
#ifdef USE_OPENMP
        #pragma omp parallel
        {
            std::vector<std::vector<uint8_t>> local_unique;
            std::unordered_set<uint64_t> local_seen;
            
            #pragma omp for nowait
            for (size_t i = 0; i < chunks.size(); ++i) {
                uint64_t h = hash_bytes(chunks[i].data(), chunks[i].size());
                
                #pragma omp critical
                {
                    if (seen_hashes.find(h) == seen_hashes.end()) {
                        seen_hashes.insert(h);
                        local_unique.push_back(chunks[i]);
                    }
                }
            }
            
            #pragma omp critical
            {
                unique_chunks.insert(unique_chunks.end(), 
                                   local_unique.begin(), 
                                   local_unique.end());
            }
        }
#else
        for (const auto& chunk : chunks) {
            uint64_t h = hash_bytes(chunk.data(), chunk.size());
            if (seen_hashes.find(h) == seen_hashes.end()) {
                seen_hashes.insert(h);
                unique_chunks.push_back(chunk);
            }
        }
#endif
        
        double reduction = chunks.empty() ? 0.0 : 
            (1.0 - (double)unique_chunks.size() / chunks.size()) * 100.0;
        
        return {unique_chunks, reduction};
    }
};