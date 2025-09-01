"""
Document Management Routes
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..models.documents import (
    DocumentResponse,
    DocumentUploadResponse,
    BatchUploadResponse,
    DocumentStatus,
    NetworkDiagram,
    ExtractedTable
)
from ..services.document_service import DocumentService
from ..services.auth import get_current_user

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> DocumentUploadResponse:
    """Upload a single PDF document for processing"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    document_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    
    # Save file to storage
    file_path = await document_service.save_upload(document_id, file)
    
    # Create document record
    document = await document_service.create_document(
        document_id=document_id,
        filename=file.filename,
        file_path=file_path,
        user_id=user.get("id"),
        job_id=job_id
    )
    
    # Queue processing job
    background_tasks.add_task(
        document_service.queue_processing,
        document_id=document_id,
        job_id=job_id
    )
    
    return DocumentUploadResponse(
        document_id=document_id,
        job_id=job_id,
        status=DocumentStatus.QUEUED,
        message="Document uploaded and queued for processing"
    )

@router.post("/batch", response_model=BatchUploadResponse)
async def batch_upload(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> BatchUploadResponse:
    """Upload multiple PDF documents for batch processing"""
    batch_id = str(uuid.uuid4())
    documents = []
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            continue
        
        document_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())
        
        # Save file to storage
        file_path = await document_service.save_upload(document_id, file)
        
        # Create document record
        document = await document_service.create_document(
            document_id=document_id,
            filename=file.filename,
            file_path=file_path,
            user_id=user.get("id"),
            job_id=job_id,
            batch_id=batch_id
        )
        
        documents.append({
            "document_id": document_id,
            "job_id": job_id,
            "filename": file.filename,
            "status": DocumentStatus.QUEUED
        })
        
        # Queue processing job
        background_tasks.add_task(
            document_service.queue_processing,
            document_id=document_id,
            job_id=job_id
        )
    
    return BatchUploadResponse(
        batch_id=batch_id,
        total_documents=len(documents),
        documents=documents,
        message=f"Batch upload completed. {len(documents)} documents queued for processing"
    )

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> DocumentResponse:
    """Get document details by ID"""
    document = await document_service.get_document(document_id, user.get("id"))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> Dict[str, str]:
    """Delete a document and all associated data"""
    success = await document_service.delete_document(document_id, user.get("id"))
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}

@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> Dict[str, Any]:
    """Get processing status of a document"""
    status = await document_service.get_document_status(document_id, user.get("id"))
    if not status:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return status

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
):
    """Download original PDF document"""
    file_response = await document_service.get_document_file(document_id, user.get("id"))
    if not file_response:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return file_response

@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str,
    page: Optional[int] = Query(None, description="Specific page number"),
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> Dict[str, Any]:
    """Get extracted text content from document"""
    content = await document_service.get_document_content(
        document_id, 
        user.get("id"),
        page=page
    )
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content

@router.get("/{document_id}/diagrams", response_model=List[NetworkDiagram])
async def get_network_diagrams(
    document_id: str,
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> List[NetworkDiagram]:
    """Get extracted network diagrams from document"""
    diagrams = await document_service.get_network_diagrams(document_id, user.get("id"))
    return diagrams

@router.get("/{document_id}/tables", response_model=List[ExtractedTable])
async def get_tables(
    document_id: str,
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> List[ExtractedTable]:
    """Get extracted tables from document"""
    tables = await document_service.get_tables(document_id, user.get("id"))
    return tables

@router.get("/")
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[DocumentStatus] = None,
    user: Dict = Depends(get_current_user),
    document_service: DocumentService = Depends()
) -> Dict[str, Any]:
    """List all documents with pagination"""
    documents = await document_service.list_documents(
        user_id=user.get("id"),
        skip=skip,
        limit=limit,
        status=status
    )
    
    return {
        "documents": documents,
        "total": len(documents),
        "skip": skip,
        "limit": limit
    }