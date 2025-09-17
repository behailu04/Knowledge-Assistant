"""
LLM Orchestrator for RAG with Chain-of-Thought and Self-Consistency
"""
import logging
import asyncio
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.retrieval import RetrievalService
from services.query_planner import QueryPlanner
from services.verification import VerificationService
from config import settings

logger = logging.getLogger(__name__)

class LLMOrchestrator:
    """Orchestrates LLM operations with multi-hop reasoning and self-consistency"""
    
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.query_planner = QueryPlanner()
        self.verification_service = VerificationService()
        self.llm_provider = self._initialize_llm_provider()
    
    def _initialize_llm_provider(self):
        """Initialize LLM provider based on configuration"""
        if settings.LLM_PROVIDER == "openai":
            from services.llm_providers.openai_provider import OpenAIProvider
            return OpenAIProvider()
        elif settings.LLM_PROVIDER == "ollama":
            from services.llm_providers.ollama_provider import OllamaProvider
            return OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL
            )
        else:
            # Default to a mock provider for development
            from services.llm_providers.mock_provider import MockProvider
            return MockProvider()
    
    async def process_query(self, question: str, tenant_id: str, 
                          max_hops: int = 3, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query with multi-hop reasoning and self-consistency"""
        try:
            if options is None:
                options = {}
            
            use_cot = options.get("use_cot", settings.COT_ENABLED)
            self_consistency_samples = options.get("self_consistency_samples", settings.SELF_CONSISTENCY_SAMPLES)
            
            logger.info(f"Processing query: {question[:100]}...")
            
            # Plan the query
            execution_plan = await self.query_planner.plan_query(question, max_hops)
            
            if len(execution_plan) == 1:
                # Single-hop query
                result = await self._process_single_hop_query(
                    question, tenant_id, use_cot, self_consistency_samples
                )
            else:
                # Multi-hop query
                result = await self._process_multi_hop_query(
                    question, tenant_id, execution_plan, use_cot, self_consistency_samples
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your query. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "reasoning_traces": [],
                "hop_count": 0,
                "error": str(e)
            }
    
    async def _process_single_hop_query(self, question: str, tenant_id: str, 
                                      use_cot: bool, self_consistency_samples: int) -> Dict[str, Any]:
        """Process a single-hop query"""
        try:
            # Retrieve relevant documents
            retrieved_docs = await self.retrieval_service.retrieve_documents(question, tenant_id)
            
            if not retrieved_docs:
                return {
                    "answer": "I couldn't find relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0,
                    "reasoning_traces": [],
                    "hop_count": 1
                }
            
            if self_consistency_samples > 1:
                # Use self-consistency
                return await self._process_with_self_consistency(
                    question, retrieved_docs, use_cot, self_consistency_samples
                )
            else:
                # Single generation
                return await self._process_single_generation(
                    question, retrieved_docs, use_cot
                )
                
        except Exception as e:
            logger.error(f"Error in single-hop processing: {e}")
            raise
    
    async def _process_multi_hop_query(self, question: str, tenant_id: str, 
                                     execution_plan: List[Dict[str, Any]], 
                                     use_cot: bool, self_consistency_samples: int) -> Dict[str, Any]:
        """Process a multi-hop query"""
        try:
            context = {"tenant_id": tenant_id, "question": question}
            hop_results = []
            
            # Execute each hop
            for hop_plan in execution_plan:
                hop_result = await self.query_planner.execute_hop(
                    hop_plan, context, self.retrieval_service
                )
                hop_results.append(hop_result)
                
                # Update context for next hop
                context["previous_results"] = hop_result.get("result", [])
                context["entities"] = hop_result.get("entities", [])
            
            # Combine hop results
            all_sources = []
            for hop_result in hop_results:
                all_sources.extend(hop_result.get("sources", []))
            
            # Generate final answer
            if self_consistency_samples > 1:
                return await self._process_with_self_consistency(
                    question, all_sources, use_cot, self_consistency_samples, hop_results
                )
            else:
                return await self._process_single_generation(
                    question, all_sources, use_cot, hop_results
                )
                
        except Exception as e:
            logger.error(f"Error in multi-hop processing: {e}")
            raise
    
    async def _process_with_self_consistency(self, question: str, sources: List[Dict[str, Any]], 
                                           use_cot: bool, samples: int, 
                                           hop_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process query with self-consistency sampling"""
        try:
            logger.info(f"Processing with self-consistency: {samples} samples")
            
            # Generate multiple reasoning traces
            reasoning_traces = []
            answers = []
            
            for i in range(samples):
                trace_id = str(uuid.uuid4())
                
                # Generate answer with different temperature for diversity
                temperature = 0.7 + (i * 0.1)  # Vary temperature
                
                answer_result = await self._generate_answer(
                    question, sources, use_cot, temperature, hop_results
                )
                
                reasoning_traces.append({
                    "trace_id": trace_id,
                    "steps": answer_result.get("reasoning_steps", []),
                    "vote_score": 1.0 / samples,  # Equal weight for now
                    "reasoning": answer_result.get("reasoning", ""),
                    "answer": answer_result.get("answer", "")
                })
                
                answers.append(answer_result.get("answer", ""))
            
            # Aggregate answers
            final_answer, confidence = self._aggregate_answers(answers, reasoning_traces)
            
            # Verify claims
            verification_result = await self.verification_service.verify_claims(
                final_answer, sources
            )
            
            return {
                "answer": final_answer,
                "sources": sources[:5],  # Top 5 sources
                "confidence": confidence,
                "reasoning_traces": reasoning_traces,
                "hop_count": len(hop_results) if hop_results else 1,
                "verification": verification_result
            }
            
        except Exception as e:
            logger.error(f"Error in self-consistency processing: {e}")
            raise
    
    async def _process_single_generation(self, question: str, sources: List[Dict[str, Any]], 
                                       use_cot: bool, hop_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process query with single generation"""
        try:
            # Generate answer
            answer_result = await self._generate_answer(
                question, sources, use_cot, 0.7, hop_results
            )
            
            # Verify claims
            verification_result = await self.verification_service.verify_claims(
                answer_result.get("answer", ""), sources
            )
            
            return {
                "answer": answer_result.get("answer", ""),
                "sources": sources[:5],  # Top 5 sources
                "confidence": answer_result.get("confidence", 0.5),
                "reasoning_traces": [{
                    "trace_id": str(uuid.uuid4()),
                    "steps": answer_result.get("reasoning_steps", []),
                    "vote_score": 1.0,
                    "reasoning": answer_result.get("reasoning", "")
                }],
                "hop_count": len(hop_results) if hop_results else 1,
                "verification": verification_result
            }
            
        except Exception as e:
            logger.error(f"Error in single generation processing: {e}")
            raise
    
    async def _generate_answer(self, question: str, sources: List[Dict[str, Any]], 
                             use_cot: bool, temperature: float, 
                             hop_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate answer using LLM"""
        try:
            # Prepare context
            context_text = self._prepare_context(sources, hop_results)
            
            # Create prompt
            if use_cot:
                prompt = self._create_cot_prompt(question, context_text)
            else:
                prompt = self._create_direct_prompt(question, context_text)
            
            # Generate response
            response = await self.llm_provider.generate_response(
                prompt, temperature=temperature, max_tokens=settings.MAX_TOKENS
            )
            
            # Parse response
            if use_cot:
                answer, reasoning = self._parse_cot_response(response)
                reasoning_steps = self._extract_reasoning_steps(reasoning)
            else:
                answer = response
                reasoning = ""
                reasoning_steps = []
            
            # Calculate confidence (simplified)
            confidence = self._calculate_confidence(answer, sources)
            
            return {
                "answer": answer,
                "reasoning": reasoning,
                "reasoning_steps": reasoning_steps,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "I apologize, but I couldn't generate a proper response.",
                "reasoning": "",
                "reasoning_steps": [],
                "confidence": 0.0
            }
    
    def _prepare_context(self, sources: List[Dict[str, Any]], 
                        hop_results: List[Dict[str, Any]] = None) -> str:
        """Prepare context from sources and hop results"""
        context_parts = []
        
        # Add sources
        if sources:
            context_parts.append("Relevant Information:")
            for i, source in enumerate(sources[:10], 1):  # Limit to top 10
                context_parts.append(f"{i}. {source.get('text', '')[:500]}...")
                context_parts.append(f"   Source: {source.get('doc_id', 'unknown')}")
                context_parts.append("")
        
        # Add hop results if available
        if hop_results:
            context_parts.append("Multi-hop Analysis:")
            for i, hop_result in enumerate(hop_results, 1):
                hop_type = hop_result.get("hop_type", "unknown")
                hop_subquery = hop_result.get("subquery", "")
                context_parts.append(f"Step {i} ({hop_type}): {hop_subquery}")
                
                hop_sources = hop_result.get("sources", [])
                if hop_sources:
                    context_parts.append(f"Found {len(hop_sources)} relevant documents")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _create_cot_prompt(self, question: str, context: str) -> str:
        """Create Chain-of-Thought prompt"""
        return f"""You are a helpful AI assistant. Use the following information to answer the question step by step.

{context}

Question: {question}

Please think through this step by step:
1. What information is relevant to answering this question?
2. What are the key facts or details I need to consider?
3. How do these pieces of information relate to each other?
4. What is the most accurate answer based on the available information?

Answer:"""
    
    def _create_direct_prompt(self, question: str, context: str) -> str:
        """Create direct prompt without Chain-of-Thought"""
        return f"""You are a helpful AI assistant. Use the following information to answer the question.

{context}

Question: {question}

Answer:"""
    
    def _parse_cot_response(self, response: str) -> tuple:
        """Parse Chain-of-Thought response to extract answer and reasoning"""
        try:
            # Look for "Answer:" marker
            if "Answer:" in response:
                parts = response.split("Answer:", 1)
                reasoning = parts[0].strip()
                answer = parts[1].strip()
            else:
                # Fallback: use the whole response as answer
                reasoning = ""
                answer = response.strip()
            
            return answer, reasoning
            
        except Exception as e:
            logger.error(f"Error parsing CoT response: {e}")
            return response.strip(), ""
    
    def _extract_reasoning_steps(self, reasoning: str) -> List[str]:
        """Extract individual reasoning steps"""
        try:
            steps = []
            lines = reasoning.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                           line.startswith(('•', '-', '*'))):
                    steps.append(line)
            
            return steps
            
        except Exception as e:
            logger.error(f"Error extracting reasoning steps: {e}")
            return []
    
    def _calculate_confidence(self, answer: str, sources: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the answer"""
        try:
            if not answer or not sources:
                return 0.0
            
            # Base confidence on source quality and answer length
            source_scores = [source.get("score", 0.0) for source in sources]
            avg_source_score = sum(source_scores) / len(source_scores) if source_scores else 0.0
            
            # Answer length factor (longer answers might be more confident)
            answer_length_factor = min(len(answer.split()) / 50, 1.0)
            
            # Combine factors
            confidence = (avg_source_score * 0.7) + (answer_length_factor * 0.3)
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _aggregate_answers(self, answers: List[str], reasoning_traces: List[Dict[str, Any]]) -> tuple:
        """Aggregate multiple answers using majority vote or consensus"""
        try:
            if not answers:
                return "I couldn't generate a proper answer.", 0.0
            
            if len(answers) == 1:
                return answers[0], 0.5
            
            # Simple majority vote (in production, use more sophisticated methods)
            answer_counts = {}
            for answer in answers:
                # Normalize answer for comparison
                normalized = answer.lower().strip()
                answer_counts[normalized] = answer_counts.get(normalized, 0) + 1
            
            # Find most common answer
            most_common_answer = max(answer_counts, key=answer_counts.get)
            vote_count = answer_counts[most_common_answer]
            
            # Calculate confidence based on consensus
            confidence = vote_count / len(answers)
            
            # Return the first occurrence of the most common answer
            for answer in answers:
                if answer.lower().strip() == most_common_answer:
                    return answer, confidence
            
            return answers[0], confidence
            
        except Exception as e:
            logger.error(f"Error aggregating answers: {e}")
            return answers[0] if answers else "Error in answer aggregation", 0.0
