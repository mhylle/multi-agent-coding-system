"""
Communication protocols and message formatting utilities.
Provides standard message formats and helper functions.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.types import (
    Message, MessageType, TaskPriority, Task, AgentResponse,
    AgentRole, WorkflowStep, ServiceRequest
)


logger = logging.getLogger(__name__)


class ProtocolHelper:
    """Helper class for creating standardized messages between agents."""
    
    @staticmethod
    def create_task_request(sender: str, recipient: str, task: Task, 
                           priority: TaskPriority = TaskPriority.MEDIUM,
                           correlation_id: Optional[str] = None) -> Message:
        """Create a standardized task request message."""
        content = {
            "task": {
                "task_id": task.task_id,
                "title": task.title,
                "description": task.description,
                "requirements": task.requirements,
                "priority": task.priority.value,
                "required_agent_role": task.required_agent_role.value if task.required_agent_role else None,
                "dependencies": task.dependencies,
                "metadata": task.metadata,
                "context": task.context,
                "created_at": task.created_at.isoformat(),
                "deadline": task.deadline.isoformat() if task.deadline else None
            },
            "message_version": "1.0",
            "protocol": "task_request"
        }
        
        return Message(
            message_type=MessageType.TASK_REQUEST,
            sender=sender,
            recipient=recipient,
            content=content,
            priority=priority,
            correlation_id=correlation_id,
            requires_response=True
        )
    
    @staticmethod
    def create_task_response(sender: str, recipient: str, 
                           agent_response: AgentResponse, task_id: str,
                           correlation_id: Optional[str] = None) -> Message:
        """Create a standardized task response message."""
        content = {
            "task_id": task_id,
            "response": {
                "success": agent_response.success,
                "result": agent_response.result,
                "error": agent_response.error,
                "feedback": agent_response.feedback,
                "confidence": agent_response.confidence,
                "execution_time": agent_response.execution_time,
                "metadata": agent_response.metadata,
                "suggestions": agent_response.suggestions
            },
            "message_version": "1.0",
            "protocol": "task_response"
        }
        
        return Message(
            message_type=MessageType.TASK_RESPONSE,
            sender=sender,
            recipient=recipient,
            content=content,
            correlation_id=correlation_id
        )
    
    @staticmethod
    def create_status_update(sender: str, recipient: str, 
                           status: str, details: Dict[str, Any] = None,
                           task_id: Optional[str] = None) -> Message:
        """Create a status update message."""
        content = {
            "status": status,
            "details": details or {},
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "message_version": "1.0",
            "protocol": "status_update"
        }
        
        return Message(
            message_type=MessageType.STATUS_UPDATE,
            sender=sender,
            recipient=recipient,
            content=content,
            priority=TaskPriority.LOW
        )
    
    @staticmethod
    def create_error_report(sender: str, recipient: str, error: str,
                          context: Dict[str, Any] = None,
                          task_id: Optional[str] = None) -> Message:
        """Create an error report message."""
        content = {
            "error": error,
            "context": context or {},
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "message_version": "1.0",
            "protocol": "error_report"
        }
        
        return Message(
            message_type=MessageType.ERROR_REPORT,
            sender=sender,
            recipient=recipient,
            content=content,
            priority=TaskPriority.HIGH
        )
    
    @staticmethod
    def create_collaboration_request(sender: str, recipient: str,
                                   collaboration_type: str,
                                   data: Dict[str, Any],
                                   priority: TaskPriority = TaskPriority.MEDIUM) -> Message:
        """Create a collaboration request between agents."""
        content = {
            "collaboration_type": collaboration_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "message_version": "1.0",
            "protocol": "collaboration_request"
        }
        
        return Message(
            message_type=MessageType.COLLABORATION_REQUEST,
            sender=sender,
            recipient=recipient,
            content=content,
            priority=priority,
            requires_response=True
        )
    
    @staticmethod
    def create_workflow_control(sender: str, recipient: str,
                               command: str, workflow_data: Dict[str, Any],
                               priority: TaskPriority = TaskPriority.HIGH) -> Message:
        """Create a workflow control message."""
        content = {
            "command": command,
            "workflow_data": workflow_data,
            "timestamp": datetime.now().isoformat(),
            "message_version": "1.0",
            "protocol": "workflow_control"
        }
        
        return Message(
            message_type=MessageType.WORKFLOW_CONTROL,
            sender=sender,
            recipient=recipient,
            content=content,
            priority=priority
        )
    
    @staticmethod
    def extract_task_from_message(message: Message) -> Optional[Task]:
        """Extract a Task object from a task request message."""
        if message.message_type != MessageType.TASK_REQUEST:
            return None
        
        try:
            task_data = message.content.get("task", {})
            
            # Parse datetime fields
            created_at = datetime.fromisoformat(task_data["created_at"])
            deadline = None
            if task_data.get("deadline"):
                deadline = datetime.fromisoformat(task_data["deadline"])
            
            # Parse enum fields
            priority = TaskPriority(task_data.get("priority", "medium"))
            required_agent_role = None
            if task_data.get("required_agent_role"):
                required_agent_role = AgentRole(task_data["required_agent_role"])
            
            return Task(
                task_id=task_data["task_id"],
                title=task_data["title"],
                description=task_data["description"],
                requirements=task_data.get("requirements", []),
                priority=priority,
                required_agent_role=required_agent_role,
                dependencies=task_data.get("dependencies", []),
                metadata=task_data.get("metadata", {}),
                created_at=created_at,
                deadline=deadline,
                context=task_data.get("context", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to extract task from message: {str(e)}")
            return None
    
    @staticmethod
    def extract_agent_response_from_message(message: Message) -> Optional[AgentResponse]:
        """Extract an AgentResponse object from a task response message."""
        if message.message_type != MessageType.TASK_RESPONSE:
            return None
        
        try:
            response_data = message.content.get("response", {})
            
            return AgentResponse(
                success=response_data.get("success", False),
                result=response_data.get("result", {}),
                error=response_data.get("error"),
                feedback=response_data.get("feedback", []),
                confidence=response_data.get("confidence", 1.0),
                execution_time=response_data.get("execution_time"),
                metadata=response_data.get("metadata", {}),
                suggestions=response_data.get("suggestions", [])
            )
            
        except Exception as e:
            logger.error(f"Failed to extract agent response from message: {str(e)}")
            return None
    
    @staticmethod
    def validate_message_format(message: Message) -> Dict[str, Any]:
        """Validate message format and return validation results."""
        issues = []
        warnings = []
        
        # Check required fields
        if not message.sender:
            issues.append("Missing sender")
        
        if not message.recipient:
            issues.append("Missing recipient")
        
        if not message.content:
            warnings.append("Empty content")
        
        # Check protocol version if present
        if "message_version" in message.content:
            version = message.content["message_version"]
            if version != "1.0":
                warnings.append(f"Unsupported message version: {version}")
        
        # Validate content based on message type
        if message.message_type == MessageType.TASK_REQUEST:
            if "task" not in message.content:
                issues.append("Task request missing task data")
            elif "task_id" not in message.content["task"]:
                issues.append("Task request missing task_id")
        
        elif message.message_type == MessageType.TASK_RESPONSE:
            if "response" not in message.content:
                issues.append("Task response missing response data")
            elif "success" not in message.content["response"]:
                issues.append("Task response missing success flag")
        
        # Check message size (warn if large)
        try:
            message_size = len(json.dumps(message.content))
            if message_size > 100000:  # 100KB
                warnings.append(f"Large message size: {message_size} bytes")
        except:
            warnings.append("Could not determine message size")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "message_id": message.message_id,
            "message_type": message.message_type.value
        }
    
    @staticmethod
    def create_heartbeat(sender: str, recipient: str, 
                        status: Dict[str, Any] = None) -> Message:
        """Create a heartbeat message for health monitoring."""
        content = {
            "type": "heartbeat",
            "status": status or {"state": "active"},
            "timestamp": datetime.now().isoformat(),
            "message_version": "1.0",
            "protocol": "heartbeat"
        }
        
        return Message(
            message_type=MessageType.STATUS_UPDATE,
            sender=sender,
            recipient=recipient,
            content=content,
            priority=TaskPriority.LOW
        )
    
    @staticmethod
    def create_service_request_message(sender: str, recipient: str,
                                     service_request: ServiceRequest,
                                     priority: TaskPriority = TaskPriority.MEDIUM) -> Message:
        """Create a message for service requests."""
        content = {
            "service_request": {
                "service_type": service_request.service_type,
                "operation": service_request.operation,
                "data": service_request.data,
                "context": service_request.context,
                "requester_id": service_request.requester_id,
                "request_id": service_request.request_id
            },
            "message_version": "1.0",
            "protocol": "service_request"
        }
        
        return Message(
            message_type=MessageType.COLLABORATION_REQUEST,
            sender=sender,
            recipient=recipient,
            content=content,
            priority=priority,
            requires_response=True
        )


class MessageValidator:
    """Validates messages for security and format compliance."""
    
    @staticmethod
    def validate_content_security(content: Dict[str, Any]) -> Dict[str, Any]:
        """Check message content for potential security issues."""
        issues = []
        
        # Check for potentially dangerous content
        content_str = json.dumps(content).lower()
        
        dangerous_patterns = [
            "eval(",
            "exec(",
            "import os",
            "subprocess",
            "__import__",
            "file://",
            "javascript:",
            "<script"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content_str:
                issues.append(f"Potentially dangerous content detected: {pattern}")
        
        # Check for extremely long strings that might cause issues
        for key, value in content.items():
            if isinstance(value, str) and len(value) > 50000:
                issues.append(f"Very long string in field '{key}': {len(value)} characters")
        
        return {
            "secure": len(issues) == 0,
            "issues": issues
        }
    
    @staticmethod
    def sanitize_content(content: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize message content by removing or escaping dangerous elements."""
        # This is a basic implementation - in production, use proper sanitization
        sanitized = {}
        
        for key, value in content.items():
            if isinstance(value, str):
                # Basic sanitization - remove potential script tags
                sanitized[key] = value.replace("<script", "&lt;script").replace("</script>", "&lt;/script&gt;")
            elif isinstance(value, dict):
                sanitized[key] = MessageValidator.sanitize_content(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    MessageValidator.sanitize_content(item) if isinstance(item, dict)
                    else str(item).replace("<script", "&lt;script") if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized