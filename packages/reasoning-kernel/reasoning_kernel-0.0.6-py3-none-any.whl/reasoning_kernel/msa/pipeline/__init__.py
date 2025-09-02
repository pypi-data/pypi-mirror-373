"""Nested pipeline package for compatibility with tests.

This provides imports like `reasoning_kernel.msa.pipeline.msa_pipeline`.
"""

from .._pipeline_core import MSAPipeline, MSAPipelineConfig, MSAPipelineResult  # noqa: F401

__all__ = ["MSAPipeline", "MSAPipelineConfig", "MSAPipelineResult"]
