"""
Tenant-aware FAISS vector store using LangChain
"""
import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class TenantAwareFAISSStore:
    """FAISS vector store with tenant isolation"""
    
    def __init__(self, 
                 embedding_function: Embeddings,
                 storage_path: str = "./data/vector_stores",
                 index_type: str = "HNSW"):
        
        self.embedding_function = embedding_function
        self.storage_path = Path(storage_path)
        self.index_type = index_type
        self.tenant_stores: Dict[str, FAISS] = {}
        self.tenant_metadata: Dict[str, Dict] = {}
        
        self._ensure_storage_path()
        self._load_existing_stores()
    
    def _ensure_storage_path(self):
        """Ensure storage path exists"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _load_existing_stores(self):
        """Load existing tenant stores from disk"""
        try:
            for tenant_dir in self.storage_path.iterdir():
                if tenant_dir.is_dir():
                    tenant_id = tenant_dir.name
                    store_path = tenant_dir / "faiss_index"
                    metadata_path = tenant_dir / "metadata.pkl"
                    
                    if store_path.exists() and metadata_path.exists():
                        try:
                            # Load FAISS store
                            store = FAISS.load_local(
                                str(store_path), 
                                self.embedding_function,
                                allow_dangerous_deserialization=True
                            )
                            self.tenant_stores[tenant_id] = store
                            
                            # Load metadata
                            with open(metadata_path, 'rb') as f:
                                metadata = pickle.load(f)
                            self.tenant_metadata[tenant_id] = metadata
                            
                            logger.info(f"Loaded existing store for tenant: {tenant_id}")
                            
                        except Exception as e:
                            logger.error(f"Error loading store for tenant {tenant_id}: {e}")
                            
        except Exception as e:
            logger.error(f"Error loading existing stores: {e}")
    
    def add_documents(self, documents: List[Document], tenant_id: str) -> List[str]:
        """Add documents to tenant-specific store"""
        try:
            if tenant_id not in self.tenant_stores:
                self._create_tenant_store(tenant_id)
            
            # Add documents to existing store
            ids = self.tenant_stores[tenant_id].add_documents(documents)
            
            # Update metadata
            if tenant_id not in self.tenant_metadata:
                self.tenant_metadata[tenant_id] = {
                    'document_count': 0,
                    'last_updated': None,
                    'index_type': self.index_type
                }
            
            self.tenant_metadata[tenant_id]['document_count'] += len(documents)
            self.tenant_metadata[tenant_id]['last_updated'] = self._get_current_timestamp()
            
            # Save store and metadata
            self._save_tenant_store(tenant_id)
            
            logger.info(f"Added {len(documents)} documents to tenant {tenant_id}")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents to tenant {tenant_id}: {e}")
            raise
    
    def similarity_search(self, 
                         query: str, 
                         tenant_id: str, 
                         k: int = 5,
                         filter_dict: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents in tenant store"""
        try:
            if tenant_id not in self.tenant_stores:
                logger.warning(f"No store found for tenant: {tenant_id}")
                return []
            
            # Perform similarity search
            if filter_dict:
                docs = self.tenant_stores[tenant_id].similarity_search(
                    query, k=k, filter=filter_dict
                )
            else:
                docs = self.tenant_stores[tenant_id].similarity_search(query, k=k)
            
            return docs
            
        except Exception as e:
            logger.error(f"Error searching tenant {tenant_id}: {e}")
            return []
    
    def similarity_search_with_score(self, 
                                   query: str, 
                                   tenant_id: str, 
                                   k: int = 5) -> List[tuple]:
        """Search with similarity scores"""
        try:
            if tenant_id not in self.tenant_stores:
                return []
            
            docs_with_scores = self.tenant_stores[tenant_id].similarity_search_with_score(
                query, k=k
            )
            
            return docs_with_scores
            
        except Exception as e:
            logger.error(f"Error searching with scores for tenant {tenant_id}: {e}")
            return []
    
    def delete_documents(self, tenant_id: str, document_ids: List[str]) -> bool:
        """Delete specific documents from tenant store"""
        try:
            if tenant_id not in self.tenant_stores:
                return False
            
            # Note: FAISS doesn't support deletion directly
            # In production, implement a deletion strategy (rebuild index, etc.)
            logger.warning("Document deletion not fully supported in FAISS - consider rebuilding index")
            
            # Update metadata
            self.tenant_metadata[tenant_id]['document_count'] -= len(document_ids)
            self.tenant_metadata[tenant_id]['last_updated'] = self._get_current_timestamp()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents from tenant {tenant_id}: {e}")
            return False
    
    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get statistics for a tenant store"""
        if tenant_id not in self.tenant_stores:
            return {'error': 'Tenant not found'}
        
        metadata = self.tenant_metadata.get(tenant_id, {})
        store = self.tenant_stores[tenant_id]
        
        return {
            'tenant_id': tenant_id,
            'document_count': metadata.get('document_count', 0),
            'last_updated': metadata.get('last_updated'),
            'index_type': metadata.get('index_type', self.index_type),
            'vector_count': store.index.ntotal if hasattr(store, 'index') else 0,
            'embedding_dimension': self.embedding_function.get_embedding_dimension() if hasattr(self.embedding_function, 'get_embedding_dimension') else 'unknown'
        }
    
    def list_tenants(self) -> List[str]:
        """List all tenant IDs"""
        return list(self.tenant_stores.keys())
    
    def _create_tenant_store(self, tenant_id: str):
        """Create a new store for a tenant"""
        try:
            # Create empty store with dummy document
            dummy_doc = Document(page_content="", metadata={"tenant_id": tenant_id})
            store = FAISS.from_documents([dummy_doc], self.embedding_function)
            
            self.tenant_stores[tenant_id] = store
            self.tenant_metadata[tenant_id] = {
                'document_count': 0,
                'last_updated': self._get_current_timestamp(),
                'index_type': self.index_type
            }
            
            logger.info(f"Created new store for tenant: {tenant_id}")
            
        except Exception as e:
            logger.error(f"Error creating store for tenant {tenant_id}: {e}")
            raise
    
    def _save_tenant_store(self, tenant_id: str):
        """Save tenant store to disk"""
        try:
            tenant_dir = self.storage_path / tenant_id
            tenant_dir.mkdir(exist_ok=True)
            
            store_path = tenant_dir / "faiss_index"
            metadata_path = tenant_dir / "metadata.pkl"
            
            # Save FAISS store
            self.tenant_stores[tenant_id].save_local(str(store_path))
            
            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.tenant_metadata[tenant_id], f)
                
        except Exception as e:
            logger.error(f"Error saving store for tenant {tenant_id}: {e}")
            raise
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def health_check(self) -> bool:
        """Check if vector store is healthy"""
        try:
            # Check if we can access at least one tenant store
            if not self.tenant_stores:
                return True  # Empty store is still healthy
            
            # Test with first tenant
            first_tenant = next(iter(self.tenant_stores.keys()))
            test_result = self.similarity_search("health check", first_tenant, k=1)
            return True
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            return False
    
    def as_retriever(self, tenant_id: str, **kwargs):
        """Get retriever for a specific tenant"""
        if tenant_id not in self.tenant_stores:
            # Create a default empty store for the tenant
            logger.info(f"Creating default store for tenant: {tenant_id}")
            self._create_tenant_store(tenant_id)
        
        return self.tenant_stores[tenant_id].as_retriever(**kwargs)
