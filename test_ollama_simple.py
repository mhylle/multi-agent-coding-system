#!/usr/bin/env python3
"""
Simple test script to verify Ollama integration.
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.types import LLMRequest
from core.ollama_client import OllamaProvider


async def test_ollama_basic():
    """Test basic Ollama functionality."""
    print("🧪 Testing Ollama integration...")
    
    # Create Ollama provider
    ollama = OllamaProvider()
    
    # Check health
    print("📋 Checking Ollama health...")
    is_healthy = await ollama.check_health()
    print(f"   Health: {'✅ OK' if is_healthy else '❌ Failed'}")
    
    if not is_healthy:
        print("❌ Ollama is not accessible. Make sure it's running.")
        return False
    
    # List models
    print("📋 Available models:")
    models = await ollama.list_models()
    if models:
        for model in models:
            print(f"   - {model}")
    else:
        print("   No models available")
        return False
    
    # Test generation with simplest request
    print("🤖 Testing text generation...")
    request = LLMRequest(
        prompt="Say hello in exactly 3 words",
        model=models[0] if models else "qwen:7b",
        temperature=0.1,
        max_tokens=10
    )
    
    response = await ollama.generate_response(request)
    
    if response.success:
        print(f"✅ Response: {response.content}")
        print(f"   Model: {response.model}")
        print(f"   Provider: {response.provider}")
        print(f"   Time: {response.response_time:.2f}s")
        return True
    else:
        print(f"❌ Generation failed: {response.error}")
        return False


async def main():
    """Main test function."""
    try:
        success = await test_ollama_basic()
        if success:
            print("\n🎉 Ollama integration test passed!")
        else:
            print("\n❌ Ollama integration test failed!")
        return success
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)