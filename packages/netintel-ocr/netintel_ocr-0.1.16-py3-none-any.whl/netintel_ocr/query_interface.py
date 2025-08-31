"""
Query Interface for NetIntel-OCR v0.1.11
Provides search capabilities for vector databases (foundation for future implementation).
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import os


class QueryInterface:
    """Query interface for searching vector databases."""
    
    def __init__(self, lancedb_path: Optional[str] = None, lancedb_uri: Optional[str] = None):
        """
        Initialize query interface.
        
        Args:
            lancedb_path: Local path to LanceDB
            lancedb_uri: Remote URI for LanceDB (S3/MinIO)
        """
        self.lancedb_path = lancedb_path
        self.lancedb_uri = lancedb_uri
        self.results = []
    
    def query(self, 
              query_text: str,
              limit: int = 10,
              similarity_threshold: float = 0.7,
              filter_dict: Optional[Dict[str, Any]] = None,
              output_format: str = "json") -> Any:
        """
        Query the vector database.
        
        Args:
            query_text: Search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            filter_dict: Additional filters
            output_format: Output format (json, markdown, csv)
            
        Returns:
            Query results in specified format
        """
        # This is a foundation implementation
        # Full implementation will be added in future versions
        print(f"🔍 Query interface initialized (foundation mode)")
        print(f"   Query: {query_text}")
        print(f"   Database: {self.lancedb_path or self.lancedb_uri}")
        print(f"   Note: Full query functionality coming in v0.1.12")
        
        # Return sample structure for now
        sample_result = {
            "query": query_text,
            "status": "foundation",
            "message": "Query interface foundation ready. Full implementation coming in v0.1.12",
            "database": self.lancedb_path or self.lancedb_uri,
            "limit": limit,
            "similarity_threshold": similarity_threshold
        }
        
        if output_format == "markdown":
            return self._format_markdown(sample_result)
        elif output_format == "csv":
            return self._format_csv(sample_result)
        else:
            return sample_result
    
    def _format_markdown(self, results: Dict) -> str:
        """Format results as markdown."""
        md = f"# Query Results\n\n"
        md += f"**Query**: {results['query']}\n"
        md += f"**Status**: {results['status']}\n"
        md += f"**Message**: {results['message']}\n"
        return md
    
    def _format_csv(self, results: Dict) -> str:
        """Format results as CSV."""
        return f"query,status,message\n\"{results['query']}\",\"{results['status']}\",\"{results['message']}\""
    
    def list_documents(self, lancedb_path: Optional[str] = None) -> List[Dict]:
        """
        List all documents in the database.
        
        Args:
            lancedb_path: Path to LanceDB
            
        Returns:
            List of document metadata
        """
        db_path = lancedb_path or self.lancedb_path
        if not db_path:
            return []
        
        documents = []
        base_path = Path(db_path).parent if "lancedb" in str(db_path) else Path(db_path)
        
        # Look for document folders (MD5 checksums)
        for folder in base_path.iterdir():
            if folder.is_dir() and len(folder.name) == 32:  # MD5 checksum length
                metadata_file = folder / "lancedb" / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        documents.append(metadata)
        
        return documents
    
    def validate_database(self, lancedb_path: Optional[str] = None) -> tuple[bool, List[str]]:
        """
        Validate database integrity.
        
        Args:
            lancedb_path: Path to LanceDB
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        db_path = lancedb_path or self.lancedb_path
        issues = []
        
        if not db_path:
            return False, ["No database path specified"]
        
        db_path = Path(db_path)
        
        # Check for required files
        required_files = ["chunks.jsonl", "metadata.json", "schema.json"]
        for file_name in required_files:
            file_path = db_path / file_name if "lancedb" in str(db_path) else db_path / "lancedb" / file_name
            if not file_path.exists():
                issues.append(f"Missing required file: {file_name}")
        
        return len(issues) == 0, issues


class CentralizedDatabaseManager:
    """Manager for centralized LanceDB operations (foundation for v0.1.12)."""
    
    def __init__(self, centralized_path: str = "output/lancedb"):
        """
        Initialize centralized database manager.
        
        Args:
            centralized_path: Path to centralized database
        """
        self.centralized_path = Path(centralized_path)
        self.ingestion_log_path = self.centralized_path / "ingestion_log.json"
    
    def merge_to_centralized(self, source_dir: str = "output") -> int:
        """
        Merge per-document databases into centralized database.
        
        Args:
            source_dir: Directory containing per-document folders
            
        Returns:
            Number of documents merged
        """
        print("🔄 Centralized database merger (foundation mode)")
        print(f"   Source: {source_dir}")
        print(f"   Target: {self.centralized_path}")
        print(f"   Note: Full merge functionality coming in v0.1.12")
        
        # Count potential documents to merge
        source_path = Path(source_dir)
        doc_count = 0
        
        if not source_path.exists():
            print(f"   Source directory '{source_dir}' does not exist")
            return 0
        
        for folder in source_path.iterdir():
            if folder.is_dir() and len(folder.name) == 32:  # MD5 checksum
                chunks_file = folder / "lancedb" / "chunks.jsonl"
                if chunks_file.exists():
                    doc_count += 1
        
        print(f"   Found {doc_count} documents ready for merging")
        return doc_count
    
    def get_ingestion_log(self) -> Dict[str, Any]:
        """
        Get ingestion log for tracking merged documents.
        
        Returns:
            Ingestion log dictionary
        """
        if self.ingestion_log_path.exists():
            with open(self.ingestion_log_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_ingestion_log(self, log: Dict[str, Any]):
        """
        Save ingestion log.
        
        Args:
            log: Ingestion log to save
        """
        self.centralized_path.mkdir(parents=True, exist_ok=True)
        with open(self.ingestion_log_path, 'w') as f:
            json.dump(log, f, indent=2)
    
    def is_document_ingested(self, md5_checksum: str) -> bool:
        """
        Check if document has been ingested.
        
        Args:
            md5_checksum: MD5 checksum of document
            
        Returns:
            True if document already ingested
        """
        log = self.get_ingestion_log()
        return md5_checksum in log