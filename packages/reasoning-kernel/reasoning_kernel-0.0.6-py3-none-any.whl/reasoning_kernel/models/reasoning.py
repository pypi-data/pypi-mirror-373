"""
Reasoning Models
===============

Core models for reasoning results and pipeline data.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ReasoningResult:
    """Result from the reasoning pipeline"""

    success: bool
    session_id: str
    scenario: str
    final_conclusion: Optional[str] = None
    confidence_score: float = 0.0
    key_insights: List[str] = None
    stage_results: List[Dict[str, Any]] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.key_insights is None:
            self.key_insights = []
        if self.stage_results is None:
            self.stage_results = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "session_id": self.session_id,
            "scenario": self.scenario,
            "final_conclusion": self.final_conclusion,
            "confidence_score": self.confidence_score,
            "key_insights": self.key_insights,
            "stage_results": self.stage_results,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class StageResult:
    """Result from a single MSA stage"""

    stage_name: str
    success: bool
    data: Dict[str, Any]
    insights: List[str]
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "stage_name": self.stage_name,
            "success": self.success,
            "data": self.data,
            "insights": self.insights,
            "confidence_score": self.confidence_score,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
        }


@dataclass
class PipelineConfig:
    """Configuration for the reasoning pipeline"""

    enable_parallel_stages: bool = False
    confidence_threshold: float = 0.7
    max_processing_time: int = 300
    enable_caching: bool = True
    debug_mode: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enable_parallel_stages": self.enable_parallel_stages,
            "confidence_threshold": self.confidence_threshold,
            "max_processing_time": self.max_processing_time,
            "enable_caching": self.enable_caching,
            "debug_mode": self.debug_mode,
        }
