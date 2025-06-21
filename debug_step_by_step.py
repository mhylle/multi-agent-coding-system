#!/usr/bin/env python3
"""
Debug step by step
"""
import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest


async def debug_step_by_step():
    """Debug step by step."""
    print("🔍 Step by step debugging...")
    
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    
    client = LLMClient(config)
    
    # Get response from Ollama
    request = LLMRequest(
        prompt="Return JSON with {\"test\": \"value\", \"array\": [1, 2, 3]}",
        model="qwen:7b",
        temperature=0.1,
        max_tokens=200
    )
    
    response = await client.generate_response(request)
    
    if response.success:
        content = response.content
        print(f"Raw content:\n'{content}'\n")
        
        # Step 1: Direct JSON parsing
        print("Step 1: Direct JSON parsing")
        try:
            direct_result = json.loads(content)
            print(f"✅ Direct parsing worked: {type(direct_result)}")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Direct parsing failed: {e}")
        
        # Step 2: Markdown code block extraction
        print("\nStep 2: Markdown code block extraction")
        json_start = content.find("```json")
        if json_start != -1:
            print(f"Found ```json at position {json_start}")
            json_start += len("```json")
            json_end = content.find("```", json_start)
            if json_end != -1:
                print(f"Found closing ``` at position {json_end}")
                json_content = content[json_start:json_end].strip()
                print(f"Extracted content:\n'{json_content}'\n")
                try:
                    markdown_result = json.loads(json_content)
                    print(f"✅ Markdown extraction worked: {type(markdown_result)}")
                    print(f"Keys: {list(markdown_result.keys()) if isinstance(markdown_result, dict) else 'Not a dict'}")
                    return
                except json.JSONDecodeError as e:
                    print(f"❌ Markdown extraction failed: {e}")
            else:
                print("No closing ``` found")
        else:
            print("No ```json found")
        
        # Step 3: Manual object extraction
        print("\nStep 3: Manual object extraction")
        brace_start = content.find("{")
        if brace_start != -1:
            print(f"Found {{ at position {brace_start}")
            
            # Test our bracket counting logic
            bracket_count = 0
            start_found = False
            
            for i, char in enumerate(content[brace_start:], brace_start):
                if char == "{":
                    if not start_found:
                        start_found = True
                        print(f"Starting from position {i}")
                    bracket_count += 1
                elif char == "}":
                    bracket_count -= 1
                    if bracket_count == 0 and start_found:
                        json_content = content[brace_start:i+1]
                        print(f"Extracted object from {brace_start} to {i}")
                        print(f"Extracted content:\n'{json_content}'\n")
                        try:
                            object_result = json.loads(json_content)
                            print(f"✅ Object extraction worked: {type(object_result)}")
                            return
                        except json.JSONDecodeError as e:
                            print(f"❌ Object extraction failed: {e}")
                        break
        else:
            print("No { found")
            
        print("❌ All extraction methods failed")


if __name__ == "__main__":
    asyncio.run(debug_step_by_step())