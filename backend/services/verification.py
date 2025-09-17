"""
Verification service for claim validation and evidence checking
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
import asyncio

logger = logging.getLogger(__name__)

class VerificationService:
    """Service for verifying claims and checking evidence"""
    
    def __init__(self):
        self.similarity_threshold = 0.7
        self.reranker_threshold = 0.5
    
    async def verify_claims(self, answer: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify claims in the answer against sources"""
        try:
            if not answer or not sources:
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "unverified_claims": [],
                    "evidence": []
                }
            
            # Extract claims from answer
            claims = self._extract_claims(answer)
            
            if not claims:
                return {
                    "verified": True,
                    "confidence": 1.0,
                    "unverified_claims": [],
                    "evidence": []
                }
            
            # Verify each claim
            verified_claims = []
            unverified_claims = []
            evidence = []
            
            for claim in claims:
                is_verified, claim_evidence = await self._verify_single_claim(claim, sources)
                
                if is_verified:
                    verified_claims.append(claim)
                    evidence.extend(claim_evidence)
                else:
                    unverified_claims.append(claim)
            
            # Calculate overall verification confidence
            verification_confidence = len(verified_claims) / len(claims) if claims else 1.0
            
            return {
                "verified": len(unverified_claims) == 0,
                "confidence": verification_confidence,
                "verified_claims": verified_claims,
                "unverified_claims": unverified_claims,
                "evidence": evidence,
                "total_claims": len(claims)
            }
            
        except Exception as e:
            logger.error(f"Error verifying claims: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "unverified_claims": [],
                "evidence": [],
                "error": str(e)
            }
    
    def _extract_claims(self, answer: str) -> List[str]:
        """Extract factual claims from the answer"""
        try:
            claims = []
            
            # Split answer into sentences
            sentences = re.split(r'[.!?]+', answer)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Skip questions and conversational phrases
                if (sentence.endswith('?') or 
                    sentence.lower().startswith(('i think', 'i believe', 'i feel', 'i guess'))):
                    continue
                
                # Look for factual statements
                if self._is_factual_claim(sentence):
                    claims.append(sentence)
            
            return claims
            
        except Exception as e:
            logger.error(f"Error extracting claims: {e}")
            return []
    
    def _is_factual_claim(self, sentence: str) -> bool:
        """Check if a sentence is a factual claim"""
        # Simple heuristics for factual claims
        factual_indicators = [
            r'\b(is|are|was|were|has|have|had)\b',
            r'\b(contains|includes|shows|indicates|suggests)\b',
            r'\b(according to|based on|the data shows)\b',
            r'\b\d+\b',  # Contains numbers
            r'\b(expires|expired|valid|invalid)\b',
            r'\b(domain|email|date|time|period)\b'
        ]
        
        sentence_lower = sentence.lower()
        
        # Must contain at least one factual indicator
        has_indicators = any(re.search(pattern, sentence_lower) for pattern in factual_indicators)
        
        # Must not be purely conversational
        conversational_phrases = [
            'i apologize', 'i\'m sorry', 'i don\'t know', 'i can\'t',
            'please', 'thank you', 'you\'re welcome'
        ]
        
        is_conversational = any(phrase in sentence_lower for phrase in conversational_phrases)
        
        return has_indicators and not is_conversational and len(sentence.split()) >= 3
    
    async def _verify_single_claim(self, claim: str, sources: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Verify a single claim against sources"""
        try:
            evidence = []
            
            for source in sources:
                source_text = source.get("text", "").lower()
                claim_lower = claim.lower()
                
                # Check for direct text overlap
                if self._has_text_overlap(claim_lower, source_text):
                    evidence.append({
                        "source": source,
                        "type": "direct_match",
                        "confidence": 1.0,
                        "matched_text": self._extract_matched_text(claim_lower, source_text)
                    })
                    continue
                
                # Check for semantic similarity
                similarity = await self._calculate_semantic_similarity(claim, source_text)
                if similarity >= self.similarity_threshold:
                    evidence.append({
                        "source": source,
                        "type": "semantic_match",
                        "confidence": similarity,
                        "matched_text": self._extract_similar_text(claim_lower, source_text)
                    })
            
            # Check for entity matches
            entity_evidence = await self._check_entity_matches(claim, sources)
            evidence.extend(entity_evidence)
            
            # Consider claim verified if we have sufficient evidence
            is_verified = len(evidence) > 0 and any(
                e["confidence"] >= self.similarity_threshold for e in evidence
            )
            
            return is_verified, evidence
            
        except Exception as e:
            logger.error(f"Error verifying single claim: {e}")
            return False, []
    
    def _has_text_overlap(self, claim: str, source_text: str) -> bool:
        """Check if claim has significant text overlap with source"""
        try:
            # Extract key terms from claim
            claim_terms = set(re.findall(r'\b\w+\b', claim))
            source_terms = set(re.findall(r'\b\w+\b', source_text))
            
            # Calculate overlap ratio
            if not claim_terms:
                return False
            
            overlap = len(claim_terms & source_terms)
            overlap_ratio = overlap / len(claim_terms)
            
            return overlap_ratio >= 0.3  # At least 30% term overlap
            
        except Exception as e:
            logger.error(f"Error checking text overlap: {e}")
            return False
    
    def _extract_matched_text(self, claim: str, source_text: str) -> str:
        """Extract the matched text from source"""
        try:
            # Find the best matching substring
            claim_words = claim.split()
            if len(claim_words) < 3:
                return source_text[:200] + "..." if len(source_text) > 200 else source_text
            
            # Look for consecutive word matches
            best_match = ""
            best_length = 0
            
            for i in range(len(source_text.split()) - len(claim_words) + 1):
                source_words = source_text.split()[i:i + len(claim_words)]
                source_phrase = " ".join(source_words).lower()
                
                if claim in source_phrase:
                    if len(source_phrase) > best_length:
                        best_match = source_phrase
                        best_length = len(source_phrase)
            
            return best_match if best_match else source_text[:200] + "..."
            
        except Exception as e:
            logger.error(f"Error extracting matched text: {e}")
            return source_text[:200] + "..."
    
    def _extract_similar_text(self, claim: str, source_text: str) -> str:
        """Extract similar text from source"""
        try:
            # Find sentences that contain similar terms
            sentences = re.split(r'[.!?]+', source_text)
            claim_terms = set(re.findall(r'\b\w+\b', claim))
            
            best_sentence = ""
            best_score = 0
            
            for sentence in sentences:
                sentence_terms = set(re.findall(r'\b\w+\b', sentence.lower()))
                overlap = len(claim_terms & sentence_terms)
                
                if overlap > best_score:
                    best_score = overlap
                    best_sentence = sentence.strip()
            
            return best_sentence if best_sentence else source_text[:200] + "..."
            
        except Exception as e:
            logger.error(f"Error extracting similar text: {e}")
            return source_text[:200] + "..."
    
    async def _calculate_semantic_similarity(self, claim: str, source_text: str) -> float:
        """Calculate semantic similarity between claim and source text"""
        try:
            # Simple word-based similarity (in production, use embedding similarity)
            claim_words = set(re.findall(r'\b\w+\b', claim.lower()))
            source_words = set(re.findall(r'\b\w+\b', source_text.lower()))
            
            if not claim_words or not source_words:
                return 0.0
            
            intersection = len(claim_words & source_words)
            union = len(claim_words | source_words)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    async def _check_entity_matches(self, claim: str, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for entity matches between claim and sources"""
        try:
            evidence = []
            
            # Extract entities from claim
            claim_entities = self._extract_entities(claim)
            
            for source in sources:
                source_entities = source.get("metadata", {}).get("entities", [])
                
                # Check for entity overlap
                if claim_entities and source_entities:
                    overlap = set(claim_entities) & set(source_entities)
                    if overlap:
                        evidence.append({
                            "source": source,
                            "type": "entity_match",
                            "confidence": len(overlap) / len(claim_entities),
                            "matched_entities": list(overlap)
                        })
            
            return evidence
            
        except Exception as e:
            logger.error(f"Error checking entity matches: {e}")
            return []
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        try:
            entities = []
            
            # Extract email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            entities.extend(emails)
            
            # Extract URLs
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            entities.extend(urls)
            
            # Extract capitalized words (potential entities)
            capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
            entities.extend(capitalized[:5])  # Limit to first 5
            
            # Extract numbers (dates, amounts, etc.)
            numbers = re.findall(r'\b\d+\b', text)
            entities.extend(numbers[:3])  # Limit to first 3
            
            return list(set(entities))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if verification service is healthy"""
        try:
            # Test with a simple verification
            test_claim = "This is a test claim"
            test_sources = [{"text": "This is a test source", "metadata": {}}]
            
            result = await self.verify_claims(test_claim, test_sources)
            return "verified" in result
            
        except Exception as e:
            logger.error(f"Verification service health check failed: {e}")
            return False
