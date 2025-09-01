"""
Document Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NetworkDevice(BaseModel):
    id: str
    type: str
    label: Optional[str] = None
    x: float
    y: float
    properties: Dict[str, Any] = {}

class NetworkConnection(BaseModel):
    source: str
    target: str
    type: Optional[str] = None
    label: Optional[str] = None
    properties: Dict[str, Any] = {}

class NetworkDiagram(BaseModel):
    diagram_id: str
    page_number: int
    devices: List[NetworkDevice]
    connections: List[NetworkConnection]
    metadata: Dict[str, Any] = {}

class ExtractedTable(BaseModel):
    table_id: str
    page_number: int
    headers: List[str]
    rows: List[List[str]]
    metadata: Dict[str, Any] = {}

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    page_count: Optional[int] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = {}
    error_message: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    document_id: str
    job_id: str
    status: DocumentStatus
    message: str

class BatchUploadResponse(BaseModel):
    batch_id: str
    total_documents: int
    documents: List[Dict[str, Any]]
    message: str

class DocumentContent(BaseModel):
    document_id: str
    page_number: Optional[int] = None
    text: str
    metadata: Dict[str, Any] = {}