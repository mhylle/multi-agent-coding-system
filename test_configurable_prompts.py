#!/usr/bin/env python3
"""
Test the configurable prompt system with qwen3:14b
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest
from core.prompt_manager import get_prompt_manager


async def test_configurable_prompts():
    """Test the configurable prompt system."""
    print("🧪 Testing configurable prompt system with qwen3:14b...")
    
    # Initialize LLM client
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    client = LLMClient(config)
    
    # Initialize prompt manager
    prompt_manager = get_prompt_manager()
    
    try:
        # Load Domain Advisor prompts
        print("📋 Loading Domain Advisor prompts...")
        domain_prompts = prompt_manager.load_prompts("domain_advisor")
        print(f"✅ Loaded prompts with variants: {prompt_manager.list_available_variants('domain_advisor')}")
        
        # Test with default prompts
        print("\n🤖 Testing with default prompts...")
        system_prompt = prompt_manager.get_system_prompt("domain_advisor")
        user_prompt = prompt_manager.format_user_prompt(
            "domain_advisor",
            domain_type="task management",
            requirements_list="- Users create tasks\n- Team collaboration\n- Secure data"
        )
        
        model_config = prompt_manager.get_model_config("domain_advisor")
        
        request = LLMRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=model_config.get("model", "qwen3:14b"),
            temperature=model_config.get("temperature", 0.1),
            max_tokens=model_config.get("max_tokens", 1000)
        )
        
        print(f"   Model: {request.model}")
        print(f"   System prompt preview: {system_prompt[:100]}...")
        print(f"   User prompt: {user_prompt}")
        
        response = await client.generate_response(request)
        
        if response.success:
            print("✅ Default prompts successful!")
            print(f"   Time: {response.response_time:.2f}s")
            print(f"   Response length: {len(response.content)} chars")
            
            # Try to parse as JSON
            result = client._extract_json_from_response(response.content)
            if isinstance(result, dict) and "domain_model" in result:
                print("✅ JSON structure valid!")
                print(f"   Fields: {list(result.keys())}")
            else:
                print("❌ JSON structure invalid")
                return False
        else:
            print(f"❌ Default prompts failed: {response.error}")
            return False
        
        # Test with simple variant
        print("\n🤖 Testing with 'simple' variant...")
        simple_system = prompt_manager.get_system_prompt("domain_advisor", "simple")
        simple_user = prompt_manager.format_user_prompt(
            "domain_advisor", 
            "simple",
            requirements="Users can create tasks and collaborate in teams"
        )
        
        simple_request = LLMRequest(
            prompt=simple_user,
            system_prompt=simple_system,
            model=model_config.get("model", "qwen3:14b"),
            temperature=model_config.get("temperature", 0.1),
            max_tokens=1000  # Sufficient for complete JSON
        )
        
        print(f"   Simple system prompt: {simple_system}")
        print(f"   Simple user prompt: {simple_user}")
        
        simple_response = await client.generate_response(simple_request)
        
        if simple_response.success:
            print("✅ Simple variant successful!")
            print(f"   Time: {simple_response.response_time:.2f}s")
            print(f"   Response length: {len(simple_response.content)} chars")
            
            # Parse JSON
            simple_result = client._extract_json_from_response(simple_response.content)
            if isinstance(simple_result, dict):
                print("✅ Simple JSON structure valid!")
                print(f"   Fields: {list(simple_result.keys())}")
            else:
                print("❌ Simple JSON structure invalid")
                return False
        else:
            print(f"❌ Simple variant failed: {simple_response.error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configurable prompts test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_prompt_modification():
    """Test modifying prompts on the fly."""
    print("\n🔧 Testing prompt modification...")
    
    prompt_manager = get_prompt_manager()
    
    try:
        # Load current prompts
        prompts = prompt_manager.load_prompts("domain_advisor")
        
        # Create a custom variant
        if "prompt_variants" not in prompts:
            prompts["prompt_variants"] = {}
        
        prompts["prompt_variants"]["custom"] = {
            "system_prompt": "Create JSON analysis for requirements. Return only: {\"entities\": [], \"specs\": {}, \"users\": []}",
            "user_template": "Analyze: {requirements}. Return JSON."
        }
        
        # Save updated prompts
        prompt_manager.save_prompts("domain_advisor", prompts)
        print("✅ Added custom prompt variant")
        
        # Test the new variant
        custom_system = prompt_manager.get_system_prompt("domain_advisor", "custom")
        custom_user = prompt_manager.format_user_prompt(
            "domain_advisor",
            "custom", 
            requirements="Task management with user roles"
        )
        
        print(f"   Custom system: {custom_system}")
        print(f"   Custom user: {custom_user}")
        print("✅ Prompt modification successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt modification failed: {e}")
        return False


async def main():
    """Main test function."""
    try:
        # Test configurable prompts
        success1 = await test_configurable_prompts()
        
        # Test prompt modification
        success2 = await test_prompt_modification()
        
        if success1 and success2:
            print("\n🎉 Configurable prompt system PASSED!")
            print("✅ qwen3:14b works with multiple prompt variants")
            print("✅ Prompts can be easily modified for fine-tuning")
        else:
            print("\n❌ Configurable prompt system FAILED!")
        
        return success1 and success2
        
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)