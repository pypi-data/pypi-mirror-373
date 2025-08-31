"""
Database Management Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.database import (
    DatabaseInfo,
    CollectionStats,
    IndexInfo
)
from ..services.database_service import DatabaseService
from ..services.auth import get_current_user, require_admin

router = APIRouter()

@router.get("/info", response_model=DatabaseInfo)
async def get_database_info(
    user: Dict = Depends(get_current_user),
    database_service: DatabaseService = Depends()
) -> DatabaseInfo:
    """Get database information and statistics"""
    info = await database_service.get_database_info()
    return info

@router.get("/collections", response_model=List[CollectionStats])
async def list_collections(
    user: Dict = Depends(get_current_user),
    database_service: DatabaseService = Depends()
) -> List[CollectionStats]:
    """List all collections with statistics"""
    collections = await database_service.list_collections()
    return collections

@router.get("/collections/{collection_name}", response_model=CollectionStats)
async def get_collection_stats(
    collection_name: str,
    user: Dict = Depends(get_current_user),
    database_service: DatabaseService = Depends()
) -> CollectionStats:
    """Get detailed statistics for a specific collection"""
    stats = await database_service.get_collection_stats(collection_name)
    if not stats:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    return stats

@router.post("/collections/{collection_name}/optimize")
async def optimize_collection(
    collection_name: str,
    user: Dict = Depends(require_admin),
    database_service: DatabaseService = Depends()
) -> Dict[str, str]:
    """Optimize a collection for better performance"""
    success = await database_service.optimize_collection(collection_name)
    if not success:
        raise HTTPException(status_code=500, detail="Optimization failed")
    
    return {"message": f"Collection {collection_name} optimized successfully"}

@router.get("/indexes", response_model=List[IndexInfo])
async def list_indexes(
    collection_name: Optional[str] = None,
    user: Dict = Depends(get_current_user),
    database_service: DatabaseService = Depends()
) -> List[IndexInfo]:
    """List all indexes or indexes for a specific collection"""
    indexes = await database_service.list_indexes(collection_name)
    return indexes

@router.post("/indexes")
async def create_index(
    collection_name: str,
    field: str,
    index_type: str = "vector",
    user: Dict = Depends(require_admin),
    database_service: DatabaseService = Depends()
) -> Dict[str, str]:
    """Create a new index on a collection"""
    success = await database_service.create_index(collection_name, field, index_type)
    if not success:
        raise HTTPException(status_code=500, detail="Index creation failed")
    
    return {"message": f"Index created on {collection_name}.{field}"}

@router.delete("/indexes/{index_name}")
async def delete_index(
    index_name: str,
    user: Dict = Depends(require_admin),
    database_service: DatabaseService = Depends()
) -> Dict[str, str]:
    """Delete an index"""
    success = await database_service.delete_index(index_name)
    if not success:
        raise HTTPException(status_code=404, detail="Index not found")
    
    return {"message": f"Index {index_name} deleted successfully"}

@router.post("/backup")
async def create_backup(
    user: Dict = Depends(require_admin),
    database_service: DatabaseService = Depends()
) -> Dict[str, Any]:
    """Create a database backup"""
    backup_info = await database_service.create_backup()
    if not backup_info:
        raise HTTPException(status_code=500, detail="Backup creation failed")
    
    return {
        "message": "Backup created successfully",
        "backup_id": backup_info["backup_id"],
        "location": backup_info["location"],
        "timestamp": backup_info["timestamp"]
    }

@router.post("/restore")
async def restore_backup(
    backup_id: str,
    user: Dict = Depends(require_admin),
    database_service: DatabaseService = Depends()
) -> Dict[str, str]:
    """Restore database from a backup"""
    success = await database_service.restore_backup(backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    return {"message": f"Database restored from backup {backup_id}"}

@router.get("/storage/stats")
async def get_storage_stats(
    user: Dict = Depends(get_current_user),
    database_service: DatabaseService = Depends()
) -> Dict[str, Any]:
    """Get storage statistics"""
    stats = await database_service.get_storage_stats()
    return stats

@router.post("/cleanup")
async def cleanup_database(
    days_old: int = Query(30, description="Delete data older than N days"),
    user: Dict = Depends(require_admin),
    database_service: DatabaseService = Depends()
) -> Dict[str, Any]:
    """Clean up old data from database"""
    result = await database_service.cleanup_old_data(days_old)
    
    return {
        "message": "Cleanup completed",
        "deleted_documents": result["documents"],
        "deleted_jobs": result["jobs"],
        "freed_space_mb": result["freed_space_mb"]
    }

@router.get("/export")
async def export_data(
    format: str = Query("json", description="Export format: json, csv, parquet"),
    collection: Optional[str] = None,
    user: Dict = Depends(require_admin),
    database_service: DatabaseService = Depends()
):
    """Export database data"""
    export_file = await database_service.export_data(format, collection)
    if not export_file:
        raise HTTPException(status_code=500, detail="Export failed")
    
    return export_file