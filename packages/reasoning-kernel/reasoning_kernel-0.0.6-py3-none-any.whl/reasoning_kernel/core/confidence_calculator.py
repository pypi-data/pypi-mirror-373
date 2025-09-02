"""
The `ConfidenceCalculator` class is responsible for assessing the reliability of the reasoning process. It operates by extracting confidence scores from various stages of the reasoning pipeline, such as parsing, retrieval, and graph generation. Each stage produces a confidence value, which is then used to compute a weighted overall confidence score. This final score provides a quantitative measure of the trustworthiness of the reasoning outcome. Additionally, the module determines the success of the entire reasoning process by checking if critical stages were completed and if the overall confidence meets predefined thresholds.
"""

from typing import Any

from .. import constants
from ..models.reasoning_types import ReasoningResult


class ConfidenceCalculator:
    def extract_confidence_from_stage_result(
        self, stage_result: Any, stage: str
    ) -> float:
        """Extract confidence value from stage result object."""
        if hasattr(stage_result, constants.CONFIDENCE_ATTR_PARSING):
            return getattr(stage_result, constants.CONFIDENCE_ATTR_PARSING)
        elif hasattr(stage_result, constants.CONFIDENCE_ATTR_RETRIEVAL):
            return getattr(stage_result, constants.CONFIDENCE_ATTR_RETRIEVAL)
        elif hasattr(stage_result, constants.CONFIDENCE_ATTR_GRAPH):
            return getattr(stage_result, constants.CONFIDENCE_ATTR_GRAPH)
        elif hasattr(stage_result, constants.CONFIDENCE_ATTR_GENERIC):
            return getattr(stage_result, constants.CONFIDENCE_ATTR_GENERIC)
        else:
            return constants.DEFAULT_CONFIDENCE

    def calculate_overall_confidence(self, result: ReasoningResult) -> float:
        """Calculate overall confidence from stage confidences"""
        confidences = list((result.stage_confidences or {}).values())
        if not confidences:
            return 0.0
        weights = [1.0, 1.2, 1.4, 1.6, 1.8][: len(confidences)]
        weighted_sum = sum(c * w for c, w in zip(confidences, weights))
        weight_total = sum(weights)
        return weighted_sum / weight_total if weight_total > 0 else 0.0

    def determine_success(self, result: ReasoningResult) -> bool:
        """Determine if reasoning was successful based on stages completed"""
        # Must complete at least parse and retrieve stages
        if not result.parsed_vignette or not result.retrieval_context:
            return False

        # If probabilistic program was generated but failed validation, check for partial success
        if result.probabilistic_program and not getattr(
            result.probabilistic_program, "validation_status", False
        ):
            return result.overall_confidence >= constants.PARTIAL_SUCCESS_CONFIDENCE

        # Full success requires inference completion
        if result.inference_result:
            inference_status = getattr(
                result.inference_result, "inference_status", None
            )
            if inference_status:
                status_name = getattr(inference_status, "name", str(inference_status))
                if status_name == "COMPLETED":
                    return True

        # Partial success if most stages completed with reasonable confidence
        completed_stages = len(result.stage_timings or {})
        return (
            completed_stages >= 3
            and result.overall_confidence >= constants.DEFAULT_CONFIDENCE_THRESHOLD
        )


# Compatibility stubs for tests
class ConfidenceMetrics:
    """Metrics container for confidence calculations"""

    def __init__(self, confidence: float = 0.0, uncertainty: float = 1.0):
        self.confidence = confidence
        self.uncertainty = uncertainty


class UncertaintyEstimator:
    """Estimator for uncertainty in reasoning results"""

    def __init__(self):
        pass

    def estimate_uncertainty(self, result: Any) -> float:
        """Estimate uncertainty from result"""
        return 0.5
