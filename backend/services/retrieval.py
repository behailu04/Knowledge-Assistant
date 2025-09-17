"""
Retrieval service for document search and ranking
"""
import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from services.embedding import EmbeddingService
from services.vector_store import VectorStoreService
from services.reranker import RerankerService
from config import settings

logger = logging.getLogger(__name__)

class RetrievalService:
    """Service for document retrieval and ranking"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.reranker = RerankerService()
    
    async def retrieve_documents(self, query: str, tenant_id: str, 
                               top_k: int = None, top_n: int = None) -> List[Dict[str, Any]]:
        """Retrieve and rank documents for a query"""
        try:
            if top_k is None:
                top_k = settings.TOP_K_RETRIEVAL
            if top_n is None:
                top_n = settings.TOP_N_RERANK
            
            logger.info(f"Retrieving documents for query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Search vector store
            candidates = await self.vector_store.search(
                query_embedding=query_embedding,
                tenant_id=tenant_id,
                top_k=top_k,
                similarity_threshold=settings.SIMILARITY_THRESHOLD
            )
            
            if not candidates:
                logger.warning(f"No candidates found for query: {query}")
                return []
            
            logger.info(f"Found {len(candidates)} candidates, reranking to top {top_n}")
            
            # Rerank candidates
            ranked_results = await self.reranker.rerank(
                query=query,
                candidates=candidates,
                top_n=top_n
            )
            
            # Format results
            results = []
            for i, result in enumerate(ranked_results):
                results.append({
                    "chunk_id": result["chunk_id"],
                    "doc_id": result["doc_id"],
                    "text": result["text"],
                    "score": result["score"],
                    "rank": i + 1,
                    "metadata": result.get("metadata", {}),
                    "snippet": self._create_snippet(result["text"], query)
                })
            
            logger.info(f"Retrieved {len(results)} ranked documents")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    async def retrieve_for_multi_hop(self, subquery: str, tenant_id: str, 
                                   context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve documents for multi-hop reasoning"""
        try:
            # Enhance subquery with context if available
            enhanced_query = self._enhance_query_with_context(subquery, context)
            
            # Retrieve documents
            results = await self.retrieve_documents(
                query=enhanced_query,
                tenant_id=tenant_id,
                top_k=settings.TOP_K_RETRIEVAL // 2,  # Fewer for subqueries
                top_n=settings.TOP_N_RERANK // 2
            )
            
            # Add context information
            for result in results:
                result["subquery"] = subquery
                result["context"] = context or {}
            
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-hop retrieval: {e}")
            return []
    
    def _create_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Create a snippet highlighting the query terms"""
        try:
            # Simple snippet creation - in production, use more sophisticated highlighting
            query_terms = query.lower().split()
            text_lower = text.lower()
            
            # Find the best position to start the snippet
            best_pos = 0
            max_matches = 0
            
            for i in range(len(text) - max_length):
                snippet = text[i:i + max_length].lower()
                matches = sum(1 for term in query_terms if term in snippet)
                if matches > max_matches:
                    max_matches = matches
                    best_pos = i
            
            snippet = text[best_pos:best_pos + max_length]
            
            # Add ellipsis if needed
            if best_pos > 0:
                snippet = "..." + snippet
            if best_pos + max_length < len(text):
                snippet = snippet + "..."
            
            return snippet
            
        except Exception as e:
            logger.error(f"Error creating snippet: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def _enhance_query_with_context(self, subquery: str, context: Dict[str, Any]) -> str:
        """Enhance subquery with context from previous hops"""
        if not context:
            return subquery
        
        # Add relevant context information
        context_parts = []
        
        if "previous_results" in context:
            # Add information from previous retrieval results
            prev_results = context["previous_results"]
            if prev_results:
                context_parts.append("Previous findings:")
                for result in prev_results[:3]:  # Limit context
                    context_parts.append(f"- {result.get('text', '')[:100]}...")
        
        if "entities" in context:
            # Add relevant entities
            entities = context["entities"]
            if entities:
                context_parts.append(f"Relevant entities: {', '.join(entities)}")
        
        if context_parts:
            enhanced_query = f"{subquery}\n\nContext:\n" + "\n".join(context_parts)
            return enhanced_query
        
        return subquery
    
    async def get_document_chunks(self, doc_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            chunks = await self.vector_store.get_document_chunks(doc_id, tenant_id)
            
            # Format chunks
            formatted_chunks = []
            for chunk in chunks:
                formatted_chunks.append({
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                    "index_id": chunk["index_id"]
                })
            
            return formatted_chunks
            
        except Exception as e:
            logger.error(f"Error getting document chunks: {e}")
            return []
    
    async def search_similar_chunks(self, chunk_id: str, tenant_id: str, 
                                  top_k: int = 10) -> List[Dict[str, Any]]:
        """Find chunks similar to a specific chunk"""
        try:
            # Get the chunk
            chunk = await self.vector_store.get_chunk(chunk_id)
            if not chunk or chunk["tenant_id"] != tenant_id:
                return []
            
            # Get its embedding (would need to store this separately in production)
            # For now, we'll use the text to generate embedding
            embedding = await self.embedding_service.generate_embedding(chunk["text"])
            
            # Search for similar chunks
            similar_chunks = await self.vector_store.search(
                query_embedding=embedding,
                tenant_id=tenant_id,
                top_k=top_k + 1,  # +1 to exclude the original chunk
                similarity_threshold=0.5
            )
            
            # Filter out the original chunk
            filtered_chunks = [
                c for c in similar_chunks 
                if c["chunk_id"] != chunk_id
            ]
            
            return filtered_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if retrieval service is healthy"""
        try:
            embedding_healthy = await self.embedding_service.health_check()
            vector_store_healthy = await self.vector_store.health_check()
            
            return embedding_healthy and vector_store_healthy
            
        except Exception as e:
            logger.error(f"Retrieval service health check failed: {e}")
            return False
