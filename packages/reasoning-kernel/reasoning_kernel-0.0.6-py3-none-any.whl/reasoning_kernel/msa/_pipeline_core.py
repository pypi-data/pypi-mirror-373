"""MSA Pipeline primitives used by tests.

Provides a simple 5-stage pipeline with retries, timeout handling, and basic metrics.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional
from enum import Enum

from .stage_manager import MSAStageInput, MSAStageManager, MSAStageResult


# Add compatibility symbols expected by tests
class PipelineStage(Enum):
    """Pipeline stages for MSA processing."""

    PARSE = "parse"
    KNOWLEDGE = "knowledge"
    GRAPH = "graph"
    SYNTHESIS = "synthesis"
    INFERENCE = "inference"
    PROGRAM = "program"  # New stage for PPL generation
    EXECUTION = "execution"  # New stage for PPL execution


class StageResult:
    """Result from executing a pipeline stage."""

    def __init__(
        self, stage: str, success: bool, data: Dict[str, Any] = None, execution_time: float = 0.0, error: str = None
    ):
        self.stage = stage
        self.success = success
        self.data = data or {}
        self.execution_time = execution_time
        self.error = error


class PipelineExecutionResult:
    """Result from executing an entire pipeline."""

    def __init__(
        self,
        success: bool,
        stages: Dict[str, StageResult] = None,
        total_time: float = 0.0,
        metadata: Dict[str, Any] = None,
    ):
        self.success = success
        self.stages = stages or {}
        self.total_time = total_time
        self.metadata = metadata or {}


@dataclass
class MSAPipelineConfig:
    enable_caching: bool = True
    enable_parallel_stages: bool = False
    timeout_seconds: float = 300.0
    retry_attempts: int = 0
    enhanced_mode: bool = False
    verbose_logging: bool = False


@dataclass
class MSAPipelineResult:
    success: bool
    session_id: str
    stage_results: Dict[str, MSAStageResult] = field(default_factory=dict)
    total_execution_time: float = 0.0
    final_insights: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MSAPipeline:
    """A minimal but functional MSA pipeline for tests.

    Executes the following stages in order: parse, knowledge, graph, synthesis, inference.
    """

    def __init__(self, config: Optional[MSAPipelineConfig] = None) -> None:
        self.config = config or MSAPipelineConfig()
        self.stage_manager = MSAStageManager()
        self._execution_history: List[MSAPipelineResult] = []

    async def _execute_with_retries(self, stage: str, stage_input: MSAStageInput) -> MSAStageResult:
        attempts = max(1, int(self.config.retry_attempts) + 1)
        last_exc: Optional[Exception] = None
        for _ in range(attempts):
            try:
                return await self.stage_manager.execute_stage(stage, stage_input)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                await asyncio.sleep(0)
        # If plugin raised exceptions all attempts, return failure result
        return MSAStageResult(
            stage_name=stage,
            success=False,
            data={},
            insights=[],
            confidence_score=0.0,
            processing_time=0.0,
            metadata={},
            error=str(last_exc) if last_exc else "Execution failed",
        )

    async def execute(
        self,
        scenario: str,
        session_id: str,
        previous_results: Optional[Mapping[str, Any]] = None,
    ) -> MSAPipelineResult:
        start_time = time.perf_counter()
        stages = ["parse", "knowledge", "graph", "synthesis", "inference"]
        stage_results: Dict[str, MSAStageResult] = {}

        # Build initial previous results
        prev: Mapping[str, Any] = previous_results or {}

        for idx, stage in enumerate(stages):
            # Merge real previous stage results into a dict of stage -> data
            accumulated: Dict[str, Any] = {}
            for s, res in stage_results.items():
                accumulated[s] = res.data
            # Include external previous_results only for first stage
            if idx == 0 and prev:
                accumulated.update(prev)

            stage_input = MSAStageInput(
                scenario=scenario,
                previous_results=accumulated,
                session_id=session_id,
                enhanced_mode=self.config.enhanced_mode,
                verbose=self.config.verbose_logging,
            )

            # Execute with retries and optional timeout
            try:
                if self.config.timeout_seconds and self.config.timeout_seconds > 0:
                    result = await asyncio.wait_for(
                        self._execute_with_retries(stage, stage_input),
                        timeout=self.config.timeout_seconds,
                    )
                else:
                    result = await self._execute_with_retries(stage, stage_input)
            except asyncio.TimeoutError:
                # Timeout handling: record failure and continue
                result = MSAStageResult(
                    stage_name=stage,
                    success=False,
                    data={},
                    insights=[],
                    confidence_score=0.0,
                    processing_time=self.config.timeout_seconds or 0.0,
                    metadata={"timeout": True},
                    error="Stage execution timed out",
                )

            stage_results[stage] = result

        # Aggregate result
        total_time = time.perf_counter() - start_time
        success = all(r.success for r in stage_results.values())
        # Simple confidence heuristic: average of stage confidences
        confidences = [max(0.0, min(1.0, r.confidence_score)) for r in stage_results.values()]
        confidence = sum(confidences) / len(confidences) if confidences else 0.0

        final_insights: List[str] = []
        for r in stage_results.values():
            final_insights.extend(r.insights)

        result = MSAPipelineResult(
            success=success,
            session_id=session_id,
            stage_results=stage_results,
            total_execution_time=total_time,
            final_insights=final_insights,
            confidence_score=confidence,
            metadata={"stages_executed": stages},
        )

        # Track history for tests
        self._execution_history.append(result)
        return result
