#!/usr/bin/env python3
"""
Show actual Domain Advisor output with a realistic business scenario.
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

async def show_domain_advisor_output():
    print("🏢 DOMAIN ADVISOR OUTPUT DEMO")
    print("=" * 60)
    print("📋 Business Scenario: E-commerce Platform")
    print()
    
    # Initialize LLM client and prompt manager
    config = {
        "default_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "enable_ollama": True
    }
    client = LLMClient(config)
    prompt_manager = get_prompt_manager()
    
    # Realistic e-commerce requirements
    business_requirements = """
    E-commerce platform requirements:
    - Customers can browse products by category and search
    - Shopping cart functionality with save for later
    - Secure checkout with multiple payment methods
    - User accounts with order history and wishlists  
    - Inventory management for store owners
    - Order tracking and shipping integration
    - Customer reviews and ratings system
    - Admin dashboard for sales analytics
    - Mobile responsive design required
    - GDPR compliance for EU customers
    - PCI DSS compliance for payments
    """
    
    print(f"Requirements:\n{business_requirements}\n")
    
    # Use the detailed variant for comprehensive output
    system_prompt = prompt_manager.get_system_prompt("domain_advisor", "detailed")
    user_prompt = prompt_manager.format_user_prompt(
        "domain_advisor",
        "detailed",
        domain_type="e-commerce",
        requirements_list=business_requirements,
        domain="retail/e-commerce",
        stakeholders="customers, store owners, administrators, payment processors",
        compliance_needs="GDPR, PCI DSS, accessibility standards"
    )
    
    model_config = prompt_manager.get_model_config("domain_advisor")
    
    request = LLMRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model=model_config.get("model", "qwen3:14b"),
        temperature=0.2,  # Lower for more structured output
        max_tokens=2000   # More tokens for detailed analysis
    )
    
    print("🤖 Processing with Domain Advisor Agent (qwen3:14b)...")
    print("⏳ This may take 2-4 minutes on CPU...")
    
    response = await client.generate_response(request)
    
    if response.success:
        print(f"✅ Analysis completed in {response.response_time:.1f} seconds!\n")
        
        # Extract and display structured output
        result = client._extract_json_from_response(response.content)
        
        if isinstance(result, dict):
            print("📊 DOMAIN ADVISOR OUTPUT:")
            print("=" * 40)
            
            # Domain Model
            if "domain_model" in result:
                domain_model = result["domain_model"]
                print("\n🏗️ DOMAIN MODEL:")
                
                entities = domain_model.get("entities", [])
                print(f"\n📦 Entities ({len(entities)}):")
                for i, entity in enumerate(entities[:3], 1):  # Show first 3
                    if isinstance(entity, dict):
                        print(f"  {i}. {entity.get('name', 'Unknown')}")
                        print(f"     Description: {entity.get('description', 'N/A')}")
                        print(f"     Attributes: {entity.get('attributes', [])}")
                if len(entities) > 3:
                    print(f"     ... and {len(entities) - 3} more entities")
                
                relationships = domain_model.get("relationships", [])
                print(f"\n🔗 Relationships ({len(relationships)}):")
                for i, rel in enumerate(relationships[:2], 1):  # Show first 2
                    if isinstance(rel, dict):
                        print(f"  {i}. {rel.get('from', 'Unknown')} → {rel.get('to', 'Unknown')}")
                        print(f"     Type: {rel.get('type', 'N/A')}")
                
                business_rules = domain_model.get("business_rules", [])
                print(f"\n📋 Business Rules ({len(business_rules)}):")
                for i, rule in enumerate(business_rules[:2], 1):  # Show first 2
                    if isinstance(rule, dict):
                        print(f"  {i}. {rule.get('rule', 'N/A')}")
                        print(f"     Category: {rule.get('category', 'N/A')}")
            
            # Technical Specifications
            if "technical_specifications" in result:
                tech_specs = result["technical_specifications"]
                print(f"\n🔧 TECHNICAL SPECIFICATIONS:")
                
                if "authentication" in tech_specs:
                    auth = tech_specs["authentication"]
                    print(f"\n🔐 Authentication:")
                    print(f"  Method: {auth.get('method', 'N/A')}")
                    print(f"  Requirements: {auth.get('requirements', [])}")
                
                if "data_architecture" in tech_specs:
                    data_arch = tech_specs["data_architecture"]
                    print(f"\n💾 Data Architecture:")
                    print(f"  Storage: {data_arch.get('storage', 'N/A')}")
                    print(f"  Database: {data_arch.get('database', 'N/A')}")
                
                if "security_measures" in tech_specs:
                    security = tech_specs["security_measures"]
                    print(f"\n🛡️ Security Measures:")
                    print(f"  Level: {security.get('level', 'N/A')}")
                    measures = security.get('measures', [])
                    if measures:
                        print(f"  Measures: {', '.join(measures[:3])}")
            
            # User Personas
            if "user_personas" in result:
                personas = result["user_personas"]
                print(f"\n👥 USER PERSONAS ({len(personas)}):")
                for i, persona in enumerate(personas[:2], 1):  # Show first 2
                    if isinstance(persona, dict):
                        print(f"\n  {i}. {persona.get('name', 'Unknown')}")
                        print(f"     Description: {persona.get('description', 'N/A')}")
                        print(f"     Needs: {persona.get('needs', [])}")
            
            print(f"\n📈 ANALYSIS SUMMARY:")
            print(f"  • {len(result.get('domain_model', {}).get('entities', []))} business entities identified")
            print(f"  • {len(result.get('domain_model', {}).get('relationships', []))} relationships mapped")
            print(f"  • {len(result.get('domain_model', {}).get('business_rules', []))} business rules defined")
            print(f"  • {len(result.get('user_personas', []))} user personas created")
            print(f"  • Complete technical specifications provided")
            
            # Show raw JSON structure for reference
            print(f"\n🔍 JSON STRUCTURE KEYS:")
            print(f"  {list(result.keys())}")
            
            return True
        else:
            print("❌ Failed to parse JSON output")
            print(f"Raw response: {response.content[:500]}...")
            return False
    else:
        print(f"❌ Domain Advisor failed: {response.error}")
        return False

if __name__ == "__main__":
    success = asyncio.run(show_domain_advisor_output())
    if success:
        print("\n🎉 Domain Advisor successfully analyzed business requirements!")
    else:
        print("\n⚠️ Domain Advisor analysis failed")
    sys.exit(0 if success else 1)