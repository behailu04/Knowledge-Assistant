"""
OpenAI LLM Provider
"""
import logging
import openai
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OpenAIProvider:
    """OpenAI API provider for LLM operations"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=openai.api_key)
        self.model = "gpt-3.5-turbo"
    
    async def generate_response(self, prompt: str, temperature: float = 0.7, 
                              max_tokens: int = 1000) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return "I apologize, but I couldn't generate a response at this time."
    
    async def health_check(self) -> bool:
        """Check if OpenAI provider is healthy"""
        try:
            # Test with a simple request
            response = await self.generate_response("Hello", temperature=0.1, max_tokens=10)
            return len(response) > 0
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
