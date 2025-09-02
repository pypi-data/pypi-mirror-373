"""
Prompt Manager for MSA Integration

This module provides centralized prompt management for the unified MSA architecture,
integrating with Semantic Kernel and GPT-5 connector for enhanced reasoning capabilities.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from reasoning_kernel.prompts.msa_prompt_templates import PromptTemplate, get_msa_templates
from reasoning_kernel.prompts.performance_optimizer import OptimizationConfig, get_optimizer
from reasoning_kernel.prompts.template_versioning import get_version_manager

# from reasoning_kernel.cloud.gpt5_connector import LLMRequest, LLMResponse  # Removed - GPT5 not available yet


@dataclass
class LLMResponse:
    content: str
    usage: Dict[str, Any]
    model: str
    response_time: float


@dataclass
class LLMRequest:
    messages: Any
    temperature: float
    max_tokens: int
    thinking_effort: Any = None
    enable_summary: bool = False


logger = logging.getLogger(__name__)


@dataclass
class PromptContext:
    """Context for prompt execution"""

    stage: str
    scenario: str
    session_id: str
    enhanced_mode: bool = True
    verbose: bool = False
    previous_results: Dict[str, Any] = None
    stage_config: Dict[str, Any] = None

    def __post_init__(self):
        if self.previous_results is None:
            self.previous_results = {}
        if self.stage_config is None:
            self.stage_config = {}


class MSAPromptManager:
    """Centralized prompt manager for MSA reasoning"""

    def __init__(self, gpt5_connector=None, optimization_config: OptimizationConfig = None):
        self.gpt5_connector = gpt5_connector
        self.templates = get_msa_templates()
        self.optimizer = get_optimizer(optimization_config)
        self.version_manager = get_version_manager()
        self._prompt_cache = {}  # Legacy cache, now using optimizer

    async def execute_prompt(self, template_name: str, context: PromptContext, **template_variables) -> LLMResponse:
        """
        Execute a prompt template with the given context and variables

        Args:
            template_name: Name of the template to execute
            context: Prompt execution context
            **template_variables: Variables to substitute in the template

        Returns:
            LLM response from GPT-5
        """
        try:
            # Get template (considering A/B testing and versioning)
            user_id = context.session_id  # Use session_id as user identifier for A/B testing
            versioned_template = self.version_manager.get_template_for_execution(template_name, user_id)

            if versioned_template:
                template = versioned_template
            else:
                # Fallback to default template
                template = self.templates.get_template(template_name)
                if not template:
                    raise ValueError(f"Template '{template_name}' not found")

            # Add context variables to template variables
            enhanced_variables = self._prepare_template_variables(context, template_variables)

            # Use optimizer for execution
            async def _execute_template():
                # Format prompt
                formatted_prompt = self.templates.format_prompt(template_name, **enhanced_variables)

                # Execute with GPT-5
                if self.gpt5_connector:
                    request = LLMRequest(
                        messages=[{"role": "user", "content": formatted_prompt}],
                        temperature=template.temperature,
                        max_tokens=template.max_tokens,
                        thinking_effort=template.thinking_effort,
                        enable_summary=True,
                    )

                    response = await self.gpt5_connector.generate_response(request)

                    if context.verbose:
                        logger.info(f"Executed prompt '{template_name}' for stage '{context.stage}'")

                    return response
                else:
                    # Fallback response if no GPT-5 connector
                    logger.warning(f"No GPT-5 connector available for prompt '{template_name}'")
                    return LLMResponse(
                        content=f"Fallback response for {template_name}",
                        usage={
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                        model="fallback",
                        response_time=0.0,
                    )

            # Execute with optimization
            response, metrics = await self.optimizer.optimize_template_execution(
                template_name=template_name,
                variables=enhanced_variables,
                execution_func=_execute_template,
            )

            # Log performance metrics if verbose
            if context.verbose:
                logger.info(
                    f"Template '{template_name}' metrics: "
                    f"time={metrics.execution_time:.2f}s, "
                    f"tokens={metrics.tokens_used}, "
                    f"cache_hit={metrics.cache_hit}"
                )

            # Record metrics for versioning system if using versioned template
            if versioned_template:
                active_version = self.version_manager.get_active_version(template_name)
                if active_version:
                    performance_metrics = {
                        "execution_time": metrics.execution_time,
                        "tokens_used": metrics.tokens_used,
                        "success_rate": 1.0 if metrics.success else 0.0,
                        "response_size": len(response.content) if response.content else 0,
                    }
                    self.version_manager.record_performance_metrics(
                        template_name, active_version.version_id, performance_metrics
                    )

            return response

        except Exception as e:
            logger.error(f"Failed to execute prompt '{template_name}': {e}")
            return LLMResponse(
                content=f"Error executing prompt: {str(e)}",
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                model="error",
                response_time=0.0,
            )

    def _prepare_template_variables(self, context: PromptContext, template_variables: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare template variables by combining context and provided variables"""
        enhanced_variables = {
            "scenario": context.scenario,
            "session_id": context.session_id,
            "stage": context.stage,
            "enhanced_mode": context.enhanced_mode,
            "verbose": context.verbose,
            "previous_results": self._format_previous_results(context.previous_results),
            "context": self._extract_context_info(context),
        }

        # Add stage-specific variables
        enhanced_variables.update(self._get_stage_specific_variables(context))

        # Add provided template variables (these override defaults)
        enhanced_variables.update(template_variables)

        return enhanced_variables

    def _format_previous_results(self, previous_results: Dict[str, Any]) -> str:
        """Format previous results for template inclusion"""
        if not previous_results:
            return "No previous results available."

        formatted = []
        for stage, result in previous_results.items():
            if isinstance(result, dict) and result.get("success"):
                stage_data = result.get("data", {})
                formatted.append(f"{stage.upper()} STAGE:")

                if hasattr(stage_data, "natural_language_description"):
                    formatted.append(f"  Description: {stage_data.natural_language_description[:200]}...")
                elif hasattr(stage_data, "summary"):
                    formatted.append(f"  Summary: {stage_data.summary}")
                elif isinstance(stage_data, str):
                    formatted.append(f"  Result: {stage_data[:200]}...")

                formatted.append("")

        return "\n".join(formatted) if formatted else "Previous results available but not formatted."

    def _extract_context_info(self, context: PromptContext) -> str:
        """Extract contextual information for prompts"""
        context_info = []

        if context.enhanced_mode:
            context_info.append("Enhanced reasoning mode enabled")

        if context.verbose:
            context_info.append("Verbose processing requested")

        if context.stage_config:
            context_info.append(f"Stage configuration: {context.stage_config}")

        return "; ".join(context_info) if context_info else "Standard processing mode"

    def _get_stage_specific_variables(self, context: PromptContext) -> Dict[str, Any]:
        """Get stage-specific variables for template enhancement"""
        stage_variables = {}

        # Extract information from previous results based on stage
        if context.stage == "parse":
            stage_variables.update(
                {
                    "domain": self._extract_domain(context.scenario),
                    "entities": [],
                    "causal_factors": [],
                }
            )

        elif context.stage == "knowledge":
            parse_result = context.previous_results.get("parse", {}).get("data", {})
            stage_variables.update(
                {
                    "entities": getattr(parse_result, "entities", []),
                    "concepts": getattr(parse_result, "concept_trace", {}).get("concepts", []),
                    "domain_context": self._extract_domain(context.scenario),
                    "retrieved_knowledge": [],
                    "background_knowledge": "",
                }
            )

        elif context.stage == "graph":
            parse_result = context.previous_results.get("parse", {}).get("data", {})
            knowledge_result = context.previous_results.get("knowledge", {}).get("data", {})
            stage_variables.update(
                {
                    "entities": getattr(parse_result, "entities", []),
                    "concepts": getattr(parse_result, "concept_trace", {}).get("concepts", []),
                    "relationships": [],
                    "background_knowledge": getattr(knowledge_result, "informal_background_knowledge", ""),
                    "previous_analysis": self._format_previous_results(context.previous_results),
                }
            )

        elif context.stage == "synthesis":
            stage_variables.update(
                {
                    "causal_structure": self._extract_causal_structure(context.previous_results),
                    "knowledge_graph": self._extract_knowledge_graph(context.previous_results),
                    "background_knowledge": self._extract_background_knowledge(context.previous_results),
                    "concept_dependencies": self._extract_concept_dependencies(context.previous_results),
                    "requirements": "Comprehensive model synthesis",
                    "constraints": "Maintain logical consistency",
                }
            )

        elif context.stage == "inference":
            stage_variables.update(
                {
                    "model": self._extract_model(context.previous_results),
                    "evidence": self._extract_evidence(context.scenario),
                    "queries": self._extract_queries(context.scenario),
                    "method": "MCMC",
                    "computational_approach": "WebPPL",
                }
            )

        return stage_variables

    def _extract_domain(self, scenario: str) -> str:
        """Extract domain information from scenario"""
        # Simple domain extraction based on keywords
        scenario_lower = scenario.lower()

        if any(word in scenario_lower for word in ["student", "exam", "test", "grade", "education"]):
            return "education"
        elif any(word in scenario_lower for word in ["medical", "patient", "doctor", "treatment", "health"]):
            return "healthcare"
        elif any(word in scenario_lower for word in ["business", "company", "market", "profit", "sales"]):
            return "business"
        elif any(word in scenario_lower for word in ["sport", "game", "team", "competition", "athlete"]):
            return "sports"
        else:
            return "general"

    def _extract_causal_structure(self, previous_results: Dict[str, Any]) -> str:
        """Extract causal structure from previous results"""
        parse_result = previous_results.get("parse", {}).get("data", {})
        if hasattr(parse_result, "natural_language_description"):
            return parse_result.natural_language_description
        return "Causal structure not available"

    def _extract_knowledge_graph(self, previous_results: Dict[str, Any]) -> str:
        """Extract knowledge graph from previous results"""
        graph_result = previous_results.get("graph", {}).get("data", {})
        if isinstance(graph_result, dict):
            return str(graph_result)
        return "Knowledge graph not available"

    def _extract_background_knowledge(self, previous_results: Dict[str, Any]) -> str:
        """Extract background knowledge from previous results"""
        knowledge_result = previous_results.get("knowledge", {}).get("data", {})
        if hasattr(knowledge_result, "informal_background_knowledge"):
            return knowledge_result.informal_background_knowledge
        return "Background knowledge not available"

    def _extract_concept_dependencies(self, previous_results: Dict[str, Any]) -> str:
        """Extract concept dependencies from previous results"""
        parse_result = previous_results.get("parse", {}).get("data", {})
        if hasattr(parse_result, "concept_trace"):
            concept_trace = parse_result.concept_trace
            if hasattr(concept_trace, "dependencies"):
                return str(concept_trace.dependencies)
        return "Concept dependencies not available"

    def _extract_model(self, previous_results: Dict[str, Any]) -> str:
        """Extract model from previous results"""
        synthesis_result = previous_results.get("synthesis", {}).get("data", {})
        if isinstance(synthesis_result, dict):
            return str(synthesis_result)
        return "Model not available"

    def _extract_evidence(self, scenario: str) -> str:
        """Extract evidence from scenario"""
        # Simple evidence extraction - look for factual statements
        lines = scenario.split("\n")
        evidence = []

        for line in lines:
            line = line.strip()
            if line and any(word in line.lower() for word in ["in", "on", "during", "when", "given", "observed"]):
                evidence.append(line)

        return "; ".join(evidence) if evidence else "No explicit evidence identified"

    def _extract_queries(self, scenario: str) -> str:
        """Extract queries from scenario"""
        # Look for questions or query patterns
        lines = scenario.split("\n")
        queries = []

        for line in lines:
            line = line.strip()
            if line and (
                line.endswith("?")
                or any(word in line.lower() for word in ["what", "how", "why", "which", "who", "when", "where"])
            ):
                queries.append(line)

        return "; ".join(queries) if queries else "No explicit queries identified"

    async def execute_stage_prompts(
        self,
        stage: str,
        context: PromptContext,
        custom_variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, LLMResponse]:
        """Execute all relevant prompts for a specific MSA stage"""
        stage_prompts = self._get_stage_prompt_sequence(stage)
        results = {}

        for prompt_name in stage_prompts:
            try:
                variables = custom_variables or {}
                response = await self.execute_prompt(prompt_name, context, **variables)
                results[prompt_name] = response

                if context.verbose:
                    logger.info(f"Completed prompt '{prompt_name}' for stage '{stage}'")

            except Exception as e:
                logger.error(f"Failed to execute prompt '{prompt_name}' for stage '{stage}': {e}")
                results[prompt_name] = LLMResponse(
                    content=f"Error: {str(e)}",
                    usage={
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    },
                    model="error",
                    response_time=0.0,
                )

        return results

    def _get_stage_prompt_sequence(self, stage: str) -> List[str]:
        """Get the sequence of prompts to execute for a stage"""
        stage_sequences = {
            "parse": [
                "parse_causal_structure",
                "concept_trace_generation",
                "entity_extraction",
            ],
            "knowledge": ["background_knowledge", "knowledge_synthesis"],
            "graph": ["graph_construction", "relationship_mapping"],
            "synthesis": ["model_synthesis", "causal_model_generation"],
            "inference": ["probabilistic_inference", "webppl_generation"],
        }

        return stage_sequences.get(stage, [])

    def get_available_templates(self) -> List[str]:
        """Get list of available prompt templates"""
        return self.templates.list_templates()

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a specific template"""
        return self.templates.get_template_info(template_name)

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return self.optimizer.get_performance_report()

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache-specific statistics"""
        return self.optimizer.get_cache_statistics()

    async def clear_cache(self, template_name: Optional[str] = None):
        """Clear cache entries"""
        await self.optimizer.clear_cache(template_name)

    async def optimize_template_parameters(self, template_name: str) -> Dict[str, Any]:
        """Analyze and suggest optimizations for a specific template"""
        return await self.optimizer.optimize_template_parameters(template_name)

    # Template Versioning Methods

    def create_template_version(
        self,
        template_name: str,
        template: PromptTemplate,
        description: str,
        changelog: List[str],
        created_by: str = "system",
    ) -> str:
        """Create a new version of a template"""
        return self.version_manager.create_version(template_name, template, description, changelog, created_by)

    def activate_template_version(self, template_name: str, version_id: str) -> bool:
        """Activate a specific version of a template"""
        return self.version_manager.activate_version(template_name, version_id)

    def create_ab_test(
        self,
        template_name: str,
        version_a_id: str,
        version_b_id: str,
        traffic_split: float = 0.5,
        duration_days: int = 7,
        success_metrics: List[str] = None,
    ) -> str:
        """Create an A/B test between two template versions"""
        return self.version_manager.create_ab_test(
            template_name,
            version_a_id,
            version_b_id,
            traffic_split,
            duration_days,
            success_metrics,
        )

    def get_ab_test_report(self, test_id: str) -> Dict[str, Any]:
        """Get A/B test report"""
        return self.version_manager.get_ab_test_report(test_id)

    def get_template_version_history(self, template_name: str) -> List[Dict[str, Any]]:
        """Get version history for a template"""
        return self.version_manager.get_version_history(template_name)

    def promote_template_version(self, template_name: str, version_id: str) -> bool:
        """Promote a version to active status"""
        return self.version_manager.promote_version(template_name, version_id)

    def rollback_template_version(self, template_name: str) -> bool:
        """Rollback to previous active version"""
        return self.version_manager.rollback_version(template_name)


# Global prompt manager instance
_prompt_manager: Optional[MSAPromptManager] = None


async def get_prompt_manager(gpt5_connector=None, optimization_config: OptimizationConfig = None) -> MSAPromptManager:
    """Get the global prompt manager instance"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = MSAPromptManager(gpt5_connector, optimization_config)
    return _prompt_manager


# Compatibility alias for tests
PromptManager = MSAPromptManager
