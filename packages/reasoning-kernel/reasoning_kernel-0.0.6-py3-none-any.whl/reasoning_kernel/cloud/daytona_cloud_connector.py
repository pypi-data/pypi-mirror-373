"""
Daytona Cloud Connector for Inference Stage

This module provides Daytona Cloud integration for:
- Probabilistic model execution
- NumPyro/JAX computations
- Secure sandbox execution of generated code
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from aiohttp import ClientSession, ClientTimeout

from ..config.cloud_services import get_cloud_config

logger = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Request for code execution in Daytona Cloud"""

    code: str
    language: str = "python"
    requirements: Optional[List[str]] = None
    environment_vars: Optional[Dict[str, str]] = None
    timeout_seconds: Optional[int] = None
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result from Daytona Cloud execution"""

    execution_id: str
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used: Optional[str] = None
    cpu_used: Optional[str] = None
    exit_code: int = 0


@dataclass
class NumPyroInferenceRequest:
    """Request for NumPyro probabilistic inference"""

    model_code: str
    data: Dict[str, Any]
    num_samples: int = 1000
    num_warmup: int = 500
    num_chains: int = 4
    random_seed: Optional[int] = None
    inference_method: str = "MCMC"  # MCMC, SVI, etc.


class DaytonaCloudConnector:
    """Daytona Cloud connector for inference stage operations"""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        cloud = get_cloud_config()
        self.config = cloud.daytona_cloud
        self.api_key = api_key or self.config.api_key
        self.endpoint = endpoint or self.config.api_endpoint
        self.timeout = self.config.timeout_seconds
        self.session: Optional[ClientSession] = None
        self._is_connected = False

    async def connect(self) -> bool:
        """Establish connection to Daytona Cloud"""
        try:
            # Create HTTP session with timeout
            timeout = ClientTimeout(total=self.config.timeout_seconds)

            self.session = ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "reasoning-kernel/1.0",
                },
            )

            # Test connection with health check
            health_check = await self._health_check()
            if health_check:
                self._is_connected = True
                logger.info("Successfully connected to Daytona Cloud")
                return True
            else:
                logger.error("Daytona Cloud health check failed")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to Daytona Cloud: {e}")
            self._is_connected = False
            return False

    async def disconnect(self) -> None:
        """Close Daytona Cloud connection"""
        if self.session:
            await self.session.close()
        self._is_connected = False
        logger.info("Disconnected from Daytona Cloud")

    async def _health_check(self) -> bool:
        """Check if Daytona Cloud is accessible"""
        try:
            if not self.session:
                return False

            async with self.session.get(
                f"{self.config.api_endpoint}/health"
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.warning(f"Daytona Cloud health check failed: {e}")
            return False

    async def execute_code(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute code in Daytona Cloud sandbox"""
        try:
            if not self._is_connected:
                await self.connect()

            execution_id = str(uuid.uuid4())

            # Prepare execution request
            payload = {
                "execution_id": execution_id,
                "code": request.code,
                "language": request.language,
                "requirements": request.requirements or [],
                "environment_vars": request.environment_vars or {},
                "timeout_seconds": request.timeout_seconds
                or self.config.timeout_seconds,
                "memory_limit": request.memory_limit or self.config.memory_limit,
                "cpu_limit": request.cpu_limit or self.config.cpu_limit,
                "python_version": self.config.python_version,
            }

            # Submit execution request
            async with self.session.post(
                f"{self.config.api_endpoint}/execute", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Daytona execution request failed: {error_text}")
                    return ExecutionResult(
                        execution_id=execution_id,
                        success=False,
                        output="",
                        error=f"Request failed with status {response.status}: {error_text}",
                    )

                result_data = await response.json()

                # Poll for completion
                return await self._poll_execution_result(
                    execution_id, result_data.get("poll_url")
                )

        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return ExecutionResult(
                execution_id=execution_id if "execution_id" in locals() else "unknown",
                success=False,
                output="",
                error=str(e),
            )

    async def _poll_execution_result(
        self, execution_id: str, poll_url: Optional[str]
    ) -> ExecutionResult:
        """Poll for execution completion"""
        if not poll_url:
            poll_url = f"{self.config.api_endpoint}/execution/{execution_id}/status"

        start_time = datetime.now()
        timeout = timedelta(seconds=self.config.timeout_seconds)

        while datetime.now() - start_time < timeout:
            try:
                async with self.session.get(poll_url) as response:
                    if response.status != 200:
                        await asyncio.sleep(1)
                        continue

                    result_data = await response.json()
                    status = result_data.get("status")

                    if status == "completed":
                        return ExecutionResult(
                            execution_id=execution_id,
                            success=result_data.get("success", False),
                            output=result_data.get("output", ""),
                            error=result_data.get("error"),
                            execution_time=result_data.get("execution_time", 0.0),
                            memory_used=result_data.get("memory_used"),
                            cpu_used=result_data.get("cpu_used"),
                            exit_code=result_data.get("exit_code", 0),
                        )
                    elif status == "failed":
                        return ExecutionResult(
                            execution_id=execution_id,
                            success=False,
                            output=result_data.get("output", ""),
                            error=result_data.get("error", "Execution failed"),
                            execution_time=result_data.get("execution_time", 0.0),
                            exit_code=result_data.get("exit_code", 1),
                        )

                    # Still running, wait and poll again
                    await asyncio.sleep(2)

            except Exception as e:
                logger.warning(f"Error polling execution status: {e}")
                await asyncio.sleep(1)

        # Timeout reached
        return ExecutionResult(
            execution_id=execution_id,
            success=False,
            output="",
            error="Execution timeout reached",
        )

    async def run_numpyro_inference(
        self, request: NumPyroInferenceRequest
    ) -> ExecutionResult:
        """Run NumPyro probabilistic inference"""
        try:
            # Generate NumPyro execution code
            numpyro_code = self._generate_numpyro_code(request)

            # Prepare execution request
            execution_request = ExecutionRequest(
                code=numpyro_code,
                language="python",
                requirements=[
                    "numpyro",
                    "jax",
                    "jaxlib",
                    "numpy",
                    "scipy",
                    "matplotlib",
                    "arviz",
                ],
                environment_vars={
                    "JAX_PLATFORM_NAME": self.config.jax_platform,
                    "JAX_ENABLE_X64": "True",
                },
                timeout_seconds=self.config.timeout_seconds,
                memory_limit=self.config.memory_limit,
                cpu_limit=self.config.cpu_limit,
            )

            # Execute the inference
            result = await self.execute_code(execution_request)

            logger.info(f"NumPyro inference completed: {result.success}")
            return result

        except Exception as e:
            logger.error(f"NumPyro inference failed: {e}")
            return ExecutionResult(
                execution_id="numpyro-" + str(uuid.uuid4()),
                success=False,
                output="",
                error=str(e),
            )

    def _generate_numpyro_code(self, request: NumPyroInferenceRequest) -> str:
        """Generate NumPyro execution code"""
        code_template = f"""
import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, SVI, Trace_ELBO
import json
import numpy as np

# Set random seed for reproducibility
if {request.random_seed} is not None:
    jax.random.PRNGKey({request.random_seed})

# Data from request
data = {json.dumps(request.data)}

# Model definition
{request.model_code}

# Run inference
def run_inference():
    try:
        if "{request.inference_method}" == "MCMC":
            # MCMC inference
            nuts_kernel = NUTS(model)
            mcmc = MCMC(
                nuts_kernel,
                num_samples={request.num_samples},
                num_warmup={request.num_warmup},
                num_chains={request.num_chains}
            )

            rng_key = jax.random.PRNGKey(42)
            mcmc.run(rng_key, **data)

            # Get samples
            samples = mcmc.get_samples()

            # Convert to serializable format
            results = {{}}
            for key, value in samples.items():
                if isinstance(value, jnp.ndarray):
                    results[key] = value.tolist()
                else:
                    results[key] = value

            # Summary statistics
            summary = {{}}
            for key, value in samples.items():
                if isinstance(value, jnp.ndarray):
                    summary[key] = {{
                        "mean": float(jnp.mean(value)),
                        "std": float(jnp.std(value)),
                        "quantiles": {{
                            "5%": float(jnp.percentile(value, 5)),
                            "25%": float(jnp.percentile(value, 25)),
                            "50%": float(jnp.percentile(value, 50)),
                            "75%": float(jnp.percentile(value, 75)),
                            "95%": float(jnp.percentile(value, 95))
                        }}
                    }}

            return {{
                "samples": results,
                "summary": summary,
                "num_samples": {request.num_samples},
                "num_chains": {request.num_chains},
                "inference_method": "{request.inference_method}"
            }}

        else:
            raise ValueError(f"Unsupported inference method: {request.inference_method}")

    except Exception as e:
        return {{"error": str(e)}}

# Execute inference
result = run_inference()
print(json.dumps(result, indent=2))
"""
        return code_template


# Global connector instance
_daytona_connector: Optional[DaytonaCloudConnector] = None


async def get_daytona_connector() -> DaytonaCloudConnector:
    """Get the global Daytona Cloud connector"""
    global _daytona_connector
    if _daytona_connector is None:
        _daytona_connector = DaytonaCloudConnector()
        await _daytona_connector.connect()
    return _daytona_connector


async def close_daytona_connector() -> None:
    """Close the global Daytona Cloud connector"""
    global _daytona_connector
    if _daytona_connector:
        await _daytona_connector.disconnect()
        _daytona_connector = None
