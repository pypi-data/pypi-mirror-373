"""
Schema Generator for Vector Database Integration

Generates schema definitions for vector databases, particularly
optimized for LanceDB table creation and management.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class SchemaGenerator:
    """Generate schemas for vector databases."""
    
    def __init__(self, 
                 vector_format: str = "lancedb",
                 embedding_model: str = "text-embedding-ada-002",
                 embedding_provider: str = "openai"):
        """
        Initialize schema generator.
        
        Args:
            vector_format: Target vector database format
            embedding_model: Embedding model to use
            embedding_provider: Provider for embeddings (openai, ollama)
        """
        self.vector_format = vector_format
        self.embedding_model = embedding_model
        self.embedding_provider = embedding_provider
        
        # Define Ollama embedding model configurations
        self.ollama_models = {
            "qwen3-embedding:0.6b": {
                "dimension": 1024,
                "max_tokens": 32768,
                "layers": 28,
                "size": "0.6B"
            },
            "qwen3-embedding:4b": {
                "dimension": 2560,
                "max_tokens": 32768,
                "layers": 36,
                "size": "4B"
            },
            "qwen3-embedding:8b": {
                "dimension": 4096,
                "max_tokens": 32768,
                "layers": 36,
                "size": "8B"
            },
            # Add other common Ollama embedding models
            "nomic-embed-text": {
                "dimension": 768,
                "max_tokens": 8192,
                "layers": 12,
                "size": "137M"
            },
            "mxbai-embed-large": {
                "dimension": 1024,
                "max_tokens": 512,
                "layers": 24,
                "size": "335M"
            }
        }
    
    def generate_lancedb_schema(self) -> Dict:
        """
        Generate LanceDB table schema.
        
        Returns:
            Schema dictionary for LanceDB table creation
        """
        schema = {
            "name": "documents",
            "description": "NetIntel-OCR extracted documents with vector embeddings",
            "fields": [
                {
                    "name": "id",
                    "type": "string",
                    "description": "Unique chunk identifier",
                    "required": True,
                    "primary_key": True
                },
                {
                    "name": "document_id",
                    "type": "string",
                    "description": "Parent document identifier",
                    "required": True,
                    "index": True
                },
                {
                    "name": "chunk_index",
                    "type": "int32",
                    "description": "Chunk position in document",
                    "required": True
                },
                {
                    "name": "content",
                    "type": "string",
                    "description": "Chunk text content",
                    "required": True
                },
                {
                    "name": "embedding",
                    "type": "vector",
                    "dimension": 1536,  # OpenAI ada-002 dimension
                    "description": "Vector embedding of content",
                    "required": False
                },
                {
                    "name": "vector",
                    "type": "vector",
                    "dimension": 1536,  # Alternative vector field
                    "description": "Alternative vector representation",
                    "required": False
                },
                {
                    "name": "page_numbers",
                    "type": "list<int32>",
                    "description": "Page numbers this chunk spans",
                    "required": False
                },
                {
                    "name": "metadata",
                    "type": "struct",
                    "description": "Chunk and document metadata",
                    "fields": [
                        {"name": "char_count", "type": "int32"},
                        {"name": "token_count", "type": "int32"},
                        {"name": "start_char", "type": "int64"},
                        {"name": "end_char", "type": "int64"},
                        {"name": "content_type", "type": "string"},
                        {"name": "information_density", "type": "float32"},
                        {"name": "entities", "type": "struct"},
                        {"name": "document", "type": "struct", "fields": [
                            {"name": "source_file", "type": "string"},
                            {"name": "page_count", "type": "int32"},
                            {"name": "extraction_date", "type": "timestamp"}
                        ]}
                    ]
                }
            ],
            "indexes": [
                {
                    "name": "document_idx",
                    "fields": ["document_id"]
                },
                {
                    "name": "content_type_idx",
                    "fields": ["metadata.content_type"]
                }
            ],
            "vector_indexes": [
                {
                    "name": "embedding_idx",
                    "field": "embedding",
                    "metric": "cosine",
                    "index_type": "IVF_FLAT",
                    "nlist": 100
                }
            ]
        }
        
        return schema
    
    def generate_pinecone_schema(self) -> Dict:
        """
        Generate Pinecone index schema.
        
        Returns:
            Schema for Pinecone index
        """
        schema = {
            "name": "netintel-ocr",
            "dimension": self.get_embedding_dimensions(),
            "metric": "cosine",
            "pods": 1,
            "replicas": 1,
            "pod_type": "p1.x1",
            "metadata_config": {
                "indexed": [
                    "document_id",
                    "chunk_index",
                    "content_type",
                    "page_numbers"
                ]
            }
        }
        
        return schema
    
    def generate_weaviate_schema(self) -> Dict:
        """
        Generate Weaviate class schema.
        
        Returns:
            Schema for Weaviate class
        """
        schema = {
            "class": "Document",
            "description": "NetIntel-OCR extracted document chunks",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada",
                    "modelVersion": "002",
                    "type": "text"
                }
            },
            "properties": [
                {
                    "name": "chunk_id",
                    "dataType": ["string"],
                    "description": "Unique chunk identifier"
                },
                {
                    "name": "document_id",
                    "dataType": ["string"],
                    "description": "Parent document identifier"
                },
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Chunk text content"
                },
                {
                    "name": "chunk_index",
                    "dataType": ["int"],
                    "description": "Chunk position"
                },
                {
                    "name": "page_numbers",
                    "dataType": ["int[]"],
                    "description": "Page numbers"
                },
                {
                    "name": "metadata",
                    "dataType": ["object"],
                    "description": "Additional metadata"
                }
            ]
        }
        
        return schema
    
    def generate_qdrant_schema(self) -> Dict:
        """
        Generate Qdrant collection schema.
        
        Returns:
            Schema for Qdrant collection
        """
        schema = {
            "collection_name": "netintel_ocr",
            "vectors": {
                "size": 1536,
                "distance": "Cosine"
            },
            "optimizers_config": {
                "default_segment_number": 2
            },
            "replication_factor": 1,
            "payload_schema": {
                "document_id": {"type": "keyword"},
                "chunk_index": {"type": "integer"},
                "content": {"type": "text"},
                "content_type": {"type": "keyword"},
                "page_numbers": {"type": "integer[]"},
                "metadata": {"type": "object"}
            }
        }
        
        return schema
    
    def generate_chroma_schema(self) -> Dict:
        """
        Generate Chroma collection schema.
        
        Returns:
            Schema for Chroma collection
        """
        schema = {
            "name": "netintel_ocr",
            "metadata": {
                "description": "NetIntel-OCR document chunks"
            },
            "embedding_function": "openai",
            "distance_metric": "cosine",
            "hnsw_config": {
                "M": 16,
                "ef_construction": 200,
                "ef_search": 150
            }
        }
        
        return schema
    
    def get_embedding_dimensions(self) -> int:
        """Get embedding dimensions for the configured model."""
        if self.embedding_provider == "ollama":
            model_key = self.embedding_model.lower()
            if model_key in self.ollama_models:
                return self.ollama_models[model_key]["dimension"]
            # Default for unknown Ollama models
            return 768
        elif self.embedding_provider == "openai":
            if "ada-002" in self.embedding_model:
                return 1536
            elif "ada-001" in self.embedding_model:
                return 1024
            # Default OpenAI dimension
            return 1536
        else:
            # Default dimension
            return 768
    
    def _get_ollama_host(self) -> str:
        """Get Ollama host from environment or use default."""
        return os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
    
    def generate_embeddings_config(self) -> Dict:
        """
        Generate embedding generation configuration.
        
        Returns:
            Configuration for embedding generation
        """
        if self.embedding_provider == "ollama":
            model_key = self.embedding_model.lower()
            model_info = self.ollama_models.get(model_key, {})
            
            config = {
                "model": self.embedding_model,
                "provider": "ollama",
                "dimension": model_info.get("dimension", 768),
                "batch_size": 10,  # Smaller batch size for local processing
                "max_tokens": model_info.get("max_tokens", 8192),
                "normalize": True,
                "ollama_config": {
                    "base_url": self._get_ollama_host(),
                    "timeout": 30,
                    "keep_alive": "5m"
                },
                "model_info": {
                    "size": model_info.get("size", "unknown"),
                    "layers": model_info.get("layers", "unknown"),
                    "mrl_support": True if "qwen3" in model_key else False,
                    "instruction_aware": True if "qwen3" in model_key else False
                },
                "retry_config": {
                    "max_retries": 3,
                    "initial_delay": 1,
                    "max_delay": 10,
                    "exponential_backoff": True
                }
            }
        else:
            # OpenAI configuration (default)
            config = {
                "model": self.embedding_model,
                "provider": "openai",
                "dimension": self.get_embedding_dimensions(),
                "batch_size": 100,
                "max_tokens": 8191,
                "encoding": "cl100k_base",
                "normalize": True,
                "retry_config": {
                    "max_retries": 3,
                    "initial_delay": 1,
                    "max_delay": 10,
                    "exponential_backoff": True
                },
                "rate_limit": {
                    "requests_per_minute": 3000,
                    "tokens_per_minute": 350000
                }
            }
        
        return config
    
    def generate_index_config(self) -> Dict:
        """
        Generate vector index configuration.
        
        Returns:
            Index configuration for vector search
        """
        config = {
            "index_type": "HNSW",
            "metric": "cosine",
            "parameters": {
                "M": 16,  # Number of connections
                "ef_construction": 200,  # Build-time accuracy
                "ef_search": 150,  # Query-time accuracy
                "max_elements": 1000000  # Maximum vectors
            },
            "quantization": {
                "enabled": False,
                "type": "scalar",
                "bits": 8
            },
            "cache": {
                "enabled": True,
                "size_mb": 1024,
                "ttl_seconds": 3600
            }
        }
        
        return config
    
    def generate_table_schema(self, sample_data: List[Dict]) -> Dict:
        """
        Generate schema from sample table data.
        
        Args:
            sample_data: Sample rows from flattened table
            
        Returns:
            Inferred schema for table data
        """
        if not sample_data:
            return {}
        
        schema = {
            "fields": {},
            "inferred_from": len(sample_data),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
        # Analyze first few rows to infer types
        for row in sample_data[:10]:
            for key, value in row.items():
                if key not in schema["fields"]:
                    schema["fields"][key] = {
                        "type": self._infer_type(value),
                        "nullable": False,
                        "examples": []
                    }
                
                # Add example values
                if len(schema["fields"][key]["examples"]) < 3:
                    if value not in schema["fields"][key]["examples"]:
                        schema["fields"][key]["examples"].append(value)
                
                # Check for nulls
                if value is None:
                    schema["fields"][key]["nullable"] = True
        
        return schema
    
    def _infer_type(self, value: Any) -> str:
        """Infer data type from value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "int64"
        elif isinstance(value, float):
            return "float64"
        elif isinstance(value, str):
            # Check for special string types
            if self._is_date(value):
                return "timestamp"
            elif self._is_url(value):
                return "url"
            elif self._is_email(value):
                return "email"
            elif self._is_ip(value):
                return "ip_address"
            else:
                return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "struct"
        else:
            return "unknown"
    
    def _is_date(self, value: str) -> bool:
        """Check if string is a date."""
        import re
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{2}-\w{3}-\d{4}'
        ]
        return any(re.match(pattern, value) for pattern in date_patterns)
    
    def _is_url(self, value: str) -> bool:
        """Check if string is a URL."""
        return value.startswith(('http://', 'https://', 'ftp://'))
    
    def _is_email(self, value: str) -> bool:
        """Check if string is an email."""
        import re
        return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', value))
    
    def _is_ip(self, value: str) -> bool:
        """Check if string is an IP address."""
        import re
        return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', value))
    
    def generate_schema(self) -> Dict:
        """
        Generate schema based on configured vector format.
        
        Returns:
            Schema dictionary for the configured format
        """
        if self.vector_format == "lancedb":
            return self.generate_lancedb_schema()
        elif self.vector_format == "pinecone":
            return self.generate_pinecone_schema()
        elif self.vector_format == "weaviate":
            return self.generate_weaviate_schema()
        elif self.vector_format == "qdrant":
            return self.generate_qdrant_schema()
        elif self.vector_format == "chroma":
            return self.generate_chroma_schema()
        else:
            # Default to LanceDB
            return self.generate_lancedb_schema()