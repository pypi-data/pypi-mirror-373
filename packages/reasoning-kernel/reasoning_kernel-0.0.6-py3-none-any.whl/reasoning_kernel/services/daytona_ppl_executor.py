"""
Enhanced Daytona service for probabilistic program execution (PPL).

This module extends the existing DaytonaService with specialized capabilities
for secure execution of probabilistic programs in sandboxed environments.
"""

import asyncio
import ast
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
import json
import logging
import time
from typing import Any, Dict, List, Optional

from .daytona_service import DaytonaSandboxError
from .daytona_service import DaytonaService
from .daytona_service import DaytonaServiceError
from .daytona_service import DaytonaTimeoutError
from .daytona_service import ExecutionResult
from .daytona_service import RetryConfig
from .daytona_service import SandboxConfig
from .daytona_service import SandboxStatus


logger = logging.getLogger(__name__)


class PPLFramework(Enum):
    """Supported probabilistic programming frameworks"""

    NUMPYRO = "numpyro"
    PYRO = "pyro"
    TENSORFLOW_PROBABILITY = "tfp"
    STAN = "stan"


class PPLExecutionError(Exception):
    """Raised when PPL execution fails in a non-Daytona specific way."""


@dataclass
class PPLExecutionConfig:
    """Configuration for PPL execution environment"""

    framework: PPLFramework = PPLFramework.NUMPYRO
    max_execution_time: float = 300.0  # 5 minutes default
    memory_limit_mb: int = 2048  # 2GB memory limit
    cpu_limit: float = 2.0  # 2 CPU cores
    enable_gpu: bool = False
    python_version: str = "3.10"
    required_packages: List[str] = field(
        default_factory=lambda: ["numpy>=1.21.0", "jax>=0.4.0", "numpyro>=0.13.0", "arviz>=0.16.0", "matplotlib>=3.5.0"]
    )
    environment_vars: Dict[str, str] = field(default_factory=dict)
    workspace_cleanup: bool = True


@dataclass
class PPLProgram:
    """Represents a probabilistic program to be executed"""

    code: str
    framework: PPLFramework
    entry_point: str = "main"
    input_data: Optional[Dict[str, Any]] = None
    validation_rules: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)


@dataclass
class PPLExecutionResult(ExecutionResult):
    """Extended execution result for PPL programs"""

    inference_results: Optional[Dict[str, Any]] = None
    posterior_samples: Optional[Dict[str, Any]] = None
    convergence_diagnostics: Optional[Dict[str, float]] = None
    execution_metadata: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = field(default_factory=list)

    @classmethod
    def from_base_result(
        cls,
        base_result: ExecutionResult,
        inference_results: Optional[Dict[str, Any]] = None,
        posterior_samples: Optional[Dict[str, Any]] = None,
        convergence_diagnostics: Optional[Dict[str, float]] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        validation_errors: Optional[List[str]] = None,
    ) -> "PPLExecutionResult":
        """Create PPLExecutionResult from base ExecutionResult"""
        return cls(
            exit_code=base_result.exit_code,
            stdout=base_result.stdout,
            stderr=base_result.stderr,
            execution_time=base_result.execution_time,
            status=base_result.status,
            resource_usage=base_result.resource_usage,
            metadata=base_result.metadata,
            inference_results=inference_results,
            posterior_samples=posterior_samples,
            convergence_diagnostics=convergence_diagnostics,
            execution_metadata=execution_metadata,
            validation_errors=validation_errors or [],
        )


class DaytonaPPLExecutor:
    """
    Specialized executor for probabilistic programs in Daytona sandboxes.

    Provides secure execution of PPL code with proper validation, timeout handling,
    and result extraction for MSA pipeline integration.
    """

    def __init__(
        self,
        daytona_service: Optional[DaytonaService] = None,
        ppl_config: Optional[PPLExecutionConfig] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """Initialize PPL executor with Daytona service and configuration"""
        # Initialize base Daytona service if not provided
        if daytona_service is None:
            sandbox_config = SandboxConfig(
                cpu_limit=int(ppl_config.cpu_limit) if ppl_config else 2,
                memory_limit_mb=ppl_config.memory_limit_mb if ppl_config else 2048,
                execution_timeout=int(ppl_config.max_execution_time) if ppl_config else 300,
                enable_networking=False,
                python_version=ppl_config.python_version if ppl_config else "3.10",
            )
            self.daytona_service = DaytonaService(config=sandbox_config)
        else:
            self.daytona_service = daytona_service

        self.ppl_config = ppl_config or PPLExecutionConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def validate_ppl_program(self, program: PPLProgram) -> List[str]:
        """
        Validate PPL program for security and correctness.

        Args:
            program: PPL program to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        validation_errors = []

        try:
            # Basic syntax validation using ast parsing (safer than compile)
            try:
                import ast

                ast.parse(program.code)
            except SyntaxError as e:
                validation_errors.append(f"Syntax error: {e}")

            # Security validation - check for dangerous imports/operations
            dangerous_patterns = [
                "import os",
                "import subprocess",
                "import sys",
                "from os import",
                "from subprocess import",
                "__import__",
                "eval(",
                "exec(",
                "open(",
                "file(",
                "input(",
                "raw_input(",
            ]

            code_lower = program.code.lower()
            for pattern in dangerous_patterns:
                if pattern in code_lower:
                    validation_errors.append(f"Potentially dangerous operation detected: {pattern}")

            # Framework-specific validation
            if program.framework == PPLFramework.NUMPYRO:
                if "import numpyro" not in program.code and "from numpyro" not in program.code:
                    validation_errors.append("NumPyro program must import numpyro")

            # Entry point existence is optional: the execution wrapper checks for it at runtime
            # and will skip invocation if not defined. We avoid hard-failing validation here to
            # support simple scripts that just run top-level code.

            # Custom validation rules
            for rule in program.validation_rules:
                if rule not in program.code:
                    validation_errors.append(f"Validation rule failed: {rule}")

        except Exception as e:
            validation_errors.append(f"Validation error: {str(e)}")

        return validation_errors

    async def prepare_execution_environment(self, program: PPLProgram) -> Dict[str, str]:
        """
        Prepare the execution environment for PPL program.

        Args:
            program: PPL program to prepare environment for

        Returns:
            Dictionary of environment setup commands
        """
        setup_commands = {}

        try:
            # Base Python environment setup
            setup_commands["python_setup"] = f"python{self.ppl_config.python_version} -m pip install --upgrade pip"

            # Install required packages
            packages = " ".join(self.ppl_config.required_packages)
            setup_commands["package_install"] = f"python{self.ppl_config.python_version} -m pip install {packages}"

            # Framework-specific setup
            if program.framework == PPLFramework.NUMPYRO:
                setup_commands["jax_setup"] = "python -c 'import jax; print(jax.default_backend())'"

            # Set environment variables
            for key, value in self.ppl_config.environment_vars.items():
                setup_commands[f"env_{key}"] = f"export {key}='{value}'"

        except Exception as e:
            self.logger.error(f"Error preparing execution environment: {e}")
            raise DaytonaServiceError(f"Environment preparation failed: {e}")

        return setup_commands

    async def execute_ppl_program(self, program: PPLProgram, _: bool = False) -> PPLExecutionResult:
        """
        Execute probabilistic program in secure Daytona sandbox.

        Args:
            program: PPL program to execute
            _: Use current sandbox if available (not implemented)

        Returns:
            PPL execution result with inference data
        """
        start_time = time.time()

        try:
            # Validate program first
            self.logger.info(f"Validating PPL program with framework {program.framework.value}")
            validation_errors = await self.validate_ppl_program(program)

            if validation_errors:
                return PPLExecutionResult(
                    exit_code=1,
                    stdout="",
                    stderr="Program validation failed",
                    execution_time=time.time() - start_time,
                    status=SandboxStatus.FAILED,
                    resource_usage={},
                    metadata={"validation_errors": validation_errors},
                    validation_errors=validation_errors,
                )

            # Ensure a Daytona sandbox exists when service is available
            try:
                if getattr(self.daytona_service, "is_available", lambda: False)():
                    # Create sandbox if none exists yet
                    if not getattr(self.daytona_service, "current_sandbox", None):
                        self.logger.info("No active Daytona sandbox - creating one now")
                        try:
                            await self.daytona_service.create_sandbox()
                        except Exception as e:
                            # Don't hard fail here; allow fallback paths to handle execution
                            self.logger.warning(
                                f"Failed to create Daytona sandbox, execution may fallback locally: {e}"
                            )
            except Exception as e:
                # Defensive: sandbox creation shouldn't prevent overall execution attempt
                self.logger.warning(f"Sandbox pre-check error (continuing): {e}")

            # Prepare execution environment
            self.logger.info("Preparing PPL execution environment")
            setup_commands = await self.prepare_execution_environment(program)

            # Setup environment in sandbox (run only Python-valid commands)
            for command_name, command in setup_commands.items():
                try:
                    # Execute only if it's valid Python code (skip shell-like commands)
                    ast.parse(command)
                except Exception:
                    self.logger.debug(f"Skipping non-Python setup command {command_name}: {command}")
                    continue

                self.logger.debug(f"Running setup command {command_name}: {command}")
                setup_result = await self.daytona_service.execute_code(code=command, timeout=60)

                if setup_result.exit_code != 0:
                    return PPLExecutionResult.from_base_result(
                        setup_result,
                        validation_errors=[f"Environment setup failed at {command_name}: {setup_result.stderr}"],
                    )

            # Create execution wrapper script
            execution_script = self._create_execution_wrapper(program)

            # Execute PPL program
            self.logger.info("Executing PPL program in sandbox")
            execution_result = await self.daytona_service.execute_code(
                code=execution_script, timeout=int(self.ppl_config.max_execution_time)
            )

            # Parse PPL-specific results
            ppl_result = self._parse_ppl_results(execution_result)

            return ppl_result

        except Exception as e:
            self.logger.error(f"PPL execution failed: {e}")

            if isinstance(e, (DaytonaServiceError, DaytonaSandboxError, DaytonaTimeoutError)):
                raise
            else:
                # Create error result
                return PPLExecutionResult(
                    exit_code=1,
                    stdout="",
                    stderr=str(e),
                    execution_time=time.time() - start_time,
                    status=SandboxStatus.FAILED,
                    resource_usage={},
                    metadata={"error": str(e)},
                    validation_errors=[str(e)],
                )

    def _create_execution_wrapper(self, program: PPLProgram) -> str:
        """Create Python wrapper script for PPL execution"""

        wrapper_template = """
import json
import traceback
import time
import sys
from typing import Any, Dict, Optional

# Execution metadata
execution_metadata = {{
    "start_time": time.time(),
    "framework": "{framework}",
    "entry_point": "{entry_point}"
}}

try:
    # User PPL code
    {user_code}
    
    # Execute entry point if specified
    if "{entry_point}" != "main":
        if "{entry_point}" in globals():
            result = globals()["{entry_point}"]({input_data})
        else:
            raise ValueError(f"Entry point '{entry_point}' not found")
    else:
        result = main({input_data}) if "main" in globals() else None
    
    # Capture execution metadata
    execution_metadata["end_time"] = time.time()
    execution_metadata["execution_time"] = execution_metadata["end_time"] - execution_metadata["start_time"]
    execution_metadata["success"] = True
    
    # Output results in structured format
    output = {{
        "success": True,
        "result": result,
        "execution_metadata": execution_metadata
    }}
    
    print("PPL_RESULT_START")
    print(json.dumps(output, default=str))
    print("PPL_RESULT_END")
    
except Exception as e:
    execution_metadata["end_time"] = time.time() 
    execution_metadata["execution_time"] = execution_metadata["end_time"] - execution_metadata["start_time"]
    execution_metadata["success"] = False
    execution_metadata["error"] = str(e)
    execution_metadata["traceback"] = traceback.format_exc()
    
    error_output = {{
        "success": False,
        "error": str(e),
        "traceback": traceback.format_exc(),
        "execution_metadata": execution_metadata
    }}
    
    print("PPL_RESULT_START")
    print(json.dumps(error_output, default=str))
    print("PPL_RESULT_END")
    
    sys.exit(1)
"""

        # Indent user code to be inside the try block
        indented_user_code = program.code.replace("\n", "\n    ")

        return wrapper_template.format(
            framework=program.framework.value,
            entry_point=program.entry_point,
            user_code=indented_user_code,
            input_data=json.dumps(program.input_data) if program.input_data else "None",
        )

    def _parse_ppl_results(self, execution_result: ExecutionResult) -> PPLExecutionResult:
        """Parse PPL-specific results from execution output"""

        try:
            # Extract structured results from output
            output = execution_result.stdout

            # Look for structured result markers
            start_marker = "PPL_RESULT_START"
            end_marker = "PPL_RESULT_END"

            if start_marker in output and end_marker in output:
                start_idx = output.find(start_marker) + len(start_marker)
                end_idx = output.find(end_marker)
                result_json = output[start_idx:end_idx].strip()

                try:
                    parsed_result = json.loads(result_json)

                    return PPLExecutionResult.from_base_result(
                        execution_result,
                        inference_results=parsed_result.get("result"),
                        execution_metadata=parsed_result.get("execution_metadata"),
                        validation_errors=[],
                    )

                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse PPL results JSON: {e}")

            # Fallback to basic execution result
            return PPLExecutionResult.from_base_result(execution_result, validation_errors=[])

        except Exception as e:
            self.logger.error(f"Error parsing PPL results: {e}")
            return PPLExecutionResult.from_base_result(
                execution_result, validation_errors=[f"Result parsing failed: {str(e)}"]
            )

    async def batch_execute_programs(
        self, programs: List[PPLProgram], max_concurrent: int = 3
    ) -> List[PPLExecutionResult]:
        """
        Execute multiple PPL programs concurrently with rate limiting.

        Args:
            programs: List of PPL programs to execute
            max_concurrent: Maximum concurrent executions

        Returns:
            List of execution results in same order as input
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(program: PPLProgram) -> PPLExecutionResult:
            async with semaphore:
                return await self.execute_ppl_program(program)

        # Use enhanced async patterns for better performance
        from ..core.async_utils import smart_gather

        tasks = [execute_with_semaphore(program) for program in programs]
        results = await smart_gather(*tasks, max_concurrency=max_concurrent, timeout=600.0)

        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    PPLExecutionResult(
                        exit_code=1,
                        stdout="",
                        stderr=f"Execution failed: {str(result)}",
                        execution_time=0.0,
                        status=SandboxStatus.FAILED,
                        resource_usage={},
                        metadata={"error": str(result)},
                        validation_errors=[str(result)],
                    )
                )
            else:
                processed_results.append(result)

        return processed_results
