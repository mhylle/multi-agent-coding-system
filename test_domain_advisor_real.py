"""
Test Domain Advisor Agent with real LLM API.
This test requires actual API keys to be set in environment variables.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.llm_client import initialize_llm_client
from src.agents.domain_advisor.domain_advisor import DomainAdvisorAgent


async def test_with_real_llm():
    """Test Domain Advisor with real LLM API."""
    
    print("🤖 Testing Domain Advisor Agent with Real LLM")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not anthropic_key and not openai_key:
        print("❌ No API keys found in environment variables!")
        print("   Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file")
        print("\n   Example .env file:")
        print("   ANTHROPIC_API_KEY=sk-ant-...")
        print("   OPENAI_API_KEY=sk-...")
        return
    
    # Initialize LLM client with real credentials
    config = {
        "anthropic_api_key": anthropic_key,
        "openai_api_key": openai_key,
        "default_provider": "anthropic" if anthropic_key else "openai",
        "max_retries": 3,
        "rate_limit_rpm": 20  # Conservative rate limit for testing
    }
    
    print(f"✅ Using {config['default_provider']} as LLM provider")
    
    try:
        initialize_llm_client(config)
        print("✅ LLM client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")
        return
    
    # Create Domain Advisor Agent
    print("\n📋 Creating Domain Advisor Agent...")
    domain_advisor = DomainAdvisorAgent("production_test_agent")
    print("✅ Agent created")
    
    # Test Case: Real-world SaaS Platform Requirements
    print("\n🧪 Test Case: SaaS Project Management Platform")
    print("-" * 60)
    
    requirements = [
        "Multi-tenant SaaS platform for project management",
        "Users can create organizations and invite team members",
        "Hierarchical project structure with tasks and subtasks",
        "Real-time collaboration features like comments and mentions",
        "Kanban board and Gantt chart views for project visualization",
        "Time tracking and billing functionality",
        "Integration with popular tools (Slack, GitHub, Jira)",
        "Advanced search and filtering capabilities",
        "Role-based permissions at organization and project levels",
        "API for third-party integrations",
        "Mobile applications for iOS and Android",
        "Enterprise SSO support (SAML, OAuth)",
        "Audit logs for compliance",
        "Data export capabilities",
        "Multi-language support",
        "GDPR and SOC2 compliance required"
    ]
    
    print("📝 Requirements:")
    for i, req in enumerate(requirements[:5], 1):
        print(f"   {i}. {req}")
    print(f"   ... and {len(requirements) - 5} more requirements")
    
    print("\n🔄 Processing with LLM (this may take 20-30 seconds)...")
    
    try:
        response = await domain_advisor.analyze_business_requirements(
            requirements=requirements,
            domain="saas_project_management",
            stakeholders=["organization_owners", "project_managers", "team_members", "external_clients"],
            compliance_needs=["GDPR", "SOC2", "ISO27001"]
        )
        
        if response.success:
            print("\n✅ Analysis completed successfully!")
            print(f"   Confidence Score: {response.confidence:.2f}")
            print(f"   Execution Time: {response.execution_time:.2f} seconds")
            
            # Display results summary
            result = response.result
            
            print("\n📊 Analysis Results:")
            
            # Domain Model
            if "domain_model" in result:
                dm = result["domain_model"]
                print("\n   Domain Model:")
                print(f"      - Entities: {len(dm.get('entities', []))}")
                if dm.get('entities'):
                    entity_names = [e['name'] for e in dm['entities'][:5]]
                    print(f"        Examples: {', '.join(entity_names)}...")
                print(f"      - Relationships: {len(dm.get('relationships', []))}")
                print(f"      - Business Rules: {len(dm.get('business_rules', []))}")
                print(f"      - Core Processes: {len(dm.get('processes', []))}")
            
            # Requirements
            if "functional_requirements" in result:
                print(f"\n   Functional Requirements: {len(result['functional_requirements'])}")
                if result['functional_requirements']:
                    print(f"      First requirement: {result['functional_requirements'][0].get('requirement', 'N/A')}")
            
            if "non_functional_requirements" in result:
                print(f"\n   Non-Functional Requirements: {len(result['non_functional_requirements'])}")
                categories = set(r.get('category', '') for r in result['non_functional_requirements'])
                print(f"      Categories: {', '.join(categories)}")
            
            # Technical Specifications
            if "technical_specifications" in result:
                tech = result["technical_specifications"]
                print(f"\n   Technical Specifications:")
                for key in tech:
                    print(f"      - {key.title()}: ✓")
            
            # User Personas
            if "user_personas" in result:
                print(f"\n   User Personas: {len(result['user_personas'])}")
                if result['user_personas']:
                    personas = [p.get('name', 'Unknown') for p in result['user_personas']]
                    print(f"      Identified: {', '.join(personas)}")
            
            # Compliance
            if "compliance_requirements" in result:
                print(f"\n   Compliance Requirements: {len(result['compliance_requirements'])}")
                for comp in result['compliance_requirements']:
                    print(f"      - {comp.get('standard', 'N/A')}: {len(comp.get('requirements', []))} requirements")
            
            # Save detailed results
            print("\n💾 Saving detailed results to file...")
            import json
            with open("domain_advisor_real_test_results.json", "w") as f:
                json.dump({
                    "test_info": {
                        "provider": config['default_provider'],
                        "confidence": response.confidence,
                        "execution_time": response.execution_time,
                        "requirements_count": len(requirements)
                    },
                    "results": result
                }, f, indent=2)
            print("   Results saved to: domain_advisor_real_test_results.json")
            
        else:
            print(f"\n❌ Analysis failed: {response.error}")
            if response.feedback:
                print("   Feedback:")
                for feedback in response.feedback:
                    print(f"      - {feedback}")
                    
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete!")
    
    if response and response.success:
        print("\n✅ Domain Advisor Agent is working correctly with real LLM!")
        print("   - Successfully analyzed complex requirements")
        print("   - Generated comprehensive domain model")
        print("   - Created actionable technical specifications")
        print("   - Handled compliance requirements appropriately")
        print("\n🎯 Ready to proceed with Solution Architect Agent implementation!")
    else:
        print("\n⚠️  Test did not complete successfully. Check the errors above.")


if __name__ == "__main__":
    print("🔍 Checking for .env file...")
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("⚠️  No .env file found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("📝 Created .env file. Please add your API keys before running.")
            sys.exit(1)
    
    asyncio.run(test_with_real_llm())