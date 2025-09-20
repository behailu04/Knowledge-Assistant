"""
Multi-hop reasoning agent using LangChain
"""
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.retrievers import BaseRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class MultiHopReasoningAgent:
    """Agent for multi-hop reasoning and query decomposition"""
    
    def __init__(self, 
                 llm: BaseLanguageModel,
                 retriever: BaseRetriever,
                 max_hops: int = 3):
        
        self.llm = llm
        self.retriever = retriever
        self.max_hops = max_hops
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Create prompt template
        self.prompt = self._create_prompt()
        
        # Create agent
        self.agent = create_react_agent(
            llm=llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=max_hops,
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        
        def search_documents(query: str) -> str:
            """Search for relevant documents"""
            try:
                docs = self.retriever.invoke(query)
                if not docs:
                    return "No relevant documents found."
                
                result = "Found relevant documents:\n"
                for i, doc in enumerate(docs[:3]):  # Limit to top 3
                    result += f"\nDocument {i+1}:\n"
                    result += f"Content: {doc.page_content[:500]}...\n"
                    result += f"Metadata: {doc.metadata}\n"
                
                return result
            except Exception as e:
                return f"Error searching documents: {str(e)}"
        
        def analyze_context(context: str, question: str) -> str:
            """Analyze the context to extract relevant information"""
            try:
                # This would use the LLM to analyze context
                analysis_prompt = f"""
                Analyze the following context to answer the question:
                
                Context: {context}
                Question: {question}
                
                Extract the most relevant information and provide a focused analysis.
                """
                
                # For now, return a simple analysis
                return f"Analyzed context of {len(context)} characters for question: {question}"
            except Exception as e:
                return f"Error analyzing context: {str(e)}"
        
        def synthesize_information(info1: str, info2: str) -> str:
            """Synthesize information from multiple sources"""
            try:
                synthesis_prompt = f"""
                Synthesize the following information:
                
                Information 1: {info1}
                Information 2: {info2}
                
                Provide a coherent synthesis that combines the key points.
                """
                
                # For now, return a simple synthesis
                return f"Synthesized information from two sources: {len(info1)} and {len(info2)} characters"
            except Exception as e:
                return f"Error synthesizing information: {str(e)}"
        
        return [
            Tool(
                name="search_documents",
                description="Search for relevant documents in the knowledge base",
                func=search_documents
            ),
            Tool(
                name="analyze_context", 
                description="Analyze context to extract relevant information",
                func=analyze_context
            ),
            Tool(
                name="synthesize_information",
                description="Synthesize information from multiple sources",
                func=synthesize_information
            )
        ]
    
    def _create_prompt(self) -> PromptTemplate:
        """Create prompt template for multi-hop reasoning"""
        template = """
        You are an AI assistant that performs multi-hop reasoning to answer complex questions.
        
        You have access to the following tools:
        {tools}
        
        Use the following format:
        
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Begin!
        
        Question: {input}
        Thought: {agent_scratchpad}
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
    
    async def process_query(self, 
                          question: str, 
                          tenant_id: str = None,
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a query using multi-hop reasoning"""
        try:
            logger.info(f"Processing multi-hop query: {question[:100]}...")
            
            # Set tenant context if supported
            if hasattr(self.retriever, 'tenant_id') and tenant_id:
                self.retriever.tenant_id = tenant_id
            
            # Execute the agent
            result = await self.agent_executor.ainvoke({
                "input": question,
                "context": context or {}
            })
            
            # Extract reasoning steps
            reasoning_steps = self._extract_reasoning_steps(result)
            
            return {
                "answer": result.get("output", ""),
                "reasoning_steps": reasoning_steps,
                "hop_count": len(reasoning_steps),
                "confidence": self._calculate_confidence(result),
                "metadata": {
                    "agent_type": "multi_hop",
                    "tenant_id": tenant_id,
                    "question": question
                }
            }
            
        except Exception as e:
            logger.error(f"Error in multi-hop reasoning: {e}")
            return {
                "answer": "I encountered an error during multi-hop reasoning. Please try again.",
                "reasoning_steps": [],
                "hop_count": 0,
                "confidence": 0.0,
                "error": str(e),
                "metadata": {
                    "agent_type": "multi_hop",
                    "tenant_id": tenant_id,
                    "question": question
                }
            }
    
    def _extract_reasoning_steps(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract reasoning steps from agent execution"""
        try:
            # This would parse the agent's intermediate steps
            # For now, return a simple structure
            steps = []
            
            if "intermediate_steps" in result:
                for i, step in enumerate(result["intermediate_steps"]):
                    steps.append({
                        "step": i + 1,
                        "action": step.get("action", ""),
                        "observation": step.get("observation", ""),
                        "thought": step.get("thought", "")
                    })
            
            return steps
            
        except Exception as e:
            logger.error(f"Error extracting reasoning steps: {e}")
            return []
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence based on reasoning quality"""
        try:
            # Base confidence on number of steps and quality
            steps = result.get("intermediate_steps", [])
            base_confidence = min(len(steps) / self.max_hops, 1.0)
            
            # Adjust based on answer quality
            answer = result.get("output", "")
            if len(answer) < 50:
                quality_factor = 0.7
            elif len(answer) > 500:
                quality_factor = 1.0
            else:
                quality_factor = 0.9
            
            return round(base_confidence * quality_factor, 2)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def health_check(self) -> bool:
        """Check if the agent is healthy"""
        try:
            # Test with a simple query
            test_result = self.process_query("test query")
            return "error" not in test_result
        except Exception as e:
            logger.error(f"Multi-hop agent health check failed: {e}")
            return False
