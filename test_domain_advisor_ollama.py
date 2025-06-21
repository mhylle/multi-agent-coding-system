#!/usr/bin/env python3
"""
Test Domain Advisor Agent with Ollama integration.
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import initialize_llm_client, LLMClient
from core.types import Task
from core.base_agent import BaseAgent, BaseOrchestrator, BaseExecutor, BaseReviewer

# Import domain advisor components directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'agents', 'domain_advisor'))
from domain_advisor import DomainAdvisorAgent


async def test_domain_advisor_with_ollama():
    """Test Domain Advisor with Ollama LLM."""
    print("🧪 Testing Domain Advisor with Ollama...")
    
    # Initialize LLM client with Ollama
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True,
        "max_retries": 2,
        "timeout": 120.0
    }
    
    initialize_llm_client(config)
    
    # Create Domain Advisor
    domain_advisor = DomainAdvisorAgent()
    
    # Test simple requirements analysis
    print("\n📋 Testing simple requirements analysis...")
    
    response = await domain_advisor.analyze_business_requirements(
        requirements=[
            "Users can create and manage personal tasks",
            "System supports team collaboration features",
            "Data must be stored securely with user privacy",
            "Mobile app support is required"
        ],
        domain="task_management",
        stakeholders=["individual_users", "team_leads", "administrators"],
        compliance_needs=["GDPR", "basic_security"]
    )
    
    if response.success:
        print("✅ Analysis completed successfully!")
        print(f"   Confidence: {response.confidence_score}")
        
        result = response.result
        print("\n📊 Domain Model:")
        if "domain_model" in result:
            domain_model = result["domain_model"]
            print(f"   Entities: {len(domain_model.get('entities', []))}")
            print(f"   Relationships: {len(domain_model.get('relationships', []))}")
            print(f"   Business Rules: {len(domain_model.get('business_rules', []))}")
        
        print("\n🔧 Technical Specifications:")
        if "technical_specifications" in result:
            tech_specs = result["technical_specifications"]
            print(f"   Authentication: {tech_specs.get('authentication', {}).get('method', 'N/A')}")
            print(f"   Data Storage: {tech_specs.get('data_architecture', {}).get('primary_storage', 'N/A')}")
            print(f"   Security Level: {tech_specs.get('security_measures', {}).get('level', 'N/A')}")
        
        print("\n🎯 User Personas:")
        if "user_personas" in result:
            personas = result["user_personas"]
            print(f"   Identified {len(personas)} personas")
            for persona in personas[:2]:  # Show first 2
                print(f"   - {persona.get('name', 'Unknown')}: {persona.get('description', 'No description')[:50]}...")
        
        return True
    else:
        print(f"❌ Analysis failed: {response.error}")
        return False


async def main():
    """Main test function."""
    try:
        success = await test_domain_advisor_with_ollama()
        if success:
            print("\n🎉 Domain Advisor + Ollama integration test passed!")
        else:
            print("\n❌ Domain Advisor + Ollama integration test failed!")
        return success
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)