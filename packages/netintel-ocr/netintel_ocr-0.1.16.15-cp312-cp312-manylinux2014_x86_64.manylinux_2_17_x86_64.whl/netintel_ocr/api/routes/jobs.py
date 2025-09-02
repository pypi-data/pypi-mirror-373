"""
Job Management Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.jobs import (
    JobResponse,
    JobStatus,
    JobCreate,
    JobMetrics
)
from ..services.job_service import JobService
from ..services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> JobResponse:
    """Create a new processing job"""
    job_response = await job_service.create_job(
        document_id=job.document_id,
        job_type=job.job_type,
        priority=job.priority,
        user_id=user.get("id")
    )
    
    # Queue job for processing
    background_tasks.add_task(
        job_service.queue_job,
        job_id=job_response.job_id
    )
    
    return job_response

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> JobResponse:
    """Get job details by ID"""
    job = await job_service.get_job(job_id, user.get("id"))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.get("/{job_id}/status")
async def get_job_status(
    job_id: str,
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> Dict[str, Any]:
    """Get current status of a job"""
    status = await job_service.get_job_status(job_id, user.get("id"))
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status

@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> Dict[str, str]:
    """Cancel a running or queued job"""
    success = await job_service.cancel_job(job_id, user.get("id"))
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
    
    return {"message": "Job cancelled successfully"}

@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> JobResponse:
    """Retry a failed job"""
    job = await job_service.retry_job(job_id, user.get("id"))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or cannot be retried")
    
    # Queue job for processing
    background_tasks.add_task(
        job_service.queue_job,
        job_id=job.job_id
    )
    
    return job

@router.get("/")
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[JobStatus] = None,
    document_id: Optional[str] = None,
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> Dict[str, Any]:
    """List all jobs with pagination and filters"""
    jobs = await job_service.list_jobs(
        user_id=user.get("id"),
        skip=skip,
        limit=limit,
        status=status,
        document_id=document_id
    )
    
    return {
        "jobs": jobs,
        "total": len(jobs),
        "skip": skip,
        "limit": limit
    }

@router.get("/queue/status")
async def get_queue_status(
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> Dict[str, Any]:
    """Get current queue status and statistics"""
    stats = await job_service.get_queue_stats()
    
    return {
        "queue": stats,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics", response_model=JobMetrics)
async def get_job_metrics(
    time_range: str = Query("1h", description="Time range: 1h, 24h, 7d"),
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> JobMetrics:
    """Get job processing metrics"""
    metrics = await job_service.get_metrics(time_range, user.get("id"))
    return metrics

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> Dict[str, str]:
    """Delete a job record"""
    success = await job_service.delete_job(job_id, user.get("id"))
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}

@router.get("/batch/{batch_id}")
async def get_batch_jobs(
    batch_id: str,
    user: Dict = Depends(get_current_user),
    job_service: JobService = Depends()
) -> Dict[str, Any]:
    """Get all jobs in a batch"""
    jobs = await job_service.get_batch_jobs(batch_id, user.get("id"))
    
    return {
        "batch_id": batch_id,
        "jobs": jobs,
        "total": len(jobs),
        "status": {
            "completed": sum(1 for j in jobs if j["status"] == JobStatus.COMPLETED),
            "failed": sum(1 for j in jobs if j["status"] == JobStatus.FAILED),
            "processing": sum(1 for j in jobs if j["status"] == JobStatus.PROCESSING),
            "queued": sum(1 for j in jobs if j["status"] == JobStatus.QUEUED)
        }
    }