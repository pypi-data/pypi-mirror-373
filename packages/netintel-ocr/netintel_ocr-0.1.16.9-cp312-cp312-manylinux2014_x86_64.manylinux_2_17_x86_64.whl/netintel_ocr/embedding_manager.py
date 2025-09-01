"""
Embedding Manager for NetIntel-OCR v0.1.12
Handles embedding generation with multiple providers and caching.
"""

import json
import os
import hashlib
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum
import requests
from tqdm import tqdm

# Set up logging
logger = logging.getLogger(__name__)


class EmbeddingProvider(Enum):
    """Supported embedding providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"


@dataclass
class EmbeddingModel:
    """Embedding model configuration."""
    name: str
    provider: EmbeddingProvider
    dimension: int
    max_tokens: int
    batch_size: int


# Predefined embedding models
EMBEDDING_MODELS = {
    # Ollama models
    "qwen3-embedding:4b": EmbeddingModel(
        name="qwen3-embedding:4b",
        provider=EmbeddingProvider.OLLAMA,
        dimension=768,  # Qwen3 4B embedding dimension
        max_tokens=8192,
        batch_size=32
    ),
    "nomic-embed-text": EmbeddingModel(
        name="nomic-embed-text",
        provider=EmbeddingProvider.OLLAMA,
        dimension=768,
        max_tokens=8192,
        batch_size=32
    ),
    "mxbai-embed-large": EmbeddingModel(
        name="mxbai-embed-large",
        provider=EmbeddingProvider.OLLAMA,
        dimension=1024,
        max_tokens=512,
        batch_size=16
    ),
    "all-minilm": EmbeddingModel(
        name="all-minilm",
        provider=EmbeddingProvider.OLLAMA,
        dimension=384,
        max_tokens=256,
        batch_size=64
    ),
    # OpenAI models
    "text-embedding-3-small": EmbeddingModel(
        name="text-embedding-3-small",
        provider=EmbeddingProvider.OPENAI,
        dimension=1536,
        max_tokens=8191,
        batch_size=100
    ),
    "text-embedding-3-large": EmbeddingModel(
        name="text-embedding-3-large",
        provider=EmbeddingProvider.OPENAI,
        dimension=3072,
        max_tokens=8191,
        batch_size=50
    ),
    "text-embedding-ada-002": EmbeddingModel(
        name="text-embedding-ada-002",
        provider=EmbeddingProvider.OPENAI,
        dimension=1536,
        max_tokens=8191,
        batch_size=100
    ),
}


class EmbeddingCache:
    """Cache for embeddings."""
    
    def __init__(self, 
                 cache_dir: str = ".embedding_cache",
                 ttl_hours: int = 24,
                 max_size_mb: int = 1024):
        """
        Initialize embedding cache.
        
        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time to live in hours
            max_size_mb: Maximum cache size in MB
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Load cache index."""
        index_file = self.cache_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_index(self):
        """Save cache index."""
        index_file = self.cache_dir / "index.json"
        with open(index_file, 'w') as f:
            json.dump(self.cache_index, f)
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """
        Get embedding from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached embedding or None
        """
        if key not in self.cache_index:
            return None
        
        entry = self.cache_index[key]
        
        # Check TTL
        cached_time = datetime.fromisoformat(entry['timestamp'])
        if datetime.now() - cached_time > self.ttl:
            # Expired
            self._remove(key)
            return None
        
        # Load embedding
        cache_file = self.cache_dir / entry['file']
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                self._remove(key)
        
        return None
    
    def put(self, key: str, embedding: np.ndarray):
        """
        Store embedding in cache.
        
        Args:
            key: Cache key
            embedding: Embedding to cache
        """
        # Check cache size
        self._enforce_size_limit()
        
        # Generate filename
        filename = f"{hashlib.md5(key.encode()).hexdigest()}.pkl"
        cache_file = self.cache_dir / filename
        
        # Save embedding
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)
        
        # Update index
        self.cache_index[key] = {
            'file': filename,
            'timestamp': datetime.now().isoformat(),
            'size': cache_file.stat().st_size
        }
        self._save_index()
    
    def _remove(self, key: str):
        """Remove entry from cache."""
        if key in self.cache_index:
            entry = self.cache_index[key]
            cache_file = self.cache_dir / entry['file']
            if cache_file.exists():
                cache_file.unlink()
            del self.cache_index[key]
            self._save_index()
    
    def _enforce_size_limit(self):
        """Enforce cache size limit using LRU eviction."""
        total_size = sum(entry['size'] for entry in self.cache_index.values())
        
        if total_size > self.max_size_bytes:
            # Sort by timestamp (oldest first)
            sorted_entries = sorted(
                self.cache_index.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            # Remove oldest entries until under limit
            for key, entry in sorted_entries:
                if total_size <= self.max_size_bytes:
                    break
                self._remove(key)
                total_size -= entry['size']


class EmbeddingManager:
    """Manages embedding generation for NetIntel-OCR."""
    
    def __init__(self,
                 provider: str = "ollama",
                 model: str = "qwen3-embedding:4b",
                 dimension: Optional[int] = None,
                 batch_size: int = 32,
                 cache_enabled: bool = True,
                 ollama_host: Optional[str] = None):
        """
        Initialize embedding manager.
        
        Args:
            provider: Embedding provider
            model: Model name
            dimension: Embedding dimension (auto-detected if None)
            batch_size: Batch size for generation
            cache_enabled: Enable caching
            ollama_host: Ollama server URL
        """
        self.provider = EmbeddingProvider(provider.lower())
        self.model_name = model
        
        # Get model configuration
        if model in EMBEDDING_MODELS:
            self.model = EMBEDDING_MODELS[model]
        else:
            # Custom model
            self.model = EmbeddingModel(
                name=model,
                provider=self.provider,
                dimension=dimension or 768,
                max_tokens=8192,
                batch_size=batch_size
            )
        
        self.batch_size = batch_size
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # Log Ollama configuration
        if self.provider == EmbeddingProvider.OLLAMA:
            logger.info(f"Using Ollama embeddings: model={self.model_name}, host={self.ollama_host}")
        
        # Initialize cache
        self.cache = EmbeddingCache() if cache_enabled else None
    
    def generate_embeddings(self,
                           texts: Union[str, List[str]],
                           use_cache: bool = True,
                           show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for texts.
        
        Args:
            texts: Text or list of texts
            use_cache: Use cache if available
            show_progress: Show progress bar
            
        Returns:
            Embeddings array
        """
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache
        if use_cache and self.cache:
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                cached = self.cache.get(cache_key)
                if cached is not None:
                    embeddings.append(cached)
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = self._generate_batch(
                uncached_texts,
                show_progress=show_progress
            )
            
            # Cache new embeddings
            if use_cache and self.cache:
                for text, embedding in zip(uncached_texts, new_embeddings):
                    cache_key = self._get_cache_key(text)
                    self.cache.put(cache_key, embedding)
            
            # Merge with cached embeddings
            if embeddings:
                # Insert new embeddings at correct positions
                result = []
                cached_idx = 0
                new_idx = 0
                
                for i in range(len(texts)):
                    if i in uncached_indices:
                        result.append(new_embeddings[new_idx])
                        new_idx += 1
                    else:
                        result.append(embeddings[cached_idx])
                        cached_idx += 1
                
                embeddings = result
            else:
                embeddings = new_embeddings
        
        return np.array(embeddings)
    
    def _generate_batch(self,
                       texts: List[str],
                       show_progress: bool = False) -> List[np.ndarray]:
        """
        Generate embeddings in batches.
        
        Args:
            texts: Texts to embed
            show_progress: Show progress bar
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        # Process in batches
        batches = [texts[i:i + self.batch_size] 
                  for i in range(0, len(texts), self.batch_size)]
        
        iterator = tqdm(batches, desc="Generating embeddings") if show_progress else batches
        
        for batch in iterator:
            if self.provider == EmbeddingProvider.OLLAMA:
                batch_embeddings = self._generate_ollama(batch)
            elif self.provider == EmbeddingProvider.OPENAI:
                batch_embeddings = self._generate_openai(batch)
            else:
                # Fallback to random for unsupported providers
                batch_embeddings = self._generate_random(batch)
            
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def _generate_ollama(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings using Ollama.
        
        Args:
            texts: Texts to embed
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        for text in texts:
            try:
                response = requests.post(
                    f"{self.ollama_host}/api/embeddings",
                    json={
                        "model": self.model_name,
                        "prompt": text
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    embedding = np.array(data.get('embedding', []))
                    
                    # Ensure correct dimension
                    if len(embedding) != self.model.dimension:
                        embedding = np.zeros(self.model.dimension)
                    
                    embeddings.append(embedding)
                else:
                    logger.warning(f"Ollama embedding failed: {response.status_code}")
                    embeddings.append(np.zeros(self.model.dimension))
                    
            except Exception as e:
                logger.error(f"Error generating Ollama embedding: {e}")
                embeddings.append(np.zeros(self.model.dimension))
        
        return embeddings
    
    def _generate_openai(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings using OpenAI.
        
        Args:
            texts: Texts to embed
            
        Returns:
            List of embeddings
        """
        # This would require OpenAI API key and client
        # For now, return placeholder
        logger.warning("OpenAI embeddings not implemented, using random")
        return self._generate_random(texts)
    
    def _generate_random(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate random embeddings (for testing).
        
        Args:
            texts: Texts to embed
            
        Returns:
            List of random embeddings
        """
        embeddings = []
        
        for text in texts:
            # Generate deterministic "random" embedding based on text
            np.random.seed(hash(text) % (2**32))
            embedding = np.random.randn(self.model.dimension)
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        
        return embeddings
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return f"{self.provider.value}:{self.model_name}:{hashlib.md5(text.encode()).hexdigest()}"
    
    def generate_embeddings_for_chunks(self,
                                      chunks: List[Dict],
                                      text_field: str = "content",
                                      show_progress: bool = True) -> List[Dict]:
        """
        Generate embeddings for a list of chunks.
        
        Args:
            chunks: List of chunk dictionaries
            text_field: Field containing text to embed
            show_progress: Show progress bar
            
        Returns:
            Chunks with embeddings added
        """
        # Extract texts
        texts = [chunk.get(text_field, "") for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts, show_progress=show_progress)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding.tolist()
            chunk['embedding_model'] = self.model_name
            chunk['embedding_dimension'] = self.model.dimension
        
        return chunks
    
    def validate_embeddings(self, chunks: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate that chunks have proper embeddings.
        
        Args:
            chunks: Chunks to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        for i, chunk in enumerate(chunks):
            if 'embedding' not in chunk:
                issues.append(f"Chunk {i}: Missing embedding field")
                continue
            
            embedding = chunk['embedding']
            
            if embedding is None:
                issues.append(f"Chunk {i}: Embedding is None")
                continue
            
            if not isinstance(embedding, (list, np.ndarray)):
                issues.append(f"Chunk {i}: Invalid embedding type")
                continue
            
            if len(embedding) != self.model.dimension:
                issues.append(f"Chunk {i}: Wrong dimension ({len(embedding)} != {self.model.dimension})")
        
        return len(issues) == 0, issues
    
    def get_model_info(self) -> Dict:
        """Get information about the current embedding model."""
        return {
            'name': self.model_name,
            'provider': self.provider.value,
            'dimension': self.model.dimension,
            'max_tokens': self.model.max_tokens,
            'batch_size': self.model.batch_size
        }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4