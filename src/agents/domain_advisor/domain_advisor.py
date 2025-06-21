"""
Domain Advisor Agent - Translates business requirements into technical specifications.

This agent analyzes business requirements and produces structured technical specifications
that other agents can use to design and implement solutions.
"""

import logging
from typing import Dict, Any, List

from ...core.base_agent import BaseAgent, BaseOrchestrator, BaseExecutor, BaseReviewer
from ...core.types import (
    Task, AgentRole, AgentResponse, ReviewResult, LLMRequest
)
from ...core.llm_client import get_llm_client
from .prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT, EXECUTOR_SYSTEM_PROMPT, REVIEWER_SYSTEM_PROMPT,
    ORCHESTRATOR_PLANNING_PROMPT, EXECUTOR_DOMAIN_ANALYSIS_PROMPT,
    EXECUTOR_REQUIREMENTS_ANALYSIS_PROMPT, EXECUTOR_TECHNICAL_SPECIFICATION_PROMPT,
    REVIEWER_COMPLETENESS_PROMPT, REVIEWER_TECHNICAL_VALIDATION_PROMPT
)


logger = logging.getLogger(__name__)


class DomainAdvisorOrchestrator(BaseOrchestrator):
    """
    Domain Advisor Orchestrator - Plans business requirements analysis approach.
    """
    
    async def _create_execution_plan(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution plan for domain analysis."""
        
        # Extract relevant information from task
        domain = task.metadata.get("domain", "general")
        stakeholders = task.metadata.get("stakeholders", [])
        compliance_needs = task.metadata.get("compliance_needs", [])
        
        # Use LLM to create comprehensive execution plan
        prompt = ORCHESTRATOR_PLANNING_PROMPT.format(
            title=task.title,
            description=task.description,
            requirements=task.requirements,
            domain=domain,
            stakeholders=stakeholders,
            compliance_needs=compliance_needs
        )
        
        request = LLMRequest(
            prompt=prompt,
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            max_tokens=2000,
            temperature=0.3  # Lower temperature for more structured planning
        )
        
        response = await self.llm_client.generate_response(request)
        
        if response.success:
            try:
                plan_data = await self.llm_client.parse_structured_response(response)
                return plan_data.get("execution_plan", {})
            except Exception as e:
                logger.error(f"Failed to parse orchestration response: {e}")
                return self._create_fallback_plan(task)
        else:
            logger.error(f"LLM orchestration failed: {response.error}")
            return self._create_fallback_plan(task)
    
    def _create_fallback_plan(self, task: Task) -> Dict[str, Any]:
        """Create a basic fallback execution plan."""
        return {
            "analysis_type": "general_analysis",
            "focus_areas": ["domain_modeling", "requirements_analysis", "technical_specs"],
            "extraction_steps": [
                {
                    "step": "domain_analysis",
                    "description": "Extract entities, relationships, and business rules",
                    "outputs": ["domain_model"]
                },
                {
                    "step": "requirements_analysis", 
                    "description": "Categorize and analyze requirements",
                    "outputs": ["functional_requirements", "non_functional_requirements"]
                },
                {
                    "step": "technical_specification",
                    "description": "Create technical specifications",
                    "outputs": ["technical_specifications"]
                }
            ],
            "quality_gates": ["completeness_check", "consistency_validation"],
            "estimated_duration": 15,
            "required_resources": ["business_requirements", "domain_context"]
        }


class DomainAdvisorExecutor(BaseExecutor):
    """
    Domain Advisor Executor - Performs the actual business requirements analysis.
    """
    
    async def _execute_task(self, task: Task, execution_plan: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute domain analysis according to the plan."""
        
        result = {
            "analysis_type": execution_plan.get("analysis_type", "general_analysis"),
            "domain_model": {},
            "functional_requirements": [],
            "non_functional_requirements": [],
            "compliance_requirements": [],
            "user_personas": [],
            "use_cases": [],
            "technical_specifications": {}
        }
        
        try:
            # Step 1: Domain Analysis
            logger.info(f"Performing domain analysis for task {task.task_id}")
            domain_model = await self._perform_domain_analysis(task, context)
            result["domain_model"] = domain_model
            
            # Step 2: Requirements Analysis
            logger.info(f"Performing requirements analysis for task {task.task_id}")
            requirements_analysis = await self._perform_requirements_analysis(task, domain_model)
            result.update(requirements_analysis)
            
            # Step 3: Technical Specifications
            logger.info(f"Creating technical specifications for task {task.task_id}")
            technical_specs = await self._create_technical_specifications(domain_model, requirements_analysis)
            result["technical_specifications"] = technical_specs
            
            logger.info(f"Domain analysis completed for task {task.task_id}")
            return result
            
        except Exception as e:
            logger.error(f"Domain analysis execution failed: {str(e)}")
            return {"error": f"Execution failed: {str(e)}"}
    
    async def _perform_domain_analysis(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform domain modeling and entity extraction."""
        
        domain = task.metadata.get("domain", "general")
        
        prompt = EXECUTOR_DOMAIN_ANALYSIS_PROMPT.format(
            requirements=task.requirements,
            domain=domain,
            context=context
        )
        
        request = LLMRequest(
            prompt=prompt,
            system_prompt=EXECUTOR_SYSTEM_PROMPT,
            max_tokens=3000,
            temperature=0.4
        )
        
        response = await self.llm_client.generate_response(request)
        
        if response.success:
            try:
                analysis = await self.llm_client.parse_structured_response(response)
                return analysis.get("domain_model", {})
            except Exception as e:
                logger.error(f"Failed to parse domain analysis: {e}")
                return self._create_fallback_domain_model(task)
        else:
            logger.error(f"Domain analysis LLM call failed: {response.error}")
            return self._create_fallback_domain_model(task)
    
    async def _perform_requirements_analysis(self, task: Task, domain_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and categorize business requirements."""
        
        prompt = EXECUTOR_REQUIREMENTS_ANALYSIS_PROMPT.format(
            requirements=task.requirements,
            domain_context=domain_context
        )
        
        request = LLMRequest(
            prompt=prompt,
            system_prompt=EXECUTOR_SYSTEM_PROMPT,
            max_tokens=3000,
            temperature=0.4
        )
        
        response = await self.llm_client.generate_response(request)
        
        if response.success:
            try:
                analysis = await self.llm_client.parse_structured_response(response)
                return {
                    "functional_requirements": analysis.get("functional_requirements", []),
                    "non_functional_requirements": analysis.get("non_functional_requirements", []),
                    "compliance_requirements": analysis.get("compliance_requirements", []),
                    "user_personas": analysis.get("user_personas", []),
                    "use_cases": analysis.get("use_cases", [])
                }
            except Exception as e:
                logger.error(f"Failed to parse requirements analysis: {e}")
                return self._create_fallback_requirements()
        else:
            logger.error(f"Requirements analysis LLM call failed: {response.error}")
            return self._create_fallback_requirements()
    
    async def _create_technical_specifications(self, domain_model: Dict[str, Any], 
                                             requirements_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create technical specifications based on analysis."""
        
        prompt = EXECUTOR_TECHNICAL_SPECIFICATION_PROMPT.format(
            domain_model=domain_model,
            requirements_analysis=requirements_analysis
        )
        
        request = LLMRequest(
            prompt=prompt,
            system_prompt=EXECUTOR_SYSTEM_PROMPT,
            max_tokens=2500,
            temperature=0.3
        )
        
        response = await self.llm_client.generate_response(request)
        
        if response.success:
            try:
                specs = await self.llm_client.parse_structured_response(response)
                return specs.get("technical_specifications", {})
            except Exception as e:
                logger.error(f"Failed to parse technical specifications: {e}")
                return self._create_fallback_technical_specs()
        else:
            logger.error(f"Technical specifications LLM call failed: {response.error}")
            return self._create_fallback_technical_specs()
    
    def _create_fallback_domain_model(self, task: Task) -> Dict[str, Any]:
        """Create basic fallback domain model."""
        return {
            "entities": [{"name": "User", "description": "System user", "attributes": ["id", "name"], "constraints": []}],
            "relationships": [],
            "business_rules": [{"rule": "Users must be authenticated", "category": "security", "entities_affected": ["User"], "priority": "critical"}],
            "processes": []
        }
    
    def _create_fallback_requirements(self) -> Dict[str, Any]:
        """Create basic fallback requirements."""
        return {
            "functional_requirements": [],
            "non_functional_requirements": [],
            "compliance_requirements": [],
            "user_personas": [],
            "use_cases": []
        }
    
    def _create_fallback_technical_specs(self) -> Dict[str, Any]:
        """Create basic fallback technical specifications."""
        return {
            "authentication": {"method": "JWT", "requirements": ["secure token"], "considerations": ["token expiry"]},
            "authorization": {"model": "RBAC", "roles": [], "policies": []},
            "data_handling": {"storage_requirements": [], "processing_requirements": [], "security_requirements": [], "retention_policies": []},
            "integration": {"external_systems": [], "apis_needed": [], "data_exchange": []},
            "security": {"measures": [], "compliance_mappings": [], "risk_assessments": []}
        }


class DomainAdvisorReviewer(BaseReviewer):
    """
    Domain Advisor Reviewer - Validates the quality and completeness of domain analysis.
    """
    
    async def _review_result(self, task: Task, execution_result: Dict[str, Any], 
                           context: Dict[str, Any]) -> ReviewResult:
        """Review the domain analysis result for quality and completeness."""
        
        analysis_result = execution_result.get("result", {})
        
        try:
            # Perform completeness review
            completeness_review = await self._review_completeness(task, analysis_result)
            
            # Perform technical validation
            technical_review = await self._review_technical_specifications(task, analysis_result)
            
            # Combine reviews
            overall_score = (completeness_review["confidence_score"] + technical_review["alignment_score"]) / 2
            all_issues = completeness_review.get("issues", []) + technical_review.get("issues", [])
            
            # Determine approval
            critical_issues = [issue for issue in all_issues if issue.get("severity") == "critical"]
            approved = len(critical_issues) == 0 and overall_score >= 0.7
            
            return ReviewResult(
                approved=approved,
                score=overall_score,
                issues=[issue.get("issue", str(issue)) for issue in all_issues],
                suggestions=completeness_review.get("improvement_suggestions", []) + 
                           technical_review.get("improvement_recommendations", []),
                strengths=completeness_review.get("strengths", []),
                metadata={
                    "completeness_review": completeness_review,
                    "technical_review": technical_review,
                    "critical_issues_count": len(critical_issues)
                }
            )
            
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
    
    async def _review_completeness(self, task: Task, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Review analysis for completeness."""
        
        prompt = REVIEWER_COMPLETENESS_PROMPT.format(
            original_requirements=task.requirements,
            analysis_result=analysis_result
        )
        
        request = LLMRequest(
            prompt=prompt,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            max_tokens=2000,
            temperature=0.2  # Low temperature for consistent evaluation
        )
        
        response = await self.llm_client.generate_response(request)
        
        if response.success:
            try:
                review = await self.llm_client.parse_structured_response(response)
                return review.get("review_result", {})
            except Exception as e:
                logger.error(f"Failed to parse completeness review: {e}")
                return self._create_fallback_review()
        else:
            logger.error(f"Completeness review LLM call failed: {response.error}")
            return self._create_fallback_review()
    
    async def _review_technical_specifications(self, task: Task, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Review technical specifications for validity."""
        
        technical_specs = analysis_result.get("technical_specifications", {})
        
        prompt = REVIEWER_TECHNICAL_VALIDATION_PROMPT.format(
            requirements=task.requirements,
            technical_specs=technical_specs
        )
        
        request = LLMRequest(
            prompt=prompt,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            max_tokens=2000,
            temperature=0.2
        )
        
        response = await self.llm_client.generate_response(request)
        
        if response.success:
            try:
                review = await self.llm_client.parse_structured_response(response)
                return review.get("validation_result", {})
            except Exception as e:
                logger.error(f"Failed to parse technical validation: {e}")
                return self._create_fallback_technical_review()
        else:
            logger.error(f"Technical validation LLM call failed: {response.error}")
            return self._create_fallback_technical_review()
    
    def _create_fallback_review(self) -> Dict[str, Any]:
        """Create fallback completeness review."""
        return {
            "approved": True,
            "confidence_score": 0.5,
            "completeness_score": 0.5,
            "accuracy_score": 0.5,
            "issues": [],
            "strengths": ["Analysis completed"],
            "missing_elements": [],
            "improvement_suggestions": []
        }
    
    def _create_fallback_technical_review(self) -> Dict[str, Any]:
        """Create fallback technical review."""
        return {
            "approved": True,
            "alignment_score": 0.5,
            "feasibility_score": 0.5,
            "issues": [],
            "compliance_coverage": [],
            "improvement_recommendations": []
        }


class DomainAdvisorAgent(BaseAgent):
    """
    Domain Advisor Agent - Main agent class that coordinates business requirements analysis.
    
    This agent translates business requirements into structured technical specifications
    that can be used by other agents in the system.
    """
    
    def __init__(self, agent_id: str = "domain_advisor_001"):
        """Initialize the Domain Advisor Agent."""
        super().__init__(agent_id, AgentRole.DOMAIN_ADVISOR)
        logger.info(f"Domain Advisor Agent initialized: {agent_id}")
    
    def _create_orchestrator(self) -> BaseOrchestrator:
        """Create the orchestrator component."""
        return DomainAdvisorOrchestrator(self.agent_id)
    
    def _create_executor(self) -> BaseExecutor:
        """Create the executor component."""
        return DomainAdvisorExecutor(self.agent_id)
    
    def _create_reviewer(self) -> BaseReviewer:
        """Create the reviewer component."""
        return DomainAdvisorReviewer(self.agent_id)
    
    async def analyze_business_requirements(self, requirements: List[str], 
                                          domain: str = "general",
                                          stakeholders: List[str] = None,
                                          compliance_needs: List[str] = None) -> AgentResponse:
        """
        Convenience method for analyzing business requirements.
        
        Args:
            requirements: List of business requirements
            domain: Business domain (e.g., 'e-commerce', 'healthcare')
            stakeholders: List of stakeholder types
            compliance_needs: List of compliance requirements
            
        Returns:
            AgentResponse with structured analysis results
        """
        if stakeholders is None:
            stakeholders = []
        if compliance_needs is None:
            compliance_needs = []
        
        task = Task(
            title="Business Requirements Analysis",
            description=f"Analyze business requirements for {domain} domain",
            requirements=requirements,
            required_agent_role=AgentRole.DOMAIN_ADVISOR,
            metadata={
                "domain": domain,
                "stakeholders": stakeholders,
                "compliance_needs": compliance_needs
            }
        )
        
        return await self.process_task(task)