"""
Knowledge Assistant - Main FastAPI Application (LangChain Only)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routers import documents, queries, health
from services.langchain_rag_service import LangChainRAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Knowledge Assistant with LangChain...")
    await init_db()
    
    # Initialize LangChain RAG service
    try:
        app.state.rag_service = LangChainRAGService()
        logger.info("LangChain RAG Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LangChain service: {e}")
        raise
    
    logger.info("Knowledge Assistant started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down Knowledge Assistant...")

# Create FastAPI app
app = FastAPI(
    title="Knowledge Assistant API",
    description="AI-powered knowledge assistant with multi-hop reasoning and self-consistency using LangChain",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(queries.router, prefix="/api/v1", tags=["queries"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Knowledge Assistant API",
        "version": "2.0.0",
        "status": "running",
        "architecture": "langchain",
        "service_type": "rag"
    }

@app.get("/api/v1/service/status")
async def get_service_status():
    """Get service status"""
    return {
        "service_type": "langchain",
        "status": "running",
        "version": "2.0.0",
        "architecture": "langchain-only",
        "features": [
            "multi-format-document-processing",
            "hybrid-text-splitting",
            "tenant-aware-vector-storage",
            "advanced-rag-chains",
            "multi-hop-reasoning",
            "self-consistency"
        ]
    }

@app.get("/api/v1/health/detailed")
async def detailed_health_check():
    """Detailed health check"""
    try:
        health_status = app.state.rag_service.health_check()
        
        return {
            "overall": health_status["overall"],
            "timestamp": "2024-01-17T22:00:00Z",  # Will be set by caller
            "service_type": "langchain",
            "components": health_status.get("components", {}),
            "tenants": app.state.rag_service.list_tenants()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "overall": False,
            "error": str(e),
            "service_type": "langchain"
        }

@app.get("/api/v1/config")
async def get_config():
    """Get current configuration"""
    try:
        config = app.state.rag_service.get_config()
        return {
            "config": config,
            "environment": {
                "use_langchain": settings.USE_LANGCHAIN,
                "llm_provider": settings.LANGCHAIN_LLM_PROVIDER,
                "embedding_provider": settings.LANGCHAIN_EMBEDDING_PROVIDER
            }
        }
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tenants")
async def list_tenants():
    """List all tenants"""
    try:
        tenants = app.state.rag_service.list_tenants()
        return {
            "tenants": tenants,
            "count": len(tenants)
        }
    except Exception as e:
        logger.error(f"Error listing tenants: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tenants/{tenant_id}/stats")
async def get_tenant_stats(tenant_id: str):
    """Get statistics for a specific tenant"""
    try:
        stats = app.state.rag_service.get_tenant_stats(tenant_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting stats for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )