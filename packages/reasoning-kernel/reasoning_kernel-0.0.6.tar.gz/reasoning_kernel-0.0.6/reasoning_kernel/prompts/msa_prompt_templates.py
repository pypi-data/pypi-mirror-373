"""
MSA Prompt Templates for Enhanced Natural Language Reasoning

This module provides standardized prompt templates based on MSA research patterns
for improving reasoning quality across all MSA stages in the unified architecture.
These templates are optimized for GPT-5 with high thinking effort and Semantic Kernel integration.

Templates maintain consistency with MSA research patterns:
- START_SCRATCHPAD/END_SCRATCHPAD for reasoning
- START_CONCEPT_TRACE/END_CONCEPT_TRACE for dependency mapping
- Natural language causal structure descriptions
- Background knowledge synthesis
- Confidence assessment and validation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class PromptType(Enum):
    """Types of MSA prompt templates"""

    PARSE_CAUSAL_STRUCTURE = "parse_causal_structure"
    CONCEPT_TRACE_GENERATION = "concept_trace_generation"
    BACKGROUND_KNOWLEDGE = "background_knowledge"
    ENTITY_EXTRACTION = "entity_extraction"
    GRAPH_CONSTRUCTION = "graph_construction"
    MODEL_SYNTHESIS = "model_synthesis"
    PROBABILISTIC_INFERENCE = "probabilistic_inference"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"
    FINAL_SYNTHESIS = "final_synthesis"


@dataclass
class PromptTemplate:
    """Template for MSA reasoning prompts"""

    name: str
    prompt_type: PromptType
    template: str
    variables: List[str]
    thinking_effort: str = "high"
    max_tokens: int = 2048
    temperature: float = 0.7
    description: str = ""


class MSAPromptTemplates:
    """Collection of standardized MSA prompt templates"""

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize all MSA prompt templates"""
        templates = {}

        # Parse Stage Templates
        templates["parse_causal_structure"] = self._create_parse_causal_structure_template()
        templates["concept_trace_generation"] = self._create_concept_trace_template()
        templates["entity_extraction"] = self._create_entity_extraction_template()

        # Knowledge Stage Templates
        templates["background_knowledge"] = self._create_background_knowledge_template()
        templates["knowledge_synthesis"] = self._create_knowledge_synthesis_template()

        # Graph Stage Templates
        templates["graph_construction"] = self._create_graph_construction_template()
        templates["relationship_mapping"] = self._create_relationship_mapping_template()

        # Synthesis Stage Templates
        templates["model_synthesis"] = self._create_model_synthesis_template()
        templates["causal_model_generation"] = self._create_causal_model_template()

        # Inference Stage Templates
        templates["probabilistic_inference"] = self._create_probabilistic_inference_template()
        templates["webppl_generation"] = self._create_webppl_generation_template()

        # Cross-stage Templates
        templates["confidence_assessment"] = self._create_confidence_assessment_template()
        templates["final_synthesis"] = self._create_final_synthesis_template()

        return templates

    def _create_graph_construction_template(self) -> PromptTemplate:
        """Template for knowledge graph construction"""
        template = """
Construct a comprehensive knowledge graph from the analyzed scenario information.

Scenario: {scenario}
Entities: {entities}
Concepts: {concepts}
Relationships: {relationships}
Background Knowledge: {background_knowledge}

Create a knowledge graph that captures:

1. **Nodes (Entities and Concepts)**:
   - Primary entities with their properties
   - Abstract concepts and their characteristics
   - Measurable variables and their ranges
   - Categories and classifications

2. **Edges (Relationships)**:
   - Causal relationships (A causes B)
   - Dependency relationships (A depends on B)
   - Similarity relationships (A is similar to B)
   - Part-of relationships (A is part of B)
   - Temporal relationships (A occurs before B)

3. **Graph Properties**:
   - Relationship strengths (weak, moderate, strong)
   - Relationship types (positive, negative, neutral)
   - Confidence levels for each relationship
   - Temporal aspects (static vs. dynamic)

Format your response as:
<START_KNOWLEDGE_GRAPH>
NODES:
- entity/concept: type, properties, confidence
...

EDGES:
- source -> target: relationship_type, strength, confidence, description
...

CLUSTERS:
- cluster_name: [node1, node2, ...], description
...
<END_KNOWLEDGE_GRAPH>

Previous Analysis: {previous_analysis}
"""

        return PromptTemplate(
            name="graph_construction",
            prompt_type=PromptType.GRAPH_CONSTRUCTION,
            template=template,
            variables=[
                "scenario",
                "entities",
                "concepts",
                "relationships",
                "background_knowledge",
                "previous_analysis",
            ],
            thinking_effort="high",
            max_tokens=1024,
            temperature=0.6,
            description="Constructs comprehensive knowledge graphs from scenario analysis",
        )

    def _create_relationship_mapping_template(self) -> PromptTemplate:
        """Template for relationship mapping and analysis"""
        template = """
Analyze and map the relationships between entities and concepts in this scenario.

Scenario: {scenario}
Entities: {entities}
Concepts: {concepts}
Causal Structure: {causal_structure}

Identify and analyze relationships focusing on:

1. **Causal Relationships**:
   - Direct causation (A directly causes B)
   - Indirect causation (A causes B through C)
   - Bidirectional causation (A and B influence each other)
   - Conditional causation (A causes B only if C)

2. **Dependency Relationships**:
   - Functional dependencies (B is a function of A)
   - Statistical dependencies (A and B are correlated)
   - Logical dependencies (B requires A to be true)
   - Temporal dependencies (B can only occur after A)

3. **Structural Relationships**:
   - Hierarchical (A is above/below B)
   - Compositional (A is made up of B, C, D)
   - Categorical (A and B are both types of C)
   - Spatial (A is located near/in B)

4. **Relationship Properties**:
   - Strength: How strong is the relationship?
   - Direction: Is it unidirectional or bidirectional?
   - Stability: Does it change over time?
   - Conditionality: Does it depend on other factors?

Provide detailed analysis with confidence assessments for each relationship.

Context: {context}
Domain Knowledge: {domain_knowledge}
"""

        return PromptTemplate(
            name="relationship_mapping",
            prompt_type=PromptType.GRAPH_CONSTRUCTION,
            template=template,
            variables=["scenario", "entities", "concepts", "causal_structure", "context", "domain_knowledge"],
            thinking_effort="high",
            max_tokens=1024,
            temperature=0.6,
            description="Maps and analyzes relationships between entities and concepts",
        )

    def _create_model_synthesis_template(self) -> PromptTemplate:
        """Template for model synthesis and generation"""
        template = """
Synthesize a comprehensive model from the analyzed scenario components.

Scenario: {scenario}
Causal Structure: {causal_structure}
Knowledge Graph: {knowledge_graph}
Background Knowledge: {background_knowledge}
Concept Dependencies: {concept_dependencies}

Create a unified model that:

1. **Integrates All Components**:
   - Combines causal structure with knowledge graph
   - Incorporates background knowledge appropriately
   - Respects concept dependencies and relationships
   - Maintains logical consistency across components

2. **Defines Model Structure**:
   - Core variables and their types (continuous, categorical, binary)
   - Parameter distributions and priors
   - Functional relationships between variables
   - Conditional dependencies and constraints

3. **Specifies Model Behavior**:
   - How inputs map to outputs
   - Sources of uncertainty and randomness
   - Feedback loops and dynamic behavior
   - Boundary conditions and constraints

4. **Provides Model Validation**:
   - Internal consistency checks
   - Alignment with domain knowledge
   - Testable predictions and implications
   - Sensitivity to key assumptions

<START_MODEL_SYNTHESIS>
MODEL_STRUCTURE:
- Variables: [list with types and descriptions]
- Parameters: [list with priors and constraints]
- Relationships: [functional forms and dependencies]

MODEL_BEHAVIOR:
- Input-Output Mapping: [description]
- Uncertainty Sources: [list and characterization]
- Dynamic Aspects: [temporal behavior]

MODEL_VALIDATION:
- Consistency Checks: [internal validation]
- Domain Alignment: [external validation]
- Predictions: [testable implications]
<END_MODEL_SYNTHESIS>

Requirements: {requirements}
Constraints: {constraints}
"""

        return PromptTemplate(
            name="model_synthesis",
            prompt_type=PromptType.MODEL_SYNTHESIS,
            template=template,
            variables=[
                "scenario",
                "causal_structure",
                "knowledge_graph",
                "background_knowledge",
                "concept_dependencies",
                "requirements",
                "constraints",
            ],
            thinking_effort="high",
            max_tokens=1536,
            temperature=0.6,
            description="Synthesizes comprehensive models from analyzed components",
        )

    def _create_causal_model_template(self) -> PromptTemplate:
        """Template for causal model generation"""
        template = """
Generate a detailed causal model based on the scenario analysis.

Scenario: {scenario}
Causal Structure: {causal_structure}
Entities: {entities}
Causal Factors: {causal_factors}
Relationships: {relationships}

Develop a causal model that specifies:

1. **Causal Variables**:
   - Exogenous variables (external causes)
   - Endogenous variables (internal effects)
   - Mediating variables (intermediate causes)
   - Moderating variables (conditional influences)

2. **Causal Mechanisms**:
   - Direct causal pathways
   - Indirect causal chains
   - Confounding relationships
   - Interaction effects

3. **Causal Assumptions**:
   - Independence assumptions
   - Exclusion restrictions
   - Temporal ordering
   - Functional form assumptions

4. **Model Identification**:
   - Identifiable causal effects
   - Sources of causal identification
   - Potential confounders
   - Robustness considerations

Focus on creating a model that enables causal inference and prediction.

<START_CAUSAL_MODEL>
VARIABLES:
- Exogenous: [list with descriptions]
- Endogenous: [list with descriptions]
- Mediators: [list with descriptions]
- Moderators: [list with descriptions]

MECHANISMS:
- Direct Effects: [A -> B relationships]
- Indirect Effects: [A -> C -> B chains]
- Interactions: [A*B -> C effects]

ASSUMPTIONS:
- Independence: [what is assumed independent]
- Exclusions: [what is excluded from affecting what]
- Temporal: [ordering assumptions]
- Functional: [form assumptions]
<END_CAUSAL_MODEL>

Domain: {domain}
Purpose: {purpose}
"""

        return PromptTemplate(
            name="causal_model_generation",
            prompt_type=PromptType.MODEL_SYNTHESIS,
            template=template,
            variables=[
                "scenario",
                "causal_structure",
                "entities",
                "causal_factors",
                "relationships",
                "domain",
                "purpose",
            ],
            thinking_effort="high",
            max_tokens=1024,
            temperature=0.5,
            description="Generates detailed causal models for inference and prediction",
        )

    def _create_probabilistic_inference_template(self) -> PromptTemplate:
        """Template for probabilistic inference and reasoning"""
        template = """
Perform probabilistic inference based on the synthesized model and available evidence.

Scenario: {scenario}
Model: {model}
Evidence: {evidence}
Queries: {queries}

Conduct probabilistic reasoning that:

1. **Incorporates Evidence**:
   - Observed facts and conditions
   - Measurement uncertainties
   - Prior knowledge and beliefs
   - Contextual constraints

2. **Performs Inference**:
   - Posterior probability calculations
   - Predictive distributions
   - Causal effect estimation
   - Uncertainty quantification

3. **Addresses Queries**:
   - Direct probability questions
   - Conditional probability questions
   - Causal effect questions
   - Prediction questions

4. **Assesses Uncertainty**:
   - Parameter uncertainty
   - Model uncertainty
   - Prediction uncertainty
   - Sensitivity to assumptions

<START_PROBABILISTIC_INFERENCE>
EVIDENCE_INTEGRATION:
- Observations: [what is observed]
- Uncertainties: [measurement and other uncertainties]
- Priors: [prior beliefs and knowledge]

INFERENCE_RESULTS:
- Posteriors: [updated beliefs given evidence]
- Predictions: [forecasts and projections]
- Causal_Effects: [estimated causal impacts]

UNCERTAINTY_ASSESSMENT:
- Parameter_Uncertainty: [uncertainty in model parameters]
- Model_Uncertainty: [uncertainty about model structure]
- Prediction_Uncertainty: [uncertainty in predictions]

QUERY_ANSWERS:
{query_template}
<END_PROBABILISTIC_INFERENCE>

Method: {method}
Computational_Approach: {computational_approach}
"""

        return PromptTemplate(
            name="probabilistic_inference",
            prompt_type=PromptType.PROBABILISTIC_INFERENCE,
            template=template,
            variables=[
                "scenario",
                "model",
                "evidence",
                "queries",
                "query_template",
                "method",
                "computational_approach",
            ],
            thinking_effort="high",
            max_tokens=1536,
            temperature=0.4,
            description="Performs probabilistic inference and uncertainty quantification",
        )

    def _create_webppl_generation_template(self) -> PromptTemplate:
        """Template for WebPPL code generation"""
        template = """
Generate WebPPL code to implement the probabilistic model for this scenario.

Scenario: {scenario}
Model Structure: {model_structure}
Variables: {variables}
Relationships: {relationships}
Conditions: {conditions}
Queries: {queries}

Generate WebPPL code that:

1. **Implements the Model**:
   - Define all variables with appropriate distributions
   - Implement causal relationships and dependencies
   - Include background knowledge as priors
   - Handle uncertainty and randomness appropriately

2. **Incorporates Conditions**:
   - Translate scenario conditions into WebPPL condition statements
   - Ensure conditions are meaningful and general
   - Avoid hard constraints on continuous variables
   - Use appropriate conditioning syntax

3. **Addresses Queries**:
   - Implement query functions for all questions
   - Return appropriate data types and formats
   - Handle both point estimates and distributions
   - Include uncertainty quantification

4. **Follows Best Practices**:
   - Define functions in proper order (dependencies first)
   - Use memoization (mem) for stable random variables
   - Implement helper functions for complex operations
   - Include comments explaining the model structure

Remember WebPPL constraints:
- No assignment expressions (+=, -=, etc.)
- No looping constructs (for, while, do)
- No switch expressions
- Use "!" for negation, not "not"
- Define functions before calling them

<START_WEBPPL_CODE>
// Model for: {scenario_title}

// Helper functions
{helper_functions}

// Main model
var model = function() {{
    // Background knowledge and priors
    {background_priors}

    // Core variables and relationships
    {core_variables}

    // Conditions from scenario
    {condition_statements}

    // Return query results
    return {{
        {query_returns}
    }};
}};

// Run inference
var posterior = Infer({{
    model: model,
    method: "{inference_method}",
    samples: {num_samples}
}});

// Display results
{result_display}
<END_WEBPPL_CODE>

Domain_Knowledge: {domain_knowledge}
Inference_Method: {inference_method}
"""

        return PromptTemplate(
            name="webppl_generation",
            prompt_type=PromptType.PROBABILISTIC_INFERENCE,
            template=template,
            variables=[
                "scenario",
                "model_structure",
                "variables",
                "relationships",
                "conditions",
                "queries",
                "scenario_title",
                "helper_functions",
                "background_priors",
                "core_variables",
                "condition_statements",
                "query_returns",
                "inference_method",
                "num_samples",
                "result_display",
                "domain_knowledge",
            ],
            thinking_effort="high",
            max_tokens=2048,
            temperature=0.3,
            description="Generates WebPPL code for probabilistic model implementation",
        )

    def _create_knowledge_synthesis_template(self) -> PromptTemplate:
        """Template for knowledge synthesis and integration"""
        template = """
Synthesize and integrate knowledge from multiple sources for enhanced reasoning.

Scenario: {scenario}
Retrieved Knowledge: {retrieved_knowledge}
Background Knowledge: {background_knowledge}
Domain Context: {domain_context}
Previous Analysis: {previous_analysis}

Integrate knowledge by:

1. **Consolidating Information**:
   - Merge complementary information from different sources
   - Resolve conflicts or inconsistencies
   - Identify gaps in knowledge coverage
   - Prioritize most relevant and reliable information

2. **Enhancing Understanding**:
   - Connect scenario-specific facts to general principles
   - Identify patterns and analogies from similar situations
   - Extract implicit knowledge and assumptions
   - Clarify ambiguous or incomplete information

3. **Supporting Reasoning**:
   - Provide context for causal relationships
   - Offer probabilistic information and base rates
   - Suggest relevant factors that might be overlooked
   - Highlight potential confounders or alternative explanations

4. **Organizing Knowledge**:
   - Structure information hierarchically
   - Group related concepts and facts
   - Establish knowledge dependencies
   - Create knowledge maps and connections

<START_KNOWLEDGE_SYNTHESIS>
CONSOLIDATED_KNOWLEDGE:
- Core Facts: [verified and consolidated facts]
- Principles: [general principles and rules]
- Patterns: [identified patterns and regularities]
- Uncertainties: [areas of uncertainty or conflict]

ENHANCED_UNDERSTANDING:
- Context: [situational and domain context]
- Analogies: [relevant analogies and comparisons]
- Implications: [logical implications and consequences]
- Assumptions: [underlying assumptions and presuppositions]

REASONING_SUPPORT:
- Causal_Context: [background for causal relationships]
- Base_Rates: [relevant frequencies and probabilities]
- Hidden_Factors: [potentially overlooked factors]
- Alternative_Explanations: [competing hypotheses]

KNOWLEDGE_ORGANIZATION:
- Hierarchy: [structured organization of knowledge]
- Clusters: [grouped related concepts]
- Dependencies: [knowledge dependencies and prerequisites]
- Connections: [cross-references and relationships]
<END_KNOWLEDGE_SYNTHESIS>

Quality_Criteria: {quality_criteria}
Confidence_Assessment: {confidence_assessment}
"""

        return PromptTemplate(
            name="knowledge_synthesis",
            prompt_type=PromptType.BACKGROUND_KNOWLEDGE,
            template=template,
            variables=[
                "scenario",
                "retrieved_knowledge",
                "background_knowledge",
                "domain_context",
                "previous_analysis",
                "quality_criteria",
                "confidence_assessment",
            ],
            thinking_effort="high",
            max_tokens=1536,
            temperature=0.6,
            description="Synthesizes and integrates knowledge from multiple sources",
        )

    def _create_parse_causal_structure_template(self) -> PromptTemplate:
        """Template for natural language causal structure analysis"""
        template = """
You are an expert in causal reasoning and natural language analysis. Your task is to analyze the causal structure of scenarios and provide comprehensive natural language descriptions.

Write a natural language description of the causal structure of the underlying model for this scenario.

Make sure to describe the structure of the world that would allow you to reason about the scenario provided. 
Make sure to RELATE ALL RELEVANT INFORMATION in the scenario in your description.

The natural language should describe the general, causal model of the situation and what factors matter. 
Draw on your prior common sense knowledge about the world to write this description, and make sure to 
include any frequencies, probabilities, and units for causal factors you mention.

Consider the following aspects in your analysis:
1. **Underlying Mechanisms**: What are the fundamental processes that drive outcomes in this scenario?
2. **Causal Factors**: What variables influence the outcomes and how do they interact?
3. **Dependencies**: Which factors depend on others and in what ways?
4. **Probabilistic Elements**: What aspects involve uncertainty or randomness?
5. **Domain Knowledge**: What background knowledge is relevant to understanding this scenario?

Follow the prompts and start your response with <START_SCRATCHPAD> and end with <END_SCRATCHPAD>.

Scenario: {scenario}

Additional Context: {context}
"""

        return PromptTemplate(
            name="parse_causal_structure",
            prompt_type=PromptType.PARSE_CAUSAL_STRUCTURE,
            template=template,
            variables=["scenario", "context"],
            thinking_effort="high",
            max_tokens=1024,
            temperature=0.7,
            description="Generates natural language descriptions of causal structure",
        )

    def _create_concept_trace_template(self) -> PromptTemplate:
        """Template for concept trace generation with dependencies"""
        template = """
Based on the scenario and natural language description, extract a list of concepts and their dependencies.

Scenario: {scenario}

Natural Language Description: {natural_description}

Extract concepts that your description implies. Include any dependencies between the concepts, 
and make sure to sort the concepts so that named concepts appear before any that depend on them.

Consider the following when identifying concepts:
1. **Core Entities**: Key objects, people, or systems in the scenario
2. **Properties**: Attributes or characteristics of entities
3. **Processes**: Actions, transformations, or mechanisms
4. **Outcomes**: Results, effects, or consequences
5. **Relationships**: Connections or interactions between concepts

For dependencies, consider:
- **Causal Dependencies**: A causes or influences B
- **Definitional Dependencies**: A is required to define B
- **Temporal Dependencies**: A must occur before B
- **Logical Dependencies**: A is a prerequisite for understanding B

Format your response as:
<START_CONCEPT_TRACE>
- concept1
- concept2
  - depends on: concept1
- concept3
  - depends on: concept1, concept2
- concept4
  - depends on: concept2
<END_CONCEPT_TRACE>

Entities: {entities}
Causal Factors: {causal_factors}
"""

        return PromptTemplate(
            name="concept_trace_generation",
            prompt_type=PromptType.CONCEPT_TRACE_GENERATION,
            template=template,
            variables=["scenario", "natural_description", "entities", "causal_factors"],
            thinking_effort="high",
            max_tokens=512,
            temperature=0.5,
            description="Generates concept traces with dependency mapping",
        )

    def _create_background_knowledge_template(self) -> PromptTemplate:
        """Template for background knowledge synthesis"""
        template = """
Generate comprehensive background knowledge for this scenario that will enhance reasoning and modeling capabilities.

Scenario: {scenario}

Key Entities: {entities}
Key Concepts: {concepts}
Domain: {domain}

Please provide background knowledge that includes:

1. **Domain-Specific Information**: 
   - Relevant facts, principles, and patterns specific to this domain
   - Typical behaviors, constraints, and relationships
   - Standard practices and common approaches

2. **Causal Relationships**:
   - How different factors typically influence outcomes
   - Common cause-and-effect patterns in this domain
   - Interaction effects and feedback loops

3. **Probabilistic Information**:
   - Typical frequencies, rates, and probabilities
   - Uncertainty sources and variability patterns
   - Statistical relationships and correlations

4. **Contextual Factors**:
   - Environmental conditions that matter
   - Temporal aspects and timing considerations
   - Scale effects and boundary conditions

5. **Hidden Factors**:
   - Important variables that might not be explicitly mentioned
   - Confounding variables or alternative explanations
   - Assumptions that are typically made in this domain

Structure your response to provide comprehensive background that would help someone understand the causal structure and make informed predictions about this type of scenario.

Start with <START_BACKGROUND_KNOWLEDGE> and end with <END_BACKGROUND_KNOWLEDGE>.

Previous Analysis: {previous_analysis}
"""

        return PromptTemplate(
            name="background_knowledge",
            prompt_type=PromptType.BACKGROUND_KNOWLEDGE,
            template=template,
            variables=["scenario", "entities", "concepts", "domain", "previous_analysis"],
            thinking_effort="high",
            max_tokens=1024,
            temperature=0.7,
            description="Generates comprehensive background knowledge for reasoning",
        )

    def _create_entity_extraction_template(self) -> PromptTemplate:
        """Template for entity and causal factor extraction"""
        template = """
Extract entities and causal factors from this scenario and its natural language description.

Scenario: {scenario}

Natural Language Description: {natural_description}

Please identify:

1. **ENTITIES**: 
   - People, organizations, objects, or systems mentioned
   - Abstract concepts that play key roles
   - Measurable quantities or variables
   - Groups, categories, or classifications

2. **CAUSAL_FACTORS**: 
   - Variables that influence outcomes or decisions
   - Mechanisms that drive changes or effects
   - Conditions that enable or prevent outcomes
   - Sources of variation or uncertainty

Consider both explicitly mentioned and implicitly relevant factors based on domain knowledge.

Format as JSON:
{{
    "entities": ["entity1", "entity2", ...],
    "causal_factors": ["factor1", "factor2", ...],
    "entity_types": {{"entity1": "person", "entity2": "system", ...}},
    "factor_types": {{"factor1": "performance", "factor2": "environmental", ...}}
}}

Context: {context}
"""

        return PromptTemplate(
            name="entity_extraction",
            prompt_type=PromptType.ENTITY_EXTRACTION,
            template=template,
            variables=["scenario", "natural_description", "context"],
            thinking_effort="medium",
            max_tokens=512,
            temperature=0.3,
            description="Extracts entities and causal factors with categorization",
        )

    def _create_confidence_assessment_template(self) -> PromptTemplate:
        """Template for confidence assessment and validation"""
        template = """
Assess the confidence and reliability of the reasoning analysis for this scenario.

Scenario: {scenario}

Analysis Results:
{analysis_results}

Please evaluate the following aspects and provide a confidence assessment:

1. **Data Quality** (0-1 scale):
   - Completeness of information provided
   - Clarity and specificity of the scenario
   - Presence of ambiguous or conflicting information

2. **Reasoning Quality** (0-1 scale):
   - Logical consistency of the analysis
   - Appropriateness of causal relationships identified
   - Alignment with domain knowledge and common sense

3. **Coverage Completeness** (0-1 scale):
   - Comprehensiveness of entity identification
   - Completeness of causal factor analysis
   - Coverage of relevant background knowledge

4. **Uncertainty Factors**:
   - Sources of uncertainty in the analysis
   - Assumptions that were made
   - Alternative interpretations that are plausible

5. **Validation Checks**:
   - Internal consistency of the analysis
   - Alignment with expected patterns
   - Robustness to minor variations

Provide your assessment in the following format:
{{
    "overall_confidence": 0.0-1.0,
    "data_quality": 0.0-1.0,
    "reasoning_quality": 0.0-1.0,
    "coverage_completeness": 0.0-1.0,
    "uncertainty_sources": ["source1", "source2", ...],
    "key_assumptions": ["assumption1", "assumption2", ...],
    "confidence_explanation": "Detailed explanation of confidence assessment",
    "improvement_suggestions": ["suggestion1", "suggestion2", ...]
}}

Stage: {stage}
Metrics: {metrics}
"""

        return PromptTemplate(
            name="confidence_assessment",
            prompt_type=PromptType.CONFIDENCE_ASSESSMENT,
            template=template,
            variables=["scenario", "analysis_results", "stage", "metrics"],
            thinking_effort="high",
            max_tokens=1024,
            temperature=0.3,
            description="Assesses confidence and reliability of reasoning analysis",
        )

    def _create_final_synthesis_template(self) -> PromptTemplate:
        """Template for final answer synthesis"""
        template = """
Based on the comprehensive MSA analysis results, provide a detailed final answer for this scenario.

Original Scenario: {scenario}

Analysis Results from All Stages:
{stage_results}

Key Insights:
{insights}

Confidence Assessment: {confidence_score}

Please provide a comprehensive final answer that:

1. **Directly Addresses the Scenario**:
   - Answer any specific questions posed
   - Address the core reasoning challenge
   - Provide actionable insights or recommendations

2. **Synthesizes Multi-Stage Analysis**:
   - Integrate findings from parse, knowledge, graph, synthesis, and inference stages
   - Highlight key causal relationships and dependencies
   - Connect background knowledge to specific scenario elements

3. **Provides Clear Reasoning**:
   - Explain the logical flow from analysis to conclusions
   - Justify key inferences and predictions
   - Acknowledge uncertainty where appropriate

4. **Offers Practical Value**:
   - Provide actionable recommendations or next steps
   - Highlight critical factors to monitor or consider
   - Suggest areas for further investigation if needed

5. **Maintains Appropriate Confidence**:
   - Clearly communicate the reliability of conclusions
   - Distinguish between high-confidence and speculative elements
   - Provide appropriate caveats and limitations

Format your response as a structured analysis with clear sections:
- **Executive Summary**: Key findings and recommendations
- **Detailed Analysis**: Comprehensive reasoning and evidence
- **Confidence Assessment**: Reliability and limitations
- **Next Steps**: Recommendations for action or further analysis

Session Context: {session_context}
User Requirements: {user_requirements}
"""

        return PromptTemplate(
            name="final_synthesis",
            prompt_type=PromptType.FINAL_SYNTHESIS,
            template=template,
            variables=[
                "scenario",
                "stage_results",
                "insights",
                "confidence_score",
                "session_context",
                "user_requirements",
            ],
            thinking_effort="high",
            max_tokens=2048,
            temperature=0.7,
            description="Synthesizes comprehensive final answer from all MSA stages",
        )

    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Get a specific prompt template by name"""
        return self.templates.get(template_name)

    def get_templates_by_type(self, prompt_type: PromptType) -> List[PromptTemplate]:
        """Get all templates of a specific type"""
        return [template for template in self.templates.values() if template.prompt_type == prompt_type]

    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with provided variables"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Check if all required variables are provided
        missing_vars = [var for var in template.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables for template '{template_name}': {missing_vars}")

        # Format the template
        return template.template.format(**kwargs)

    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a specific template"""
        template = self.get_template(template_name)
        if not template:
            return {}

        return {
            "name": template.name,
            "type": template.prompt_type.value,
            "variables": template.variables,
            "thinking_effort": template.thinking_effort,
            "max_tokens": template.max_tokens,
            "temperature": template.temperature,
            "description": template.description,
        }


# Global template instance
_msa_templates: Optional[MSAPromptTemplates] = None


def get_msa_templates() -> MSAPromptTemplates:
    """Get the global MSA prompt templates instance"""
    global _msa_templates
    if _msa_templates is None:
        _msa_templates = MSAPromptTemplates()
    return _msa_templates
