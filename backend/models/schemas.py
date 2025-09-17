"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ChunkResponse(BaseModel):
    """Chunk response schema"""
    chunk_id: str
    doc_id: str
    text: str
    start_pos: int
    end_pos: int
    heading: Optional[str] = None
    language: str = "en"
    entities: List[str] = []
    score: Optional[float] = None

class SourceResponse(BaseModel):
    """Source response schema"""
    doc_id: str
    chunk_id: str
    snippet: str
    score: float
    heading: Optional[str] = None

class ReasoningTrace(BaseModel):
    """Reasoning trace schema"""
    trace_id: str
    steps: List[str]
    vote_score: float
    reasoning: str

class QueryRequest(BaseModel):
    """Query request schema"""
    tenant_id: str
    user_id: str
    question: str
    max_hops: int = Field(default=3, ge=1, le=5)
    options: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "org_123",
                "user_id": "u_456",
                "question": "Which domains expire in next 30 days and lack SSL?",
                "max_hops": 3,
                "options": {
                    "use_cot": True,
                    "self_consistency_samples": 5
                }
            }
        }

class QueryResponse(BaseModel):
    """Query response schema"""
    answer: str
    sources: List[SourceResponse]
    confidence: float
    reasoning_traces: List[ReasoningTrace] = []
    hop_count: int = 1
    processing_time: float
    query_id: str

class DocumentUploadRequest(BaseModel):
    """Document upload request schema"""
    tenant_id: str
    doc_type: str
    language: str = "en"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentResponse(BaseModel):
    """Document response schema"""
    doc_id: str
    tenant_id: str
    original_path: str
    doc_type: str
    language: str
    uploaded_at: datetime
    is_processed: bool
    file_size: int
    metadata: Dict[str, Any]

class IngestionStatusResponse(BaseModel):
    """Ingestion status response schema"""
    doc_id: str
    status: str  # pending, processing, completed, failed
    message: Optional[str] = None
    chunks_created: int = 0
    processing_time: Optional[float] = None

class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str] = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
