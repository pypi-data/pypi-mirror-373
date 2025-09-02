"""
Document Service - Business logic for document operations
"""

from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import uuid
import os
from datetime import datetime

from .database import get_db
from .storage import get_storage
from .queue import enqueue_job
from ..models.documents import DocumentStatus, NetworkDiagram, ExtractedTable

class DocumentService:
    """Service for document management operations"""
    
    async def save_upload(self, document_id: str, file: UploadFile) -> str:
        """Save uploaded file to storage"""
        s3_client, bucket = get_storage()
        
        # Generate storage path
        file_path = f"documents/{document_id}/{file.filename}"
        
        # Upload to S3/MinIO
        await s3_client.upload_fileobj(
            file.file,
            bucket,
            file_path
        )
        
        return file_path
    
    async def create_document(
        self,
        document_id: str,
        filename: str,
        file_path: str,
        user_id: str,
        job_id: str,
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create document record in database"""
        db = get_db()
        
        # Create or get documents table
        if "documents" not in db.table_names():
            table = db.create_table("documents", data=[])
        else:
            table = db.open_table("documents")
        
        # Create document record
        document = {
            "document_id": document_id,
            "filename": filename,
            "file_path": file_path,
            "user_id": user_id,
            "job_id": job_id,
            "batch_id": batch_id,
            "status": DocumentStatus.QUEUED,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert into database
        table.add([document])
        
        return document
    
    async def queue_processing(self, document_id: str, job_id: str):
        """Queue document for processing"""
        job_data = {
            "job_id": job_id,
            "document_id": document_id,
            "type": "pdf_processing",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await enqueue_job("processing_queue", job_data)
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        db = get_db()
        
        if "documents" not in db.table_names():
            return None
        
        table = db.open_table("documents")
        results = table.search().where(f"document_id = '{document_id}'").limit(1).to_list()
        
        if not results:
            return None
        
        document = results[0]
        
        # Check user access
        if document.get("user_id") != user_id and user_id != "admin":
            return None
        
        return document
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document and associated data"""
        document = await self.get_document(document_id, user_id)
        if not document:
            return False
        
        # Delete from storage
        s3_client, bucket = get_storage()
        file_path = document.get("file_path")
        if file_path:
            await s3_client.delete_object(Bucket=bucket, Key=file_path)
        
        # Delete from database
        db = get_db()
        table = db.open_table("documents")
        table.delete(f"document_id = '{document_id}'")
        
        return True
    
    async def get_document_status(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get document processing status"""
        document = await self.get_document(document_id, user_id)
        if not document:
            return None
        
        return {
            "document_id": document_id,
            "status": document.get("status"),
            "progress": document.get("progress", 0),
            "updated_at": document.get("updated_at")
        }
    
    async def get_document_file(self, document_id: str, user_id: str):
        """Get document file for download"""
        document = await self.get_document(document_id, user_id)
        if not document:
            return None
        
        s3_client, bucket = get_storage()
        file_path = document.get("file_path")
        
        # Get file from S3
        response = await s3_client.get_object(Bucket=bucket, Key=file_path)
        
        return StreamingResponse(
            response['Body'],
            media_type='application/pdf',
            headers={
                "Content-Disposition": f"attachment; filename={document.get('filename')}"
            }
        )
    
    async def get_document_content(
        self,
        document_id: str,
        user_id: str,
        page: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get extracted text content"""
        document = await self.get_document(document_id, user_id)
        if not document:
            return None
        
        db = get_db()
        
        if "content" not in db.table_names():
            return None
        
        table = db.open_table("content")
        
        if page is not None:
            results = table.search().where(
                f"document_id = '{document_id}' AND page_number = {page}"
            ).to_list()
        else:
            results = table.search().where(
                f"document_id = '{document_id}'"
            ).to_list()
        
        return {
            "document_id": document_id,
            "pages": results,
            "total_pages": len(results)
        }
    
    async def get_network_diagrams(
        self,
        document_id: str,
        user_id: str
    ) -> List[NetworkDiagram]:
        """Get extracted network diagrams"""
        document = await self.get_document(document_id, user_id)
        if not document:
            return []
        
        db = get_db()
        
        if "diagrams" not in db.table_names():
            return []
        
        table = db.open_table("diagrams")
        results = table.search().where(f"document_id = '{document_id}'").to_list()
        
        diagrams = []
        for result in results:
            diagram = NetworkDiagram(
                diagram_id=result.get("diagram_id"),
                page_number=result.get("page_number"),
                devices=result.get("devices", []),
                connections=result.get("connections", []),
                metadata=result.get("metadata", {})
            )
            diagrams.append(diagram)
        
        return diagrams
    
    async def get_tables(
        self,
        document_id: str,
        user_id: str
    ) -> List[ExtractedTable]:
        """Get extracted tables"""
        document = await self.get_document(document_id, user_id)
        if not document:
            return []
        
        db = get_db()
        
        if "tables" not in db.table_names():
            return []
        
        table = db.open_table("tables")
        results = table.search().where(f"document_id = '{document_id}'").to_list()
        
        tables = []
        for result in results:
            extracted_table = ExtractedTable(
                table_id=result.get("table_id"),
                page_number=result.get("page_number"),
                headers=result.get("headers", []),
                rows=result.get("rows", []),
                metadata=result.get("metadata", {})
            )
            tables.append(extracted_table)
        
        return tables
    
    async def list_documents(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[DocumentStatus] = None
    ) -> List[Dict[str, Any]]:
        """List documents with pagination"""
        db = get_db()
        
        if "documents" not in db.table_names():
            return []
        
        table = db.open_table("documents")
        
        # Build query
        query = table.search()
        
        # Filter by user (unless admin)
        if user_id != "admin":
            query = query.where(f"user_id = '{user_id}'")
        
        # Filter by status if provided
        if status:
            query = query.where(f"status = '{status}'")
        
        # Apply pagination
        results = query.limit(limit).offset(skip).to_list()
        
        return results