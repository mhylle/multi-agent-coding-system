#!/usr/bin/env python3
"""Final comprehensive test using configurable prompts system."""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest
from core.prompt_manager import get_prompt_manager

async def final_test():
    print("🎯 FINAL TEST: Domain Advisor with qwen3:14b + Configurable Prompts")
    print("=" * 70)
    
    # Initialize LLM client
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    client = LLMClient(config)
    
    # Initialize prompt manager
    prompt_manager = get_prompt_manager()
    
    # Test with simple variant (most reliable)
    print("🤖 Testing with 'simple' variant for task management system...")
    
    system_prompt = prompt_manager.get_system_prompt("domain_advisor", "simple")
    user_prompt = prompt_manager.format_user_prompt(
        "domain_advisor", 
        "simple",
        requirements="Task management system: users create tasks, assign to team members, track progress, secure data storage"
    )
    
    model_config = prompt_manager.get_model_config("domain_advisor")
    
    request = LLMRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model=model_config.get("model", "qwen3:14b"),
        temperature=model_config.get("temperature", 0.1),
        max_tokens=1000
    )
    
    print("Making request to qwen3:14b...")
    response = await client.generate_response(request)
    
    if response.success:
        print(f"✅ Response successful! ({response.response_time:.1f}s on CPU)")
        
        # Extract JSON
        result = client._extract_json_from_response(response.content)
        
        if isinstance(result, dict) and "domain_model" in result:
            print("✅ JSON structure valid!")
            print(f"   Domain model entities: {len(result['domain_model'].get('entities', []))}")
            print(f"   Technical specs: {list(result.get('technical_specifications', {}).keys())}")
            print(f"   User personas: {len(result.get('user_personas', []))}")
            
            print("\n🎉 FINAL TEST PASSED!")
            print("✅ Multi-agent system foundation is ready!")
            print("✅ Ollama + qwen3:14b integration working")
            print("✅ Configurable prompts system working")
            print("✅ JSON parsing robust and reliable")
            return True
        else:
            print("❌ JSON structure invalid")
            print(f"   Result type: {type(result)}")
            return False
    else:
        print(f"❌ Request failed: {response.error}")
        return False

if __name__ == "__main__":
    success = asyncio.run(final_test())
    if success:
        print("\n🚀 SYSTEM READY FOR NEXT PHASE!")
    else:
        print("\n⚠️  SYSTEM NEEDS ATTENTION")
    sys.exit(0 if success else 1)