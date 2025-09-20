"""
Query planner agent for decomposing complex queries
"""
from typing import Dict, Any, List, Optional, Tuple
from langchain_core.language_models import BaseLanguageModel
import re
import logging

logger = logging.getLogger(__name__)

class QueryPlannerAgent:
    """Agent for planning and decomposing complex queries"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
    
    async def analyze_query_complexity(self, question: str) -> Dict[str, Any]:
        """Analyze the complexity of a query"""
        try:
            complexity_indicators = {
                "multi_part": self._has_multiple_parts(question),
                "comparison": self._has_comparison(question),
                "temporal": self._has_temporal_elements(question),
                "conditional": self._has_conditional_logic(question),
                "aggregation": self._has_aggregation(question),
                "reasoning": self._requires_reasoning(question)
            }
            
            # Calculate overall complexity score
            complexity_score = sum(complexity_indicators.values()) / len(complexity_indicators)
            
            # Determine complexity level
            if complexity_score >= 0.7:
                complexity_level = "high"
            elif complexity_score >= 0.4:
                complexity_level = "medium"
            else:
                complexity_level = "low"
            
            return {
                "complexity_score": round(complexity_score, 2),
                "complexity_level": complexity_level,
                "indicators": complexity_indicators,
                "requires_multi_hop": complexity_score >= 0.5
            }
            
        except Exception as e:
            logger.error(f"Error analyzing query complexity: {e}")
            return {
                "complexity_score": 0.5,
                "complexity_level": "medium",
                "indicators": {},
                "requires_multi_hop": True,
                "error": str(e)
            }
    
    def _has_multiple_parts(self, question: str) -> bool:
        """Check if question has multiple parts (AND, OR, etc.)"""
        multi_part_indicators = [
            r'\band\b', r'\bor\b', r'\bbut\b', r'\bhowever\b',
            r'\bwhat\s+and\s+', r'\bhow\s+and\s+', r'\bwhy\s+and\s+',
            r'\?.*\?', r'\bcompare\b', r'\bcontrast\b'
        ]
        
        for pattern in multi_part_indicators:
            if re.search(pattern, question, re.IGNORECASE):
                return True
        return False
    
    def _has_comparison(self, question: str) -> bool:
        """Check if question involves comparison"""
        comparison_indicators = [
            r'\bcompare\b', r'\bcontrast\b', r'\bversus\b', r'\bvs\b',
            r'\bbetter\b', r'\bworse\b', r'\bmore\b', r'\bless\b',
            r'\bdifference\b', r'\bsimilar\b', r'\bdifferent\b',
            r'\bthan\b', r'\bcompared\s+to\b'
        ]
        
        for pattern in comparison_indicators:
            if re.search(pattern, question, re.IGNORECASE):
                return True
        return False
    
    def _has_temporal_elements(self, question: str) -> bool:
        """Check if question has temporal elements"""
        temporal_indicators = [
            r'\bwhen\b', r'\btime\b', r'\bdate\b', r'\byear\b',
            r'\bmonth\b', r'\bday\b', r'\bperiod\b', r'\bduration\b',
            r'\bbefore\b', r'\bafter\b', r'\bduring\b', r'\bwhile\b',
            r'\buntil\b', r'\bsince\b', r'\bago\b', r'\blater\b',
            r'\bnow\b', r'\bthen\b', r'\bcurrent\b', r'\bprevious\b'
        ]
        
        for pattern in temporal_indicators:
            if re.search(pattern, question, re.IGNORECASE):
                return True
        return False
    
    def _has_conditional_logic(self, question: str) -> bool:
        """Check if question has conditional logic"""
        conditional_indicators = [
            r'\bif\b', r'\bwhen\b', r'\bunless\b', r'\bprovided\b',
            r'\bassuming\b', r'\bsuppose\b', r'\bwhat\s+if\b',
            r'\bwould\b', r'\bcould\b', r'\bshould\b', r'\bmight\b'
        ]
        
        for pattern in conditional_indicators:
            if re.search(pattern, question, re.IGNORECASE):
                return True
        return False
    
    def _has_aggregation(self, question: str) -> bool:
        """Check if question involves aggregation"""
        aggregation_indicators = [
            r'\btotal\b', r'\bsum\b', r'\baverage\b', r'\bmean\b',
            r'\bcount\b', r'\bnumber\b', r'\bhow\s+many\b',
            r'\ball\b', r'\bevery\b', r'\beach\b', r'\bmost\b',
            r'\bleast\b', r'\bhighest\b', r'\blowest\b', r'\bmaximum\b',
            r'\bminimum\b', r'\boverall\b', r'\bcombined\b'
        ]
        
        for pattern in aggregation_indicators:
            if re.search(pattern, question, re.IGNORECASE):
                return True
        return False
    
    def _requires_reasoning(self, question: str) -> bool:
        """Check if question requires reasoning"""
        reasoning_indicators = [
            r'\bwhy\b', r'\bhow\b', r'\bexplain\b', r'\bdescribe\b',
            r'\banalyze\b', r'\bevaluate\b', r'\bassess\b',
            r'\bimplications\b', r'\bconsequences\b', r'\beffects\b',
            r'\bcauses\b', r'\breasons\b', r'\bfactors\b',
            r'\bprocess\b', r'\bmechanism\b', r'\bapproach\b'
        ]
        
        for pattern in reasoning_indicators:
            if re.search(pattern, question, re.IGNORECASE):
                return True
        return False
    
    async def decompose_query(self, question: str) -> List[Dict[str, Any]]:
        """Decompose a complex query into sub-queries"""
        try:
            complexity = await self.analyze_query_complexity(question)
            
            if not complexity["requires_multi_hop"]:
                return [{
                    "sub_query": question,
                    "query_type": "simple",
                    "priority": 1,
                    "dependencies": []
                }]
            
            # Use LLM to decompose the query
            decomposition_prompt = f"""
            Decompose the following complex question into simpler sub-questions that can be answered independently or in sequence.
            
            Original Question: {question}
            
            Please provide 2-4 sub-questions that, when answered together, will help answer the original question.
            For each sub-question, indicate:
            1. The sub-question text
            2. The type of query (retrieval, analysis, comparison, etc.)
            3. Priority (1=highest, 2=medium, 3=lowest)
            4. Dependencies (which other sub-questions this depends on)
            
            Format your response as:
            Sub-query 1: [question text]
            Type: [query type]
            Priority: [1-3]
            Dependencies: [list of other sub-query numbers or "none"]
            
            Sub-query 2: [question text]
            Type: [query type]
            Priority: [1-3]
            Dependencies: [list of other sub-query numbers or "none"]
            
            And so on...
            """
            
            response = await self.llm.ainvoke(decomposition_prompt)
            sub_queries = self._parse_decomposition(response)
            
            # If parsing failed, create a simple decomposition
            if not sub_queries:
                sub_queries = self._create_simple_decomposition(question)
            
            return sub_queries
            
        except Exception as e:
            logger.error(f"Error decomposing query: {e}")
            return [{
                "sub_query": question,
                "query_type": "simple",
                "priority": 1,
                "dependencies": [],
                "error": str(e)
            }]
    
    def _parse_decomposition(self, response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response into structured sub-queries"""
        try:
            sub_queries = []
            lines = response.strip().split('\n')
            
            current_query = {}
            for line in lines:
                line = line.strip()
                if line.startswith('Sub-query'):
                    if current_query:
                        sub_queries.append(current_query)
                    current_query = {"sub_query": "", "query_type": "retrieval", "priority": 1, "dependencies": []}
                    # Extract question text
                    if ':' in line:
                        current_query["sub_query"] = line.split(':', 1)[1].strip()
                elif line.startswith('Type:'):
                    current_query["query_type"] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('Priority:'):
                    try:
                        current_query["priority"] = int(line.split(':', 1)[1].strip())
                    except:
                        current_query["priority"] = 1
                elif line.startswith('Dependencies:'):
                    deps = line.split(':', 1)[1].strip()
                    if deps.lower() != "none" and deps:
                        current_query["dependencies"] = [d.strip() for d in deps.split(',')]
            
            # Add the last query
            if current_query and current_query["sub_query"]:
                sub_queries.append(current_query)
            
            return sub_queries
            
        except Exception as e:
            logger.error(f"Error parsing decomposition: {e}")
            return []
    
    def _create_simple_decomposition(self, question: str) -> List[Dict[str, Any]]:
        """Create a simple decomposition when LLM parsing fails"""
        # Simple heuristics for decomposition
        if ' and ' in question.lower():
            parts = question.split(' and ')
            return [
                {
                    "sub_query": parts[0].strip(),
                    "query_type": "retrieval",
                    "priority": 1,
                    "dependencies": []
                },
                {
                    "sub_query": parts[1].strip(),
                    "query_type": "retrieval", 
                    "priority": 2,
                    "dependencies": []
                }
            ]
        elif ' or ' in question.lower():
            parts = question.split(' or ')
            return [
                {
                    "sub_query": parts[0].strip(),
                    "query_type": "retrieval",
                    "priority": 1,
                    "dependencies": []
                },
                {
                    "sub_query": parts[1].strip(),
                    "query_type": "retrieval",
                    "priority": 1,
                    "dependencies": []
                }
            ]
        else:
            return [{
                "sub_query": question,
                "query_type": "retrieval",
                "priority": 1,
                "dependencies": []
            }]
    
    async def create_execution_plan(self, sub_queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create an execution plan for sub-queries"""
        try:
            # Sort by priority and dependencies
            execution_order = []
            remaining = sub_queries.copy()
            
            while remaining:
                # Find queries with no unmet dependencies
                ready_queries = []
                for query in remaining:
                    deps = query.get("dependencies", [])
                    if not deps or all(dep in [q.get("sub_query", "") for q in execution_order] for dep in deps):
                        ready_queries.append(query)
                
                if not ready_queries:
                    # If no queries are ready, add the highest priority one
                    ready_queries = [max(remaining, key=lambda q: q.get("priority", 1))]
                
                # Sort ready queries by priority
                ready_queries.sort(key=lambda q: q.get("priority", 1))
                
                # Add the first ready query to execution order
                next_query = ready_queries[0]
                execution_order.append(next_query)
                remaining.remove(next_query)
            
            # Add execution metadata
            for i, query in enumerate(execution_order):
                query["execution_order"] = i + 1
                query["estimated_difficulty"] = self._estimate_difficulty(query)
            
            return execution_order
            
        except Exception as e:
            logger.error(f"Error creating execution plan: {e}")
            return sub_queries
    
    def _estimate_difficulty(self, query: Dict[str, Any]) -> str:
        """Estimate the difficulty of a sub-query"""
        question = query.get("sub_query", "")
        query_type = query.get("query_type", "retrieval")
        
        # Base difficulty on query type
        type_difficulty = {
            "retrieval": 1,
            "analysis": 2,
            "comparison": 3,
            "synthesis": 4,
            "reasoning": 3
        }
        
        base_difficulty = type_difficulty.get(query_type, 2)
        
        # Adjust based on question characteristics
        if len(question) > 100:
            base_difficulty += 1
        if any(word in question.lower() for word in ["complex", "detailed", "comprehensive"]):
            base_difficulty += 1
        
        if base_difficulty <= 2:
            return "easy"
        elif base_difficulty <= 3:
            return "medium"
        else:
            return "hard"
    
    async def plan_query_execution(self, question: str) -> Dict[str, Any]:
        """Plan the execution of a complex query"""
        try:
            logger.info(f"Planning execution for query: {question[:100]}...")
            
            # Analyze complexity
            complexity = await self.analyze_query_complexity(question)
            
            # Decompose if needed
            if complexity["requires_multi_hop"]:
                sub_queries = await self.decompose_query(question)
                execution_plan = await self.create_execution_plan(sub_queries)
            else:
                sub_queries = [{
                    "sub_query": question,
                    "query_type": "simple",
                    "priority": 1,
                    "dependencies": [],
                    "execution_order": 1,
                    "estimated_difficulty": "easy"
                }]
                execution_plan = sub_queries
            
            return {
                "original_question": question,
                "complexity_analysis": complexity,
                "sub_queries": sub_queries,
                "execution_plan": execution_plan,
                "estimated_execution_time": len(execution_plan) * 2,  # Rough estimate
                "requires_parallel_execution": len(execution_plan) > 1 and not any(
                    q.get("dependencies", []) for q in execution_plan
                )
            }
            
        except Exception as e:
            logger.error(f"Error planning query execution: {e}")
            return {
                "original_question": question,
                "error": str(e),
                "sub_queries": [],
                "execution_plan": [],
                "complexity_analysis": {"complexity_level": "unknown"}
            }
    
    def health_check(self) -> bool:
        """Check if the query planner is healthy"""
        try:
            # Test with a simple query
            test_result = self.plan_query_execution("What is the capital of France?")
            return "error" not in test_result
        except Exception as e:
            logger.error(f"Query planner health check failed: {e}")
            return False
