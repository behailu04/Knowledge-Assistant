"""
Knowledge Assistant - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from config import settings
from database import get_db, init_db
from routers import documents, queries, health
from services.ingestion import IngestionService
from services.retrieval import RetrievalService
from services.llm_orchestrator import LLMOrchestrator
from models.schemas import QueryRequest, QueryResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Knowledge Assistant...")
    await init_db()
    
    # Initialize services
    app.state.ingestion_service = IngestionService()
    app.state.retrieval_service = RetrievalService()
    app.state.llm_orchestrator = LLMOrchestrator()
    
    logger.info("Knowledge Assistant started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down Knowledge Assistant...")

# Create FastAPI app
app = FastAPI(
    title="Knowledge Assistant API",
    description="AI-powered knowledge assistant with multi-hop reasoning and self-consistency",
    version="1.0.0",
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
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
