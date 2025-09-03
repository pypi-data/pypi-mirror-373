"""
Daytona NumPyro Executor

Executes NumPyro models inside Daytona sandboxes. This file provides a thin
adapter over the existing DaytonaService/Executor APIs in the repo. It prepares
model code, creates sandbox configurations, runs the code, and parses JSON
results printed by the execution harness.

Notes & assumptions:
- Assumes a `DaytonaService` with `create_sandbox`, `execute_code`, and
  `destroy_sandbox` coroutine methods that accept sensible inputs and return
  dictionaries with `sandbox_id`, `output` (stdout), and `execution_time`.
- The sandboxed code must print a single JSON object to stdout containing
  `status` plus any results (samples, diagnostics, posterior_stats).
- The executor intentionally keeps execution code generation simple so it can
  be tested without JAX/NumPyro available locally.
"""

from __future__ import annotations

import asyncio
import json
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from reasoning_kernel.services.daytona_service import DaytonaService
except Exception:  # pragma: no cover - environment differences
    DaytonaService = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class NumPyroSandboxRequest:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_code: str = ""
    model_type: str = "causal"
    data: Optional[Dict[str, Any]] = None
    inference_params: Dict[str, Any] = field(
        default_factory=lambda: {"num_samples": 2000, "num_warmup": 1000, "num_chains": 2}
    )
    requires_jax_metal: bool = False
    timeout: int = 300
    memory_limit: str = "4GB"
    cpu_limit: str = "2"


@dataclass
class NumPyroSandboxResult:
    request_id: str
    status: str
    samples: Optional[Dict[str, Any]] = None
    diagnostics: Optional[Dict[str, Any]] = None
    posterior_stats: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    sandbox_id: Optional[str] = None
    error: Optional[str] = None


class DaytonaNumPyroExecutor:
    """Executor that runs NumPyro code in Daytona sandboxes."""

    def __init__(self, daytona_service: Optional[DaytonaService] = None):
        self.daytona = daytona_service or (DaytonaService() if DaytonaService else None)
        self.active_sandboxes: Dict[str, str] = {}

    def _create_sandbox_config(self, request: NumPyroSandboxRequest) -> Dict[str, Any]:
        packages = [
            "numpy>=1.24.0",
            "jax>=0.4.20",
            "jaxlib>=0.4.20",
            "numpyro>=0.15.0",
            "arviz>=0.17.0",
        ]

        if request.requires_jax_metal:
            packages.append("jax-metal>=0.1.0")

        config = {
            "image": "python:3.11-slim",
            "memory": request.memory_limit,
            "cpu": request.cpu_limit,
            "environment": {
                "JAX_PLATFORM_NAME": "metal" if request.requires_jax_metal else "cpu",
                "JAX_ENABLE_X64": "True",
                "XLA_PYTHON_CLIENT_PREALLOCATE": "False",
            },
            "packages": packages,
        }

        return config

    def _prepare_execution_code(self, request: NumPyroSandboxRequest) -> str:
        # Minimal wrapper that expects the model code to define a `model` function
        # and then runs MCMC using NUTS. It prints a JSON object with results.
        template = """
import json
import warnings
warnings.filterwarnings('ignore')

# Attempt to import NumPyro and JAX; if missing, return a clear error JSON.
try:
    import jax
    import jax.numpy as jnp
    import numpyro
    import numpyro.distributions as dist
    from numpyro.infer import MCMC, NUTS, Predictive
except Exception as e:
    print(json.dumps({"status": "error", "error": f"ImportError: {str(e)}"}))
    raise SystemExit(1)

# User model code begins
{model_code}
# User model code ends

# Data and params
data = {data}
num_samples = {num_samples}
num_warmup = {num_warmup}
num_chains = {num_chains}

try:
    kernel = NUTS(model)
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples, num_chains=num_chains, progress_bar=False)
    rng_key = jax.random.PRNGKey(0)
    if data and isinstance(data, dict) and len(data) > 0:
        mcmc.run(rng_key, **data)
    else:
        mcmc.run(rng_key)

    samples = mcmc.get_samples()

    # Keep a small sample subset to avoid huge payloads
    samples_small = {k: v[:100].tolist() for k, v in samples.items()}

    posterior_stats = {}
    for k, v in samples.items():
        posterior_stats[k] = {
            "mean": float(jnp.mean(v)),
            "std": float(jnp.std(v)),
            "median": float(jnp.median(v))
        }

    # Diagnostics best-effort
    try:
        from numpyro.diagnostics import effective_sample_size, split_gelman_rubin
        n_eff = {k: float(v.mean()) for k, v in effective_sample_size(samples).items()} if 'effective_sample_size' in globals() else {}
        r_hat = {k: float(v.mean()) for k, v in split_gelman_rubin(samples).items()} if 'split_gelman_rubin' in globals() else {}
        diagnostics = {"n_eff": n_eff, "r_hat": r_hat}
    except Exception:
        diagnostics = {}

    result = {
        "status": "success",
        "samples": samples_small,
        "posterior_stats": posterior_stats,
        "diagnostics": diagnostics
    }
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"status": "error", "error": str(e)}))
"""

        # Fill in the template
        filled = template.format(
            model_code=request.model_code,
            data=json.dumps(request.data) if request.data else "{}",
            num_samples=request.inference_params.get("num_samples", 2000),
            num_warmup=request.inference_params.get("num_warmup", 1000),
            num_chains=request.inference_params.get("num_chains", 2),
        )

        return filled

    def _parse_sandbox_output(
        self, sandbox_response: Dict[str, Any], request: NumPyroSandboxRequest
    ) -> NumPyroSandboxResult:
        output = sandbox_response.get("output", "{}")
        try:
            parsed = json.loads(output)
        except Exception as e:
            logger.error("Failed to parse sandbox output as JSON: %s", e)
            return NumPyroSandboxResult(
                request_id=request.request_id,
                status="error",
                error=f"Invalid JSON output: {e}",
                execution_time=sandbox_response.get("execution_time", 0.0),
                sandbox_id=sandbox_response.get("sandbox_id"),
            )

        if parsed.get("status") == "success":
            return NumPyroSandboxResult(
                request_id=request.request_id,
                status="success",
                samples=parsed.get("samples"),
                diagnostics=parsed.get("diagnostics"),
                posterior_stats=parsed.get("posterior_stats"),
                execution_time=sandbox_response.get("execution_time", 0.0),
                sandbox_id=sandbox_response.get("sandbox_id"),
            )
        else:
            return NumPyroSandboxResult(
                request_id=request.request_id,
                status="error",
                error=parsed.get("error", "unknown"),
                execution_time=sandbox_response.get("execution_time", 0.0),
                sandbox_id=sandbox_response.get("sandbox_id"),
            )

    async def execute_model(
        self, request: NumPyroSandboxRequest, on_event: Optional[Any] = None
    ) -> NumPyroSandboxResult:
        """Create sandbox, run the model code, parse results, and clean up."""
        if not self.daytona:
            logger.error("DaytonaService is not configured in environment")
            return NumPyroSandboxResult(
                request_id=request.request_id, status="error", error="DaytonaService not available"
            )

        start = datetime.now()

        if on_event:
            await on_event({"type": "sandbox_starting", "message": "Creating Daytona sandbox"})

        config = self._create_sandbox_config(request)

        try:
            sandbox = await self.daytona.create_sandbox(config)
            sandbox_id = sandbox.get("sandbox_id") if isinstance(sandbox, dict) else str(sandbox)
            self.active_sandboxes[request.request_id] = sandbox_id

            if on_event:
                await on_event({"type": "sandbox_executing", "message": "Executing model in sandbox"})

            code = self._prepare_execution_code(request)

            response = await self.daytona.execute_code(sandbox_id=sandbox_id, code=code, timeout=request.timeout)

            # The response should contain an "output" key with stdout and execution_time
            result = self._parse_sandbox_output(response, request)
            result.sandbox_id = sandbox_id
            result.execution_time = response.get("execution_time", (datetime.now() - start).total_seconds())

            return result

        except asyncio.TimeoutError:
            logger.exception("Sandbox execution timed out")
            return NumPyroSandboxResult(
                request_id=request.request_id,
                status="timeout",
                error="Execution timed out",
                execution_time=(datetime.now() - start).total_seconds(),
            )

        except Exception as e:
            logger.exception("Error during sandbox execution: %s", e)
            return NumPyroSandboxResult(
                request_id=request.request_id,
                status="error",
                error=str(e),
                execution_time=(datetime.now() - start).total_seconds(),
            )

        finally:
            # Cleanup sandbox
            sid = self.active_sandboxes.pop(request.request_id, None)
            if sid:
                try:
                    await self.daytona.destroy_sandbox(sid)
                except Exception:
                    logger.exception("Failed to destroy sandbox %s", sid)


# Global accessor
_executor: Optional[DaytonaNumPyroExecutor] = None


def get_daytona_numpyro_executor() -> DaytonaNumPyroExecutor:
    global _executor
    if _executor is None:
        _executor = DaytonaNumPyroExecutor()
    return _executor
