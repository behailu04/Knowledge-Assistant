"""
Vector store service using FAISS
"""
import logging
import numpy as np
import faiss
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for vector storage and retrieval using FAISS"""
    
    def __init__(self, index_path: str = "./data/vector_index", dimension: int = 384):
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.index = None
        self.metadata = {}  # Store chunk metadata
        self.tenant_indices = {}  # Per-tenant indices for isolation
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize vector storage"""
        try:
            # Create directory if it doesn't exist
            self.index_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing index if available
            self._load_index()
            
            logger.info(f"Vector store initialized at {self.index_path}")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def _load_index(self):
        """Load existing FAISS index"""
        try:
            index_file = self.index_path / "faiss_index.bin"
            metadata_file = self.index_path / "metadata.pkl"
            
            if index_file.exists() and metadata_file.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(index_file))
                
                # Load metadata
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self._create_new_index()
                
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        try:
            # Create HNSW index for fast approximate search
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.metadata = {}
            
            logger.info("Created new FAISS index")
            
        except Exception as e:
            logger.error(f"Error creating new index: {e}")
            raise
    
    async def add_chunk(self, chunk_id: str, doc_id: str, tenant_id: str, 
                       text: str, embedding: List[float], 
                       metadata: Dict[str, Any]) -> str:
        """Add a chunk to the vector store"""
        try:
            # Convert embedding to numpy array
            embedding_array = np.array(embedding, dtype=np.float32).reshape(1, -1)
            
            # Add to index
            self.index.add(embedding_array)
            
            # Store metadata
            chunk_metadata = {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "tenant_id": tenant_id,
                "text": text,
                "metadata": metadata,
                "index_id": self.index.ntotal - 1  # FAISS index ID
            }
            
            self.metadata[chunk_id] = chunk_metadata
            
            # Save index and metadata
            await self._save_index()
            
            logger.info(f"Added chunk {chunk_id} to vector store")
            return chunk_id
            
        except Exception as e:
            logger.error(f"Error adding chunk to vector store: {e}")
            raise
    
    async def search(self, query_embedding: List[float], tenant_id: str, 
                    top_k: int = 50, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            # Convert query to numpy array
            query_array = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_array, top_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # Invalid index
                    continue
                
                # Find chunk metadata by index ID
                chunk_metadata = None
                for chunk_id, meta in self.metadata.items():
                    if meta["index_id"] == idx:
                        chunk_metadata = meta
                        break
                
                if not chunk_metadata:
                    continue
                
                # Filter by tenant
                if chunk_metadata["tenant_id"] != tenant_id:
                    continue
                
                # Apply similarity threshold
                if score < similarity_threshold:
                    continue
                
                results.append({
                    "chunk_id": chunk_metadata["chunk_id"],
                    "doc_id": chunk_metadata["doc_id"],
                    "text": chunk_metadata["text"],
                    "score": float(score),
                    "metadata": chunk_metadata["metadata"]
                })
            
            logger.info(f"Found {len(results)} similar chunks for tenant {tenant_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    async def delete_document_chunks(self, doc_id: str, tenant_id: str) -> bool:
        """Delete all chunks for a document"""
        try:
            # Find chunks for this document
            chunks_to_delete = []
            for chunk_id, metadata in self.metadata.items():
                if (metadata["doc_id"] == doc_id and 
                    metadata["tenant_id"] == tenant_id):
                    chunks_to_delete.append(chunk_id)
            
            # Remove from metadata
            for chunk_id in chunks_to_delete:
                del self.metadata[chunk_id]
            
            # Note: FAISS doesn't support deletion, so we'll need to rebuild
            # In production, consider using a different vector store or implement
            # a deletion strategy
            
            logger.info(f"Deleted {len(chunks_to_delete)} chunks for document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document chunks: {e}")
            return False
    
    async def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get chunk by ID"""
        return self.metadata.get(chunk_id)
    
    async def get_document_chunks(self, doc_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document"""
        chunks = []
        for chunk_id, metadata in self.metadata.items():
            if (metadata["doc_id"] == doc_id and 
                metadata["tenant_id"] == tenant_id):
                chunks.append(metadata)
        
        return chunks
    
    async def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            index_file = self.index_path / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata_file = self.index_path / "metadata.pkl"
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.debug("Saved vector index and metadata")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if vector store is healthy"""
        try:
            return self.index is not None and self.index.ntotal >= 0
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            return {
                "total_vectors": self.index.ntotal if self.index else 0,
                "dimension": self.dimension,
                "total_chunks": len(self.metadata),
                "index_type": "HNSW" if self.index else "None"
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            return {}
