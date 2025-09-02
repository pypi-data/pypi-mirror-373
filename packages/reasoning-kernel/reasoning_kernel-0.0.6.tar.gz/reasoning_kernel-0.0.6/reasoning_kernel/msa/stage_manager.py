"""MSA Stage Manager primitives used by tests.

Implements minimal but functional stage registration/execution, plus simple result types.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Tuple

from reasoning_kernel.core.exceptions import MSAError


@dataclass(frozen=True)
class MSAStageInput:
    """Immutable input to a stage execution.

    previous_results is stored as a tuple for hashability and test expectations.
    """

    scenario: str
    previous_results: Tuple[Tuple[str, Any], ...]
    session_id: str
    enhanced_mode: bool = False
    verbose: bool = False

    def __init__(
        self,
        scenario: str,
        previous_results: Mapping[str, Any]
        | MutableMapping[str, Any]
        | Tuple[Tuple[str, Any], ...],
        session_id: str,
        enhanced_mode: bool = False,
        verbose: bool = False,
    ) -> None:
        object.__setattr__(self, "scenario", scenario)
        if isinstance(previous_results, tuple):
            pr: Tuple[Tuple[str, Any], ...] = previous_results
        else:
            pr = tuple(sorted(previous_results.items()))
        object.__setattr__(self, "previous_results", pr)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "enhanced_mode", enhanced_mode)
        object.__setattr__(self, "verbose", verbose)


@dataclass
class MSAStageResult:
    """Result returned by a stage plugin execution."""

    stage_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    # Compatibility aliases used by some assertions in tests
    @property
    def stage(self) -> str:  # pragma: no cover - simple alias
        return self.stage_name

    @property
    def execution_time(self) -> float:  # pragma: no cover - simple alias
        return self.processing_time


class MSAStageManager:
    """Registers and executes stage plugins."""

    def __init__(self) -> None:
        self.plugins: Dict[str, Any] = {}
        self.stage_registry: List[str] = []

    def register_plugin(self, stage_name: str, plugin: Any) -> None:
        self.plugins[stage_name] = plugin
        if stage_name not in self.stage_registry:
            self.stage_registry.append(stage_name)

    def unregister_plugin(self, stage_name: str) -> None:
        self.plugins.pop(stage_name, None)
        if stage_name in self.stage_registry:
            self.stage_registry.remove(stage_name)

    def get_registered_stages(self) -> List[str]:
        return list(self.stage_registry)

    def is_stage_registered(self, stage_name: str) -> bool:
        return stage_name in self.plugins

    def get_all_capabilities(self) -> Dict[str, List[str]]:
        caps: Dict[str, List[str]] = {}
        for name, plugin in self.plugins.items():
            try:
                capabilities = plugin.get_capabilities()
            except Exception:
                capabilities = []
            caps[name] = capabilities or []
        return caps

    async def execute_stage(
        self, stage_name: str, stage_input: MSAStageInput
    ) -> MSAStageResult:
        if stage_name not in self.plugins:
            raise MSAError(f"Stage '{stage_name}' is not registered")

        plugin = self.plugins[stage_name]
        start = time.perf_counter()
        try:
            # Optional validation
            is_valid = True
            if hasattr(plugin, "validate_input"):
                is_valid = bool(plugin.validate_input(stage_input))
            if not is_valid:
                elapsed = time.perf_counter() - start
                return MSAStageResult(
                    stage_name=stage_name,
                    success=False,
                    data={},
                    insights=[],
                    confidence_score=0.0,
                    processing_time=elapsed,
                    metadata={"validated": False},
                    error="Input validation failed",
                )

            # Execute
            result: MSAStageResult = await plugin.execute(stage_input)
            # Ensure timing populated
            elapsed = time.perf_counter() - start
            if result.processing_time == 0.0:
                result.processing_time = elapsed
            return result
        except Exception as exc:  # noqa: BLE001 - broadened for test safety
            elapsed = time.perf_counter() - start
            return MSAStageResult(
                stage_name=stage_name,
                success=False,
                data={},
                insights=[],
                confidence_score=0.0,
                processing_time=elapsed,
                metadata={},
                error=str(exc),
            )
