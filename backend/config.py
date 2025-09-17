"""
Configuration settings for the Knowledge Assistant
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Knowledge Assistant"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/knowledge_assistant"
    
    # Vector Store
    VECTOR_STORE_TYPE: str = "faiss"  # faiss, milvus, pinecone
    VECTOR_DIMENSION: int = 384  # sentence-transformers default
    VECTOR_INDEX_PATH: str = "./data/vector_index"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"  # cpu, cuda
    
    # LLM Settings
    LLM_PROVIDER: str = "ollama"  # openai, ollama, local
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # Retrieval Settings
    TOP_K_RETRIEVAL: int = 50
    TOP_N_RERANK: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    RERANKER_THRESHOLD: float = 0.5
    
    # Multi-hop Settings
    MAX_HOPS: int = 3
    SELF_CONSISTENCY_SAMPLES: int = 5
    COT_ENABLED: bool = True
    
    # Chunking Settings
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 50
    MIN_CHUNK_SIZE: int = 100
    
    # Storage
    S3_BUCKET: Optional[str] = None
    S3_REGION: str = "us-east-1"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
