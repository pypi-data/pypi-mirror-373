#include <vector>
#include <string>
#include <cstdint>
#include <algorithm>
#include <functional>

#ifdef USE_OPENMP
#include <omp.h>
#endif

#ifdef __AVX2__
#include <immintrin.h>
#endif

class SimHash {
private:
    int bits;
    std::hash<std::string> hasher;
    
public:
    SimHash(int bits = 64) : bits(bits) {}
    
    std::vector<uint8_t> compute(const std::string& text) {
        std::vector<int> v(bits, 0);
        
        // Tokenize and accumulate hash values
        size_t start = 0;
        while (start < text.length()) {
            size_t end = text.find(' ', start);
            if (end == std::string::npos) end = text.length();
            
            std::string token = text.substr(start, end - start);
            std::transform(token.begin(), token.end(), token.begin(), ::tolower);
            
            uint64_t h = hasher(token);
            
            for (int i = 0; i < bits; ++i) {
                if ((h >> i) & 1) {
                    v[i]++;
                } else {
                    v[i]--;
                }
            }
            
            start = end + 1;
        }
        
        // Generate fingerprint
        std::vector<uint8_t> fingerprint(bits / 8, 0);
        for (int i = 0; i < bits; ++i) {
            if (v[i] >= 0) {
                fingerprint[i / 8] |= (1 << (i % 8));
            }
        }
        
        return fingerprint;
    }
    
    static int hamming_distance(const std::vector<uint8_t>& fp1, 
                                const std::vector<uint8_t>& fp2) {
        int distance = 0;
        
#ifdef __AVX2__
        // AVX2 optimized version
        size_t i = 0;
        for (; i + 32 <= fp1.size(); i += 32) {
            __m256i a = _mm256_loadu_si256((__m256i*)&fp1[i]);
            __m256i b = _mm256_loadu_si256((__m256i*)&fp2[i]);
            __m256i xor_result = _mm256_xor_si256(a, b);
            
            // Count bits in each byte
            for (int j = 0; j < 32; ++j) {
                distance += __builtin_popcount(((uint8_t*)&xor_result)[j]);
            }
        }
        
        // Handle remaining bytes
        for (; i < fp1.size(); ++i) {
            distance += __builtin_popcount(fp1[i] ^ fp2[i]);
        }
#else
        // Standard version
        for (size_t i = 0; i < fp1.size(); ++i) {
            uint8_t xor_val = fp1[i] ^ fp2[i];
            distance += __builtin_popcount(xor_val);
        }
#endif
        
        return distance;
    }
};