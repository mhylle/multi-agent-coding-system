"""
LLM client for integrating with various language model providers.
Provides unified interface with error handling, retries, and response parsing.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import asdict

from .types import LLMRequest, LLMResponse
from .ollama_client import OllamaProvider


logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified client for interacting with multiple LLM providers.
    Handles authentication, rate limiting, retries, and response parsing.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize LLM client with configuration."""
        self.config = config
        self.anthropic_api_key = config.get("anthropic_api_key")
        self.openai_api_key = config.get("openai_api_key")
        self.ollama_base_url = config.get("ollama_base_url", "http://localhost:11434")
        self.default_provider = config.get("default_provider", "anthropic")
        
        # Initialize Ollama provider if needed
        if self.default_provider == "ollama" or config.get("enable_ollama", False):
            self.ollama_provider = OllamaProvider(self.ollama_base_url)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        self.timeout = config.get("timeout", 60.0)
        
        # Rate limiting
        self.rate_limit_requests_per_minute = config.get("rate_limit_rpm", 50)
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window_start = time.time()
        
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response using the specified LLM.
        Handles provider routing, retries, and error handling.
        """
        provider = self._determine_provider(request.model)
        
        # Apply rate limiting
        await self._apply_rate_limiting()
        
        # Attempt request with retries
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                if provider == "anthropic":
                    response = await self._call_anthropic(request)
                elif provider == "openai":
                    response = await self._call_openai(request)
                elif provider == "ollama":
                    response = await self._call_ollama(request)
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
                
                response.response_time = time.time() - start_time
                response.request_id = request.request_id
                
                logger.info(f"LLM request successful: {request.request_id}, "
                           f"provider: {provider}, time: {response.response_time:.2f}s")
                
                return response
                
            except Exception as e:
                logger.warning(f"LLM request attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == self.max_retries - 1:
                    # Final attempt failed
                    return LLMResponse(
                        content="",
                        model=request.model,
                        provider=provider,
                        success=False,
                        error=f"Failed after {self.max_retries} attempts: {str(e)}",
                        request_id=request.request_id
                    )
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
    
    async def _call_anthropic(self, request: LLMRequest) -> LLMResponse:
        """Call Anthropic Claude API."""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.anthropic_api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Prepare the request payload
        payload = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [
                {"role": "user", "content": request.prompt}
            ]
        }
        
        if request.system_prompt:
            payload["system"] = request.system_prompt
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            return LLMResponse(
                content=data["content"][0]["text"],
                model=data["model"],
                provider="anthropic",
                usage=data.get("usage", {}),
                success=True
            )
    
    async def _call_openai(self, request: LLMRequest) -> LLMResponse:
        """Call OpenAI GPT API."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        payload = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                provider="openai", 
                usage=data.get("usage", {}),
                success=True
            )
    
    async def _call_ollama(self, request: LLMRequest) -> LLMResponse:
        """Call Ollama API."""
        if not hasattr(self, 'ollama_provider'):
            self.ollama_provider = OllamaProvider(self.ollama_base_url)
        
        return await self.ollama_provider.generate_response(request)
    
    def _determine_provider(self, model: str) -> str:
        """Determine which provider to use based on model name."""
        if "claude" in model.lower():
            return "anthropic"
        elif "gpt" in model.lower():
            return "openai"
        elif "qwen" in model.lower() or "ollama" in model.lower():
            return "ollama"
        else:
            return self.default_provider
    
    async def _apply_rate_limiting(self):
        """Apply rate limiting to prevent exceeding API limits."""
        current_time = time.time()
        
        # Reset window if needed
        if current_time - self.rate_limit_window_start >= 60:
            self.request_count = 0
            self.rate_limit_window_start = current_time
        
        # Check if we need to wait
        if self.request_count >= self.rate_limit_requests_per_minute:
            wait_time = 60 - (current_time - self.rate_limit_window_start)
            if wait_time > 0:
                logger.info(f"Rate limiting: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.rate_limit_window_start = time.time()
        
        self.request_count += 1
        self.last_request_time = current_time
    
    async def parse_structured_response(self, response: LLMResponse, 
                                      expected_format: str = "json") -> Dict[str, Any]:
        """
        Parse structured response from LLM.
        Handles JSON extraction and validation.
        """
        if not response.success:
            raise ValueError(f"Cannot parse failed response: {response.error}")
        
        content = response.content.strip()
        
        if expected_format == "json":
            return self._extract_json_from_response(content)
        else:
            raise ValueError(f"Unsupported format: {expected_format}")
    
    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """Extract JSON from LLM response content."""
        # First try direct JSON parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        json_start = content.find("```json")
        if json_start != -1:
            json_start += len("```json")
            json_end = content.find("```", json_start)
            if json_end != -1:
                json_content = content[json_start:json_end].strip()
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    pass
        
        # Try to find complete JSON object (prioritize objects over arrays)
        # Look for main JSON object starting with {
        brace_start = content.find("{")
        if brace_start != -1:
            bracket_count = 0
            start_found = False
            in_string = False
            escape_next = False
            
            for i, char in enumerate(content[brace_start:], brace_start):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == "\\" and in_string:
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == "{":
                        if not start_found:
                            start_found = True
                        bracket_count += 1
                    elif char == "}":
                        bracket_count -= 1
                        if bracket_count == 0 and start_found:
                            json_content = content[brace_start:i+1]
                            try:
                                return json.loads(json_content)
                            except json.JSONDecodeError:
                                # Continue looking for another complete JSON object
                                bracket_count = 0
                                start_found = False
                                continue
        
        # If no object found, try arrays
        array_start = content.find("[")
        if array_start != -1:
            bracket_count = 0
            start_found = False
            
            for i, char in enumerate(content[array_start:], array_start):
                if char == "[":
                    if not start_found:
                        start_found = True
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1
                    if bracket_count == 0 and start_found:
                        json_content = content[array_start:i+1]
                        try:
                            return json.loads(json_content)
                        except json.JSONDecodeError:
                            break
        
        # If all else fails, return the content as a string result
        return {"content": content, "parsed": False}
    
    async def generate_with_schema(self, request: LLMRequest, 
                                 schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response that conforms to a specific schema.
        Includes schema validation and retry logic.
        """
        # Add schema instruction to prompt
        schema_instruction = f"\n\nPlease respond with valid JSON that matches this schema:\n{json.dumps(schema, indent=2)}"
        
        enhanced_request = LLMRequest(
            prompt=request.prompt + schema_instruction,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
            context=request.context,
            request_id=request.request_id
        )
        
        response = await self.generate_response(enhanced_request)
        
        if response.success:
            try:
                parsed_data = await self.parse_structured_response(response)
                # TODO: Add schema validation here
                return parsed_data
            except Exception as e:
                logger.error(f"Failed to parse structured response: {e}")
                return {"error": f"Parse failed: {e}", "raw_content": response.content}
        else:
            return {"error": response.error}


# Global LLM client instance
_llm_client: Optional[LLMClient] = None


def initialize_llm_client(config: Dict[str, Any]) -> LLMClient:
    """Initialize the global LLM client."""
    global _llm_client
    _llm_client = LLMClient(config)
    return _llm_client


def get_llm_client() -> LLMClient:
    """Get the global LLM client instance."""
    if _llm_client is None:
        raise RuntimeError("LLM client not initialized. Call initialize_llm_client() first.")
    return _llm_client