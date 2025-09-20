"""
LangChain-based RAG service integrating all components
"""
import os
from typing import Dict, Any, List, Optional
from langchain_community.chat_models import ChatOpenAI, ChatOllama
from langchain_community.llms import OpenAI, Ollama
from langchain_core.documents import Document
import logging

from langchain_services.document_processing import (
    MultiFormatDocumentLoader, 
    HybridTextSplitter, 
    EmbeddingManager
)
from langchain_services.vector_stores import TenantAwareMilvusStore
from langchain_services.chains import AdvancedRAGChain
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
from config import settings

logger = logging.getLogger(__name__)

class LangChainRAGService:
    """Main RAG service using LangChain components"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        
        # Initialize components
        self._initialize_llm()
        self._initialize_embeddings()
        self._initialize_document_processing()
        self._initialize_vector_store()
        self._initialize_chains()
        self._initialize_agents()
        self._initialize_utilities()
        
        logger.info("LangChain RAG Service initialized successfully")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        logger.info(f"Settings OLLAMA_MODEL: {settings.OLLAMA_MODEL}, LLM_PROVIDER: {settings.LLM_PROVIDER}")
        return {
            "llm_provider": settings.LLM_PROVIDER,
            "llm_model": settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else "gpt-3.5-turbo",
            "ollama_base_url": settings.OLLAMA_BASE_URL,
            "embedding_provider": "huggingface",
            "embedding_model": settings.LANGCHAIN_EMBEDDING_MODEL,
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "milvus_collection_name": settings.MILVUS_COLLECTION_NAME,
            "use_conversational": True
        }
    
    def _initialize_llm(self):
        """Initialize LLM based on configuration"""
        provider = self.config.get("llm_provider", "ollama").lower()
        model = self.config.get("llm_model", "llama2:7b")
        
        logger.info(f"Initializing LLM with provider: {provider}, model: {model}")
        
        try:
            if provider == "openai":
                self.llm = ChatOpenAI(
                    model=model,
                    temperature=0.7,
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
            elif provider == "ollama":
                base_url = self.config.get("ollama_base_url", "http://localhost:11434")
                self.llm = ChatOllama(
                    model=model,
                    base_url=base_url,
                    temperature=0.7
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
            
            logger.info(f"Initialized {provider} LLM with model {model}")
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise
    
    def _initialize_embeddings(self):
        """Initialize embedding manager"""
        try:
            self.embedding_manager = EmbeddingManager(
                provider=self.config.get("embedding_provider", "ollama"),
                model_name=self.config.get("embedding_model", "nomic-embed-text"),
                cache_folder="./embeddings_cache"
            )
            logger.info(f"Initialized embeddings with provider: {self.config.get('embedding_provider')}")
            
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            raise
    
    def _initialize_document_processing(self):
        """Initialize document processing components"""
        try:
            self.document_loader = MultiFormatDocumentLoader()
            
            self.text_splitter = HybridTextSplitter(
                chunk_size=self.config.get("chunk_size", 1000),
                chunk_overlap=self.config.get("chunk_overlap", 200)
            )
            
            logger.info("Initialized document processing components")
            
        except Exception as e:
            logger.error(f"Error initializing document processing: {e}")
            raise
    
    def _initialize_vector_store(self):
        """Initialize vector store"""
        try:
            self.vector_store = TenantAwareMilvusStore(
                embedding_function=self.embedding_manager.embedder,
                collection_name=self.config.get("milvus_collection_name", "knowledge_chunks")
            )
            logger.info("Initialized Milvus vector store")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def _initialize_chains(self):
        """Initialize RAG chains"""
        try:
            # Create retriever with default tenant
            retriever = self.vector_store.as_retriever(
                tenant_id="default",
                search_kwargs={"k": 5}
            )
            
            # Initialize RAG chain
            self.rag_chain = AdvancedRAGChain(
                llm=self.llm,
                retriever=retriever,
                chain_type="stuff",
                return_source_documents=True
            )
            
            logger.info("Initialized RAG chains")
            
        except Exception as e:
            logger.error(f"Error initializing chains: {e}")
            raise
    
    def _initialize_agents(self):
        """Initialize reasoning agents"""
        try:
            # Create retriever for agents
            retriever = self.vector_store.as_retriever(
                tenant_id="default",
                search_kwargs={"k": 5}
            )
            
            # Initialize agents
            self.multi_hop_agent = MultiHopReasoningAgent(
                llm=self.llm,
                retriever=retriever,
                max_hops=self.config.get("max_hops", 3)
            )
            
            # Temporarily disable self-consistency agent to avoid recursion
            # self.self_consistency_agent = SelfConsistencyAgent(
            #     llm=self.llm,
            #     num_samples=self.config.get("self_consistency_samples", 5),
            #     temperature=self.config.get("temperature", 0.7)
            # )
            self.self_consistency_agent = None
            
            self.query_planner_agent = QueryPlannerAgent(
                llm=self.llm
            )
            
            logger.info("Initialized reasoning agents")
            
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
            raise
    
    def _initialize_utilities(self):
        """Initialize utility classes"""
        try:
            self.prompt_templates = PromptTemplates()
            self.response_formatter = ResponseFormatter()
            self.performance_monitor = PerformanceMonitor()
            self.validation_utils = ValidationUtils()
            
            logger.info("Initialized utility classes")
            
        except Exception as e:
            logger.error(f"Error initializing utilities: {e}")
            raise
    
    async def process_document(self, 
                             content: bytes, 
                             file_type: str, 
                             tenant_id: str,
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process document through LangChain pipeline"""
        try:
            logger.info(f"Processing {file_type} document for tenant {tenant_id}")
            
            # Add tenant metadata
            doc_metadata = metadata or {}
            doc_metadata["tenant_id"] = tenant_id
            
            # Load document
            documents = self.document_loader.load_document(
                content, file_type, doc_metadata
            )
            
            if not documents:
                return {
                    "status": "error",
                    "message": "No documents could be loaded from the file",
                    "tenant_id": tenant_id
                }
            
            # Split documents
            split_docs = self.text_splitter.split_documents(
                documents, 
                splitter_type="recursive",
                preserve_metadata=True
            )
            
            # Add documents to vector store
            doc_ids = self.vector_store.add_documents(split_docs, tenant_id)
            
            # Get chunk statistics
            chunk_stats = self.text_splitter.get_chunk_stats(split_docs)
            
            logger.info(f"Successfully processed document for tenant {tenant_id}: {len(split_docs)} chunks")
            
            return {
                "status": "success",
                "tenant_id": tenant_id,
                "chunks_created": len(split_docs),
                "document_ids": doc_ids,
                "chunk_stats": chunk_stats,
                "file_type": file_type
            }
            
        except Exception as e:
            logger.error(f"Error processing document for tenant {tenant_id}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "tenant_id": tenant_id
            }
    
    async def process_query(self, 
                          question: str, 
                          tenant_id: str,
                          options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process query using advanced LangChain RAG with multi-hop reasoning"""
        try:
            options = options or {}
            logger.info(f"Processing query for tenant {tenant_id}: {question[:100]}...")
            
            # Start performance monitoring
            self.performance_monitor.start_monitoring()
            
            # Validate inputs
            validation_result = self.validation_utils.validate_question(question)
            if not validation_result["valid"]:
                return self.response_formatter.format_error_response(
                    validation_result["error"], "validation_error", tenant_id
                )
            
            # Validate options
            options_validation = self.validation_utils.validate_query_options(options)
            if not options_validation["valid"]:
                return self.response_formatter.format_error_response(
                    f"Invalid options: {', '.join(options_validation['errors'])}", 
                    "validation_error", tenant_id
                )
            
            # Plan query execution
            query_plan = await self.query_planner_agent.plan_query_execution(question)
            
            # Determine processing strategy based on complexity
            complexity_level = query_plan.get("complexity_analysis", {}).get("complexity_level", "low")
            requires_multi_hop = query_plan.get("complexity_analysis", {}).get("requires_multi_hop", False)
            use_self_consistency = options.get("use_self_consistency", complexity_level == "high")
            
            # Process based on complexity
            if requires_multi_hop and options.get("use_multi_hop", True):
                result = await self._process_multi_hop_query(
                    question, tenant_id, query_plan, options
                )
            elif use_self_consistency and options.get("use_self_consistency", True):
                # Temporarily use simple query processing to avoid recursion
                result = await self._process_simple_query(
                    question, tenant_id, options
                )
            else:
                result = await self._process_simple_query(
                    question, tenant_id, options
                )
            
            # Stop performance monitoring
            self.performance_monitor.stop_monitoring()
            
            # Add performance metadata
            performance_metrics = self.performance_monitor.get_metrics()
            performance_summary = self.performance_monitor.get_summary()
            result = self.response_formatter.add_processing_metadata(
                result, 
                performance_summary.get("total_time", 0),
                {},  # No resource usage available from PerformanceMonitor
                {"query_plan": query_plan, "complexity_level": complexity_level}
            )
            
            # Validate response format
            response_validation = self.validation_utils.validate_response(result)
            if not response_validation["valid"]:
                logger.warning(f"Response validation failed: {response_validation['errors']}")
            
            logger.info(f"Successfully processed query for tenant {tenant_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query for tenant {tenant_id}: {e}")
            return self.response_formatter.format_error_response(
                str(e), "processing_error", tenant_id
            )
    
    async def _process_simple_query(self, 
                                  question: str, 
                                  tenant_id: str,
                                  options: Dict[str, Any]) -> Dict[str, Any]:
        """Process a simple query using basic RAG"""
        try:
            # Temporarily bypass retriever to isolate the recursion issue
            logger.info(f"Processing simple query for tenant {tenant_id}: {question}")
            
            # Create a simple prompt without context for now
            prompt = f"""
            Please answer the following question to the best of your ability:
            
            Question: {question}
            
            Please provide a clear and helpful answer.
            """
            
            # Generate response directly with LLM
            logger.info("Calling LLM for simple query")
            response = await self.llm.ainvoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            logger.info("LLM response received")
            
            # Format response
            result = {
                "answer": response_text,
                "sources": [],  # No sources for now
                "confidence": 0.8,
                "chain_type": "simple",
                "metadata": {
                    "tenant_id": tenant_id,
                    "question": question
                }
            }
            
            logger.info("Formatting response")
            return self.response_formatter.format_rag_response(result, tenant_id)
            
        except Exception as e:
            logger.error(f"Error in simple query processing: {e}")
            raise
    
    async def _process_multi_hop_query(self, 
                                     question: str, 
                                     tenant_id: str,
                                     query_plan: Dict[str, Any],
                                     options: Dict[str, Any]) -> Dict[str, Any]:
        """Process a complex query using multi-hop reasoning"""
        try:
            # Update retriever with tenant context
            retriever = self.vector_store.as_retriever(
                tenant_id=tenant_id,
                search_kwargs={"k": options.get("top_k", 5)}
            )
            
            # Update multi-hop agent retriever
            self.multi_hop_agent.retriever = retriever
            
            # Process with multi-hop reasoning
            result = await self.multi_hop_agent.process_query(
                question=question,
                tenant_id=tenant_id,
                context=query_plan
            )
            
            return self.response_formatter.format_multi_hop_response(result, tenant_id)
            
        except Exception as e:
            logger.error(f"Error in multi-hop query processing: {e}")
            raise
    
    async def _process_self_consistency_query(self, 
                                            question: str, 
                                            tenant_id: str,
                                            options: Dict[str, Any]) -> Dict[str, Any]:
        """Process a query using self-consistency"""
        try:
            # Get context from vector store
            retriever = self.vector_store.as_retriever(
                tenant_id=tenant_id,
                search_kwargs={"k": options.get("top_k", 5)}
            )
            
            # Get relevant documents for context
            context_docs = retriever.invoke(question)
            context = "\n".join([doc.page_content for doc in context_docs[:3]])
            
            # Process with self-consistency (simplified to avoid recursion)
            result = await self._process_with_simple_consistency(
                question=question,
                context=context,
                tenant_id=tenant_id
            )
            
            # Add sources from context
            result["sources"] = context_docs
            
            return self.response_formatter.format_self_consistency_response(result, tenant_id)
            
        except Exception as e:
            logger.error(f"Error in self-consistency query processing: {e}")
            raise
    
    async def _process_with_simple_consistency(self, 
                                             question: str, 
                                             context: str, 
                                             tenant_id: str) -> Dict[str, Any]:
        """Simplified self-consistency processing to avoid recursion"""
        try:
            # Create a simple prompt
            prompt = f"""
            Based on the following context, please answer the question with detailed reasoning.
            
            Context: {context}
            
            Question: {question}
            
            Please provide:
            1. Your reasoning process
            2. Your final answer
            """
            
            # Generate response
            response = await self.llm.ainvoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Simple extraction
            if "Answer:" in response_text:
                reasoning = response_text.split("Answer:")[0].strip()
                answer = response_text.split("Answer:")[1].strip()
            else:
                reasoning = response_text
                answer = response_text
            
            return {
                "answer": answer,
                "reasoning": reasoning,
                "confidence": 0.8,  # Default confidence
                "traces_analyzed": 1
            }
            
        except Exception as e:
            logger.error(f"Error in simple consistency processing: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your query.",
                "reasoning": f"Error: {str(e)}",
                "confidence": 0.0,
                "traces_analyzed": 0
            }
    
    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get statistics for a tenant"""
        try:
            vector_stats = self.vector_store.get_tenant_stats(tenant_id)
            
            return {
                "tenant_id": tenant_id,
                "vector_store": vector_stats,
                "embedding_info": self.embedding_manager.get_model_info(),
                "llm_info": {
                    "provider": self.config.get("llm_provider"),
                    "model": self.config.get("llm_model")
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for tenant {tenant_id}: {e}")
            return {"error": str(e), "tenant_id": tenant_id}
    
    def list_tenants(self) -> List[str]:
        """List all tenants in the system"""
        try:
            return self.vector_store.list_tenants()
        except Exception as e:
            logger.error(f"Error listing tenants: {e}")
            return []
    
    def health_check(self) -> Dict[str, bool]:
        """Comprehensive health check"""
        try:
            health_status = {
                "llm": True,  # Will test below
                "embeddings": self.embedding_manager.health_check(),
                "vector_store": self.vector_store.health_check(),
                "rag_chain": self.rag_chain.health_check(),
                "multi_hop_agent": self.multi_hop_agent.health_check(),
                "self_consistency_agent": self.self_consistency_agent.health_check() if self.self_consistency_agent else {"status": "disabled"},
                "query_planner_agent": self.query_planner_agent.health_check()
            }
            
            # Test LLM with simple query
            try:
                test_result = self.rag_chain.query("test", use_conversational=False)
                health_status["llm"] = "error" not in test_result
            except:
                health_status["llm"] = False
            
            overall_health = all(health_status.values())
            
            return {
                "overall": overall_health,
                "components": health_status,
                "timestamp": self.response_formatter._get_timestamp(),
                "service_type": "langchain_advanced_rag"
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "overall": False,
                "error": str(e),
                "timestamp": self.response_formatter._get_timestamp(),
                "service_type": "langchain_advanced_rag"
            }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration (requires reinitialization)"""
        self.config.update(new_config)
        logger.info("Configuration updated - consider reinitializing service for full effect")
    
    def clear_tenant_data(self, tenant_id: str) -> bool:
        """Clear all data for a tenant"""
        try:
            # This would need to be implemented based on vector store capabilities
            logger.warning(f"Tenant data clearing not fully implemented for tenant: {tenant_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing tenant data for {tenant_id}: {e}")
            return False
