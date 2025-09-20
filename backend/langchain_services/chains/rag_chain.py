"""
Advanced RAG chain using LangChain
"""
from typing import Dict, Any, List, Optional
from langchain.chains import RetrievalQA
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class AdvancedRAGChain:
    """Advanced RAG chain with enhanced prompts and memory"""
    
    def __init__(self, 
                 llm: BaseLanguageModel,
                 retriever: BaseRetriever,
                 memory: Optional[ConversationalRetrievalChain] = None,
                 chain_type: str = "stuff",
                 return_source_documents: bool = True):
        
        self.llm = llm
        self.retriever = retriever
        self.chain_type = chain_type
        self.return_source_documents = return_source_documents
        
        # Initialize memory if not provided
        if memory is None:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        else:
            self.memory = memory
        
        # Create custom prompt template
        self.qa_prompt = self._create_qa_prompt()
        
        # Initialize retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type=chain_type,
            retriever=retriever,
            chain_type_kwargs={"prompt": self.qa_prompt},
            return_source_documents=return_source_documents,
            memory=self.memory if isinstance(self.memory, ConversationBufferMemory) else None
        )
        
        # Initialize conversational chain for chat-like interactions
        self.conversational_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=return_source_documents,
            combine_docs_chain_kwargs={"prompt": self.qa_prompt}
        )
    
    def _create_qa_prompt(self) -> PromptTemplate:
        """Create custom prompt template for QA"""
        template = """
        You are a helpful AI assistant with access to a knowledge base. Use the following pieces of context to answer the user's question accurately and comprehensively.

        Context:
        {context}

        Question: {question}

        Instructions:
        1. Answer the question based on the provided context
        2. If the context doesn't contain enough information to answer the question, say so clearly
        3. Include relevant citations or references to the source documents
        4. Be concise but complete in your response
        5. If you're uncertain about any part of your answer, indicate your confidence level

        Answer:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(self, 
              question: str, 
              tenant_id: str = None,
              use_conversational: bool = False,
              **kwargs) -> Dict[str, Any]:
        """
        Process a query and return response with sources
        
        Args:
            question: The question to answer
            tenant_id: Tenant ID for context (if needed)
            use_conversational: Whether to use conversational chain
            **kwargs: Additional arguments for the chain
        """
        try:
            # Add tenant context to retriever if supported
            if hasattr(self.retriever, 'tenant_id') and tenant_id:
                self.retriever.tenant_id = tenant_id
            
            # Choose appropriate chain
            if use_conversational:
                result = self.conversational_chain({
                    "question": question,
                    "chat_history": self.memory.chat_memory.messages if hasattr(self.memory, 'chat_memory') else []
                })
            else:
                result = self.qa_chain({"query": question})
            
            # Extract and format response
            response = {
                "answer": result.get("result", result.get("answer", "")),
                "sources": result.get("source_documents", []),
                "confidence": self._calculate_confidence(result),
                "chain_type": "conversational" if use_conversational else "qa",
                "metadata": {
                    "tenant_id": tenant_id,
                    "question": question
                }
            }
            
            logger.info(f"Processed query for tenant {tenant_id} using {response['chain_type']} chain")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your query. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e),
                "metadata": {"tenant_id": tenant_id, "question": question}
            }
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on retrieved sources and answer quality"""
        try:
            sources = result.get("source_documents", [])
            answer = result.get("result", result.get("answer", ""))
            
            # Base confidence on number of relevant sources
            source_confidence = min(len(sources) / 5.0, 1.0)  # Max confidence with 5+ sources
            
            # Adjust based on answer length and quality
            if len(answer) < 50:
                length_penalty = 0.7
            elif len(answer) > 500:
                length_penalty = 1.0
            else:
                length_penalty = 0.9
            
            # Check for uncertainty indicators in answer
            uncertainty_indicators = [
                "i don't know", "i'm not sure", "unclear", "uncertain",
                "cannot determine", "not enough information", "may be"
            ]
            
            uncertainty_penalty = 1.0
            answer_lower = answer.lower()
            for indicator in uncertainty_indicators:
                if indicator in answer_lower:
                    uncertainty_penalty *= 0.7
            
            final_confidence = source_confidence * length_penalty * uncertainty_penalty
            return round(min(max(final_confidence, 0.0), 1.0), 2)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default moderate confidence
    
    def add_documents(self, documents: List[Document], tenant_id: str = None):
        """Add documents to the retriever's underlying vector store"""
        try:
            if hasattr(self.retriever, 'vectorstore'):
                if hasattr(self.retriever.vectorstore, 'add_documents'):
                    if tenant_id and hasattr(self.retriever.vectorstore, 'add_documents'):
                        # Tenant-aware addition
                        self.retriever.vectorstore.add_documents(documents, tenant_id)
                    else:
                        self.retriever.vectorstore.add_documents(documents)
                    
                    logger.info(f"Added {len(documents)} documents to RAG chain")
                else:
                    logger.warning("Vector store doesn't support adding documents")
            else:
                logger.warning("Retriever doesn't have access to vector store")
                
        except Exception as e:
            logger.error(f"Error adding documents to RAG chain: {e}")
    
    def clear_memory(self):
        """Clear conversation memory"""
        if hasattr(self.memory, 'clear'):
            self.memory.clear()
            logger.info("Cleared RAG chain memory")
    
    def get_memory_state(self) -> Dict[str, Any]:
        """Get current memory state"""
        try:
            if hasattr(self.memory, 'chat_memory'):
                return {
                    "message_count": len(self.memory.chat_memory.messages),
                    "memory_type": type(self.memory).__name__
                }
            else:
                return {"memory_type": type(self.memory).__name__}
        except Exception as e:
            logger.error(f"Error getting memory state: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Check if RAG chain is healthy"""
        try:
            # Simple health check without running a query to avoid recursion
            return (
                self.llm is not None and 
                self.retriever is not None and 
                self.qa_chain is not None
            )
        except Exception as e:
            logger.error(f"RAG chain health check failed: {e}")
            return False
