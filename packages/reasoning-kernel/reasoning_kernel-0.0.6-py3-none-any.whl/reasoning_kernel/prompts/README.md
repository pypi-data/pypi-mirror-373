# MSA Prompt Templates for Enhanced Natural Language Reasoning

This directory contains standardized prompt templates based on MSA research patterns for improving reasoning quality across all MSA stages in the unified architecture.

## Overview

The prompt template system provides:

- **Standardized prompts** based on MSA research patterns from the msa-cogsci-2025-data repository
- **Semantic Kernel integration** for advanced orchestration and planning
- **GPT-5 optimization** with high thinking effort and structured outputs
- **Consistent formatting** with research-validated markers and patterns
- **Cross-stage integration** for comprehensive reasoning workflows

## Key Components

### 1. MSA Prompt Templates (`msa_prompt_templates.py`)

Contains standardized templates for all MSA stages:

#### Parse Stage Templates

- **`parse_causal_structure`**: Natural language causal structure analysis
- **`concept_trace_generation`**: Concept dependency mapping with topological sorting
- **`entity_extraction`**: Entity and causal factor identification

#### Knowledge Stage Templates

- **`background_knowledge`**: Comprehensive domain knowledge synthesis
- **`knowledge_synthesis`**: Multi-source knowledge integration

#### Graph Stage Templates

- **`graph_construction`**: Knowledge graph creation with nodes, edges, and clusters
- **`relationship_mapping`**: Detailed relationship analysis and categorization

#### Synthesis Stage Templates

- **`model_synthesis`**: Comprehensive model integration and validation
- **`causal_model_generation`**: Detailed causal model specification

#### Inference Stage Templates

- **`probabilistic_inference`**: Bayesian reasoning and uncertainty quantification
- **`webppl_generation`**: WebPPL code generation with MSA patterns

#### Cross-Stage Templates

- **`confidence_assessment`**: Reliability and uncertainty evaluation
- **`final_synthesis`**: Comprehensive answer generation

### 2. Prompt Manager (`prompt_manager.py`)

Centralized management system providing:

- **Template execution** with GPT-5 integration
- **Context management** for stage-specific variables
- **Variable preparation** and automatic context injection
- **Stage orchestration** with sequential prompt execution
- **Error handling** and fallback mechanisms

## MSA Research Patterns

The templates incorporate proven patterns from MSA research:

### Structured Markers

```
<START_SCRATCHPAD>
[Natural language reasoning and analysis]
<END_SCRATCHPAD>

<START_CONCEPT_TRACE>
- concept1
- concept2
  - depends on: concept1
<END_CONCEPT_TRACE>

<START_KNOWLEDGE_GRAPH>
NODES: [entities and concepts]
EDGES: [relationships and dependencies]
<END_KNOWLEDGE_GRAPH>
```

### Causal Structure Analysis

- **Background knowledge integration**: Domain-specific facts and principles
- **Causal relationship mapping**: Direct, indirect, and conditional causation
- **Probabilistic reasoning**: Uncertainty quantification and base rates
- **Natural language explanations**: Comprehensive causal descriptions

### Concept Dependency Mapping

- **Topological sorting**: Concepts ordered by dependencies
- **Dependency types**: Causal, definitional, temporal, logical
- **Relationship strength**: Weak, moderate, strong classifications
- **Confidence assessment**: Reliability scoring for each relationship

## Usage Examples

### Basic Template Execution

```python
from reasoning_kernel.prompts.prompt_manager import get_prompt_manager, PromptContext

# Initialize prompt manager
prompt_manager = await get_prompt_manager(gpt5_connector)

# Create context
context = PromptContext(
    stage="parse",
    scenario="Your scenario here",
    session_id="session_123",
    enhanced_mode=True,
    verbose=True
)

# Execute specific template
response = await prompt_manager.execute_prompt(
    "parse_causal_structure",
    context,
    context="Additional context information"
)
```

### Stage-Based Orchestration

```python
# Execute all prompts for a stage
stage_results = await prompt_manager.execute_stage_prompts(
    stage="parse",
    context=context,
    custom_variables={"domain": "healthcare"}
)
```

### Plugin Integration

```python
class MyMSAPlugin(BaseMSAPlugin):
    async def _initialize_plugin(self):
        self._prompt_manager = await get_prompt_manager(
            await self._get_gpt5_connector()
        )

    async def _process_stage(self, stage_input):
        context = PromptContext(
            stage=self.name,
            scenario=stage_input.scenario,
            session_id=stage_input.session_id,
            enhanced_mode=stage_input.enhanced_mode,
            verbose=stage_input.verbose,
            previous_results=stage_input.previous_results
        )

        response = await self._prompt_manager.execute_prompt(
            "my_template",
            context
        )

        return self._process_response(response)
```

## Template Structure

Each template includes:

### Template Definition

```python
PromptTemplate(
    name="template_name",
    prompt_type=PromptType.CATEGORY,
    template="Template content with {variables}",
    variables=["list", "of", "required", "variables"],
    thinking_effort="high",  # GPT-5 thinking effort level
    max_tokens=2048,         # Maximum response tokens
    temperature=0.7,         # Creativity/randomness level
    description="Template description"
)
```

### Variable Injection

Templates automatically receive:

- **`scenario`**: The input scenario text
- **`session_id`**: Current session identifier
- **`stage`**: Current MSA stage name
- **`previous_results`**: Formatted results from previous stages
- **`context`**: Additional contextual information

### Stage-Specific Variables

Each stage receives relevant variables:

- **Parse**: `domain`, `entities`, `causal_factors`
- **Knowledge**: `entities`, `concepts`, `domain_context`
- **Graph**: `relationships`, `background_knowledge`
- **Synthesis**: `causal_structure`, `knowledge_graph`
- **Inference**: `model`, `evidence`, `queries`

## GPT-5 Integration

Templates are optimized for GPT-5 with:

### High Thinking Effort

- **Deep reasoning**: Complex causal analysis and relationship mapping
- **Multi-step processing**: Sequential reasoning with intermediate steps
- **Uncertainty handling**: Confidence assessment and reliability scoring

### Structured Outputs

- **Consistent formatting**: Research-validated markers and patterns
- **Parseable responses**: JSON and structured text outputs
- **Error handling**: Graceful degradation and fallback mechanisms

### Context Management

- **Session persistence**: Maintaining context across stages
- **Progressive enhancement**: Building on previous stage results
- **Adaptive prompting**: Context-aware variable injection

## Best Practices

### Template Design

1. **Clear instructions**: Specific, actionable guidance
2. **Structured outputs**: Consistent formatting with markers
3. **Variable flexibility**: Support for optional and required variables
4. **Error resilience**: Graceful handling of missing information

### Prompt Execution

1. **Context preparation**: Ensure all required variables are provided
2. **Response validation**: Check for expected markers and structure
3. **Error handling**: Implement fallback mechanisms
4. **Performance monitoring**: Track execution time and token usage

### Integration Patterns

1. **Plugin consistency**: Use standard prompt manager integration
2. **Stage coordination**: Leverage previous results effectively
3. **Configuration management**: Support for stage-specific settings
4. **Testing validation**: Verify prompt effectiveness with test scenarios

## Configuration

### Template Settings

- **Thinking Effort**: `low`, `medium`, `high` for GPT-5 reasoning depth
- **Temperature**: 0.0-1.0 for creativity vs. consistency balance
- **Max Tokens**: Response length limits for different template types
- **Prompt Type**: Categorization for template organization

### Manager Settings

- **Cache Management**: Template and response caching strategies
- **Error Handling**: Fallback mechanisms and retry policies
- **Performance Monitoring**: Execution time and token usage tracking
- **Context Management**: Variable preparation and injection strategies

## Extending the System

### Adding New Templates

1. Define template in `msa_prompt_templates.py`
2. Add to appropriate stage sequence in prompt manager
3. Update variable preparation logic if needed
4. Test with representative scenarios

### Custom Prompt Types

1. Extend `PromptType` enum with new categories
2. Implement template creation methods
3. Update prompt manager stage sequences
4. Document usage patterns and best practices

This prompt template system provides a robust foundation for enhanced natural language reasoning in the unified MSA architecture, leveraging proven research patterns and optimized for modern LLM capabilities.
