"""
Document management router
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
import hashlib
import os
from datetime import datetime

from database import get_db, Document
from models.schemas import (
    DocumentResponse, 
    DocumentUploadRequest, 
    IngestionStatusResponse,
    ErrorResponse
)
from services.ingestion import IngestionService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tenant_id: str = None,
    doc_type: str = None,
    language: str = "en",
    db: Session = Depends(get_db)
):
    """Upload a document for processing"""
    if not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    if not doc_type:
        raise HTTP_TaskException(status_code=400, detail="doc_type is required")
    
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Calculate checksum
        checksum = hashlib.sha256(content).hexdigest()
        
        # Check if document already exists
        existing_doc = db.query(Document).filter(
            Document.tenant_id == tenant_id,
            Document.checksum == checksum
        ).first()
        
        if existing_doc:
            return DocumentResponse(
                doc_id=str(existing_doc.doc_id),
                tenant_id=existing_doc.tenant_id,
                original_path=existing_doc.original_path,
                doc_type=existing_doc.doc_type,
                language=existing_doc.language,
                uploaded_at=existing_doc.uploaded_at,
                is_processed=existing_doc.is_processed,
                file_size=existing_doc.file_size,
                metadata=existing_doc.doc_metadata or {}
            )
        
        # Create document record
        doc = Document(
            tenant_id=tenant_id,
            original_path=file.filename,
            doc_type=doc_type,
            language=language,
            checksum=checksum,
            file_size=file_size,
            metadata={"original_filename": file.filename}
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Start background processing
        ingestion_service = IngestionService()
        background_tasks.add_task(
            process_document_background,
            doc.doc_id,
            content,
            tenant_id
        )
        
        return DocumentResponse(
            doc_id=str(doc.doc_id),
            tenant_id=doc.tenant_id,
            original_path=doc.original_path,
            doc_type=doc.doc_type,
            language=doc.language,
            uploaded_at=doc.uploaded_at,
            is_processed=doc.is_processed,
            file_size=doc.file_size,
            metadata=doc.doc_metadata or {}
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

async def process_document_background(doc_id: str, content: bytes, tenant_id: str):
    """Background task to process document"""
    try:
        ingestion_service = IngestionService()
        await ingestion_service.process_document(doc_id, content, tenant_id)
    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {e}")

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Get document by ID"""
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        doc_id=str(doc.doc_id),
        tenant_id=doc.tenant_id,
        original_path=doc.original_path,
        doc_type=doc.doc_type,
        language=doc.language,
        uploaded_at=doc.uploaded_at,
        is_processed=doc.is_processed,
        file_size=doc.file_size,
        metadata=doc.metadata or {}
    )

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    tenant_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List documents for a tenant"""
    docs = db.query(Document).filter(
        Document.tenant_id == tenant_id
    ).offset(skip).limit(limit).all()
    
    return [
        DocumentResponse(
            doc_id=str(doc.doc_id),
            tenant_id=doc.tenant_id,
            original_path=doc.original_path,
            doc_type=doc.doc_type,
            language=doc.language,
            uploaded_at=doc.uploaded_at,
            is_processed=doc.is_processed,
            file_size=doc.file_size,
            metadata=doc.doc_metadata or {}
        )
        for doc in docs
    ]

@router.get("/documents/{doc_id}/status", response_model=IngestionStatusResponse)
async def get_ingestion_status(doc_id: str, db: Session = Depends(get_db)):
    """Get document ingestion status"""
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Count chunks for this document
    from database import Chunk
    chunk_count = db.query(Chunk).filter(Chunk.doc_id == doc_id).count()
    
    status = "completed" if doc.is_processed else "processing"
    
    return IngestionStatusResponse(
        doc_id=str(doc.doc_id),
        status=status,
        message="Processing completed" if doc.is_processed else "Processing in progress",
        chunks_created=chunk_count
    )

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete a document and its chunks"""
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete chunks first
        from database import Chunk
        db.query(Chunk).filter(Chunk.doc_id == doc_id).delete()
        
        # Delete document
        db.delete(doc)
        db.commit()
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
