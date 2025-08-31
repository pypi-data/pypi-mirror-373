"""
Configuration module for NetIntel-OCR v0.1.15 with Milvus integration
"""
from pydantic import BaseSettings, Field
from typing import Optional, Literal
import os
from pathlib import Path
import yaml


class VectorDBConfig(BaseSettings):
    """Vector database configuration"""
    
    # Database type
    db_type: Literal["milvus"] = Field(
        default="milvus",
        description="Vector database type (only Milvus in v0.1.15)"
    )
    
    # Milvus configuration
    milvus_host: str = Field(
        default="localhost",
        env="MILVUS_HOST",
        description="Milvus server host"
    )
    
    milvus_port: int = Field(
        default=19530,
        env="MILVUS_PORT",
        description="Milvus server port"
    )
    
    milvus_collection: str = Field(
        default="netintel_vectors",
        env="MILVUS_COLLECTION",
        description="Milvus collection name"
    )
    
    milvus_deployment: Literal["standalone", "distributed"] = Field(
        default="standalone",
        env="MILVUS_DEPLOYMENT",
        description="Milvus deployment type"
    )
    
    # Index configuration
    index_type: str = Field(
        default="IVF_SQ8",
        description="Index type for vectors"
    )
    
    # Connection pool settings
    pool_size: int = Field(
        default=10,
        description="Connection pool size"
    )
    
    # Performance settings
    search_params: dict = Field(
        default={"nprobe": 10},
        description="Search parameters"
    )
    
    index_params: dict = Field(
        default={
            "index_type": "IVF_SQ8",
            "metric_type": "COSINE",
            "params": {"nlist": 1024}
        },
        description="Index parameters"
    )
    
    # Batch settings
    insert_batch_size: int = Field(
        default=1000,
        description="Batch size for insertions"
    )
    
    class Config:
        env_prefix = "VECTOR_DB_"


class EmbeddingConfig(BaseSettings):
    """Embedding configuration"""
    
    provider: Literal["ollama"] = Field(
        default="ollama",
        description="Embedding provider"
    )
    
    model: str = Field(
        default="qwen3-embedding:8b",
        env="EMBEDDING_MODEL",
        description="Embedding model name"
    )
    
    ollama_host: str = Field(
        default_factory=lambda: os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        env="OLLAMA_HOST",
        description="Ollama server URL"
    )
    
    dimension: int = Field(
        default=4096,
        description="Embedding dimension (qwen3-8b uses 4096)"
    )
    
    batch_size: int = Field(
        default=32,
        description="Batch size for embedding generation"
    )
    
    class Config:
        env_prefix = "EMBEDDING_"


class DeduplicationConfig(BaseSettings):
    """Deduplication configuration"""
    
    mode: Literal["exact", "fuzzy", "hybrid", "full"] = Field(
        default="full",
        env="DEDUP_MODE",
        description="Deduplication mode"
    )
    
    simhash_bits: int = Field(
        default=64,
        description="SimHash fingerprint bits (64 or 128)"
    )
    
    hamming_threshold: int = Field(
        default=5,
        description="Hamming distance threshold for near-duplicates"
    )
    
    cdc_min_length: int = Field(
        default=128,
        description="Minimum chunk length for CDC"
    )
    
    use_cpp_core: bool = Field(
        default=True,
        description="Use C++ acceleration if available"
    )
    
    class Config:
        env_prefix = "DEDUP_"


class ProcessingConfig(BaseSettings):
    """Processing configuration"""
    
    pdf_dpi: int = Field(
        default=300,
        description="DPI for PDF rendering"
    )
    
    ocr_engine: str = Field(
        default="tesseract",
        description="OCR engine to use"
    )
    
    parallel_workers: int = Field(
        default=4,
        env="PARALLEL_WORKERS",
        description="Number of parallel workers"
    )
    
    max_file_size_mb: int = Field(
        default=100,
        description="Maximum file size in MB"
    )
    
    class Config:
        env_prefix = "PROCESSING_"


class APIConfig(BaseSettings):
    """API server configuration"""
    
    host: str = Field(
        default="0.0.0.0",
        env="API_HOST",
        description="API server host"
    )
    
    port: int = Field(
        default=8000,
        env="API_PORT",
        description="API server port"
    )
    
    cors_enabled: bool = Field(
        default=True,
        description="Enable CORS"
    )
    
    max_request_size_mb: int = Field(
        default=100,
        description="Maximum request size in MB"
    )
    
    class Config:
        env_prefix = "API_"


class DeploymentConfig(BaseSettings):
    """Deployment configuration"""
    
    scale: Literal["development", "production"] = Field(
        default="development",
        env="DEPLOYMENT_SCALE",
        description="Deployment scale"
    )
    
    workers: int = Field(
        default=4,
        description="Number of workers based on scale"
    )
    
    class Config:
        env_prefix = "DEPLOYMENT_"


class NetIntelConfig(BaseSettings):
    """Main configuration class for NetIntel-OCR"""
    
    version: str = Field(
        default="0.1.15",
        description="NetIntel-OCR version"
    )
    
    # Sub-configurations
    deployment: DeploymentConfig = Field(
        default_factory=DeploymentConfig
    )
    
    vector_db: VectorDBConfig = Field(
        default_factory=VectorDBConfig
    )
    
    embedding: EmbeddingConfig = Field(
        default_factory=EmbeddingConfig
    )
    
    deduplication: DeduplicationConfig = Field(
        default_factory=DeduplicationConfig
    )
    
    processing: ProcessingConfig = Field(
        default_factory=ProcessingConfig
    )
    
    api: APIConfig = Field(
        default_factory=APIConfig
    )
    
    @classmethod
    def load_from_file(cls, config_file: Optional[Path] = None) -> "NetIntelConfig":
        """Load configuration from YAML file"""
        if config_file is None:
            config_file = Path.home() / ".netintel-ocr" / "config.yaml"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                return cls(**config_data)
        
        # Return default configuration if file doesn't exist
        return cls()
    
    def save_to_file(self, config_file: Optional[Path] = None):
        """Save configuration to YAML file"""
        if config_file is None:
            config_file = Path.home() / ".netintel-ocr" / "config.yaml"
        
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            yaml.dump(self.dict(), f, default_flow_style=False)
    
    class Config:
        env_prefix = "NETINTEL_"


# Global configuration instance
_config: Optional[NetIntelConfig] = None


def get_config() -> NetIntelConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = NetIntelConfig.load_from_file()
    return _config


def set_config(config: NetIntelConfig):
    """Set global configuration instance"""
    global _config
    _config = config