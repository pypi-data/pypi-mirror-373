"""
Search Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class VectorSearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    document_ids: Optional[List[str]] = Field(None, description="Limit search to specific documents")

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

class SearchResult(BaseModel):
    document_id: str
    page_number: Optional[int] = None
    score: float
    text: str
    highlight: Optional[str] = None
    metadata: Dict[str, Any] = {}

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    search_type: str
    execution_time_ms: Optional[float] = None