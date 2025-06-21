"""
Ollama integration for the LLM client.
Provides support for local Ollama models.
"""

import json
import logging
from typing import Dict, Any, Optional, List
import httpx

from .types import LLMRequest, LLMResponse


logger = logging.getLogger(__name__)


class OllamaProvider:
    """Provider for Ollama local models."""
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 default_model: str = "qwen3:14b"):
        """Initialize Ollama provider."""
        self.base_url = base_url
        self.default_model = default_model
        self.timeout = 300.0  # Much longer timeout for large models
        
    async def check_health(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available models in Ollama."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Ollama."""
        
        # Use model from request or default
        model = request.model if request.model != "claude-3-sonnet-20240229" else self.default_model
        
        # Check if model contains 'qwen', otherwise use default
        if 'qwen' not in model.lower() and model not in await self.list_models():
            logger.warning(f"Model {model} not found, using default: {self.default_model}")
            model = self.default_model
        
        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": self._format_prompt(request),
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Clean the response content
                content = data.get("response", "")
                cleaned_content = self._clean_response_content(content)
                
                return LLMResponse(
                    content=cleaned_content,
                    model=model,
                    provider="ollama",
                    usage={
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                    },
                    success=True,
                    response_time=data.get("total_duration", 0) / 1e9  # Convert nanoseconds to seconds
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e}")
            return LLMResponse(
                content="",
                model=model,
                provider="ollama",
                success=False,
                error=f"HTTP {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return LLMResponse(
                content="",
                model=model,
                provider="ollama",
                success=False,
                error=str(e)
            )
    
    def _format_prompt(self, request: LLMRequest) -> str:
        """Format prompt for Ollama, including system prompt if provided."""
        if request.system_prompt:
            # Qwen models respond well to this format
            return f"""System: {request.system_prompt}

User: {request.prompt}

Assistant:"""
        else:
            return request.prompt
    
    def _clean_response_content(self, content: str) -> str:
        """Clean response content by removing thinking tokens and unwanted artifacts."""
        if not content:
            return content
        
        # Remove thinking tokens that some Qwen models produce
        if "<think>" in content:
            # Find the end of thinking section
            think_end = content.find("</think>")
            if think_end != -1:
                content = content[think_end + 8:].strip()
            else:
                # If no closing tag, remove everything from <think> onwards until we find actual content
                think_start = content.find("<think>")
                if think_start == 0:
                    # Thinking is at the start, try to find where actual content begins
                    lines = content.split('\n')
                    clean_lines = []
                    in_thinking = True
                    for line in lines:
                        if "<think>" in line:
                            in_thinking = True
                            continue
                        if in_thinking and (line.strip() == "" or line.startswith("好的") or line.startswith("用户") or "JSON" in line and "返回" in line):
                            continue
                        if line.strip() and not line.startswith("好的") and not line.startswith("用户"):
                            in_thinking = False
                        if not in_thinking:
                            clean_lines.append(line)
                    content = '\n'.join(clean_lines).strip()
        
        # Remove other common artifacts
        content = content.strip()
        
        # If content still starts with Chinese thinking text, try to extract JSON or meaningful content
        if content and (content.startswith("好的") or content.startswith("用户")):
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and (line.startswith('{') or line.startswith('[') or 
                           (not line.startswith("好的") and not line.startswith("用户") and len(line) > 10)):
                    content = '\n'.join(lines[i:]).strip()
                    break
        
        return content