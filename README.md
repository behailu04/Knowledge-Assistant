# Knowledge Assistant

An AI-powered knowledge assistant with multi-hop reasoning, self-consistency, and evidence-backed answers. Built with FastAPI backend and Next.js frontend.

## Features

- **Multi-hop Reasoning**: Complex queries broken down into sequential reasoning steps
- **Self-Consistency**: Multiple reasoning traces with consensus-based answers
- **Chain-of-Thought**: Step-by-step reasoning for complex problems
- **Evidence Verification**: Claims verified against source documents
- **Document Management**: Upload and process various document formats
- **Real-time Chat**: Interactive chat interface with source citations
- **Confidence Scoring**: Reliability metrics for all answers
- **Tenant Isolation**: Multi-tenant support with data isolation

## Architecture

```
[Documents] → [Ingestion] → [Chunking] → [Embedding] → [Vector Store]
                                                           ↓
[Query] → [Embedding] → [Retrieval] → [Reranking] → [LLM Orchestrator]
                                                           ↓
[Multi-hop Planning] → [Self-Consistency] → [Verification] → [Response]
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Ollama (for local LLM inference) - optional, can use external Ollama instance

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd knowledge-assistant
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Set up Ollama models (if using local Ollama)**
   ```bash
   # If you have Ollama running locally, pull the required models:
   ollama pull llama2:7b
   ollama pull llama2:13b
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Ollama API: http://localhost:11434

### Manual Setup

#### Backend Setup

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   # Start PostgreSQL and Redis
   # Update DATABASE_URL and REDIS_URL in .env
   ```

3. **Run the backend**
   ```bash
   uvicorn main:app --reload
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the frontend**
   ```bash
   npm run dev
   ```

## Usage

### Document Upload

1. Navigate to the Documents section
2. Drag and drop files or click to select
3. Supported formats: PDF, DOC, DOCX, TXT, MD
4. Documents are automatically processed and indexed

### Query Processing

1. Go to the Chat interface
2. Ask questions about your documents
3. Examples:
   - "What are the main points in the contract?"
   - "Which domains expire in the next 30 days?"
   - "Compare the terms in documents A and B"

### Multi-hop Reasoning

The system automatically detects complex queries and breaks them down:

1. **Query Planning**: Analyzes query complexity
2. **Subquery Generation**: Creates sequential reasoning steps
3. **Hop Execution**: Executes each step with context
4. **Result Aggregation**: Combines results from all hops
5. **Self-Consistency**: Generates multiple reasoning traces
6. **Consensus Building**: Aggregates answers for reliability

## API Reference

### Query Endpoint

```http
POST /api/v1/query
Content-Type: application/json

{
  "tenant_id": "org_123",
  "user_id": "u_456",
  "question": "Which domains expire in next 30 days and lack SSL?",
  "max_hops": 3,
  "options": {
    "use_cot": true,
    "self_consistency_samples": 5
  }
}
```

### Document Upload

```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

file: <file>
tenant_id: org_123
doc_type: pdf
language: en
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `LLM_PROVIDER`: LLM provider (ollama, openai)
- `OLLAMA_BASE_URL`: Ollama API URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Ollama model name (default: llama2)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `VECTOR_STORE_TYPE`: Vector store type (faiss, milvus, pinecone)
- `EMBEDDING_MODEL`: Sentence transformer model
- `MAX_HOPS`: Maximum reasoning hops (default: 3)
- `SELF_CONSISTENCY_SAMPLES`: Number of reasoning traces (default: 5)

### Model Configuration

- **Embedding Models**: sentence-transformers/all-MiniLM-L6-v2
- **LLM Models**: 
  - Ollama: llama2:7b, llama2:13b, codellama:7b, mistral:7b, neural-chat:7b
  - OpenAI: GPT-3.5-turbo, GPT-4
- **Vector Store**: FAISS (default), Milvus, Pinecone

## Development

### Project Structure

```
knowledge-assistant/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database models
│   ├── routers/               # API routes
│   ├── services/              # Core services
│   └── models/                # Pydantic schemas
├── frontend/
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   ├── context/               # React context providers
│   └── public/                # Static assets
├── docker-compose.yml         # Docker services
└── README.md                  # This file
```

### Adding New Features

1. **Backend Services**: Add new services in `backend/services/`
2. **API Routes**: Create new routers in `backend/routers/`
3. **Frontend Components**: Add components in `frontend/components/`
4. **Database Models**: Update models in `backend/database.py`

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Production Deployment

1. **Update environment variables**
   ```bash
   # Set production values
   DATABASE_URL=postgresql://user:pass@prod-db:5432/knowledge_assistant
   OPENAI_API_KEY=your_production_key
   SECRET_KEY=your_production_secret
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Set up SSL certificates**
   ```bash
   # Add certificates to ./ssl/ directory
   # Update nginx.conf for HTTPS
   ```

### Scaling Considerations

- **Horizontal Scaling**: Use load balancer with multiple backend instances
- **Vector Store**: Consider Milvus or Pinecone for large-scale deployments
- **Caching**: Implement Redis caching for frequent queries
- **Monitoring**: Add Prometheus metrics and Grafana dashboards

## Monitoring

### Health Checks

- Backend: `GET /api/v1/health`
- Frontend: `GET /`
- Database: PostgreSQL health check
- Redis: Redis ping check

### Metrics

- Query processing time
- Retrieval accuracy (Recall@k, nDCG)
- Confidence scores
- Error rates
- System resource usage

## Security

- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: Encryption at rest and in transit
- **Audit Logging**: Complete audit trail
- **Rate Limiting**: API rate limiting with Nginx
- **CORS**: Configured CORS policies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API reference

## Roadmap

- [ ] Advanced document formats (Excel, PowerPoint)
- [ ] Multi-language support
- [ ] Custom embedding models
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Enterprise SSO integration