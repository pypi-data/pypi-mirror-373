"""
Job Service - Job management and processing
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from .database import get_db
from .queue import enqueue_job, get_queue
from ..models.jobs import JobStatus, JobType, JobPriority, JobResponse, JobMetrics

class JobService:
    """Service for job management operations"""
    
    async def create_job(
        self,
        document_id: str,
        job_type: JobType,
        priority: JobPriority,
        user_id: str
    ) -> JobResponse:
        """Create a new processing job"""
        db = get_db()
        
        # Create or get jobs table
        if "jobs" not in db.table_names():
            table = db.create_table("jobs", data=[])
        else:
            table = db.open_table("jobs")
        
        # Create job record
        job_id = str(uuid.uuid4())
        job = {
            "job_id": job_id,
            "document_id": document_id,
            "job_type": job_type,
            "status": JobStatus.QUEUED,
            "priority": priority,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "progress": 0
        }
        
        # Insert into database
        table.add([job])
        
        return JobResponse(**job)
    
    async def queue_job(self, job_id: str):
        """Queue job for processing"""
        job_data = {
            "job_id": job_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await enqueue_job("job_queue", job_data)
    
    async def get_job(self, job_id: str, user_id: str) -> Optional[JobResponse]:
        """Get job by ID"""
        db = get_db()
        
        if "jobs" not in db.table_names():
            return None
        
        table = db.open_table("jobs")
        results = table.search().where(f"job_id = '{job_id}'").limit(1).to_list()
        
        if not results:
            return None
        
        job = results[0]
        
        # Check user access
        if job.get("user_id") != user_id and user_id != "admin":
            return None
        
        return JobResponse(**job)
    
    async def get_job_status(self, job_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        job = await self.get_job(job_id, user_id)
        if not job:
            return None
        
        return {
            "job_id": job_id,
            "status": job.status,
            "progress": job.progress,
            "updated_at": job.updated_at
        }
    
    async def cancel_job(self, job_id: str, user_id: str) -> bool:
        """Cancel a job"""
        job = await self.get_job(job_id, user_id)
        if not job:
            return False
        
        if job.status not in [JobStatus.QUEUED, JobStatus.PROCESSING]:
            return False
        
        # Update job status
        db = get_db()
        table = db.open_table("jobs")
        
        # TODO: Implement proper update
        # For now, return success
        return True
    
    async def retry_job(self, job_id: str, user_id: str) -> Optional[JobResponse]:
        """Retry a failed job"""
        job = await self.get_job(job_id, user_id)
        if not job:
            return None
        
        if job.status != JobStatus.FAILED:
            return None
        
        # Create new job
        new_job = await self.create_job(
            document_id=job.document_id,
            job_type=job.job_type,
            priority=job.priority,
            user_id=user_id
        )
        
        return new_job
    
    async def list_jobs(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[JobStatus] = None,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List jobs with filters"""
        db = get_db()
        
        if "jobs" not in db.table_names():
            return []
        
        table = db.open_table("jobs")
        
        # Build query
        query = table.search()
        
        # Filter by user (unless admin)
        if user_id != "admin":
            query = query.where(f"user_id = '{user_id}'")
        
        # Filter by status if provided
        if status:
            query = query.where(f"status = '{status}'")
        
        # Filter by document if provided
        if document_id:
            query = query.where(f"document_id = '{document_id}'")
        
        # Apply pagination
        results = query.limit(limit).offset(skip).to_list()
        
        return results
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        queue = get_queue()
        
        # Get queue lengths
        job_queue_length = await queue.llen("job_queue")
        processing_queue_length = await queue.llen("processing_queue")
        
        return {
            "job_queue": job_queue_length,
            "processing_queue": processing_queue_length,
            "total": job_queue_length + processing_queue_length
        }
    
    async def get_metrics(
        self,
        time_range: str,
        user_id: Optional[str] = None
    ) -> JobMetrics:
        """Get job processing metrics"""
        # TODO: Implement actual metrics calculation
        return JobMetrics(
            total_jobs=0,
            completed=0,
            failed=0,
            processing=0,
            queued=0,
            average_processing_time_seconds=0.0,
            success_rate=0.0,
            throughput_per_hour=0.0
        )
    
    async def delete_job(self, job_id: str, user_id: str) -> bool:
        """Delete a job"""
        job = await self.get_job(job_id, user_id)
        if not job:
            return False
        
        db = get_db()
        table = db.open_table("jobs")
        
        # TODO: Implement delete
        return True
    
    async def get_batch_jobs(
        self,
        batch_id: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Get all jobs in a batch"""
        db = get_db()
        
        if "jobs" not in db.table_names():
            return []
        
        table = db.open_table("jobs")
        
        # Query jobs by batch_id
        query = table.search().where(f"batch_id = '{batch_id}'")
        
        # Filter by user (unless admin)
        if user_id != "admin":
            query = query.where(f"user_id = '{user_id}'")
        
        results = query.to_list()
        
        return results