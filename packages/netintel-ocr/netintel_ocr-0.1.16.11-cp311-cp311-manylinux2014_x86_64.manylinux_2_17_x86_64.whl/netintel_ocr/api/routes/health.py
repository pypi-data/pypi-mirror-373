"""
Health Check Routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import psutil
import os
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.13"
    }

@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes"""
    try:
        from ..services.database import check_database_connection
        from ..services.storage import check_storage_connection
        from ..services.queue import check_queue_connection
        
        db_status = await check_database_connection()
        storage_status = await check_storage_connection()
        queue_status = await check_queue_connection()
        
        if not all([db_status, storage_status, queue_status]):
            raise HTTPException(status_code=503, detail="Service not ready")
        
        return {
            "status": "ready",
            "database": db_status,
            "storage": storage_status,
            "queue": queue_status
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes"""
    return {"status": "alive"}

@router.get("/health/metrics")
async def metrics() -> Dict[str, Any]:
    """System metrics endpoint"""
    process = psutil.Process(os.getpid())
    
    return {
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "process": {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "threads": process.num_threads()
        }
    }