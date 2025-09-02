"""
MSA Program and Execution Plugins (Semantic Kernel)
===================================================

Step 1 (LLM): Generate a probabilistic program (PPL) from parsed knowledge/graph.
Step 2 (PPL): Execute the program with mathematical precision using Daytona sandbox.

These plugins expose SK kernel functions that integrate tightly with the existing
DaytonaPPLExecutor while keeping LLM generation optional (has safe fallbacks).
"""

from __future__ import annotations

import json
import logging
from typing import Annotated, Optional, Any

# Simple fallback approach for SK imports
try:
    from semantic_kernel import Kernel
    from semantic_kernel.functions import kernel_function

    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    print("Warning: Semantic Kernel not available, using fallback")
    Kernel = Any
    SEMANTIC_KERNEL_AVAILABLE = False

    def kernel_function(**kwargs):
        """Fallback decorator when SK is not available."""

        def decorator(func):
            return func

        return decorator


# Temporarily comment out unused imports to fix SK environment
# from .azure_responses_adapter import (
#     chat_text_via_responses,
#     get_reasoning_config_from_env,
#     use_responses_api,
# )
from ..services.daytona_ppl_executor import (
    DaytonaPPLExecutor,
    PPLExecutionConfig,
    PPLExecutionResult,
    PPLFramework,
    PPLProgram,
)

logger = logging.getLogger(__name__)


class MSAProgramPlugin:
    """Generate a PPL program (NumPyro by default) from MSA stage outputs."""

    def __init__(self, kernel=None):
        self.kernel = kernel

    async def _chat_with_ai(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1200) -> str:
        """Chat with AI using kernel's chat service, with fallback."""
        if not self.kernel or not SEMANTIC_KERNEL_AVAILABLE:
            return ""
        try:
            # Use kernel's chat functionality - simplified for SK 1.36.0 compatibility
            chat_service = self.kernel.get_service("azure_openai_chat")
            if not chat_service:
                return ""

            # Simple prompt-based completion for compatibility
            response = await chat_service.complete_async(prompt, max_tokens=max_tokens, temperature=temperature)
            return response if isinstance(response, str) else str(response)
        except Exception as e:  # pragma: no cover - network/config optional
            logger.warning(f"PPL generation LLM call failed, using fallback: {e}")
            return ""

    @kernel_function(
        name="generate_probabilistic_program",
        description="Create executable probabilistic program from multi-stage analysis data using specified framework",
    )
    async def generate_probabilistic_program(
        self,
        synthesis_data: Annotated[str, "Analysis synthesis results as JSON string"],
        framework: Annotated[str, "Target framework: numpyro, pyro, or tfp"] = "numpyro",
        parsed_data: Annotated[str, "Parsed vignette elements as JSON"] = "{}",
        knowledge_data: Annotated[str, "Domain knowledge as JSON"] = "{}",
        graph_data: Annotated[str, "Reasoning graph as JSON"] = "{}",
    ) -> str:
        """
        Generate executable probabilistic programming code from MSA synthesis.

        Uses LLM to translate analysis results into framework-specific PPL code.
        Falls back to template if LLM unavailable. Optimized for token efficiency.

        Args:
            synthesis_data: Core analysis results (primary input)
            framework: Target PPL framework
            parsed_data: Optional parsed elements for context
            knowledge_data: Optional domain knowledge for context
            graph_data: Optional reasoning graph for context

        Returns:
            Executable Python PPL code string
        """

        # Prioritize synthesis_data as primary input, others for context only
        try:
            # Build token-optimized prompt focusing on synthesis
            prompt = f"""Create {framework} probabilistic model:

Synthesis: {synthesis_data}

Return Python code only:
- Function: def main(data=None) -> dict
- Include posterior sampling 
- Return {{\"posterior_mean\": float, \"confidence\": float}}"""

            # Add context only if synthesis is insufficient
            if parsed_data and parsed_data != "{}":
                prompt += f"\nContext: {parsed_data[:200]}..."  # Limit context tokens

            code = await self._chat_with_ai(prompt, temperature=0.1, max_tokens=800)

            if not code or len(code) < 50:
                logger.warning("LLM generated insufficient code, using fallback")
                return self._generate_fallback_template(framework, synthesis_data)

            logger.info(f"Generated {len(code)} chars of {framework} code")
            return code

        except Exception as e:
            logger.error(f"PPL generation failed: {e}")
            return self._generate_fallback_template(framework, synthesis_data)

    def _generate_fallback_template(self, framework: str, synthesis_data: str) -> str:
        """Generate fallback template when LLM fails."""
        # Return hardcoded minimal NumPyro template that always runs
        template = (
            "import numpy as np\n"
            "import jax.numpy as jnp\n"
            "import numpyro\n"
            "import numpyro.distributions as dist\n\n"
            "def model():\n"
            "    mu = numpyro.sample('mu', dist.Normal(0.0, 1.0))\n"
            "    sigma = numpyro.sample('sigma', dist.HalfNormal(1.0))\n"
            "    with numpyro.plate('N', 5):\n"
            "        numpyro.sample('obs', dist.Normal(mu, sigma), obs=jnp.array([0., 0.5, -0.2, 0.1, 0.3]))\n\n"
            "def main(input_data=None):\n"
            "    # Minimal stub returns deterministic summaries without sampling to keep runtime fast in tests.\n"
            "    return {'posterior_mean': 0.0, 'notes': 'fallback program'}\n"
        )
        return template


class MSAExecutionPlugin:
    """Execute a PPL program via DaytonaPPLExecutor and return structured results."""

    def __init__(self, kernel=None, executor=None):
        self.kernel = kernel
        self.executor = executor or DaytonaPPLExecutor()

    @kernel_function(
        name="execute_ppl",
        description="Execute a PPL program and return structured execution results",
    )
    @kernel_function(
        name="execute_probabilistic_program",
        description="Execute PPL program and return structured inference results as JSON",
    )
    async def execute_probabilistic_program(
        self,
        code: Annotated[str, "PPL program code to execute"],
        framework: Annotated[str, "PPL framework (numpyro|pyro|tfp|stan)"] = "numpyro",
        input_data: Annotated[str, "Input data as JSON string"] = "{}",
        timeout: Annotated[int, "Maximum execution time in seconds"] = 60,
    ) -> str:
        """
        Execute probabilistic programming code with structured error handling.

        Runs PPL code in sandboxed environment and returns inference results.
        Optimized for Semantic Kernel function calling with minimal parameters.

        Args:
            code: Complete Python PPL program with main() function
            framework: Target framework (defaults to numpyro)
            input_data: Optional input data as JSON
            timeout: Execution timeout in seconds

        Returns:
            JSON string with execution results or error details
        """

        try:
            # Normalize framework name for compatibility
            fw = framework.lower().strip()
            fw_enum = {
                "numpyro": PPLFramework.NUMPYRO,
                "pyro": PPLFramework.PYRO,
                "tfp": PPLFramework.TENSORFLOW_PROBABILITY,
                "stan": PPLFramework.STAN,
            }.get(fw, PPLFramework.NUMPYRO)

            # Configure executor with timeout (preserve injected mocks for testing)
            if self.executor is None:
                self.executor = DaytonaPPLExecutor(ppl_config=PPLExecutionConfig(max_execution_time=float(timeout)))
            else:
                try:
                    self.executor.ppl_config.max_execution_time = float(timeout)
                except Exception:
                    # Fallback to fresh executor if config adjustment fails
                    self.executor = DaytonaPPLExecutor(ppl_config=PPLExecutionConfig(max_execution_time=float(timeout)))

            # Create and execute PPL program
            program = PPLProgram(
                code=code,
                framework=fw_enum,
                entry_point="main",
                input_data=json.loads(input_data) if input_data.strip() else None,
            )

            result: PPLExecutionResult = await self.executor.execute_ppl_program(program)

            # Structure response for optimal LLM consumption
            status_obj = getattr(result, "status", None)
            response = {
                "success": result.exit_code == 0,
                "exit_code": result.exit_code,
                "status": getattr(status_obj, "value", None) if status_obj else None,
                "execution_time": result.execution_time,
                "inference_results": result.inference_results,
                "posterior_samples": result.posterior_samples,
                "convergence_diagnostics": result.convergence_diagnostics,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "validation_errors": result.validation_errors,
                "execution_metadata": result.execution_metadata,
            }

            logger.info(f"PPL execution completed: {fw} program, exit_code={result.exit_code}")
            return json.dumps(response)

        except Exception as e:
            logger.error(f"PPL execution failed: {e}")
            # Structured error response for LLM self-correction
            error_response = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "guidance": "Check code syntax, ensure main() function exists, verify input data format",
            }
            return json.dumps(error_response)
