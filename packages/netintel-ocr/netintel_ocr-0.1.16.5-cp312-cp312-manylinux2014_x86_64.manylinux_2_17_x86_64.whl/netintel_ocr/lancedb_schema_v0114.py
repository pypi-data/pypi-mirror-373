"""
NetIntel-OCR v0.1.14 LanceDB Schema Extensions
Adds deduplication metadata fields to document schema
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DeduplicationMetadata(BaseModel):
    """Deduplication metadata for documents."""
    md5_checksum: Optional[str] = Field(None, description="MD5 hash of document content")
    simhash: Optional[str] = Field(None, description="SimHash fingerprint (hex string)")
    simhash_bits: Optional[int] = Field(64, description="SimHash fingerprint size (64 or 128 bits)")
    hamming_neighbors: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Similar documents by Hamming distance")
    cdc_reduction_percent: Optional[float] = Field(0.0, description="CDC deduplication reduction percentage")
    is_duplicate: bool = Field(False, description="Whether this document is a duplicate")
    duplicate_of: Optional[str] = Field(None, description="Document ID of the original if this is a duplicate")
    similarity_score: Optional[float] = Field(None, description="Similarity score to original document (0-1)")


class DocumentChunkV0114(BaseModel):
    """Extended document chunk schema for v0.1.14 with deduplication."""
    # Core fields from original schema
    document_id: str = Field(description="Unique document identifier (MD5 hash)")
    source_file: str = Field(description="Original PDF filename")
    chunk_id: str = Field(description="Unique chunk identifier")
    page_number: int = Field(description="Page number in original PDF")
    chunk_index: int = Field(description="Sequential index of chunk within document")
    
    # Content fields
    content: str = Field(description="Chunk text content")
    content_type: str = Field(default="text", description="Type of content: text, diagram, table, mixed")
    
    # Metadata fields
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    # Deduplication fields (v0.1.14)
    dedup_metadata: Optional[DeduplicationMetadata] = Field(None, description="Deduplication metadata")
    
    # Vector fields (optional, for when embeddings are computed)
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of content")
    embedding_model: Optional[str] = Field(None, description="Model used for embedding generation")


class NetworkDiagramV0114(BaseModel):
    """Extended network diagram schema for v0.1.14."""
    document_id: str = Field(description="Document identifier")
    page_number: int = Field(description="Page number")
    diagram_index: int = Field(description="Index of diagram on page")
    
    # Diagram content
    mermaid_code: str = Field(description="Mermaid.js diagram code")
    diagram_type: str = Field(description="Type of network diagram")
    components: List[Dict[str, Any]] = Field(default_factory=list, description="Diagram components")
    
    # Deduplication for diagrams (v0.1.14)
    diagram_hash: Optional[str] = Field(None, description="Hash of diagram structure")
    is_duplicate_diagram: bool = Field(False, description="Whether this diagram is a duplicate")
    duplicate_diagram_of: Optional[str] = Field(None, description="Original diagram ID if duplicate")


class TableV0114(BaseModel):
    """Extended table schema for v0.1.14."""
    document_id: str = Field(description="Document identifier")
    page_number: int = Field(description="Page number")
    table_index: int = Field(description="Index of table on page")
    
    # Table content
    headers: List[str] = Field(description="Table headers")
    rows: List[List[Any]] = Field(description="Table rows")
    table_format: str = Field(default="markdown", description="Format of table representation")
    
    # Deduplication for tables (v0.1.14)
    table_hash: Optional[str] = Field(None, description="Hash of table content")
    is_duplicate_table: bool = Field(False, description="Whether this table is a duplicate")
    duplicate_table_of: Optional[str] = Field(None, description="Original table ID if duplicate")


class DocumentMetadataV0114(BaseModel):
    """Complete document metadata for v0.1.14."""
    document_id: str = Field(description="Unique document identifier")
    source_file: str = Field(description="Original PDF filename")
    file_size_bytes: int = Field(description="File size in bytes")
    page_count: int = Field(description="Total number of pages")
    
    # Processing metadata
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_seconds: float = Field(description="Total processing time")
    netintel_version: str = Field(default="0.1.14")
    
    # Content statistics
    total_chunks: int = Field(description="Total number of chunks")
    total_diagrams: int = Field(default=0, description="Number of network diagrams")
    total_tables: int = Field(default=0, description="Number of tables")
    
    # Deduplication statistics (v0.1.14)
    dedup_metadata: DeduplicationMetadata = Field(description="Document-level deduplication metadata")
    dedup_stats: Dict[str, Any] = Field(default_factory=dict, description="Deduplication statistics")
    
    # Deployment information (v0.1.14)
    deployment_scale: Optional[str] = Field(None, description="Deployment scale when processed")
    cpp_core_used: bool = Field(False, description="Whether C++ core was used")
    faiss_used: bool = Field(False, description="Whether Faiss was used")


def create_lancedb_schema_v0114() -> Dict[str, Any]:
    """Create LanceDB schema definition for v0.1.14."""
    return {
        "chunks": {
            "schema": DocumentChunkV0114,
            "indexes": [
                {"field": "document_id", "type": "btree"},
                {"field": "dedup_metadata.md5_checksum", "type": "hash"},
                {"field": "dedup_metadata.simhash", "type": "hash"},
                {"field": "content_type", "type": "btree"},
                {"field": "embedding", "type": "vector", "metric": "cosine"}
            ],
            "partitions": ["document_id"]
        },
        "documents": {
            "schema": DocumentMetadataV0114,
            "indexes": [
                {"field": "document_id", "type": "primary"},
                {"field": "source_file", "type": "btree"},
                {"field": "dedup_metadata.md5_checksum", "type": "unique"},
                {"field": "processed_at", "type": "btree"}
            ]
        },
        "diagrams": {
            "schema": NetworkDiagramV0114,
            "indexes": [
                {"field": "document_id", "type": "btree"},
                {"field": "diagram_hash", "type": "hash"}
            ]
        },
        "tables": {
            "schema": TableV0114,
            "indexes": [
                {"field": "document_id", "type": "btree"},
                {"field": "table_hash", "type": "hash"}
            ]
        }
    }


def migrate_schema_to_v0114(existing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate existing data to v0.1.14 schema."""
    migrated = existing_data.copy()
    
    # Add deduplication metadata if missing
    if "dedup_metadata" not in migrated:
        migrated["dedup_metadata"] = {
            "md5_checksum": None,
            "simhash": None,
            "simhash_bits": 64,
            "hamming_neighbors": [],
            "cdc_reduction_percent": 0.0,
            "is_duplicate": False,
            "duplicate_of": None,
            "similarity_score": None
        }
    
    # Add v0.1.14 specific fields
    if "netintel_version" not in migrated:
        migrated["netintel_version"] = "0.1.14"
    
    if "deployment_scale" not in migrated:
        migrated["deployment_scale"] = "unknown"
    
    if "cpp_core_used" not in migrated:
        migrated["cpp_core_used"] = False
    
    if "faiss_used" not in migrated:
        migrated["faiss_used"] = False
    
    return migrated