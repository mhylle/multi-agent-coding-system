#!/usr/bin/env python3
"""
Simple test of Domain Advisor Agent with Ollama integration.
"""
import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import initialize_llm_client
from core.types import LLMRequest


async def test_domain_advisor_llm_directly():
    """Test Domain Advisor prompts directly with Ollama LLM."""
    print("🧪 Testing Domain Advisor prompts with Ollama...")
    
    # Initialize LLM client with Ollama
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True,
        "max_retries": 2,
        "timeout": 120.0
    }
    
    from core.llm_client import LLMClient
    client = LLMClient(config)
    
    # Test a simplified domain analysis prompt
    system_prompt = """You are a Domain Advisor Agent that analyzes business requirements and creates technical specifications.

Your task is to analyze business requirements and return a JSON response with:
- domain_model: entities, relationships, business_rules
- technical_specifications: authentication, data_architecture, security_measures
- user_personas: identified user types

Return only valid JSON without additional text."""

    user_prompt = """Analyze these requirements for a task management system:

Requirements:
- Users can create and manage personal tasks
- System supports team collaboration 
- Data must be stored securely
- Mobile app support required

Domain: task_management
Stakeholders: individual_users, team_leads
Compliance: GDPR, basic_security

Provide analysis as JSON."""

    request = LLMRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen:7b",
        temperature=0.3,
        max_tokens=1000
    )
    
    print("🤖 Sending request to Ollama...")
    response = await client.generate_response(request)
    
    if response.success:
        print("✅ Response received!")
        print(f"   Model: {response.model}")
        print(f"   Time: {response.response_time:.2f}s")
        print(f"   Content length: {len(response.content)} chars")
        
        # Try to parse as JSON using the LLM client's extraction method directly
        try:
            result = client._extract_json_from_response(response.content)
            print("✅ Valid JSON response!")
            print(f"   Result type: {type(result)}")
            if isinstance(result, dict):
                if "content" in result and "parsed" in result:
                    print("   ❌ Got fallback result")
                else:
                    print(f"   Available fields: {list(result.keys())}")
            else:
                print(f"   ❌ Wrong type: {type(result)}")
                return False
            
            # Check required fields
            required_fields = ["domain_model", "technical_specifications", "user_personas"]
            for field in required_fields:
                if field in result:
                    print(f"   ✅ {field}: Present")
                    if field == "domain_model" and isinstance(result[field], dict):
                        dm = result[field]
                        print(f"      - Entities: {len(dm.get('entities', []))}")
                        print(f"      - Relationships: {len(dm.get('relationships', []))}")
                        print(f"      - Business Rules: {len(dm.get('business_rules', []))}")
                else:
                    print(f"   ❌ {field}: Missing")
            
            return True
        except Exception as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {response.content[:200]}...")
            return False
    else:
        print(f"❌ Generation failed: {response.error}")
        return False


async def main():
    """Main test function."""
    try:
        success = await test_domain_advisor_llm_directly()
        if success:
            print("\n🎉 Domain Advisor Ollama test passed!")
        else:
            print("\n❌ Domain Advisor Ollama test failed!")
        return success
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)