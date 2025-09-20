# LangChain Implementation Guide

## Overview

This document describes the comprehensive LangChain implementation for the Knowledge Assistant, which provides advanced RAG (Retrieval-Augmented Generation) capabilities with multi-hop reasoning, self-consistency, and intelligent query planning.

## Architecture

### Core Components

1. **LangChainRAGService** - Main service orchestrating all components
2. **Document Processing** - Multi-format document loading and text splitting
3. **Vector Stores** - Tenant-aware FAISS vector storage
4. **Reasoning Agents** - Multi-hop reasoning, self-consistency, and query planning
5. **Utility Classes** - Prompt templates, response formatting, performance monitoring

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LangChainRAGService                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Document    │  │ Vector      │  │ Reasoning   │         │
│  │ Processing  │  │ Store       │  │ Agents      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Prompt      │  │ Response    │  │ Performance │         │
│  │ Templates   │  │ Formatters  │  │ Monitor     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Multi-Format Document Processing

- **Supported Formats**: PDF, DOCX, DOC, TXT, MD
- **Intelligent Chunking**: Hybrid text splitting with semantic awareness
- **Metadata Preservation**: Maintains document structure and context

### 2. Advanced Reasoning Capabilities

#### Multi-Hop Reasoning
- Decomposes complex queries into sub-questions
- Executes reasoning steps sequentially
- Builds context across multiple information sources

#### Self-Consistency
- Generates multiple reasoning traces
- Finds consensus among different approaches
- Provides confidence scores based on agreement

#### Query Planning
- Analyzes query complexity
- Determines optimal processing strategy
- Creates execution plans for complex queries

### 3. Tenant-Aware Architecture

- Complete data isolation between tenants
- Tenant-specific vector stores
- Configurable per-tenant settings

### 4. Performance Monitoring

- Real-time performance metrics
- Resource usage tracking
- Latency and throughput monitoring
- Comprehensive health checks

## Usage

### Basic Setup

```python
from services.langchain_rag_service import LangChainRAGService

# Initialize with default configuration
rag_service = LangChainRAGService()

# Or with custom configuration
config = {
    "llm_provider": "ollama",
    "llm_model": "llama2",
    "embedding_provider": "huggingface",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_hops": 3,
    "self_consistency_samples": 5
}

rag_service = LangChainRAGService(config)
```

### Document Processing

```python
# Process a document
content = b"Your document content here"
file_type = "pdf"
tenant_id = "your_tenant_id"

result = await rag_service.process_document(
    content=content,
    file_type=file_type,
    tenant_id=tenant_id,
    metadata={"source": "upload"}
)

print(f"Status: {result['status']}")
print(f"Chunks created: {result['chunks_created']}")
```

### Query Processing

```python
# Simple query
question = "What is machine learning?"
tenant_id = "your_tenant_id"

result = await rag_service.process_query(question, tenant_id)
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")

# Complex query with options
options = {
    "top_k": 10,
    "use_multi_hop": True,
    "use_self_consistency": True,
    "use_conversational": False
}

result = await rag_service.process_query(question, tenant_id, options)
```

### Advanced Query Processing

```python
# Multi-hop reasoning
options = {
    "use_multi_hop": True,
    "max_hops": 3
}

result = await rag_service.process_query(
    "What are the causes and effects of climate change?",
    tenant_id,
    options
)

# Self-consistency processing
options = {
    "use_self_consistency": True,
    "self_consistency_samples": 5
}

result = await rag_service.process_query(
    "Explain quantum computing",
    tenant_id,
    options
)
```

## Configuration

### Environment Variables

```bash
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Embedding Configuration
LANGCHAIN_EMBEDDING_PROVIDER=huggingface
LANGCHAIN_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Processing Configuration
LANGCHAIN_CHUNK_SIZE=1000
LANGCHAIN_CHUNK_OVERLAP=200
LANGCHAIN_VECTOR_STORE_PATH=./data/langchain_vector_stores

# Advanced Features
MAX_HOPS=3
SELF_CONSISTENCY_SAMPLES=5
TEMPERATURE=0.7
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `llm_provider` | string | "ollama" | LLM provider (ollama, openai) |
| `llm_model` | string | "llama2" | Model name |
| `embedding_provider` | string | "huggingface" | Embedding provider |
| `embedding_model` | string | "sentence-transformers/all-MiniLM-L6-v2" | Embedding model |
| `chunk_size` | int | 1000 | Text chunk size |
| `chunk_overlap` | int | 200 | Chunk overlap |
| `max_hops` | int | 3 | Maximum reasoning hops |
| `self_consistency_samples` | int | 5 | Number of consistency samples |
| `temperature` | float | 0.7 | LLM temperature |

## API Endpoints

### Document Management

```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

{
  "file": <file>,
  "tenant_id": "your_tenant_id",
  "doc_type": "pdf"
}
```

### Query Processing

```http
POST /api/v1/query
Content-Type: application/json

{
  "question": "What is artificial intelligence?",
  "tenant_id": "your_tenant_id",
  "user_id": "user123",
  "options": {
    "use_multi_hop": true,
    "use_self_consistency": true,
    "top_k": 10
  }
}
```

### Health Check

```http
GET /api/v1/health/detailed
```

### Tenant Statistics

```http
GET /api/v1/tenants/{tenant_id}/stats
```

## Advanced Features

### 1. Multi-Hop Reasoning

The system automatically detects complex queries and applies multi-hop reasoning:

```python
# Complex query that triggers multi-hop reasoning
question = "What are the environmental impacts of renewable energy adoption in developing countries, and how do they compare to fossil fuels?"

# The system will:
# 1. Decompose into sub-questions
# 2. Execute reasoning steps
# 3. Synthesize information
# 4. Provide comprehensive answer
```

### 2. Self-Consistency

For high-confidence answers, the system generates multiple reasoning traces:

```python
# Enable self-consistency
options = {
    "use_self_consistency": True,
    "self_consistency_samples": 5
}

result = await rag_service.process_query(question, tenant_id, options)

# Result includes:
# - consensus_answer
# - agreement_score
# - individual_traces
# - consensus_metadata
```

### 3. Query Planning

Intelligent query analysis and execution planning:

```python
# The system analyzes:
# - Query complexity
# - Required reasoning steps
# - Optimal processing strategy
# - Execution order

# Query complexity indicators:
# - Multi-part questions
# - Comparisons
# - Temporal elements
# - Conditional logic
# - Aggregation requirements
```

## Performance Monitoring

### Built-in Metrics

- **Processing Time**: Query and document processing duration
- **Resource Usage**: CPU and memory consumption
- **Throughput**: Operations per second
- **Latency**: Individual operation timing
- **Health Status**: Component availability

### Performance Reports

```python
# Get comprehensive performance report
performance_report = rag_service.performance_monitor.get_comprehensive_report()

print(f"Total operations: {performance_report['performance_summary']['total_operations']}")
print(f"Average time: {performance_report['performance_summary']['average_operation_time']}")
print(f"Memory usage: {performance_report['resource_usage']['memory']}")
```

## Error Handling

### Validation

All inputs are validated before processing:

```python
# Question validation
validation_result = rag_service.validation_utils.validate_question(question)
if not validation_result["valid"]:
    print(f"Error: {validation_result['error']}")

# Document validation
validation_result = rag_service.validation_utils.validate_document_content(content, file_type)
if not validation_result["valid"]:
    print(f"Error: {validation_result['error']}")
```

### Error Responses

Consistent error response format:

```python
{
    "answer": "Error message",
    "sources": [],
    "confidence": 0.0,
    "error": "Detailed error information",
    "error_type": "validation_error",
    "metadata": {
        "tenant_id": "tenant_id",
        "response_type": "error",
        "timestamp": "2024-01-17T22:00:00Z"
    }
}
```

## Testing

### Running Tests

```bash
# Run all tests
pytest backend/tests/test_langchain_implementation.py -v

# Run specific test categories
pytest backend/tests/test_langchain_implementation.py::TestLangChainRAGService -v
pytest backend/tests/test_langchain_implementation.py::TestMultiHopReasoningAgent -v
pytest backend/tests/test_langchain_implementation.py::TestSelfConsistencyAgent -v
```

### Test Coverage

The test suite covers:
- Service initialization and configuration
- Document processing pipeline
- Query processing with different strategies
- Agent functionality
- Utility classes
- Error handling
- Integration scenarios

## Troubleshooting

### Common Issues

1. **LLM Connection Issues**
   ```bash
   # Check Ollama is running
   curl http://localhost:11434/api/tags
   
   # Check model availability
   ollama list
   ```

2. **Embedding Model Issues**
   ```python
   # Test embedding generation
   embedding_manager = EmbeddingManager("huggingface")
   test_embedding = embedding_manager.embed_query("test")
   print(f"Embedding dimension: {len(test_embedding)}")
   ```

3. **Vector Store Issues**
   ```python
   # Check vector store health
   health_status = rag_service.vector_store.health_check()
   print(f"Vector store healthy: {health_status}")
   ```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific components
logger = logging.getLogger('langchain_services')
logger.setLevel(logging.DEBUG)
```

## Best Practices

### 1. Configuration Management

- Use environment variables for sensitive data
- Validate configuration before service initialization
- Monitor configuration changes

### 2. Error Handling

- Always validate inputs
- Implement proper error responses
- Log errors with context

### 3. Performance Optimization

- Monitor resource usage
- Tune chunk sizes for your use case
- Use appropriate reasoning strategies

### 4. Security

- Validate all inputs
- Sanitize user content
- Implement proper tenant isolation

## Future Enhancements

### Planned Features

1. **Advanced Agents**
   - Specialized domain agents
   - Custom reasoning strategies
   - Agent collaboration

2. **Enhanced Monitoring**
   - Real-time dashboards
   - Alert systems
   - Performance analytics

3. **Scalability Improvements**
   - Distributed processing
   - Load balancing
   - Caching strategies

4. **Additional Integrations**
   - More LLM providers
   - Advanced vector stores
   - External knowledge sources

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review test cases for examples
3. Check logs for detailed error information
4. Validate configuration and inputs

## License

This implementation is part of the Knowledge Assistant project and follows the same licensing terms.
