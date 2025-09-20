"""
Advanced retriever for vector stores
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.vectorstores import FAISS
import logging

logger = logging.getLogger(__name__)


class AdvancedRetriever(VectorStoreRetriever):
    """
    Advanced retriever with enhanced filtering and ranking capabilities
    """
    
    def __init__(
        self,
        vectorstore: FAISS,
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            vectorstore=vectorstore,
            search_type=search_type,
            search_kwargs=search_kwargs or {"k": 4},
            **kwargs
        )
        self.tenant_id = tenant_id
        self.logger = logging.getLogger(__name__)
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents for the given query
        """
        try:
            # Apply tenant filtering if tenant_id is provided
            if self.tenant_id:
                # Filter documents by tenant_id in metadata
                docs = self.vectorstore.similarity_search(
                    query,
                    k=self.search_kwargs.get("k", 4),
                    filter={"tenant_id": self.tenant_id}
                )
            else:
                docs = self.vectorstore.similarity_search(
                    query,
                    k=self.search_kwargs.get("k", 4)
                )
            
            self.logger.info(f"Retrieved {len(docs)} documents for query: {query[:100]}...")
            return docs
            
        except Exception as e:
            self.logger.error(f"Error retrieving documents: {e}")
            return []
    
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """
        Async version of get_relevant_documents
        """
        try:
            # Apply tenant filtering if tenant_id is provided
            if self.tenant_id:
                docs = await self.vectorstore.asimilarity_search(
                    query,
                    k=self.search_kwargs.get("k", 4),
                    filter={"tenant_id": self.tenant_id}
                )
            else:
                docs = await self.vectorstore.asimilarity_search(
                    query,
                    k=self.search_kwargs.get("k", 4)
                )
            
            self.logger.info(f"Retrieved {len(docs)} documents for query: {query[:100]}...")
            return docs
            
        except Exception as e:
            self.logger.error(f"Error retrieving documents: {e}")
            return []
    
    def get_relevant_documents_with_scores(self, query: str) -> List[tuple]:
        """
        Retrieve relevant documents with similarity scores
        """
        try:
            if self.tenant_id:
                docs_with_scores = self.vectorstore.similarity_search_with_score(
                    query,
                    k=self.search_kwargs.get("k", 4),
                    filter={"tenant_id": self.tenant_id}
                )
            else:
                docs_with_scores = self.vectorstore.similarity_search_with_score(
                    query,
                    k=self.search_kwargs.get("k", 4)
                )
            
            self.logger.info(f"Retrieved {len(docs_with_scores)} documents with scores for query: {query[:100]}...")
            return docs_with_scores
            
        except Exception as e:
            self.logger.error(f"Error retrieving documents with scores: {e}")
            return []
    
    def set_tenant_id(self, tenant_id: str):
        """
        Set the tenant ID for filtering
        """
        self.tenant_id = tenant_id
        self.logger.info(f"Set tenant ID to: {tenant_id}")
    
    def clear_tenant_id(self):
        """
        Clear the tenant ID filter
        """
        self.tenant_id = None
        self.logger.info("Cleared tenant ID filter")
