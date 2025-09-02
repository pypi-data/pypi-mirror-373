"""
Milvus vector database client for NetIntel-OCR v0.1.15
"""
from typing import List, Dict, Any, Optional
import numpy as np
from pymilvus import (
    connections,
    utility,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    MilvusClient
)
import logging

logger = logging.getLogger(__name__)


class MilvusVectorDB:
    """Milvus vector database client for NetIntel-OCR"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 19530,
        collection_name: str = "netintel_vectors",
        dim: int = 4096,  # qwen3-embedding:8b dimension
        deployment_type: str = "standalone"
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dim = dim
        self.deployment_type = deployment_type
        self.collection = None
        
        # Connect to Milvus
        self._connect()
        
        # Initialize collection
        self._init_collection()
    
    def _connect(self):
        """Establish connection to Milvus"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
                timeout=30
            )
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def _init_collection(self):
        """Initialize or load collection"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            self.collection.load()
            logger.info(f"Loaded existing collection: {self.collection_name}")
        else:
            self._create_collection()
    
    def _create_collection(self):
        """Create new collection with schema"""
        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True
            ),
            FieldSchema(
                name="document_id",
                dtype=DataType.VARCHAR,
                max_length=256
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.INT64
            ),
            FieldSchema(
                name="content_type",
                dtype=DataType.VARCHAR,
                max_length=64
            ),
            FieldSchema(
                name="content",
                dtype=DataType.VARCHAR,
                max_length=65535
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.dim
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON
            )
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="NetIntel-OCR vector embeddings"
        )
        
        self.collection = Collection(
            name=self.collection_name,
            schema=schema,
            consistency_level="Strong"
        )
        
        # Create indexes based on deployment type
        if self.deployment_type == "standalone":
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_SQ8",
                "params": {"nlist": 1024}
            }
        else:  # distributed/production
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_SQ8",
                "params": {"nlist": 4096}
            }
        
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        # Create scalar indexes
        self.collection.create_index(
            field_name="document_id",
            index_params={}
        )
        
        self.collection.create_index(
            field_name="content_type",
            index_params={}
        )
        
        self.collection.load()
        logger.info(f"Created new collection: {self.collection_name}")
    
    def insert(
        self,
        embeddings: List[np.ndarray],
        documents: List[Dict[str, Any]]
    ) -> List[int]:
        """Insert vectors and metadata into collection"""
        data = []
        for embedding, doc in zip(embeddings, documents):
            data.append({
                "document_id": doc.get("document_id", ""),
                "page_number": doc.get("page_number", 0),
                "content_type": doc.get("content_type", "text"),
                "content": doc.get("content", ""),
                "embedding": embedding.tolist(),
                "metadata": doc.get("metadata", {})
            })
        
        result = self.collection.insert(data)
        self.collection.flush()
        
        logger.info(f"Inserted {len(data)} vectors")
        return result.primary_keys
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        results = self.collection.search(
            data=[query_vector.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filters,
            output_fields=[
                "document_id",
                "page_number",
                "content_type",
                "content",
                "metadata"
            ]
        )
        
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "document_id": hit.entity.get("document_id"),
                    "page_number": hit.entity.get("page_number"),
                    "content_type": hit.entity.get("content_type"),
                    "content": hit.entity.get("content"),
                    "metadata": hit.entity.get("metadata")
                })
        
        return formatted_results
    
    def delete(self, document_id: str):
        """Delete vectors by document ID"""
        expr = f'document_id == "{document_id}"'
        self.collection.delete(expr)
        logger.info(f"Deleted vectors for document: {document_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        stats = {
            "collection_name": self.collection_name,
            "num_entities": self.collection.num_entities,
            "deployment_type": self.deployment_type,
            "indexes": []
        }
        
        for field in self.collection.schema.fields:
            if field.name == "embedding":
                index = self.collection.index(field_name=field.name)
                stats["indexes"].append({
                    "field": field.name,
                    "index_type": index.params.get("index_type"),
                    "metric_type": index.params.get("metric_type")
                })
        
        return stats