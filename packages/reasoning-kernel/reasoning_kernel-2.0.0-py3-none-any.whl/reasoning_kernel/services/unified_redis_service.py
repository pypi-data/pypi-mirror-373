"""
Unified Redis Service for Reasoning Kernel

This module consolidates three separate Redis implementations into a single,
production-ready service with connection pooling, vector operations, and
comprehensive functionality for the MSA Reasoning Engine.

Consolidates:
- RedisMemoryService: General purpose Redis operations
- RedisVectorService: Vector storage with Semantic Kernel
- ProductionRedisManager: Production-ready schema-aware operations

Key Features:
- Connection pooling with async operations
- Vector storage and similarity search
- World model operations with hierarchical support
- Reasoning chain storage and retrieval
- Knowledge management with tagging
- Session management and caching
- Production-ready error handling and monitoring
- Schema-aware key generation with TTL policies
- Batch operations for performance
- Circuit breaker integration

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from typing import Any, Dict, List, Optional, Set

# Import circuit breaker
from ..core.circuit_breaker import CircuitBreaker
from ..core.exceptions import ServiceError
from ..core.logging_config import log_domain_error, log_service_call
from ..core.logging_utils import simple_log_error

try:
    import redis
    from redis import asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    aioredis = None

try:
    from semantic_kernel.connectors.ai.embedding_generator_base import EmbeddingGeneratorBase
    from semantic_kernel.connectors.redis import RedisStore
except Exception:
    # Fallback implementations
    class _DummyRedisStore:
        def __init__(self, *args, **kwargs):
            pass

        def get_collection(self, *args, **kwargs):
            class _DummyCollection:
                async def upsert(self, *a, **k):
                    return None

            return _DummyCollection()

    RedisStore = _DummyRedisStore

    class EmbeddingGeneratorBase:
        async def generate_embeddings(self, texts: List[str]):
            return [[0.0] * 1 for _ in texts]


from ..core.constants import DEFAULT_CACHE_TTL, REASONING_RESULT_TTL, SHORT_CACHE_TTL

# Import MSA data models for schema integration
try:
    from ..msa.models.data_types import (
        ConfidenceMetrics,
        InferenceResult,
        KnowledgeBase,
        ModelSpecification,
        MSARequest,
        MSAResponse,
        PipelineResult,
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

# Schema imports
try:
    from ..schemas.redis_memory_schema import (
        ReasoningKernelRedisSchema,
        TTLPolicy,
        create_development_schema,
        create_production_schema,
    )
except ImportError:
    # Fallback for missing schema
    class TTLPolicy:
        def __init__(self, default_ttl: int = 3600):
            self.default_ttl = default_ttl

    class ReasoningKernelRedisSchema:
        def __init__(self):
            self.config = type("config", (), {"namespace_prefix": "rk"})()
            self.ttl_policies = {}

    def create_production_schema():
        """Create production schema with appropriate TTL settings"""
        schema = ReasoningKernelRedisSchema()
        schema.ttl_policies = {
            "reasoning_chain": TTLPolicy(7200),  # 2 hours
            "world_model": TTLPolicy(3600),  # 1 hour
            "knowledge": TTLPolicy(86400),  # 24 hours
            "session": TTLPolicy(1800),  # 30 minutes
            "cache": TTLPolicy(900),  # 15 minutes
        }
        return schema

    def create_development_schema():
        """Create development schema with shorter TTL settings"""
        schema = ReasoningKernelRedisSchema()
        schema.ttl_policies = {
            "reasoning_chain": TTLPolicy(1800),  # 30 minutes
            "world_model": TTLPolicy(900),  # 15 minutes
            "knowledge": TTLPolicy(3600),  # 1 hour
            "session": TTLPolicy(600),  # 10 minutes
            "cache": TTLPolicy(300),  # 5 minutes
        }
        return schema


# World model imports
try:
    from ..core.exploration_triggers import ExplorationTrigger, TriggerDetectionResult
    from ..models.world_model import WorldModel, WorldModelEvidence
except ImportError:
    # Fallback classes for missing models
    class WorldModel:
        pass

    class WorldModelEvidence:
        pass

    class ExplorationTrigger:
        pass

    class TriggerDetectionResult:
        pass


logger = logging.getLogger(__name__)


@dataclass
class ReasoningRecord:
    """Record for reasoning patterns and results"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: str = ""
    question: str = ""
    reasoning_steps: str = ""
    final_answer: str = ""
    confidence_score: float = 0.0
    context: str = "{}"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    embedding: List[float] = field(default_factory=list)


@dataclass
class WorldModelRecord:
    """Record for world model states and contexts"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_type: str = ""
    state_data: str = "{}"
    confidence: float = 0.0
    context_keys: str = "[]"
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    embedding: List[float] = field(default_factory=list)


@dataclass
class ExplorationRecord:
    """Record for exploration patterns and discoveries"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exploration_type: str = ""
    hypothesis: str = ""
    evidence: str = ""
    conclusion: str = ""
    exploration_path: str = "[]"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    embedding: List[float] = field(default_factory=list)


@dataclass
class RedisConnectionConfig:
    """Configuration for Redis connection"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True
    max_connections: int = 50
    retry_attempts: int = 3
    timeout: float = 30.0
    redis_url: Optional[str] = None


class UnifiedRedisService:
    """
    Unified Redis service combining memory operations, vector storage,
    and production-ready schema management.

    This service consolidates functionality from:
    - RedisMemoryService: General Redis operations
    - RedisVectorService: Vector operations with Semantic Kernel
    - ProductionRedisManager: Production schema operations
    """

    def __init__(
        self,
        config: Optional[RedisConnectionConfig] = None,
        embedding_generator: Optional[EmbeddingGeneratorBase] = None,
        schema: Optional[ReasoningKernelRedisSchema] = None,
        enable_monitoring: bool = True,
    ):
        """Initialize unified Redis service"""
        self.config = config or RedisConnectionConfig()
        self.embedding_generator = embedding_generator
        self.schema = schema or create_production_schema()
        self.enable_monitoring = enable_monitoring

        # Connection management
        self.redis_client: Optional[Any] = None
        self._connection_pool: Optional[Any] = None
        self._is_connected = False

        # Vector store components
        self.redis_store = None
        self._collections = {}
        self._vector_initialized = False

        # Monitoring and performance
        self._operation_count = 0
        self._error_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._memory_cache: Dict[
            str, Any
        ] = {}  # In-memory cache for frequently accessed items
        self._memory_cache_ttl: Dict[str, float] = {}  # TTL for memory cache items
        self._last_cleanup_time = time.time()

        # Circuit breaker for Redis operations
        from ..core.circuit_breaker import CircuitBreakerConfig, ServiceType

        circuit_breaker_config = CircuitBreakerConfig(
            service_type=ServiceType.REDIS,
            failure_threshold=5,
            timeout_duration=30.0,
            max_retries=3,
            base_delay=1.0,
            retriable_exceptions=(
                ConnectionError,
                TimeoutError,
                OSError,
            ),
        )
        self._circuit_breaker = CircuitBreaker("redis", circuit_breaker_config)

        logger.info(
            f"UnifiedRedisService initialized with schema: {self.schema.config.namespace_prefix}"
        )

    # Connection Management
    async def connect(self) -> bool:
        """Establish connection to Redis with connection pooling"""
        if self._is_connected and self.redis_client:
            return True

        if not REDIS_AVAILABLE:
            simple_log_error(
                logger,
                "connect",
                Exception("Redis is not available - install redis-py"),
            )
            return False

        try:
            connection_kwargs = {
                "decode_responses": self.config.decode_responses,
                "retry_on_timeout": True,
                "socket_connect_timeout": self.config.timeout,
                "socket_timeout": self.config.timeout,
            }

            # Build pool and client via helper for clarity and reuse
            from .redis_connection import build_connection_pool, build_redis_client

            self._connection_pool = build_connection_pool(
                redis_url=self.config.redis_url,
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                connection_kwargs=connection_kwargs,
            )

            self.redis_client = build_redis_client(self._connection_pool)

            # Test connection
            await self.redis_client.ping()
            self._is_connected = True

            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
            return True

        except Exception as e:
            simple_log_error(
                logger,
                "connect",
                e,
                redis_url=self.config.redis_url if self.config else "unknown",
            )
            self._is_connected = False
            return False

    async def disconnect(self) -> None:
        """Close Redis connection and cleanup resources"""
        try:
            if self.redis_client:
                await self.redis_client.aclose()
                self.redis_client = None

            if self._connection_pool:
                await self._connection_pool.aclose()
                self._connection_pool = None

            self._is_connected = False
            self._vector_initialized = False
            self._collections.clear()

            logger.info("Disconnected from Redis")

        except Exception as e:
            simple_log_error(logger, "disconnect", e)

    async def _ensure_connected(self) -> bool:
        """Ensure Redis connection is established"""
        if not self._is_connected:
            # Use circuit breaker for connection attempts
            async with self._circuit_breaker:
                return await self.connect()
        return True

    def _increment_operation_count(self, operation_type: str = "general") -> None:
        """Track operation counts for monitoring"""
        if self.enable_monitoring:
            self._operation_count += 1

    def _increment_error_count(self) -> None:
        """Track error counts for monitoring"""
        if self.enable_monitoring:
            self._error_count += 1

    def _cleanup_expired_memory_cache(self):
        """Clean up expired entries in the in-memory cache"""
        from .redis_maintenance import cleanup_expired_memory_cache

        cleanup_expired_memory_cache(self._memory_cache, self._memory_cache_ttl)
        self._last_cleanup_time = time.time()

    # Vector Operations (from RedisVectorService)
    async def initialize_vector_store(self) -> bool:
        """Initialize Redis vector store for embeddings"""
        if self._vector_initialized or not self.embedding_generator:
            return True

        try:
            connection_string = (
                self.config.redis_url
                or f"redis://{self.config.host}:{self.config.port}"
            )

            from .redis_vectors import initialize_vector_store

            self.redis_store = await initialize_vector_store(
                connection_string, self.embedding_generator
            )

            # Initialize collections on-demand to avoid definition issues
            self._vector_initialized = True
            logger.info("Vector store initialized successfully")
            return True

        except Exception as e:
            simple_log_error(logger, "initialize_vector_store", e)
            return False

    async def _get_or_create_collection(self, collection_name: str, record_type: type):
        """Lazy collection creation for vector operations"""
        if collection_name not in self._collections:
            if not self._vector_initialized:
                await self.initialize_vector_store()

            try:
                from .redis_vectors import get_or_create_collection

                self._collections[collection_name] = await get_or_create_collection(
                    self.redis_store, self._collections, collection_name, record_type
                )
                logger.debug(f"Created collection: {collection_name}")
            except Exception as e:
                simple_log_error(
                    logger,
                    "get_or_create_collection",
                    e,
                    collection_name=collection_name,
                )
                raise

        return self._collections[collection_name]

    # Reasoning Chain Operations (from RedisMemoryService)
    async def store_reasoning_chain(
        self, chain_id: str, chain_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Store reasoning chain with optional TTL"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                key = (
                    f"{self.schema.config.namespace_prefix}:reasoning:chain:{chain_id}"
                )
                serialized_data = json.dumps(chain_data, default=str)

                if ttl:
                    await self.redis_client.setex(key, ttl, serialized_data)
                else:
                    await self.redis_client.set(key, serialized_data)

                # Also store with embedding if vector store available
                if self._vector_initialized:
                    try:
                        await self._store_reasoning_pattern_vector(
                            pattern_type="reasoning_chain",
                            question=chain_data.get("question", ""),
                            reasoning_steps=chain_data.get("steps", ""),
                            final_answer=chain_data.get("conclusion", ""),
                            confidence_score=chain_data.get("confidence", 0.0),
                            context=chain_data,
                        )
                    except Exception as vector_error:
                        logger.warning(
                            f"Vector storage failed for reasoning chain {chain_id}: {vector_error}"
                        )

                # Update in-memory cache
                cache_key = f"reasoning_chain:{chain_id}"
                self._memory_cache[cache_key] = chain_data
                self._memory_cache_ttl[cache_key] = time.time()

                self._increment_operation_count("store_reasoning_chain")
                logger.debug(f"Stored reasoning chain: {chain_id}")
                return True

        except Exception as e:
            simple_log_error(logger, "store_reasoning_chain", e, chain_id=chain_id)
            self._increment_error_count()
            return False

    async def get_reasoning_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve reasoning chain by ID"""
        # Check in-memory cache first
        cache_key = f"reasoning_chain:{chain_id}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if (
                time.time() - self._memory_cache_ttl.get(cache_key, 0)
                < DEFAULT_CACHE_TTL
            ):
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]

        if not await self._ensure_connected():
            return None

        try:
            async with self._circuit_breaker:
                key = (
                    f"{self.schema.config.namespace_prefix}:reasoning:chain:{chain_id}"
                )
                data = await self.redis_client.get(key)

                if data:
                    self._cache_hits += 1
                    result = json.loads(data)
                    # Store in in-memory cache for faster access next time
                    self._memory_cache[cache_key] = result
                    self._memory_cache_ttl[cache_key] = time.time()
                    self._increment_operation_count("get_reasoning_chain")
                    return result
                else:
                    self._cache_misses += 1
                    return None

        except Exception as e:
            simple_log_error(logger, "get_reasoning_chain", e, chain_id=chain_id)
            self._increment_error_count()
            return None

    async def _store_reasoning_pattern_vector(
        self,
        pattern_type: str,
        question: str,
        reasoning_steps: str,
        final_answer: str,
        confidence_score: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Store reasoning pattern with vector embedding"""
        try:
            # Generate embedding from combined text
            combined_text = f"{question} {reasoning_steps} {final_answer}"
            embedding = await self.embedding_generator.generate_embeddings(
                [combined_text]
            )

            # Create record
            record = ReasoningRecord(
                pattern_type=pattern_type,
                question=question,
                reasoning_steps=reasoning_steps,
                final_answer=final_answer,
                confidence_score=confidence_score,
                context=json.dumps(context or {}, default=str),
                embedding=embedding[0] if embedding else [],
            )

            # Store in collection
            collection = await self._get_or_create_collection(
                "reasoning", ReasoningRecord
            )
            await collection.upsert(record)

            logger.debug(f"Stored reasoning pattern with ID: {record.id}")
            return record.id

        except Exception as e:
            simple_log_error(logger, "store_reasoning_pattern_vector", e)
            return None

    # World Model Operations (from ProductionRedisManager + RedisVectorService)
    async def store_world_model(
        self, scenario: str, world_model: WorldModel, abstraction_level: str = "omega1"
    ) -> bool:
        """Store world model with schema-aware key generation"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                # Generate schema-aware key
                scenario_hash = self._generate_scenario_hash(scenario)
                key = f"{self.schema.config.namespace_prefix}:world_model:{scenario_hash}:{abstraction_level}"

                # Serialize world model
                model_data = {
                    "scenario": scenario,
                    "abstraction_level": abstraction_level,
                    "model_type": str(world_model.model_type)
                    if hasattr(world_model, "model_type")
                    else "unknown",
                    "model_level": str(world_model.model_level)
                    if hasattr(world_model, "model_level")
                    else "unknown",
                    "confidence": getattr(world_model, "confidence", 0.0),
                    "state": getattr(world_model, "state", {}),
                    "evidence": [str(e) for e in getattr(world_model, "evidence", [])],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                # Store in Redis with TTL
                ttl = self._get_ttl_for_abstraction_level(abstraction_level)
                await self.redis_client.setex(
                    key, ttl, json.dumps(model_data, default=str)
                )

                # Store vector representation if available
                if self._vector_initialized:
                    await self._store_world_model_vector(
                        model_type=model_data["model_type"],
                        state_data=model_data["state"],
                        confidence=model_data["confidence"],
                    )

                # Update in-memory cache
                cache_key = f"world_model:{scenario}:{abstraction_level}"
                self._memory_cache[cache_key] = model_data
                self._memory_cache_ttl[cache_key] = time.time()

                self._increment_operation_count("store_world_model")
                logger.debug(f"Stored world model for scenario: {scenario}")
                return True

        except Exception as e:
            simple_log_error(logger, "store_world_model", e, scenario=scenario)
            self._increment_error_count()
            return False

    async def _store_world_model_vector(
        self,
        model_type: str,
        state_data: Dict[str, Any],
        confidence: float = 0.0,
        context_keys: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Store world model with vector embedding"""
        try:
            # Serialize state data
            state_str = json.dumps(state_data, sort_keys=True)
            context_keys_str = json.dumps(context_keys or [], sort_keys=True)

            # Delegate to helper
            from .redis_world_model import upsert_world_model_vector

            rec_id = await upsert_world_model_vector(
                store=self.redis_store,
                collections=self._collections,
                embedding_generator=self.embedding_generator,
                model_type=model_type,
                state_data=state_data,
                confidence=confidence,
                context_keys=context_keys,
            )

            logger.debug(f"Stored world model with ID: {rec_id}")
            return rec_id

        except Exception as e:
            simple_log_error(logger, "store_world_model_vector", e)
            return None

    async def retrieve_world_model(
        self, scenario: str, abstraction_level: str = "omega1"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve world model by scenario and abstraction level"""
        # Check in-memory cache first
        cache_key = f"world_model:{scenario}:{abstraction_level}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if (
                time.time() - self._memory_cache_ttl.get(cache_key, 0)
                < DEFAULT_CACHE_TTL
            ):
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]

        if not await self._ensure_connected():
            return None

        try:
            async with self._circuit_breaker:
                scenario_hash = self._generate_scenario_hash(scenario)
                key = f"{self.schema.config.namespace_prefix}:world_model:{scenario_hash}:{abstraction_level}"

                data = await self.redis_client.get(key)
                if data:
                    self._cache_hits += 1
                    result = json.loads(data)

                    # Store in in-memory cache for faster access next time
                    self._memory_cache[cache_key] = result
                    self._memory_cache_ttl[cache_key] = time.time()

                    self._increment_operation_count("retrieve_world_model")
                    return result
                else:
                    self._cache_misses += 1
                    return None

        except Exception as e:
            simple_log_error(logger, "retrieve_world_model", e, scenario=scenario)
            self._increment_error_count()
            return None

    # Knowledge Operations (from RedisMemoryService)
    async def store_knowledge(
        self,
        knowledge_id: str,
        knowledge_data: Dict[str, Any],
        knowledge_type: str = "general",
        tags: Optional[Set[str]] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        """Store knowledge with tagging and categorization"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                from .redis_knowledge import store_knowledge as _store_knowledge

                ok = await _store_knowledge(
                    redis_client=self.redis_client,
                    namespace_prefix=self.schema.config.namespace_prefix,
                    knowledge_id=knowledge_id,
                    knowledge_data=knowledge_data,
                    knowledge_type=knowledge_type,
                    tags=tags,
                    ttl=ttl,
                    memory_cache=self._memory_cache,
                    memory_cache_ttl=self._memory_cache_ttl,
                )
                self._increment_operation_count("store_knowledge")
                logger.debug(f"Stored knowledge: {knowledge_id}")
                return ok

        except Exception as e:
            simple_log_error(logger, "store_knowledge", e, knowledge_id=knowledge_id)
            self._increment_error_count()
            return False

    async def retrieve_knowledge_by_type(
        self, knowledge_type: str
    ) -> List[Dict[str, Any]]:
        """Retrieve all knowledge entries by type"""
        # Check in-memory cache first
        cache_key = f"knowledge_type:{knowledge_type}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if (
                time.time() - self._memory_cache_ttl.get(cache_key, 0)
                < DEFAULT_CACHE_TTL
            ):
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]

        if not await self._ensure_connected():
            return []

        try:
            async with self._circuit_breaker:
                from .redis_knowledge import retrieve_knowledge_by_type as _get_knowledge_by_type

                results = await _get_knowledge_by_type(
                    redis_client=self.redis_client,
                    namespace_prefix=self.schema.config.namespace_prefix,
                    knowledge_type=knowledge_type,
                    memory_cache=self._memory_cache,
                    memory_cache_ttl=self._memory_cache_ttl,
                )
                self._increment_operation_count("retrieve_knowledge_by_type")
                return results

        except Exception as e:
            simple_log_error(
                logger, "retrieve_knowledge_by_type", e, knowledge_type=knowledge_type
            )
            self._increment_error_count()
            return []

    # Session Management (from RedisMemoryService)
    async def create_session(
        self, session_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Create a new session with optional TTL"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                from .redis_session_cache import create_session as _create_session

                ok = await _create_session(
                    redis_client=self.redis_client,
                    namespace_prefix=self.schema.config.namespace_prefix,
                    session_id=session_id,
                    session_data=session_data,
                    ttl=ttl,
                    memory_cache=self._memory_cache,
                    memory_cache_ttl=self._memory_cache_ttl,
                )
                self._increment_operation_count("create_session")
                logger.debug(f"Created session: {session_id}")
                return ok

        except Exception as e:
            simple_log_error(logger, "create_session", e, session_id=session_id)
            self._increment_error_count()
            return False

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data and update last accessed"""
        # Check in-memory cache first
        cache_key = f"session:{session_id}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if (
                time.time() - self._memory_cache_ttl.get(cache_key, 0)
                < DEFAULT_CACHE_TTL
            ):
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]

        if not await self._ensure_connected():
            return None

        try:
            async with self._circuit_breaker:
                from .redis_session_cache import get_session as _get_session

                result = await _get_session(
                    redis_client=self.redis_client,
                    namespace_prefix=self.schema.config.namespace_prefix,
                    session_id=session_id,
                    memory_cache=self._memory_cache,
                    memory_cache_ttl=self._memory_cache_ttl,
                )

                if result is not None:
                    self._cache_hits += 1
                    self._increment_operation_count("get_session")
                    return result
                else:
                    self._cache_misses += 1
                    return None

        except Exception as e:
            simple_log_error(logger, "get_session", e, session_id=session_id)
            self._increment_error_count()
            return None

    # Caching Operations (from RedisMemoryService)
    async def cache_model_result(
        self,
        model_name: str,
        input_hash: str,
        result: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """Cache model result with optional TTL"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                from .redis_session_cache import cache_model_result as _cache_model_result

                ok = await _cache_model_result(
                    redis_client=self.redis_client,
                    namespace_prefix=self.schema.config.namespace_prefix,
                    model_name=model_name,
                    input_hash=input_hash,
                    result=result,
                    ttl=ttl,
                    memory_cache=self._memory_cache,
                    memory_cache_ttl=self._memory_cache_ttl,
                )
                self._increment_operation_count("cache_model_result")
                logger.debug(f"Cached model result for {model_name}:{input_hash}")
                return ok

        except Exception as e:
            simple_log_error(
                logger,
                "cache_model_result",
                e,
                model_name=model_name,
                input_hash=input_hash,
            )
            self._increment_error_count()
            return False

    async def get_cached_model_result(
        self, model_name: str, input_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached model result"""
        # Check in-memory cache first
        cache_key = f"model_cache:{model_name}:{input_hash}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if (
                time.time() - self._memory_cache_ttl.get(cache_key, 0)
                < DEFAULT_CACHE_TTL
            ):
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]

        if not await self._ensure_connected():
            return None

        try:
            async with self._circuit_breaker:
                from .redis_session_cache import get_cached_model_result as _get_cached_model_result

                result = await _get_cached_model_result(
                    redis_client=self.redis_client,
                    namespace_prefix=self.schema.config.namespace_prefix,
                    model_name=model_name,
                    input_hash=input_hash,
                    memory_cache=self._memory_cache,
                    memory_cache_ttl=self._memory_cache_ttl,
                )
                if result is not None:
                    self._cache_hits += 1
                    self._increment_operation_count("get_cached_model_result")
                    return result
                else:
                    self._cache_misses += 1
                    return None

        except Exception as e:
            simple_log_error(
                logger,
                "get_cached_model_result",
                e,
                model_name=model_name,
                input_hash=input_hash,
            )
            self._increment_error_count()
            return None

    # Vector Search Operations
    async def similarity_search(
        self, collection_name: str, query_text: str, limit: int = 10
    ) -> List[Any]:
        """Perform similarity search in specified collection"""
        if not self._vector_initialized:
            return []

        try:
            from .redis_vectors import similarity_search as _sim_search

            results = await _sim_search(
                self._collections, collection_name, query_text, limit
            )
            self._increment_operation_count("similarity_search")
            return results

        except Exception as e:
            simple_log_error(
                logger, "similarity_search", e, collection_name=collection_name
            )
            self._increment_error_count()
            return []

    # Utility Methods
    def _generate_scenario_hash(self, scenario: str) -> str:
        """Generate deterministic hash for scenario identification"""
        return hashlib.sha256(scenario.encode("utf-8")).hexdigest()[:16]

    def _get_ttl_for_abstraction_level(self, level: str) -> int:
        """Get appropriate TTL based on abstraction level"""
        ttl_map = {
            "omega1": REASONING_RESULT_TTL,  # 2 hours
            "omega2": DEFAULT_CACHE_TTL,  # 1 hour
            "omega3": SHORT_CACHE_TTL,  # 5 minutes
            "default": DEFAULT_CACHE_TTL,
        }
        return ttl_map.get(level, ttl_map["default"])

    def generate_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        if args:
            args_hash = hashlib.sha256(
                json.dumps(args, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest()[:8]
            return f"{self.schema.config.namespace_prefix}:cache:{prefix}:{args_hash}"
        else:
            return f"{self.schema.config.namespace_prefix}:cache:{prefix}"

    # Health and Monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        # Periodically clean up expired memory cache entries
        if time.time() - self._last_cleanup_time > 60:  # Clean up every minute
            self._cleanup_expired_memory_cache()

        health_data = {
            "status": "unknown",
            "redis_connected": self._is_connected,
            "vector_store_initialized": self._vector_initialized,
            "collections": list(self._collections.keys()),
            "memory_cache_size": len(self._memory_cache),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if self.enable_monitoring:
            health_data.update(
                {
                    "operation_count": self._operation_count,
                    "error_count": self._error_count,
                    "cache_hits": self._cache_hits,
                    "cache_misses": self._cache_misses,
                    "cache_hit_ratio": self._cache_hits
                    / max(1, self._cache_hits + self._cache_misses),
                }
            )

        try:
            if await self._ensure_connected():
                await self.redis_client.ping()
                health_data["status"] = "healthy"
            else:
                health_data["status"] = "disconnected"
        except Exception as e:
            health_data["status"] = "error"
            health_data["error"] = str(e)

        return health_data

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        return {
            "operations": {
                "total_operations": self._operation_count,
                "total_errors": self._error_count,
                "error_rate": self._error_count / max(1, self._operation_count),
            },
            "cache": {
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "hit_ratio": self._cache_hits
                / max(1, self._cache_hits + self._cache_misses),
                "memory_cache_size": len(self._memory_cache),
            },
            "connection": {
                "is_connected": self._is_connected,
                "vector_initialized": self._vector_initialized,
                "active_collections": len(self._collections),
                "circuit_breaker_state": (
                    str(self._circuit_breaker.state)
                    if hasattr(self._circuit_breaker, "state")
                    else "unknown"
                ),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Batch Operations for Performance
    async def batch_store(self, items: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Store multiple items in batch for better performance"""
        if not await self._ensure_connected():
            return {item.get("id"): False for item in items if item.get("id")}

        results = {}

        try:
            async with self._circuit_breaker:
                pipe = self.redis_client.pipeline()

                for item in items:
                    item_type = item.get("type", "unknown")
                    item_id = item.get("id")
                    data = item.get("data", {})
                    ttl = item.get("ttl")

                    if not item_id:
                        continue

                    key = f"{self.schema.config.namespace_prefix}:{item_type}:{item_id}"
                    serialized_data = json.dumps(data, default=str)

                    if ttl:
                        await pipe.setex(key, ttl, serialized_data)
                    else:
                        await pipe.set(key, serialized_data)

                    results[item_id] = True  # Assume success for now

                await pipe.execute()
                self._increment_operation_count("batch_store")
                logger.debug(f"Batch stored {len(items)} items")

                return results  # All successful

        except Exception as e:
            simple_log_error(logger, "batch_store", e)
            self._increment_error_count()
            # Mark all as failed
            for item in items:
                if item.get("id"):
                    results[item["id"]] = False

        return results

    async def cleanup_expired_keys(self, pattern: str = "*") -> int:
        """Clean up expired keys matching pattern using SCAN with retry"""
        if not await self._ensure_connected():
            return 0

        start_time = time.time()
        try:
            from ..core.async_utils import with_retry
            from .redis_maintenance import cleanup_expired_keys as _cleanup

            ns_pattern = f"{self.schema.config.namespace_prefix}:{pattern}"

            async def _task():
                return await _cleanup(
                    redis_client=self.redis_client, pattern=ns_pattern
                )

            expired_count = await with_retry(_task, retries=2, backoff_base=0.05)

            duration_ms = (time.time() - start_time) * 1000
            log_service_call(
                logger,
                "redis",
                "cleanup_expired_keys",
                True,
                duration_ms=duration_ms,
                expired_count=expired_count,
                pattern=pattern,
            )

            logger.info(f"Cleaned up {expired_count} keys")
            return expired_count

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            wrapped_error = ServiceError(
                f"Redis cleanup failed: {str(e)}", service_name="redis"
            )
            log_domain_error(
                logger, wrapped_error, "cleanup_expired_keys", duration_ms=duration_ms
            )
            return 0

    # Exploration Pattern Operations (from ProductionRedisManager)
    async def store_exploration_pattern(
        self,
        scenario: str,
        trigger_result: TriggerDetectionResult,
        pattern_data: Dict[str, Any],
    ) -> bool:
        """Store an exploration pattern with trigger information"""
        if not await self._ensure_connected():
            return False

        try:
            # Use the triggers list from TriggerDetectionResult
            main_trigger = (
                trigger_result.triggers[0]
                if trigger_result.triggers
                else ExplorationTrigger.NOVEL_SITUATION
            )

            pattern_id = hashlib.md5(
                f"{scenario}{main_trigger.value}".encode()
            ).hexdigest()[:8]
            key = f"{self.schema.config.namespace_prefix}:exploration:trigger_patterns:{main_trigger.value}:{pattern_id}"

            pattern_store_data = {
                "scenario": scenario,
                "trigger_type": main_trigger.value,
                "all_triggers": json.dumps([t.value for t in trigger_result.triggers]),
                "novelty_score": str(trigger_result.novelty_score),
                "complexity_score": str(trigger_result.complexity_score),
                "pattern_data": json.dumps(pattern_data),
                "created": datetime.now(timezone.utc).isoformat(),
                "usage_count": "1",
                "success_rate": "1.0",
            }

            ttl = self._get_ttl_for_abstraction_level(
                "omega1"
            )  # Use default TTL for exploration patterns

            await self.redis_client.setex(
                key, ttl, json.dumps(pattern_store_data, default=str)
            )

            self._increment_operation_count("store_exploration_pattern")
            logger.debug(f"Stored exploration pattern: {key}")
            return True

        except Exception as e:
            simple_log_error(logger, "store_exploration_pattern", e, scenario=scenario)
            self._increment_error_count()
            return False

    async def retrieve_exploration_patterns(
        self, trigger_type: ExplorationTrigger, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve exploration patterns by trigger type"""
        if not await self._ensure_connected():
            return []

        try:
            pattern_key = f"{self.schema.config.namespace_prefix}:exploration:trigger_patterns:{trigger_type.value}*"
            keys = await self.redis_client.keys(pattern_key)

            patterns = []
            for key in keys[:limit]:
                pattern_data = await self.redis_client.get(key)
                if pattern_data:
                    patterns.append(json.loads(pattern_data))

            self._increment_operation_count("retrieve_exploration_patterns")
            logger.debug(f"Retrieved {len(patterns)} patterns for {trigger_type.value}")
            return patterns

        except Exception as e:
            simple_log_error(
                logger,
                "retrieve_exploration_patterns",
                e,
                trigger_type=trigger_type.value if trigger_type else "unknown",
            )
            self._increment_error_count()
            return []

    # Agent Memory Operations (from ProductionRedisManager)
    async def store_agent_memory(
        self, agent_type: str, agent_id: str, memory_data: Dict[str, Any]
    ) -> bool:
        """Store agent memory with proper indexing"""
        if not await self._ensure_connected():
            return False

        try:
            key = f"{self.schema.config.namespace_prefix}:agents:agent_memories:{agent_type}:{agent_id}"

            memory_store_data = {
                "agent_type": agent_type,
                "agent_id": agent_id,
                "memory_data": json.dumps(memory_data),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "memory_size": str(len(json.dumps(memory_data))),
                "access_count": "1",
            }

            ttl = self._get_ttl_for_abstraction_level(
                "omega1"
            )  # Use default TTL for agent memories

            await self.redis_client.setex(
                key, ttl, json.dumps(memory_store_data, default=str)
            )

            self._increment_operation_count("store_agent_memory")
            logger.debug(f"Stored agent memory: {key}")
            return True

        except Exception as e:
            simple_log_error(
                logger,
                "store_agent_memory",
                e,
                agent_type=agent_type,
                agent_id=agent_id,
            )
            self._increment_error_count()
            return False

    async def retrieve_agent_memory(
        self, agent_type: str, agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve agent memory data"""
        if not await self._ensure_connected():
            return None

        try:
            key = f"{self.schema.config.namespace_prefix}:agents:agent_memories:{agent_type}:{agent_id}"
            data = await self.redis_client.get(key)

            if data:
                self._cache_hits += 1
                result = json.loads(data)
                # Increment access count
                await self.redis_client.hincrby(key, "access_count", 1)
                self._increment_operation_count("retrieve_agent_memory")
                logger.debug(f"Retrieved agent memory: {key}")
                return result
            else:
                self._cache_misses += 1
                return None

        except Exception as e:
            simple_log_error(
                logger,
                "retrieve_agent_memory",
                e,
                agent_type=agent_type,
                agent_id=agent_id,
            )
            self._increment_error_count()
            return None

    # Similar World Models Search (from ProductionRedisManager)
    async def search_similar_world_models(
        self, domain: str, confidence_threshold: float = 0.7, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar world models by domain and confidence"""
        if not await self._ensure_connected():
            return []

        try:
            # Use Redis SCAN to find matching keys
            pattern = f"{self.schema.config.namespace_prefix}:world_model:*"
            similar_models = []

            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor, match=pattern, count=100
                )

                for key in keys:
                    model_data = await self.redis_client.get(key)
                    if model_data:
                        decoded_data = json.loads(model_data)
                        if (
                            decoded_data.get("domain") == domain
                            and float(decoded_data.get("confidence", 0))
                            >= confidence_threshold
                        ):
                            similar_models.append(decoded_data)

                    if len(similar_models) >= limit:
                        break

                if cursor == 0 or len(similar_models) >= limit:
                    break

            search_results = similar_models[:limit]
            logger.debug(
                f"Found {len(search_results)} similar world models for domain: {domain}"
            )
            return search_results

        except Exception as e:
            simple_log_error(logger, "search_similar_world_models", e, domain=domain)
            return []

    # Basic Redis Operations for Agent Orchestration
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis"""
        if not await self._ensure_connected():
            return False

        try:
            if expire:
                await self.redis_client.setex(key, expire, value)
            else:
                await self.redis_client.set(key, value)
            self._increment_operation_count("set")
            return True
        except Exception as e:
            simple_log_error(logger, "set", e, key=key)
            self._increment_error_count()
            return False

    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis by key"""
        if not await self._ensure_connected():
            return None

        try:
            value = await self.redis_client.get(key)
            self._increment_operation_count("get")
            return value.decode("utf-8") if value else None
        except Exception as e:
            simple_log_error(logger, "get", e, key=key)
            self._increment_error_count()
            return None

    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        if not await self._ensure_connected():
            return False

        try:
            await self.redis_client.delete(key)
            self._increment_operation_count("delete")
            return True
        except Exception as e:
            simple_log_error(logger, "delete", e, key=key)
            self._increment_error_count()
            return False

    async def keys(self, pattern: str) -> List[str]:
        """Get all keys matching a pattern"""
        if not await self._ensure_connected():
            return []

        try:
            keys = await self.redis_client.keys(pattern)
            self._increment_operation_count("keys")
            return [key.decode("utf-8") for key in keys]
        except Exception as e:
            simple_log_error(logger, "keys", e, pattern=pattern)
            self._increment_error_count()
            return []

    async def lpush(self, key: str, value: str) -> bool:
        """Push a value to the left of a list"""
        if not await self._ensure_connected():
            return False

        try:
            await self.redis_client.lpush(key, value)
            self._increment_operation_count("lpush")
            return True
        except Exception as e:
            simple_log_error(logger, "lpush", e, key=key)
            self._increment_error_count()
            return False

    async def rpop(self, key: str) -> Optional[str]:
        """Pop a value from the right of a list"""
        if not await self._ensure_connected():
            return None

        try:
            value = await self.redis_client.rpop(key)
            self._increment_operation_count("rpop")
            return value.decode("utf-8") if value else None
        except Exception as e:
            simple_log_error(logger, "rpop", e, key=key)
            self._increment_error_count()
            return None

    # Factory Functions (from ProductionRedisManager)
    async def create_production_redis_manager(
        self, redis_url: str = "redis://localhost:6379"
    ) -> "UnifiedRedisService":
        """Create and connect a production Redis manager (factory function)"""
        config = RedisConnectionConfig(redis_url=redis_url)
        service = UnifiedRedisService(
            config=config, schema=create_production_schema(), enable_monitoring=True
        )
        await service.connect()
        return service

    async def create_development_redis_manager(
        self, redis_url: str = "redis://localhost:6379"
    ) -> "UnifiedRedisService":
        """Create and connect a development Redis manager (factory function)"""
        config = RedisConnectionConfig(redis_url=redis_url)
        service = UnifiedRedisService(
            config=config, schema=create_development_schema(), enable_monitoring=True
        )
        await service.connect()
        return service

    # Schema-Aware MSA Data Operations
    async def store_knowledge_base(
        self,
        knowledge_base: "KnowledgeBase",
        request_id: str,
        embedding_vector: Optional[List[float]] = None,
    ) -> bool:
        """Store knowledge base with schema-aware structure and optional vector embedding"""
        try:
            async with self._circuit_breaker:
                # Generate key using schema pattern
                key = f"kb:{request_id}"

                # Convert dataclass to dict for JSON storage
                if hasattr(knowledge_base, "__dict__"):
                    kb_data = {
                        "request_id": request_id,
                        "entities": knowledge_base.entities,
                        "relationships": knowledge_base.relationships,
                        "constraints": knowledge_base.constraints,
                        "assumptions": knowledge_base.assumptions,
                        "domain_knowledge": knowledge_base.domain_knowledge,
                        "confidence": knowledge_base.confidence,
                        "extraction_metadata": knowledge_base.extraction_metadata,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                else:
                    kb_data = knowledge_base

                # Store as JSON document with TTL
                await self.redis_client.json().set(key, "$", kb_data)
                await self.redis_client.expire(key, 86400)  # 24 hours

                # Add to domain index if domain is specified
                domain = kb_data.get("domain_knowledge", {}).get("medical_domain")
                if domain:
                    await self.redis_client.sadd(f"idx:domain:{domain}", key)

                # Add to confidence ranking
                confidence = kb_data.get("confidence", 0.0)
                await self.redis_client.zadd(
                    "idx:confidence:knowledge_bases", {key: confidence}
                )

                # Add to request tracking
                await self.redis_client.sadd(f"idx:request:{request_id}", key)

                # Store vector embedding if provided
                if embedding_vector and self._vector_initialized:
                    await self._store_vector_embedding(key, embedding_vector)

                log_service_call(
                    logger,
                    "store_knowledge_base",
                    {"key": key, "confidence": confidence},
                )
                return True

        except Exception as e:
            log_domain_error(
                logger, "store_knowledge_base", e, {"request_id": request_id}
            )
            return False

    async def store_model_specification(
        self,
        model_spec: "ModelSpecification",
        request_id: str,
        embedding_vector: Optional[List[float]] = None,
    ) -> bool:
        """Store model specification with schema-aware structure"""
        try:
            async with self._circuit_breaker:
                key = f"ms:{request_id}"

                # Convert to dict for JSON storage
                if hasattr(model_spec, "__dict__"):
                    ms_data = {
                        "request_id": request_id,
                        "variables": model_spec.variables,
                        "distributions": model_spec.distributions,
                        "dependencies": model_spec.dependencies,
                        "constraints": model_spec.constraints,
                        "priors": model_spec.priors,
                        "model_type": model_spec.model_type,
                        "complexity_score": model_spec.complexity_score,
                        "specification_metadata": model_spec.specification_metadata,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                else:
                    ms_data = model_spec

                # Store with 2-hour TTL
                await self.redis_client.json().set(key, "$", ms_data)
                await self.redis_client.expire(key, 7200)  # 2 hours

                # Add to request tracking
                await self.redis_client.sadd(f"idx:request:{request_id}", key)

                # Store vector embedding if provided
                if embedding_vector and self._vector_initialized:
                    await self._store_vector_embedding(key, embedding_vector)

                log_service_call(
                    logger,
                    "store_model_specification",
                    {"key": key, "model_type": ms_data.get("model_type")},
                )
                return True

        except Exception as e:
            log_domain_error(
                logger, "store_model_specification", e, {"request_id": request_id}
            )
            return False

    async def store_pipeline_result(
        self,
        pipeline_result: "PipelineResult",
        request_id: str,
    ) -> bool:
        """Store complete pipeline result with schema-aware structure"""
        try:
            async with self._circuit_breaker:
                key = f"pr:pipeline_{request_id}"

                # Convert to dict for JSON storage
                if hasattr(pipeline_result, "__dict__"):
                    pr_data = {
                        "request_id": request_id,
                        "scenario": pipeline_result.scenario,
                        "reasoning_mode": str(pipeline_result.reasoning_mode),
                        "knowledge_base": f"kb:{request_id}"
                        if pipeline_result.knowledge_base
                        else None,
                        "model_specification": f"ms:{request_id}"
                        if pipeline_result.model_specification
                        else None,
                        "synthesis_result": f"sr:{request_id}"
                        if pipeline_result.synthesis_result
                        else None,
                        "inference_result": f"ir:{request_id}"
                        if pipeline_result.inference_result
                        else None,
                        "confidence_metrics": (
                            pipeline_result.confidence_metrics.__dict__
                            if pipeline_result.confidence_metrics
                            else None
                        ),
                        "reasoning_steps": [
                            step.__dict__ if hasattr(step, "__dict__") else step
                            for step in pipeline_result.reasoning_steps
                        ],
                        "execution_time": pipeline_result.execution_time,
                        "success": pipeline_result.success,
                        "error_message": pipeline_result.error_message,
                        "metadata": pipeline_result.metadata,
                        "timestamp": pipeline_result.timestamp,
                    }
                else:
                    pr_data = pipeline_result

                # Store with 24-hour TTL
                await self.redis_client.json().set(key, "$", pr_data)
                await self.redis_client.expire(key, 86400)  # 24 hours

                # Add to request tracking
                await self.redis_client.sadd(f"idx:request:{request_id}", key)

                log_service_call(
                    logger,
                    "store_pipeline_result",
                    {"key": key, "success": pr_data.get("success")},
                )
                return True

        except Exception as e:
            log_domain_error(
                logger, "store_pipeline_result", e, {"request_id": request_id}
            )
            return False

    async def get_request_artifacts(self, request_id: str) -> Dict[str, Any]:
        """Get all artifacts associated with a request"""
        try:
            async with self._circuit_breaker:
                # Get all artifact keys for this request
                artifact_keys = await self.redis_client.smembers(
                    f"idx:request:{request_id}"
                )

                artifacts = {}
                for key in artifact_keys:
                    try:
                        # Determine artifact type from key prefix
                        if key.startswith("kb:"):
                            artifact_type = "knowledge_base"
                        elif key.startswith("ms:"):
                            artifact_type = "model_specification"
                        elif key.startswith("sr:"):
                            artifact_type = "synthesis_result"
                        elif key.startswith("ir:"):
                            artifact_type = "inference_result"
                        elif key.startswith("pr:"):
                            artifact_type = "pipeline_result"
                        else:
                            artifact_type = "unknown"

                        # Retrieve the data
                        data = await self.redis_client.json().get(key)
                        artifacts[artifact_type] = data

                    except Exception as e:
                        log_domain_error(
                            logger, "get_request_artifacts", e, {"key": key}
                        )
                        continue

                return artifacts

        except Exception as e:
            log_domain_error(
                logger, "get_request_artifacts", e, {"request_id": request_id}
            )
            return {}

    async def _store_vector_embedding(
        self, key: str, embedding_vector: List[float]
    ) -> bool:
        """Helper method to store vector embedding for semantic search"""
        try:
            if not self._vector_initialized or not self.embedding_generator:
                return False

            # Store vector in hash field for vector search
            await self.redis_client.hset(key, "embedding", json.dumps(embedding_vector))
            return True

        except Exception as e:
            log_domain_error(logger, "_store_vector_embedding", e, {"key": key})
            return False


# Factory Functions
async def create_unified_redis_service(
    redis_url: str = "redis://localhost:6379",
    embedding_generator: Optional[EmbeddingGeneratorBase] = None,
    environment: str = "production",
) -> UnifiedRedisService:
    """Create and initialize a unified Redis service"""

    config = RedisConnectionConfig(redis_url=redis_url)

    if environment == "production":
        schema = create_production_schema()
    else:
        schema = create_development_schema()

    service = UnifiedRedisService(
        config=config,
        embedding_generator=embedding_generator,
        schema=schema,
        enable_monitoring=True,
    )

    await service.connect()

    if embedding_generator:
        await service.initialize_vector_store()

    return service


async def create_redis_service_from_config(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
    max_connections: int = 50,
    **kwargs,
) -> UnifiedRedisService:
    """Create Redis service from individual config parameters"""

    config = RedisConnectionConfig(
        host=host,
        port=port,
        db=db,
        password=password,
        max_connections=max_connections,
        **kwargs,
    )

    service = UnifiedRedisService(config=config)
    await service.connect()
    return service


# Backward-compatible factory expected by tests and other modules
async def create_production_redis_manager(
    redis_url: str = "redis://localhost:6379",
    embedding_generator: Optional[EmbeddingGeneratorBase] = None,
) -> UnifiedRedisService:
    """Create a production-configured UnifiedRedisService and connect it.

    This wrapper exists to maintain compatibility with modules/tests that
    import `create_production_redis_manager` directly from this module.
    """
    return await create_unified_redis_service(
        redis_url=redis_url,
        embedding_generator=embedding_generator,
        environment="production",
    )
