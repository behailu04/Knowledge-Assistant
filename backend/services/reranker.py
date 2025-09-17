"""
Reranking service for improving retrieval quality
"""
import logging
from typing import List, Dict, Any
import asyncio
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class RerankerService:
    """Service for reranking retrieved documents"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    async def rerank(self, query: str, candidates: List[Dict[str, Any]], 
                    top_n: int = 5) -> List[Dict[str, Any]]:
        """Rerank candidates using multiple signals"""
        try:
            if not candidates:
                return []
            
            if len(candidates) <= top_n:
                return candidates
            
            logger.info(f"Reranking {len(candidates)} candidates to top {top_n}")
            
            # Extract texts for reranking
            texts = [candidate["text"] for candidate in candidates]
            
            # Compute multiple ranking signals
            tfidf_scores = await self._compute_tfidf_scores(query, texts)
            length_scores = self._compute_length_scores(texts)
            position_scores = self._compute_position_scores(candidates)
            entity_scores = await self._compute_entity_scores(query, candidates)
            
            # Combine scores
            combined_scores = []
            for i, candidate in enumerate(candidates):
                # Weighted combination of different signals
                combined_score = (
                    0.4 * candidate["score"] +  # Original similarity score
                    0.3 * tfidf_scores[i] +     # TF-IDF similarity
                    0.1 * length_scores[i] +    # Length preference
                    0.1 * position_scores[i] +  # Position preference
                    0.1 * entity_scores[i]      # Entity matching
                )
                
                combined_scores.append((i, combined_score))
            
            # Sort by combined score
            combined_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top N results
            reranked_candidates = []
            for rank, (original_idx, score) in enumerate(combined_scores[:top_n]):
                candidate = candidates[original_idx].copy()
                candidate["rerank_score"] = score
                candidate["rerank_rank"] = rank + 1
                reranked_candidates.append(candidate)
            
            logger.info(f"Reranked to {len(reranked_candidates)} candidates")
            return reranked_candidates
            
        except Exception as e:
            logger.error(f"Error reranking candidates: {e}")
            return candidates[:top_n]  # Fallback to original ranking
    
    async def _compute_tfidf_scores(self, query: str, texts: List[str]) -> List[float]:
        """Compute TF-IDF similarity scores"""
        try:
            # Combine query and texts
            all_texts = [query] + texts
            
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Get query vector (first row)
            query_vector = tfidf_matrix[0:1]
            
            # Get text vectors (remaining rows)
            text_vectors = tfidf_matrix[1:]
            
            # Compute cosine similarities
            similarities = cosine_similarity(query_vector, text_vectors)[0]
            
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"Error computing TF-IDF scores: {e}")
            return [0.0] * len(texts)
    
    def _compute_length_scores(self, texts: List[str]) -> List[float]:
        """Compute length-based scores (prefer medium-length texts)"""
        try:
            scores = []
            lengths = [len(text.split()) for text in texts]
            
            if not lengths:
                return []
            
            # Optimal length range (100-500 words)
            optimal_min, optimal_max = 100, 500
            
            for length in lengths:
                if optimal_min <= length <= optimal_max:
                    # Perfect length
                    score = 1.0
                elif length < optimal_min:
                    # Too short
                    score = length / optimal_min
                else:
                    # Too long
                    score = optimal_max / length
                
                scores.append(score)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error computing length scores: {e}")
            return [0.5] * len(texts)
    
    def _compute_position_scores(self, candidates: List[Dict[str, Any]]) -> List[float]:
        """Compute position-based scores (prefer earlier in document)"""
        try:
            scores = []
            
            for candidate in candidates:
                metadata = candidate.get("metadata", {})
                start_pos = metadata.get("start_pos", 0)
                
                # Prefer chunks that appear earlier in the document
                # This is a simple heuristic - in production, use more sophisticated logic
                if start_pos < 1000:
                    score = 1.0
                elif start_pos < 5000:
                    score = 0.8
                else:
                    score = 0.6
                
                scores.append(score)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error computing position scores: {e}")
            return [0.5] * len(candidates)
    
    async def _compute_entity_scores(self, query: str, candidates: List[Dict[str, Any]]) -> List[float]:
        """Compute entity matching scores"""
        try:
            # Extract entities from query (simplified)
            query_entities = self._extract_entities(query)
            
            scores = []
            for candidate in candidates:
                metadata = candidate.get("metadata", {})
                chunk_entities = metadata.get("entities", [])
                
                if not query_entities or not chunk_entities:
                    score = 0.5
                else:
                    # Compute entity overlap
                    query_entities_lower = [e.lower() for e in query_entities]
                    chunk_entities_lower = [e.lower() for e in chunk_entities]
                    
                    overlap = len(set(query_entities_lower) & set(chunk_entities_lower))
                    total = len(set(query_entities_lower) | set(chunk_entities_lower))
                    
                    score = overlap / total if total > 0 else 0.5
                
                scores.append(score)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error computing entity scores: {e}")
            return [0.5] * len(candidates)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (simplified)"""
        try:
            import re
            
            entities = []
            
            # Extract capitalized words (potential entities)
            capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
            entities.extend(capitalized)
            
            # Extract email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            entities.extend(emails)
            
            # Extract URLs
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            entities.extend(urls)
            
            # Remove duplicates and return
            return list(set(entities))
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def rerank_with_cross_encoder(self, query: str, candidates: List[Dict[str, Any]], 
                                      top_n: int = 5) -> List[Dict[str, Any]]:
        """Rerank using a cross-encoder model (more accurate but slower)"""
        try:
            # This would use a cross-encoder model like sentence-transformers
            # For now, fall back to the basic reranking
            return await self.rerank(query, candidates, top_n)
            
        except Exception as e:
            logger.error(f"Error in cross-encoder reranking: {e}")
            return await self.rerank(query, candidates, top_n)
    
    async def health_check(self) -> bool:
        """Check if reranker service is healthy"""
        try:
            # Test with a simple reranking task
            test_candidates = [
                {"text": "test document", "score": 0.8, "metadata": {}},
                {"text": "another test", "score": 0.7, "metadata": {}}
            ]
            
            result = await self.rerank("test query", test_candidates, 2)
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Reranker service health check failed: {e}")
            return False
