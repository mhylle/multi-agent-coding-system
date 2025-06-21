#!/usr/bin/env python3
"""
Debug JSON parsing issue
"""
import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest


async def debug_json_parsing():
    """Debug the JSON parsing issue."""
    print("🔍 Debugging JSON parsing...")
    
    # Initialize LLM client with Ollama
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    
    client = LLMClient(config)
    
    # Get a response from Ollama
    request = LLMRequest(
        prompt="Return a simple JSON object with just {\"test\": \"value\"}",
        model="qwen:7b",
        temperature=0.1,
        max_tokens=100
    )
    
    response = await client.generate_response(request)
    
    if response.success:
        print("Raw response:")
        print(f"'{response.content}'")
        print()
        
        # Test the JSON extraction method directly
        try:
            result = client._extract_json_from_response(response.content)
            print(f"Extracted result type: {type(result)}")
            print(f"Extracted result: {result}")
            
            if isinstance(result, list):
                print("❌ Result is a list - this is the bug!")
                if len(result) > 0:
                    print(f"First item: {result[0]}")
            elif isinstance(result, dict):
                print("✅ Result is a dict as expected")
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
    else:
        print(f"❌ LLM request failed: {response.error}")


if __name__ == "__main__":
    asyncio.run(debug_json_parsing())