#!/usr/bin/env python3
"""
Test script for the retry mechanism in Phase 1 implementation.
Uses intentionally vague requirements to trigger review failures and retries.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), ''))

from src.core.types import Task, TaskPriority, AgentRole
from src.agents.domain_advisor.domain_advisor import DomainAdvisorAgent
from src.core.llm_client import initialize_llm_client


# Initialize LLM client with Ollama configuration
llm_config = {
    "default_provider": "ollama",
    "ollama_base_url": "http://localhost:11434",
    "timeout": 300,  # 5 minutes timeout for qwen3:14b
    "max_retries": 1
}
initialize_llm_client(llm_config)


# Configure logging to see retry behavior
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'test_retry_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)


async def test_retry_with_vague_requirements():
    """Test the retry mechanism with intentionally vague requirements."""
    
    print("\n" + "="*80)
    print("TESTING RETRY MECHANISM WITH VAGUE REQUIREMENTS")
    print("="*80 + "\n")
    
    # Create a task with intentionally vague requirements
    vague_task = Task(
        title="Build something with AI",
        description="We need an AI solution for our business",
        requirements=[
            "Build something with AI",
            "Make it user-friendly",
            "Should be modern and scalable"
        ],
        priority=TaskPriority.HIGH,
        required_agent_role=AgentRole.DOMAIN_ADVISOR,
        metadata={
            "domain": "general",
            "test_type": "vague_requirements_retry_test"
        }
    )
    
    print(f"Task ID: {vague_task.task_id}")
    print(f"Task Title: {vague_task.title}")
    print(f"Requirements: {vague_task.requirements}")
    print("\n" + "-"*80 + "\n")
    
    # Create the Domain Advisor agent
    domain_advisor = DomainAdvisorAgent(
        agent_id="test_domain_advisor_001"
    )
    
    print("Processing task with Domain Advisor...")
    print("Expected behavior: First attempt should fail review due to vague requirements")
    print("Then retry with feedback should improve the analysis")
    print("\n" + "-"*80 + "\n")
    
    # Process the task
    start_time = datetime.now()
    response = await domain_advisor.process_task(vague_task)
    end_time = datetime.now()
    
    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")
    
    print(f"Success: {response.success}")
    print(f"Confidence Score: {response.confidence:.2f}")
    print(f"Total Execution Time: {(end_time - start_time).total_seconds():.2f} seconds")
    print(f"Total Attempts: {response.metadata.get('total_attempts', 1)}")
    
    if response.error:
        print(f"\nError: {response.error}")
    
    if response.feedback:
        print(f"\nFeedback ({len(response.feedback)} items):")
        for i, feedback in enumerate(response.feedback, 1):
            print(f"  {i}. {feedback}")
    
    if response.suggestions:
        print(f"\nSuggestions ({len(response.suggestions)} items):")
        for i, suggestion in enumerate(response.suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    # Display retry information if available
    if 'review_results' in response.metadata:
        print(f"\n\nReview Results Across Attempts:")
        for i, review in enumerate(response.metadata['review_results'], 1):
            print(f"\nAttempt {i}:")
            print(f"  - Approved: {review['approved']}")
            print(f"  - Score: {review['score']:.2f}")
            print(f"  - Issues: {len(review['issues'])}")
            if review['issues']:
                for issue in review['issues'][:3]:  # Show first 3 issues
                    print(f"    • {issue}")
    
    # Display improvement context if retries occurred
    if response.metadata.get('improvement_context'):
        ic = response.metadata['improvement_context']
        print(f"\n\nImprovement Context:")
        print(f"  - Total retry attempts: {ic['attempt_number']}")
        print(f"  - Quality score progression: {[f'{score:.2f}' for score in ic['quality_scores']]}")
        print(f"  - Improvement history:")
        for history in ic['improvement_history']:
            print(f"    • {history}")
    
    # Display final result summary
    if response.success and response.result:
        print(f"\n\nFinal Analysis Summary:")
        result = response.result
        
        if 'domain_model' in result and result['domain_model']:
            print(f"  - Domain entities identified: {len(result['domain_model'].get('entities', []))}")
        
        if 'functional_requirements' in result:
            print(f"  - Functional requirements: {len(result['functional_requirements'])}")
            
        if 'non_functional_requirements' in result:
            print(f"  - Non-functional requirements: {len(result['non_functional_requirements'])}")
            
        if 'user_personas' in result:
            print(f"  - User personas defined: {len(result['user_personas'])}")
            
        if 'use_cases' in result:
            print(f"  - Use cases identified: {len(result['use_cases'])}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")
    
    return response


async def test_clear_requirements_no_retry():
    """Test with clear requirements that should pass on first attempt."""
    
    print("\n" + "="*80)
    print("TESTING WITH CLEAR REQUIREMENTS (CONTROL TEST)")
    print("="*80 + "\n")
    
    # Create a task with clear, specific requirements
    clear_task = Task(
        title="E-commerce Platform Development",
        description="Develop a modern e-commerce platform for selling electronics",
        requirements=[
            "User registration and authentication system with email verification",
            "Product catalog with categories, search, and filtering",
            "Shopping cart and checkout process with payment integration",
            "Order management and tracking for customers",
            "Admin panel for inventory and order management",
            "RESTful API for mobile app integration",
            "Support for 10,000 concurrent users",
            "PCI compliance for payment processing"
        ],
        priority=TaskPriority.HIGH,
        required_agent_role=AgentRole.DOMAIN_ADVISOR,
        metadata={
            "domain": "e-commerce",
            "stakeholders": ["customers", "administrators", "vendors"],
            "compliance_needs": ["PCI-DSS", "GDPR"],
            "test_type": "clear_requirements_control_test"
        }
    )
    
    print(f"Task ID: {clear_task.task_id}")
    print(f"Task Title: {clear_task.title}")
    print(f"Requirements: {len(clear_task.requirements)} specific requirements")
    print("\n" + "-"*80 + "\n")
    
    # Create the Domain Advisor agent
    domain_advisor = DomainAdvisorAgent(
        agent_id="test_domain_advisor_002"
    )
    
    print("Processing task with Domain Advisor...")
    print("Expected behavior: Should pass review on first attempt")
    print("\n" + "-"*80 + "\n")
    
    # Process the task
    start_time = datetime.now()
    response = await domain_advisor.process_task(clear_task)
    end_time = datetime.now()
    
    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")
    
    print(f"Success: {response.success}")
    print(f"Confidence Score: {response.confidence:.2f}")
    print(f"Total Execution Time: {(end_time - start_time).total_seconds():.2f} seconds")
    print(f"Total Attempts: {response.metadata.get('total_attempts', 1)}")
    
    print("\n" + "="*80)
    print("CONTROL TEST COMPLETED")
    print("="*80 + "\n")
    
    return response


async def main():
    """Run both tests to demonstrate retry mechanism."""
    
    print("\n" + "="*80)
    print("PHASE 1 RETRY MECHANISM TEST SUITE")
    print("Testing autonomous retry with reviewer feedback")
    print("="*80 + "\n")
    
    # Test 1: Vague requirements (should trigger retry)
    print("Test 1: Vague Requirements (Expected to trigger retry)")
    vague_response = await test_retry_with_vague_requirements()
    
    # Brief pause between tests
    await asyncio.sleep(2)
    
    # Test 2: Clear requirements (should not need retry)
    print("\n\nTest 2: Clear Requirements (Expected to pass without retry)")
    clear_response = await test_clear_requirements_no_retry()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80 + "\n")
    
    print("Test 1 (Vague Requirements):")
    print(f"  - Success: {vague_response.success}")
    print(f"  - Attempts: {vague_response.metadata.get('total_attempts', 1)}")
    print(f"  - Final Score: {vague_response.confidence:.2f}")
    
    print("\nTest 2 (Clear Requirements):")
    print(f"  - Success: {clear_response.success}")
    print(f"  - Attempts: {clear_response.metadata.get('total_attempts', 1)}")
    print(f"  - Final Score: {clear_response.confidence:.2f}")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())