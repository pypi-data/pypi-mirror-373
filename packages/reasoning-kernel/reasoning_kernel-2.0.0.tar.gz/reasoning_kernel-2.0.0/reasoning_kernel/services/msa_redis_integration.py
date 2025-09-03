"""
MSA Redis Integration Service

This service provides high-level integration between the MSA pipeline
and the Redis Cloud schema implementation, offering convenient methods
for storing and retrieving MSA data with proper schema compliance.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from ..core.logging_config import log_domain_error, log_service_call
from .unified_redis_service import UnifiedRedisService, create_unified_redis_service

# Import MSA data models
try:
    from ..msa.models.data_types import (
        ConfidenceMetrics,
        InferenceResult,
        KnowledgeBase,
        ModelSpecification,
        MSARequest,
        MSAResponse,
        PipelineResult,
        ReasoningMode,
        ReasoningStep,
        SynthesisResult,
    )
except ImportError:
    # Fallback for missing MSA models
    KnowledgeBase = None
    ModelSpecification = None
    SynthesisResult = None
    InferenceResult = None
    ConfidenceMetrics = None
    PipelineResult = None
    ReasoningStep = None
    MSARequest = None
    MSAResponse = None
    ReasoningMode = None

logger = logging.getLogger(__name__)


class MSARedisIntegration:
    """
    High-level integration service for MSA pipeline and Redis Cloud schema.

    This service provides convenient methods for:
    - Storing complete MSA pipeline results
    - Retrieving and searching MSA data
    - Managing request lifecycles
    - Vector-based semantic search
    """

    def __init__(self, redis_service: UnifiedRedisService):
        """Initialize with an existing Redis service"""
        self.redis = redis_service
        self._logger = logger

    @classmethod
    async def create(
        cls,
        redis_url: str = "redis://localhost:6379",
        embedding_generator=None,
        environment: str = "production",
    ) -> "MSARedisIntegration":
        """Create a new MSA Redis integration service"""
        redis_service = await create_unified_redis_service(
            redis_url=redis_url,
            embedding_generator=embedding_generator,
            environment=environment,
        )
        return cls(redis_service)

    async def store_msa_request(self, msa_request: "MSARequest") -> bool:
        """Store an MSA request for tracking and reference"""
        try:
            request_data = {
                "scenario": msa_request.scenario,
                "context": msa_request.context,
                "reasoning_mode": str(msa_request.reasoning_mode),
                "enabled_stages": msa_request.enabled_stages,
                "configuration": msa_request.configuration,
                "timeout_seconds": msa_request.timeout_seconds,
                "request_id": msa_request.request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Store request with 24-hour TTL
            key = f"req:{msa_request.request_id}"
            await self.redis.redis_client.json().set(key, "$", request_data)
            await self.redis.redis_client.expire(key, 86400)

            log_service_call(
                self._logger,
                "store_msa_request",
                {"request_id": msa_request.request_id},
            )
            return True

        except Exception as e:
            log_domain_error(
                self._logger,
                "store_msa_request",
                e,
                {"request_id": msa_request.request_id},
            )
            return False

    async def store_complete_msa_pipeline(
        self,
        request_id: str,
        knowledge_base: Optional["KnowledgeBase"] = None,
        model_specification: Optional["ModelSpecification"] = None,
        synthesis_result: Optional["SynthesisResult"] = None,
        inference_result: Optional["InferenceResult"] = None,
        pipeline_result: Optional["PipelineResult"] = None,
        embeddings: Optional[Dict[str, List[float]]] = None,
    ) -> bool:
        """Store complete MSA pipeline results with proper schema compliance"""
        try:
            success_count = 0
            total_operations = 0

            # Store knowledge base
            if knowledge_base:
                total_operations += 1
                embedding = embeddings.get("knowledge_base") if embeddings else None
                if await self.redis.store_knowledge_base(
                    knowledge_base, request_id, embedding
                ):
                    success_count += 1

            # Store model specification
            if model_specification:
                total_operations += 1
                embedding = (
                    embeddings.get("model_specification") if embeddings else None
                )
                if await self.redis.store_model_specification(
                    model_specification, request_id, embedding
                ):
                    success_count += 1

            # Store synthesis result
            if synthesis_result:
                total_operations += 1
                if await self._store_synthesis_result(synthesis_result, request_id):
                    success_count += 1

            # Store inference result
            if inference_result:
                total_operations += 1
                if await self._store_inference_result(inference_result, request_id):
                    success_count += 1

            # Store pipeline result
            if pipeline_result:
                total_operations += 1
                if await self.redis.store_pipeline_result(pipeline_result, request_id):
                    success_count += 1

            log_service_call(
                self._logger,
                "store_complete_msa_pipeline",
                {
                    "request_id": request_id,
                    "success_count": success_count,
                    "total_operations": total_operations,
                },
            )

            return success_count == total_operations

        except Exception as e:
            log_domain_error(
                self._logger,
                "store_complete_msa_pipeline",
                e,
                {"request_id": request_id},
            )
            return False
