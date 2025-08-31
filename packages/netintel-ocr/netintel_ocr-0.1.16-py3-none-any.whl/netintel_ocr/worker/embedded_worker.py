"""
Embedded Workers for Resource-Limited Environments

This module provides in-process PDF processing workers that run within the API
server process, eliminating the need for separate Kubernetes jobs or containers.
Suitable for small deployments with limited resources.
"""

import os
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Optional, Dict, Any, List
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from ..processor import process_pdf
from ..hybrid_processor import process_pdf_hybrid
from ..network_processor import process_pdf_network_diagrams

logger = logging.getLogger(__name__)


class EmbeddedWorkerConfig:
    """Configuration for embedded workers"""
    
    def __init__(
        self,
        max_workers: int = 2,
        mode: str = "threaded",
        timeout: int = 300,
        use_local_storage: bool = False,
        storage_path: str = "./data"
    ):
        """
        Initialize embedded worker configuration.
        
        Args:
            max_workers: Maximum number of concurrent workers
            mode: "threaded" or "process" for executor type
            timeout: Maximum time per PDF in seconds
            use_local_storage: Use local filesystem instead of MinIO
            storage_path: Path for local storage
        """
        self.max_workers = max_workers
        self.mode = mode
        self.timeout = timeout
        self.use_local_storage = use_local_storage
        self.storage_path = Path(storage_path)
        
        # Create storage directories if using local storage
        if use_local_storage:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            (self.storage_path / "documents").mkdir(exist_ok=True)
            (self.storage_path / "processing").mkdir(exist_ok=True)
            (self.storage_path / "output").mkdir(exist_ok=True)
    
    def get_executor(self):
        """Get the appropriate executor based on mode"""
        if self.mode == "threaded":
            return ThreadPoolExecutor(max_workers=self.max_workers)
        else:
            return ProcessPoolExecutor(max_workers=self.max_workers)


class EmbeddedWorkerPool:
    """Manages a pool of embedded workers for PDF processing"""
    
    def __init__(self, config: EmbeddedWorkerConfig):
        """
        Initialize the worker pool.
        
        Args:
            config: Worker configuration
        """
        self.config = config
        self.executor = config.get_executor()
        self.active_jobs: Dict[str, asyncio.Future] = {}
        self.completed_jobs: List[str] = []
        self.failed_jobs: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized embedded worker pool with {config.max_workers} workers in {config.mode} mode")
    
    async def process_pdf_async(
        self,
        pdf_path: str,
        job_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a PDF asynchronously using embedded workers.
        
        Args:
            pdf_path: Path to the PDF file
            job_id: Unique job identifier
            options: Processing options
            
        Returns:
            Processing result dictionary
        """
        if job_id in self.active_jobs:
            raise ValueError(f"Job {job_id} is already being processed")
        
        # Set default options
        if options is None:
            options = {}
        
        # Configure storage based on settings
        if self.config.use_local_storage:
            options["output_dir"] = str(self.config.storage_path / "output")
            options["use_local_storage"] = True
        
        # Create a future for this job
        loop = asyncio.get_event_loop()
        
        try:
            # Mark job as active
            self.active_jobs[job_id] = asyncio.create_task(
                self._process_in_executor(pdf_path, options, job_id)
            )
            
            # Wait for completion with timeout
            result = await asyncio.wait_for(
                self.active_jobs[job_id],
                timeout=self.config.timeout
            )
            
            # Mark as completed
            self.completed_jobs.append(job_id)
            del self.active_jobs[job_id]
            
            return {
                "status": "completed",
                "job_id": job_id,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            # Handle timeout
            logger.error(f"Job {job_id} timed out after {self.config.timeout} seconds")
            self.failed_jobs.append({
                "job_id": job_id,
                "error": "Processing timeout",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Cancel the task
            if job_id in self.active_jobs:
                self.active_jobs[job_id].cancel()
                del self.active_jobs[job_id]
            
            return {
                "status": "failed",
                "job_id": job_id,
                "error": f"Processing timed out after {self.config.timeout} seconds",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Handle other errors
            logger.error(f"Job {job_id} failed: {str(e)}")
            self.failed_jobs.append({
                "job_id": job_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Remove from active jobs
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            
            return {
                "status": "failed",
                "job_id": job_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _process_in_executor(
        self,
        pdf_path: str,
        options: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:
        """
        Run PDF processing in the executor.
        
        Args:
            pdf_path: Path to PDF file
            options: Processing options
            job_id: Job identifier
            
        Returns:
            Processing result
        """
        loop = asyncio.get_event_loop()
        
        # Determine processing mode
        mode = options.get("mode", "hybrid")
        
        # Select the appropriate processor
        if mode == "network":
            processor_func = process_pdf_network_diagrams
        elif mode == "text":
            processor_func = process_pdf
        else:
            processor_func = process_pdf_hybrid
        
        # Run in executor
        result = await loop.run_in_executor(
            self.executor,
            self._process_wrapper,
            processor_func,
            pdf_path,
            options,
            job_id
        )
        
        return result
    
    def _process_wrapper(
        self,
        processor_func,
        pdf_path: str,
        options: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:
        """
        Wrapper function for processing in executor.
        
        Args:
            processor_func: The processing function to use
            pdf_path: Path to PDF
            options: Processing options
            job_id: Job identifier
            
        Returns:
            Processing result
        """
        # Create a temporary working directory for this job
        work_dir = None
        
        try:
            if self.config.use_local_storage:
                work_dir = self.config.storage_path / "processing" / job_id
                work_dir.mkdir(parents=True, exist_ok=True)
                options["work_dir"] = str(work_dir)
            else:
                work_dir = Path(tempfile.mkdtemp(prefix=f"netintel_{job_id}_"))
                options["work_dir"] = str(work_dir)
            
            # Log processing start
            logger.info(f"Starting embedded processing for job {job_id}")
            
            # Process the PDF
            result = processor_func(pdf_path, **options)
            
            # Add job metadata
            result["job_id"] = job_id
            result["worker_type"] = "embedded"
            result["worker_mode"] = self.config.mode
            
            logger.info(f"Completed embedded processing for job {job_id}")
            
            return result
            
        finally:
            # Clean up temporary directory if not using local storage
            if work_dir and not self.config.use_local_storage:
                try:
                    shutil.rmtree(work_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up work directory: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the worker pool.
        
        Returns:
            Status dictionary
        """
        return {
            "max_workers": self.config.max_workers,
            "mode": self.config.mode,
            "active_jobs": len(self.active_jobs),
            "active_job_ids": list(self.active_jobs.keys()),
            "completed_jobs": len(self.completed_jobs),
            "failed_jobs": len(self.failed_jobs),
            "storage_mode": "local" if self.config.use_local_storage else "minio"
        }
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status or None if not found
        """
        if job_id in self.active_jobs:
            return {
                "job_id": job_id,
                "status": "processing",
                "worker_type": "embedded"
            }
        elif job_id in self.completed_jobs:
            return {
                "job_id": job_id,
                "status": "completed",
                "worker_type": "embedded"
            }
        else:
            # Check failed jobs
            for failed in self.failed_jobs:
                if failed["job_id"] == job_id:
                    return {
                        "job_id": job_id,
                        "status": "failed",
                        "error": failed["error"],
                        "timestamp": failed["timestamp"],
                        "worker_type": "embedded"
                    }
        
        return None
    
    def shutdown(self):
        """Shutdown the worker pool"""
        logger.info("Shutting down embedded worker pool")
        
        # Cancel active jobs
        for job_id, future in self.active_jobs.items():
            logger.warning(f"Cancelling active job {job_id}")
            future.cancel()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Embedded worker pool shutdown complete")


class LocalStorageAdapter:
    """
    Local filesystem storage adapter for minimal deployments.
    Provides MinIO-compatible interface using local filesystem.
    """
    
    def __init__(self, base_path: str = "./data"):
        """
        Initialize local storage adapter.
        
        Args:
            base_path: Base directory for storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create standard directories
        (self.base_path / "documents").mkdir(exist_ok=True)
        (self.base_path / "centralized").mkdir(exist_ok=True)
        (self.base_path / "temp").mkdir(exist_ok=True)
    
    def store_document(self, document_id: str, content: bytes) -> str:
        """
        Store a document locally.
        
        Args:
            document_id: Document identifier (MD5)
            content: Document content
            
        Returns:
            Path to stored document
        """
        doc_path = self.base_path / "documents" / document_id
        doc_path.mkdir(parents=True, exist_ok=True)
        
        # Store PDF
        pdf_path = doc_path / "raw.pdf"
        pdf_path.write_bytes(content)
        
        # Create subdirectories for processing
        (doc_path / "images").mkdir(exist_ok=True)
        (doc_path / "markdown").mkdir(exist_ok=True)
        (doc_path / "vectors").mkdir(exist_ok=True)
        (doc_path / "lancedb").mkdir(exist_ok=True)
        
        return str(pdf_path)
    
    def get_document(self, document_id: str) -> bytes:
        """
        Retrieve a document from local storage.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Document content
        """
        pdf_path = self.base_path / "documents" / document_id / "raw.pdf"
        if not pdf_path.exists():
            raise FileNotFoundError(f"Document {document_id} not found")
        
        return pdf_path.read_bytes()
    
    def list_documents(self) -> List[str]:
        """
        List all stored documents.
        
        Returns:
            List of document IDs
        """
        docs_dir = self.base_path / "documents"
        if not docs_dir.exists():
            return []
        
        return [d.name for d in docs_dir.iterdir() if d.is_dir()]
    
    def delete_document(self, document_id: str):
        """
        Delete a document from storage.
        
        Args:
            document_id: Document identifier
        """
        doc_path = self.base_path / "documents" / document_id
        if doc_path.exists():
            shutil.rmtree(doc_path)
    
    def get_document_metadata(self, document_id: str) -> Dict[str, Any]:
        """
        Get metadata for a document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Document metadata
        """
        doc_path = self.base_path / "documents" / document_id
        if not doc_path.exists():
            raise FileNotFoundError(f"Document {document_id} not found")
        
        pdf_path = doc_path / "raw.pdf"
        
        return {
            "document_id": document_id,
            "size": pdf_path.stat().st_size if pdf_path.exists() else 0,
            "created": datetime.fromtimestamp(doc_path.stat().st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(doc_path.stat().st_mtime).isoformat(),
            "storage_type": "local"
        }


# Singleton instance for the worker pool
_worker_pool: Optional[EmbeddedWorkerPool] = None


def get_worker_pool(config: Optional[EmbeddedWorkerConfig] = None) -> EmbeddedWorkerPool:
    """
    Get or create the singleton worker pool.
    
    Args:
        config: Worker configuration (used only on first call)
        
    Returns:
        The worker pool instance
    """
    global _worker_pool
    
    if _worker_pool is None:
        if config is None:
            config = EmbeddedWorkerConfig()
        _worker_pool = EmbeddedWorkerPool(config)
    
    return _worker_pool


def shutdown_worker_pool():
    """Shutdown the global worker pool"""
    global _worker_pool
    
    if _worker_pool is not None:
        _worker_pool.shutdown()
        _worker_pool = None