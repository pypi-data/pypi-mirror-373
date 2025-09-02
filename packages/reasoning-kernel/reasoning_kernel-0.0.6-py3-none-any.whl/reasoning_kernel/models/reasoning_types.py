"""
Types for Reasoning Kernel
==========================
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..core import constants
from ..utils.reasoning_chains import ReasoningChain


class ReasoningStage(Enum):
    """Reasoning stages"""

    PARSE = constants.STAGE_PARSE
    RETRIEVE = constants.STAGE_RETRIEVE
    GRAPH = constants.STAGE_GRAPH
    SYNTHESIZE = constants.STAGE_SYNTHESIZE
    INFER = constants.STAGE_INFER


@dataclass
class ReasoningConfig:
    """Configuration for reasoning pipeline"""

    parse_model: str = "gemini-2.5-pro"
    retrieve_top_k: int = 5
    graph_model: str = "gemini-2.5-pro"
    synthesis_model: str = "gemini-2.5-pro"
    inference_samples: int = 1000
    max_retries: int = 3
    fallback_models: Optional[Dict[str, str]] = None
    timeout_per_stage: int = 120
    enable_parallel_processing: bool = True
    enable_thinking_mode: bool = True
    thinking_detail_level: str = "detailed"
    generate_reasoning_sentences: bool = True
    include_step_by_step_thinking: bool = True

    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = {
                "parse": "o4-mini",
                "graph": "o4-mini",
                "synthesis": "o4-mini",
            }


@dataclass
class ReasoningResult:
    """Complete result from five-stage reasoning pipeline"""

    parsed_vignette: Optional[Any] = None
    retrieval_context: Optional[Any] = None
    dependency_graph: Optional[Any] = None
    probabilistic_program: Optional[Any] = None
    inference_result: Optional[Any] = None
    reasoning_chain: Optional[ReasoningChain] = None
    total_execution_time: float = 0.0
    overall_confidence: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    stage_timings: Dict[str, float] = field(default_factory=dict)
    stage_confidences: Dict[str, float] = field(default_factory=dict)
    thinking_process: List[str] = field(default_factory=list)
    reasoning_sentences: List[str] = field(default_factory=list)
    step_by_step_analysis: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Creates a JSON-serializable representation of the result."""
        return asdict(self)


@dataclass
class CallbackBundle:
    """Holds optional callback callables for pipeline execution."""

    on_stage_start: Optional[Any] = None
    on_stage_complete: Optional[Any] = None
    on_thinking_sentence: Optional[Any] = None
    on_sandbox_event: Optional[Any] = None


@dataclass
class StageDescriptor:
    """Descriptor for a single pipeline stage used by unified executor."""

    name: str
    stage: ReasoningStage
    exec_factory: Any
    completion_payload: Any
    predicate: Optional[Any] = None
    sandbox_events: Optional[Dict[str, str]] = None

    def should_run(self, result: "ReasoningResult") -> bool:
        """Check if the stage should run"""
        if self.predicate is None:
            return True
        try:
            return bool(self.predicate(result))
        except Exception:
            return False

    def build_payload(self, stage_result: Any) -> Dict[str, Any]:
        """Build the payload for the stage"""
        try:
            return self.completion_payload(stage_result) if self.completion_payload else {}
        except Exception:
            return {}
