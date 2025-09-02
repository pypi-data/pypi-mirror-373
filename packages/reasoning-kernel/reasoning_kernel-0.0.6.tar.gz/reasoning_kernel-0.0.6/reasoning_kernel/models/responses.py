"""
Response models for MSA API endpoints
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic import Field


class KnowledgeBase(BaseModel):
    """Knowledge base extracted from Mode 1"""

    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    causal_factors: List[Dict[str, Any]] = Field(default_factory=list)
    constraints: List[Dict[str, Any]] = Field(default_factory=list)
    domain_knowledge: List[str] = Field(default_factory=list)
    scenario: str = ""


class ModelSpecifications(BaseModel):
    """Model specifications for probabilistic synthesis"""

    variables: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: List[Dict[str, Any]] = Field(default_factory=list)
    uncertainties: List[Dict[str, Any]] = Field(default_factory=list)
    model_type: str = "generic_bayesian"


class UncertaintyAnalysis(BaseModel):
    """Uncertainty analysis from probabilistic model"""

    epistemic_uncertainty: Dict[str, Any] = Field(default_factory=dict)
    aleatory_uncertainty: Dict[str, Any] = Field(default_factory=dict)
    total_uncertainty: Dict[str, Any] = Field(default_factory=dict)
    overall_assessment: Dict[str, Any] = Field(default_factory=dict)


class ProbabilisticAnalysis(BaseModel):
    """Results from probabilistic model synthesis"""

    model_structure: Dict[str, Any] = Field(default_factory=dict)
    inference_results: Dict[str, Any] = Field(default_factory=dict)
    predictions: Dict[str, Any] = Field(default_factory=dict)
    uncertainty_analysis: UncertaintyAnalysis = Field(default_factory=UncertaintyAnalysis)
    success: bool = False


class ReasoningStep(BaseModel):
    """Individual step in the reasoning chain"""

    step_id: str
    step_type: str
    description: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None


class ConfidenceMetrics(BaseModel):
    """Probabilistic model confidence metrics"""

    overall_score: float = Field(ge=0.0, le=1.0, description="Overall confidence score")
    confidence_level: str = Field(description="Categorical confidence level")

    # Component scores
    knowledge_extraction_score: float = Field(ge=0.0, le=1.0)
    model_synthesis_score: float = Field(ge=0.0, le=1.0)
    uncertainty_quantification_score: float = Field(ge=0.0, le=1.0)
    integration_coherence_score: float = Field(ge=0.0, le=1.0)

    # Detailed metrics
    completeness_metrics: Dict[str, Any] = Field(default_factory=dict)
    reliability_metrics: Dict[str, Any] = Field(default_factory=dict)
    consistency_metrics: Dict[str, Any] = Field(default_factory=dict)

    # Explanations
    confidence_explanation: str = ""
    improvement_suggestions: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)


class ThinkingModeOutput(BaseModel):
    """Thinking mode outputs with sentence-based reasoning"""

    thinking_process: List[str] = Field(default_factory=list, description="High-level reasoning steps and thoughts")
    reasoning_sentences: List[str] = Field(
        default_factory=list, description="Coherent sentences explaining the thinking process"
    )
    step_by_step_analysis: Dict[str, List[str]] = Field(
        default_factory=dict, description="Detailed analysis for each reasoning stage"
    )
    thinking_detail_level: str = Field(
        default="detailed", description="Level of thinking detail (minimal, moderate, detailed)"
    )


class FinalReasoning(BaseModel):
    """Final integrated reasoning results"""

    summary: str
    key_insights: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    uncertainty_assessment: Dict[str, Any] = Field(default_factory=dict)
    reasoning_quality: Dict[str, Any] = Field(default_factory=dict)
    confidence_metrics: Optional[ConfidenceMetrics] = None
    thinking_mode: Optional[ThinkingModeOutput] = None


class MSAReasoningResponse(BaseModel):
    """Complete response from MSA reasoning"""

    session_id: str
    scenario: str
    reasoning_chain: List[ReasoningStep]
    knowledge_base: KnowledgeBase
    model_specifications: ModelSpecifications
    probabilistic_analysis: ProbabilisticAnalysis
    final_reasoning: FinalReasoning
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool
    error: Optional[str] = None
    error_type: Optional[str] = None


class KnowledgeExtractionResponse(BaseModel):
    """Response from knowledge extraction endpoint"""

    knowledge_base: KnowledgeBase
    model_specifications: ModelSpecifications
    processing_time_seconds: float
    success: bool
    error: Optional[str] = None


class ProbabilisticModelResponse(BaseModel):
    """Response from probabilistic model synthesis"""

    probabilistic_analysis: ProbabilisticAnalysis
    processing_time_seconds: float
    success: bool
    error: Optional[str] = None


class SessionStatus(BaseModel):
    """Session status information"""

    session_id: str
    status: str  # "processing", "completed", "failed"
    start_time: datetime
    scenario_preview: str
    processing_time: Optional[float] = None
    error: Optional[str] = None


class SessionListResponse(BaseModel):
    """Response listing active sessions"""

    active_sessions: List[SessionStatus]
    total_count: int


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    kernel_initialized: bool
    msa_initialized: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str
    message: str
    error_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = None
