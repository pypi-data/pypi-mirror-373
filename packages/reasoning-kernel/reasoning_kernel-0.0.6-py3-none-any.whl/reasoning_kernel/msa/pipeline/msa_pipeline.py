"""Compatibility module providing MSAPipeline symbols at nested path.

Tests import `reasoning_kernel.msa.pipeline.msa_pipeline` directly.
"""

from .._pipeline_core import (
    MSAPipeline,
    MSAPipelineConfig,
    MSAPipelineResult,
    PipelineStage,
    StageResult,
    PipelineExecutionResult,
)

__all__ = [
    "MSAPipeline",
    "MSAPipelineConfig",
    "MSAPipelineResult",
    "PipelineStage",
    "StageResult",
    "PipelineExecutionResult",
]
