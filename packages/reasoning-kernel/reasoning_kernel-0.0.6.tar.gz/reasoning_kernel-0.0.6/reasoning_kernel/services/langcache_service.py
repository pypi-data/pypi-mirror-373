"""
LangCache Service for Redis

This module implements a comprehensive LangCache service that integrates with Redis LangCache
for AI model caching and optimization. LangCache provides intelligent caching for AI workloads,
reducing latency and costs by caching model responses and embeddings.

Features:
- Model response caching with TTL
- Embedding caching and similarity search
- Cache warming strategies
- Performance monitoring and metrics
- Integration with existing Redis services
- Circuit breaker protection
- Async operations support

Based on Redis LangCache: https://redis.io/docs/latest/develop/ai/langcache/
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple

from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, ServiceType
from reasoning_kernel.config.settings import LangCacheConfig

try:
    import aioredis

    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle both missing dependency and Python 3.13 compatibility issues
    aioredis = None
    REDIS_AVAILABLE = False
    print(f"Warning: aioredis not available: {e}")

try:
    import httpx
except ImportError:
    httpx = None


logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached entry with metadata"""

    key: str
    value: Any
    ttl_seconds: int
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        if self.ttl_seconds <= 0:
            return False  # No expiration
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl_seconds)


@dataclass
class CacheStats:
    """Cache performance statistics"""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    sets: int = 0
    size_bytes: int = 0
    warmup_operations: int = 0

    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class LangCacheService:
    """
    Redis LangCache Service for AI model caching and optimization

    This service provides intelligent caching for AI workloads including:
    - Model response caching
    - Embedding caching
    - Prompt caching
    - Performance monitoring
    - Cache warming strategies
    """

    def __init__(self, config: LangCacheConfig):
        """
        Initialize LangCache service

        Args:
            config: LangCache configuration
        """
        self.config = config
        self.logger = get_logger(__name__)

        # Circuit breaker for resilience
        circuit_config = CircuitBreakerConfig(
            service_type=ServiceType.REDIS, failure_threshold=5, timeout_duration=60.0
        )
        self.circuit_breaker = CircuitBreaker("langcache", circuit_config)

        # HTTP client for API calls
        self.http_client: Optional[Any] = None
        self.redis_client: Optional[Any] = None

        # Cache statistics
        self.stats = CacheStats()

        # Cache warming patterns
        self.warming_patterns = ["common_prompts", "frequent_embeddings", "popular_responses"]

        self.logger.info("LangCache service initialized", cache_id=config.cache_id)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()

    async def initialize(self) -> None:
        """Initialize the LangCache service"""
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis dependencies not available")

        try:
            # Initialize HTTP client for LangCache API
            if httpx is None:
                raise RuntimeError("httpx dependency not available")
            self.http_client = httpx.AsyncClient(
                base_url=self.config.endpoint,
                headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"},
                timeout=30.0,
            )

            # Initialize Redis client for local caching
            if aioredis is None:
                raise RuntimeError("redis dependency not available")
            self.redis_client = aioredis.from_url(
                "redis://localhost:6379/0",  # Local Redis for additional caching
                encoding="utf-8",
                decode_responses=True,
            )

            # Test connection
            await self._test_connection()

            self.logger.info("LangCache service initialized successfully")

        except Exception as e:
            self.logger.error("Failed to initialize LangCache service", error=str(e))
            raise

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.http_client:
            await self.http_client.aclose()
        if self.redis_client:
            await self.redis_client.close()

        self.logger.info("LangCache service cleaned up")

    async def _test_connection(self) -> None:
        """Test connection to LangCache service"""
        if self.http_client is None:
            raise RuntimeError("HTTP client not available")

        try:
            # Test basic connectivity
            response = await self.http_client.get("/health")
            if response.status_code != 200:
                raise RuntimeError(f"LangCache health check failed: {response.status_code}")

            self.logger.info("LangCache connection test successful")

        except Exception as e:
            self.logger.error("LangCache connection test failed", error=str(e))
            raise

    def _generate_cache_key(self, content: Union[str, Dict, List]) -> str:
        """Generate a deterministic cache key from content"""
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)

        # Create hash of content
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]

        return f"langcache:{self.config.cache_id}:{content_hash}"

    async def cache_model_response(
        self,
        prompt: str,
        response: str,
        model_name: str,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Cache a model response

        Args:
            prompt: Input prompt
            response: Model response
            model_name: Name of the model used
            ttl_seconds: Time to live in seconds (uses default if None)
            metadata: Additional metadata

        Returns:
            Cache key used for storage
        """
        if not self.config.enable_caching:
            return ""

        try:
            cache_key = self._generate_cache_key(prompt)
            ttl = ttl_seconds or self.config.default_ttl_seconds

            cache_data = {
                "prompt": prompt,
                "response": response,
                "model": model_name,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
                "ttl": ttl,
            }

            # Store in LangCache via API
            await self._store_in_langcache(cache_key, cache_data, ttl)

            # Also store locally in Redis for faster access
            if self.redis_client is not None:
                await self.redis_client.setex(f"local:{cache_key}", ttl, json.dumps(cache_data))

            self.stats.sets += 1
            self.logger.debug("Model response cached", cache_key=cache_key, model=model_name)

            return cache_key

        except Exception as e:
            self.logger.error("Failed to cache model response", error=str(e))
            return ""

    async def get_cached_response(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached model response

        Args:
            prompt: Input prompt to search for

        Returns:
            Cached response data or None if not found
        """
        if not self.config.enable_caching:
            return None

        try:
            cache_key = self._generate_cache_key(prompt)

            # Try local Redis first for faster access
            if self.redis_client is not None:
                local_data = await self.redis_client.get(f"local:{cache_key}")
                if local_data:
                    self.stats.hits += 1
                    return json.loads(local_data)

            # Fallback to LangCache API
            cached_data = await self._retrieve_from_langcache(cache_key)
            if cached_data:
                self.stats.hits += 1
                # Store locally for future fast access
                if self.redis_client is not None:
                    await self.redis_client.setex(
                        f"local:{cache_key}",
                        cached_data.get("ttl", self.config.default_ttl_seconds),
                        json.dumps(cached_data),
                    )
                return cached_data

            self.stats.misses += 1
            return None

        except Exception as e:
            self.logger.error("Failed to retrieve cached response", error=str(e))
            return None

    async def cache_embedding(
        self, text: str, embedding: List[float], model_name: str, ttl_seconds: Optional[int] = None
    ) -> str:
        """
        Cache text embeddings

        Args:
            text: Original text
            embedding: Embedding vector
            model_name: Embedding model name
            ttl_seconds: Time to live in seconds

        Returns:
            Cache key used for storage
        """
        if not self.config.enable_caching:
            return ""

        try:
            cache_key = self._generate_cache_key(text)
            ttl = ttl_seconds or self.config.default_ttl_seconds

            embedding_data = {
                "text": text,
                "embedding": embedding,
                "model": model_name,
                "dimensions": len(embedding),
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
            }

            # Store in LangCache
            await self._store_in_langcache(cache_key, embedding_data, ttl)

            # Store locally
            if self.redis_client is not None:
                await self.redis_client.setex(f"embedding:{cache_key}", ttl, json.dumps(embedding_data))

            self.stats.sets += 1
            self.logger.debug("Embedding cached", cache_key=cache_key, model=model_name)

            return cache_key

        except Exception as e:
            self.logger.error("Failed to cache embedding", error=str(e))
            return ""

    async def get_cached_embedding(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached embedding

        Args:
            text: Text to search for

        Returns:
            Cached embedding data or None if not found
        """
        if not self.config.enable_caching:
            return None

        try:
            cache_key = self._generate_cache_key(text)

            # Try local cache first
            if self.redis_client is not None:
                local_data = await self.redis_client.get(f"embedding:{cache_key}")
                if local_data:
                    self.stats.hits += 1
                    return json.loads(local_data)

            # Fallback to LangCache API
            cached_data = await self._retrieve_from_langcache(cache_key)
            if cached_data:
                self.stats.hits += 1
                # Store locally
                if self.redis_client is not None:
                    await self.redis_client.setex(
                        f"embedding:{cache_key}",
                        cached_data.get("ttl", self.config.default_ttl_seconds),
                        json.dumps(cached_data),
                    )
                return cached_data

            self.stats.misses += 1
            return None

        except Exception as e:
            self.logger.error("Failed to retrieve cached embedding", error=str(e))
            return None

    async def find_similar_embeddings(
        self, query_embedding: List[float], limit: int = 10, threshold: float = 0.8
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find similar embeddings using vector similarity search

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)

        Returns:
            List of (embedding_data, similarity_score) tuples
        """
        try:
            # This would use LangCache's vector search capabilities
            # For now, we'll implement a basic similarity search
            similar_results = []

            # Get all cached embeddings (in production, this would be optimized)
            if self.redis_client is not None:
                keys = await self.redis_client.keys("embedding:langcache:*")

                for key in keys[:limit]:  # Limit for performance
                    data_str = await self.redis_client.get(key)
                    if data_str:
                        data = json.loads(data_str)
                        embedding = data["embedding"]

                        # Calculate cosine similarity
                        similarity = self._cosine_similarity(query_embedding, embedding)

                        if similarity >= threshold:
                            similar_results.append((data, similarity))

            # Sort by similarity (highest first)
            similar_results.sort(key=lambda x: x[1], reverse=True)

            return similar_results[:limit]

        except Exception as e:
            self.logger.error("Failed to find similar embeddings", error=str(e))
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def _store_in_langcache(self, cache_key: str, data: Dict[str, Any], ttl_seconds: int) -> None:
        """Store data in LangCache via API"""
        if self.http_client is None:
            raise RuntimeError("HTTP client not available")

        try:
            payload = {"key": cache_key, "value": data, "ttl": ttl_seconds}

            response = await self.http_client.post("/cache", json=payload)

            if response.status_code not in [200, 201]:
                raise RuntimeError(f"LangCache API error: {response.status_code}")

        except Exception as e:
            self.logger.error("Failed to store in LangCache", error=str(e))
            raise

    async def _retrieve_from_langcache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from LangCache via API"""
        if self.http_client is None:
            return None

        try:
            response = await self.http_client.get(f"/cache/{cache_key}")

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise RuntimeError(f"LangCache API error: {response.status_code}")

        except Exception as e:
            self.logger.error("Failed to retrieve from LangCache", error=str(e))
            raise

    async def warmup_cache(self, patterns: Optional[List[str]] = None) -> None:
        """
        Warm up the cache with common patterns

        Args:
            patterns: List of warming patterns to use
        """
        if not self.config.enable_caching:
            return

        patterns = patterns or self.warming_patterns

        try:
            self.logger.info("Starting cache warmup", patterns=patterns)

            for pattern in patterns:
                # Implement pattern-specific warming logic
                if pattern == "common_prompts":
                    await self._warmup_common_prompts()
                elif pattern == "frequent_embeddings":
                    await self._warmup_frequent_embeddings()
                elif pattern == "popular_responses":
                    await self._warmup_popular_responses()

            self.stats.warmup_operations += 1
            self.logger.info("Cache warmup completed")

        except Exception as e:
            self.logger.error("Cache warmup failed", error=str(e))

    async def _warmup_common_prompts(self) -> None:
        """Warm up cache with common prompts"""
        common_prompts = [
            "Hello, how are you?",
            "What is the weather like?",
            "Tell me a joke",
            "Explain quantum computing",
            "What are the latest news?",
        ]

        for prompt in common_prompts:
            # Pre-cache these prompts (would normally call actual model)
            cache_key = self._generate_cache_key(prompt)
            if self.redis_client is not None:
                await self.redis_client.setex(
                    f"warmup:{cache_key}",
                    self.config.default_ttl_seconds,
                    json.dumps({"prompt": prompt, "warmed": True}),
                )

    async def _warmup_frequent_embeddings(self) -> None:
        """Warm up cache with frequent embedding patterns"""
        # This would typically load from a dataset of common texts
        pass

    async def _warmup_popular_responses(self) -> None:
        """Warm up cache with popular response patterns"""
        # This would typically load from historical response data
        pass

    async def clear_cache(self, pattern: str = "*") -> int:
        """
        Clear cache entries matching a pattern

        Args:
            pattern: Glob pattern to match keys

        Returns:
            Number of keys cleared
        """
        try:
            # Clear local Redis cache
            if self.redis_client is not None:
                local_keys = await self.redis_client.keys(f"*{pattern}*")
                if local_keys:
                    await self.redis_client.delete(*local_keys)
                    cleared_count = len(local_keys)
                else:
                    cleared_count = 0
            else:
                cleared_count = 0

            # Clear LangCache via API (if supported)
            # This would depend on LangCache API capabilities

            self.logger.info("Cache cleared", pattern=pattern, cleared_count=cleared_count)

            return cleared_count

        except Exception as e:
            self.logger.error("Failed to clear cache", error=str(e))
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics

        Returns:
            Dictionary with cache statistics
        """
        try:
            # Get Redis memory info
            redis_info = {}
            if self.redis_client is not None:
                redis_info = await self.redis_client.info("memory")

            stats = {
                "cache_stats": {
                    "hits": self.stats.hits,
                    "misses": self.stats.misses,
                    "hit_ratio": self.stats.hit_ratio,
                    "sets": self.stats.sets,
                    "evictions": self.stats.evictions,  # Fixed: was evict, should be evictions
                    "warmup_operations": self.stats.warmup_operations,
                },
                "redis_memory": {
                    "used_memory": redis_info.get("used_memory"),
                    "used_memory_human": redis_info.get("used_memory_human"),
                    "max_memory": redis_info.get("max_memory"),
                },
                "configuration": {
                    "cache_id": self.config.cache_id,
                    "enable_caching": self.config.enable_caching,
                    "default_ttl": self.config.default_ttl_seconds,
                    "max_cache_size_mb": self.config.max_cache_size_mb,
                },
            }

            return stats

        except Exception as e:
            self.logger.error("Failed to get cache stats", error=str(e))
            return {}

    async def health_check(self) -> bool:
        """Check if LangCache service is healthy."""
        if self.http_client is None:
            return False

        try:
            response = await self.http_client.get("/health")
            return response.status_code == 200
        except Exception as e:
            self.logger.error("LangCache health check failed", error=str(e))
            return False


# Global service instance
_langcache_service: Optional[LangCacheService] = None


async def get_langcache_service() -> LangCacheService:
    """
    Get or create the global LangCache service instance

    Returns:
        LangCacheService instance
    """
    global _langcache_service

    if _langcache_service is None:
        try:
            config = LangCacheConfig.from_env()
            _langcache_service = LangCacheService(config)
            await _langcache_service.initialize()
        except Exception as e:
            logger.error("Failed to initialize LangCache service", error=str(e))
            raise

    return _langcache_service


async def cache_model_response(prompt: str, response: str, model_name: str, ttl_seconds: Optional[int] = None) -> str:
    """
    Convenience function to cache a model response

    Args:
        prompt: Input prompt
        response: Model response
        model_name: Model name
        ttl_seconds: TTL in seconds

    Returns:
        Cache key
    """
    service = await get_langcache_service()
    return await service.cache_model_response(prompt, response, model_name, ttl_seconds)


async def get_cached_response(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get a cached response

    Args:
        prompt: Input prompt

    Returns:
        Cached response data or None
    """
    service = await get_langcache_service()
    return await service.get_cached_response(prompt)


async def cache_embedding(text: str, embedding: List[float], model_name: str, ttl_seconds: Optional[int] = None) -> str:
    """
    Convenience function to cache an embedding

    Args:
        text: Original text
        embedding: Embedding vector
        model_name: Model name
        ttl_seconds: TTL in seconds

    Returns:
        Cache key
    """
    service = await get_langcache_service()
    return await service.cache_embedding(text, embedding, model_name, ttl_seconds)


async def get_cached_embedding(text: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get a cached embedding

    Args:
        text: Original text

    Returns:
        Cached embedding data or None
    """
    service = await get_langcache_service()
    return await service.get_cached_embedding(text)
