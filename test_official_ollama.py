#!/usr/bin/env python3
"""
Test using the official Ollama Python library
"""
import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import ollama
    print("✅ Official Ollama library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Ollama library: {e}")
    sys.exit(1)


async def test_official_ollama():
    """Test using the official Ollama Python library."""
    print("🧪 Testing with official Ollama Python library...")
    
    # Test with qwen3:14b as specifically requested
    model = "qwen3:14b"
    
    try:
        # Check if model is available
        print(f"📋 Checking available models...")
        models = ollama.list()
        print(f"Available models: {[m.model for m in models.models]}")
        
        if not any(model in m.model for m in models.models):
            print(f"❌ Model {model} not found in available models")
            return False
        
        print(f"✅ Model {model} is available")
        
        # Test simple generation
        print(f"🤖 Testing simple generation with {model}...")
        
        response = ollama.generate(
            model=model,
            prompt="Say 'Hello from qwen3:14b' and nothing else.",
            options={
                'temperature': 0.1,
                'num_predict': 20
            }
        )
        
        if response and 'response' in response:
            print(f"✅ Simple generation successful!")
            print(f"   Response: {response['response'].strip()}")
            
            # Test structured JSON generation
            print(f"🤖 Testing JSON generation with {model}...")
            
            json_prompt = '''Return only a valid JSON object with these fields:
{
  "test": "success",
  "model": "qwen3:14b",
  "status": "working"
}

Return only the JSON, no additional text.'''
            
            json_response = ollama.generate(
                model=model,
                prompt=json_prompt,
                options={
                    'temperature': 0.1,
                    'num_predict': 100
                }
            )
            
            if json_response and 'response' in json_response:
                print(f"✅ JSON generation successful!")
                print(f"   Raw response: {json_response['response'].strip()}")
                
                # Try to parse JSON
                try:
                    parsed = json.loads(json_response['response'].strip())
                    print(f"✅ JSON parsing successful!")
                    print(f"   Parsed: {parsed}")
                    return True
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
                    # Try to extract JSON from the response
                    content = json_response['response'].strip()
                    if '{' in content and '}' in content:
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        json_part = content[start:end]
                        try:
                            parsed = json.loads(json_part)
                            print(f"✅ JSON extraction successful!")
                            print(f"   Extracted: {parsed}")
                            return True
                        except json.JSONDecodeError:
                            print(f"❌ JSON extraction also failed")
                            return False
            else:
                print(f"❌ JSON generation failed: {json_response}")
                return False
        else:
            print(f"❌ Simple generation failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    try:
        success = asyncio.run(test_official_ollama())
        if success:
            print("\n🎉 Official Ollama + qwen3:14b test PASSED!")
            print("✅ qwen3:14b is working correctly with official library")
        else:
            print("\n❌ Official Ollama + qwen3:14b test FAILED!")
        return success
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)