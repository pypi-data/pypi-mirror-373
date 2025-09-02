"""
Unified Orchestrator (minimal implementation)
=============================================

Provides OrchestratorConfig and UnifiedOrchestrator used by the CLI and tests.
This keeps semantics light: initialize optional KernelManager and execute a
simple flow returning a well-structured dict so the CLI can render output.

Note: This module is maintained for backward compatibility with legacy imports
(`reasoning_kernel.orchestrator`). New code should prefer the SK 1.36-based
implementation in `reasoning_kernel.sk_core.sk_orchestrator`.
"""

from __future__ import annotations

import time
import warnings as _warnings
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .core.exceptions import MSAError
from .core.kernel_manager import KernelManager, KernelManagerConfig
from .core.logging_config import get_logger

logger = get_logger(__name__)

# Emit a one-time deprecation warning on import to guide migration
_warnings.warn(
    "reasoning_kernel.orchestrator is kept for compatibility; prefer"
    " reasoning_kernel.sk_core.sk_orchestrator in new code.",
    DeprecationWarning,
    stacklevel=2,
)


@dataclass
class OrchestratorConfig:
    enable_semantic_kernel: bool = False
    enable_cloud_services: bool = False
    enable_caching: bool = False
    enable_performance_monitoring: bool = False
    msa_config: Any = None  # placeholder; tests pass an object with timeout_seconds


@dataclass
class UnifiedOrchestrator:
    config: OrchestratorConfig
    kernel_manager: Optional[KernelManager] = field(default=None, init=False)
    _initialized: bool = field(default=False, init=False)

    async def initialize(self) -> bool:
        if self._initialized:
            return True
        try:
            if self.config.enable_semantic_kernel:
                self.kernel_manager = KernelManager(
                    KernelManagerConfig(enable_semantic_kernel=True)
                )
            else:
                self.kernel_manager = KernelManager()

            # Initialize kernel manager; ignore errors if SK disabled
            ok = await self.kernel_manager.initialize()
            self._initialized = bool(ok)
            return self._initialized
        except Exception as e:
            logger.error(f"Orchestrator initialization failed: {e}")
            self._initialized = False
            return False

    async def execute_reasoning(
        self,
        scenario: str,
        session_id: Optional[str] = None,
        mode: str = "msa",
        **kwargs,
    ) -> Dict[str, Any]:
        if not self._initialized:
            ok = await self.initialize()
            if not ok:
                raise MSAError("Failed to initialize orchestrator")

        start = time.time()

        try:
            if mode not in {"msa", "semantic_kernel", "hybrid"}:
                raise MSAError(f"Unsupported mode: {mode}")

            sk_result = None
            if mode == "semantic_kernel" or mode == "hybrid":
                # Use kernel manager for a minimal call
                kernel = (
                    self.kernel_manager.get_kernel() if self.kernel_manager else None
                )
                if kernel is not None:
                    sk_result = await kernel.invoke_function(
                        "reasoning", "analyze", input=scenario, **kwargs
                    )

            # For now, produce a basic response structure that tests/CLI expect
            execution_time = time.time() - start

            result: Dict[str, Any] = {
                "success": True,
                "mode": mode,
                "session_id": session_id or "session-unknown",
                "execution_time": execution_time,
                "confidence_score": 0.5,
            }
            # Include insights for CLI pretty output
            result["insights"] = [
                f"Processed: {scenario[:120]}" + ("..." if len(scenario) > 120 else ""),
            ]
            if mode in {"semantic_kernel", "hybrid"} and sk_result:
                result.setdefault("metadata", {})["sk"] = sk_result

            return result
        except Exception as e:
            execution_time = time.time() - start
            logger.error(f"Reasoning execution failed: {e}")
            return {
                "success": False,
                "mode": mode,
                "session_id": session_id or "session-unknown",
                "execution_time": execution_time,
                "error": str(e),
            }

    async def get_status(self, session_id: str) -> Dict[str, Any]:
        """Return a minimal status payload. Tests patch this method on a mock.

        Provided here so AsyncMock(spec=UnifiedOrchestrator) exposes this attribute.
        """
        return {
            "status": "unknown",
            "current_stage": None,
            "progress": 0.0,
            "elapsed_time": 0.0,
            "estimated_remaining": None,
        }

    async def cancel_session(self, session_id: str) -> bool:
        """Cancel a reasoning session. Default to True for the stub."""
        return True
