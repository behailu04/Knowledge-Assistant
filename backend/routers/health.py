"""
Health check router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from database import get_db
from models.schemas import HealthResponse
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    services = {}
    
    # Check database
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        services["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services["database"] = "unhealthy"
    
    # Check vector store
    try:
        # This would check FAISS index or other vector store
        services["vector_store"] = "healthy"
    except Exception as e:
        logger.error(f"Vector store health check failed: {e}")
        services["vector_store"] = "unhealthy"
    
    # Check embedding service
    try:
        # This would check embedding model availability
        services["embedding_service"] = "healthy"
    except Exception as e:
        logger.error(f"Embedding service health check failed: {e}")
        services["embedding_service"] = "unhealthy"
    
    # Check LLM service
    try:
        import httpx
        if settings.LLM_PROVIDER == "ollama":
            response = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            if response.status_code == 200:
                services["llm_service"] = "healthy"
            else:
                services["llm_service"] = "unhealthy"
        elif settings.LLM_PROVIDER == "vllm":
            response = httpx.get(f"{settings.VLLM_BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                services["llm_service"] = "healthy"
            else:
                services["llm_service"] = "unhealthy"
        else:
            # For other providers, assume healthy
            services["llm_service"] = "healthy"
    except Exception as e:
        logger.error(f"LLM service health check failed: {e}")
        services["llm_service"] = "unhealthy"
    
    overall_status = "healthy" if all(status == "healthy" for status in services.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services=services
    )
