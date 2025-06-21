#!/usr/bin/env python3
"""
Show Domain Advisor output with a simple, working example.
"""
import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from core.types import LLMRequest
from core.prompt_manager import get_prompt_manager

async def show_simple_domain_output():
    print("🎯 DOMAIN ADVISOR OUTPUT EXAMPLE")
    print("=" * 50)
    
    # Simple working configuration
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    
    # Start fresh Ollama connection
    try:
        import subprocess
        subprocess.run(["docker", "kill", "ollama-agent-system"], capture_output=True)
        subprocess.run(["docker", "rm", "ollama-agent-system"], capture_output=True)
        
        # Run simple docker command
        result = subprocess.run([
            "docker", "run", "-d", 
            "--name", "ollama-agent-system",
            "-p", "11434:11434",
            "-v", "/tmp/ollama:/root/.ollama",
            "ollama/ollama"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Started fresh Ollama container")
            # Wait for startup
            await asyncio.sleep(5)
            
            # Pull model if needed
            subprocess.run(["docker", "exec", "ollama-agent-system", "ollama", "pull", "qwen3:14b"], 
                          capture_output=True)
            print("✅ qwen3:14b model ready")
        else:
            print("⚠️ Using existing Ollama setup")
            
    except Exception as e:
        print(f"⚠️ Container setup issue: {e}")
    
    # Test simple task management scenario
    print("\n📋 Business Scenario: Simple Task Management")
    requirements = "Task management system where users create tasks, assign to team members, and track progress"
    
    client = LLMClient(config)
    prompt_manager = get_prompt_manager()
    
    # Use simple variant that we know works
    system_prompt = prompt_manager.get_system_prompt("domain_advisor", "simple")
    user_prompt = prompt_manager.format_user_prompt(
        "domain_advisor", 
        "simple",
        requirements=requirements
    )
    
    model_config = prompt_manager.get_model_config("domain_advisor")
    
    request = LLMRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen3:14b",
        temperature=0.1,
        max_tokens=1000
    )
    
    print(f"\nInput: {requirements}")
    print("\n🤖 Processing with qwen3:14b...")
    
    response = await client.generate_response(request)
    
    if response.success:
        print(f"✅ Completed in {response.response_time:.1f}s")
        
        # Show raw response first
        print(f"\n📝 RAW RESPONSE ({len(response.content)} chars):")
        print("─" * 50)
        print(response.content[:500] + ("..." if len(response.content) > 500 else ""))
        print("─" * 50)
        
        # Extract and show structured data
        result = client._extract_json_from_response(response.content)
        
        if isinstance(result, dict):
            print(f"\n🏗️ STRUCTURED OUTPUT:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:1000] + ("..." if len(str(result)) > 1000 else ""))
            
            print(f"\n📊 ANALYSIS BREAKDOWN:")
            
            # Domain Model
            if "domain_model" in result:
                dm = result["domain_model"]
                print(f"  🏗️ Domain Model:")
                print(f"    • Entities: {len(dm.get('entities', []))}")
                print(f"    • Relationships: {len(dm.get('relationships', []))}")
                print(f"    • Business Rules: {len(dm.get('business_rules', []))}")
            
            # Technical Specs
            if "technical_specifications" in result:
                ts = result["technical_specifications"]
                print(f"  🔧 Technical Specifications:")
                for key, value in ts.items():
                    print(f"    • {key}: {type(value).__name__}")
            
            # User Personas
            if "user_personas" in result:
                personas = result["user_personas"]
                print(f"  👥 User Personas: {len(personas)}")
                for i, persona in enumerate(personas[:2]):
                    if isinstance(persona, dict):
                        print(f"    • {persona.get('name', f'Persona {i+1}')}")
            
            print(f"\n✅ DOMAIN ADVISOR SUCCESSFULLY PRODUCED:")
            print(f"   • Complete domain model with {len(result.get('domain_model', {}).get('entities', []))} entities")
            print(f"   • Technical architecture specifications")
            print(f"   • {len(result.get('user_personas', []))} user personas")
            print(f"   • Structured JSON output ready for next agents")
            
            return True
        else:
            print(f"❌ JSON parsing failed, got: {type(result)}")
            return False
    else:
        print(f"❌ Request failed: {response.error}")
        return False

if __name__ == "__main__":
    success = asyncio.run(show_simple_domain_output())
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)