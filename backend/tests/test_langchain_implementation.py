"""
Comprehensive tests for LangChain implementation
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Import the services to test
from services.langchain_rag_service import LangChainRAGService
from langchain_services.agents import (
    MultiHopReasoningAgent,
    SelfConsistencyAgent,
    QueryPlannerAgent
)
from langchain_services.utils import (
    PromptTemplates,
    ResponseFormatter,
    PerformanceMonitor,
    ValidationUtils
)
from langchain_services.document_processing import (
    MultiFormatDocumentLoader,
    HybridTextSplitter,
    EmbeddingManager
)
from langchain_services.vector_stores import TenantAwareFAISSStore
from langchain_services.chains import AdvancedRAGChain

class TestLangChainRAGService:
    """Test the main LangChain RAG service"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing"""
        return {
            "llm_provider": "ollama",
            "llm_model": "llama2",
            "ollama_base_url": "http://localhost:11434",
            "embedding_provider": "huggingface",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "vector_store_path": "./test_vector_stores",
            "max_hops": 3,
            "self_consistency_samples": 3,
            "temperature": 0.7
        }
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value="Test response")
        return mock_llm
    
    @pytest.fixture
    def mock_embedding_manager(self):
        """Mock embedding manager"""
        mock_embedder = Mock()
        mock_embedder.embed_query = Mock(return_value=[0.1] * 384)
        mock_embedder.embed_documents = Mock(return_value=[[0.1] * 384])
        mock_embedder.get_embedding_dimension = Mock(return_value=384)
        
        mock_manager = Mock()
        mock_manager.embedder = mock_embedder
        mock_manager.health_check = Mock(return_value=True)
        mock_manager.get_model_info = Mock(return_value={"provider": "huggingface"})
        
        return mock_manager
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store"""
        mock_store = Mock()
        mock_store.add_documents = Mock(return_value=["doc1", "doc2"])
        mock_store.similarity_search = Mock(return_value=[])
        mock_store.similarity_search_with_score = Mock(return_value=[])
        mock_store.as_retriever = Mock(return_value=Mock())
        mock_store.get_tenant_stats = Mock(return_value={"document_count": 0})
        mock_store.list_tenants = Mock(return_value=["tenant1"])
        mock_store.health_check = Mock(return_value=True)
        
        return mock_store
    
    @pytest.fixture
    def mock_rag_chain(self):
        """Mock RAG chain"""
        mock_chain = Mock()
        mock_chain.query = Mock(return_value={
            "answer": "Test answer",
            "sources": [],
            "confidence": 0.8
        })
        mock_chain.health_check = Mock(return_value=True)
        
        return mock_chain
    
    @pytest.fixture
    def rag_service(self, mock_config, mock_llm, mock_embedding_manager, mock_vector_store, mock_rag_chain):
        """Create RAG service with mocked dependencies"""
        with patch('services.langchain_rag_service.ChatOllama', return_value=mock_llm), \
             patch('services.langchain_rag_service.EmbeddingManager', return_value=mock_embedding_manager), \
             patch('services.langchain_rag_service.TenantAwareFAISSStore', return_value=mock_vector_store), \
             patch('services.langchain_rag_service.AdvancedRAGChain', return_value=mock_rag_chain), \
             patch('services.langchain_rag_service.MultiHopReasoningAgent'), \
             patch('services.langchain_rag_service.SelfConsistencyAgent'), \
             patch('services.langchain_rag_service.QueryPlannerAgent'):
            
            service = LangChainRAGService(mock_config)
            return service
    
    @pytest.mark.asyncio
    async def test_process_document_success(self, rag_service):
        """Test successful document processing"""
        content = b"Test document content"
        file_type = "txt"
        tenant_id = "test_tenant"
        
        result = await rag_service.process_document(content, file_type, tenant_id)
        
        assert result["status"] == "success"
        assert result["tenant_id"] == tenant_id
        assert "chunks_created" in result
    
    @pytest.mark.asyncio
    async def test_process_document_unsupported_type(self, rag_service):
        """Test document processing with unsupported file type"""
        content = b"Test content"
        file_type = "unsupported"
        tenant_id = "test_tenant"
        
        result = await rag_service.process_document(content, file_type, tenant_id)
        
        assert result["status"] == "error"
        assert "Unsupported file type" in result["message"]
    
    @pytest.mark.asyncio
    async def test_process_query_simple(self, rag_service):
        """Test simple query processing"""
        question = "What is the capital of France?"
        tenant_id = "test_tenant"
        
        result = await rag_service.process_query(question, tenant_id)
        
        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert result["metadata"]["tenant_id"] == tenant_id
    
    @pytest.mark.asyncio
    async def test_process_query_with_options(self, rag_service):
        """Test query processing with options"""
        question = "What is machine learning?"
        tenant_id = "test_tenant"
        options = {
            "top_k": 10,
            "use_conversational": False,
            "use_multi_hop": True
        }
        
        result = await rag_service.process_query(question, tenant_id, options)
        
        assert "answer" in result
        assert result["metadata"]["tenant_id"] == tenant_id
    
    def test_health_check(self, rag_service):
        """Test health check functionality"""
        health_status = rag_service.health_check()
        
        assert "overall" in health_status
        assert "components" in health_status
        assert "timestamp" in health_status
        assert health_status["service_type"] == "langchain_advanced_rag"
    
    def test_get_tenant_stats(self, rag_service):
        """Test getting tenant statistics"""
        tenant_id = "test_tenant"
        stats = rag_service.get_tenant_stats(tenant_id)
        
        assert "tenant_id" in stats
        assert "vector_store" in stats
        assert "embedding_info" in stats
        assert "llm_info" in stats
    
    def test_list_tenants(self, rag_service):
        """Test listing tenants"""
        tenants = rag_service.list_tenants()
        
        assert isinstance(tenants, list)
        assert "tenant1" in tenants

class TestMultiHopReasoningAgent:
    """Test the multi-hop reasoning agent"""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value="Test multi-hop response")
        return mock_llm
    
    @pytest.fixture
    def mock_retriever(self):
        """Mock retriever for testing"""
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents = Mock(return_value=[])
        return mock_retriever
    
    @pytest.fixture
    def agent(self, mock_llm, mock_retriever):
        """Create multi-hop agent with mocked dependencies"""
        with patch('langchain_services.agents.multi_hop_agent.create_react_agent'), \
             patch('langchain_services.agents.multi_hop_agent.AgentExecutor'):
            
            agent = MultiHopReasoningAgent(mock_llm, mock_retriever, max_hops=3)
            return agent
    
    @pytest.mark.asyncio
    async def test_process_query(self, agent):
        """Test query processing with multi-hop reasoning"""
        question = "What are the causes and effects of climate change?"
        tenant_id = "test_tenant"
        
        result = await agent.process_query(question, tenant_id)
        
        assert "answer" in result
        assert "reasoning_steps" in result
        assert "hop_count" in result
        assert "confidence" in result
        assert result["metadata"]["agent_type"] == "multi_hop"
    
    def test_health_check(self, agent):
        """Test health check"""
        health = agent.health_check()
        assert isinstance(health, bool)

class TestSelfConsistencyAgent:
    """Test the self-consistency agent"""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value="Reasoning: Test reasoning\nAnswer: Test answer")
        return mock_llm
    
    @pytest.fixture
    def agent(self, mock_llm):
        """Create self-consistency agent with mocked LLM"""
        agent = SelfConsistencyAgent(mock_llm, num_samples=3, temperature=0.7)
        return agent
    
    @pytest.mark.asyncio
    async def test_generate_multiple_traces(self, agent):
        """Test generating multiple reasoning traces"""
        question = "What is the meaning of life?"
        context = "Philosophical context"
        tenant_id = "test_tenant"
        
        traces = await agent.generate_multiple_traces(question, context, tenant_id)
        
        assert isinstance(traces, list)
        assert len(traces) <= 3  # Should not exceed num_samples
    
    @pytest.mark.asyncio
    async def test_find_consensus(self, agent):
        """Test finding consensus among traces"""
        traces = [
            {"answer": "Answer A", "confidence": 0.8},
            {"answer": "Answer A", "confidence": 0.9},
            {"answer": "Answer B", "confidence": 0.7}
        ]
        
        consensus = await agent.find_consensus(traces)
        
        assert "consensus_answer" in consensus
        assert "consensus_confidence" in consensus
        assert "agreement_score" in consensus
        assert consensus["traces_analyzed"] == 3
    
    @pytest.mark.asyncio
    async def test_process_with_consistency(self, agent):
        """Test processing with self-consistency"""
        question = "What is artificial intelligence?"
        context = "AI context"
        tenant_id = "test_tenant"
        
        result = await agent.process_with_consistency(question, context, tenant_id)
        
        assert "answer" in result
        assert "reasoning" in result
        assert "confidence" in result
        assert "agreement_score" in result
        assert result["metadata"]["agent_type"] == "self_consistency"
    
    def test_health_check(self, agent):
        """Test health check"""
        health = agent.health_check()
        assert isinstance(health, bool)

class TestQueryPlannerAgent:
    """Test the query planner agent"""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value="Sub-query 1: What is X?\nType: retrieval\nPriority: 1\nDependencies: none")
        return mock_llm
    
    @pytest.fixture
    def agent(self, mock_llm):
        """Create query planner agent with mocked LLM"""
        agent = QueryPlannerAgent(mock_llm)
        return agent
    
    @pytest.mark.asyncio
    async def test_analyze_query_complexity(self, agent):
        """Test query complexity analysis"""
        question = "What are the causes and effects of climate change, and how do they compare?"
        
        complexity = await agent.analyze_query_complexity(question)
        
        assert "complexity_score" in complexity
        assert "complexity_level" in complexity
        assert "indicators" in complexity
        assert "requires_multi_hop" in complexity
        assert complexity["complexity_level"] in ["low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_decompose_query(self, agent):
        """Test query decomposition"""
        question = "What are the causes and effects of climate change?"
        
        sub_queries = await agent.decompose_query(question)
        
        assert isinstance(sub_queries, list)
        assert len(sub_queries) > 0
        assert all("sub_query" in sq for sq in sub_queries)
        assert all("query_type" in sq for sq in sub_queries)
        assert all("priority" in sq for sq in sub_queries)
    
    @pytest.mark.asyncio
    async def test_plan_query_execution(self, agent):
        """Test query execution planning"""
        question = "What are the causes and effects of climate change?"
        
        plan = await agent.plan_query_execution(question)
        
        assert "original_question" in plan
        assert "complexity_analysis" in plan
        assert "sub_queries" in plan
        assert "execution_plan" in plan
        assert "estimated_execution_time" in plan
    
    def test_health_check(self, agent):
        """Test health check"""
        health = agent.health_check()
        assert isinstance(health, bool)

class TestUtilityClasses:
    """Test utility classes"""
    
    def test_prompt_templates(self):
        """Test prompt templates"""
        templates = PromptTemplates()
        
        # Test getting QA prompt
        qa_prompt = templates.get_qa_prompt()
        assert qa_prompt is not None
        assert "context" in qa_prompt.input_variables
        assert "question" in qa_prompt.input_variables
        
        # Test getting prompt by type
        conversational_prompt = templates.get_prompt_by_type("conversational")
        assert conversational_prompt is not None
        
        # Test custom prompt
        custom_prompt = templates.get_custom_prompt("Test {input}", ["input"])
        assert custom_prompt is not None
    
    def test_response_formatter(self):
        """Test response formatter"""
        formatter = ResponseFormatter()
        
        # Test RAG response formatting
        rag_result = {
            "answer": "Test answer",
            "sources": [],
            "confidence": 0.8
        }
        
        formatted = formatter.format_rag_response(rag_result, "test_tenant")
        assert "answer" in formatted
        assert "sources" in formatted
        assert "confidence" in formatted
        assert "metadata" in formatted
        assert formatted["metadata"]["tenant_id"] == "test_tenant"
    
    def test_performance_monitor(self):
        """Test performance monitor"""
        monitor = PerformanceMonitor()
        
        # Test monitoring lifecycle
        monitor.start_monitoring()
        monitor.add_operation("test_op", 1.5, {"test": "data"})
        monitor.stop_monitoring()
        
        metrics = monitor.get_metrics()
        assert "operations" in metrics
        assert len(metrics["operations"]) == 1
        assert metrics["operations"][0]["name"] == "test_op"
        
        summary = monitor.get_summary()
        assert "total_operations" in summary
        assert summary["total_operations"] == 1
    
    def test_validation_utils(self):
        """Test validation utilities"""
        validator = ValidationUtils()
        
        # Test tenant ID validation
        assert validator.validate_tenant_id("valid_tenant_123") == True
        assert validator.validate_tenant_id("invalid@tenant") == False
        assert validator.validate_tenant_id("") == False
        
        # Test question validation
        question_result = validator.validate_question("What is AI?")
        assert question_result["valid"] == True
        
        invalid_question = validator.validate_question("")
        assert invalid_question["valid"] == False
        
        # Test config validation
        valid_config = {
            "llm_provider": "ollama",
            "embedding_provider": "huggingface",
            "chunk_size": 1000,
            "temperature": 0.7
        }
        
        config_result = validator.validate_config(valid_config)
        assert config_result["valid"] == True

class TestDocumentProcessing:
    """Test document processing components"""
    
    def test_multi_format_loader(self):
        """Test multi-format document loader"""
        loader = MultiFormatDocumentLoader()
        
        # Test supported formats
        assert loader.is_supported("pdf") == True
        assert loader.is_supported("docx") == True
        assert loader.is_supported("txt") == True
        assert loader.is_supported("unsupported") == False
        
        # Test getting supported formats
        formats = loader.get_supported_formats()
        assert isinstance(formats, list)
        assert "pdf" in formats
    
    def test_hybrid_text_splitter(self):
        """Test hybrid text splitter"""
        splitter = HybridTextSplitter(chunk_size=100, chunk_overlap=20)
        
        # Test text splitting
        text = "This is a test document. " * 10  # Create long text
        chunks = splitter.split_text(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should be split into multiple chunks
        
        # Test chunk stats
        from langchain.schema import Document
        docs = [Document(page_content=chunk) for chunk in chunks]
        stats = splitter.get_chunk_stats(docs)
        
        assert "total_chunks" in stats
        assert "avg_chunk_size" in stats
        assert stats["total_chunks"] == len(chunks)

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_document_processing(self):
        """Test end-to-end document processing"""
        # This would test the full pipeline from document upload to query processing
        # For now, we'll create a simplified test
        
        config = {
            "llm_provider": "ollama",
            "llm_model": "llama2",
            "embedding_provider": "huggingface",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "chunk_size": 100,
            "chunk_overlap": 20,
            "vector_store_path": "./test_vector_stores"
        }
        
        # Mock all external dependencies
        with patch('services.langchain_rag_service.ChatOllama'), \
             patch('services.langchain_rag_service.EmbeddingManager'), \
             patch('services.langchain_rag_service.TenantAwareFAISSStore'), \
             patch('services.langchain_rag_service.AdvancedRAGChain'), \
             patch('services.langchain_rag_service.MultiHopReasoningAgent'), \
             patch('services.langchain_rag_service.SelfConsistencyAgent'), \
             patch('services.langchain_rag_service.QueryPlannerAgent'):
            
            service = LangChainRAGService(config)
            
            # Test document processing
            content = b"Test document content for processing"
            result = await service.process_document(content, "txt", "test_tenant")
            
            assert result["status"] == "success"
            assert result["tenant_id"] == "test_tenant"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling across the system"""
        config = {
            "llm_provider": "invalid_provider",
            "embedding_provider": "huggingface"
        }
        
        # This should raise an error during initialization
        with pytest.raises(Exception):
            LangChainRAGService(config)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
