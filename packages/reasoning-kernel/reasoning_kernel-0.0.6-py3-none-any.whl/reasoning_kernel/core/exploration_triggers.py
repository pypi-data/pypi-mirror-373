"""Exploration triggers for the reasoning kernel."""

from enum import Enum
from typing import Any, Dict, Optional


class ExplorationTrigger(Enum):
    """Types of exploration triggers for reasoning."""

    UNCERTAINTY_HIGH = "uncertainty_high"
    CONFIDENCE_LOW = "confidence_low"
    NOVELTY_DETECTED = "novelty_detected"
    CONTRADICTION_FOUND = "contradiction_found"
    KNOWLEDGE_GAP = "knowledge_gap"
    PATTERN_MISMATCH = "pattern_mismatch"
    USER_REQUESTED = "user_requested"
    AUTOMATIC_SAMPLING = "automatic_sampling"


class TriggerEvent:
    """Event that triggered exploration."""

    def __init__(
        self,
        trigger_type: ExplorationTrigger,
        confidence: float = 0.0,
        uncertainty: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.trigger_type = trigger_type
        self.confidence = confidence
        self.uncertainty = uncertainty
        self.metadata = metadata or {}

    def should_explore(self) -> bool:
        """Determine if exploration should be triggered."""
        return self.confidence < 0.5 or self.uncertainty > 0.7 or self.trigger_type == ExplorationTrigger.USER_REQUESTED
