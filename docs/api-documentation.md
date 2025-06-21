# API Documentation

## System Usage Guide

This document describes how to use the current multi-agent coding system to analyze business requirements and generate technical specifications.

## Available Agents

### 1. Domain Advisor Agent
**Purpose**: Translates business requirements into technical specifications  
**Input**: Business requirements, user stories, compliance needs  
**Output**: Technical specifications, domain model, validation rules

### 2. Solution Architect Agent  
**Purpose**: Creates high-level system architecture  
**Input**: Domain specifications from Domain Advisor  
**Output**: Architecture pattern, technology stack, implementation roadmap

### 3. Software Architect Agent
**Purpose**: Detailed component and API design  
**Input**: Solution architecture specifications  
**Output**: Component design, API specifications, database schema, implementation guides

## Usage Examples

### Basic Workflow

```python
import asyncio
from src.core.task_manager import TaskManager
from src.core.types import Task, TaskPriority, AgentRole
from src.communication.message_bus import MessageBus
from src.agents.domain_advisor.domain_advisor import DomainAdvisorAgent
from src.agents.solution_architect.solution_architect import SolutionArchitectAgent
from src.agents.software_architect.software_architect import SoftwareArchitectAgent

async def analyze_project_requirements():
    # Initialize system
    message_bus = MessageBus()
    task_manager = TaskManager(message_bus)
    
    # Initialize agents
    domain_advisor = DomainAdvisorAgent()
    solution_architect = SolutionArchitectAgent()
    software_architect = SoftwareArchitectAgent()
    
    # Register agents
    task_manager.register_agent(domain_advisor.agent_id, AgentRole.DOMAIN_ADVISOR)
    task_manager.register_agent(solution_architect.agent_id, AgentRole.SOLUTION_ARCHITECT)
    task_manager.register_agent(software_architect.agent_id, AgentRole.SOFTWARE_ARCHITECT)
    
    # Start task manager
    await task_manager.start()
    
    # Create domain analysis task
    domain_task = Task(
        title="Analyze Task Management App Requirements",
        description="Build a task management application with user authentication, task CRUD operations, and team collaboration features",
        requirements=[
            "Users can create, read, update, and delete tasks",
            "Users can assign tasks to team members", 
            "Users can organize tasks into projects",
            "System must support real-time notifications",
            "Application must be secure and scalable"
        ],
        priority=TaskPriority.HIGH,
        metadata={
            "required_agent_role": AgentRole.DOMAIN_ADVISOR,
            "domain": "task_management"
        }
    )
    
    # Submit domain analysis task
    domain_task_id = await task_manager.submit_task(domain_task, workflow_id="task_mgmt_app")
    
    # Wait for completion and get results
    while task_manager.get_task_status(domain_task_id)["status"] != "completed":
        await asyncio.sleep(1)
    
    domain_result = task_manager.tasks[domain_task_id].result
    print("Domain Analysis Complete:", domain_result)
    
    # Create solution architecture task
    solution_task = Task(
        title="Design System Architecture",
        description="Create high-level architecture for task management application",
        priority=TaskPriority.HIGH,
        metadata={
            "required_agent_role": AgentRole.SOLUTION_ARCHITECT,
            "domain_specifications": domain_result
        }
    )
    
    solution_task_id = await task_manager.submit_task(solution_task, workflow_id="task_mgmt_app")
    
    # Wait for solution architecture
    while task_manager.get_task_status(solution_task_id)["status"] != "completed":
        await asyncio.sleep(1)
    
    solution_result = task_manager.tasks[solution_task_id].result
    print("Solution Architecture Complete:", solution_result)
    
    # Create software architecture task
    software_task = Task(
        title="Design Detailed Components",
        description="Create detailed component design and API specifications",
        priority=TaskPriority.HIGH,
        metadata={
            "required_agent_role": AgentRole.SOFTWARE_ARCHITECT,
            "solution_architecture": solution_result
        }
    )
    
    software_task_id = await task_manager.submit_task(software_task, workflow_id="task_mgmt_app")
    
    # Wait for software architecture
    while task_manager.get_task_status(software_task_id)["status"] != "completed":
        await asyncio.sleep(1)
    
    software_result = task_manager.tasks[software_task_id].result
    print("Software Architecture Complete:", software_result)
    
    # Cleanup
    await task_manager.stop()

# Run the example
asyncio.run(analyze_project_requirements())
```

## Agent APIs

### Domain Advisor Agent

#### Input Format
```python
task = Task(
    title="Business Analysis Task",
    description="Detailed description of business requirements",
    requirements=[
        "Specific requirement 1",
        "Specific requirement 2", 
        "Compliance requirement"
    ],
    metadata={
        "required_agent_role": AgentRole.DOMAIN_ADVISOR,
        "domain": "business_domain",
        "stakeholders": ["users", "admins"],
        "compliance_needs": ["GDPR", "SOC2"]
    }
)
```

#### Output Format
```python
{
    "analysis_type": "user_requirements_analysis",
    "domain_model": {
        "entities": ["User", "Task", "Project", "Team"],
        "relationships": [...],
        "business_rules": [...]
    },
    "functional_requirements": [...],
    "non_functional_requirements": [...],
    "user_personas": [...],
    "use_cases": [...],
    "technical_specifications": {
        "authentication": "Multi-factor authentication required",
        "authorization": "Role-based access control",
        "data_handling": "Encryption at rest and in transit"
    }
}
```

### Solution Architect Agent

#### Input Format
```python
task = Task(
    title="Architecture Design Task",
    description="Create system architecture",
    metadata={
        "required_agent_role": AgentRole.SOLUTION_ARCHITECT,
        "domain_specifications": domain_advisor_result
    }
)
```

#### Output Format
```python
{
    "specification_type": "solution_architecture", 
    "architecture_overview": {
        "recommended_architecture": "modular_monolith",
        "architecture_specifications": {...},
        "scalability_assessment": {...},
        "deployment_strategy": {...}
    },
    "technology_stack": {
        "recommended_stack": {
            "frontend": {"framework": "React", "state_management": "Redux"},
            "backend": {"language": "Node.js + TypeScript", "framework": "Express.js"},
            "database": {"primary": "PostgreSQL", "caching": "Redis"}
        },
        "rationale": {...},
        "alternatives": {...}
    },
    "implementation_roadmap": [...],
    "risk_analysis": [...],
    "decision_log": [...]
}
```

### Software Architect Agent

#### Input Format
```python
task = Task(
    title="Detailed Design Task",
    description="Create component and API specifications",
    metadata={
        "required_agent_role": AgentRole.SOFTWARE_ARCHITECT,
        "solution_architecture": solution_architect_result
    }
)
```

#### Output Format
```python
{
    "specification_type": "software_architecture",
    "component_design": {
        "components": [
            {
                "name": "UserManagementComponent",
                "responsibility": "Handle user authentication and management",
                "entities": ["User", "Role", "Permission"],
                "interfaces": ["IUserService", "IAuthService"],
                "dependencies": []
            }
        ],
        "interfaces": {...},
        "quality_analysis": {...}
    },
    "api_specifications": {
        "api_specifications": {
            "UserManagementComponent": {
                "base_path": "/api/v1/user-management",
                "endpoints": [...]
            }
        },
        "data_transfer_objects": [...],
        "openapi_specification": {...}
    },
    "data_architecture": {
        "database_schema": {...},
        "data_models": [...],
        "relationships": {...}
    },
    "implementation_guides": {
        "development_workflow": {...},
        "coding_standards": {...},
        "testing_approach": {...}
    }
}
```

## Direct Agent Usage

### Using Agents Directly

```python
async def use_domain_advisor_directly():
    # Create agent
    agent = DomainAdvisorAgent()
    
    # Create task
    task = Task(
        title="E-commerce Analysis",
        description="Analyze requirements for an e-commerce platform",
        requirements=[
            "Product catalog management",
            "Shopping cart functionality", 
            "Payment processing",
            "Order management",
            "User accounts"
        ]
    )
    
    # Process task
    result = await agent.process_task(task)
    
    if result.success:
        print("Domain analysis successful!")
        print(f"Analysis result: {result.result}")
    else:
        print(f"Analysis failed: {result.error}")
        print(f"Feedback: {result.feedback}")

asyncio.run(use_domain_advisor_directly())
```

### Service-Level Usage

```python
from src.services.delegation_service import DelegationRequest, get_service_delegator
from src.agents.solution_architect.interfaces.architecture_analysis_interface import IArchitectureAnalysisService

async def use_architecture_service_directly():
    # Get service delegator
    delegator = get_service_delegator()
    
    # Create delegation request
    request = DelegationRequest(
        service_type=IArchitectureAnalysisService,
        task=Task(title="Architecture Analysis"),
        context={
            "domain_specifications": {
                "domain_model": {"entities": ["User", "Product", "Order"]},
                "scalability_requirements": ["high_load", "global_distribution"]
            }
        },
        requester_id="direct_client"
    )
    
    # Delegate request
    result = await delegator.delegate_request(request)
    
    if result.success:
        print("Service delegation successful!")
        print(f"Service result: {result.response.result}")
    else:
        print(f"Service delegation failed: {result.error}")

asyncio.run(use_architecture_service_directly())
```

## Message Bus Usage

### Send Messages Between Agents

```python
from src.communication.message_bus import MessageBus
from src.communication.protocols import ProtocolHelper, MessageType

async def agent_communication_example():
    # Create message bus
    message_bus = MessageBus()
    
    # Register message handler
    async def handle_message(message):
        print(f"Received message: {message.message_type}")
        print(f"Content: {message.content}")
    
    message_bus.register_agent("agent1", handle_message)
    
    # Create and send message
    message = ProtocolHelper.create_task_request(
        sender="agent2",
        recipient="agent1", 
        task=Task(title="Collaboration Request"),
        priority=TaskPriority.HIGH
    )
    
    success = await message_bus.send_message(message)
    print(f"Message sent: {success}")

asyncio.run(agent_communication_example())
```

## Configuration and Setup

### System Configuration

```python
# config.py
SYSTEM_CONFIG = {
    "message_bus": {
        "max_queue_size": 1000,
        "message_retention": 10000
    },
    "task_manager": {
        "max_concurrent_tasks": 50,
        "dependency_check_interval": 5.0
    },
    "service_registry": {
        "health_check_interval": 30.0,
        "service_timeout": 60.0
    }
}
```

### Agent Configuration

```python
# Agent-specific configuration
AGENT_CONFIG = {
    "domain_advisor": {
        "analysis_depth": "comprehensive",
        "compliance_checking": True
    },
    "solution_architect": {
        "architecture_preferences": ["microservices", "modular_monolith"],
        "technology_constraints": []
    },
    "software_architect": {
        "design_patterns": ["repository", "service_layer"],
        "api_style": "REST"
    }
}
```

## Error Handling

### Common Error Scenarios

```python
try:
    result = await agent.process_task(task)
    if not result.success:
        if "validation" in result.error.lower():
            # Handle validation errors
            print("Input validation failed")
            print(f"Feedback: {result.feedback}")
        elif "timeout" in result.error.lower():
            # Handle timeout errors
            print("Task processing timed out")
        else:
            # Handle other errors
            print(f"Task failed: {result.error}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

### Service Delegation Errors

```python
result = await delegator.delegate_request(request)

if not result.success:
    if "no services available" in result.error:
        print("No services registered for this interface")
    elif "service overloaded" in result.error:
        print("All services are currently overloaded")
    elif "capability mismatch" in result.error:
        print("No services can handle this request type")
    else:
        print(f"Delegation failed: {result.error}")
```

## Monitoring and Debugging

### Get System Status

```python
# Check task manager status
status = task_manager.get_system_status()
print(f"System status: {status}")

# Check message bus health
health = await message_bus.health_check()
print(f"Message bus health: {health}")

# Check service registry
services = get_service_registry().get_registered_services()
print(f"Registered services: {services}")
```

### Performance Monitoring

```python
# Get agent performance metrics
agent_status = agent.get_status()
print(f"Agent performance: {agent_status['performance_metrics']}")

# Get service delegation statistics
delegator_stats = delegator.get_system_stats()
print(f"Delegation stats: {delegator_stats}")
```

This API documentation provides comprehensive guidance for using the current multi-agent system effectively.