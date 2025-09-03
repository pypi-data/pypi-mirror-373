"""
Hierarchical World Model Manager - Multi-level world model management
=====================================================================

Implements hierarchical world model management with Bayesian updates
and abstraction capabilities following MSA framework patterns.
"""

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid

import numpy as np
from reasoning_kernel.core.exploration_triggers import ExplorationTrigger
from reasoning_kernel.models.world_model import ModelType
from reasoning_kernel.models.world_model import WorldModel
from reasoning_kernel.models.world_model import WorldModelEvidence
from reasoning_kernel.models.world_model import WorldModelLevel
from reasoning_kernel.services.thinking_exploration_redis import (
    ThinkingExplorationRedisManager,
)
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel import Kernel


logger = logging.getLogger(__name__)


@dataclass
class ModelSimilarity:
    """Represents similarity between two world models"""

    model_id: str
    similarity_score: float
    shared_patterns: List[str]
    confidence: float


@dataclass
class PriorAggregation:
    """Result of aggregating priors from multiple abstract models"""

    aggregated_beliefs: Dict[str, float]
    weight_distribution: Dict[str, float]
    uncertainty_estimate: float
    contributing_models: List[str]


class HierarchicalWorldModelManager:
    """
    Manages hierarchical world models with Bayesian updates and abstraction.

    Implements the MSA framework's hierarchical world model approach where:
    - Ω1: Instance-specific models for particular situations
    - Ω2-Ωn: Abstract models capturing generalizable patterns
    """

    def __init__(self, redis_manager: ThinkingExplorationRedisManager, kernel: Optional[Kernel] = None):
        self.redis_manager = redis_manager
        self.kernel = kernel
        self.abstraction_threshold = 10  # Number of instance models before abstraction
        self.similarity_threshold = 0.3  # Minimum similarity for pattern extraction
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @kernel_function(
        description="Construct instance-specific world model with informative priors", name="construct_instance_model"
    )
    async def construct_instance_model(
        self, scenario_id: str, scenario_description: str, context: Optional[Dict[str, Any]] = None
    ) -> WorldModel:
        """
        Construct Ω1 instance model with informative priors from abstract levels.

        Args:
            scenario_id: Unique identifier for the scenario
            scenario_description: Natural language description of the scenario
            context: Additional context information

        Returns:
            WorldModel: Constructed instance model with priors
        """
        try:
            self.logger.info(f"Constructing instance model for scenario: {scenario_id}")

            # Get relevant abstract models as priors
            priors = await self._get_informative_priors(scenario_description, context or {})

            # Create new instance model
            instance_model = WorldModel(
                model_id=str(uuid.uuid4()),
                model_level=WorldModelLevel.INSTANCE,
                model_type=ModelType.PROBABILISTIC,
                domain=scenario_id,
                context_description=scenario_description,
                parameters=priors.aggregated_beliefs if priors else {},
                uncertainty_estimate=priors.uncertainty_estimate if priors else 0.8,
                confidence_score=0.3,  # Start with low confidence for new instances
                metadata={
                    "context": context or {},
                    "prior_sources": priors.contributing_models if priors else [],
                    "construction_method": "hierarchical_priors",
                    "prior_weight_distribution": priors.weight_distribution if priors else {},
                },
            )

            # Store in Redis
            await self.redis_manager.store_world_model(instance_model)

            self.logger.info(f"Instance model {instance_model.model_id} constructed successfully")
            return instance_model

        except Exception as e:
            self.logger.error(f"Error constructing instance model: {str(e)}")
            # Create fallback model without priors
            fallback_model = WorldModel(
                model_id=str(uuid.uuid4()),
                model_level=WorldModelLevel.INSTANCE,
                model_type=ModelType.PROBABILISTIC,
                domain=scenario_id,
                context_description=scenario_description,
                parameters={},
                uncertainty_estimate=0.9,
                confidence_score=0.1,
                metadata={"context": context or {}, "fallback": True},
            )
            try:
                await self.redis_manager.store_world_model(fallback_model)
            except Exception as store_err:
                self.logger.warning(f"Failed to store fallback model: {store_err}")
            return fallback_model

    @kernel_function(description="Abstract instance models to higher-level patterns", name="abstract_to_higher_level")
    async def abstract_to_higher_level(
        self, domain: str, trigger_type: Optional[ExplorationTrigger] = None
    ) -> Optional[WorldModel]:
        """
        Extract patterns from instance models and create abstract model.

        Args:
            domain: Domain or category for abstraction
            trigger_type: Type of exploration trigger to focus abstraction

        Returns:
            WorldModel: New abstract model or None if insufficient data
        """
        try:
            self.logger.info(f"Starting abstraction for domain: {domain}")

            # Get instance models for this domain
            instance_models = await self._get_instance_models_by_domain(domain, trigger_type)

            if len(instance_models) < self.abstraction_threshold:
                self.logger.debug(f"Insufficient models ({len(instance_models)}) for abstraction")
                return None

            # Find similar patterns across instance models
            pattern_clusters = await self._identify_pattern_clusters(instance_models)

            if not pattern_clusters:
                self.logger.debug("No significant patterns found for abstraction")
                return None

            # Extract generalizable beliefs
            abstract_beliefs = await self._extract_generalizable_beliefs(pattern_clusters)

            # Create abstract model
            abstract_model = WorldModel(
                model_id=str(uuid.uuid4()),
                model_level=WorldModelLevel.ABSTRACT,
                model_type=ModelType.PROBABILISTIC,
                domain=domain,
                context_description=f"Abstract model for {domain} scenarios",
                parameters=abstract_beliefs,
                uncertainty_estimate=self._calculate_abstract_uncertainty(pattern_clusters),
                confidence_score=self._calculate_abstract_confidence(instance_models),
                metadata={
                    "domain": domain,
                    "trigger_type": trigger_type.name if trigger_type else None,
                    "source_instances": [m.model_id for m in instance_models],
                    "pattern_clusters": len(pattern_clusters),
                    "abstraction_timestamp": datetime.now().isoformat(),
                },
            )

            # Store abstract model
            await self.redis_manager.store_world_model(abstract_model)

            self.logger.info(f"Abstract model {abstract_model.model_id} created successfully")
            return abstract_model

        except Exception as e:
            self.logger.error(f"Error in abstraction process: {str(e)}")
            return None

    @kernel_function(
        description="Update world model with new observations using Bayesian inference", name="bayesian_update"
    )
    async def bayesian_update(
        self, model_id: str, new_evidence: WorldModelEvidence, learning_rate: float = 0.1
    ) -> Optional[WorldModel]:
        """
        Update world model beliefs using Bayesian inference.

        Args:
            model_id: ID of the model to update
            new_evidence: New evidence to incorporate
            learning_rate: Rate of belief updating (0.0 to 1.0)

        Returns:
            WorldModel: Updated model or None if error
        """
        try:
            self.logger.info(f"Performing Bayesian update for model: {model_id}")

            # Retrieve existing model
            model = await self.redis_manager.retrieve_world_model(model_id)
            if not model:
                self.logger.error(f"Model {model_id} not found")
                return None

            # Add new evidence
            model.add_evidence(new_evidence)

            # Update beliefs based on evidence
            updated_beliefs = await self._update_beliefs_bayesian(model.parameters, new_evidence, learning_rate)

            # Update uncertainty and confidence
            model.parameters = updated_beliefs
            model.uncertainty_estimate = max(0.0, model.uncertainty_estimate - learning_rate * 0.1)
            model.confidence_score = min(1.0, model.confidence_score + learning_rate * 0.1)

            # Store updated model
            await self.redis_manager.store_world_model(model)

            self.logger.info(f"Model {model_id} updated successfully")
            return model

        except Exception as e:
            self.logger.error(f"Error in Bayesian update: {str(e)}")
            return None

    async def compute_model_similarity(self, model1: WorldModel, model2: WorldModel) -> ModelSimilarity:
        """
        Compute similarity between two world models.

        Args:
            model1: First model for comparison
            model2: Second model for comparison

        Returns:
            ModelSimilarity: Similarity metrics
        """
        try:
            # Belief similarity (cosine similarity of belief vectors)
            belief_sim = self._compute_belief_similarity(model1.parameters, model2.parameters)

            # Pattern similarity (Jaccard index of evidence patterns)
            pattern_sim = self._compute_pattern_similarity(model1.evidence_history, model2.evidence_history)

            # Context similarity
            context_sim = self._compute_context_similarity(
                model1.metadata.get("context", {}), model2.metadata.get("context", {})
            )

            # Weighted overall similarity
            overall_similarity = 0.5 * belief_sim + 0.3 * pattern_sim + 0.2 * context_sim

            # Identify shared patterns
            shared_patterns = self._identify_shared_patterns(model1, model2)

            # Calculate confidence in similarity measure
            confidence = min(model1.confidence_score, model2.confidence_score) * overall_similarity

            return ModelSimilarity(
                model_id=model2.model_id,
                similarity_score=overall_similarity,
                shared_patterns=shared_patterns,
                confidence=confidence,
            )

        except Exception as e:
            self.logger.error(f"Error computing model similarity: {str(e)}")
            return ModelSimilarity(model_id=model2.model_id, similarity_score=0.0, shared_patterns=[], confidence=0.0)

    async def _get_informative_priors(
        self, scenario_description: str, context: Dict[str, Any]
    ) -> Optional[PriorAggregation]:
        """Get informative priors from relevant abstract models."""
        try:
            # Find relevant abstract models
            relevant_models = await self._find_relevant_abstract_models(scenario_description, context)

            if not relevant_models:
                return None

            # Aggregate beliefs from relevant models
            aggregated_beliefs = {}
            weight_distribution = {}
            contributing_models = []

            total_weight = 0.0
            for model, relevance_score in relevant_models:
                weight = relevance_score * model.confidence_score
                total_weight += weight
                contributing_models.append(model.model_id)
                weight_distribution[model.model_id] = weight

                # Weighted belief aggregation
                for belief_key, belief_value in model.parameters.items():
                    if belief_key not in aggregated_beliefs:
                        aggregated_beliefs[belief_key] = 0.0
                    aggregated_beliefs[belief_key] += weight * belief_value

            # Normalize beliefs
            if total_weight > 0:
                for key in aggregated_beliefs:
                    aggregated_beliefs[key] /= total_weight
                    weight_distribution[key] = weight_distribution.get(key, 0) / total_weight

            # Calculate uncertainty estimate
            uncertainty_estimate = 1.0 - (total_weight / len(relevant_models)) if relevant_models else 0.9

            return PriorAggregation(
                aggregated_beliefs=aggregated_beliefs,
                weight_distribution=weight_distribution,
                uncertainty_estimate=uncertainty_estimate,
                contributing_models=contributing_models,
            )

        except Exception as e:
            self.logger.error(f"Error getting informative priors: {str(e)}")
            return None

    async def _find_relevant_abstract_models(
        self, scenario_description: str, context: Dict[str, Any]
    ) -> List[Tuple[WorldModel, float]]:
        """Find abstract models relevant to the scenario."""
        try:
            # Get all abstract models
            abstract_models = await self.redis_manager.get_models_by_level(WorldModelLevel.ABSTRACT)

            relevant_models = []
            for model in abstract_models:
                # Calculate relevance score based on description similarity
                relevance_score = await self._calculate_relevance_score(model, scenario_description, context)

                if relevance_score >= 0.3:  # Relevance threshold
                    relevant_models.append((model, relevance_score))

            # Sort by relevance score
            relevant_models.sort(key=lambda x: x[1], reverse=True)

            # Return top 5 most relevant models
            return relevant_models[:5]

        except Exception as e:
            self.logger.error(f"Error finding relevant abstract models: {str(e)}")
            return []

    async def _calculate_relevance_score(
        self, model: WorldModel, scenario_description: str, context: Dict[str, Any]
    ) -> float:
        """Calculate how relevant an abstract model is to a scenario."""
        try:
            # Simple text similarity for now (could use embeddings)
            description_words = set(scenario_description.lower().split())
            model_words = set(model.context_description.lower().split())

            # Jaccard similarity
            intersection = description_words.intersection(model_words)
            union = description_words.union(model_words)

            text_similarity = len(intersection) / len(union) if union else 0.0

            # Context similarity
            model_context = model.metadata.get("context", {})
            context_similarity = self._compute_context_similarity(context, model_context)

            # Domain match boost
            domain_match = 1.0 if context.get("domain", "").lower() == (model.domain or "").lower() else 0.0
            # Combined relevance score
            relevance_score = 0.5 * text_similarity + 0.2 * context_similarity + 0.4 * domain_match

            return relevance_score

        except Exception as e:
            self.logger.error(f"Error calculating relevance score: {str(e)}")
            return 0.0

    async def _get_instance_models_by_domain(
        self, domain: str, trigger_type: Optional[ExplorationTrigger] = None
    ) -> List[WorldModel]:
        """Get instance models for a specific domain."""
        try:
            # Get all instance models
            instance_models = await self.redis_manager.get_models_by_level(WorldModelLevel.INSTANCE)

            # Filter by domain and trigger type
            filtered_models = []
            for model in instance_models:
                model_domain = model.metadata.get("domain", model.domain or "")
                model_trigger = model.metadata.get("trigger_type")

                domain_match = (
                    domain.lower() in model_domain.lower() or domain.lower() in model.context_description.lower()
                )
                trigger_match = trigger_type is None or model_trigger is None or model_trigger == trigger_type.name

                if domain_match and trigger_match:
                    filtered_models.append(model)

            return filtered_models

        except Exception as e:
            self.logger.error(f"Error getting instance models by domain: {str(e)}")
            return []

    async def _identify_pattern_clusters(self, models: List[WorldModel]) -> List[List[WorldModel]]:
        """Identify clusters of similar models for pattern extraction."""
        try:
            if len(models) < 2:
                return []

            # Simple clustering based on similarity
            clusters = []
            used_models = set()

            for i, model1 in enumerate(models):
                if model1.model_id in used_models:
                    continue

                cluster = [model1]
                used_models.add(model1.model_id)

                for j, model2 in enumerate(models[i + 1 :], i + 1):
                    if model2.model_id in used_models:
                        continue

                    similarity = await self.compute_model_similarity(model1, model2)
                    if similarity.similarity_score > self.similarity_threshold:
                        cluster.append(model2)
                        used_models.add(model2.model_id)

                if len(cluster) >= 2:  # Only keep clusters with multiple models
                    clusters.append(cluster)

            return clusters

        except Exception as e:
            self.logger.error(f"Error identifying pattern clusters: {str(e)}")
            return []

    async def _extract_generalizable_beliefs(self, pattern_clusters: List[List[WorldModel]]) -> Dict[str, float]:
        """Extract generalizable beliefs from pattern clusters."""
        try:
            generalized_beliefs = {}

            for cluster in pattern_clusters:
                # Aggregate beliefs within cluster
                cluster_beliefs = {}
                for model in cluster:
                    for belief_key, belief_value in model.parameters.items():
                        if belief_key not in cluster_beliefs:
                            cluster_beliefs[belief_key] = []
                        cluster_beliefs[belief_key].append(belief_value)

                # Calculate average beliefs for this cluster
                for belief_key, values in cluster_beliefs.items():
                    avg_value = sum(values) / len(values)
                    # Weight by cluster size and confidence
                    cluster_weight = len(cluster) / sum(len(c) for c in pattern_clusters)
                    avg_confidence = sum(m.confidence_score for m in cluster) / len(cluster)

                    weighted_value = avg_value * cluster_weight * avg_confidence

                    if belief_key not in generalized_beliefs:
                        generalized_beliefs[belief_key] = 0.0
                    generalized_beliefs[belief_key] += weighted_value

            return generalized_beliefs

        except Exception as e:
            self.logger.error(f"Error extracting generalizable beliefs: {str(e)}")
            return {}

    def _calculate_abstract_uncertainty(self, pattern_clusters: List[List[WorldModel]]) -> float:
        """Calculate uncertainty for abstract model based on pattern clusters."""
        if not pattern_clusters:
            return 0.9

        # Lower uncertainty with more consistent patterns
        cluster_consistency = sum(len(cluster) for cluster in pattern_clusters) / len(pattern_clusters)
        uncertainty = max(0.1, 1.0 - (cluster_consistency / 10.0))
        return uncertainty

    def _calculate_abstract_confidence(self, instance_models: List[WorldModel]) -> float:
        """Calculate confidence for abstract model based on instance models."""
        if not instance_models:
            return 0.1

        avg_confidence = sum(m.confidence_score for m in instance_models) / len(instance_models)
        # Scale by number of contributing models
        confidence_boost = min(0.3, len(instance_models) / 50.0)
        return min(1.0, avg_confidence + confidence_boost)

    async def _update_beliefs_bayesian(
        self, current_beliefs: Dict[str, float], new_evidence: WorldModelEvidence, learning_rate: float
    ) -> Dict[str, float]:
        """Update beliefs using simple Bayesian inference."""
        updated_beliefs = current_beliefs.copy()

        # Simple belief update based on evidence
        evidence_impact = new_evidence.reliability * learning_rate

        # Update relevant beliefs based on evidence content
        for key in updated_beliefs:
            if key.lower() in str(new_evidence.data).lower():
                # Simple positive/negative evidence detection
                positive_indicators = ["success", "positive", "good", "high", "increase"]
                negative_indicators = ["failure", "negative", "bad", "low", "decrease"]

                evidence_text = str(new_evidence.data).lower()
                is_positive = any(indicator in evidence_text for indicator in positive_indicators)
                is_negative = any(indicator in evidence_text for indicator in negative_indicators)

                if is_positive:
                    updated_beliefs[key] = min(1.0, updated_beliefs[key] + evidence_impact)
                elif is_negative:
                    updated_beliefs[key] = max(0.0, updated_beliefs[key] - evidence_impact)

        return updated_beliefs

    def _compute_belief_similarity(self, beliefs1: Dict[str, float], beliefs2: Dict[str, float]) -> float:
        """Compute cosine similarity between belief vectors."""
        if not beliefs1 or not beliefs2:
            return 0.0

        # Get common keys
        common_keys = set(beliefs1.keys()).intersection(set(beliefs2.keys()))
        if not common_keys:
            return 0.0

        # Create vectors
        vec1 = np.array([beliefs1[key] for key in common_keys])
        vec2 = np.array([beliefs2[key] for key in common_keys])

        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _compute_pattern_similarity(
        self, evidence1: List[WorldModelEvidence], evidence2: List[WorldModelEvidence]
    ) -> float:
        """Compute Jaccard similarity between evidence patterns."""
        if not evidence1 or not evidence2:
            return 0.0

        # Extract pattern keywords from evidence
        patterns1 = set()
        patterns2 = set()

        for ev in evidence1:
            patterns1.update(str(ev.data).lower().split())

        for ev in evidence2:
            patterns2.update(str(ev.data).lower().split())

        # Jaccard similarity
        intersection = patterns1.intersection(patterns2)
        union = patterns1.union(patterns2)

        return len(intersection) / len(union) if union else 0.0

    def _compute_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Compute similarity between context dictionaries."""
        if not context1 or not context2:
            return 0.0

        # Simple key overlap similarity
        keys1 = set(context1.keys())
        keys2 = set(context2.keys())

        intersection = keys1.intersection(keys2)
        union = keys1.union(keys2)

        return len(intersection) / len(union) if union else 0.0

    def _identify_shared_patterns(self, model1: WorldModel, model2: WorldModel) -> List[str]:
        """Identify shared patterns between two models."""
        shared_patterns = []

        # Shared belief keys
        common_beliefs = set(model1.parameters.keys()).intersection(set(model2.parameters.keys()))
        shared_patterns.extend([f"belief_{key}" for key in common_beliefs])

        # Shared evidence patterns
        if model1.evidence_history and model2.evidence_history:
            patterns1 = set()
            patterns2 = set()

            for ev in model1.evidence_history:
                patterns1.update(str(ev.data).lower().split())

            for ev in model2.evidence_history:
                patterns2.update(str(ev.data).lower().split())

            common_patterns = patterns1.intersection(patterns2)
            shared_patterns.extend([f"evidence_{pattern}" for pattern in common_patterns])

        return shared_patterns
