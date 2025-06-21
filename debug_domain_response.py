#!/usr/bin/env python3
"""
Debug the specific domain advisor response
"""
import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest


async def debug_domain_response():
    """Debug the specific domain advisor response."""
    print("🔍 Debugging domain advisor response...")
    
    # Initialize LLM client with Ollama
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    
    client = LLMClient(config)
    
    # Get the problematic domain advisor response
    system_prompt = """You are a Domain Advisor Agent. Return ONLY a valid JSON object with these exact fields:
- domain_model: object with entities, relationships, business_rules arrays
- technical_specifications: object with authentication, data_architecture, security_measures
- user_personas: array of user types

Return only JSON, no markdown, no explanation."""

    user_prompt = """Analyze: Users can create tasks, team collaboration, secure data, mobile support.
Domain: task_management"""

    request = LLMRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen:7b",
        temperature=0.1,
        max_tokens=800
    )
    
    response = await client.generate_response(request)
    
    if response.success:
        print("Raw response:")
        print(f"'{response.content}'")
        print()
        
        # Test direct JSON parsing
        try:
            direct_result = json.loads(response.content)
            print(f"✅ Direct JSON parsing worked: {type(direct_result)}")
            print(f"Keys: {list(direct_result.keys()) if isinstance(direct_result, dict) else 'Not a dict'}")
        except json.JSONDecodeError as e:
            print(f"❌ Direct JSON parsing failed: {e}")
            
            # Test the extraction method
            try:
                extracted_result = client._extract_json_from_response(response.content)
                print(f"Extraction result type: {type(extracted_result)}")
                
                if isinstance(extracted_result, list):
                    print(f"❌ Bug confirmed - got list with {len(extracted_result)} items")
                    if len(extracted_result) > 0:
                        print(f"First item type: {type(extracted_result[0])}")
                        print(f"First item: {extracted_result[0]}")
                elif isinstance(extracted_result, dict):
                    print(f"✅ Got dict with keys: {list(extracted_result.keys())}")
                    
            except Exception as e:
                print(f"❌ Extraction failed: {e}")
    else:
        print(f"❌ LLM request failed: {response.error}")


if __name__ == "__main__":
    asyncio.run(debug_domain_response())