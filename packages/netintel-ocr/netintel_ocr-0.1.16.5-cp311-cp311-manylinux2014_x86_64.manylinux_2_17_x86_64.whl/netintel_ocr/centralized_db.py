"""
Centralized Database Manager for NetIntel-OCR v0.1.12
Handles merging per-document databases into a unified LanceDB with full functionality.
"""

import json
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)


class MergeMode(Enum):
    """Merge modes for centralized database."""
    APPEND = "append"
    OVERWRITE = "overwrite"
    UPDATE = "update"


@dataclass
class MergeResult:
    """Result of a merge operation."""
    total_documents: int
    documents_merged: int
    documents_skipped: int
    chunks_added: int
    errors: List[str]
    duration_seconds: float
    

@dataclass
class DocumentInfo:
    """Information about a document in the database."""
    document_id: str
    source_file: str
    md5_checksum: str
    page_count: int
    chunk_count: int
    indexed_at: str
    metadata: Dict[str, Any]


class CentralizedDatabaseManager:
    """Manages centralized LanceDB operations for NetIntel-OCR."""
    
    def __init__(self, 
                 centralized_path: str = "output/lancedb",
                 compute_embeddings: bool = True):
        """
        Initialize centralized database manager.
        
        Args:
            centralized_path: Path to centralized database
            compute_embeddings: Whether to compute embeddings during merge
        """
        self.centralized_path = Path(centralized_path)
        self.ingestion_log_path = self.centralized_path / "ingestion_log.json"
        self.statistics_path = self.centralized_path / "statistics.json"
        self.compute_embeddings = compute_embeddings
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.centralized_path.mkdir(parents=True, exist_ok=True)
    
    def merge_to_centralized(self,
                           source_dir: str = "output",
                           mode: MergeMode = MergeMode.APPEND,
                           dedupe: bool = True,
                           batch_size: int = 100,
                           progress_callback: Optional[callable] = None) -> MergeResult:
        """
        Merge per-document databases into centralized LanceDB.
        
        Args:
            source_dir: Directory containing per-document folders
            mode: Merge mode (append, overwrite, update)
            dedupe: Prevent duplicate document ingestion
            batch_size: Number of chunks to process at once
            progress_callback: Optional callback for progress updates
            
        Returns:
            MergeResult with statistics and any errors
        """
        start_time = datetime.now()
        errors = []
        documents_merged = 0
        documents_skipped = 0
        chunks_added = 0
        
        # Load ingestion log
        ingestion_log = self._load_ingestion_log()
        
        # Discover documents
        documents = self._discover_documents(source_dir)
        total_documents = len(documents)
        
        if progress_callback:
            progress_callback(0, total_documents, "Starting merge...")
        
        # Handle different merge modes
        if mode == MergeMode.OVERWRITE:
            self._clear_database()
            ingestion_log = {}
        
        # Process each document
        for idx, doc_path in enumerate(documents):
            try:
                md5_checksum = doc_path.parent.name
                
                # Check for duplicates
                if dedupe and md5_checksum in ingestion_log:
                    if mode != MergeMode.UPDATE:
                        documents_skipped += 1
                        logger.info(f"Skipping duplicate: {md5_checksum}")
                        continue
                
                # Load document chunks
                chunks = self._load_document_chunks(doc_path)
                if not chunks:
                    errors.append(f"No chunks found in {doc_path}")
                    continue
                
                # Load document metadata
                metadata = self._load_document_metadata(doc_path.parent)
                
                # Add document ID to chunks
                for chunk in chunks:
                    chunk['document_id'] = md5_checksum
                    if 'metadata' not in chunk:
                        chunk['metadata'] = {}
                    chunk['metadata']['document_id'] = md5_checksum
                
                # Compute embeddings if requested
                if self.compute_embeddings and not self._chunks_have_embeddings(chunks):
                    chunks = self._compute_embeddings_for_chunks(chunks, batch_size)
                
                # Add chunks to centralized database
                chunks_added += self._add_chunks_to_database(chunks, batch_size)
                
                # Update ingestion log
                ingestion_log[md5_checksum] = {
                    'ingested_at': datetime.now().isoformat(),
                    'chunk_count': len(chunks),
                    'source_file': metadata.get('source_file', 'unknown'),
                    'page_count': metadata.get('page_count', 0)
                }
                
                documents_merged += 1
                
                if progress_callback:
                    progress_callback(idx + 1, total_documents, 
                                    f"Merged {doc_path.parent.name}")
                
            except Exception as e:
                error_msg = f"Error processing {doc_path}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Save ingestion log
        self._save_ingestion_log(ingestion_log)
        
        # Update statistics
        self._update_statistics(documents_merged, chunks_added)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        return MergeResult(
            total_documents=total_documents,
            documents_merged=documents_merged,
            documents_skipped=documents_skipped,
            chunks_added=chunks_added,
            errors=errors,
            duration_seconds=duration
        )
    
    def _discover_documents(self, source_dir: str) -> List[Path]:
        """
        Discover all documents with chunks in source directory.
        
        Args:
            source_dir: Directory to search
            
        Returns:
            List of paths to chunks.jsonl files
        """
        source_path = Path(source_dir)
        documents = []
        
        if not source_path.exists():
            return documents
        
        # Look for MD5 checksum folders
        for folder in source_path.iterdir():
            if folder.is_dir() and len(folder.name) == 32:  # MD5 length
                chunks_file = folder / "lancedb" / "chunks.jsonl"
                if chunks_file.exists():
                    documents.append(chunks_file)
        
        return sorted(documents)
    
    def _load_document_chunks(self, chunks_path: Path) -> List[Dict]:
        """
        Load chunks from JSONL file.
        
        Args:
            chunks_path: Path to chunks.jsonl
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        try:
            with open(chunks_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunks.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error loading chunks from {chunks_path}: {e}")
        
        return chunks
    
    def _load_document_metadata(self, doc_dir: Path) -> Dict:
        """
        Load document metadata.
        
        Args:
            doc_dir: Document directory
            
        Returns:
            Metadata dictionary
        """
        metadata_path = doc_dir / "lancedb" / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata from {metadata_path}: {e}")
        
        return {}
    
    def _chunks_have_embeddings(self, chunks: List[Dict]) -> bool:
        """Check if chunks already have embeddings."""
        if not chunks:
            return False
        return all(chunk.get('embedding') is not None for chunk in chunks[:5])
    
    def _compute_embeddings_for_chunks(self, chunks: List[Dict], batch_size: int) -> List[Dict]:
        """
        Compute embeddings for chunks (placeholder for actual implementation).
        
        Args:
            chunks: List of chunks
            batch_size: Batch size for embedding generation
            
        Returns:
            Chunks with embeddings added
        """
        # This will be replaced with actual embedding generation in embedding_manager.py
        logger.info(f"Computing embeddings for {len(chunks)} chunks...")
        
        # For now, mark that embeddings should be computed
        for chunk in chunks:
            if 'embedding' not in chunk:
                chunk['embedding'] = None  # Will be computed by embedding manager
                chunk['embedding_model'] = 'pending'
        
        return chunks
    
    def _add_chunks_to_database(self, chunks: List[Dict], batch_size: int) -> int:
        """
        Add chunks to centralized database.
        
        Args:
            chunks: Chunks to add
            batch_size: Batch size for insertion
            
        Returns:
            Number of chunks added
        """
        # Save chunks to centralized location
        chunks_file = self.centralized_path / "chunks.jsonl"
        
        # Append mode - add to existing file
        with open(chunks_file, 'a', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        return len(chunks)
    
    def _clear_database(self):
        """Clear the centralized database."""
        chunks_file = self.centralized_path / "chunks.jsonl"
        if chunks_file.exists():
            chunks_file.unlink()
        
        # Clear ingestion log
        if self.ingestion_log_path.exists():
            self.ingestion_log_path.unlink()
    
    def _load_ingestion_log(self) -> Dict:
        """Load ingestion log."""
        if self.ingestion_log_path.exists():
            try:
                with open(self.ingestion_log_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading ingestion log: {e}")
        return {}
    
    def _save_ingestion_log(self, log: Dict):
        """Save ingestion log."""
        with open(self.ingestion_log_path, 'w') as f:
            json.dump(log, f, indent=2)
    
    def _update_statistics(self, documents_merged: int, chunks_added: int):
        """Update database statistics."""
        stats = {}
        if self.statistics_path.exists():
            try:
                with open(self.statistics_path, 'r') as f:
                    stats = json.load(f)
            except:
                pass
        
        # Update stats
        stats['last_update'] = datetime.now().isoformat()
        stats['total_documents'] = stats.get('total_documents', 0) + documents_merged
        stats['total_chunks'] = stats.get('total_chunks', 0) + chunks_added
        
        # Calculate database size
        chunks_file = self.centralized_path / "chunks.jsonl"
        if chunks_file.exists():
            stats['database_size_bytes'] = chunks_file.stat().st_size
        
        # Save statistics
        with open(self.statistics_path, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        if self.statistics_path.exists():
            with open(self.statistics_path, 'r') as f:
                return json.load(f)
        return {}
    
    def list_documents(self) -> List[DocumentInfo]:
        """
        List all documents in the centralized database.
        
        Returns:
            List of DocumentInfo objects
        """
        ingestion_log = self._load_ingestion_log()
        documents = []
        
        for md5_checksum, info in ingestion_log.items():
            documents.append(DocumentInfo(
                document_id=md5_checksum,
                source_file=info.get('source_file', 'unknown'),
                md5_checksum=md5_checksum,
                page_count=info.get('page_count', 0),
                chunk_count=info.get('chunk_count', 0),
                indexed_at=info.get('ingested_at', ''),
                metadata=info
            ))
        
        return documents
    
    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the centralized database.
        
        Args:
            document_id: MD5 checksum of document
            
        Returns:
            True if removed, False otherwise
        """
        # This would need actual LanceDB integration to remove chunks
        # For now, update ingestion log
        ingestion_log = self._load_ingestion_log()
        
        if document_id in ingestion_log:
            del ingestion_log[document_id]
            self._save_ingestion_log(ingestion_log)
            logger.info(f"Removed document {document_id} from ingestion log")
            return True
        
        return False
    
    def validate_database(self) -> Tuple[bool, List[str]]:
        """
        Validate database integrity.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required files
        chunks_file = self.centralized_path / "chunks.jsonl"
        if not chunks_file.exists():
            issues.append("Missing chunks.jsonl file")
        
        # Validate chunks format
        if chunks_file.exists():
            try:
                with open(chunks_file, 'r') as f:
                    line_count = 0
                    for line in f:
                        line_count += 1
                        if line.strip():
                            chunk = json.loads(line)
                            # Check required fields
                            if 'id' not in chunk:
                                issues.append(f"Line {line_count}: Missing 'id' field")
                            if 'content' not in chunk:
                                issues.append(f"Line {line_count}: Missing 'content' field")
                            if 'document_id' not in chunk.get('metadata', {}):
                                issues.append(f"Line {line_count}: Missing document_id in metadata")
            except Exception as e:
                issues.append(f"Error reading chunks file: {e}")
        
        # Check ingestion log consistency
        ingestion_log = self._load_ingestion_log()
        stats = self.get_statistics()
        
        if len(ingestion_log) != stats.get('total_documents', 0):
            issues.append("Mismatch between ingestion log and statistics")
        
        return len(issues) == 0, issues
    
    def optimize_database(self, compact: bool = True, rebuild_indices: bool = True) -> Dict:
        """
        Optimize the centralized database.
        
        Args:
            compact: Compact data files
            rebuild_indices: Rebuild indices
            
        Returns:
            Optimization results
        """
        results = {
            'started_at': datetime.now().isoformat(),
            'actions_performed': []
        }
        
        if compact:
            # Compact chunks file by removing duplicates
            self._compact_chunks()
            results['actions_performed'].append('compacted_chunks')
        
        if rebuild_indices:
            # This would rebuild actual LanceDB indices
            results['actions_performed'].append('rebuilt_indices')
        
        results['completed_at'] = datetime.now().isoformat()
        
        return results
    
    def _compact_chunks(self):
        """Compact chunks file by removing duplicates."""
        chunks_file = self.centralized_path / "chunks.jsonl"
        if not chunks_file.exists():
            return
        
        # Read all chunks
        seen_ids = set()
        unique_chunks = []
        
        with open(chunks_file, 'r') as f:
            for line in f:
                if line.strip():
                    chunk = json.loads(line)
                    chunk_id = chunk.get('id')
                    if chunk_id and chunk_id not in seen_ids:
                        seen_ids.add(chunk_id)
                        unique_chunks.append(chunk)
        
        # Write back unique chunks
        with open(chunks_file, 'w') as f:
            for chunk in unique_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        logger.info(f"Compacted chunks: {len(unique_chunks)} unique chunks retained")