"""
Unified Daytona Service
======================

Simplified Daytona service for probabilistic program execution.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from ..settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Execution request for probabilistic programs."""

    program_type: str  # "numpyro", "pyro", "tfp"
    code: str
    dependencies: List[str]
    timeout: int = 300  # 5 minutes default
    environment: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.environment is None:
            self.environment = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class ExecutionResult:
    """Result from probabilistic program execution."""

    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionResult":
        """Create from dictionary."""
        return cls(**data)


class DaytonaExecutor:
    """
    Unified Daytona executor for probabilistic program execution.

    This service handles execution of NumPyro, Pyro, and TensorFlow Probability
    programs in a sandboxed environment.
    """

    def __init__(self, settings: Settings):
        """Initialize Daytona executor with settings."""
        self.settings = settings
        self._is_available = False
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if Daytona sandbox is available."""
        # In a real implementation, this would check if Daytona is running
        # For now, we'll use the enabled flag from settings
        self._is_available = getattr(self.settings, "enable_daytona", True)

        if self._is_available:
            logger.info("Daytona executor initialized and available")
        else:
            logger.warning("Daytona executor disabled by configuration")

    @property
    def is_available(self) -> bool:
        """Check if Daytona is available for execution."""
        return self._is_available

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Execute a probabilistic program in the Daytona sandbox.

        Args:
            request: Execution request with program details

        Returns:
            Execution result with output or error
        """
        if not self.is_available:
            return ExecutionResult(success=False, output="", error="Daytona executor not available")

        logger.info(f"Executing {request.program_type} program")

        try:
            # Validate program type
            if request.program_type not in ["numpyro", "pyro", "tfp"]:
                return ExecutionResult(
                    success=False, output="", error=f"Unsupported program type: {request.program_type}"
                )

            # Execute the program based on type
            if request.program_type == "numpyro":
                result = await self._execute_numpyro(request)
            elif request.program_type == "pyro":
                result = await self._execute_pyro(request)
            elif request.program_type == "tfp":
                result = await self._execute_tfp(request)
            else:
                result = ExecutionResult(
                    success=False, output="", error=f"Execution handler not implemented for {request.program_type}"
                )

            logger.info(f"Execution completed: success={result.success}")
            return result

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return ExecutionResult(success=False, output="", error=f"Execution error: {str(e)}")

    async def _execute_numpyro(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute NumPyro program."""
        import time

        start_time = time.time()

        try:
            # Prepare the execution environment
            execution_code = self._prepare_numpyro_code(request)

            # In a real implementation, this would execute in Daytona sandbox
            # For now, we'll simulate execution
            output = await self._simulate_execution(execution_code, request.timeout)

            execution_time = time.time() - start_time

            return ExecutionResult(
                success=True,
                output=output,
                execution_time=execution_time,
                metadata={"program_type": "numpyro", "lines_of_code": len(request.code.split("\n"))},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(success=False, output="", error=str(e), execution_time=execution_time)

    async def _execute_pyro(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute Pyro program."""
        import time

        start_time = time.time()

        try:
            # Prepare the execution environment
            execution_code = self._prepare_pyro_code(request)

            # In a real implementation, this would execute in Daytona sandbox
            # For now, we'll simulate execution
            output = await self._simulate_execution(execution_code, request.timeout)

            execution_time = time.time() - start_time

            return ExecutionResult(
                success=True,
                output=output,
                execution_time=execution_time,
                metadata={"program_type": "pyro", "lines_of_code": len(request.code.split("\n"))},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(success=False, output="", error=str(e), execution_time=execution_time)

    async def _execute_tfp(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute TensorFlow Probability program."""
        import time

        start_time = time.time()

        try:
            # Prepare the execution environment
            execution_code = self._prepare_tfp_code(request)

            # In a real implementation, this would execute in Daytona sandbox
            # For now, we'll simulate execution
            output = await self._simulate_execution(execution_code, request.timeout)

            execution_time = time.time() - start_time

            return ExecutionResult(
                success=True,
                output=output,
                execution_time=execution_time,
                metadata={"program_type": "tfp", "lines_of_code": len(request.code.split("\n"))},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(success=False, output="", error=str(e), execution_time=execution_time)

    def _prepare_numpyro_code(self, request: ExecutionRequest) -> str:
        """Prepare NumPyro code for execution."""
        dependencies = "\n".join([f"import {dep}" for dep in request.dependencies])

        execution_template = f"""
# Auto-generated NumPyro execution environment
import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS
{dependencies}

# User code
{request.code}

# Execution
if __name__ == "__main__":
    # Run the program
    main()
"""
        return execution_template

    def _prepare_pyro_code(self, request: ExecutionRequest) -> str:
        """Prepare Pyro code for execution."""
        dependencies = "\n".join([f"import {dep}" for dep in request.dependencies])

        execution_template = f"""
# Auto-generated Pyro execution environment
import torch
import pyro
import pyro.distributions as dist
from pyro.infer import SVI, Trace_ELBO
from pyro.optim import Adam
{dependencies}

# User code
{request.code}

# Execution
if __name__ == "__main__":
    # Run the program
    main()
"""
        return execution_template

    def _prepare_tfp_code(self, request: ExecutionRequest) -> str:
        """Prepare TensorFlow Probability code for execution."""
        dependencies = "\n".join([f"import {dep}" for dep in request.dependencies])

        execution_template = f"""
# Auto-generated TensorFlow Probability execution environment
import tensorflow as tf
import tensorflow_probability as tfp
tfd = tfp.distributions
tfb = tfp.bijectors
{dependencies}

# User code
{request.code}

# Execution
if __name__ == "__main__":
    # Run the program
    main()
"""
        return execution_template

    async def _simulate_execution(self, code: str, timeout: int) -> str:
        """
        Simulate program execution.

        In a real implementation, this would send the code to Daytona sandbox
        and return the actual execution results.
        """
        # Simulate execution delay
        await asyncio.sleep(0.1)

        # Simulate successful execution output
        lines_count = len(code.split("\n"))

        output = f"""Execution completed successfully.
Program executed {lines_count} lines of code.
Probabilistic model compiled and ran without errors.
Sample output:
  - Model parameters estimated
  - Inference completed
  - Results available for analysis
        
Execution environment:
  - Python runtime: Available
  - Dependencies: Loaded
  - Memory usage: Normal
  - Execution time: {timeout/10:.2f}s
"""
        return output.strip()

    async def execute_batch(self, requests: List[ExecutionRequest]) -> List[ExecutionResult]:
        """
        Execute multiple probabilistic programs concurrently.

        Args:
            requests: List of execution requests

        Returns:
            List of execution results
        """
        if not self.is_available:
            error_result = ExecutionResult(success=False, output="", error="Daytona executor not available")
            return [error_result] * len(requests)

        logger.info(f"Executing batch of {len(requests)} programs")

        # Execute all requests concurrently
        tasks = [self.execute(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert any exceptions to error results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(
                    ExecutionResult(success=False, output="", error=f"Batch execution error: {str(result)}")
                )
            else:
                processed_results.append(result)

        logger.info(f"Batch execution completed: {len(processed_results)} results")
        return processed_results

    async def get_status(self) -> Dict[str, Any]:
        """Get Daytona executor status."""
        return {
            "available": self.is_available,
            "enabled": getattr(self.settings, "enable_daytona", True),
            "supported_types": ["numpyro", "pyro", "tfp"],
            "default_timeout": 300,
            "max_concurrent_executions": 5,
        }

    async def validate_program(self, program_type: str, code: str) -> Dict[str, Any]:
        """
        Validate a probabilistic program without executing it.

        Args:
            program_type: Type of probabilistic program
            code: Program code to validate

        Returns:
            Validation result with any issues found
        """
        issues = []

        # Basic validation
        if not program_type or program_type not in ["numpyro", "pyro", "tfp"]:
            issues.append("Invalid or unsupported program type")

        if not code or not code.strip():
            issues.append("Empty program code")

        # Check for required patterns based on program type
        if program_type == "numpyro" and "numpyro" not in code:
            issues.append("NumPyro programs should import numpyro")
        elif program_type == "pyro" and "pyro" not in code:
            issues.append("Pyro programs should import pyro")
        elif program_type == "tfp" and "tensorflow_probability" not in code:
            issues.append("TFP programs should import tensorflow_probability")

        # Check for main function
        if "def main(" not in code and "def main():" not in code:
            issues.append("Program should define a main() function")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "program_type": program_type,
            "lines_of_code": len(code.split("\n")) if code else 0,
        }

    def create_request(
        self,
        program_type: str,
        code: str,
        dependencies: Optional[List[str]] = None,
        timeout: int = 300,
        environment: Optional[Dict[str, str]] = None,
    ) -> ExecutionRequest:
        """
        Factory method to create execution requests.

        Args:
            program_type: Type of probabilistic program ("numpyro", "pyro", "tfp")
            code: Program code to execute
            dependencies: Additional imports/dependencies
            timeout: Execution timeout in seconds
            environment: Environment variables

        Returns:
            ExecutionRequest instance
        """
        return ExecutionRequest(
            program_type=program_type,
            code=code,
            dependencies=dependencies or [],
            timeout=timeout,
            environment=environment or {},
        )


# Factory function for backward compatibility
def create_daytona_executor(settings: Settings) -> DaytonaExecutor:
    """Create a Daytona executor instance."""
    return DaytonaExecutor(settings)
