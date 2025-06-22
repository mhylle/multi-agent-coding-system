"""
Core data types and structures for the multi-agent system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid


class AgentRole(Enum):
    """Defines the role and specialty of each agent in the system."""
    DOMAIN_ADVISOR = "domain_advisor"
    SOLUTION_ARCHITECT = "solution_architect"  
    SOFTWARE_ARCHITECT = "software_architect"
    FRONTEND_CODER = "frontend_coder"
    BACKEND_CODER = "backend_coder"
    INFRASTRUCTURE_CODER = "infrastructure_coder"
    TESTING_AGENT = "testing_agent"
    QUALITY_REVIEWER = "quality_reviewer"
    MASTER_ORCHESTRATOR = "master_orchestrator"


class TaskPriority(Enum):
    """Priority levels for task processing."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    """Status of task processing."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(Enum):
    """Types of messages in the system."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    COLLABORATION_REQUEST = "collaboration_request"
    WORKFLOW_CONTROL = "workflow_control"


@dataclass
class Task:
    """Represents a task to be processed by an agent."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    required_agent_role: Optional[AgentRole] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent after processing a task."""
    success: bool
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    feedback: List[str] = field(default_factory=list)
    confidence: float = 1.0
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    """Result of a quality review process."""
    approved: bool
    score: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Inter-agent communication message."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.TASK_REQUEST
    sender: str = ""
    recipient: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    requires_response: bool = False


@dataclass
class LLMRequest:
    """Request to LLM provider."""
    prompt: str
    model: str = "qwen3:14b"
    max_tokens: int = 4000
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    provider: str
    usage: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    response_time: Optional[float] = None
    request_id: Optional[str] = None


@dataclass
class ServiceRequest:
    """Request to a specialized service."""
    service_type: str
    operation: str
    data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    requester_id: str = ""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ServiceResponse:
    """Response from a specialized service."""
    success: bool
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    service_id: str = ""
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """Represents a step in a workflow."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    agent_role: AgentRole = AgentRole.DOMAIN_ADVISOR
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None
    estimated_duration: Optional[int] = None  # minutes
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class ImprovementContext:
    """Context passed to executors when retrying after review failure."""
    attempt_number: int
    previous_results: List[Dict[str, Any]] = field(default_factory=list)
    reviewer_feedback: List[str] = field(default_factory=list)
    reviewer_suggestions: List[str] = field(default_factory=list)
    quality_scores: List[float] = field(default_factory=list)
    improvement_history: List[str] = field(default_factory=list)
    delegation_candidates: List[AgentRole] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class Workflow:
    """Represents a complete workflow with multiple steps."""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    current_step: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


# Type aliases for common patterns
TaskResult = Union[AgentResponse, Dict[str, Any]]
ServiceInterface = type
AgentConfig = Dict[str, Any]