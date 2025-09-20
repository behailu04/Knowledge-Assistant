"""
Self-consistency agent for multiple reasoning traces
"""
from typing import Dict, Any, List, Optional
from langchain_core.language_models import BaseLanguageModel
import asyncio
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class SelfConsistencyAgent:
    """Agent for self-consistency through multiple reasoning traces"""
    
    def __init__(self, 
                 llm: BaseLanguageModel,
                 num_samples: int = 5,
                 temperature: float = 0.7):
        
        self.llm = llm
        self.num_samples = num_samples
        self.temperature = temperature
    
    async def generate_multiple_traces(self, 
                                     question: str,
                                     context: Optional[str] = None,
                                     tenant_id: str = None) -> List[Dict[str, Any]]:
        """Generate multiple reasoning traces for the same question"""
        try:
            logger.info(f"Generating {self.num_samples} reasoning traces for question")
            
            # Create tasks for parallel execution
            tasks = []
            for i in range(self.num_samples):
                task = self._generate_single_trace(
                    question=question,
                    context=context,
                    trace_id=i,
                    tenant_id=tenant_id
                )
                tasks.append(task)
            
            # Execute all traces in parallel
            traces = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return valid traces
            valid_traces = []
            for trace in traces:
                if isinstance(trace, dict) and "error" not in trace:
                    valid_traces.append(trace)
                elif isinstance(trace, Exception):
                    logger.error(f"Trace generation failed: {trace}")
            
            logger.info(f"Generated {len(valid_traces)} valid traces out of {self.num_samples}")
            return valid_traces
            
        except Exception as e:
            logger.error(f"Error generating multiple traces: {e}")
            return []
    
    async def _generate_single_trace(self, 
                                   question: str,
                                   context: Optional[str] = None,
                                   trace_id: int = 0,
                                   tenant_id: str = None) -> Dict[str, Any]:
        """Generate a single reasoning trace"""
        try:
            # Create prompt for this trace
            prompt = self._create_trace_prompt(question, context, trace_id)
            
            # Generate response with some randomness
            response = await self.llm.ainvoke(prompt)
            
            # Parse the response
            response_text = response.content if hasattr(response, 'content') else str(response)
            answer = self._extract_answer(response_text)
            reasoning = self._extract_reasoning(response_text)
            
            return {
                "trace_id": trace_id,
                "question": question,
                "answer": answer,
                "reasoning": reasoning,
                "confidence": self._calculate_trace_confidence(answer, reasoning),
                "metadata": {
                    "tenant_id": tenant_id,
                    "temperature": self.temperature,
                    "trace_length": len(reasoning)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating trace {trace_id}: {e}")
            return {
                "trace_id": trace_id,
                "error": str(e),
                "answer": "",
                "reasoning": "",
                "confidence": 0.0
            }
    
    def _create_trace_prompt(self, question: str, context: Optional[str], trace_id: int) -> str:
        """Create prompt for generating a reasoning trace"""
        base_prompt = f"""
        You are an AI assistant that provides detailed reasoning for complex questions.
        
        Question: {question}
        """
        
        if context:
            base_prompt += f"\nContext: {context}"
        
        base_prompt += f"""
        
        Please provide a step-by-step reasoning process and then give your final answer.
        Be thorough and consider multiple perspectives.
        
        Format your response as:
        Reasoning: [Your detailed reasoning process]
        Answer: [Your final answer]
        """
        
        return base_prompt
    
    def _extract_answer(self, response: str) -> str:
        """Extract the final answer from the response"""
        try:
            # Look for "Answer:" marker
            if "Answer:" in response:
                answer_section = response.split("Answer:")[-1].strip()
                return answer_section.split("\n")[0].strip()
            
            # If no marker, return the last line
            lines = response.strip().split("\n")
            return lines[-1] if lines else response.strip()
            
        except Exception as e:
            logger.error(f"Error extracting answer: {e}")
            return response.strip()
    
    def _extract_reasoning(self, response: str) -> str:
        """Extract the reasoning process from the response"""
        try:
            # Look for "Reasoning:" marker
            if "Reasoning:" in response:
                reasoning_section = response.split("Reasoning:")[1]
                if "Answer:" in reasoning_section:
                    reasoning_section = reasoning_section.split("Answer:")[0]
                return reasoning_section.strip()
            
            # If no marker, return everything except the last line
            lines = response.strip().split("\n")
            if len(lines) > 1:
                return "\n".join(lines[:-1]).strip()
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error extracting reasoning: {e}")
            return response.strip()
    
    def _calculate_trace_confidence(self, answer: str, reasoning: str) -> float:
        """Calculate confidence for a single trace"""
        try:
            # Base confidence on answer length and reasoning quality
            answer_confidence = min(len(answer) / 100, 1.0)
            reasoning_confidence = min(len(reasoning) / 500, 1.0)
            
            # Check for uncertainty indicators
            uncertainty_words = [
                "maybe", "perhaps", "might", "could", "possibly",
                "unclear", "uncertain", "not sure", "don't know"
            ]
            
            uncertainty_penalty = 1.0
            text_lower = (answer + " " + reasoning).lower()
            for word in uncertainty_words:
                if word in text_lower:
                    uncertainty_penalty *= 0.8
            
            final_confidence = (answer_confidence + reasoning_confidence) / 2 * uncertainty_penalty
            return round(min(max(final_confidence, 0.0), 1.0), 2)
            
        except Exception as e:
            logger.error(f"Error calculating trace confidence: {e}")
            return 0.5
    
    async def find_consensus(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find consensus among multiple reasoning traces"""
        try:
            if not traces:
                return {
                    "consensus_answer": "",
                    "consensus_confidence": 0.0,
                    "agreement_score": 0.0,
                    "traces_analyzed": 0
                }
            
            # Extract answers
            answers = [trace.get("answer", "") for trace in traces if "answer" in trace]
            
            if not answers:
                return {
                    "consensus_answer": "",
                    "consensus_confidence": 0.0,
                    "agreement_score": 0.0,
                    "traces_analyzed": 0
                }
            
            # Find most common answer (simple consensus)
            answer_counts = Counter(answers)
            most_common_answer, count = answer_counts.most_common(1)[0]
            
            # Calculate agreement score
            agreement_score = count / len(answers)
            
            # Calculate average confidence
            confidences = [trace.get("confidence", 0.0) for trace in traces if "confidence" in trace]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Consensus confidence combines agreement and average confidence
            consensus_confidence = (agreement_score + avg_confidence) / 2
            
            # Get reasoning from the most confident trace
            best_trace = max(traces, key=lambda t: t.get("confidence", 0.0))
            consensus_reasoning = best_trace.get("reasoning", "")
            
            return {
                "consensus_answer": most_common_answer,
                "consensus_reasoning": consensus_reasoning,
                "consensus_confidence": round(consensus_confidence, 2),
                "agreement_score": round(agreement_score, 2),
                "traces_analyzed": len(traces),
                "answer_distribution": dict(answer_counts),
                "individual_confidences": confidences
            }
            
        except Exception as e:
            logger.error(f"Error finding consensus: {e}")
            return {
                "consensus_answer": "",
                "consensus_confidence": 0.0,
                "agreement_score": 0.0,
                "traces_analyzed": 0,
                "error": str(e)
            }
    
    async def process_with_consistency(self, 
                                    question: str,
                                    context: Optional[str] = None,
                                    tenant_id: str = None) -> Dict[str, Any]:
        """Process a question with self-consistency"""
        try:
            logger.info(f"Processing question with self-consistency: {question[:100]}...")
            
            # Generate multiple traces
            traces = await self.generate_multiple_traces(
                question=question,
                context=context,
                tenant_id=tenant_id
            )
            
            # Find consensus
            consensus = await self.find_consensus(traces)
            
            return {
                "answer": consensus["consensus_answer"],
                "reasoning": consensus["consensus_reasoning"],
                "confidence": consensus["consensus_confidence"],
                "agreement_score": consensus["agreement_score"],
                "traces_analyzed": consensus["traces_analyzed"],
                "individual_traces": traces,
                "consensus_metadata": consensus,
                "metadata": {
                    "agent_type": "self_consistency",
                    "tenant_id": tenant_id,
                    "question": question,
                    "num_samples": self.num_samples
                }
            }
            
        except Exception as e:
            logger.error(f"Error in self-consistency processing: {e}")
            return {
                "answer": "I encountered an error during self-consistency processing. Please try again.",
                "reasoning": "",
                "confidence": 0.0,
                "error": str(e),
                "metadata": {
                    "agent_type": "self_consistency",
                    "tenant_id": tenant_id,
                    "question": question
                }
            }
    
    def health_check(self) -> bool:
        """Check if the self-consistency agent is healthy"""
        try:
            # Test with a simple question
            test_result = self.process_with_consistency("What is 2+2?")
            return "error" not in test_result
        except Exception as e:
            logger.error(f"Self-consistency agent health check failed: {e}")
            return False
