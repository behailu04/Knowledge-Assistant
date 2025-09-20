# Knowledge Assistant Backend

This is the backend service for the Knowledge Assistant application. For the complete project documentation, see the [main README](../README.md).

## Quick Start

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables:
   ```bash
   cp ../env.example .env
   # Edit .env with your configuration
   ```

3. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once running, visit:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

## Architecture

The backend is built with:
- **FastAPI** for the web framework
- **LangChain** for RAG and agent orchestration
- **FAISS** for vector storage
- **PostgreSQL** for metadata storage
- **Redis** for caching

For detailed information about the full system architecture and features, see the [main project README](../README.md).
