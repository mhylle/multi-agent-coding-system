#!/usr/bin/env python3
"""
Test Domain Advisor with qwen2.5:14b model as requested
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest


async def test_domain_advisor_14b():
    """Test Domain Advisor with the larger qwen2.5:14b model."""
    print("🧪 Testing Domain Advisor with qwen3:14b (as specifically requested)...")
    
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    
    client = LLMClient(config)
    
    # Use the specifically requested qwen3:14b model
    system_prompt = """Analyze business requirements and return valid JSON only.

Required JSON structure:
{
  "domain_model": {"entities": [], "relationships": [], "business_rules": []},
  "technical_specifications": {"authentication": {}, "data_architecture": {}, "security_measures": {}},
  "user_personas": []
}

Return only the JSON object, no other text."""

    user_prompt = """Task management system requirements:
- Users create/manage tasks
- Team collaboration features
- Secure data storage
- Mobile support

Analyze and return JSON only."""

    request = LLMRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen3:14b",  # Use the specifically requested qwen3:14b model
        temperature=0.1,
        max_tokens=1000
    )
    
    print("🤖 Sending request to qwen3:14b model...")
    print(f"   Model: {request.model}")
    
    response = await client.generate_response(request)
    
    if response.success:
        print("✅ Response received!")
        print(f"   Model: {response.model}")
        print(f"   Time: {response.response_time:.2f}s")
        print(f"   Content length: {len(response.content)} chars")
        
        # Parse the JSON response
        try:
            result = client._extract_json_from_response(response.content)
            
            if isinstance(result, dict) and "content" in result and "parsed" in result:
                print("❌ Got fallback result - JSON extraction failed")
                print(f"Raw response preview: {response.content[:300]}...")
                return False
            elif isinstance(result, dict):
                print("✅ Successfully parsed JSON response!")
                print(f"   Available fields: {list(result.keys())}")
                
                # Validate required fields
                required_fields = ["domain_model", "technical_specifications", "user_personas"]
                all_present = True
                
                for field in required_fields:
                    if field in result:
                        print(f"   ✅ {field}: Present")
                        
                        # Show some details for domain_model
                        if field == "domain_model" and isinstance(result[field], dict):
                            dm = result[field]
                            entities = dm.get('entities', [])
                            relationships = dm.get('relationships', [])
                            business_rules = dm.get('business_rules', [])
                            print(f"      - Entities: {len(entities)}")
                            print(f"      - Relationships: {len(relationships)}")
                            print(f"      - Business Rules: {len(business_rules)}")
                            
                        # Show some details for user_personas
                        elif field == "user_personas" and isinstance(result[field], list):
                            personas = result[field]
                            print(f"      - {len(personas)} personas identified")
                            for i, persona in enumerate(personas[:3]):  # Show first 3
                                if isinstance(persona, dict) and "name" in persona:
                                    print(f"      - {persona['name']}")
                                    
                    else:
                        print(f"   ❌ {field}: Missing")
                        all_present = False
                
                return all_present
            else:
                print(f"❌ Unexpected result type: {type(result)}")
                return False
                
        except Exception as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response preview: {response.content[:300]}...")
            return False
    else:
        print(f"❌ Generation failed: {response.error}")
        return False


async def main():
    """Main test function."""
    try:
        success = await test_domain_advisor_14b()
        if success:
            print("\n🎉 Domain Advisor + qwen3:14b test PASSED!")
            print("✅ The qwen3:14b model provides comprehensive analysis as requested")
        else:
            print("\n❌ Domain Advisor + qwen3:14b test FAILED!")
        return success
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)