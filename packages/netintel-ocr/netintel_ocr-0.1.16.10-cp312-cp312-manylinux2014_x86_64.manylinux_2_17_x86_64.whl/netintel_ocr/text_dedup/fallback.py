"""
Python fallback implementation for text deduplication when C++ core is not available
"""

import hashlib
import numpy as np
from typing import List, Tuple, Optional

class SimHash:
    """Python fallback implementation of SimHash."""
    
    def __init__(self, bits: int = 64):
        self.bits = bits
    
    def compute(self, text: str) -> bytes:
        """Compute SimHash of text."""
        # Simple Python implementation
        tokens = text.lower().split()
        v = [0] * self.bits
        
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            for i in range(self.bits):
                if h & (1 << i):
                    v[i] += 1
                else:
                    v[i] -= 1
        
        simhash = 0
        for i in range(self.bits):
            if v[i] > 0:
                simhash |= (1 << i)
        
        return simhash.to_bytes(self.bits // 8, 'big')
    
    def hamming_distance(self, hash1: bytes, hash2: bytes) -> int:
        """Calculate Hamming distance between two hashes."""
        xor = int.from_bytes(hash1, 'big') ^ int.from_bytes(hash2, 'big')
        return bin(xor).count('1')

class CDC:
    """Python fallback implementation of Content-Defined Chunking."""
    
    def __init__(self, min_length: int = 128, avg_length: int = 512, max_length: int = 2048):
        self.min_length = min_length
        self.avg_length = avg_length
        self.max_length = max_length
        self.mask = (1 << 13) - 1  # For average chunk size
    
    def chunk(self, text: str) -> List[str]:
        """Split text into content-defined chunks."""
        chunks = []
        current_chunk = []
        current_length = 0
        
        words = text.split()
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            
            if current_length >= self.min_length:
                # Check if we should break here
                h = hash(' '.join(current_chunk))
                if (h & self.mask) == 0 or current_length >= self.max_length:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_length = 0
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def deduplicate(self, text: str) -> Tuple[str, float]:
        """Deduplicate text using CDC."""
        chunks = self.chunk(text)
        unique_chunks = list(dict.fromkeys(chunks))  # Preserve order
        
        original_size = len(text)
        deduped_text = ' '.join(unique_chunks)
        deduped_size = len(deduped_text)
        
        reduction = (1 - deduped_size / original_size) * 100 if original_size > 0 else 0
        
        return deduped_text, reduction

def _openmp_available() -> bool:
    """Check if OpenMP is available (always False in fallback)."""
    return False

def has_avx2() -> bool:
    """Check if AVX2 is available (always False in fallback)."""
    return False

def has_openmp() -> bool:
    """Check if OpenMP is available (always False in fallback)."""
    return False

__version__ = "0.0.0-fallback"