"""
Milvus schema with deduplication support for NetIntel-OCR v0.1.15
"""
from pymilvus import (
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
import logging

logger = logging.getLogger(__name__)


def create_dedup_collection(collection_name: str = "netintel_dedup") -> Collection:
    """Create Milvus collection with deduplication support"""
    
    # Check if collection already exists
    if utility.has_collection(collection_name):
        logger.info(f"Collection {collection_name} already exists, loading it")
        collection = Collection(collection_name)
        collection.load()
        return collection
    
    fields = [
        # Primary identifiers
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=256),
        
        # Deduplication fields
        FieldSchema(name="md5_checksum", dtype=DataType.VARCHAR, max_length=32),
        FieldSchema(name="simhash_64", dtype=DataType.BINARY_VECTOR, dim=64),
        FieldSchema(name="simhash_hex", dtype=DataType.VARCHAR, max_length=16),
        
        # Content and embeddings
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="content_embedding", dtype=DataType.FLOAT_VECTOR, dim=4096),  # qwen3-embedding:8b
        FieldSchema(name="cdc_chunks", dtype=DataType.JSON),  # Array of CDC chunks
        
        # Deduplication metrics
        FieldSchema(name="is_duplicate", dtype=DataType.BOOL),
        FieldSchema(name="duplicate_of", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="cdc_reduction_percent", dtype=DataType.FLOAT),
        FieldSchema(name="original_size", dtype=DataType.INT64),
        FieldSchema(name="deduped_size", dtype=DataType.INT64),
        
        # Metadata
        FieldSchema(name="page_number", dtype=DataType.INT64),
        FieldSchema(name="processing_time_ms", dtype=DataType.FLOAT),
        FieldSchema(name="metadata", dtype=DataType.JSON)
    ]
    
    schema = CollectionSchema(fields=fields, description="NetIntel-OCR with deduplication")
    
    collection = Collection(name=collection_name, schema=schema)
    
    # Create optimized indexes
    # Binary index for SimHash (Hamming distance)
    collection.create_index(
        field_name="simhash_64",
        index_params={
            "index_type": "BIN_IVF_FLAT",
            "metric_type": "HAMMING",
            "params": {"nlist": 1024}
        }
    )
    
    # Vector index for semantic search (CPU-optimized IVF_SQ8)
    collection.create_index(
        field_name="content_embedding",
        index_params={
            "index_type": "IVF_SQ8",
            "metric_type": "COSINE",
            "params": {"nlist": 1024}
        }
    )
    
    # Scalar indexes for fast filtering
    collection.create_index(field_name="md5_checksum")
    collection.create_index(field_name="document_id")
    collection.create_index(field_name="is_duplicate")
    
    collection.load()
    logger.info(f"Created deduplication collection: {collection_name}")
    
    return collection


def get_dedup_statistics(collection: Collection) -> dict:
    """Get comprehensive deduplication statistics from Milvus"""
    
    # Total documents
    total_docs = collection.num_entities
    
    # Exact duplicates
    exact_dups = collection.query(
        expr="is_duplicate == true",
        output_fields=["document_id"],
        consistency_level="Strong"
    )
    
    # Average reduction
    avg_reduction = collection.query(
        expr="cdc_reduction_percent > 0",
        output_fields=["cdc_reduction_percent"]
    )
    
    avg_reduction_pct = 0
    if avg_reduction:
        import numpy as np
        avg_reduction_pct = np.mean([r["cdc_reduction_percent"] for r in avg_reduction])
    
    # Storage savings
    original_sizes = collection.query(
        expr="original_size > 0",
        output_fields=["original_size", "deduped_size"]
    )
    
    total_original = sum(r["original_size"] for r in original_sizes) if original_sizes else 0
    total_deduped = sum(r["deduped_size"] for r in original_sizes) if original_sizes else 0
    
    return {
        "total_documents": total_docs,
        "exact_duplicates": len(exact_dups),
        "average_reduction_percent": avg_reduction_pct,
        "total_original_size_gb": total_original / (1024**3),
        "total_deduped_size_gb": total_deduped / (1024**3),
        "storage_saved_gb": (total_original - total_deduped) / (1024**3) if total_original > 0 else 0,
        "deduplication_ratio": total_original / total_deduped if total_deduped > 0 else 1
    }