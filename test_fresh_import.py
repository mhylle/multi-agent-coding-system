#!/usr/bin/env python3
"""
Test with fresh import to avoid caching issues
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import fresh
from core.llm_client import LLMClient
from core.types import LLMRequest


async def test_fresh():
    """Test with fresh import."""
    print("🧪 Testing with fresh import...")
    
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    
    client = LLMClient(config)
    
    # Test the extraction method directly with a simple case
    test_content = '''```json
{
  "domain_model": {
    "entities": [{"name": "User"}],
    "relationships": [],
    "business_rules": []
  },
  "technical_specifications": {
    "authentication": {"method": "password"}
  },
  "user_personas": [
    {"name": "Test User"}
  ]
}
```'''
    
    print("Testing extraction method directly...")
    result = client._extract_json_from_response(test_content)
    
    print(f"Result type: {type(result)}")
    
    if isinstance(result, dict):
        if "content" in result and "parsed" in result:
            print("❌ Got fallback result")
            return False
        else:
            print("✅ Got proper JSON dict!")
            print(f"Keys: {list(result.keys())}")
            return True
    else:
        print(f"❌ Wrong type: {type(result)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_fresh())
    print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")