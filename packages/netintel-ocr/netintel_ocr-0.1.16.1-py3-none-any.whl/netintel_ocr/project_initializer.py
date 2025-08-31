"""
Project Initializer for NetIntel-OCR v0.1.13
Creates complete containerized environment with Docker, Helm, and configuration files.
Now includes support for multiple deployment scales and server modes.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
import yaml
import json


class ProjectInitializer:
    """Initialize NetIntel-OCR project with Docker and Kubernetes support."""
    
    def __init__(self, base_dir: str = "./netintel-ocr", 
                 deployment_scale: str = "all",
                 with_kubernetes: bool = False):
        """
        Initialize the project initializer.
        
        Args:
            base_dir: Base directory for project initialization
            deployment_scale: Scale of deployment (minimal, small, medium, large, all)
            with_kubernetes: Whether to include Kubernetes/Helm charts
        """
        self.base_dir = Path(base_dir)
        self.deployment_scale = deployment_scale
        self.with_kubernetes = with_kubernetes
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://192.168.68.20:11434")
    
    def initialize_project(self, force: bool = False) -> bool:
        """
        Initialize complete NetIntel-OCR project structure.
        
        Args:
            force: Force overwrite existing files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if directory exists
            if self.base_dir.exists() and not force:
                print(f"❌ Directory {self.base_dir} already exists. Use --force to overwrite.")
                return False
            
            # Create directory structure
            self._create_directory_structure()
            
            # Create Docker files
            self._create_dockerfile()
            
            # Create Docker Compose files based on deployment scale
            if self.deployment_scale in ["minimal", "all"]:
                self._create_docker_compose_minimal()
                
            if self.deployment_scale in ["small", "all"]:
                self._create_docker_compose_small()
                
            if self.deployment_scale in ["medium", "all"]:
                self._create_docker_compose_medium()
                
            if self.deployment_scale in ["large", "all"]:
                self._create_docker_compose_large()
                
            # Always create dev compose for development
            self._create_docker_compose_dev()
            
            # Create Helm charts if requested
            if self.with_kubernetes or self.deployment_scale in ["large", "all"]:
                self._create_helm_chart()
            
            # Create configuration files
            self._create_config_yaml()
            self._create_env_file()
            
            # Create README
            self._create_readme()
            
            print(f"✅ Successfully initialized NetIntel-OCR project at {self.base_dir}")
            print(f"\n📦 Deployment scale: {self.deployment_scale.upper()}")
            
            # Show what was created
            print(f"\n📁 Created files:")
            if self.deployment_scale == "minimal" or self.deployment_scale == "all":
                print(f"   • docker/docker-compose.minimal.yml - Single container deployment")
            if self.deployment_scale == "small" or self.deployment_scale == "all":
                print(f"   • docker/docker-compose.yml - Small team deployment (2-5 users)")
            if self.deployment_scale == "medium" or self.deployment_scale == "all":
                print(f"   • docker/docker-compose.medium.yml - Department deployment (5-20 users)")
            if self.deployment_scale == "large" or self.deployment_scale == "all":
                print(f"   • docker/docker-compose.large.yml - Enterprise deployment (20+ users)")
            if self.with_kubernetes or self.deployment_scale in ["large", "all"]:
                print(f"   • helm/netintel-ocr/ - Kubernetes Helm charts")
            print(f"   • docker/Dockerfile - Container image")
            print(f"   • config/config.yaml - Configuration file")
            print(f"   • .env - Environment variables")
            
            print(f"\n📋 Next steps:")
            print(f"   1. cd {self.base_dir}")
            print(f"   2. Update .env with your Ollama server address")
            
            if self.deployment_scale == "minimal":
                print(f"   3. docker-compose -f docker/docker-compose.minimal.yml up")
                print(f"      Access API at http://localhost:8000")
                print(f"      Access MCP at http://localhost:8001")
            elif self.deployment_scale == "small":
                print(f"   3. cd docker && docker-compose up -d")
                print(f"      API with embedded workers at http://localhost:8000")
                print(f"      Optional: docker-compose --profile with-mcp up -d")
            elif self.deployment_scale == "medium":
                print(f"   3. docker-compose -f docker/docker-compose.medium.yml up -d")
                print(f"      API at http://localhost:8000")
                print(f"      MCP instances at ports 8001-8002")
                print(f"      Load balancer at port 8003")
            elif self.deployment_scale == "large":
                print(f"   3. docker-compose -f docker/docker-compose.large.yml up -d")
                print(f"      HAProxy at http://localhost:80")
                print(f"      Grafana at http://localhost:3000")
                print(f"      Prometheus at http://localhost:9090")
                if self.with_kubernetes:
                    print(f"   OR use Kubernetes:")
                    print(f"      helm install netintel-ocr ./helm")
            else:  # all
                print(f"   3. Choose your deployment scale:")
                print(f"      • Minimal: docker-compose -f docker/docker-compose.minimal.yml up")
                print(f"      • Small:   cd docker && docker-compose up -d")
                print(f"      • Medium:  docker-compose -f docker/docker-compose.medium.yml up -d")
                print(f"      • Large:   docker-compose -f docker/docker-compose.large.yml up -d")
                if self.with_kubernetes:
                    print(f"      • K8s:     helm install netintel-ocr ./helm")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing project: {e}")
            return False
    
    def _create_directory_structure(self):
        """Create the project directory structure."""
        directories = [
            self.base_dir / "docker",
            self.base_dir / "helm" / "templates",
            self.base_dir / "config",
            self.base_dir / "input",
            self.base_dir / "output",
            self.base_dir / "scripts",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _create_dockerfile(self):
        """Create Dockerfile for NetIntel-OCR."""
        # First create requirements.txt
        requirements_content = '''# NetIntel-OCR Requirements
pillow>=11.2.1
pymupdf>=1.26.1
requests>=2.32.4
tqdm>=4.67.1
opencv-python-headless>=4.5.0
pdfplumber>=0.10.0
pandas>=2.0.0
jsonschema>=4.0.0
pyyaml>=6.0.0
netintel-ocr
'''
        requirements_path = self.base_dir / "docker" / "requirements.txt"
        requirements_path.write_text(requirements_content)
        
        dockerfile_content = '''FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    libmupdf-dev \\
    mupdf-tools \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /data/input /data/output /data/models /config

# Set environment variables
ENV OLLAMA_HOST=${OLLAMA_HOST:-http://192.168.68.20:11434}
ENV NETINTEL_OUTPUT=/data/output
ENV NETINTEL_CONFIG=/config/config.yml
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1000 netintel && \\
    chown -R netintel:netintel /data /config

USER netintel

WORKDIR /data

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f ${OLLAMA_HOST}/api/tags || exit 1

ENTRYPOINT ["netintel-ocr"]
CMD ["--help"]
'''
        
        dockerfile_path = self.base_dir / "docker" / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)
    
    def _create_docker_compose_small(self):
        """Create docker-compose.yml for small scale deployment (2-5 users)."""
        compose_content = '''# NetIntel-OCR v0.1.13 - Small Scale Deployment
# Suitable for small teams (2-5 users, 10-50 PDFs/day)
version: '3.8'

services:
  netintel-ocr:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netintel-ocr
    volumes:
      - ../input:/data/input
      - ../output:/data/output
      - ../config:/config
    environment:
      - OLLAMA_HOST=${OLLAMA_HOST:-http://192.168.68.20:11434}
      - MINIO_ENDPOINT=http://minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
      - NETINTEL_LOG_LEVEL=${NETINTEL_LOG_LEVEL:-INFO}
    depends_on:
      minio:
        condition: service_healthy
    networks:
      - netintel-network
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    container_name: netintel-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - ../output:/data
      - minio-data:/minio-data
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY:-minioadmin}
      - MINIO_VOLUMES=/minio-data
    command: server /minio-data --console-address ":9001"
    networks:
      - netintel-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    restart: unless-stopped

  minio-init:
    image: minio/mc:latest
    container_name: netintel-minio-init
    depends_on:
      minio:
        condition: service_healthy
    environment:
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
    entrypoint: >
      /bin/sh -c "
      mc alias set myminio http://minio:9000 $${MINIO_ACCESS_KEY} $${MINIO_SECRET_KEY};
      mc mb myminio/lancedb || true;
      mc mb myminio/documents || true;
      mc policy set public myminio/lancedb;
      mc policy set public myminio/documents;
      mc version enable myminio/lancedb || true;
      echo 'MinIO initialization complete';
      exit 0;
      "
    networks:
      - netintel-network

volumes:
  minio-data:
    driver: local

networks:
  netintel-network:
    driver: bridge
'''
        
        compose_path = self.base_dir / "docker" / "docker-compose.yml"
        compose_path.write_text(compose_content)
    
    def _create_docker_compose_minimal(self):
        """Create docker-compose.minimal.yml for single-container deployment."""
        minimal_content = '''# NetIntel-OCR v0.1.13 - Minimal Deployment
# Single container with all services (API, MCP, Workers)
version: '3.8'

services:
  netintel-all:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netintel-all
    command: [
      "python", "-m", "netintel_ocr.cli",
      "--all-in-one",
      "--local-storage",
      "--sqlite-queue",
      "--max-workers", "1"
    ]
    ports:
      - "8000:8000"  # API
      - "8001:8001"  # MCP
    volumes:
      - ../data:/data
      - ../input:/input
      - ../output:/output
    environment:
      - MODE=minimal
      - MAX_CONCURRENT_PDFS=1
      - OLLAMA_HOST=${OLLAMA_HOST:-http://192.168.68.20:11434}
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
'''
        path = self.base_dir / "docker" / "docker-compose.minimal.yml"
        path.write_text(minimal_content)
    
    def _create_docker_compose_medium(self):
        """Create docker-compose.medium.yml for medium scale deployment (5-20 users)."""
        medium_content = '''# NetIntel-OCR v0.1.13 - Medium Scale Deployment
# Suitable for departments/teams (5-20 users, 50-200 PDFs/day)
version: '3.8'

services:
  # API Server with more workers
  netintel-api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netintel-api
    command: [
      "python", "-m", "netintel_ocr.cli",
      "--api",
      "--embedded-workers",
      "--max-workers", "4"
    ]
    ports:
      - "8000:8000"
    volumes:
      - ../data:/data
      - ../input:/input
      - ../output:/output
    environment:
      - OLLAMA_HOST=${OLLAMA_HOST:-http://192.168.68.20:11434}
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-admin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-password123}
      - MAX_CONCURRENT_PDFS=5
      - WORKER_MODE=embedded
    depends_on:
      - minio
      - redis
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  # MCP Server cluster (2 instances)
  netintel-mcp-1:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netintel-mcp-1
    command: ["python", "-m", "netintel_ocr.cli", "--mcp", "--mcp-port", "8001"]
    ports:
      - "8001:8001"
    volumes:
      - ../data:/data:ro
      - ../output:/output:ro
    environment:
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-admin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-password123}
    depends_on:
      - minio
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G

  netintel-mcp-2:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netintel-mcp-2
    command: ["python", "-m", "netintel_ocr.cli", "--mcp", "--mcp-port", "8002"]
    ports:
      - "8002:8002"
    volumes:
      - ../data:/data:ro
      - ../output:/output:ro
    environment:
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-admin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-password123}
    depends_on:
      - minio
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G

  # Nginx Load Balancer for MCP
  nginx:
    image: nginx:alpine
    container_name: netintel-nginx
    ports:
      - "8003:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - netintel-mcp-1
      - netintel-mcp-2
    networks:
      - netintel-network
    restart: unless-stopped

  # MinIO with more resources
  minio:
    image: minio/minio:latest
    container_name: netintel-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY:-admin}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY:-password123}
    volumes:
      - minio-data:/data
    command: server /data --console-address ":9001"
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

  # Redis with persistence
  redis:
    image: redis:7-alpine
    container_name: netintel-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G

volumes:
  minio-data:
  redis-data:

networks:
  netintel-network:
    driver: bridge
'''
        
        compose_path = self.base_dir / "docker" / "docker-compose.medium.yml"
        compose_path.write_text(compose_content)
        
        # Also create nginx.conf for load balancing
        nginx_conf = '''events {
    worker_connections 1024;
}

http {
    upstream mcp_servers {
        server netintel-mcp-1:8001;
        server netintel-mcp-2:8002;
    }

    server {
        listen 80;
        
        location / {
            proxy_pass http://mcp_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
'''
        nginx_path = self.base_dir / "docker" / "nginx.conf"
        nginx_path.write_text(nginx_conf)
    
    def _create_docker_compose_large(self):
        """Create docker-compose.large.yml for large scale/enterprise deployment."""
        large_content = '''# NetIntel-OCR v0.1.13 - Large Scale/Enterprise Deployment
# Suitable for enterprise (20-100+ users, 200+ PDFs/day)
# Note: For true enterprise scale, use Kubernetes deployment
version: '3.8'

services:
  # API Server (single instance for consistency)
  netintel-api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netintel-api
    command: ["python", "-m", "netintel_ocr.cli", "--api"]
    ports:
      - "8000:8000"
    volumes:
      - ../data:/data
      - ../input:/input
      - ../output:/output
    environment:
      - ENV=production
      - OLLAMA_HOST=${OLLAMA_HOST:-http://192.168.68.20:11434}
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio1:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-admin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-password123}
      - WORKER_MODE=external
    depends_on:
      - minio1
      - minio2
      - redis-master
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G

  # MCP Server cluster (5 instances)
  netintel-mcp-1:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    command: ["python", "-m", "netintel_ocr.cli", "--mcp"]
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  # PDF Processing Workers (separate containers)
  netintel-worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    command: ["python", "-m", "netintel_ocr.worker.standalone"]
    volumes:
      - ../data:/data
      - ../input:/input
      - ../output:/output
    environment:
      - REDIS_URL=redis://redis-master:6379
      - MINIO_ENDPOINT=minio1:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-admin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-password123}
      - OLLAMA_HOST=${OLLAMA_HOST:-http://192.168.68.20:11434}
    depends_on:
      - redis-master
      - minio1
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      replicas: 5  # 5 parallel workers
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  # HAProxy Load Balancer
  haproxy:
    image: haproxy:alpine
    container_name: netintel-haproxy
    ports:
      - "80:80"      # Main entry point
      - "8001:8001"  # MCP load balanced endpoint
      - "8404:8404"  # HAProxy stats
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
    depends_on:
      - netintel-api
      - netintel-mcp-1
    networks:
      - netintel-network
    restart: unless-stopped

  # MinIO Distributed (2 nodes for demonstration)
  minio1:
    image: minio/minio:latest
    hostname: minio1
    ports:
      - "9001:9000"
    volumes:
      - minio1-data:/data
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY:-admin}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY:-password123}
    command: server http://minio{1...2}/data
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  minio2:
    image: minio/minio:latest
    hostname: minio2
    ports:
      - "9002:9000"
    volumes:
      - minio2-data:/data
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY:-admin}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY:-password123}
    command: server http://minio{1...2}/data
    networks:
      - netintel-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  # Redis Master-Slave setup
  redis-master:
    image: redis:7-alpine
    container_name: netintel-redis-master
    ports:
      - "6379:6379"
    volumes:
      - redis-master-data:/data
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    networks:
      - netintel-network
    restart: unless-stopped

  redis-slave:
    image: redis:7-alpine
    container_name: netintel-redis-slave
    ports:
      - "6380:6379"
    volumes:
      - redis-slave-data:/data
    command: redis-server --appendonly yes --replicaof redis-master 6379
    depends_on:
      - redis-master
    networks:
      - netintel-network
    restart: unless-stopped

  # Prometheus for monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: netintel-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - netintel-network
    restart: unless-stopped

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    container_name: netintel-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - netintel-network
    restart: unless-stopped

volumes:
  minio1-data:
  minio2-data:
  redis-master-data:
  redis-slave-data:
  prometheus-data:
  grafana-data:

networks:
  netintel-network:
    driver: bridge
'''
        
        compose_path = self.base_dir / "docker" / "docker-compose.large.yml"
        compose_path.write_text(compose_content)
        
        # Create HAProxy configuration
        haproxy_cfg = '''global
    log stdout local0
    maxconn 4096

defaults
    mode http
    log global
    option httplog
    option dontlognull
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend api_frontend
    bind *:80
    default_backend api_backend

backend api_backend
    balance roundrobin
    server api1 netintel-api:8000 check

frontend mcp_frontend
    bind *:8001
    default_backend mcp_backend

backend mcp_backend
    balance roundrobin
    server mcp1 netintel-mcp-1:8001 check
    server mcp2 netintel-mcp-1:8001 check
    server mcp3 netintel-mcp-1:8001 check
    server mcp4 netintel-mcp-1:8001 check
    server mcp5 netintel-mcp-1:8001 check

stats enable
stats uri /stats
stats refresh 30s
'''
        haproxy_path = self.base_dir / "docker" / "haproxy.cfg"
        haproxy_path.write_text(haproxy_cfg)
        
        # Create Prometheus configuration
        prometheus_yml = '''global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'netintel-api'
    static_configs:
      - targets: ['netintel-api:8000']
  
  - job_name: 'netintel-mcp'
    static_configs:
      - targets: ['netintel-mcp-1:8001']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-master:6379', 'redis-slave:6379']
'''
        prometheus_path = self.base_dir / "docker" / "prometheus.yml"
        prometheus_path.write_text(prometheus_yml)
    
    def _create_docker_compose_production(self):
        """Create docker-compose.production.yml for production deployment."""
        production_content = '''# NetIntel-OCR v0.1.13 - Production Deployment
# Full scale with separate services
version: '3.8'

services:
  netintel-api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    command: ["python", "-m", "netintel_ocr.cli", "--api"]
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio:9000
      - OLLAMA_HOST=${OLLAMA_HOST}
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '4.0'
          memory: 4G
    depends_on:
      - redis
      - minio

  netintel-mcp:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    command: ["python", "-m", "netintel_ocr.cli", "--mcp"]
    ports:
      - "8001:8001"
    environment:
      - ENV=production
      - MINIO_ENDPOINT=minio:9000
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    depends_on:
      - minio

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY:-admin}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY:-password123}
    command: server /data --console-address ":9001"
    volumes:
      - minio-data:/data

volumes:
  minio-data:
'''
        path = self.base_dir / "docker" / "docker-compose.production.yml"
        path.write_text(production_content)
    
    def _create_docker_compose_dev(self):
        """Create docker-compose.dev.yml for development environment."""
        dev_content = '''# NetIntel-OCR v0.1.13 - Development Environment
version: '3.8'

services:
  netintel-api-dev:
    build:
      context: ..
      dockerfile: docker/Dockerfile.dev
    command: [
      "python", "-m", "netintel_ocr.cli",
      "--api", "--dev",
      "--embedded-workers",
      "--max-workers", "1"
    ]
    ports:
      - "8000:8000"
      - "5678:5678"  # Debugger
    volumes:
      - ..:/app  # Mount source for hot reload
      - ../data:/data
    environment:
      - ENV=development
      - DEBUG=true
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
    depends_on:
      - redis
      - minio

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=password123
    command: server /data --console-address ":9001"
'''
        path = self.base_dir / "docker" / "docker-compose.dev.yml"
        path.write_text(dev_content)
    
    def _create_helm_chart(self):
        """Create Helm chart for Kubernetes deployment."""
        # Chart.yaml
        chart_yaml = '''apiVersion: v2
name: netintel-ocr
description: A Helm chart for NetIntel-OCR with MinIO integration
type: application
version: 0.1.11
appVersion: "0.1.11"
keywords:
  - pdf-processing
  - ocr
  - vector-database
  - lancedb
  - minio
maintainers:
  - name: NetIntel-OCR Team
    email: support@netintel-ocr.io
'''
        
        # values.yaml
        values_yaml = '''# Default values for netintel-ocr

replicaCount: 1

image:
  repository: netintel-ocr
  pullPolicy: IfNotPresent
  tag: "0.1.11"

nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

# External Ollama configuration
ollama:
  host: "http://ollama-service.ollama-namespace.svc.cluster.local:11434"
  timeout: 30

# MinIO configuration
minio:
  enabled: true
  mode: standalone
  replicas: 1
  rootUser: minioadmin
  rootPassword: minioadmin
  persistence:
    enabled: true
    size: 100Gi
    storageClass: "standard"
  
  buckets:
    - name: lancedb
      policy: public
      versioning: true
    - name: documents
      policy: public

# Storage configuration
storage:
  input:
    enabled: true
    size: 50Gi
    storageClass: "standard"
    accessMode: ReadWriteMany
  
  output:
    enabled: true
    size: 100Gi
    storageClass: "standard"
    accessMode: ReadWriteMany

# ConfigMap settings
config:
  processing:
    maxPages: 100
    mode: hybrid
    timeouts:
      textExtraction: 120
      networkDetection: 60
  
  models:
    text: "nanonets-ocr-s:latest"
    network: "qwen2.5vl:latest"
    embedding: "qwen3-embedding:4b"
  
  vector:
    enabled: true
    chunkSize: 1000
    chunkOverlap: 100

# Resources
resources:
  limits:
    cpu: 4
    memory: 8Gi
  requests:
    cpu: 2
    memory: 4Gi

# Autoscaling
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

# Ingress
ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
  hosts:
    - host: netintel-ocr.local
      paths:
        - path: /
          pathType: Prefix
  tls: []

nodeSelector: {}
tolerations: []
affinity: {}
'''
        
        # deployment.yaml template
        deployment_yaml = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "netintel-ocr.fullname" . }}
  labels:
    {{- include "netintel-ocr.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "netintel-ocr.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "netintel-ocr.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "netintel-ocr.serviceAccountName" . }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          env:
            - name: OLLAMA_HOST
              value: {{ .Values.ollama.host }}
            - name: MINIO_ENDPOINT
              value: "http://{{ include "netintel-ocr.fullname" . }}-minio:9000"
            - name: MINIO_ACCESS_KEY
              value: {{ .Values.minio.rootUser }}
            - name: MINIO_SECRET_KEY
              value: {{ .Values.minio.rootPassword }}
          volumeMounts:
            - name: config
              mountPath: /config
            - name: input
              mountPath: /data/input
            - name: output
              mountPath: /data/output
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
      volumes:
        - name: config
          configMap:
            name: {{ include "netintel-ocr.fullname" . }}
        - name: input
          persistentVolumeClaim:
            claimName: {{ include "netintel-ocr.fullname" . }}-input
        - name: output
          persistentVolumeClaim:
            claimName: {{ include "netintel-ocr.fullname" . }}-output
'''
        
        # _helpers.tpl
        helpers_tpl = '''{{/*
Expand the name of the chart.
*/}}
{{- define "netintel-ocr.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "netintel-ocr.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "netintel-ocr.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "netintel-ocr.labels" -}}
helm.sh/chart: {{ include "netintel-ocr.chart" . }}
{{ include "netintel-ocr.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "netintel-ocr.selectorLabels" -}}
app.kubernetes.io/name: {{ include "netintel-ocr.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "netintel-ocr.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "netintel-ocr.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
'''
        
        # Write Helm files
        (self.base_dir / "helm" / "Chart.yaml").write_text(chart_yaml)
        (self.base_dir / "helm" / "values.yaml").write_text(values_yaml)
        (self.base_dir / "helm" / "templates" / "deployment.yaml").write_text(deployment_yaml)
        (self.base_dir / "helm" / "templates" / "_helpers.tpl").write_text(helpers_tpl)
    
    def _create_config_yaml(self):
        """Create default configuration YAML file."""
        config = {
            "processing": {
                "max_pages": 100,
                "mode": "hybrid",
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
                    "model": "qwen3-embedding:4b",
                    "dimension": 2560
                }
            },
            "vector": {
                "enabled": True,
                "chunk_size": 1000,
                "chunk_overlap": 100,
                "chunk_strategy": "semantic",
                "lancedb": {
                    "local_path": "/data/output/lancedb",
                    "centralized": False,
                    "batch_size": 100
                }
            },
            "storage": {
                "input_dir": "/data/input",
                "output_dir": "/data/output",
                "s3": {
                    "enabled": True,
                    "endpoint": "http://minio:9000",
                    "bucket": "lancedb",
                    "region": "us-east-1"
                },
                "cleanup": {
                    "keep_images": False,
                    "archive_after_days": 30,
                    "compress_archives": True
                }
            },
            "ollama": {
                "host": "${OLLAMA_HOST:-http://192.168.68.20:11434}",
                "timeout": 30,
                "keep_alive": "5m",
                "expected_models": [
                    "nanonets-ocr-s:latest",
                    "qwen2.5vl:latest",
                    "qwen3-embedding:4b"
                ]
            },
            "logging": {
                "level": "INFO",
                "file": "/data/output/netintel-ocr.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "performance": {
                "max_workers": 4,
                "max_memory_mb": 4096,
                "cache": {
                    "enabled": True,
                    "path": "/data/output/.cache",
                    "max_size_mb": 1024
                }
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
        
        config_path = self.base_dir / "config" / "config.yml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    def _create_env_file(self):
        """Create .env file with environment variables."""
        env_content = f'''# NetIntel-OCR Environment Variables
# Generated by netintel-ocr --init

# Ollama Configuration (External Server)
OLLAMA_HOST={self.ollama_host}

# MinIO Configuration
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=lancedb

# NetIntel-OCR Settings
NETINTEL_OUTPUT=/data/output
NETINTEL_CONFIG=/config/config.yml
NETINTEL_LOG_LEVEL=INFO

# Resource Limits
DOCKER_MEMORY_LIMIT=8g
DOCKER_CPU_LIMIT=4

# Vector Database Configuration
NETINTEL_LANCEDB_URI=s3://minio:9000/lancedb
NETINTEL_CENTRALIZED_DB=false
NETINTEL_EMBEDDING_MODEL=qwen3-embedding:4b

# Query Defaults
NETINTEL_QUERY_LIMIT=10
NETINTEL_SIMILARITY_THRESHOLD=0.7
'''
        
        env_path = self.base_dir / ".env"
        env_path.write_text(env_content)
    
    def _create_readme(self):
        """Create README with instructions."""
        readme_content = '''# NetIntel-OCR Containerized Environment

This directory contains a complete NetIntel-OCR deployment with Docker and Kubernetes support.

## Quick Start

### Using Docker Compose

1. **Update Ollama Server Address**:
   Edit `.env` and set your Ollama server address:
   ```
   OLLAMA_HOST=http://your-ollama-server:11434
   ```

2. **Start Services**:
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Process Documents**:
   Place PDFs in the `input/` directory, then run:
   ```bash
   docker-compose run --rm netintel-ocr /data/input/document.pdf
   ```

4. **Access MinIO Console**:
   - URL: http://localhost:9001
   - Username: minioadmin
   - Password: minioadmin

### Using Kubernetes

1. **Install Helm Chart**:
   ```bash
   helm install netintel-ocr ./helm \\
     --namespace netintel-ocr \\
     --create-namespace \\
     --set ollama.host=http://your-ollama-server:11434
   ```

2. **Check Deployment**:
   ```bash
   kubectl get all -n netintel-ocr
   ```

## Directory Structure

```
.
├── docker/               # Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
├── helm/                 # Kubernetes Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── config/               # Configuration files
│   └── config.yml
├── input/                # Input PDFs
├── output/               # Processing output
│   └── <md5>/           # Per-document folders
│       ├── markdown/
│       ├── lancedb/
│       └── tables/
└── .env                  # Environment variables
```

## Configuration

### config.yml
Main configuration file for processing settings, models, and storage options.

### .env
Environment variables for Docker deployment.

### helm/values.yaml
Kubernetes deployment configuration.

## Features

- **Vector Generation**: Automatic LanceDB vector files
- **MinIO Integration**: S3-compatible storage
- **External Ollama**: Uses existing Ollama server
- **Per-Document Processing**: Isolated MD5-based folders
- **Kubernetes Ready**: Full Helm chart included

## Next Steps

- Process multiple documents: `docker-compose run --rm netintel-ocr /data/input/*.pdf`
- Query vectors (coming in v0.1.12): `netintel-ocr --query "network topology"`
- Scale with Kubernetes: Edit `helm/values.yaml` and redeploy

## Support

For issues or questions, please visit:
https://github.com/netintel-ocr/netintel-ocr
'''
        
        readme_path = self.base_dir / "README.md"
        readme_path.write_text(readme_content)