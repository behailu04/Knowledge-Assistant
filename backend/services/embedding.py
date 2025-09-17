"""
Embedding service for generating vector representations
"""
import logging
import numpy as np
from typing import List, Union
import asyncio
from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Embedding model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            if not self.model:
                raise ValueError("Embedding model not loaded")
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self._encode_text, 
                text
            )
            
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            if not self.model:
                raise ValueError("Embedding model not loaded")
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self._encode_texts_batch,
                texts
            )
            
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def _encode_text(self, text: str) -> np.ndarray:
        """Encode a single text to embedding"""
        return self.model.encode(text, convert_to_tensor=False)
    
    def _encode_texts_batch(self, texts: List[str]) -> np.ndarray:
        """Encode multiple texts to embeddings"""
        return self.model.encode(texts, convert_to_tensor=False)
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    async def find_most_similar(self, query_embedding: List[float], 
                              candidate_embeddings: List[List[float]], 
                              top_k: int = 5) -> List[tuple]:
        """Find most similar embeddings to query"""
        try:
            similarities = []
            query_emb = np.array(query_embedding)
            
            for i, candidate_emb in enumerate(candidate_embeddings):
                similarity = await self.compute_similarity(query_embedding, candidate_emb)
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding most similar embeddings: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        if not self.model:
            return 384  # Default for all-MiniLM-L6-v2
        
        return self.model.get_sentence_embedding_dimension()
    
    async def health_check(self) -> bool:
        """Check if embedding service is healthy"""
        try:
            # Test with a simple embedding
            test_embedding = await self.generate_embedding("test")
            return len(test_embedding) > 0
        except Exception as e:
            logger.error(f"Embedding service health check failed: {e}")
            return False
