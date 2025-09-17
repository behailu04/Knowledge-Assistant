"""
Document ingestion and preprocessing service
"""
import logging
import hashlib
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from config import settings
from database import Document, Chunk
from services.chunking import ChunkingService
from services.embedding import EmbeddingService
from services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

class IngestionService:
    """Service for document ingestion and processing"""
    
    def __init__(self):
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
    
    async def process_document(self, doc_id: str, content: bytes, tenant_id: str) -> Dict[str, Any]:
        """Process a document through the full pipeline"""
        try:
            logger.info(f"Starting processing for document {doc_id}")
            
            # Extract text from document
            text_content = await self._extract_text(content, doc_id)
            if not text_content:
                raise ValueError("No text content extracted from document")
            
            # Chunk the document
            chunks = await self.chunking_service.chunk_text(
                text=text_content,
                doc_id=doc_id,
                tenant_id=tenant_id
            )
            
            logger.info(f"Created {len(chunks)} chunks for document {doc_id}")
            
            # Generate embeddings and store in vector DB
            chunk_ids = []
            for chunk in chunks:
                # Generate embedding
                embedding = await self.embedding_service.generate_embedding(chunk["text"])
                
                # Store in vector database
                chunk_id = await self.vector_store.add_chunk(
                    chunk_id=chunk["chunk_id"],
                    doc_id=doc_id,
                    tenant_id=tenant_id,
                    text=chunk["text"],
                    embedding=embedding,
                    metadata=chunk["metadata"]
                )
                chunk_ids.append(chunk_id)
            
            # Update document status
            await self._update_document_status(doc_id, is_processed=True)
            
            logger.info(f"Successfully processed document {doc_id} with {len(chunk_ids)} chunks")
            
            return {
                "doc_id": doc_id,
                "chunks_created": len(chunks),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {e}")
            await self._update_document_status(doc_id, is_processed=False, error=str(e))
            raise
    
    async def _extract_text(self, content: bytes, doc_id: str) -> str:
        """Extract text from various document formats"""
        try:
            # Simple text extraction - in production, use proper libraries
            # For now, assume content is already text
            if isinstance(content, bytes):
                return content.decode('utf-8', errors='ignore')
            return str(content)
            
        except Exception as e:
            logger.error(f"Error extracting text from document {doc_id}: {e}")
            return ""
    
    async def _update_document_status(self, doc_id: str, is_processed: bool, error: str = None):
        """Update document processing status in database"""
        # This would update the database record
        # For now, just log the status
        logger.info(f"Document {doc_id} status: processed={is_processed}, error={error}")
    
    async def reprocess_document(self, doc_id: str) -> Dict[str, Any]:
        """Reprocess a document (useful for updates)"""
        # This would fetch the document content and reprocess it
        # Implementation depends on how documents are stored
        pass
    
    async def delete_document(self, doc_id: str, tenant_id: str) -> bool:
        """Delete a document and all its chunks"""
        try:
            # Delete from vector store
            await self.vector_store.delete_document_chunks(doc_id, tenant_id)
            
            # Delete from database
            # This would delete the document and chunk records
            
            logger.info(f"Successfully deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
