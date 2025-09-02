"""
Storage Backend for NetIntel-OCR v0.1.12
Provides S3/MinIO integration for distributed LanceDB storage.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import tempfile
import shutil

# Set up logging
logger = logging.getLogger(__name__)


class StorageProvider(Enum):
    """Supported storage providers."""
    LOCAL = "local"
    S3 = "s3"
    MINIO = "minio"
    AZURE = "azure"
    GCS = "gcs"


@dataclass
class StorageConfig:
    """Storage backend configuration."""
    provider: StorageProvider
    endpoint_url: Optional[str]
    access_key: Optional[str]
    secret_key: Optional[str]
    bucket_name: Optional[str]
    region: Optional[str]
    use_ssl: bool = True
    verify_ssl: bool = True


@dataclass
class SyncResult:
    """Result of sync operation."""
    files_uploaded: int
    files_downloaded: int
    files_skipped: int
    bytes_transferred: int
    errors: List[str]
    duration_seconds: float


class StorageBackend:
    """Abstract storage backend interface."""
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload file to storage."""
        raise NotImplementedError
    
    def download(self, remote_path: str, local_path: str) -> bool:
        """Download file from storage."""
        raise NotImplementedError
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists in storage."""
        raise NotImplementedError
    
    def list(self, prefix: str = "") -> List[str]:
        """List files in storage."""
        raise NotImplementedError
    
    def delete(self, remote_path: str) -> bool:
        """Delete file from storage."""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str):
        """Initialize local storage backend."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        """Copy file to local storage."""
        try:
            src = Path(local_path)
            dst = self.base_path / remote_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
    
    def download(self, remote_path: str, local_path: str) -> bool:
        """Copy file from local storage."""
        try:
            src = self.base_path / remote_path
            dst = Path(local_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logger.error(f"Failed to download {remote_path}: {e}")
            return False
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists."""
        return (self.base_path / remote_path).exists()
    
    def list(self, prefix: str = "") -> List[str]:
        """List files in directory."""
        path = self.base_path / prefix
        if not path.exists():
            return []
        
        files = []
        for item in path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(self.base_path)
                files.append(str(rel_path))
        return files
    
    def delete(self, remote_path: str) -> bool:
        """Delete file."""
        try:
            (self.base_path / remote_path).unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete {remote_path}: {e}")
            return False


class S3StorageBackend(StorageBackend):
    """S3/MinIO storage backend."""
    
    def __init__(self, config: StorageConfig):
        """Initialize S3 storage backend."""
        self.config = config
        self._client = None
    
    def _get_client(self):
        """Get or create S3 client."""
        if self._client is None:
            try:
                import boto3
                from botocore.config import Config
                
                # Configure client
                client_config = Config(
                    region_name=self.config.region,
                    signature_version='s3v4',
                    retries={'max_attempts': 3}
                )
                
                # Create client
                if self.config.provider == StorageProvider.MINIO:
                    # MinIO configuration
                    self._client = boto3.client(
                        's3',
                        endpoint_url=self.config.endpoint_url,
                        aws_access_key_id=self.config.access_key,
                        aws_secret_access_key=self.config.secret_key,
                        config=client_config,
                        use_ssl=self.config.use_ssl,
                        verify=self.config.verify_ssl
                    )
                else:
                    # Standard S3
                    self._client = boto3.client(
                        's3',
                        aws_access_key_id=self.config.access_key,
                        aws_secret_access_key=self.config.secret_key,
                        config=client_config
                    )
                
                # Ensure bucket exists
                self._ensure_bucket()
                
            except ImportError:
                logger.error("boto3 is required for S3 storage. Install with: pip install boto3")
                raise
            except Exception as e:
                logger.error(f"Failed to create S3 client: {e}")
                raise
        
        return self._client
    
    def _ensure_bucket(self):
        """Ensure bucket exists."""
        try:
            client = self._client
            
            # Check if bucket exists
            try:
                client.head_bucket(Bucket=self.config.bucket_name)
            except:
                # Create bucket
                if self.config.region and self.config.region != 'us-east-1':
                    client.create_bucket(
                        Bucket=self.config.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.config.region}
                    )
                else:
                    client.create_bucket(Bucket=self.config.bucket_name)
                
                logger.info(f"Created bucket: {self.config.bucket_name}")
                
        except Exception as e:
            logger.error(f"Failed to ensure bucket: {e}")
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload file to S3."""
        try:
            client = self._get_client()
            client.upload_file(
                local_path,
                self.config.bucket_name,
                remote_path
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to S3: {e}")
            return False
    
    def download(self, remote_path: str, local_path: str) -> bool:
        """Download file from S3."""
        try:
            client = self._get_client()
            
            # Ensure local directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            client.download_file(
                self.config.bucket_name,
                remote_path,
                local_path
            )
            return True
        except Exception as e:
            logger.error(f"Failed to download {remote_path} from S3: {e}")
            return False
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists in S3."""
        try:
            client = self._get_client()
            client.head_object(
                Bucket=self.config.bucket_name,
                Key=remote_path
            )
            return True
        except:
            return False
    
    def list(self, prefix: str = "") -> List[str]:
        """List files in S3."""
        try:
            client = self._get_client()
            
            files = []
            paginator = client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(
                Bucket=self.config.bucket_name,
                Prefix=prefix
            ):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append(obj['Key'])
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return []
    
    def delete(self, remote_path: str) -> bool:
        """Delete file from S3."""
        try:
            client = self._get_client()
            client.delete_object(
                Bucket=self.config.bucket_name,
                Key=remote_path
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete {remote_path} from S3: {e}")
            return False


class LanceDBStorageManager:
    """Manages LanceDB storage with cloud backend support."""
    
    def __init__(self,
                 local_path: str = "output/lancedb",
                 storage_config: Optional[StorageConfig] = None):
        """
        Initialize LanceDB storage manager.
        
        Args:
            local_path: Local LanceDB path
            storage_config: Optional cloud storage configuration
        """
        self.local_path = Path(local_path)
        self.local_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage backend
        if storage_config:
            if storage_config.provider == StorageProvider.LOCAL:
                self.backend = LocalStorageBackend(storage_config.endpoint_url or ".")
            elif storage_config.provider in [StorageProvider.S3, StorageProvider.MINIO]:
                self.backend = S3StorageBackend(storage_config)
            else:
                raise ValueError(f"Unsupported storage provider: {storage_config.provider}")
        else:
            self.backend = None
    
    def sync_to_cloud(self,
                     force: bool = False,
                     progress_callback: Optional[callable] = None) -> SyncResult:
        """
        Sync local LanceDB to cloud storage.
        
        Args:
            force: Force overwrite existing files
            progress_callback: Progress callback function
            
        Returns:
            SyncResult with statistics
        """
        if not self.backend:
            return SyncResult(
                files_uploaded=0,
                files_downloaded=0,
                files_skipped=0,
                bytes_transferred=0,
                errors=["No storage backend configured"],
                duration_seconds=0
            )
        
        start_time = datetime.now()
        files_uploaded = 0
        files_skipped = 0
        bytes_transferred = 0
        errors = []
        
        # Get all local files
        local_files = []
        for file_path in self.local_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.local_path)
                local_files.append((file_path, rel_path))
        
        total_files = len(local_files)
        
        # Upload each file
        for idx, (local_file, rel_path) in enumerate(local_files):
            remote_path = f"lancedb/{rel_path}"
            
            if progress_callback:
                progress_callback(idx, total_files, f"Uploading {rel_path}")
            
            # Check if file exists
            if not force and self.backend.exists(remote_path):
                # Compare checksums
                if self._files_match(local_file, remote_path):
                    files_skipped += 1
                    continue
            
            # Upload file
            if self.backend.upload(str(local_file), remote_path):
                files_uploaded += 1
                bytes_transferred += local_file.stat().st_size
            else:
                errors.append(f"Failed to upload {rel_path}")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return SyncResult(
            files_uploaded=files_uploaded,
            files_downloaded=0,
            files_skipped=files_skipped,
            bytes_transferred=bytes_transferred,
            errors=errors,
            duration_seconds=duration
        )
    
    def sync_from_cloud(self,
                       force: bool = False,
                       progress_callback: Optional[callable] = None) -> SyncResult:
        """
        Sync cloud storage to local LanceDB.
        
        Args:
            force: Force overwrite existing files
            progress_callback: Progress callback function
            
        Returns:
            SyncResult with statistics
        """
        if not self.backend:
            return SyncResult(
                files_uploaded=0,
                files_downloaded=0,
                files_skipped=0,
                bytes_transferred=0,
                errors=["No storage backend configured"],
                duration_seconds=0
            )
        
        start_time = datetime.now()
        files_downloaded = 0
        files_skipped = 0
        bytes_transferred = 0
        errors = []
        
        # List remote files
        remote_files = self.backend.list("lancedb/")
        total_files = len(remote_files)
        
        # Download each file
        for idx, remote_path in enumerate(remote_files):
            # Strip prefix
            rel_path = remote_path.replace("lancedb/", "")
            local_file = self.local_path / rel_path
            
            if progress_callback:
                progress_callback(idx, total_files, f"Downloading {rel_path}")
            
            # Check if file exists
            if not force and local_file.exists():
                # Compare checksums
                if self._files_match(local_file, remote_path):
                    files_skipped += 1
                    continue
            
            # Download file
            if self.backend.download(remote_path, str(local_file)):
                files_downloaded += 1
                bytes_transferred += local_file.stat().st_size
            else:
                errors.append(f"Failed to download {rel_path}")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return SyncResult(
            files_uploaded=0,
            files_downloaded=files_downloaded,
            files_skipped=files_skipped,
            bytes_transferred=bytes_transferred,
            errors=errors,
            duration_seconds=duration
        )
    
    def _files_match(self, local_file: Path, remote_path: str) -> bool:
        """
        Check if local and remote files match.
        
        Args:
            local_file: Local file path
            remote_path: Remote file path
            
        Returns:
            True if files match
        """
        # For now, just compare sizes
        # In production, would compare checksums
        try:
            # This would need actual implementation to get remote file size
            return False
        except:
            return False
    
    def get_lancedb_uri(self) -> str:
        """
        Get LanceDB URI for cloud storage.
        
        Returns:
            URI string for LanceDB connection
        """
        if not self.backend or not isinstance(self.backend, S3StorageBackend):
            return str(self.local_path)
        
        # Build S3 URI for LanceDB
        config = self.backend.config
        
        if config.provider == StorageProvider.MINIO:
            # MinIO URI format
            return f"s3://{config.bucket_name}/lancedb?endpoint={config.endpoint_url}"
        else:
            # Standard S3 URI
            return f"s3://{config.bucket_name}/lancedb"
    
    def backup_to_cloud(self,
                       backup_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create backup of local LanceDB in cloud.
        
        Args:
            backup_name: Optional backup name
            
        Returns:
            Tuple of (success, backup_path)
        """
        if not self.backend:
            return False, "No storage backend configured"
        
        # Generate backup name
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create temporary archive
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
            try:
                import tarfile
                
                # Create archive
                with tarfile.open(tmp.name, 'w:gz') as tar:
                    tar.add(self.local_path, arcname='lancedb')
                
                # Upload to cloud
                remote_path = f"backups/{backup_name}.tar.gz"
                if self.backend.upload(tmp.name, remote_path):
                    return True, remote_path
                else:
                    return False, "Failed to upload backup"
                    
            finally:
                # Clean up temp file
                Path(tmp.name).unlink(missing_ok=True)
    
    def restore_from_cloud(self,
                          backup_path: str,
                          force: bool = False) -> bool:
        """
        Restore LanceDB from cloud backup.
        
        Args:
            backup_path: Path to backup in cloud
            force: Force overwrite existing data
            
        Returns:
            True if successful
        """
        if not self.backend:
            logger.error("No storage backend configured")
            return False
        
        # Check if local data exists
        if self.local_path.exists() and any(self.local_path.iterdir()):
            if not force:
                logger.error("Local data exists. Use force=True to overwrite")
                return False
        
        # Download backup
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
            try:
                # Download from cloud
                if not self.backend.download(backup_path, tmp.name):
                    return False
                
                import tarfile
                
                # Clear local directory
                if force and self.local_path.exists():
                    shutil.rmtree(self.local_path)
                
                # Extract archive
                with tarfile.open(tmp.name, 'r:gz') as tar:
                    tar.extractall(self.local_path.parent)
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to restore backup: {e}")
                return False
                
            finally:
                # Clean up temp file
                Path(tmp.name).unlink(missing_ok=True)
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        stats = {
            'local_files': 0,
            'local_size_bytes': 0,
            'remote_files': 0,
            'backend_type': 'local'
        }
        
        # Count local files
        for file_path in self.local_path.rglob("*"):
            if file_path.is_file():
                stats['local_files'] += 1
                stats['local_size_bytes'] += file_path.stat().st_size
        
        # Count remote files if backend exists
        if self.backend:
            stats['backend_type'] = type(self.backend).__name__
            stats['remote_files'] = len(self.backend.list("lancedb/"))
        
        return stats