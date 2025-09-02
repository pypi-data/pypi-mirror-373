"""MSA module exports.

Provides pipeline and stage manager primitives expected by tests.
"""

from ._pipeline_core import MSAPipeline, MSAPipelineConfig, MSAPipelineResult  # noqa: F401
from .stage_manager import MSAStageInput, MSAStageManager, MSAStageResult  # noqa: F401

__all__ = [
    "MSAPipeline",
    "MSAPipelineConfig",
    "MSAPipelineResult",
    "MSAStageManager",
    "MSAStageInput",
    "MSAStageResult",
]
