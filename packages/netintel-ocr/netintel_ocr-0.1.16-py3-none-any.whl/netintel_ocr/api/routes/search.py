"""
Search and Query Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.search import (
    VectorSearchRequest,
    SemanticSearchRequest,
    SearchResponse,
    SearchResult
)
from ..services.search_service import SearchService
from ..services.auth import get_current_user

router = APIRouter()

@router.post("/vector", response_model=SearchResponse)
async def vector_search(
    request: VectorSearchRequest,
    user: Dict = Depends(get_current_user),
    search_service: SearchService = Depends()
) -> SearchResponse:
    """Perform vector similarity search across documents"""
    results = await search_service.vector_search(
        query=request.query,
        limit=request.limit,
        threshold=request.threshold,
        document_ids=request.document_ids,
        user_id=user.get("id")
    )
    
    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
        search_type="vector"
    )

@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    user: Dict = Depends(get_current_user),
    search_service: SearchService = Depends()
) -> SearchResponse:
    """Perform semantic search with natural language understanding"""
    results = await search_service.semantic_search(
        query=request.query,
        limit=request.limit,
        filters=request.filters,
        user_id=user.get("id")
    )
    
    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
        search_type="semantic"
    )

@router.get("/keywords")
async def keyword_search(
    q: str = Query(..., description="Search keywords"),
    limit: int = Query(10, ge=1, le=100),
    document_ids: Optional[List[str]] = Query(None),
    user: Dict = Depends(get_current_user),
    search_service: SearchService = Depends()
) -> Dict[str, Any]:
    """Perform keyword-based search"""
    results = await search_service.keyword_search(
        keywords=q,
        limit=limit,
        document_ids=document_ids,
        user_id=user.get("id")
    )
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

@router.get("/diagrams")
async def search_diagrams(
    q: Optional[str] = Query(None, description="Search query"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    limit: int = Query(10, ge=1, le=100),
    user: Dict = Depends(get_current_user),
    search_service: SearchService = Depends()
) -> Dict[str, Any]:
    """Search network diagrams"""
    results = await search_service.search_diagrams(
        query=q,
        device_type=device_type,
        limit=limit,
        user_id=user.get("id")
    )
    
    return {
        "query": q,
        "device_type": device_type,
        "results": results,
        "total": len(results)
    }

@router.get("/tables")
async def search_tables(
    q: Optional[str] = Query(None, description="Search query"),
    column_name: Optional[str] = Query(None, description="Filter by column name"),
    limit: int = Query(10, ge=1, le=100),
    user: Dict = Depends(get_current_user),
    search_service: SearchService = Depends()
) -> Dict[str, Any]:
    """Search extracted tables"""
    results = await search_service.search_tables(
        query=q,
        column_name=column_name,
        limit=limit,
        user_id=user.get("id")
    )
    
    return {
        "query": q,
        "column_name": column_name,
        "results": results,
        "total": len(results)
    }

@router.post("/hybrid")
async def hybrid_search(
    query: str,
    search_types: List[str] = Query(["vector", "keyword"], description="Types of search to combine"),
    limit: int = Query(10, ge=1, le=100),
    user: Dict = Depends(get_current_user),
    search_service: SearchService = Depends()
) -> Dict[str, Any]:
    """Perform hybrid search combining multiple search strategies"""
    if not all(st in ["vector", "keyword", "semantic"] for st in search_types):
        raise HTTPException(status_code=400, detail="Invalid search type")
    
    results = await search_service.hybrid_search(
        query=query,
        search_types=search_types,
        limit=limit,
        user_id=user.get("id")
    )
    
    return {
        "query": query,
        "search_types": search_types,
        "results": results,
        "total": len(results)
    }

@router.get("/suggest")
async def search_suggestions(
    q: str = Query(..., min_length=2, description="Query prefix"),
    limit: int = Query(5, ge=1, le=20),
    user: Dict = Depends(get_current_user),
    search_service: SearchService = Depends()
) -> Dict[str, Any]:
    """Get search suggestions based on query prefix"""
    suggestions = await search_service.get_suggestions(
        prefix=q,
        limit=limit,
        user_id=user.get("id")
    )
    
    return {
        "query": q,
        "suggestions": suggestions
    }