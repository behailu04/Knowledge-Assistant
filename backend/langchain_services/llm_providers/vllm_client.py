"""
vLLM client integration for LangChain
"""
import json
import httpx
from typing import Any, Dict, List, Optional, AsyncGenerator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class VLLMClient(BaseChatModel):
    """vLLM client for LangChain integration"""
    
    base_url: str = Field(default="http://localhost:8000")
    model: str = Field(default="phi-3-mini")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1000)
    api_key: Optional[str] = Field(default=None)
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def _llm_type(self) -> str:
        return "vllm"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response from vLLM"""
        try:
            # Convert messages to vLLM format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            # Add stop sequences if provided
            if stop:
                payload["stop"] = stop
            
            # Make request to vLLM
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            with httpx.Client(timeout=300.0) as client:
                response = client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract response content
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    message = AIMessage(content=content)
                    generation = ChatGeneration(message=message)
                    
                    return ChatResult(generations=[generation])
                else:
                    raise ValueError("No response content found in vLLM response")
                    
        except Exception as e:
            logger.error(f"Error generating response from vLLM: {e}")
            raise
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async generate a response from vLLM"""
        try:
            # Convert messages to vLLM format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            # Add stop sequences if provided
            if stop:
                payload["stop"] = stop
            
            # Make async request to vLLM
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract response content
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    message = AIMessage(content=content)
                    generation = ChatGeneration(message=message)
                    
                    return ChatResult(generations=[generation])
                else:
                    raise ValueError("No response content found in vLLM response")
                    
        except Exception as e:
            logger.error(f"Error generating async response from vLLM: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a single prompt string"""
        prompt_parts = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                prompt_parts.append(f"System: {message.content}")
            elif isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {message.content}")
            else:
                prompt_parts.append(f"{message.content}")
        
        return "\n\n".join(prompt_parts)
    
    def health_check(self) -> Dict[str, Any]:
        """Check vLLM service health"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/health")
                response.raise_for_status()
                
                return {
                    "status": "healthy",
                    "base_url": self.base_url,
                    "model": self.model,
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            logger.error(f"vLLM health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "base_url": self.base_url,
                "model": self.model
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the vLLM model"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/v1/models")
                response.raise_for_status()
                
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    model_info = result["data"][0]
                    return {
                        "model_id": model_info.get("id"),
                        "object": model_info.get("object"),
                        "created": model_info.get("created"),
                        "owned_by": model_info.get("owned_by")
                    }
                else:
                    return {"error": "No model information available"}
                    
        except Exception as e:
            logger.error(f"Error getting vLLM model info: {e}")
            return {"error": str(e)}
