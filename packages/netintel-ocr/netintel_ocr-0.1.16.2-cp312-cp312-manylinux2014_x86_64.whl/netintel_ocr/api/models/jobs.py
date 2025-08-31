"""
Job Models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobType(str, Enum):
    PDF_PROCESSING = "pdf_processing"
    DIAGRAM_EXTRACTION = "diagram_extraction"
    TABLE_EXTRACTION = "table_extraction"
    TEXT_EXTRACTION = "text_extraction"
    VECTOR_GENERATION = "vector_generation"

class JobPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class JobCreate(BaseModel):
    document_id: str
    job_type: JobType = JobType.PDF_PROCESSING
    priority: JobPriority = JobPriority.NORMAL

class JobResponse(BaseModel):
    job_id: str
    document_id: str
    job_type: JobType
    status: JobStatus
    priority: JobPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = Field(0, ge=0, le=100)
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}

class JobMetrics(BaseModel):
    total_jobs: int
    completed: int
    failed: int
    processing: int
    queued: int
    average_processing_time_seconds: float
    success_rate: float
    throughput_per_hour: float