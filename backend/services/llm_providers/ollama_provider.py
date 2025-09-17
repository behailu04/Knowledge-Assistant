"""
Ollama LLM Provider
"""
import logging
import httpx
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class OllamaProvider:
    """Ollama API provider for LLM operations"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_response(self, prompt: str, temperature: float = 0.7, 
                              max_tokens: int = 1000) -> str:
        """Generate response using Ollama API"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return "I apologize, but I couldn't generate a response at this time."
                
        except Exception as e:
            logger.error(f"Error generating Ollama response: {e}")
            return "I apologize, but I couldn't generate a response at this time."
    
    async def health_check(self) -> bool:
        """Check if Ollama provider is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def list_models(self) -> list:
        """List available models in Ollama"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model to Ollama"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
