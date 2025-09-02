"""
Deduplication manager integrated with Milvus for NetIntel-OCR v0.1.15
"""
from typing import List, Dict, Any, Optional
import numpy as np
from pymilvus import Collection, connections
import ollama
import hashlib
import time
import logging
import os

logger = logging.getLogger(__name__)


class MilvusDeduplicationManager:
    """Deduplication manager integrated with Milvus"""
    
    def __init__(
        self,
        milvus_host: str = "localhost",
        milvus_port: int = 19530,
        collection_name: str = "netintel_dedup",
        mode: str = "full",  # exact, fuzzy, hybrid, full
        hamming_threshold: int = 5,
        cdc_min_length: int = 128,
        ollama_host: str = None,
        embedding_model: str = "qwen3-embedding:8b"
    ):
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        self.collection_name = collection_name
        self.mode = mode
        self.hamming_threshold = hamming_threshold
        self.cdc_min_length = cdc_min_length
        self.ollama_host = ollama_host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.embedding_model = embedding_model
        
        # Connect to Milvus
        connections.connect(host=milvus_host, port=milvus_port)
        self.collection = Collection(collection_name)
        
        # Initialize Ollama client for embeddings
        self.ollama_client = ollama.Client(host=self.ollama_host)
        
        # Initialize C++ dedup core
        try:
            from text_dedup import dedup_core
            self.cpp_core = dedup_core
            self.use_cpp = True
            logger.info("C++ deduplication core loaded successfully")
        except ImportError:
            self.cpp_core = None
            self.use_cpp = False
            logger.warning("C++ deduplication core not available, using Python fallback")
    
    def process_document(self, pdf_path: str, text_content: str) -> Dict:
        """Process document with full deduplication pipeline"""
        start_time = time.time()
        
        # Level 1: MD5 exact matching
        md5 = self._calculate_md5(pdf_path)
        exact_dup = self._check_exact_duplicate_milvus(md5)
        
        if exact_dup and self.mode == "exact":
            return self._create_duplicate_response(md5, "exact", exact_dup)
        
        # Level 2: SimHash near-duplicate detection
        if self.use_cpp:
            simhash = self.cpp_core.compute_simhash(text_content, bits=64)
        else:
            simhash = self._compute_simhash_python(text_content)
        
        # Convert SimHash to binary vector for Milvus
        simhash_binary = np.unpackbits(np.frombuffer(simhash, dtype=np.uint8))
        
        # Search for near-duplicates in Milvus
        near_dups = self._search_near_duplicates_milvus(simhash_binary)
        
        # Level 3: CDC content deduplication
        chunks = []
        if self.mode == "full" and self.use_cpp:
            chunks, hashes = self.cpp_core.cdc_deduplicate(
                text_content,
                min_length=self.cdc_min_length
            )
            deduped_content = "".join(chunks)
        else:
            deduped_content = text_content
        
        # Calculate metrics
        original_size = len(text_content)
        deduped_size = len(deduped_content)
        reduction_percent = (1 - deduped_size / original_size) * 100 if original_size > 0 else 0
        
        # Generate embeddings using Ollama
        embedding = self._generate_embedding(deduped_content)
        
        # Store in Milvus
        self._store_in_milvus(
            document_id=pdf_path,
            md5=md5,
            simhash_binary=simhash_binary,
            simhash_hex=simhash.hex() if isinstance(simhash, bytes) else "",
            content=deduped_content,
            embedding=embedding,
            chunks=chunks,
            metrics={
                "original_size": original_size,
                "deduped_size": deduped_size,
                "reduction_percent": reduction_percent,
                "is_duplicate": len(near_dups) > 0,
                "processing_time_ms": (time.time() - start_time) * 1000
            }
        )
        
        return {
            "md5": md5,
            "simhash": simhash.hex() if isinstance(simhash, bytes) else str(simhash),
            "is_exact_duplicate": exact_dup is not None,
            "is_near_duplicate": len(near_dups) > 0,
            "similar_documents": near_dups,
            "reduction_percent": reduction_percent,
            "processing_time_ms": (time.time() - start_time) * 1000
        }
    
    def _calculate_md5(self, file_path: str) -> str:
        """Calculate MD5 checksum of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except FileNotFoundError:
            # If file doesn't exist, use the path as identifier
            hash_md5.update(file_path.encode())
        return hash_md5.hexdigest()
    
    def _check_exact_duplicate_milvus(self, md5: str) -> Optional[str]:
        """Check for exact duplicate by MD5 in Milvus"""
        try:
            results = self.collection.query(
                expr=f'md5_checksum == "{md5}"',
                output_fields=["document_id"],
                limit=1
            )
            return results[0]["document_id"] if results else None
        except Exception as e:
            logger.error(f"Error checking exact duplicate: {e}")
            return None
    
    def _search_near_duplicates_milvus(
        self,
        simhash_binary: np.ndarray,
        limit: int = 10
    ) -> List[Dict]:
        """Search for near-duplicates using Hamming distance in Milvus"""
        try:
            search_params = {
                "metric_type": "HAMMING",
                "params": {"nprobe": 10}
            }
            
            results = self.collection.search(
                data=[simhash_binary.tolist()],
                anns_field="simhash_64",
                param=search_params,
                limit=limit,
                output_fields=["document_id", "md5_checksum"]
            )
            
            near_duplicates = []
            for hits in results:
                for hit in hits:
                    if hit.distance <= self.hamming_threshold:
                        near_duplicates.append({
                            "document_id": hit.entity.get("document_id"),
                            "hamming_distance": hit.distance,
                            "similarity_score": 1 - (hit.distance / 64)  # Normalized
                        })
            
            return near_duplicates
        except Exception as e:
            logger.error(f"Error searching near duplicates: {e}")
            return []
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using Ollama qwen3-embedding:8b"""
        try:
            response = self.ollama_client.embeddings(
                model=self.embedding_model,
                prompt=text[:8000]  # Limit text length for embedding
            )
            return np.array(response['embedding'])
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector on error
            return np.zeros(4096)
    
    def _store_in_milvus(self, **kwargs):
        """Store processed document in Milvus"""
        try:
            data = [{
                "document_id": kwargs["document_id"],
                "md5_checksum": kwargs["md5"],
                "simhash_64": kwargs["simhash_binary"].tolist(),
                "simhash_hex": kwargs.get("simhash_hex", ""),
                "content": kwargs["content"][:65535],  # Limit content length
                "content_embedding": kwargs["embedding"].tolist(),
                "cdc_chunks": kwargs.get("chunks", []),
                "is_duplicate": kwargs["metrics"]["is_duplicate"],
                "cdc_reduction_percent": kwargs["metrics"]["reduction_percent"],
                "original_size": kwargs["metrics"]["original_size"],
                "deduped_size": kwargs["metrics"]["deduped_size"],
                "processing_time_ms": kwargs["metrics"]["processing_time_ms"],
                "page_number": kwargs.get("page_number", 0),
                "metadata": kwargs.get("metadata", {})
            }]
            
            self.collection.insert(data)
            self.collection.flush()
            logger.info(f"Stored document {kwargs['document_id']} in Milvus")
        except Exception as e:
            logger.error(f"Error storing in Milvus: {e}")
    
    def _compute_simhash_python(self, text: str) -> bytes:
        """Python fallback for SimHash computation"""
        # Simple SimHash implementation
        import hashlib
        
        # Tokenize text
        tokens = text.lower().split()
        
        # Initialize feature vector
        feature_vector = np.zeros(64)
        
        # Calculate SimHash
        for token in tokens:
            # Get hash of token
            token_hash = int(hashlib.md5(token.encode()).hexdigest(), 16)
            
            # Update feature vector
            for i in range(64):
                if token_hash & (1 << i):
                    feature_vector[i] += 1
                else:
                    feature_vector[i] -= 1
        
        # Generate final hash
        simhash = 0
        for i in range(64):
            if feature_vector[i] > 0:
                simhash |= (1 << i)
        
        # Convert to bytes
        return simhash.to_bytes(8, byteorder='big')
    
    def _create_duplicate_response(self, md5: str, dup_type: str, duplicate_of: str) -> Dict:
        """Create response for duplicate document"""
        return {
            "md5": md5,
            "is_exact_duplicate": dup_type == "exact",
            "is_near_duplicate": dup_type == "near",
            "duplicate_of": duplicate_of,
            "similar_documents": [{"document_id": duplicate_of}],
            "reduction_percent": 100.0,  # Complete duplicate
            "processing_time_ms": 0
        }
    
    def get_stats(self) -> Dict:
        """Get deduplication statistics"""
        from .vector_db.milvus_dedup_schema import get_dedup_statistics
        return get_dedup_statistics(self.collection)