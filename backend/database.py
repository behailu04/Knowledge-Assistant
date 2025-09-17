"""
Database configuration and models
"""
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import Generator

from config import settings

# Database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    """Document metadata table"""
    __tablename__ = "documents"
    
    doc_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    original_path = Column(String(500), nullable=False)
    doc_type = Column(String(100), nullable=False)
    language = Column(String(10), default="en")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    checksum = Column(String(64), nullable=False)
    doc_metadata = Column(JSON, default=dict)
    is_processed = Column(Boolean, default=False)
    file_size = Column(Integer)
    created_by = Column(String(255))

class Chunk(Base):
    """Chunk metadata table"""
    __tablename__ = "chunks"
    
    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(String(255), nullable=False, index=True)
    text = Column(Text, nullable=False)
    start_pos = Column(Integer, nullable=False)
    end_pos = Column(Integer, nullable=False)
    heading = Column(String(500))
    language = Column(String(10), default="en")
    entities = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding_id = Column(String(255))  # Reference to vector store

class Query(Base):
    """Query log table"""
    __tablename__ = "queries"
    
    query_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    confidence = Column(Float)
    sources = Column(JSON, default=list)
    reasoning_traces = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # in seconds
    hop_count = Column(Integer, default=1)

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
