"""
Database Models
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class DatabaseInfo(BaseModel):
    name: str
    version: str
    size_mb: float
    document_count: int
    collection_count: int
    index_count: int
    created_at: datetime
    last_backup: Optional[datetime] = None

class CollectionStats(BaseModel):
    name: str
    document_count: int
    size_mb: float
    indexes: int
    last_modified: datetime
    metadata: Dict[str, Any] = {}

class IndexInfo(BaseModel):
    name: str
    collection: str
    field: str
    type: str
    size_mb: float
    created_at: datetime
    is_unique: bool = False
    is_sparse: bool = False