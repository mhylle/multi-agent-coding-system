# Development Guide

## Getting Started

### Prerequisites
- Python 3.9+
- Understanding of async/await patterns
- Familiarity with dependency injection concepts
- Basic knowledge of service-oriented architecture

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run basic system test
python -m pytest src/tests/ -v
```

## Adding a New Agent

### Step 1: Define Agent Structure
Create directory structure following the pattern:
```
src/agents/my_agent/
├── __init__.py
├── my_agent.py                 # Main agent class
├── interfaces/                 # Service contracts
│   └── my_service_interface.py
├── services/                   # Service implementations  
│   └── my_service.py
└── components/                 # Agent components
    ├── orchestrator.py
    ├── executor.py
    └── reviewer.py
```

### Step 2: Define Service Interfaces
```python
# interfaces/my_service_interface.py
from typing import Dict, Any, Protocol

class IMyService(Protocol):
    async def process_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        ...
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data format."""
        ...
```

### Step 3: Implement Service
```python
# services/my_service.py
from ....services.delegation_service import BaseDelegationService, DelegationRequest
from ....core.types import AgentResponse
from ..interfaces.my_service_interface import IMyService

class MyService(BaseDelegationService):
    def __init__(self):
        super().__init__("my_service")
        self._capabilities = ["data_processing", "validation"]
    
    async def _process_request(self, request: DelegationRequest) -> AgentResponse:
        input_data = request.context.get("input_data", {})
        
        # Process the data
        result = await self.process_data(input_data)
        
        return AgentResponse(
            success=True,
            result=result,
            confidence=0.85
        )
    
    async def process_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation logic here
        return {"processed": input_data}
```

### Step 4: Implement Agent Components

**Orchestrator:**
```python
# components/orchestrator.py
from ....core.base_agent import BaseOrchestrator
from ....core.types import Task

class MyAgentOrchestrator(BaseOrchestrator):
    async def _create_execution_plan(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "workflow_type": "my_workflow",
            "required_services": ["my_service"],
            "execution_stages": [
                {
                    "stage": "data_processing",
                    "service": "my_service",
                    "dependencies": []
                }
            ]
        }
```

**Executor:**
```python
# components/executor.py
from ....core.base_agent import BaseExecutor
from ....services.delegation_service import DelegationRequest, get_service_delegator
from ..interfaces.my_service_interface import IMyService

class MyAgentExecutor(BaseExecutor):
    def __init__(self, agent_name: str):
        super().__init__(agent_name)
        self.delegator = get_service_delegator()
    
    async def _execute_task(self, task: Task, execution_plan: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Delegate to service
        request = DelegationRequest(
            service_type=IMyService,
            task=task,
            context=context,
            requester_id=self.agent_name
        )
        
        result = await self.delegator.delegate_request(request)
        return result.response.result if result.success else {}
```

**Reviewer:**
```python
# components/reviewer.py
from ....core.base_agent import BaseReviewer
from ....core.types import ReviewResult

class MyAgentReviewer(BaseReviewer):
    async def _review_result(self, task: Task, execution_result: Dict[str, Any], context: Dict[str, Any]) -> ReviewResult:
        # Validate results
        issues = []
        suggestions = []
        score = 0.8
        
        if not execution_result:
            issues.append("No results produced")
            score = 0.0
        
        return ReviewResult(
            approved=len(issues) == 0,
            score=score,
            issues=issues,
            suggestions=suggestions,
            strengths=["Results generated successfully"] if execution_result else []
        )
```

### Step 5: Implement Main Agent Class
```python
# my_agent.py
from ...core.base_agent import BaseAgent
from ...core.types import AgentRole
from ...services.delegation_service import get_service_delegator
from .interfaces.my_service_interface import IMyService
from .services.my_service import MyService
from .components.orchestrator import MyAgentOrchestrator
from .components.executor import MyAgentExecutor
from .components.reviewer import MyAgentReviewer

class MyAgent(BaseAgent):
    def __init__(self, agent_id: str = "my_agent_001"):
        super().__init__(agent_id, AgentRole.MY_AGENT)  # Add to AgentRole enum
        self._register_services()
    
    def _register_services(self):
        delegator = get_service_delegator()
        service = MyService()
        delegator.register_service(IMyService, service)
    
    def _create_orchestrator(self) -> BaseOrchestrator:
        return MyAgentOrchestrator(self.agent_id)
    
    def _create_executor(self) -> BaseExecutor:
        return MyAgentExecutor(self.agent_id)
    
    def _create_reviewer(self) -> BaseReviewer:
        return MyAgentReviewer(self.agent_id)
```

## Best Practices

### File Organization
- **Keep files small**: Target 50-150 lines per file
- **Single responsibility**: Each file should have one clear purpose
- **Logical grouping**: Interfaces, services, and components in separate folders
- **Clear naming**: Use descriptive names that indicate purpose

### Service Design
- **Interface first**: Always define the interface before implementation
- **Focused capabilities**: Each service should have a narrow, well-defined scope
- **Error handling**: Provide meaningful error messages and proper error types
- **Documentation**: Document service contracts and expected behavior

### Agent Design
- **Orchestrator planning**: Keep orchestrators focused on workflow planning
- **Executor delegation**: Executors should primarily delegate, not implement logic
- **Reviewer validation**: Reviewers should validate quality and completeness
- **Service registration**: Register all services in agent constructor

### Testing Strategy
- **Unit tests**: Test each service independently
- **Integration tests**: Test agent components together
- **Mock services**: Use test doubles for external dependencies
- **Error scenarios**: Test failure cases and error handling

### Code Quality
- **Type hints**: Use type hints for all function parameters and returns
- **Async/await**: Use async patterns consistently throughout
- **Error handling**: Catch and handle exceptions appropriately
- **Logging**: Use structured logging with appropriate levels

## Common Patterns

### Service with Multiple Capabilities
```python
class MultiCapabilityService(BaseDelegationService):
    def __init__(self):
        super().__init__("multi_service")
        self._capabilities = ["text_processing", "data_validation", "format_conversion"]
    
    async def _process_request(self, request: DelegationRequest) -> AgentResponse:
        operation = request.context.get("operation")
        
        if operation == "text_processing":
            return await self._process_text(request)
        elif operation == "data_validation":
            return await self._validate_data(request)
        elif operation == "format_conversion":
            return await self._convert_format(request)
        else:
            return AgentResponse(success=False, error="Unknown operation")
```

### Helper Classes
```python
# For complex logic, use helper classes
class DataProcessingHelper:
    def __init__(self):
        self.processor = DataProcessor()
    
    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Complex transformation logic
        return transformed_data
    
    def validate_schema(self, data: Dict[str, Any]) -> bool:
        # Schema validation logic
        return is_valid

# Use in service
class MyService(BaseDelegationService):
    def __init__(self):
        super().__init__("my_service")
        self.helper = DataProcessingHelper()
    
    async def _process_request(self, request: DelegationRequest) -> AgentResponse:
        data = request.context.get("data")
        processed_data = self.helper.transform_data(data)
        return AgentResponse(success=True, result=processed_data)
```

### Error Handling Pattern
```python
async def _process_request(self, request: DelegationRequest) -> AgentResponse:
    try:
        # Validate input
        if not self._validate_input(request.context):
            return AgentResponse(
                success=False,
                error="Invalid input data",
                feedback=["Check input format", "Ensure required fields are present"]
            )
        
        # Process request
        result = await self._do_processing(request.context)
        
        return AgentResponse(
            success=True,
            result=result,
            confidence=0.9
        )
        
    except ValidationError as e:
        return AgentResponse(
            success=False,
            error=f"Validation failed: {str(e)}",
            feedback=["Fix validation errors", "Check data format"]
        )
    except Exception as e:
        self.logger.error(f"Unexpected error: {str(e)}")
        return AgentResponse(
            success=False,
            error="Internal processing error"
        )
```

## Debugging and Troubleshooting

### Logging Configuration
```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# In your service/agent
self.logger = logging.getLogger(f"MyService.{self.service_id}")
self.logger.info("Processing request")
self.logger.debug(f"Input data: {data}")
self.logger.error(f"Processing failed: {error}")
```

### Common Issues

**Service Not Found**
- Check service registration in agent constructor
- Verify interface import and type matching
- Ensure service is properly inherited from BaseDelegationService

**Message Delivery Failures**
- Check agent registration with message bus
- Verify message format matches protocol
- Check message priority and queue status

**Task Execution Timeouts**
- Review service processing time
- Check for blocking operations
- Verify async/await usage

**Memory Issues**
- Monitor service instance lifecycle
- Check for proper cleanup in dispose methods
- Review message history retention settings

## Performance Optimization

### Service Optimization
- Use connection pooling for database operations
- Implement caching for expensive operations
- Batch processing for multiple items
- Lazy loading for optional data

### Agent Optimization
- Parallel execution of independent services
- Early validation to avoid unnecessary processing
- Result caching for repeated requests
- Efficient error handling and recovery

### System Optimization
- Monitor service load and adjust delegation strategies
- Tune message queue sizes and priorities
- Optimize service discovery and routing
- Profile and optimize hot code paths

This development guide provides the foundation for extending the multi-agent system while maintaining quality and consistency.