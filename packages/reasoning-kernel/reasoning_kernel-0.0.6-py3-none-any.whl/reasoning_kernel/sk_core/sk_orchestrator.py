"""
Semantic Kernel Orchestrator
============================

Replaces the complex orchestrator system with Semantic Kernel's agent orchestration.
Provides sequential and collaborative execution patterns for MSA reasoning.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from .msa_agents import MSAGraphPlugin, MSAInferencePlugin, MSAKnowledgePlugin, MSAParsePlugin, MSASynthesisPlugin
from .msa_program_plugin import MSAExecutionPlugin, MSAProgramPlugin

logger = logging.getLogger(__name__)


class MSAOrchestrator:
    """
    Orchestrates MSA reasoning pipeline using Semantic Kernel agents.
    Replaces the complex existing orchestrator with SK-native patterns.
    """

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.execution_history = []

        # Add MSA plugins to kernel
        self.kernel.add_plugin(MSAParsePlugin(kernel), plugin_name="msa_parse")
        self.kernel.add_plugin(MSAKnowledgePlugin(kernel), plugin_name="msa_knowledge")
        self.kernel.add_plugin(MSAGraphPlugin(kernel), plugin_name="msa_graph")
        self.kernel.add_plugin(MSASynthesisPlugin(kernel), plugin_name="msa_synthesis")
        self.kernel.add_plugin(MSAProgramPlugin(kernel), plugin_name="msa_program")
        self.kernel.add_plugin(MSAExecutionPlugin(kernel), plugin_name="msa_execution")
        self.kernel.add_plugin(MSAInferencePlugin(kernel), plugin_name="msa_inference")

        logger.info("MSA Orchestrator initialized with SK plugins")

    async def execute_msa_pipeline(
        self, vignette: str, pipeline_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete MSA reasoning pipeline.

        Args:
            vignette: The vignette text to analyze
            pipeline_config: Configuration for pipeline execution

        Returns:
            Complete MSA analysis results with all stage outputs
        """

        logger.info("Starting MSA pipeline execution")

        if pipeline_config is None:
            pipeline_config = {
                "extraction_mode": "all",
                "domain": "cognitive",
                "graph_type": "hybrid",
                "confidence_threshold": 0.6,
                "inference_type": "bayesian",
            }
        execution_id = f"msa_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        results: Dict[str, Any] = {
            "execution_id": execution_id,
            "vignette": vignette,
        }

        try:
            # Stage 1: Parse
            logger.info("Executing MSA Parse stage")
            parse_result = await self._execute_stage(
                plugin_name="msa_parse",
                function_name="parse_vignette",
                arguments={
                    "vignette": vignette,
                    "extraction_mode": pipeline_config.get("extraction_mode", "all"),
                },
            )
            results["parse"] = parse_result

            # Stage 2: Knowledge
            logger.info("Executing MSA Knowledge stage")
            knowledge_result = await self._execute_stage(
                plugin_name="msa_knowledge",
                function_name="retrieve_domain_knowledge",
                arguments={
                    "context": vignette,
                    "domain": pipeline_config.get("domain", "cognitive"),
                },
            )
            results["knowledge"] = knowledge_result

            # Stage 3: Graph
            logger.info("Executing MSA Graph stage")
            graph_result = await self._execute_stage(
                plugin_name="msa_graph",
                function_name="build_reasoning_graph",
                arguments={
                    "parsed_elements": parse_result,
                    "graph_type": pipeline_config.get("graph_type", "hybrid"),
                },
            )
            results["graph"] = graph_result

            # Stage 4: Synthesis
            logger.info("Executing MSA Synthesis stage")
            synthesis_result = await self._execute_stage(
                plugin_name="msa_synthesis",
                function_name="synthesize_reasoning",
                arguments={
                    "parsed_data": parse_result,
                    "knowledge_data": knowledge_result,
                    "graph_data": graph_result,
                    "confidence_threshold": pipeline_config.get("confidence_threshold", 0.6),
                },
            )
            results["synthesis"] = synthesis_result

            # Stage 5: Program Generation (LLM -> PPL)
            logger.info("Generating PPL program from MSA synthesis")
            program_code = await self._execute_stage(
                plugin_name="msa_program",
                function_name="generate_probabilistic_program",
                arguments={
                    "parsed_data": parse_result,
                    "knowledge_data": knowledge_result,
                    "graph_data": graph_result,
                    "synthesis_data": synthesis_result,
                    "framework": pipeline_config.get("ppl_framework", "numpyro"),
                },
            )
            results["program_code"] = program_code

            # Stage 6: Program Execution (PPL)
            logger.info("Executing generated PPL program")
            ppl_exec_result = await self._execute_stage(
                plugin_name="msa_execution",
                function_name="execute_probabilistic_program",
                arguments={
                    "code": program_code,
                    "framework": pipeline_config.get("ppl_framework", "numpyro"),
                    "input_data": pipeline_config.get("ppl_input", "{}"),
                    "max_seconds": int(pipeline_config.get("ppl_timeout", 90)),
                },
            )
            results["ppl_execution"] = ppl_exec_result

            # Stage 7: Inference (optional, on top of PPL results)
            logger.info("Executing MSA Inference stage")
            inference_result = await self._execute_stage(
                plugin_name="msa_inference",
                function_name="generate_probabilistic_inferences",
                arguments={
                    "synthesis_data": synthesis_result,
                    "inference_type": pipeline_config.get("inference_type", "bayesian"),
                },
            )
            results["inference"] = inference_result

            # Pipeline summary
            results["pipeline_status"] = "completed"
            results["execution_time"] = datetime.now().isoformat()
            results["config_used"] = pipeline_config

            logger.info(f"MSA pipeline completed successfully: {execution_id}")

        except Exception as e:
            logger.error(f"MSA pipeline failed: {e}")
            results["pipeline_status"] = "failed"
            results["error"] = str(e)

        self.execution_history.append(results)
        return results

    async def execute_collaborative_reasoning(
        self, vignette: str, collaboration_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute collaborative reasoning where MSA agents can interact and revise.
        More sophisticated than sequential pipeline.
        """

        logger.info("Starting collaborative MSA reasoning")

        if collaboration_config is None:
            collaboration_config = {
                "max_iterations": 3,
                "convergence_threshold": 0.1,
                "enable_cross_validation": True,
                "revision_mode": "adaptive",
            }
        execution_id = f"collab_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        results: Dict[str, Any] = {
            "execution_id": execution_id,
            "vignette": vignette,
            "mode": "collaborative",
        }

        iterations: List[Dict[str, Any]] = []

        try:
            for iteration in range(collaboration_config.get("max_iterations", 3)):
                logger.info(f"Collaborative iteration {iteration + 1}")

                iteration_result = await self._collaborative_iteration(
                    vignette=vignette,
                    previous_iterations=iterations,
                    config=collaboration_config,
                )

                iterations.append(iteration_result)

                # Check for convergence
                if self._check_convergence(iterations, collaboration_config):
                    logger.info(f"Convergence reached at iteration {iteration + 1}")
                    break

            results["iterations"] = iterations
            results["final_result"] = iterations[-1] if iterations else {}
            results["collaboration_status"] = "completed"
            results["total_iterations"] = len(iterations)

        except Exception as e:
            logger.error(f"Collaborative reasoning failed: {e}")
            results["collaboration_status"] = "failed"
            results["error"] = str(e)

        self.execution_history.append(results)
        return results

    async def _execute_stage(self, plugin_name: str, function_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a single MSA stage using SK function calling.

        Prefer Kernel.get_function(plugin, function) which is the canonical
        Semantic Kernel pattern. Fall back to locating the function from the
        plugin registry for compatibility with older setups.
        """

        try:
            kernel_func = None
            # Preferred: use SK's get_function API
            try:
                kernel_func = self.kernel.get_function(plugin_name, function_name)
            except Exception:
                # Fallback: access function via plugin mapping
                try:
                    plugin_map = self.kernel.get_plugin(plugin_name)
                    kernel_func = plugin_map[function_name]
                except Exception:
                    kernel_func = None

            if kernel_func is None:
                raise ValueError(f"Function not found: {plugin_name}.{function_name}")

            # Create kernel arguments and invoke
            kernel_args = KernelArguments(**arguments)
            result = await self.kernel.invoke(kernel_func, kernel_args)
            return str(result)

        except Exception as e:
            logger.error(f"Stage execution failed - {plugin_name}.{function_name}: {e}")
            return json.dumps({"error": str(e), "stage": f"{plugin_name}.{function_name}"})

    async def _collaborative_iteration(
        self,
        vignette: str,
        previous_iterations: List[Dict[str, Any]],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute one iteration of collaborative reasoning"""

        # Prepare context from previous iterations
        context = self._prepare_collaborative_context(previous_iterations)

        # Execute parallel analysis by multiple agents
        tasks = []

        # Parse with context from previous iterations
        tasks.append(
            self._execute_stage(
                "msa_parse",
                "parse_vignette",
                {"vignette": vignette, "extraction_mode": "all"},
            )
        )

        # Knowledge with adaptive domain selection
        tasks.append(
            self._execute_stage(
                "msa_knowledge",
                "apply_cognitive_principles",
                {"reasoning_context": vignette + context, "principles": "auto"},
            )
        )

        # Graph analysis with previous graph comparison
        if previous_iterations:
            prev_graph = self._extract_previous_graph(previous_iterations)
            tasks.append(
                self._execute_stage(
                    "msa_graph",
                    "analyze_graph_structure",
                    {"reasoning_graph": prev_graph},
                )
            )

        # Execute tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        iteration_result = {
            "iteration_data": results,
            "context_used": context,
            "timestamp": datetime.now().isoformat(),
        }

        return iteration_result

    def _prepare_collaborative_context(self, previous_iterations: List[Dict[str, Any]]) -> str:
        """Prepare context string from previous iterations"""

        if not previous_iterations:
            return ""

        context_parts = []
        for i, iteration in enumerate(previous_iterations):
            context_parts.append(f"Iteration {i+1} insights: {str(iteration)[:200]}...")

        return "\n".join(context_parts)

    def _extract_previous_graph(self, previous_iterations: List[Dict[str, Any]]) -> str:
        """Extract graph data from previous iterations"""

        for iteration in reversed(previous_iterations):
            iteration_data = iteration.get("iteration_data", [])
            for data in iteration_data:
                if isinstance(data, str) and "nodes" in data:
                    return data

        return "{}"

    def _check_convergence(self, iterations: List[Dict[str, Any]], config: Dict[str, Any]) -> bool:
        """Check if collaborative reasoning has converged"""

        if len(iterations) < 2:
            return False

        # Simple convergence check - could be more sophisticated
        threshold = config.get("convergence_threshold", 0.1)

        # For now, simple similarity check
        latest = str(iterations[-1])
        previous = str(iterations[-2])

        # Basic similarity measure
        similarity = len(set(latest.split()) & set(previous.split())) / len(set(latest.split() + previous.split()))

        return similarity > (1 - threshold)

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of all executions"""
        return self.execution_history

    def get_latest_execution(self) -> Optional[Dict[str, Any]]:
        """Get the most recent execution result"""
        return self.execution_history[-1] if self.execution_history else None


class SequentialReasoningOrchestrator:
    """
    Simplified sequential orchestrator for straightforward MSA pipeline execution.
    Uses Semantic Kernel function chaining.
    """

    def __init__(self, kernel: Kernel):
        self.kernel = kernel

        # Add orchestrator functions to kernel
        self.kernel.add_plugin(self, plugin_name="sequential_orchestrator")

    @kernel_function(
        name="execute_sequential_msa",
        description="Execute MSA pipeline in sequential stages with dependency management",
    )
    async def execute_sequential_msa(
        self,
        vignette: Annotated[str, "The vignette to analyze through MSA pipeline"],
        config: Annotated[str, "JSON configuration for pipeline execution"] = "{}",
    ) -> str:
        """Execute sequential MSA pipeline with proper stage dependencies"""

        try:
            config_dict = json.loads(config) if config else {}

            # Use the main orchestrator
            orchestrator = MSAOrchestrator(self.kernel)
            results = await orchestrator.execute_msa_pipeline(vignette, config_dict)

            return json.dumps(results, indent=2)

        except Exception as e:
            logger.error(f"Sequential MSA execution failed: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @kernel_function(
        name="execute_stage_analysis",
        description="Execute analysis of a specific MSA stage in isolation",
    )
    async def execute_stage_analysis(
        self,
        vignette: Annotated[str, "The vignette to analyze"],
        stage: Annotated[str, "MSA stage: 'parse', 'knowledge', 'graph', 'synthesis', 'inference'"],
        stage_config: Annotated[str, "JSON configuration for the specific stage"] = "{}",
    ) -> str:
        """Execute a single MSA stage for focused analysis"""

        try:
            config_dict = json.loads(stage_config) if stage_config else {}

            stage_mappings = {
                "parse": ("msa_parse", "parse_vignette", {"vignette": vignette}),
                "knowledge": (
                    "msa_knowledge",
                    "retrieve_domain_knowledge",
                    {"context": vignette},
                ),
                "graph": (
                    "msa_graph",
                    "build_reasoning_graph",
                    {"parsed_elements": "{}"},
                ),
                "synthesis": (
                    "msa_synthesis",
                    "synthesize_reasoning",
                    {"parsed_data": "{}", "knowledge_data": "{}", "graph_data": "{}"},
                ),
                "inference": (
                    "msa_inference",
                    "generate_probabilistic_inferences",
                    {"synthesis_data": "{}"},
                ),
            }

            if stage not in stage_mappings:
                raise ValueError(f"Unknown stage: {stage}")

            plugin_name, function_name, base_args = stage_mappings[stage]

            # Merge with provided config
            args = {**base_args, **config_dict}

            # Execute single stage
            orchestrator = MSAOrchestrator(self.kernel)
            result = await orchestrator._execute_stage(plugin_name, function_name, args)

            return result

        except Exception as e:
            logger.error(f"Stage analysis failed: {e}")
            return json.dumps({"error": str(e), "stage": stage, "status": "failed"})


# Export orchestrator classes
__all__ = ["MSAOrchestrator", "SequentialReasoningOrchestrator"]
