"""
Mock LLM Provider for development and testing
"""
import logging
import asyncio
import random
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MockProvider:
    """Mock LLM provider for development and testing"""
    
    def __init__(self):
        self.responses = [
            "Based on the provided information, I can help you with that.",
            "Let me analyze the available data to provide you with an accurate answer.",
            "I found relevant information that should address your question.",
            "After reviewing the sources, here's what I can tell you:",
            "The information suggests the following:"
        ]
    
    async def generate_response(self, prompt: str, temperature: float = 0.7, 
                              max_tokens: int = 1000) -> str:
        """Generate mock response"""
        try:
            # Simulate API delay
            await asyncio.sleep(0.1)
            
            # Generate mock response based on prompt
            if "step by step" in prompt.lower() or "think through" in prompt.lower():
                # Chain-of-Thought response
                response = self._generate_cot_response(prompt)
            else:
                # Direct response
                response = self._generate_direct_response(prompt)
            
            # Truncate to max_tokens (rough approximation)
            words = response.split()
            if len(words) > max_tokens // 2:  # Rough word to token ratio
                response = " ".join(words[:max_tokens // 2]) + "..."
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating mock response: {e}")
            return "I apologize, but I couldn't generate a response at this time."
    
    def _generate_cot_response(self, prompt: str) -> str:
        """Generate Chain-of-Thought mock response"""
        base_response = random.choice(self.responses)
        
        cot_steps = [
            "1. First, I need to identify the key information in the question.",
            "2. Next, I'll look for relevant data in the provided sources.",
            "3. Then, I'll analyze how the information relates to the question.",
            "4. Finally, I'll synthesize the findings into a comprehensive answer."
        ]
        
        reasoning = "\n".join(cot_steps)
        answer = f"Based on my analysis, here's what I found: The information suggests that the answer involves multiple factors that need to be considered together."
        
        return f"{reasoning}\n\nAnswer: {answer}"
    
    def _generate_direct_response(self, prompt: str) -> str:
        """Generate direct mock response"""
        base_response = random.choice(self.responses)
        
        # Extract question from prompt
        if "Question:" in prompt:
            question_part = prompt.split("Question:")[-1].strip()
            if "?" in question_part:
                question = question_part.split("?")[0] + "?"
            else:
                question = question_part
        else:
            question = "your question"
        
        # Generate contextual response
        if "which" in question.lower():
            response = f"{base_response} Regarding {question.lower()}, I found several relevant options that could apply."
        elif "what" in question.lower():
            response = f"{base_response} To answer {question.lower()}, the information indicates specific details that are relevant."
        elif "how" in question.lower():
            response = f"{base_response} For {question.lower()}, the process involves several steps that I can explain."
        elif "when" in question.lower():
            response = f"{base_response} Regarding {question.lower()}, the timing information suggests specific dates or periods."
        else:
            response = f"{base_response} I can provide information about {question.lower()} based on the available data."
        
        return response
    
    async def health_check(self) -> bool:
        """Check if mock provider is healthy"""
        try:
            response = await self.generate_response("test", temperature=0.1, max_tokens=10)
            return len(response) > 0
        except Exception as e:
            logger.error(f"Mock provider health check failed: {e}")
            return False
