"""
Query planner for multi-hop reasoning
"""
import logging
import re
from typing import List, Dict, Any, Optional
import asyncio
import json

logger = logging.getLogger(__name__)

class QueryPlanner:
    """Service for planning multi-hop queries"""
    
    def __init__(self):
        self.max_hops = 3
        self.hop_cache = {}  # Cache for intermediate results
    
    async def plan_query(self, question: str, max_hops: int = 3) -> List[Dict[str, Any]]:
        """Plan a multi-hop query execution"""
        try:
            logger.info(f"Planning query: {question}")
            
            # Analyze query complexity
            complexity = self._analyze_query_complexity(question)
            
            if complexity == "simple" or max_hops == 1:
                return [{
                    "hop": 1,
                    "subquery": question,
                    "type": "direct",
                    "dependencies": [],
                    "expected_output": "answer"
                }]
            
            # Decompose complex query
            subqueries = await self._decompose_query(question, max_hops)
            
            # Create execution plan
            execution_plan = []
            for i, subquery in enumerate(subqueries):
                execution_plan.append({
                    "hop": i + 1,
                    "subquery": subquery["query"],
                    "type": subquery["type"],
                    "dependencies": subquery.get("dependencies", []),
                    "expected_output": subquery.get("expected_output", "data"),
                    "context_requirements": subquery.get("context_requirements", [])
                })
            
            logger.info(f"Created execution plan with {len(execution_plan)} hops")
            return execution_plan
            
        except Exception as e:
            logger.error(f"Error planning query: {e}")
            # Fallback to single-hop
            return [{
                "hop": 1,
                "subquery": question,
                "type": "direct",
                "dependencies": [],
                "expected_output": "answer"
            }]
    
    def _analyze_query_complexity(self, question: str) -> str:
        """Analyze query complexity to determine if multi-hop is needed"""
        question_lower = question.lower()
        
        # Indicators of complex queries
        complex_indicators = [
            "which", "compare", "analyze", "find all", "list all",
            "what are the", "how many", "when did", "where are",
            "and", "or", "but", "however", "additionally"
        ]
        
        # Count complex indicators
        complex_count = sum(1 for indicator in complex_indicators if indicator in question_lower)
        
        # Check for multi-part questions
        question_marks = question.count("?")
        conjunctions = len(re.findall(r'\b(and|or|but|however|additionally)\b', question_lower))
        
        if complex_count >= 2 or question_marks > 1 or conjunctions >= 2:
            return "complex"
        elif complex_count >= 1 or conjunctions >= 1:
            return "medium"
        else:
            return "simple"
    
    async def _decompose_query(self, question: str, max_hops: int) -> List[Dict[str, Any]]:
        """Decompose a complex query into subqueries"""
        try:
            # Use a simple rule-based decomposition
            # In production, this would use a more sophisticated approach
            
            subqueries = []
            
            # Pattern 1: "Which X do Y and Z?"
            which_pattern = r"which\s+(\w+)\s+do\s+(.+?)\s+and\s+(.+)"
            match = re.search(which_pattern, question.lower())
            if match:
                entity_type = match.group(1)
                condition1 = match.group(2)
                condition2 = match.group(3)
                
                subqueries.append({
                    "query": f"Find all {entity_type} that {condition1}",
                    "type": "filter",
                    "expected_output": f"list_of_{entity_type}",
                    "context_requirements": ["entity_type", "condition1"]
                })
                
                subqueries.append({
                    "query": f"Check which of these {entity_type} also {condition2}",
                    "type": "filter",
                    "dependencies": [0],
                    "expected_output": f"filtered_{entity_type}",
                    "context_requirements": ["previous_results", "condition2"]
                })
                
                return subqueries
            
            # Pattern 2: "What are the X and Y of Z?"
            what_pattern = r"what\s+are\s+the\s+(.+?)\s+and\s+(.+?)\s+of\s+(.+)"
            match = re.search(what_pattern, question.lower())
            if match:
                attribute1 = match.group(1)
                attribute2 = match.group(2)
                entity = match.group(3)
                
                subqueries.append({
                    "query": f"Find information about {entity}",
                    "type": "retrieve",
                    "expected_output": f"info_about_{entity}",
                    "context_requirements": ["entity"]
                })
                
                subqueries.append({
                    "query": f"Extract {attribute1} and {attribute2} from the information",
                    "type": "extract",
                    "dependencies": [0],
                    "expected_output": f"attributes_of_{entity}",
                    "context_requirements": ["previous_results", "attributes"]
                })
                
                return subqueries
            
            # Pattern 3: "Compare X and Y"
            compare_pattern = r"compare\s+(.+?)\s+and\s+(.+)"
            match = re.search(compare_pattern, question.lower())
            if match:
                entity1 = match.group(1)
                entity2 = match.group(2)
                
                subqueries.append({
                    "query": f"Find information about {entity1}",
                    "type": "retrieve",
                    "expected_output": f"info_about_{entity1}",
                    "context_requirements": ["entity1"]
                })
                
                subqueries.append({
                    "query": f"Find information about {entity2}",
                    "type": "retrieve",
                    "expected_output": f"info_about_{entity2}",
                    "context_requirements": ["entity2"]
                })
                
                subqueries.append({
                    "query": f"Compare the information about {entity1} and {entity2}",
                    "type": "compare",
                    "dependencies": [0, 1],
                    "expected_output": "comparison_result",
                    "context_requirements": ["both_results"]
                })
                
                return subqueries
            
            # Default: Single subquery
            return [{
                "query": question,
                "type": "direct",
                "expected_output": "answer",
                "context_requirements": []
            }]
            
        except Exception as e:
            logger.error(f"Error decomposing query: {e}")
            return [{
                "query": question,
                "type": "direct",
                "expected_output": "answer",
                "context_requirements": []
            }]
    
    async def execute_hop(self, hop_plan: Dict[str, Any], context: Dict[str, Any], 
                         retrieval_service) -> Dict[str, Any]:
        """Execute a single hop in the query plan"""
        try:
            hop_number = hop_plan["hop"]
            subquery = hop_plan["subquery"]
            hop_type = hop_plan["type"]
            
            logger.info(f"Executing hop {hop_number}: {subquery}")
            
            # Check if we have cached results for this hop
            cache_key = f"hop_{hop_number}_{hash(subquery)}"
            if cache_key in self.hop_cache:
                logger.info(f"Using cached result for hop {hop_number}")
                return self.hop_cache[cache_key]
            
            # Execute based on hop type
            if hop_type == "direct":
                result = await self._execute_direct_hop(subquery, context, retrieval_service)
            elif hop_type == "filter":
                result = await self._execute_filter_hop(subquery, context, retrieval_service)
            elif hop_type == "retrieve":
                result = await self._execute_retrieve_hop(subquery, context, retrieval_service)
            elif hop_type == "extract":
                result = await self._execute_extract_hop(subquery, context, retrieval_service)
            elif hop_type == "compare":
                result = await self._execute_compare_hop(subquery, context, retrieval_service)
            else:
                result = await self._execute_direct_hop(subquery, context, retrieval_service)
            
            # Cache the result
            self.hop_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing hop {hop_plan.get('hop', 'unknown')}: {e}")
            return {
                "hop": hop_plan.get("hop", 0),
                "subquery": hop_plan.get("subquery", ""),
                "result": None,
                "error": str(e),
                "sources": []
            }
    
    async def _execute_direct_hop(self, subquery: str, context: Dict[str, Any], 
                                 retrieval_service) -> Dict[str, Any]:
        """Execute a direct retrieval hop"""
        tenant_id = context.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id required for retrieval")
        
        results = await retrieval_service.retrieve_documents(subquery, tenant_id)
        
        return {
            "hop_type": "direct",
            "subquery": subquery,
            "result": results,
            "sources": results,
            "entities": self._extract_entities_from_results(results)
        }
    
    async def _execute_filter_hop(self, subquery: str, context: Dict[str, Any], 
                                 retrieval_service) -> Dict[str, Any]:
        """Execute a filtering hop"""
        # Get previous results
        previous_results = context.get("previous_results", [])
        
        # Apply filtering logic (simplified)
        filtered_results = []
        for result in previous_results:
            if self._matches_filter_criteria(result, subquery):
                filtered_results.append(result)
        
        return {
            "hop_type": "filter",
            "subquery": subquery,
            "result": filtered_results,
            "sources": filtered_results,
            "entities": self._extract_entities_from_results(filtered_results)
        }
    
    async def _execute_retrieve_hop(self, subquery: str, context: Dict[str, Any], 
                                   retrieval_service) -> Dict[str, Any]:
        """Execute a retrieval hop"""
        return await self._execute_direct_hop(subquery, context, retrieval_service)
    
    async def _execute_extract_hop(self, subquery: str, context: Dict[str, Any], 
                                  retrieval_service) -> Dict[str, Any]:
        """Execute an extraction hop"""
        previous_results = context.get("previous_results", [])
        
        # Extract specific information (simplified)
        extracted_info = []
        for result in previous_results:
            extracted = self._extract_specific_info(result, subquery)
            if extracted:
                extracted_info.append(extracted)
        
        return {
            "hop_type": "extract",
            "subquery": subquery,
            "result": extracted_info,
            "sources": previous_results,
            "entities": self._extract_entities_from_results(extracted_info)
        }
    
    async def _execute_compare_hop(self, subquery: str, context: Dict[str, Any], 
                                  retrieval_service) -> Dict[str, Any]:
        """Execute a comparison hop"""
        previous_results = context.get("previous_results", [])
        
        # Simple comparison logic
        comparison_result = self._compare_results(previous_results, subquery)
        
        return {
            "hop_type": "compare",
            "subquery": subquery,
            "result": comparison_result,
            "sources": previous_results,
            "entities": []
        }
    
    def _matches_filter_criteria(self, result: Dict[str, Any], filter_query: str) -> bool:
        """Check if a result matches filter criteria"""
        text = result.get("text", "").lower()
        filter_query_lower = filter_query.lower()
        
        # Simple keyword matching
        keywords = filter_query_lower.split()
        return any(keyword in text for keyword in keywords)
    
    def _extract_specific_info(self, result: Dict[str, Any], extraction_query: str) -> Dict[str, Any]:
        """Extract specific information from a result"""
        text = result.get("text", "")
        
        # Simple extraction based on common patterns
        if "date" in extraction_query.lower():
            # Extract dates
            import re
            dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
            if dates:
                return {"type": "date", "value": dates[0], "source": result}
        
        if "email" in extraction_query.lower():
            # Extract emails
            import re
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if emails:
                return {"type": "email", "value": emails[0], "source": result}
        
        return None
    
    def _compare_results(self, results: List[Dict[str, Any]], comparison_query: str) -> Dict[str, Any]:
        """Compare multiple results"""
        if len(results) < 2:
            return {"comparison": "insufficient_data", "details": "Need at least 2 results to compare"}
        
        # Simple comparison
        return {
            "comparison": "basic_comparison",
            "count": len(results),
            "details": f"Found {len(results)} results for comparison"
        }
    
    def _extract_entities_from_results(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract entities from results"""
        entities = []
        for result in results:
            metadata = result.get("metadata", {})
            result_entities = metadata.get("entities", [])
            entities.extend(result_entities)
        
        return list(set(entities))  # Remove duplicates
    
    def clear_cache(self):
        """Clear the hop cache"""
        self.hop_cache.clear()
        logger.info("Hop cache cleared")
