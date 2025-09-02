"""
Batch Processing Pipeline for NetIntel-OCR v0.1.12
Handles parallel processing of multiple PDFs with progress tracking and auto-merge.
"""

import os
import json
import hashlib
import multiprocessing as mp
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# Set up logging
logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Status of document processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DocumentStatus:
    """Status of a document in batch processing."""
    file_path: str
    md5_checksum: str
    status: ProcessingStatus
    pages_processed: int
    total_pages: int
    chunks_generated: int
    error_message: Optional[str]
    processing_time: float
    

@dataclass
class BatchResult:
    """Result of batch processing."""
    total_files: int
    processed: int
    failed: int
    skipped: int
    total_chunks: int
    total_time: float
    documents: List[DocumentStatus]


class BatchProcessor:
    """Batch processor for multiple PDF documents."""
    
    def __init__(self,
                 output_dir: str = "output",
                 parallel_workers: int = 4,
                 auto_merge: bool = True,
                 checkpoint_dir: Optional[str] = None):
        """
        Initialize batch processor.
        
        Args:
            output_dir: Output directory for processed documents
            parallel_workers: Number of parallel workers
            auto_merge: Automatically merge to centralized DB
            checkpoint_dir: Directory for checkpoints
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.parallel_workers = parallel_workers
        self.auto_merge = auto_merge
        
        # Checkpoint directory
        if checkpoint_dir:
            self.checkpoint_dir = Path(checkpoint_dir)
        else:
            self.checkpoint_dir = self.output_dir / ".batch_checkpoint"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Processing state
        self.documents_status = {}
        self.start_time = None
    
    def process_batch(self,
                     input_patterns: List[str],
                     dedupe: bool = True,
                     resume: bool = True,
                     progress_callback: Optional[Callable] = None,
                     error_strategy: str = "continue") -> BatchResult:
        """
        Process multiple PDFs in parallel.
        
        Args:
            input_patterns: List of file patterns or paths
            dedupe: Skip already processed documents
            resume: Resume from checkpoint if exists
            progress_callback: Callback for progress updates
            error_strategy: "continue", "stop", or "retry"
            
        Returns:
            BatchResult with processing statistics
        """
        self.start_time = datetime.now()
        
        # Discover documents
        documents = self._discover_documents(input_patterns)
        
        if not documents:
            return BatchResult(
                total_files=0,
                processed=0,
                failed=0,
                skipped=0,
                total_chunks=0,
                total_time=0,
                documents=[]
            )
        
        # Load checkpoint if resuming
        if resume:
            self._load_checkpoint()
        
        # Filter already processed if deduping
        if dedupe:
            documents = self._filter_processed(documents)
        
        total_files = len(documents)
        logger.info(f"Starting batch processing of {total_files} documents")
        
        # Initialize progress
        processed = 0
        failed = 0
        skipped = 0
        total_chunks = 0
        
        # Process documents in parallel
        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            # Submit all tasks
            futures = {}
            for doc_path in documents:
                md5_checksum = self._calculate_md5(doc_path)
                
                # Check if already processed
                if md5_checksum in self.documents_status:
                    status = self.documents_status[md5_checksum]
                    if status.status == ProcessingStatus.COMPLETED:
                        skipped += 1
                        continue
                
                # Submit processing task
                future = executor.submit(
                    self._process_document,
                    doc_path,
                    md5_checksum
                )
                futures[future] = doc_path
            
            # Process results as they complete
            with tqdm(total=len(futures), desc="Processing documents") as pbar:
                for future in as_completed(futures):
                    doc_path = futures[future]
                    
                    try:
                        status = future.result()
                        
                        # Update counters
                        if status.status == ProcessingStatus.COMPLETED:
                            processed += 1
                            total_chunks += status.chunks_generated
                        elif status.status == ProcessingStatus.FAILED:
                            failed += 1
                            
                            if error_strategy == "stop":
                                # Cancel remaining tasks
                                for f in futures:
                                    f.cancel()
                                break
                            elif error_strategy == "retry":
                                # Retry failed document
                                self._retry_document(doc_path, status)
                        
                        # Update progress
                        pbar.update(1)
                        
                        if progress_callback:
                            progress_callback(
                                processed + failed + skipped,
                                total_files,
                                f"Processed {doc_path.name}"
                            )
                        
                        # Save checkpoint
                        self._save_checkpoint()
                        
                    except Exception as e:
                        logger.error(f"Error processing {doc_path}: {e}")
                        failed += 1
        
        # Auto-merge if enabled
        if self.auto_merge and processed > 0:
            self._merge_to_centralized()
        
        # Calculate total time
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        # Create result
        return BatchResult(
            total_files=total_files,
            processed=processed,
            failed=failed,
            skipped=skipped,
            total_chunks=total_chunks,
            total_time=total_time,
            documents=list(self.documents_status.values())
        )
    
    def _discover_documents(self, patterns: List[str]) -> List[Path]:
        """
        Discover PDF documents from patterns.
        
        Args:
            patterns: File patterns or paths
            
        Returns:
            List of PDF file paths
        """
        documents = []
        
        for pattern in patterns:
            path = Path(pattern)
            
            if path.is_file() and path.suffix.lower() == '.pdf':
                documents.append(path)
            elif path.is_dir():
                # Find all PDFs in directory
                documents.extend(path.glob("*.pdf"))
                documents.extend(path.glob("*.PDF"))
            else:
                # Treat as glob pattern
                documents.extend(Path().glob(pattern))
        
        # Remove duplicates and sort
        documents = sorted(set(documents))
        
        return documents
    
    def _filter_processed(self, documents: List[Path]) -> List[Path]:
        """
        Filter out already processed documents.
        
        Args:
            documents: List of document paths
            
        Returns:
            Filtered list
        """
        filtered = []
        
        for doc_path in documents:
            md5_checksum = self._calculate_md5(doc_path)
            
            # Check if output already exists
            output_path = self.output_dir / md5_checksum
            if output_path.exists():
                chunks_file = output_path / "lancedb" / "chunks.jsonl"
                if chunks_file.exists():
                    logger.info(f"Skipping already processed: {doc_path.name}")
                    
                    # Add to status
                    self.documents_status[md5_checksum] = DocumentStatus(
                        file_path=str(doc_path),
                        md5_checksum=md5_checksum,
                        status=ProcessingStatus.SKIPPED,
                        pages_processed=0,
                        total_pages=0,
                        chunks_generated=self._count_chunks(chunks_file),
                        error_message=None,
                        processing_time=0
                    )
                    continue
            
            filtered.append(doc_path)
        
        return filtered
    
    def _process_document(self,
                         doc_path: Path,
                         md5_checksum: str) -> DocumentStatus:
        """
        Process a single document.
        
        Args:
            doc_path: Path to PDF document
            md5_checksum: MD5 checksum of document
            
        Returns:
            Document processing status
        """
        start_time = time.time()
        
        try:
            # Import here to avoid circular dependency
            from .hybrid_processor import process_pdf_hybrid
            
            # Process document
            logger.info(f"Processing {doc_path.name}")
            
            # Call the hybrid processor
            process_pdf_hybrid(
                pdf_path=str(doc_path),
                output_dir=str(self.output_dir),
                auto_detect=True,
                generate_vector=True,
                quiet=True
            )
            
            # Count generated chunks
            chunks_file = self.output_dir / md5_checksum / "lancedb" / "chunks.jsonl"
            chunks_count = self._count_chunks(chunks_file) if chunks_file.exists() else 0
            
            # Get page count
            import fitz
            with fitz.open(str(doc_path)) as pdf:
                page_count = len(pdf)
            
            # Create status
            status = DocumentStatus(
                file_path=str(doc_path),
                md5_checksum=md5_checksum,
                status=ProcessingStatus.COMPLETED,
                pages_processed=page_count,
                total_pages=page_count,
                chunks_generated=chunks_count,
                error_message=None,
                processing_time=time.time() - start_time
            )
            
            # Update status
            self.documents_status[md5_checksum] = status
            
            return status
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to process {doc_path.name}: {error_msg}")
            
            # Create failed status
            status = DocumentStatus(
                file_path=str(doc_path),
                md5_checksum=md5_checksum,
                status=ProcessingStatus.FAILED,
                pages_processed=0,
                total_pages=0,
                chunks_generated=0,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )
            
            # Update status
            self.documents_status[md5_checksum] = status
            
            return status
    
    def _retry_document(self, doc_path: Path, prev_status: DocumentStatus):
        """
        Retry processing a failed document.
        
        Args:
            doc_path: Document path
            prev_status: Previous status
        """
        logger.info(f"Retrying {doc_path.name}")
        
        # Wait a bit before retry
        time.sleep(2)
        
        # Try processing again
        md5_checksum = self._calculate_md5(doc_path)
        new_status = self._process_document(doc_path, md5_checksum)
        
        # Update status
        self.documents_status[md5_checksum] = new_status
    
    def _merge_to_centralized(self):
        """Merge processed documents to centralized database."""
        try:
            from .centralized_db import CentralizedDatabaseManager
            
            logger.info("Auto-merging to centralized database")
            
            manager = CentralizedDatabaseManager(
                centralized_path=str(self.output_dir / "lancedb")
            )
            
            result = manager.merge_to_centralized(
                source_dir=str(self.output_dir),
                dedupe=True
            )
            
            logger.info(f"Merged {result.documents_merged} documents to centralized DB")
            
        except Exception as e:
            logger.error(f"Failed to merge to centralized DB: {e}")
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _count_chunks(self, chunks_file: Path) -> int:
        """Count chunks in JSONL file."""
        if not chunks_file.exists():
            return 0
        
        count = 0
        with open(chunks_file, 'r') as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
    
    def _save_checkpoint(self):
        """Save processing checkpoint."""
        checkpoint_file = self.checkpoint_dir / "batch_checkpoint.json"
        
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'documents': {
                md5: asdict(status)
                for md5, status in self.documents_status.items()
            }
        }
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def _load_checkpoint(self):
        """Load processing checkpoint."""
        checkpoint_file = self.checkpoint_dir / "batch_checkpoint.json"
        
        if not checkpoint_file.exists():
            return
        
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Restore documents status
            for md5, status_dict in checkpoint_data.get('documents', {}).items():
                self.documents_status[md5] = DocumentStatus(
                    file_path=status_dict['file_path'],
                    md5_checksum=status_dict['md5_checksum'],
                    status=ProcessingStatus(status_dict['status']),
                    pages_processed=status_dict['pages_processed'],
                    total_pages=status_dict['total_pages'],
                    chunks_generated=status_dict['chunks_generated'],
                    error_message=status_dict.get('error_message'),
                    processing_time=status_dict['processing_time']
                )
            
            logger.info(f"Loaded checkpoint with {len(self.documents_status)} documents")
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
    
    def get_progress_stats(self) -> Dict:
        """Get current progress statistics."""
        total = len(self.documents_status)
        completed = sum(1 for s in self.documents_status.values() 
                       if s.status == ProcessingStatus.COMPLETED)
        failed = sum(1 for s in self.documents_status.values()
                    if s.status == ProcessingStatus.FAILED)
        skipped = sum(1 for s in self.documents_status.values()
                     if s.status == ProcessingStatus.SKIPPED)
        
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'skipped': skipped,
            'in_progress': total - completed - failed - skipped,
            'completion_percentage': (completed / total * 100) if total > 0 else 0
        }
    
    def export_report(self, output_file: str):
        """
        Export processing report.
        
        Args:
            output_file: Output file path
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_progress_stats(),
            'documents': [
                asdict(status)
                for status in self.documents_status.values()
            ]
        }
        
        output_path = Path(output_file)
        
        if output_path.suffix == '.json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
        elif output_path.suffix == '.csv':
            import csv
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, 
                    fieldnames=['file_path', 'md5_checksum', 'status', 
                               'pages_processed', 'chunks_generated', 
                               'processing_time', 'error_message'])
                writer.writeheader()
                for status in self.documents_status.values():
                    writer.writerow(asdict(status))
        else:
            # Default to text
            with open(output_path, 'w') as f:
                f.write(f"Batch Processing Report\n")
                f.write(f"Generated: {report['timestamp']}\n\n")
                f.write(f"Statistics:\n")
                for key, value in report['statistics'].items():
                    f.write(f"  {key}: {value}\n")
                f.write(f"\nDocuments:\n")
                for status in self.documents_status.values():
                    f.write(f"  - {Path(status.file_path).name}: {status.status.value}\n")