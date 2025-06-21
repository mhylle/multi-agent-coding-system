#!/usr/bin/env python3
"""Quick test to verify basic functionality."""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest

async def quick_test():
    print('🧪 Quick test with qwen3:14b...')
    config = {
        'default_provider': 'ollama',
        'ollama_base_url': 'http://localhost:11434',
        'enable_ollama': True
    }
    client = LLMClient(config)
    
    request = LLMRequest(
        prompt='Return only this JSON: {"test": "success"}',
        system_prompt='Return only valid JSON.',
        model='qwen3:14b',
        temperature=0.1,
        max_tokens=100
    )
    
    print("Making request...")
    response = await client.generate_response(request)
    print(f'Success: {response.success}')
    if response.success:
        print(f'Content: {response.content[:200]}')
        print(f'Time: {response.response_time:.2f}s')
    else:
        print(f'Error: {response.error}')

if __name__ == "__main__":
    asyncio.run(quick_test())