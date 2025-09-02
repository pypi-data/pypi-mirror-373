"""
NetIntel-OCR v0.1.14 Deduplication Manager
High-performance deduplication with C++ core and Python fallback
"""

import hashlib
import json
import logging
import os
import psutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field

import numpy as np

# Try to import C++ core
try:
    from netintel_ocr.text_dedup import dedup_core
    CPP_CORE_AVAILABLE = True
except ImportError:
    CPP_CORE_AVAILABLE = False
    dedup_core = None

# Try to import Faiss
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

logger = logging.getLogger(__name__)


@dataclass
class DeduplicationConfig:
    """Configuration for deduplication based on deployment scale."""
    mode: str  # minimal, small, medium, production
    md5_enabled: bool = True
    simhash_enabled: bool = True
    simhash_bits: int = 64
    cdc_enabled: bool = False
    cdc_chunk_size: int = 1024
    faiss_index_type: str = "Flat"
    batch_size: int = 100
    cache_size_mb: int = 100
    parallel_threads: int = 1
    
    @classmethod
    def from_scale(cls, scale: str) -> 'DeduplicationConfig':
        """Create configuration based on deployment scale."""
        configs = {
            'minimal': cls(
                mode='minimal',
                md5_enabled=True,
                simhash_enabled=False,
                cdc_enabled=False,
                parallel_threads=1,
                cache_size_mb=50
            ),
            'small': cls(
                mode='small',
                md5_enabled=True,
                simhash_enabled=True,
                simhash_bits=64,
                cdc_enabled=False,
                faiss_index_type="Flat",
                batch_size=50,
                cache_size_mb=100,
                parallel_threads=2
            ),
            'medium': cls(
                mode='medium',
                md5_enabled=True,
                simhash_enabled=True,
                simhash_bits=128,
                cdc_enabled=True,
                cdc_chunk_size=512,
                faiss_index_type="IVF",
                batch_size=100,
                cache_size_mb=500,
                parallel_threads=4
            ),
            'production': cls(
                mode='production',
                md5_enabled=True,
                simhash_enabled=True,
                simhash_bits=128,
                cdc_enabled=True,
                cdc_chunk_size=256,
                faiss_index_type="HNSW",
                batch_size=500,
                cache_size_mb=2000,
                parallel_threads=8
            )
        }
        return configs.get(scale, configs['small'])


class PythonSimHash:
    """Python fallback implementation of SimHash."""
    
    def __init__(self, bits: int = 64):
        self.bits = bits
    
    def compute(self, text: str) -> bytes:
        """Compute SimHash fingerprint."""
        tokens = text.lower().split()
        v = [0] * self.bits
        
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            for i in range(self.bits):
                bit = (h >> i) & 1
                if bit:
                    v[i] += 1
                else:
                    v[i] -= 1
        
        fingerprint = 0
        for i in range(self.bits):
            if v[i] >= 0:
                fingerprint |= (1 << i)
        
        return fingerprint.to_bytes(self.bits // 8, 'big')
    
    @staticmethod
    def hamming_distance(fp1: bytes, fp2: bytes) -> int:
        """Calculate Hamming distance between two fingerprints."""
        xor = int.from_bytes(fp1, 'big') ^ int.from_bytes(fp2, 'big')
        return bin(xor).count('1')


class PythonCDC:
    """Python fallback implementation of Content-Defined Chunking."""
    
    def __init__(self, chunk_size: int = 1024):
        self.chunk_size = chunk_size
        self.window_size = 48
        self.prime = 1099511628211
        self.mask = (1 << 13) - 1
    
    def chunk(self, data: bytes) -> List[bytes]:
        """Split data into content-defined chunks."""
        chunks = []
        pos = 0
        
        while pos < len(data):
            chunk_end = min(pos + self.chunk_size * 2, len(data))
            chunk_start = pos
            
            # Rolling hash
            if pos + self.window_size < len(data):
                h = 0
                for i in range(self.window_size):
                    h = (h * self.prime) ^ data[pos + i]
                
                for i in range(pos + self.window_size, chunk_end):
                    h = (h * self.prime) ^ data[i]
                    if (h & self.mask) == 0:
                        chunk_end = i + 1
                        break
            
            chunks.append(data[chunk_start:chunk_end])
            pos = chunk_end
        
        return chunks
    
    def deduplicate(self, chunks: List[bytes]) -> Tuple[List[bytes], float]:
        """Deduplicate chunks and return unique chunks with reduction percentage."""
        unique = []
        seen = set()
        
        for chunk in chunks:
            h = hashlib.sha256(chunk).digest()
            if h not in seen:
                seen.add(h)
                unique.append(chunk)
        
        reduction = 1.0 - (len(unique) / len(chunks)) if chunks else 0.0
        return unique, reduction * 100


class DeduplicationManager:
    """Main deduplication manager with C++ core or Python fallback."""
    
    def __init__(
        self,
        mode: Optional[str] = None,
        min_length_dedup: int = 128,
        hamming_threshold: int = 5,
        cdc_min_chunk: int = 256,
        lancedb_client: Optional[Any] = None
    ):
        """Initialize deduplication manager."""
        # Auto-detect deployment scale if not specified
        if mode is None:
            mode = self._detect_deployment_scale()
        
        self.config = DeduplicationConfig.from_scale(mode)
        self.min_length_dedup = min_length_dedup
        self.hamming_threshold = hamming_threshold
        self.cdc_min_chunk = cdc_min_chunk
        self.lancedb_client = lancedb_client
        
        # Initialize backends
        self._init_backends()
        
        # Statistics
        self.stats = {
            'documents_processed': 0,
            'exact_duplicates': 0,
            'near_duplicates': 0,
            'cdc_reduction_total': 0.0,
            'processing_time': 0.0
        }
        
        logger.info(f"DeduplicationManager initialized in {mode} mode")
        logger.info(f"C++ Core: {CPP_CORE_AVAILABLE}, Faiss: {FAISS_AVAILABLE}")
    
    def _detect_deployment_scale(self) -> str:
        """Auto-detect deployment scale based on system resources."""
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        
        # Check for Kubernetes
        if os.path.exists('/var/run/secrets/kubernetes.io'):
            # In Kubernetes, check resource limits
            if memory_gb >= 16 and cpu_count >= 8:
                return 'production'
            elif memory_gb >= 8 and cpu_count >= 4:
                return 'medium'
            else:
                return 'small'
        
        # Local or VM deployment
        if memory_gb >= 32 and cpu_count >= 16:
            return 'production'
        elif memory_gb >= 16 and cpu_count >= 8:
            return 'medium'
        elif memory_gb >= 8 and cpu_count >= 4:
            return 'small'
        else:
            return 'minimal'
    
    def _init_backends(self):
        """Initialize deduplication backends."""
        # SimHash backend
        if self.config.simhash_enabled:
            if CPP_CORE_AVAILABLE:
                self.simhash = dedup_core.SimHash(self.config.simhash_bits)
                logger.info(f"Using C++ SimHash ({self.config.simhash_bits}-bit)")
            else:
                self.simhash = PythonSimHash(self.config.simhash_bits)
                logger.info(f"Using Python SimHash fallback ({self.config.simhash_bits}-bit)")
        else:
            self.simhash = None
        
        # CDC backend
        if self.config.cdc_enabled:
            if CPP_CORE_AVAILABLE:
                self.cdc = dedup_core.CDC(self.config.cdc_chunk_size)
                logger.info(f"Using C++ CDC (chunk_size={self.config.cdc_chunk_size})")
            else:
                self.cdc = PythonCDC(self.config.cdc_chunk_size)
                logger.info(f"Using Python CDC fallback (chunk_size={self.config.cdc_chunk_size})")
        else:
            self.cdc = None
        
        # Faiss index for similarity search
        if self.config.simhash_enabled and FAISS_AVAILABLE:
            self._init_faiss_index()
        else:
            self.faiss_index = None
    
    def _init_faiss_index(self):
        """Initialize Faiss index based on configuration."""
        dim = self.config.simhash_bits
        
        if self.config.faiss_index_type == "Flat":
            self.faiss_index = faiss.IndexBinaryFlat(dim)
        elif self.config.faiss_index_type == "IVF":
            quantizer = faiss.IndexBinaryFlat(dim)
            self.faiss_index = faiss.IndexBinaryIVF(quantizer, dim, min(100, self.stats['documents_processed'] // 10))
        elif self.config.faiss_index_type == "HNSW":
            self.faiss_index = faiss.IndexBinaryHNSW(dim)
        else:
            self.faiss_index = faiss.IndexBinaryFlat(dim)
        
        logger.info(f"Initialized Faiss {self.config.faiss_index_type} index (dim={dim})")
    
    def process_document(self, pdf_path: Path, text_content: str) -> Dict[str, Any]:
        """Process a document for deduplication."""
        start_time = time.time()
        result = {
            'pdf_path': str(pdf_path),
            'is_duplicate': False,
            'duplicate_of': None,
            'similarity_score': 0.0,
            'md5_checksum': None,
            'simhash': None,
            'hamming_neighbors': [],
            'cdc_reduction_percent': 0.0
        }
        
        # Skip if text too short
        if len(text_content) < self.min_length_dedup:
            return result
        
        # Level 1: MD5 exact duplicate check
        if self.config.md5_enabled:
            md5_hash = hashlib.md5(text_content.encode()).hexdigest()
            result['md5_checksum'] = md5_hash
            
            if self.lancedb_client:
                existing = self._check_md5_duplicate(md5_hash)
                if existing:
                    result['is_duplicate'] = True
                    result['duplicate_of'] = existing
                    result['similarity_score'] = 1.0
                    self.stats['exact_duplicates'] += 1
                    return result
        
        # Level 2: SimHash near-duplicate detection
        if self.config.simhash_enabled and self.simhash:
            simhash_fp = self.simhash.compute(text_content)
            result['simhash'] = simhash_fp.hex()
            
            if self.faiss_index and self.faiss_index.ntotal > 0:
                neighbors = self._find_similar_documents(simhash_fp)
                result['hamming_neighbors'] = neighbors
                
                if neighbors and neighbors[0]['distance'] <= self.hamming_threshold:
                    result['is_duplicate'] = True
                    result['duplicate_of'] = neighbors[0]['document_id']
                    result['similarity_score'] = 1.0 - (neighbors[0]['distance'] / self.config.simhash_bits)
                    self.stats['near_duplicates'] += 1
            
            # Add to Faiss index
            if self.faiss_index:
                self._add_to_faiss_index(simhash_fp, str(pdf_path))
        
        # Level 3: Content-Defined Chunking
        if self.config.cdc_enabled and self.cdc:
            chunks = self.cdc.chunk(text_content.encode())
            unique_chunks, reduction = self.cdc.deduplicate(chunks)
            result['cdc_reduction_percent'] = reduction
            self.stats['cdc_reduction_total'] += reduction
        
        # Update statistics
        self.stats['documents_processed'] += 1
        self.stats['processing_time'] += time.time() - start_time
        
        return result
    
    def _check_md5_duplicate(self, md5_hash: str) -> Optional[str]:
        """Check if MD5 hash exists in LanceDB."""
        if not self.lancedb_client:
            return None
        
        try:
            # Query LanceDB for existing MD5
            results = self.lancedb_client.query(
                f"SELECT document_id FROM documents WHERE md5_checksum = '{md5_hash}' LIMIT 1"
            )
            if results:
                return results[0]['document_id']
        except Exception as e:
            logger.error(f"Error checking MD5 duplicate: {e}")
        
        return None
    
    def _find_similar_documents(self, simhash_fp: bytes) -> List[Dict[str, Any]]:
        """Find similar documents using Faiss index."""
        if not self.faiss_index or self.faiss_index.ntotal == 0:
            return []
        
        # Convert to numpy array
        fp_array = np.frombuffer(simhash_fp, dtype=np.uint8).reshape(1, -1)
        
        # Search for nearest neighbors
        k = min(10, self.faiss_index.ntotal)
        distances, indices = self.faiss_index.search(fp_array, k)
        
        neighbors = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0:  # Valid index
                neighbors.append({
                    'document_id': f"doc_{idx}",  # Map to actual document ID
                    'distance': int(dist),
                    'similarity': 1.0 - (dist / self.config.simhash_bits)
                })
        
        return neighbors
    
    def _add_to_faiss_index(self, simhash_fp: bytes, document_id: str):
        """Add SimHash fingerprint to Faiss index."""
        if not self.faiss_index:
            return
        
        # Convert to numpy array
        fp_array = np.frombuffer(simhash_fp, dtype=np.uint8).reshape(1, -1)
        
        # Add to index
        self.faiss_index.add(fp_array)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get deduplication statistics."""
        stats = self.stats.copy()
        
        if stats['documents_processed'] > 0:
            stats['exact_duplicate_rate'] = stats['exact_duplicates'] / stats['documents_processed']
            stats['near_duplicate_rate'] = stats['near_duplicates'] / stats['documents_processed']
            stats['avg_processing_time'] = stats['processing_time'] / stats['documents_processed']
            stats['avg_cdc_reduction'] = stats['cdc_reduction_total'] / stats['documents_processed']
        
        stats['cpp_core_enabled'] = CPP_CORE_AVAILABLE
        stats['faiss_enabled'] = FAISS_AVAILABLE
        stats['deployment_mode'] = self.config.mode
        
        return stats
    
    def save_index(self, path: Path):
        """Save Faiss index to disk."""
        if self.faiss_index and self.faiss_index.ntotal > 0:
            faiss.write_index_binary(self.faiss_index, str(path))
            logger.info(f"Saved Faiss index with {self.faiss_index.ntotal} vectors to {path}")
    
    def load_index(self, path: Path):
        """Load Faiss index from disk."""
        if path.exists() and FAISS_AVAILABLE:
            self.faiss_index = faiss.read_index_binary(str(path))
            logger.info(f"Loaded Faiss index with {self.faiss_index.ntotal} vectors from {path}")