"""
Response formatting utilities for LangChain services
"""
from typing import Dict, Any, List, Optional
from langchain.schema import Document
import logging
import json

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Utility class for formatting responses from LangChain services"""
    
    @staticmethod
    def format_rag_response(result: Dict[str, Any], 
                          tenant_id: str = None,
                          include_metadata: bool = True) -> Dict[str, Any]:
        """Format a RAG response"""
        try:
            formatted = {
                "answer": result.get("answer", ""),
                "sources": ResponseFormatter._format_sources(result.get("sources", [])),
                "confidence": result.get("confidence", 0.0),
                "metadata": {
                    "tenant_id": tenant_id,
                    "response_type": "rag",
                    "timestamp": ResponseFormatter._get_timestamp()
                }
            }
            
            if include_metadata:
                formatted["metadata"].update(result.get("metadata", {}))
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting RAG response: {e}")
            return {
                "answer": "Error formatting response",
                "sources": [],
                "confidence": 0.0,
                "error": str(e),
                "metadata": {"tenant_id": tenant_id}
            }
    
    @staticmethod
    def format_multi_hop_response(result: Dict[str, Any],
                                tenant_id: str = None) -> Dict[str, Any]:
        """Format a multi-hop reasoning response"""
        try:
            formatted = {
                "answer": result.get("answer", ""),
                "reasoning_steps": result.get("reasoning_steps", []),
                "hop_count": result.get("hop_count", 0),
                "confidence": result.get("confidence", 0.0),
                "sources": ResponseFormatter._format_sources(result.get("sources", [])),
                "metadata": {
                    "tenant_id": tenant_id,
                    "response_type": "multi_hop",
                    "timestamp": ResponseFormatter._get_timestamp()
                }
            }
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting multi-hop response: {e}")
            return {
                "answer": "Error formatting multi-hop response",
                "reasoning_steps": [],
                "hop_count": 0,
                "confidence": 0.0,
                "sources": [],
                "error": str(e),
                "metadata": {"tenant_id": tenant_id}
            }
    
    @staticmethod
    def format_self_consistency_response(result: Dict[str, Any],
                                       tenant_id: str = None) -> Dict[str, Any]:
        """Format a self-consistency response"""
        try:
            formatted = {
                "answer": result.get("answer", ""),
                "reasoning": result.get("reasoning", ""),
                "confidence": result.get("confidence", 0.0),
                "agreement_score": result.get("agreement_score", 0.0),
                "traces_analyzed": result.get("traces_analyzed", 0),
                "individual_traces": result.get("individual_traces", []),
                "consensus_metadata": result.get("consensus_metadata", {}),
                "sources": ResponseFormatter._format_sources(result.get("sources", [])),
                "metadata": {
                    "tenant_id": tenant_id,
                    "response_type": "self_consistency",
                    "timestamp": ResponseFormatter._get_timestamp()
                }
            }
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting self-consistency response: {e}")
            return {
                "answer": "Error formatting self-consistency response",
                "reasoning": "",
                "confidence": 0.0,
                "agreement_score": 0.0,
                "traces_analyzed": 0,
                "individual_traces": [],
                "consensus_metadata": {},
                "sources": [],
                "error": str(e),
                "metadata": {"tenant_id": tenant_id}
            }
    
    @staticmethod
    def format_query_plan_response(result: Dict[str, Any],
                                 tenant_id: str = None) -> Dict[str, Any]:
        """Format a query planning response"""
        try:
            formatted = {
                "original_question": result.get("original_question", ""),
                "complexity_analysis": result.get("complexity_analysis", {}),
                "sub_queries": result.get("sub_queries", []),
                "execution_plan": result.get("execution_plan", []),
                "estimated_execution_time": result.get("estimated_execution_time", 0),
                "requires_parallel_execution": result.get("requires_parallel_execution", False),
                "metadata": {
                    "tenant_id": tenant_id,
                    "response_type": "query_plan",
                    "timestamp": ResponseFormatter._get_timestamp()
                }
            }
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting query plan response: {e}")
            return {
                "original_question": "",
                "complexity_analysis": {},
                "sub_queries": [],
                "execution_plan": [],
                "estimated_execution_time": 0,
                "requires_parallel_execution": False,
                "error": str(e),
                "metadata": {"tenant_id": tenant_id}
            }
    
    @staticmethod
    def _format_sources(sources: List[Any]) -> List[Dict[str, Any]]:
        """Format sources for consistent output"""
        formatted_sources = []
        
        for source in sources:
            if isinstance(source, Document):
                formatted_sources.append({
                    "content": source.page_content[:500] + "..." if len(source.page_content) > 500 else source.page_content,
                    "metadata": source.metadata,
                    "score": getattr(source, 'score', 0.0)
                })
            elif isinstance(source, dict):
                formatted_sources.append({
                    "content": source.get("content", "")[:500] + "..." if len(source.get("content", "")) > 500 else source.get("content", ""),
                    "metadata": source.get("metadata", {}),
                    "score": source.get("score", 0.0)
                })
            else:
                formatted_sources.append({
                    "content": str(source)[:500] + "..." if len(str(source)) > 500 else str(source),
                    "metadata": {},
                    "score": 0.0
                })
        
        return formatted_sources
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    @staticmethod
    def format_error_response(error: str, 
                            error_type: str = "unknown",
                            tenant_id: str = None) -> Dict[str, Any]:
        """Format an error response"""
        return {
            "answer": f"I encountered an error: {error}",
            "sources": [],
            "confidence": 0.0,
            "error": error,
            "error_type": error_type,
            "metadata": {
                "tenant_id": tenant_id,
                "response_type": "error",
                "timestamp": ResponseFormatter._get_timestamp()
            }
        }
    
    @staticmethod
    def format_health_check_response(health_status: Dict[str, Any]) -> Dict[str, Any]:
        """Format a health check response"""
        return {
            "overall": health_status.get("overall", False),
            "components": health_status.get("components", {}),
            "timestamp": ResponseFormatter._get_timestamp(),
            "service_type": "langchain_rag"
        }
    
    @staticmethod
    def format_tenant_stats_response(stats: Dict[str, Any]) -> Dict[str, Any]:
        """Format tenant statistics response"""
        return {
            "tenant_id": stats.get("tenant_id", "unknown"),
            "vector_store": stats.get("vector_store", {}),
            "embedding_info": stats.get("embedding_info", {}),
            "llm_info": stats.get("llm_info", {}),
            "timestamp": ResponseFormatter._get_timestamp()
        }
    
    @staticmethod
    def format_document_processing_response(result: Dict[str, Any]) -> Dict[str, Any]:
        """Format document processing response"""
        return {
            "status": result.get("status", "unknown"),
            "tenant_id": result.get("tenant_id", "unknown"),
            "chunks_created": result.get("chunks_created", 0),
            "document_ids": result.get("document_ids", []),
            "chunk_stats": result.get("chunk_stats", {}),
            "file_type": result.get("file_type", "unknown"),
            "message": result.get("message", ""),
            "timestamp": ResponseFormatter._get_timestamp()
        }
    
    @staticmethod
    def format_config_response(config: Dict[str, Any]) -> Dict[str, Any]:
        """Format configuration response"""
        return {
            "config": config,
            "timestamp": ResponseFormatter._get_timestamp(),
            "service_type": "langchain_rag"
        }
    
    @staticmethod
    def format_tenants_list_response(tenants: List[str]) -> Dict[str, Any]:
        """Format tenants list response"""
        return {
            "tenants": tenants,
            "count": len(tenants),
            "timestamp": ResponseFormatter._get_timestamp()
        }
    
    @staticmethod
    def add_processing_metadata(response: Dict[str, Any], 
                              processing_time: float = None,
                              memory_usage: Dict[str, Any] = None,
                              additional_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add processing metadata to a response"""
        if "metadata" not in response:
            response["metadata"] = {}
        
        if processing_time is not None:
            response["metadata"]["processing_time"] = processing_time
        
        if memory_usage is not None:
            response["metadata"]["memory_usage"] = memory_usage
        
        if additional_metadata is not None:
            response["metadata"].update(additional_metadata)
        
        return response
    
    @staticmethod
    def validate_response_format(response: Dict[str, Any]) -> bool:
        """Validate that a response has the required format"""
        required_fields = ["answer", "metadata"]
        
        for field in required_fields:
            if field not in response:
                logger.warning(f"Response missing required field: {field}")
                return False
        
        return True
    
    @staticmethod
    def sanitize_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a response by removing sensitive information"""
        sanitized = response.copy()
        
        # Remove potential sensitive information from metadata
        if "metadata" in sanitized:
            sensitive_keys = ["api_key", "password", "secret", "token"]
            for key in sensitive_keys:
                if key in sanitized["metadata"]:
                    sanitized["metadata"][key] = "[REDACTED]"
        
        return sanitized
