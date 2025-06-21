#!/usr/bin/env python3
"""
Test the JSON extraction fix directly
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient


def test_json_extraction():
    """Test JSON extraction directly."""
    print("🔍 Testing JSON extraction fix...")
    
    config = {"default_provider": "anthropic"}  # Dummy config
    client = LLMClient(config)
    
    # Test case that was failing
    problematic_content = '''```json
{
  "domain_model": {
    "entities": [
      {
        "name": "User",
        "attributes": ["personal_tasks", "team_collaboration_role"]
      },
      {
        "name": "Task",
        "attributes": ["description", "assignee", "due_date"]
      }
    ],
    "relationships": [
      {"name": "created_by", "type": "one-to-one"}
    ],
    "business_rules": [
      {"name": "task_ownership", "description": "Users own their tasks"}
    ]
  },
  "technical_specifications": {
    "authentication": {
      "method": "username_password"
    },
    "data_architecture": {
      "primary_storage": "postgresql"
    },
    "security_measures": {
      "level": "standard"
    }
  },
  "user_personas": [
    {
      "name": "Task Creator",
      "description": "Individual who creates tasks"
    },
    {
      "name": "Team Member", 
      "description": "Individual who completes tasks"
    }
  ]
}
```'''
    
    result = client._extract_json_from_response(problematic_content)
    
    print(f"Result type: {type(result)}")
    
    if isinstance(result, dict):
        if "content" in result and "parsed" in result:
            print("❌ Got fallback result - JSON extraction failed")
            print(f"Parsed flag: {result['parsed']}")
        else:
            print("✅ Got proper JSON dict!")
            print(f"Keys: {list(result.keys())}")
            
            # Check for expected fields
            if "domain_model" in result:
                print("✅ domain_model present")
            if "technical_specifications" in result:
                print("✅ technical_specifications present")
            if "user_personas" in result:
                print("✅ user_personas present")
                
            return True
    elif isinstance(result, list):
        print("❌ Still getting list instead of dict")
        print(f"List length: {len(result)}")
        if len(result) > 0:
            print(f"First item: {result[0]}")
    else:
        print(f"❌ Unexpected type: {type(result)}")
    
    return False


if __name__ == "__main__":
    success = test_json_extraction()
    print(f"\nResult: {'✅ PASS' if success else '❌ FAIL'}")