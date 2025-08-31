"""
Factory module for creating vector database clients
"""
from typing import Union
from ..config import VectorDBConfig
from .milvus_client import MilvusVectorDB
import logging

logger = logging.getLogger(__name__)


def create_vector_db(config: VectorDBConfig) -> MilvusVectorDB:
    """
    Factory function to create Milvus vector database client.
    
    In v0.1.15, Milvus is the default and only option.
    
    Args:
        config: Vector database configuration
        
    Returns:
        MilvusVectorDB instance
    """
    
    # Milvus is the default and only option in v0.1.15
    logger.info(f"Creating Milvus vector database client")
    logger.info(f"Host: {config.milvus_host}:{config.milvus_port}")
    logger.info(f"Collection: {config.milvus_collection}")
    logger.info(f"Deployment: {config.milvus_deployment}")
    logger.info(f"Index type: {config.index_type}")
    
    return MilvusVectorDB(
        host=config.milvus_host,
        port=config.milvus_port,
        collection_name=config.milvus_collection,
        deployment_type=config.milvus_deployment
    )