# -*- coding: utf-8 -*-
"""
Optimized Memory Service with Redis Integration

High-performance memory service that integrates with UnifiedRedisService
for production-ready save and search operations.
"""

import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..monitoring.tracing import trace_operation
from ..services.unified_redis_service import UnifiedRedisService

logger = logging.getLogger(__name__)


@dataclass
class MemoryRecord:
    """Optimized memory record with minimal overhead"""

    id: str
    text: str
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    collection: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "text": self.text,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "collection": self.collection,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        """Create from dictionary"""
        return cls(
            id=data.get("id", ""),
            text=data.get("text", ""),
            embedding=data.get("embedding", []),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", time.time()),
            collection=data.get("collection", ""),
        )


class OptimizedMemoryService:
    """
    High-performance memory service with Redis integration.

    Features:
    - Async batch operations for better performance
    - Connection pooling and circuit breaker integration
    - Optimized embedding generation with caching
    - Memory-efficient record storage
    - Comprehensive error handling and monitoring
    """

    def __init__(
        self,
        redis_service: UnifiedRedisService,
        embedding_service: Optional[Any] = None,
        max_batch_size: int = 100,
        enable_caching: bool = True,
    ):
        self.redis_service = redis_service
        self.embedding_service = embedding_service
        self.max_batch_size = max_batch_size
        self.enable_caching = enable_caching

        # Thread pool for CPU-bound embedding generation
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="embedding")

        # Local cache for frequently accessed records
        self._local_cache: Dict[str, MemoryRecord] = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_timestamps: Dict[str, float] = {}

        logger.info("OptimizedMemoryService initialized")

    async def _generate_embedding_async(self, text: str) -> List[float]:
        """Generate embeddings asynchronously using thread pool"""
        if not self.embedding_service:
            # Return zero vector as fallback
            return [0.0] * 384  # Common embedding dimension

        try:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(self.executor, self.embedding_service.generate_embedding, text)
            return embedding
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return [0.0] * 384

    def _get_cache_key(self, collection: str, record_id: str) -> str:
        """Generate cache key for local cache"""
        return f"{collection}:{record_id}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if not self.enable_caching:
            return False

        timestamp = self._cache_timestamps.get(cache_key, 0)
        return time.time() - timestamp < self._cache_ttl

    def _update_cache(self, record: MemoryRecord):
        """Update local cache with record"""
        if not self.enable_caching:
            return

        cache_key = self._get_cache_key(record.collection, record.id)
        self._local_cache[cache_key] = record
        self._cache_timestamps[cache_key] = time.time()

    def _get_from_cache(self, collection: str, record_id: str) -> Optional[MemoryRecord]:
        """Get record from local cache"""
        if not self.enable_caching:
            return None

        cache_key = self._get_cache_key(collection, record_id)
        if self._is_cache_valid(cache_key):
            return self._local_cache.get(cache_key)
        return None

    @trace_operation("save_memory_record")
    async def save_information_async(
        self,
        collection: str,
        text: str,
        record_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Save information to memory with optimized performance.

        Args:
            collection: Collection name
            text: Text content to save
            record_id: Unique record identifier
            description: Optional description
            metadata: Additional metadata

        Returns:
            Success status
        """
        try:
            # Check cache first
            cached_record = self._get_from_cache(collection, record_id)
            if cached_record and cached_record.text == text:
                logger.debug(f"Record {record_id} already exists in cache")
                return True

            # Generate embedding asynchronously
            embedding = await self._generate_embedding_async(text)

            # Create memory record
            record = MemoryRecord(
                id=record_id,
                text=text,
                embedding=embedding,
                collection=collection,
                metadata=metadata or {},
            )

            if description:
                record.metadata["description"] = description

            # Store in Redis using batch operation for better performance
            store_data = {
                "type": f"memory:{collection}",
                "id": record_id,
                "data": record.to_dict(),
                "ttl": 86400,  # 24 hours
            }

            results = await self.redis_service.batch_store([store_data])
            success = results.get(record_id, False)

            if success:
                # Update local cache
                self._update_cache(record)
                logger.info(f"Saved memory record {record_id} to collection {collection}")
            else:
                logger.error(f"Failed to save memory record {record_id}")

            return success

        except Exception as e:
            logger.error(f"Error saving memory record {record_id}: {e}")
            return False

    @trace_operation("search_memory_records")
    async def search_async(
        self,
        collection: str,
        query: str,
        limit: int = 10,
        min_relevance_score: float = 0.7,
        use_vector_search: bool = True,
    ) -> List[MemoryRecord]:
        """
        Search memory records with optimized performance.

        Args:
            collection: Collection to search in
            query: Search query
            limit: Maximum results to return
            min_relevance_score: Minimum relevance threshold
            use_vector_search: Whether to use vector similarity search

        Returns:
            List of matching memory records
        """
        try:
            results = []

            if use_vector_search and self.embedding_service:
                # Use vector similarity search for better results
                vector_results = await self.redis_service.similarity_search(
                    collection_name=f"memory:{collection}",
                    query_text=query,
                    limit=limit,
                )

                for result in vector_results:
                    if isinstance(result, dict):
                        record = MemoryRecord.from_dict(result)
                        # Calculate simple relevance score based on embedding similarity
                        if hasattr(result, "score"):
                            score = result.get("score", 0.0)
                            if score >= min_relevance_score:
                                results.append(record)
                        else:
                            results.append(record)
            else:
                # Fallback to text-based search using Redis keys
                if not self.redis_service.redis_client:
                    logger.warning("Redis client not available for search")
                    return []

                pattern = f"rk:memory:{collection}:*"
                keys = await self.redis_service.redis_client.keys(pattern)

                for key in keys[:limit]:  # Limit keys to avoid excessive processing
                    try:
                        data = await self.redis_service.redis_client.get(key)
                        if data:
                            record_data = json.loads(data)
                            record = MemoryRecord.from_dict(record_data)

                            # Simple text matching for fallback
                            if query.lower() in record.text.lower():
                                results.append(record)
                    except Exception as e:
                        logger.warning(f"Error processing key {key}: {e}")
                        continue

            logger.info(f"Found {len(results)} memory records for query '{query}' in {collection}")
            return results[:limit]

        except Exception as e:
            logger.error(f"Error searching memory collection {collection}: {e}")
            return []

    @trace_operation("batch_save_memory")
    async def batch_save_async(self, collection: str, records: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Batch save multiple memory records for optimal performance.

        Args:
            collection: Collection name
            records: List of record dictionaries with 'text', 'id', and optional 'metadata'

        Returns:
            Dictionary mapping record IDs to success status
        """
        try:
            # Prepare batch data
            batch_data = []
            record_objects = []

            for record_data in records:
                text = record_data.get("text", "")
                record_id = record_data.get("id", "")
                metadata = record_data.get("metadata", {})

                if not text or not record_id:
                    continue

                # Generate embedding for this record
                embedding = await self._generate_embedding_async(text)

                record = MemoryRecord(
                    id=record_id,
                    text=text,
                    embedding=embedding,
                    collection=collection,
                    metadata=metadata,
                )

                batch_data.append(
                    {
                        "type": f"memory:{collection}",
                        "id": record_id,
                        "data": record.to_dict(),
                        "ttl": 86400,
                    }
                )

                record_objects.append(record)

            if not batch_data:
                return {}

            # Batch store in Redis
            results = await self.redis_service.batch_store(batch_data)

            # Update local cache for successful records
            for record in record_objects:
                if results.get(record.id, False):
                    self._update_cache(record)

            logger.info(f"Batch saved {len(batch_data)} memory records to {collection}")
            return results

        except Exception as e:
            logger.error(f"Error in batch save to {collection}: {e}")
            return {record.get("id", ""): False for record in records if record.get("id")}

    async def get_record_async(self, collection: str, record_id: str) -> Optional[MemoryRecord]:
        """
        Get a specific memory record by ID.

        Args:
            collection: Collection name
            record_id: Record identifier

        Returns:
            MemoryRecord if found, None otherwise
        """
        try:
            # Check local cache first
            cached_record = self._get_from_cache(collection, record_id)
            if cached_record:
                return cached_record

            # Fetch from Redis
            if not self.redis_service.redis_client:
                logger.warning("Redis client not available")
                return None

            key = f"rk:memory:{collection}:{record_id}"
            data = await self.redis_service.redis_client.get(key)

            if data:
                record_data = json.loads(data)
                record = MemoryRecord.from_dict(record_data)

                # Update cache
                self._update_cache(record)

                return record

            return None

        except Exception as e:
            logger.error(f"Error getting memory record {record_id}: {e}")
            return None

    async def delete_record_async(self, collection: str, record_id: str) -> bool:
        """
        Delete a memory record.

        Args:
            collection: Collection name
            record_id: Record identifier

        Returns:
            Success status
        """
        try:
            # Remove from cache
            cache_key = self._get_cache_key(collection, record_id)
            self._local_cache.pop(cache_key, None)
            self._cache_timestamps.pop(cache_key, None)

            # Delete from Redis
            if not self.redis_service.redis_client:
                logger.warning("Redis client not available for deletion")
                return False

            key = f"rk:memory:{collection}:{record_id}"
            result = await self.redis_service.redis_client.delete(key)

            success = result > 0
            if success:
                logger.info(f"Deleted memory record {record_id} from {collection}")
            else:
                logger.warning(f"Memory record {record_id} not found in {collection}")

            return success

        except Exception as e:
            logger.error(f"Error deleting memory record {record_id}: {e}")
            return False

    async def cleanup_expired_records(self, collection: str) -> int:
        """
        Clean up expired memory records.

        Args:
            collection: Collection name

        Returns:
            Number of records cleaned up
        """
        try:
            pattern = f"rk:memory:{collection}:*"
            cleaned_count = await self.redis_service.cleanup_expired_keys(pattern)

            # Clear local cache to ensure consistency
            self._local_cache.clear()
            self._cache_timestamps.clear()

            logger.info(f"Cleaned up {cleaned_count} expired records from {collection}")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired records in {collection}: {e}")
            return 0

    async def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """
        Get statistics for a memory collection.

        Args:
            collection: Collection name

        Returns:
            Dictionary with collection statistics
        """
        try:
            if not self.redis_service.redis_client:
                logger.warning("Redis client not available for stats")
                return {"collection": collection, "error": "Redis client not available"}

            pattern = f"rk:memory:{collection}:*"
            keys = await self.redis_service.redis_client.keys(pattern)

            return {
                "collection": collection,
                "total_records": len(keys),
                "cache_size": len([k for k in self._local_cache.keys() if k.startswith(f"{collection}:")]),
                "cache_enabled": self.enable_caching,
            }

        except Exception as e:
            logger.error(f"Error getting stats for collection {collection}: {e}")
            return {"collection": collection, "error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for memory service"""
        try:
            redis_health = await self.redis_service.health_check()

            return {
                "service": "OptimizedMemoryService",
                "healthy": redis_health.get("status") == "healthy",
                "redis_connected": redis_health.get("redis_connected", False),
                "cache_enabled": self.enable_caching,
                "cache_size": len(self._local_cache),
                "embedding_service_available": self.embedding_service is not None,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Memory service health check failed: {e}")
            return {
                "service": "OptimizedMemoryService",
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    async def close(self):
        """Cleanup resources"""
        try:
            self.executor.shutdown(wait=True)
            self._local_cache.clear()
            self._cache_timestamps.clear()
            logger.info("OptimizedMemoryService closed")
        except Exception as e:
            logger.error(f"Error closing OptimizedMemoryService: {e}")


# Alias for compatibility with tests expecting MemoryService
MemoryService = OptimizedMemoryService
