"""
Embedding management using LangChain
"""
from typing import List, Optional, Dict, Any
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings, OllamaEmbeddings
from langchain_core.embeddings import Embeddings
import logging
import os

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Unified embedding manager supporting multiple providers"""
    
    def __init__(self, 
                 provider: str = "openai", 
                 model_name: Optional[str] = None,
                 cache_folder: Optional[str] = None):
        
        self.provider = provider.lower()
        self.model_name = model_name
        self.cache_folder = cache_folder or "./embeddings_cache"
        self.embedder = self._initialize_embedder()
        
        # Ensure cache directory exists
        os.makedirs(self.cache_folder, exist_ok=True)
    
    def _initialize_embedder(self) -> Embeddings:
        """Initialize embedding model based on provider"""
        try:
            if self.provider == "ollama":
                model = self.model_name or "nomic-embed-text"
                return OllamaEmbeddings(
                    model=model,
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                )
            
            elif self.provider == "huggingface":
                model = self.model_name or "sentence-transformers/all-MiniLM-L6-v2"
                return HuggingFaceEmbeddings(
                    model_name=model,
                    cache_folder=self.cache_folder
                )
            
            elif self.provider == "openai":
                model = self.model_name or "text-embedding-ada-002"
                return OpenAIEmbeddings(
                    model=model,
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    cache_folder=self.cache_folder
                )
            
            else:
                raise ValueError(f"Unsupported embedding provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error initializing embedding provider {self.provider}: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents"""
        try:
            logger.info(f"Generating embeddings for {len(texts)} documents using {self.provider}")
            embeddings = self.embedder.embed_documents(texts)
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating document embeddings: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        try:
            embedding = self.embedder.embed_query(text)
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def embed_documents_async(self, texts: List[str]) -> List[List[float]]:
        """Async version of embed_documents (if supported)"""
        # For now, just call sync version
        # In production, implement proper async embedding
        return self.embed_documents(texts)
    
    def embed_query_async(self, text: str) -> List[float]:
        """Async version of embed_query (if supported)"""
        # For now, just call sync version
        return self.embed_query(text)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        try:
            # Generate a test embedding to get dimension
            test_embedding = self.embed_query("test")
            return len(test_embedding)
        except Exception as e:
            logger.error(f"Error getting embedding dimension: {e}")
            # Return default dimension based on provider
            if self.provider == "openai":
                return 1536  # text-embedding-ada-002 dimension
            elif self.provider == "huggingface":
                return 384   # all-MiniLM-L6-v2 dimension
            else:
                return 768   # Default
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        return {
            "provider": self.provider,
            "model_name": self.model_name or "default",
            "dimension": self.get_embedding_dimension(),
            "cache_folder": self.cache_folder
        }
    
    def health_check(self) -> bool:
        """Check if embedding service is healthy"""
        try:
            # Test with a simple embedding
            test_embedding = self.embed_query("health check")
            return len(test_embedding) > 0
        except Exception as e:
            logger.error(f"Embedding service health check failed: {e}")
            return False

class MultiProviderEmbeddingManager:
    """Manager for multiple embedding providers"""
    
    def __init__(self, providers: Dict[str, Dict[str, Any]]):
        self.providers = {}
        self.default_provider = None
        
        for name, config in providers.items():
            self.providers[name] = EmbeddingManager(**config)
            if config.get("default", False) or not self.default_provider:
                self.default_provider = name
    
    def get_embedder(self, provider_name: Optional[str] = None) -> Embeddings:
        """Get embedding provider by name"""
        provider = provider_name or self.default_provider
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        return self.providers[provider].embedder
    
    def embed_documents(self, texts: List[str], provider_name: Optional[str] = None) -> List[List[float]]:
        """Generate embeddings using specified provider"""
        provider = provider_name or self.default_provider
        return self.providers[provider].embed_documents(texts)
    
    def embed_query(self, text: str, provider_name: Optional[str] = None) -> List[float]:
        """Generate query embedding using specified provider"""
        provider = provider_name or self.default_provider
        return self.providers[provider].embed_query(text)
