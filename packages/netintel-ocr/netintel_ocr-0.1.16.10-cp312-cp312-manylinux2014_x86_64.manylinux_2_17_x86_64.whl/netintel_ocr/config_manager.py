"""
Configuration Manager for NetIntel-OCR v0.1.12
Handles YAML configuration files and environment variables with full support for
centralized database, embeddings, batch processing, and cloud storage.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import json


class ConfigManager:
    """Manage configuration from YAML files and environment variables."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        self.config = {}
        self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            # Load default configuration
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "processing": {
                "max_pages": 100,
                "mode": "hybrid",
                "parallel_workers": 4,
                "batch_size": 32,
                "auto_merge": True,
                "dedupe": True,
                "timeouts": {
                    "text_extraction": 120,
                    "network_detection": 60,
                    "component_extraction": 60,
                    "mermaid_generation": 60
                },
                "confidence": {
                    "network_detection": 0.7,
                    "table_detection": 0.6
                }
            },
            "models": {
                "text": {
                    "primary": "nanonets-ocr-s:latest",
                    "fallback": "qwen2.5vl:latest"
                },
                "network": {
                    "primary": "qwen2.5vl:latest",
                    "fallback": "llava:latest"
                },
                "embedding": {
                    "model": "nomic-embed-text",
                    "dimension": 768,
                    "provider": "ollama",
                    "batch_size": 32,
                    "cache_enabled": True,
                    "cache_ttl_hours": 24
                }
            },
            "vector": {
                "enabled": True,
                "chunk_size": 1000,
                "chunk_overlap": 100,
                "chunk_strategy": "semantic",
                "lancedb": {
                    "local_path": "output/lancedb",
                    "centralized": True,
                    "centralized_path": "output/lancedb",
                    "batch_size": 100,
                    "sync_enabled": False
                },
                "query": {
                    "default_limit": 10,
                    "similarity_threshold": 0.7,
                    "rerank_enabled": False,
                    "rerank_model": "bge-reranker-base",
                    "output_format": "json"
                }
            },
            "storage": {
                "input_dir": "input",
                "output_dir": "output",
                "s3": {
                    "enabled": False,
                    "endpoint": os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
                    "bucket": "netintel-ocr",
                    "region": "us-east-1",
                    "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY")
                },
                "cache_dir": ".cache",
                "checkpoint_dir": ".checkpoint",
                "cleanup": {
                    "keep_images": False,
                    "archive_after_days": 30,
                    "compress_archives": True
                }
            },
            "ollama": {
                "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                "timeout": 30,
                "keep_alive": "5m"
            },
            "logging": {
                "level": os.getenv("NETINTEL_LOG_LEVEL", "INFO"),
                "file": "output/netintel-ocr.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "performance": {
                "max_workers": 4,
                "max_memory_mb": 4096,
                "cache": {
                    "enabled": True,
                    "path": "output/.cache",
                    "max_size_mb": 1024
                }
            },
            "monitoring": {
                "enabled": False,
                "metrics_port": 9090,
                "log_level": "INFO",
                "trace_enabled": False,
                "progress_callback": None
            },
            "network_diagram": {
                "use_icons": True,
                "fast_extraction": False,
                "multi_diagram": False,
                "diagram_only": False
            },
            "table_extraction": {
                "enabled": True,
                "method": "hybrid",
                "skip_toc": True
            }
        }
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        # Map of environment variables to config paths
        env_mappings = {
            "OLLAMA_HOST": ["ollama", "host"],
            "NETINTEL_OUTPUT": ["storage", "output_dir"],
            "NETINTEL_LOG_LEVEL": ["logging", "level"],
            "NETINTEL_LANCEDB_URI": ["vector", "lancedb", "uri"],
            "NETINTEL_CENTRALIZED_DB": ["vector", "lancedb", "centralized"],
            "NETINTEL_CENTRALIZED_PATH": ["vector", "lancedb", "centralized_path"],
            "NETINTEL_EMBEDDING_MODEL": ["models", "embedding", "model"],
            "NETINTEL_EMBEDDING_PROVIDER": ["models", "embedding", "provider"],
            "NETINTEL_BATCH_SIZE": ["processing", "batch_size"],
            "NETINTEL_PARALLEL_WORKERS": ["processing", "parallel_workers"],
            "NETINTEL_AUTO_MERGE": ["processing", "auto_merge"],
            "NETINTEL_DEDUPE": ["processing", "dedupe"],
            "NETINTEL_QUERY_LIMIT": ["vector", "query", "default_limit"],
            "NETINTEL_RERANK": ["vector", "query", "rerank_enabled"],
            "MINIO_ENDPOINT": ["storage", "s3", "endpoint"],
            "MINIO_BUCKET": ["storage", "s3", "bucket"],
            "AWS_ACCESS_KEY_ID": ["storage", "s3", "access_key"],
            "AWS_SECRET_ACCESS_KEY": ["storage", "s3", "secret_key"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config_path, value)
    
    def _set_nested_value(self, path: list, value: Any):
        """Set a value in nested dictionary using path."""
        current = self.config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string booleans
        if isinstance(value, str):
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
        
        current[path[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            path: Dot-separated path (e.g., "models.text.primary")
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split(".")
        current = self.config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def get_model_config(self, task: str = "text") -> Dict[str, str]:
        """
        Get model configuration for specific task.
        
        Args:
            task: Task type (text, network, embedding)
            
        Returns:
            Model configuration dictionary
        """
        if task == "embedding":
            return self.get("models.embedding", {})
        
        model_config = self.get(f"models.{task}", {})
        if isinstance(model_config, dict):
            return {
                "primary": model_config.get("primary", "qwen2.5vl:latest"),
                "fallback": model_config.get("fallback", "llava:latest")
            }
        return {"primary": "qwen2.5vl:latest", "fallback": "llava:latest"}
    
    def get_timeout(self, operation: str) -> int:
        """
        Get timeout for specific operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Timeout in seconds
        """
        timeout_map = {
            "text": "text_extraction",
            "network": "network_detection",
            "component": "component_extraction",
            "mermaid": "mermaid_generation"
        }
        
        timeout_key = timeout_map.get(operation, operation)
        return self.get(f"processing.timeouts.{timeout_key}", 60)
    
    def get_vector_config(self) -> Dict[str, Any]:
        """Get vector generation configuration."""
        return self.get("vector", {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration."""
        return self.get("storage", {})
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration."""
        return self.get("models.embedding", {})
    
    def get_batch_config(self) -> Dict[str, Any]:
        """Get batch processing configuration."""
        return {
            "parallel_workers": self.get("processing.parallel_workers", 4),
            "batch_size": self.get("processing.batch_size", 32),
            "auto_merge": self.get("processing.auto_merge", True),
            "dedupe": self.get("processing.dedupe", True)
        }
    
    def get_query_config(self) -> Dict[str, Any]:
        """Get query engine configuration."""
        return self.get("vector.query", {})
    
    def get_centralized_config(self) -> Dict[str, Any]:
        """Get centralized database configuration."""
        return {
            "centralized_path": self.get("vector.lancedb.centralized_path", "output/lancedb"),
            "compute_embeddings": self.get("models.embedding.cache_enabled", True),
            "sync_enabled": self.get("vector.lancedb.sync_enabled", False)
        }
    
    def is_s3_enabled(self) -> bool:
        """Check if S3/MinIO storage is enabled."""
        return self.get("storage.s3.enabled", False)
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama configuration."""
        return self.get("ollama", {})
    
    def save_config(self, output_path: Optional[str] = None):
        """
        Save current configuration to YAML file.
        
        Args:
            output_path: Path to save configuration (uses original path if not provided)
        """
        save_path = output_path or self.config_path
        if save_path:
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config.copy()
    
    def merge_cli_args(self, args):
        """
        Merge CLI arguments into configuration.
        
        Args:
            args: Parsed command-line arguments
        """
        # Map CLI arguments to configuration paths
        cli_mappings = {
            "model": ["models", "text", "primary"],
            "network_model": ["models", "network", "primary"],
            "embedding_model": ["models", "embedding", "model"],
            "chunk_size": ["vector", "chunk_size"],
            "chunk_overlap": ["vector", "chunk_overlap"],
            "chunk_strategy": ["vector", "chunk_strategy"],
            "parallel": ["processing", "parallel_workers"],
            "auto_merge": ["processing", "auto_merge"],
            "dedupe": ["processing", "dedupe"],
            "compute_embeddings": ["models", "embedding", "cache_enabled"],
            "query_limit": ["vector", "query", "default_limit"],
            "rerank": ["vector", "query", "rerank_enabled"],
            "similarity_threshold": ["vector", "query", "similarity_threshold"],
            "output_format": ["vector", "query", "output_format"],
            "embedding_provider": ["models", "embedding", "provider"],
            "timeout": ["processing", "timeouts", "network_detection"],
            "confidence": ["processing", "confidence", "network_detection"],
            "output": ["storage", "output_dir"],
            "keep_images": ["storage", "cleanup", "keep_images"],
            "no_icons": ["network_diagram", "use_icons"],
            "fast_extraction": ["network_diagram", "fast_extraction"],
            "multi_diagram": ["network_diagram", "multi_diagram"],
            "diagram_only": ["network_diagram", "diagram_only"],
            "text_only": ["processing", "mode"],
            "network_only": ["processing", "mode"],
            "no_vector": ["vector", "enabled"],
        }
        
        for arg_name, config_path in cli_mappings.items():
            if hasattr(args, arg_name):
                value = getattr(args, arg_name)
                if value is not None:
                    # Handle special cases
                    if arg_name == "no_icons":
                        value = not value
                    elif arg_name == "no_vector":
                        value = not value
                    elif arg_name == "text_only" and value:
                        value = "text-only"
                    elif arg_name == "network_only" and value:
                        value = "network-only"
                    elif arg_name in ["text_only", "network_only"] and not value:
                        continue
                    
                    self._set_nested_value(config_path, value)
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_paths = [
            "processing.max_pages",
            "models.text.primary",
            "ollama.host",
            "storage.output_dir"
        ]
        
        for path in required_paths:
            if self.get(path) is None:
                errors.append(f"Missing required configuration: {path}")
        
        # Validate numeric values
        if self.get("processing.max_pages", 0) <= 0:
            errors.append("processing.max_pages must be positive")
        
        if self.get("vector.chunk_size", 0) <= 0:
            errors.append("vector.chunk_size must be positive")
        
        # Validate timeouts
        for timeout_key in ["text_extraction", "network_detection"]:
            timeout = self.get(f"processing.timeouts.{timeout_key}", 0)
            if timeout <= 0:
                errors.append(f"processing.timeouts.{timeout_key} must be positive")
        
        return len(errors) == 0, errors