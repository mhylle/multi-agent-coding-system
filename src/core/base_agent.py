"""
Base agent class implementing the hierarchical agent pattern.
Each agent has Orchestrator, Executor, and Reviewer components.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from .types import (
    Task, AgentResponse, AgentRole, ReviewResult, 
    LLMRequest, TaskStatus
)
from .llm_client import get_llm_client


logger = logging.getLogger(__name__)


class BaseOrchestrator(ABC):
    """
    Base class for agent orchestrators.
    Responsible for analyzing tasks and creating execution plans.
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.llm_client = get_llm_client()
    
    async def orchestrate(self, task: Task, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze the task and create an execution plan.
        Uses LLM to understand requirements and plan approach.
        """
        if context is None:
            context = {}
        
        try:
            # Create execution plan using LLM
            execution_plan = await self._create_execution_plan(task, context)
            
            # Validate the plan
            validation_result = await self._validate_execution_plan(execution_plan, task)
            
            if not validation_result["valid"]:
                # Revise plan if validation failed
                execution_plan = await self._revise_execution_plan(
                    execution_plan, validation_result["issues"], task, context
                )
            
            logger.info(f"Orchestrator {self.agent_id} created execution plan for task {task.task_id}")
            
            return {
                "execution_plan": execution_plan,
                "estimated_duration": execution_plan.get("estimated_duration", 300),  # 5 min default
                "required_resources": execution_plan.get("required_resources", []),
                "success_criteria": execution_plan.get("success_criteria", []),
                "quality_gates": execution_plan.get("quality_gates", [])
            }
            
        except Exception as e:
            logger.error(f"Orchestration failed for task {task.task_id}: {str(e)}")
            return {
                "execution_plan": {"error": f"Orchestration failed: {str(e)}"},
                "estimated_duration": 0,
                "success": False
            }
    
    @abstractmethod
    async def _create_execution_plan(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed execution plan for the task."""
        pass
    
    async def _validate_execution_plan(self, plan: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Validate the execution plan using LLM."""
        validation_prompt = f"""
        Review this execution plan for completeness and feasibility:
        
        Task: {task.title}
        Description: {task.description}
        Requirements: {task.requirements}
        
        Execution Plan:
        {plan}
        
        Evaluate:
        1. Does the plan address all requirements?
        2. Are the steps logical and achievable?
        3. Are there any missing elements?
        4. Are the estimated durations realistic?
        
        Respond with JSON:
        {{
            "valid": boolean,
            "confidence": float (0-1),
            "issues": ["list of issues if any"],
            "suggestions": ["list of improvements"]
        }}
        """
        
        request = LLMRequest(
            prompt=validation_prompt,
            system_prompt="You are an expert at validating technical execution plans.",
            max_tokens=1000
        )
        
        response = await self.llm_client.generate_response(request)
        
        if response.success:
            try:
                return await self.llm_client.parse_structured_response(response)
            except:
                return {"valid": True, "confidence": 0.5, "issues": [], "suggestions": []}
        else:
            return {"valid": True, "confidence": 0.5, "issues": [], "suggestions": []}
    
    async def _revise_execution_plan(self, original_plan: Dict[str, Any], 
                                   issues: List[str], task: Task, 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Revise execution plan based on validation issues."""
        revision_prompt = f"""
        Revise this execution plan to address the identified issues:
        
        Original Plan:
        {original_plan}
        
        Issues to Address:
        {issues}
        
        Task Context:
        Title: {task.title}
        Description: {task.description}
        Requirements: {task.requirements}
        
        Provide an improved execution plan as JSON.
        """
        
        request = LLMRequest(
            prompt=revision_prompt,
            system_prompt="You are an expert at creating robust execution plans.",
            max_tokens=2000
        )
        
        response = await self.llm_client.generate_response(request)
        
        if response.success:
            try:
                revised_plan = await self.llm_client.parse_structured_response(response)
                return revised_plan
            except:
                return original_plan
        else:
            return original_plan


class BaseExecutor(ABC):
    """
    Base class for agent executors.
    Responsible for executing the plan and coordinating with services.
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.llm_client = get_llm_client()
    
    async def execute(self, task: Task, execution_plan: Dict[str, Any], 
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the task according to the execution plan.
        Coordinates with specialized services and LLMs.
        """
        if context is None:
            context = {}
        
        try:
            start_time = time.time()
            
            # Execute the main task logic
            result = await self._execute_task(task, execution_plan, context)
            
            execution_time = time.time() - start_time
            
            logger.info(f"Executor {self.agent_id} completed task {task.task_id} "
                       f"in {execution_time:.2f}s")
            
            return {
                "result": result,
                "execution_time": execution_time,
                "success": True,
                "metadata": {
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "execution_plan_used": execution_plan
                }
            }
            
        except Exception as e:
            logger.error(f"Execution failed for task {task.task_id}: {str(e)}")
            return {
                "result": {},
                "execution_time": 0,
                "success": False,
                "error": str(e),
                "metadata": {"agent_id": self.agent_id, "task_id": task.task_id}
            }
    
    @abstractmethod
    async def _execute_task(self, task: Task, execution_plan: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the core task logic."""
        pass


class BaseReviewer(ABC):
    """
    Base class for agent reviewers.
    Responsible for validating outputs and ensuring quality.
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.llm_client = get_llm_client()
    
    async def review(self, task: Task, execution_result: Dict[str, Any], 
                    context: Dict[str, Any] = None) -> ReviewResult:
        """
        Review the execution result for quality and completeness.
        Uses LLM to assess whether the output meets requirements.
        """
        if context is None:
            context = {}
        
        try:
            # Perform the review using LLM
            review_result = await self._review_result(task, execution_result, context)
            
            # Additional automated checks
            automated_checks = await self._perform_automated_checks(execution_result)
            
            # Combine results
            final_score = (review_result.score + automated_checks.get("score", 1.0)) / 2
            
            all_issues = review_result.issues + automated_checks.get("issues", [])
            all_suggestions = review_result.suggestions + automated_checks.get("suggestions", [])
            
            final_result = ReviewResult(
                approved=review_result.approved and len(all_issues) == 0,
                score=final_score,
                issues=all_issues,
                suggestions=all_suggestions,
                strengths=review_result.strengths,
                metadata={
                    "reviewer_id": self.agent_id,
                    "task_id": task.task_id,
                    "llm_review": review_result.metadata,
                    "automated_checks": automated_checks
                }
            )
            
            logger.info(f"Reviewer {self.agent_id} completed review for task {task.task_id}: "
                       f"approved={final_result.approved}, score={final_result.score:.2f}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Review failed for task {task.task_id}: {str(e)}")
            return ReviewResult(
                approved=False,
                score=0.0,
                issues=[f"Review process failed: {str(e)}"],
                suggestions=["Retry the review process"],
                strengths=[],
                metadata={"error": str(e)}
            )
    
    @abstractmethod
    async def _review_result(self, task: Task, execution_result: Dict[str, Any], 
                           context: Dict[str, Any]) -> ReviewResult:
        """Perform detailed review of execution result."""
        pass
    
    async def _perform_automated_checks(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform automated quality checks."""
        checks = {
            "has_result": len(execution_result.get("result", {})) > 0,
            "has_success_flag": "success" in execution_result,
            "no_errors": execution_result.get("error") is None
        }
        
        score = sum(checks.values()) / len(checks)
        issues = [f"Failed check: {check}" for check, passed in checks.items() if not passed]
        
        return {
            "score": score,
            "issues": issues,
            "suggestions": ["Address failed automated checks"] if issues else [],
            "checks_performed": checks
        }


class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    Implements the hierarchical agent pattern with orchestrator, executor, and reviewer.
    """
    
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self.status = TaskStatus.PENDING
        self.created_at = time.time()
        
        # Initialize components
        self.orchestrator = self._create_orchestrator()
        self.executor = self._create_executor()
        self.reviewer = self._create_reviewer()
        
        logger.info(f"Initialized {role.value} agent: {agent_id}")
    
    @abstractmethod
    def _create_orchestrator(self) -> BaseOrchestrator:
        """Create the orchestrator component for this agent."""
        pass
    
    @abstractmethod
    def _create_executor(self) -> BaseExecutor:
        """Create the executor component for this agent."""
        pass
    
    @abstractmethod
    def _create_reviewer(self) -> BaseReviewer:
        """Create the reviewer component for this agent."""
        pass
    
    async def process_task(self, task: Task, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Process a task through the complete agent workflow:
        Orchestrator -> Executor -> Reviewer
        """
        if context is None:
            context = {}
        
        start_time = time.time()
        self.status = TaskStatus.IN_PROGRESS
        
        try:
            # Phase 1: Orchestration
            logger.info(f"Agent {self.agent_id} starting orchestration for task {task.task_id}")
            orchestration_result = await self.orchestrator.orchestrate(task, context)
            
            if not orchestration_result.get("execution_plan"):
                return AgentResponse(
                    success=False,
                    error="Orchestration failed to create execution plan",
                    execution_time=time.time() - start_time
                )
            
            # Phase 2: Execution
            logger.info(f"Agent {self.agent_id} starting execution for task {task.task_id}")
            execution_result = await self.executor.execute(
                task, orchestration_result["execution_plan"], context
            )
            
            if not execution_result.get("success", False):
                return AgentResponse(
                    success=False,
                    error=execution_result.get("error", "Execution failed"),
                    execution_time=time.time() - start_time
                )
            
            # Phase 3: Review
            logger.info(f"Agent {self.agent_id} starting review for task {task.task_id}")
            review_result = await self.reviewer.review(task, execution_result, context)
            
            total_time = time.time() - start_time
            self.status = TaskStatus.COMPLETED if review_result.approved else TaskStatus.FAILED
            
            # Compile final response
            response = AgentResponse(
                success=review_result.approved,
                result=execution_result.get("result", {}),
                error=None if review_result.approved else "Quality review failed",
                feedback=review_result.issues + review_result.suggestions,
                confidence=review_result.score,
                execution_time=total_time,
                metadata={
                    "agent_id": self.agent_id,
                    "agent_role": self.role.value,
                    "task_id": task.task_id,
                    "orchestration": orchestration_result,
                    "execution": execution_result,
                    "review": review_result,
                    "workflow_times": {
                        "total": total_time,
                        "execution": execution_result.get("execution_time", 0)
                    }
                },
                suggestions=review_result.suggestions
            )
            
            logger.info(f"Agent {self.agent_id} completed task {task.task_id}: "
                       f"success={response.success}, confidence={response.confidence:.2f}")
            
            return response
            
        except Exception as e:
            self.status = TaskStatus.FAILED
            logger.error(f"Agent {self.agent_id} failed processing task {task.task_id}: {str(e)}")
            
            return AgentResponse(
                success=False,
                error=f"Agent processing failed: {str(e)}",
                execution_time=time.time() - start_time,
                metadata={"agent_id": self.agent_id, "task_id": task.task_id}
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "status": self.status.value,
            "uptime": time.time() - self.created_at,
            "components": {
                "orchestrator": type(self.orchestrator).__name__,
                "executor": type(self.executor).__name__,
                "reviewer": type(self.reviewer).__name__
            }
        }