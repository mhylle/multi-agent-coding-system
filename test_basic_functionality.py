"""
Basic functionality test for the multi-agent system.
Tests core components without requiring API keys.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.types import Task, AgentRole, TaskPriority, LLMRequest, LLMResponse
from src.core.llm_client import LLMClient, initialize_llm_client
from src.communication.message_bus import MessageBus, initialize_message_bus
from src.communication.protocols import ProtocolHelper
from src.agents.domain_advisor.domain_advisor import DomainAdvisorAgent


class MockLLMClient(LLMClient):
    """Mock LLM client for testing without API keys."""
    
    def __init__(self, config):
        # Initialize parent without calling super().__init__ to avoid API key requirements
        self.config = config
        self.max_retries = config.get("max_retries", 3)
        
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate mock response based on prompt content."""
        
        # Simple mock responses based on prompt keywords
        if "execution plan" in request.prompt.lower():
            content = '''{
                "execution_plan": {
                    "analysis_type": "user_requirements_analysis",
                    "focus_areas": ["domain_modeling", "requirements_analysis"],
                    "extraction_steps": [
                        {
                            "step": "domain_analysis",
                            "description": "Extract entities and relationships",
                            "outputs": ["domain_model"]
                        }
                    ],
                    "quality_gates": ["completeness_check"],
                    "estimated_duration": 10,
                    "required_resources": ["business_requirements"]
                }
            }'''
            
        elif "domain analysis" in request.prompt.lower():
            content = '''{
                "domain_model": {
                    "entities": [
                        {
                            "name": "User",
                            "description": "System user",
                            "attributes": ["id", "name", "email"],
                            "constraints": ["unique email"]
                        },
                        {
                            "name": "Task",
                            "description": "User task item",
                            "attributes": ["id", "title", "description", "status"],
                            "constraints": ["valid status"]
                        }
                    ],
                    "relationships": [
                        {
                            "from_entity": "User",
                            "to_entity": "Task",
                            "relationship_type": "one-to-many",
                            "description": "Users can have multiple tasks"
                        }
                    ],
                    "business_rules": [
                        {
                            "rule": "Users can only edit their own tasks",
                            "category": "authorization",
                            "entities_affected": ["User", "Task"],
                            "priority": "high"
                        }
                    ],
                    "processes": [
                        {
                            "name": "Task Creation",
                            "description": "Process for creating new tasks",
                            "steps": ["validate input", "create task", "notify user"],
                            "entities_involved": ["User", "Task"],
                            "triggers": ["user creates task"]
                        }
                    ]
                }
            }'''
            
        elif "requirements analysis" in request.prompt.lower():
            content = '''{
                "functional_requirements": [
                    {
                        "id": "FR001",
                        "requirement": "Users can create tasks",
                        "priority": "must-have",
                        "user_story": "As a user I want to create tasks so that I can track my work",
                        "acceptance_criteria": ["Task form validation", "Task saved to database"]
                    }
                ],
                "non_functional_requirements": [
                    {
                        "category": "performance",
                        "requirement": "System responds within 2 seconds",
                        "measurable_criteria": "95% of requests under 2s",
                        "priority": "high"
                    }
                ],
                "compliance_requirements": [
                    {
                        "standard": "GDPR",
                        "requirements": ["data consent", "right to deletion"],
                        "impact": "User data handling must comply with GDPR"
                    }
                ],
                "user_personas": [
                    {
                        "name": "Task Manager",
                        "role": "Project Manager",
                        "goals": ["track team progress", "manage deadlines"],
                        "pain_points": ["scattered task information"],
                        "technical_proficiency": "medium"
                    }
                ],
                "use_cases": [
                    {
                        "name": "Create Task",
                        "actor": "Task Manager",
                        "description": "Manager creates a new task",
                        "preconditions": ["user logged in"],
                        "main_flow": ["open task form", "fill details", "save task"],
                        "alternate_flows": ["validation errors"],
                        "postconditions": ["task saved", "user notified"]
                    }
                ]
            }'''
            
        elif "technical specifications" in request.prompt.lower():
            content = '''{
                "technical_specifications": {
                    "authentication": {
                        "method": "JWT",
                        "requirements": ["secure token storage", "token refresh"],
                        "considerations": ["token expiry", "secure transmission"]
                    },
                    "authorization": {
                        "model": "RBAC",
                        "roles": [
                            {
                                "role": "user",
                                "permissions": ["create_task", "view_own_tasks"],
                                "description": "Standard user role"
                            }
                        ],
                        "policies": ["users can only access own data"]
                    },
                    "data_handling": {
                        "storage_requirements": ["encrypted at rest"],
                        "processing_requirements": ["input validation"],
                        "security_requirements": ["data anonymization"],
                        "retention_policies": ["delete after 7 years"]
                    },
                    "integration": {
                        "external_systems": ["email service"],
                        "apis_needed": ["notification API"],
                        "data_exchange": ["JSON REST APIs"]
                    },
                    "security": {
                        "measures": ["HTTPS", "input sanitization"],
                        "compliance_mappings": ["GDPR compliance through data controls"],
                        "risk_assessments": ["data breach mitigation"]
                    }
                }
            }'''
            
        elif "review" in request.prompt.lower():
            content = '''{
                "review_result": {
                    "approved": true,
                    "confidence_score": 0.85,
                    "completeness_score": 0.9,
                    "accuracy_score": 0.8,
                    "issues": [],
                    "strengths": ["comprehensive domain model", "clear requirements"],
                    "missing_elements": [],
                    "improvement_suggestions": ["add more detailed acceptance criteria"]
                }
            }''' if "completeness" in request.prompt.lower() else '''{
                "validation_result": {
                    "approved": true,
                    "alignment_score": 0.85,
                    "feasibility_score": 0.9,
                    "issues": [],
                    "compliance_coverage": [
                        {
                            "requirement": "GDPR",
                            "addressed": true,
                            "how": "Data handling specifications include GDPR controls"
                        }
                    ],
                    "improvement_recommendations": ["consider additional security measures"]
                }
            }'''
        else:
            content = '{"result": "Mock response for: ' + request.prompt[:50] + '..."}'
        
        return LLMResponse(
            content=content,
            model=request.model,
            provider="mock",
            success=True
        )
    
    async def parse_structured_response(self, response: LLMResponse, 
                                      expected_format: str = "json"):
        """Parse the mock JSON response."""
        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"content": response.content, "parsed": False}


async def test_basic_functionality():
    """Test basic functionality of the multi-agent system."""
    
    print("🤖 Testing Multi-Agent Coding System")
    print("=" * 50)
    
    # Test 1: Initialize LLM Client
    print("\n1. Testing LLM Client Initialization...")
    try:
        # Use mock client instead of real one
        config = {"mock": True}
        llm_client = MockLLMClient(config)
        initialize_llm_client(config)
        
        # Replace global client with mock
        import src.core.llm_client as llm_module
        llm_module._llm_client = llm_client
        
        print("✅ LLM Client initialized (mock)")
    except Exception as e:
        print(f"❌ LLM Client failed: {e}")
        return
    
    # Test 2: Initialize Message Bus
    print("\n2. Testing Message Bus...")
    try:
        message_bus = initialize_message_bus()
        await message_bus.start()
        print("✅ Message Bus started")
        
        # Test message creation
        task = Task(
            title="Test Task",
            description="A test task for the system",
            requirements=["Test requirement 1", "Test requirement 2"]
        )
        
        message = ProtocolHelper.create_task_request(
            sender="test_sender",
            recipient="test_recipient", 
            task=task
        )
        
        print(f"✅ Message created: {message.message_id}")
        
    except Exception as e:
        print(f"❌ Message Bus failed: {e}")
        return
    
    # Test 3: Domain Advisor Agent
    print("\n3. Testing Domain Advisor Agent...")
    try:
        domain_advisor = DomainAdvisorAgent("test_domain_advisor")
        print("✅ Domain Advisor Agent created")
        
        # Test requirements analysis
        test_requirements = [
            "Users should be able to create and manage tasks",
            "System should support user authentication",
            "Tasks should be organized in projects",
            "System should send notifications for task updates",
            "Data should be stored securely and comply with GDPR"
        ]
        
        print("\n   Testing business requirements analysis...")
        response = await domain_advisor.analyze_business_requirements(
            requirements=test_requirements,
            domain="task_management",
            stakeholders=["project_managers", "team_members"],
            compliance_needs=["GDPR"]
        )
        
        if response.success:
            print("✅ Domain analysis completed successfully")
            print(f"   Confidence: {response.confidence:.2f}")
            print(f"   Execution time: {response.execution_time:.2f}s")
            
            # Check if we got expected results
            result = response.result
            if "domain_model" in result:
                entities = result["domain_model"].get("entities", [])
                print(f"   Found {len(entities)} domain entities")
                
            if "functional_requirements" in result:
                func_reqs = result["functional_requirements"]
                print(f"   Extracted {len(func_reqs)} functional requirements")
                
            if "technical_specifications" in result:
                tech_specs = result["technical_specifications"]
                print(f"   Generated technical specifications: {list(tech_specs.keys())}")
            
        else:
            print(f"❌ Domain analysis failed: {response.error}")
            if response.feedback:
                print(f"   Feedback: {response.feedback}")
        
    except Exception as e:
        print(f"❌ Domain Advisor test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Component Integration
    print("\n4. Testing Component Integration...")
    try:
        # Test task processing workflow
        test_task = Task(
            title="E-commerce Platform Analysis",
            description="Analyze requirements for building an e-commerce platform",
            requirements=[
                "Users can browse and search products",
                "Users can add items to cart and checkout",
                "System should handle payments securely",
                "Admin can manage inventory",
                "System should be scalable and performant"
            ],
            required_agent_role=AgentRole.DOMAIN_ADVISOR,
            metadata={
                "domain": "e-commerce",
                "stakeholders": ["customers", "admins", "merchants"],
                "compliance_needs": ["PCI-DSS", "GDPR"]
            }
        )
        
        response = await domain_advisor.process_task(test_task)
        
        if response.success:
            print("✅ Full workflow test passed")
            print(f"   Task processed in {response.execution_time:.2f}s")
            
            # Validate response structure
            expected_keys = ["domain_model", "functional_requirements", "technical_specifications"]
            missing_keys = [key for key in expected_keys if key not in response.result]
            
            if not missing_keys:
                print("✅ Response contains all expected components")
            else:
                print(f"⚠️  Missing components: {missing_keys}")
        else:
            print(f"❌ Workflow test failed: {response.error}")
    
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
    
    # Cleanup
    print("\n5. Cleanup...")
    try:
        await message_bus.stop()
        print("✅ Message Bus stopped")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Basic functionality testing completed!")
    print("\nNext steps:")
    print("- Add real LLM API keys to test with actual LLMs")
    print("- Implement Solution Architect Agent")
    print("- Implement Software Architect Agent")
    print("- Build the coding agents (Frontend, Backend, Infrastructure)")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())