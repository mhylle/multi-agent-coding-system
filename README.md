# Multi-Agent Coding System

A comprehensive multi-agent system that transforms business requirements into working software through collaborative AI agents. Each agent uses LLMs extensively for intelligent decision-making and follows the Service Delegation Pattern with hierarchical architecture.

## 🎯 Vision

Create a system where you can input business requirements and get complete, production-ready applications with:
- **Frontend code** (React/Vue components, styling, state management)
- **Backend code** (APIs, business logic, database operations)
- **Infrastructure code** (Docker, CI/CD, deployment scripts)
- **Comprehensive tests** (unit, integration, e2e)
- **Quality assurance** (code review, security scanning)

## 🏗️ Architecture

### Core Principles
- **Service Delegation Pattern**: Agents delegate specialized work to focused services
- **Hierarchical Agent Design**: Each agent has Orchestrator → Executor → Reviewer components
- **Real Dynamic Logic**: No hardcoded responses - everything uses LLM reasoning
- **Loose Coupling**: Communication through interfaces and message passing

### Agent Workflow
```
Business Requirements → Domain Advisor → Solution Architect → Software Architect
                                    ↓
Frontend Coder ← Master Orchestrator → Backend Coder → Infrastructure Coder
                                    ↓
Testing Agent → Quality Reviewer → Working Application
```

## 🤖 Current Status (Phase 1 Complete)

### ✅ Implemented Components
- **Base Agent Framework**: Hierarchical agent pattern (Orchestrator → Executor → Reviewer)
- **LLM Integration**: Unified client supporting Anthropic Claude and OpenAI
- **Message Bus**: Priority-based inter-agent communication
- **Domain Advisor Agent**: Complete business requirements analysis agent

### Core Infrastructure
- **Error Handling**: Comprehensive error handling with graceful fallbacks
- **Async Processing**: Full async/await support throughout
- **Quality Assurance**: Multi-level validation and review processes
- **Testing Framework**: Mock testing for development without API keys

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- API keys for LLM providers (Anthropic Claude, OpenAI)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd multi-agent-coding-system
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

```python
import asyncio
from src.core.llm_client import initialize_llm_client
from src.agents.domain_advisor.domain_advisor import DomainAdvisorAgent

async def main():
    # Initialize LLM client
    config = {
        "anthropic_api_key": "your-key-here",
        "default_provider": "anthropic"
    }
    initialize_llm_client(config)
    
    # Create Domain Advisor
    domain_advisor = DomainAdvisorAgent()
    
    # Analyze business requirements
    requirements = [
        "Users can create and manage tasks",
        "System supports team collaboration", 
        "Real-time notifications for updates",
        "Secure user authentication",
        "GDPR compliant data handling"
    ]
    
    response = await domain_advisor.analyze_business_requirements(
        requirements=requirements,
        domain="task_management",
        stakeholders=["project_managers", "team_members"],
        compliance_needs=["GDPR"]
    )
    
    if response.success:
        print("Analysis completed!")
        print(f"Confidence: {response.confidence}")
        # Access structured results
        domain_model = response.result["domain_model"]
        technical_specs = response.result["technical_specifications"]
    else:
        print(f"Analysis failed: {response.error}")

asyncio.run(main())
```

### Testing

Run basic functionality tests:
```bash
python test_basic_functionality.py
```

## 🤖 Implemented Agents

### ✅ Domain Advisor Agent
**Status**: Complete  
**Purpose**: Translates business requirements into technical specifications

**Capabilities**:
- Domain modeling (entities, relationships, business rules)
- Requirements analysis (functional, non-functional, compliance)
- User persona and use case development
- Technical specification generation

## 🚧 Planned Agents

### Solution Architect Agent
**Purpose**: High-level system architecture design
- Architecture pattern selection (microservices, monolith, serverless)
- Technology stack recommendations
- Scalability and deployment strategies

### Software Architect Agent  
**Purpose**: Detailed component and API design
- Component boundary design
- REST API specifications with OpenAPI
- Database schema design

### Implementation Agents
- **Frontend Coder**: React/Vue components, state management, styling
- **Backend Coder**: API endpoints, business logic, data access
- **Infrastructure Coder**: Docker, CI/CD, cloud deployment

### Quality Assurance Agents
- **Testing Agent**: Comprehensive test generation (unit, integration, e2e)
- **Quality Reviewer**: Code review, security scanning, compliance

### Master Orchestrator
**Purpose**: End-to-end workflow coordination and progress monitoring

## 📁 Project Structure

```
src/
├── core/                          # Core system components
│   ├── types.py                  # Data structures and enums
│   ├── llm_client.py             # LLM integration
│   └── base_agent.py             # Base agent framework
├── communication/                 # Inter-agent communication
│   ├── message_bus.py            # Priority message routing
│   └── protocols.py              # Standard message formats
├── agents/                       # Agent implementations
│   └── domain_advisor/           # Business requirements analysis
│       ├── domain_advisor.py
│       └── prompts.py
└── orchestrator/                 # Workflow coordination (planned)

docs/                             # Documentation
├── multi-agent-system-design.md
├── technical-architecture.md
├── agent-specifications.md
├── api-documentation.md
└── development-guide.md

IMPLEMENTATION_PLAN.md            # Detailed implementation roadmap
```

## 🛠️ Technology Stack

- **Python 3.9+**: Core implementation
- **AsyncIO**: Asynchronous processing
- **Anthropic Claude**: Primary LLM for analysis and generation
- **OpenAI GPT**: Secondary LLM for specialized tasks
- **HTTPX**: HTTP client for LLM APIs
- **Pydantic**: Data validation and serialization

## 🔄 Current Status

**Phase 1 Complete (Core Infrastructure)**:
- ✅ Base agent framework with hierarchical architecture
- ✅ LLM integration with error handling and retries  
- ✅ Priority-based message bus for agent communication
- ✅ Domain Advisor Agent with real LLM-powered analysis
- ✅ Comprehensive testing framework

**Phase 2 In Progress (Analysis Agents)**:
- 🔄 Solution Architect Agent
- 🔄 Software Architect Agent

## 🧪 Testing

The system includes comprehensive testing:

- **Mock Testing**: Test functionality without API keys
- **Integration Testing**: Test agent workflows end-to-end
- **Unit Testing**: Test individual components
- **LLM Response Validation**: Ensure structured outputs

Run tests:
```bash
# Basic functionality (uses mocks)
python test_basic_functionality.py

# Full test suite (requires API keys)
pytest src/tests/
```

## 🤝 Contributing

1. Read the [Development Guide](docs/development-guide.md)
2. Follow the Service Delegation Pattern
3. Ensure single responsibility (files ≤150 lines)
4. Include comprehensive tests
5. Use real LLM logic (no hardcoded responses)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Inspiration

Based on agent patterns from [Anthropic's Agent Cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents), implementing:
- Prompt chaining for sequential processing
- Parallelization for concurrent tasks
- Routing for specialized agent selection
- Orchestrator-workers for coordination
- Evaluator-optimizer for quality assurance

## 🛣️ Roadmap

### Near Term (Weeks 1-4)
- Complete Solution Architect Agent
- Complete Software Architect Agent
- Begin implementation agents

### Medium Term (Weeks 5-8)  
- Frontend Coder Agent
- Backend Coder Agent
- Infrastructure Coder Agent

### Long Term (Weeks 9-12)
- Testing Agent
- Quality Reviewer Agent
- Master Orchestrator
- Production deployment

## 📞 Support

For questions, issues, or contributions:
- Create an issue for bugs or feature requests
- See documentation in the `docs/` folder
- Follow coding standards in `docs/development-guide.md`

---

**Built with ❤️ using Claude and the Service Delegation Pattern**