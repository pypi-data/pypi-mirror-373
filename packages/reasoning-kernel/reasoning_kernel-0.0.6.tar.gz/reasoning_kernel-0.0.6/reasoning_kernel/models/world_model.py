"""
World Model representations for the Reasoning Kernel.

This module defines the data structures and operations for world models used in
thinking exploration, including hierarchical model management and evidence integration.

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from enum import auto
from enum import Enum
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid



logger = logging.getLogger(__name__)


class WorldModelLevel(Enum):
    """Hierarchical levels of world models from instance to abstract"""

    INSTANCE = 1  # Ω1 - Specific instance models
    CATEGORY = 2  # Ω2 - Category-level models
    DOMAIN = 3  # Ω3 - Domain-level models
    ABSTRACT = 4  # Ω4+ - Abstract conceptual models


class ModelType(Enum):
    """Types of world models for different reasoning approaches"""

    PROBABILISTIC = auto()  # Probabilistic programming model
    CAUSAL = auto()  # Causal graph model
    LOGICAL = auto()  # Logical rule-based model
    NEURAL = auto()  # Neural network model
    HYBRID = auto()  # Combination of multiple types


@dataclass
class BayesianPrior:
    """Bayesian prior information for world model construction"""

    distribution_type: str  # "normal", "beta", "gamma", etc.
    parameters: Dict[str, float]
    confidence: float
    source: str  # Source of prior information
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorldModelEvidence:
    """Evidence used to update world models"""

    observation_id: str
    evidence_type: str  # "observation", "experiment", "simulation"
    data: Dict[str, Any]
    timestamp: datetime
    reliability: float  # 0.0 to 1.0
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelUpdateResult:
    """Result of updating a world model with new evidence"""

    update_successful: bool
    prior_confidence: float
    posterior_confidence: float
    evidence_impact: float
    updated_parameters: Dict[str, Any]
    convergence_metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AbstractionResult:
    """Result of abstracting instance models to higher levels"""

    abstract_model_id: str
    abstraction_level: WorldModelLevel
    patterns_extracted: List[str]
    similarity_threshold: float
    instances_used: List[str]
    abstraction_confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorldModel:
    """
    Core world model data structure supporting hierarchical reasoning

    Represents models at different abstraction levels (Ω1 to Ωn) with
    Bayesian update capabilities and pattern abstraction.
    """

    # Core identification
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_level: WorldModelLevel = WorldModelLevel.INSTANCE
    model_type: ModelType = ModelType.PROBABILISTIC

    # Model content
    structure: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)

    # Hierarchical relationships
    parent_models: List[str] = field(default_factory=list)  # Higher-level abstractions
    child_models: List[str] = field(default_factory=list)  # More specific instances
    similar_models: List[Tuple[str, float]] = field(default_factory=list)  # (model_id, similarity)

    # Bayesian information
    priors: Dict[str, BayesianPrior] = field(default_factory=dict)
    posterior_updates: List[ModelUpdateResult] = field(default_factory=list)
    confidence_score: float = 0.5
    uncertainty_estimate: float = 0.5

    # Learning and adaptation
    evidence_history: List[WorldModelEvidence] = field(default_factory=list)
    adaptation_count: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    # Context and domain
    domain: str = "general"
    context_description: str = ""
    applicable_situations: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    # Storage and retrieval
    storage_key: Optional[str] = None
    ttl_seconds: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize derived properties after construction"""
        if not self.storage_key:
            self.storage_key = f"world_model:{self.model_level.name.lower()}:{self.model_id}"

        # Set appropriate TTL based on model level
        if self.ttl_seconds is None:
            ttl_mapping = {
                WorldModelLevel.INSTANCE: 3600,  # 1 hour for specific instances
                WorldModelLevel.CATEGORY: 86400,  # 1 day for categories
                WorldModelLevel.DOMAIN: 604800,  # 1 week for domains
                WorldModelLevel.ABSTRACT: 2592000,  # 1 month for abstract models
            }
            self.ttl_seconds = ttl_mapping.get(self.model_level, 3600)

    def add_evidence(self, evidence: WorldModelEvidence) -> None:
        """Add new evidence to the model's history"""
        self.evidence_history.append(evidence)
        self.last_updated = datetime.now(timezone.utc)
        logger.info(
            f"Added evidence to model {self.model_id}: {evidence.evidence_type} (reliability: {evidence.reliability})"
        )

    def update_confidence(self, new_confidence: float) -> None:
        """Update model confidence score"""
        old_confidence = self.confidence_score
        self.confidence_score = max(0.0, min(1.0, new_confidence))
        self.last_updated = datetime.now(timezone.utc)
        logger.info(f"Updated confidence for model {self.model_id}: {old_confidence} -> {self.confidence_score}")

    def add_parent_model(self, parent_id: str) -> None:
        """Add reference to a higher-level abstract model"""
        if parent_id not in self.parent_models:
            self.parent_models.append(parent_id)

    def add_child_model(self, child_id: str) -> None:
        """Add reference to a more specific instance model"""
        if child_id not in self.child_models:
            self.child_models.append(child_id)

    def add_similar_model(self, model_id: str, similarity_score: float) -> None:
        """Add reference to a similar model with similarity score"""
        # Remove existing entry for this model if it exists
        self.similar_models = [(mid, score) for mid, score in self.similar_models if mid != model_id]
        # Add new entry
        self.similar_models.append((model_id, similarity_score))
        # Sort by similarity score (highest first)
        self.similar_models.sort(key=lambda x: x[1], reverse=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert world model to dictionary for storage"""
        return {
            "model_id": self.model_id,
            "model_level": self.model_level.name,
            "model_type": self.model_type.name,
            "structure": self.structure,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "variables": self.variables,
            "parent_models": self.parent_models,
            "child_models": self.child_models,
            "similar_models": self.similar_models,
            "priors": {
                k: {
                    "distribution_type": v.distribution_type,
                    "parameters": v.parameters,
                    "confidence": v.confidence,
                    "source": v.source,
                    "metadata": v.metadata,
                }
                for k, v in self.priors.items()
            },
            "confidence_score": self.confidence_score,
            "uncertainty_estimate": self.uncertainty_estimate,
            "adaptation_count": self.adaptation_count,
            "last_updated": self.last_updated.isoformat(),
            "performance_metrics": self.performance_metrics,
            "domain": self.domain,
            "context_description": self.context_description,
            "applicable_situations": self.applicable_situations,
            "constraints": self.constraints,
            "storage_key": self.storage_key,
            "ttl_seconds": self.ttl_seconds,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldModel":
        """Create world model from dictionary"""
        # Convert string enums back to enum objects
        model_level = WorldModelLevel[data.get("model_level", "INSTANCE")]
        model_type = ModelType[data.get("model_type", "PROBABILISTIC")]

        # Reconstruct priors
        priors = {}
        for k, v in data.get("priors", {}).items():
            priors[k] = BayesianPrior(
                distribution_type=v["distribution_type"],
                parameters=v["parameters"],
                confidence=v["confidence"],
                source=v["source"],
                metadata=v.get("metadata", {}),
            )

        # Parse datetime
        last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now(timezone.utc).isoformat()))

        return cls(
            model_id=data["model_id"],
            model_level=model_level,
            model_type=model_type,
            structure=data.get("structure", {}),
            parameters=data.get("parameters", {}),
            dependencies=data.get("dependencies", []),
            variables=data.get("variables", []),
            parent_models=data.get("parent_models", []),
            child_models=data.get("child_models", []),
            similar_models=data.get("similar_models", []),
            priors=priors,
            confidence_score=data.get("confidence_score", 0.5),
            uncertainty_estimate=data.get("uncertainty_estimate", 0.5),
            adaptation_count=data.get("adaptation_count", 0),
            last_updated=last_updated,
            performance_metrics=data.get("performance_metrics", {}),
            domain=data.get("domain", "general"),
            context_description=data.get("context_description", ""),
            applicable_situations=data.get("applicable_situations", []),
            constraints=data.get("constraints", []),
            storage_key=data.get("storage_key"),
            ttl_seconds=data.get("ttl_seconds"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    def to_json(self) -> str:
        """Convert world model to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "WorldModel":
        """Create world model from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
