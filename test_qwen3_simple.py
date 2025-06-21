#!/usr/bin/env python3
"""
Test qwen3:14b with very simple prompt to verify it works
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest


async def test_qwen3_simple():
    """Test qwen3:14b with very simple prompt."""
    print("🧪 Testing qwen3:14b with simple prompt...")
    
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    
    client = LLMClient(config)
    
    # Very simple test
    request = LLMRequest(
        prompt="Say 'Hello World' in exactly 2 words",
        model="qwen3:14b",
        temperature=0.1,
        max_tokens=10
    )
    
    print("🤖 Sending simple request to qwen3:14b...")
    response = await client.generate_response(request)
    
    if response.success:
        print("✅ qwen3:14b response received!")
        print(f"   Model: {response.model}")
        print(f"   Time: {response.response_time:.2f}s")
        print(f"   Content: '{response.content}'")
        return True
    else:
        print(f"❌ qwen3:14b failed: {response.error}")
        return False


async def main():
    """Main test function."""
    try:
        success = await test_qwen3_simple()
        if success:
            print("\n🎉 qwen3:14b basic test PASSED!")
        else:
            print("\n❌ qwen3:14b basic test FAILED!")
        return success
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)