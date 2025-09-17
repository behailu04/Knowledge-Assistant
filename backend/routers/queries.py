"""
Query processing router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import time
from datetime import datetime

from database import get_db, Query
from models.schemas import QueryRequest, QueryResponse, ErrorResponse
from services.retrieval import RetrievalService
from services.llm_orchestrator import LLMOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Process a knowledge query with multi-hop reasoning"""
    start_time = time.time()
    
    try:
        # Initialize services
        retrieval_service = RetrievalService()
        llm_orchestrator = LLMOrchestrator()
        
        # Process the query
        result = await llm_orchestrator.process_query(
            question=request.question,
            tenant_id=request.tenant_id,
            max_hops=request.max_hops,
            options=request.options
        )
        
        processing_time = time.time() - start_time
        
        # Log the query
        query_record = Query(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            question=request.question,
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result["sources"],
            reasoning_traces=result["reasoning_traces"],
            processing_time=processing_time,
            hop_count=result["hop_count"]
        )
        
        db.add(query_record)
        db.commit()
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            reasoning_traces=result["reasoning_traces"],
            hop_count=result["hop_count"],
            processing_time=processing_time,
            query_id=str(query_record.query_id)
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/queries/{query_id}", response_model=QueryResponse)
async def get_query(query_id: str, db: Session = Depends(get_db)):
    """Get a specific query by ID"""
    query = db.query(Query).filter(Query.query_id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return QueryResponse(
        answer=query.answer,
        sources=query.sources or [],
        confidence=query.confidence or 0.0,
        reasoning_traces=query.reasoning_traces or [],
        hop_count=query.hop_count or 1,
        processing_time=query.processing_time or 0.0,
        query_id=str(query.query_id)
    )

@router.get("/queries")
async def list_queries(
    tenant_id: str,
    user_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List queries for a tenant/user"""
    query = db.query(Query).filter(Query.tenant_id == tenant_id)
    
    if user_id:
        query = query.filter(Query.user_id == user_id)
    
    queries = query.order_by(Query.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "query_id": str(q.query_id),
            "question": q.question,
            "answer": q.answer,
            "confidence": q.confidence,
            "created_at": q.created_at,
            "processing_time": q.processing_time,
            "hop_count": q.hop_count
        }
        for q in queries
    ]
