"""
NetIntel-OCR initialization command for v0.1.15
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any


def initialize_config():
    """Initialize NetIntel-OCR configuration with Milvus as default"""
    
    # Check for OLLAMA_HOST environment variable
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    
    # Ask for deployment scale
    print("\nNetIntel-OCR v0.1.15 Configuration")
    print("=" * 40)
    print("\nSelect deployment scale:")
    print("1. Development (8GB RAM, 4 CPU) - Development/Testing/Small Teams [DEFAULT]")
    print("2. Production (16GB+ RAM, 8+ CPU) - Enterprise")
    
    scale_choice = input("\nEnter choice (1-2) [default: 1]: ").strip() or "1"
    
    scale_configs = {
        "1": {
            "name": "development",
            "milvus_deployment": "standalone",
            "workers": 4,
            "dedup_mode": "full",  # All features
            "index_type": "IVF_SQ8"
        },
        "2": {
            "name": "production",
            "milvus_deployment": "distributed",
            "workers": 8,
            "dedup_mode": "full",
            "index_type": "IVF_SQ8"
        }
    }
    
    selected_scale = scale_configs.get(scale_choice, scale_configs["1"])
    
    config = {
        "version": "0.1.15",
        "deployment": {
            "scale": selected_scale["name"],
            "workers": selected_scale["workers"]
        },
        "vector_db": {
            "type": "milvus",
            "host": "localhost",
            "port": 19530,
            "collection_name": "netintel_vectors",
            "deployment_type": selected_scale["milvus_deployment"],
            "index_type": selected_scale["index_type"]
        },
        "embedding": {
            "provider": "ollama",
            "model": "qwen3-embedding:8b",
            "ollama_host": ollama_host,
            "dimension": 4096,
            "batch_size": 32
        },
        "deduplication": {
            "mode": selected_scale["dedup_mode"],
            "simhash_bits": 64 if selected_scale["name"] == "development" else 128,
            "hamming_threshold": 5,
            "cdc_min_length": 128
        },
        "processing": {
            "pdf_dpi": 300,
            "ocr_engine": "tesseract",
            "parallel_workers": selected_scale["workers"]
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "cors_enabled": True
        }
    }
    
    # Create config directory
    config_dir = Path.home() / ".netintel-ocr"
    config_dir.mkdir(exist_ok=True)
    
    # Write configuration
    config_file = config_dir / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"\n✓ Configuration initialized at {config_file}")
    print(f"✓ Deployment scale: {selected_scale['name'].upper()}")
    print(f"✓ Vector database: Milvus ({selected_scale['milvus_deployment']})")
    print(f"✓ Index type: {selected_scale['index_type']}")
    print(f"✓ Deduplication mode: {selected_scale['dedup_mode']}")
    print(f"✓ Parallel workers: {selected_scale['workers']}")
    print(f"✓ Embedding provider: Ollama ({ollama_host})")
    print(f"✓ Embedding model: qwen3-embedding:8b (4096 dimensions)")
    print(f"✓ Default collection: netintel_vectors")
    
    # Check if Docker Compose setup is needed (for non-production scales)
    if selected_scale["name"] != "production":
        if input("\nWould you like to set up Milvus with Docker Compose? (y/n): ").lower() == 'y':
            setup_docker_compose(selected_scale)
    else:
        print("\nFor PRODUCTION scale, use Kubernetes deployment:")
        print("  helm install milvus milvus/milvus --namespace netintel-system")
        print("  See docs/spec-0115-milvus.md for full Kubernetes setup")
    
    return config_file


def setup_docker_compose(scale_config):
    """Generate Docker Compose configuration for Milvus based on scale"""
    
    compose_dir = Path.cwd() / "netintel-deploy"
    compose_dir.mkdir(exist_ok=True)
    
    # Get OLLAMA_HOST from environment or use default
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    
    # Adjust resources based on scale
    resource_configs = {
        "development": {
            "milvus_memory": "4g",
            "minio_memory": "2g",
            "etcd_memory": "1g"
        },
        "production": {
            "milvus_memory": "8g",
            "minio_memory": "4g",
            "etcd_memory": "2g"
        }
    }
    
    resources = resource_configs.get(scale_config["name"], resource_configs["development"])
    
    # Generate docker-compose.yml
    compose_content = f"""version: '3.8'

services:
  etcd:
    container_name: milvus-etcd
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
    volumes:
      - ./volumes/etcd:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    deploy:
      resources:
        limits:
          memory: {resources['etcd_memory']}

  minio:
    container_name: milvus-minio
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    ports:
      - "9001:9001"
    volumes:
      - ./volumes/minio:/minio_data
    command: minio server /minio_data --console-address ":9001"
    deploy:
      resources:
        limits:
          memory: {resources['minio_memory']}

  milvus:
    container_name: milvus-standalone
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - ./volumes/milvus:/var/lib/milvus
      - ./milvus-{scale_config['name']}.yaml:/milvus/configs/milvus.yaml
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - etcd
      - minio
    deploy:
      resources:
        limits:
          memory: {resources['milvus_memory']}

  netintel-ocr:
    container_name: netintel-ocr
    image: netintel/ocr:latest
    environment:
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - OLLAMA_HOST={ollama_host}  # Uses existing Ollama server, not containerized
      - DEPLOYMENT_SCALE={scale_config['name']}
      - PARALLEL_WORKERS={scale_config['workers']}
      - DEDUP_MODE={scale_config['dedup_mode']}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    ports:
      - "8000:8000"
    depends_on:
      - milvus
    # Note: Ollama runs on host machine, not in Docker
"""
    
    compose_file = compose_dir / "docker-compose.yml"
    with open(compose_file, 'w') as f:
        f.write(compose_content)
    
    # Create Milvus configuration for the scale
    milvus_config = generate_milvus_config(scale_config)
    milvus_config_file = compose_dir / f"milvus-{scale_config['name']}.yaml"
    with open(milvus_config_file, 'w') as f:
        yaml.dump(milvus_config, f)
    
    # Create directories
    (compose_dir / "volumes").mkdir(exist_ok=True)
    (compose_dir / "data").mkdir(exist_ok=True)
    (compose_dir / "output").mkdir(exist_ok=True)
    
    print(f"\n✓ Docker Compose configuration created at {compose_dir}")
    print(f"✓ Deployment scale: {scale_config['name'].upper()}")
    print(f"✓ Resource limits: Milvus={resources['milvus_memory']}, MinIO={resources['minio_memory']}")
    print(f"✓ Configured to use Ollama at: {ollama_host}")
    print("\nIMPORTANT: Ensure Ollama is running on your host machine:")
    print(f"  ollama serve  # If not already running")
    print(f"  ollama pull qwen3-embedding:8b  # If model not pulled")
    print("\nTo start Milvus, run:")
    print(f"  cd {compose_dir}")
    print("  docker-compose up -d")


def generate_milvus_config(scale_config):
    """Generate Milvus configuration based on deployment scale"""
    
    base_config = {
        "etcd": {
            "endpoints": ["etcd:2379"]
        },
        "minio": {
            "address": "minio",
            "port": 9000,
            "accessKeyID": "minioadmin",
            "secretAccessKey": "minioadmin",
            "useSSL": False,
            "bucketName": "milvus-bucket"
        }
    }
    
    # Scale-specific optimizations
    if scale_config["name"] == "development":
        base_config.update({
            "dataNode": {"parallelism": 4},
            "indexNode": {"parallelism": 2},
            "queryNode": {"parallelism": 4},
            "common": {
                "cacheSize": 2048,  # MB
                "gracefulTime": 5000  # ms
            }
        })
    elif scale_config["name"] == "production":
        base_config.update({
            "dataNode": {"parallelism": 8},
            "indexNode": {"parallelism": 4},
            "queryNode": {"parallelism": 8},
            "common": {
                "cacheSize": 4096,  # MB
                "gracefulTime": 10000  # ms
            }
        })
    
    return base_config


if __name__ == "__main__":
    initialize_config()