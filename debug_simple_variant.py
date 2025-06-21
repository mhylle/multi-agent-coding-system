#!/usr/bin/env python3
"""
Debug the simple variant JSON parsing failure
"""
import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest
from core.prompt_manager import get_prompt_manager


async def debug_simple_variant():
    """Debug exactly what's wrong with the simple variant."""
    print("🔍 Debugging simple variant JSON parsing failure...")
    
    # Initialize LLM client
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    client = LLMClient(config)
    
    # Get prompt manager
    prompt_manager = get_prompt_manager()
    
    # Test simple variant
    simple_system = prompt_manager.get_system_prompt("domain_advisor", "simple")
    simple_user = prompt_manager.format_user_prompt(
        "domain_advisor", 
        "simple",
        requirements="Users can create tasks and collaborate in teams"
    )
    
    model_config = prompt_manager.get_model_config("domain_advisor")
    
    request = LLMRequest(
        prompt=simple_user,
        system_prompt=simple_system,
        model=model_config.get("model", "qwen3:14b"),
        temperature=model_config.get("temperature", 0.1),
        max_tokens=1000
    )
    
    print(f"System prompt:\n'{simple_system}'\n")
    print(f"User prompt:\n'{simple_user}'\n")
    
    response = await client.generate_response(request)
    
    if response.success:
        print("✅ Response received!")
        print(f"Raw response content:\n'{response.content}'\n")
        
        # Test our JSON extraction
        extracted = client._extract_json_from_response(response.content)
        print(f"Extracted result type: {type(extracted)}")
        print(f"Extracted result: {extracted}\n")
        
        # Test direct JSON parsing
        try:
            direct_json = json.loads(response.content.strip())
            print(f"✅ Direct JSON parsing successful: {type(direct_json)}")
        except json.JSONDecodeError as e:
            print(f"❌ Direct JSON parsing failed: {e}")
            
            # Try to find JSON in the content
            content = response.content.strip()
            if '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_part = content[start:end]
                print(f"Attempting to parse: '{json_part}'")
                try:
                    parsed = json.loads(json_part)
                    print(f"✅ Manual extraction successful: {type(parsed)}")
                    print(f"Keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'Not a dict'}")
                except json.JSONDecodeError as e2:
                    print(f"❌ Manual extraction also failed: {e2}")
    else:
        print(f"❌ Response failed: {response.error}")


if __name__ == "__main__":
    asyncio.run(debug_simple_variant())