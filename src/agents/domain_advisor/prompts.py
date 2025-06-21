"""
Prompts for Domain Advisor Agent.
Contains LLM prompts for business requirements analysis.
"""

# System prompts for different components
ORCHESTRATOR_SYSTEM_PROMPT = """
You are a Domain Advisor Orchestrator, responsible for planning how to analyze business requirements and translate them into technical specifications.

Your role is to:
1. Understand the business context and requirements
2. Plan the analysis approach
3. Identify what needs to be extracted (entities, rules, compliance, etc.)
4. Create a structured execution plan

You must be thorough and consider all aspects of business analysis including:
- Domain modeling
- Compliance requirements
- User personas and use cases
- Functional and non-functional requirements
- Risk assessment
"""

EXECUTOR_SYSTEM_PROMPT = """
You are a Domain Advisor Executor, responsible for performing detailed business requirements analysis.

Your role is to:
1. Extract domain entities and relationships
2. Identify business rules and constraints
3. Analyze compliance and regulatory requirements
4. Define user personas and use cases
5. Categorize functional and non-functional requirements

You must provide comprehensive, structured analysis that technical teams can use to build solutions.
"""

REVIEWER_SYSTEM_PROMPT = """
You are a Domain Advisor Reviewer, responsible for validating business requirements analysis for completeness and accuracy.

Your role is to:
1. Verify all business requirements have been addressed
2. Check for missing domain entities or relationships
3. Validate compliance requirements are complete
4. Ensure user personas and use cases are comprehensive
5. Confirm the analysis is actionable for technical teams

You must be thorough and identify any gaps or inconsistencies.
"""

# Orchestrator prompts
ORCHESTRATOR_PLANNING_PROMPT = """
Analyze this business requirements task and create a detailed execution plan:

Task: {title}
Description: {description}
Requirements: {requirements}
Domain: {domain}
Stakeholders: {stakeholders}
Compliance Needs: {compliance_needs}

Create an execution plan that addresses:
1. Domain analysis approach
2. Entity and relationship extraction
3. Business rules identification
4. Compliance requirements analysis
5. User persona development
6. Use case definition
7. Requirements categorization

Respond with JSON:
{{
    "execution_plan": {{
        "analysis_type": "string (compliance_analysis, process_analysis, etc.)",
        "focus_areas": ["list of key areas to analyze"],
        "extraction_steps": [
            {{
                "step": "string",
                "description": "string",
                "outputs": ["list of expected outputs"]
            }}
        ],
        "quality_gates": ["list of validation checkpoints"],
        "estimated_duration": "number (minutes)",
        "required_resources": ["list of needed information or tools"]
    }},
    "success_criteria": ["list of criteria for successful completion"]
}}
"""

# Executor prompts
EXECUTOR_DOMAIN_ANALYSIS_PROMPT = """
Perform comprehensive domain analysis for this business requirement:

Requirements: {requirements}
Domain: {domain}
Context: {context}

Extract and analyze:

1. DOMAIN ENTITIES: Identify all business entities (nouns) and their key attributes
2. RELATIONSHIPS: Define how entities relate to each other
3. BUSINESS RULES: Extract explicit and implicit business rules and constraints
4. PROCESSES: Identify key business processes and workflows

Respond with structured JSON:
{{
    "domain_model": {{
        "entities": [
            {{
                "name": "string",
                "description": "string", 
                "attributes": ["list of key attributes"],
                "constraints": ["list of business constraints"]
            }}
        ],
        "relationships": [
            {{
                "from_entity": "string",
                "to_entity": "string",
                "relationship_type": "string (one-to-one, one-to-many, many-to-many)",
                "description": "string"
            }}
        ],
        "business_rules": [
            {{
                "rule": "string",
                "category": "string (validation, authorization, business_logic)",
                "entities_affected": ["list of entities"],
                "priority": "string (critical, high, medium, low)"
            }}
        ],
        "processes": [
            {{
                "name": "string",
                "description": "string",
                "steps": ["list of process steps"],
                "entities_involved": ["list of entities"],
                "triggers": ["list of triggers that start this process"]
            }}
        ]
    }}
}}
"""

EXECUTOR_REQUIREMENTS_ANALYSIS_PROMPT = """
Analyze and categorize these business requirements:

Requirements: {requirements}
Domain Context: {domain_context}

Categorize into:
1. FUNCTIONAL REQUIREMENTS: What the system must do
2. NON-FUNCTIONAL REQUIREMENTS: How the system must perform
3. COMPLIANCE REQUIREMENTS: Regulatory and legal constraints
4. USER PERSONAS: Different types of users and their needs
5. USE CASES: Key user interactions with the system

Respond with structured JSON:
{{
    "functional_requirements": [
        {{
            "id": "string",
            "requirement": "string",
            "priority": "string (must-have, should-have, could-have)",
            "user_story": "As a ... I want ... so that ...",
            "acceptance_criteria": ["list of criteria"]
        }}
    ],
    "non_functional_requirements": [
        {{
            "category": "string (performance, security, usability, scalability)",
            "requirement": "string",
            "measurable_criteria": "string",
            "priority": "string"
        }}
    ],
    "compliance_requirements": [
        {{
            "standard": "string (GDPR, SOC2, HIPAA, etc.)",
            "requirements": ["specific compliance requirements"],
            "impact": "string (how this affects the system)"
        }}
    ],
    "user_personas": [
        {{
            "name": "string",
            "role": "string",
            "goals": ["list of user goals"],
            "pain_points": ["list of current challenges"],
            "technical_proficiency": "string (low, medium, high)"
        }}
    ],
    "use_cases": [
        {{
            "name": "string",
            "actor": "string (which persona)",
            "description": "string",
            "preconditions": ["list of preconditions"],
            "main_flow": ["list of steps"],
            "alternate_flows": ["list of alternative scenarios"],
            "postconditions": ["list of end states"]
        }}
    ]
}}
"""

EXECUTOR_TECHNICAL_SPECIFICATION_PROMPT = """
Based on the business analysis, create technical specifications:

Domain Model: {domain_model}
Requirements: {requirements_analysis}

Generate technical specifications for:
1. AUTHENTICATION: How users will be authenticated
2. AUTHORIZATION: How permissions will be managed  
3. DATA HANDLING: How data will be stored, processed, and secured
4. INTEGRATION: How the system will integrate with other systems
5. SECURITY: Security measures and considerations

Respond with JSON:
{{
    "technical_specifications": {{
        "authentication": {{
            "method": "string (OAuth2, JWT, SAML, etc.)",
            "requirements": ["specific auth requirements"],
            "considerations": ["security and UX considerations"]
        }},
        "authorization": {{
            "model": "string (RBAC, ABAC, etc.)",
            "roles": [
                {{
                    "role": "string",
                    "permissions": ["list of permissions"],
                    "description": "string"
                }}
            ],
            "policies": ["list of authorization policies"]
        }},
        "data_handling": {{
            "storage_requirements": ["data storage needs"],
            "processing_requirements": ["data processing needs"],
            "security_requirements": ["data security measures"],
            "retention_policies": ["data retention rules"]
        }},
        "integration": {{
            "external_systems": ["list of systems to integrate with"],
            "apis_needed": ["list of APIs or services needed"],
            "data_exchange": ["description of data exchange patterns"]
        }},
        "security": {{
            "measures": ["list of security measures"],
            "compliance_mappings": ["how security addresses compliance"],
            "risk_assessments": ["identified security risks and mitigations"]
        }}
    }}
}}
"""

# Reviewer prompts
REVIEWER_COMPLETENESS_PROMPT = """
Review this domain analysis for completeness and accuracy:

Original Requirements: {original_requirements}
Domain Analysis Result: {analysis_result}

Evaluate:
1. COMPLETENESS: Are all requirements addressed?
2. ACCURACY: Is the analysis correct and logical?
3. CONSISTENCY: Are there any contradictions?
4. ACTIONABILITY: Can technical teams use this effectively?
5. MISSING ELEMENTS: What might be missing?

Respond with JSON:
{{
    "review_result": {{
        "approved": boolean,
        "confidence_score": float (0.0 to 1.0),
        "completeness_score": float (0.0 to 1.0),
        "accuracy_score": float (0.0 to 1.0),
        "issues": [
            {{
                "category": "string (completeness, accuracy, consistency, etc.)",
                "issue": "string",
                "severity": "string (critical, high, medium, low)",
                "suggestion": "string"
            }}
        ],
        "strengths": ["list of strong aspects of the analysis"],
        "missing_elements": ["list of elements that should be added"],
        "improvement_suggestions": ["list of suggestions for improvement"]
    }}
}}
"""

REVIEWER_TECHNICAL_VALIDATION_PROMPT = """
Validate these technical specifications against business requirements:

Business Requirements: {requirements}
Technical Specifications: {technical_specs}

Check:
1. ALIGNMENT: Do specs align with business needs?
2. FEASIBILITY: Are the technical approaches realistic?
3. COMPLETENESS: Are all technical aspects covered?
4. COMPLIANCE: Do specs address compliance requirements?
5. SCALABILITY: Will these specs support future growth?

Respond with JSON:
{{
    "validation_result": {{
        "approved": boolean,
        "alignment_score": float (0.0 to 1.0),
        "feasibility_score": float (0.0 to 1.0),
        "issues": [
            {{
                "area": "string (authentication, authorization, etc.)",
                "issue": "string",
                "impact": "string (high, medium, low)",
                "recommendation": "string"
            }}
        ],
        "compliance_coverage": [
            {{
                "requirement": "string",
                "addressed": boolean,
                "how": "string (description of how it's addressed)"
            }}
        ],
        "improvement_recommendations": ["list of recommendations"]
    }}
}}
"""