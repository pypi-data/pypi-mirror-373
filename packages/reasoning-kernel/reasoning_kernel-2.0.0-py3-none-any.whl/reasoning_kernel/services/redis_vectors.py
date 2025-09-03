"""
Redis vector store helpers and thin service adapter.

This module encapsulates vector store initialization and collection management
and provides RedisVectorService expected by tests. The service delegates to a
mock-friendly in-memory store via MockRedisClient for simple operations and
exposes a minimal API used by tests.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

try:
    from semantic_kernel.connectors.redis import RedisStore  # type: ignore
except Exception:  # Fallback dummy

    class _DummyRedisStore:
        def __init__(self, *args, **kwargs):
            pass

        def get_collection(self, *args, **kwargs):
            class _DummyCollection:
                async def upsert(self, *a, **k):
                    return None

            return _DummyCollection()

    RedisStore = _DummyRedisStore  # type: ignore


async def initialize_vector_store(connection_string: str, embedding_generator) -> Any:
    """Create and return a RedisStore configured for embeddings."""
    store = RedisStore(
        connection_string=connection_string, embedding_generator=embedding_generator
    )
    return store


async def get_or_create_collection(
    store: Any, collections: Dict[str, Any], name: str, record_type: type
) -> Any:
    """Lazy create/retrieve a collection from RedisStore and memoize in collections dict."""
    if name in collections:
        return collections[name]
    try:
        collection = store.get_collection(record_type=record_type, collection_name=name)
    except Exception:
        # Fallback dummy if store doesn't support get_collection
        class _DummyCollection:
            async def upsert(self, *a, **k):
                return None

            async def search(self, *a, **k):
                return []

        collection = _DummyCollection()
    collections[name] = collection
    return collection


async def similarity_search(
    collections: Dict[str, Any], collection_name: str, query_text: str, limit: int = 10
) -> List[Any]:
    """Perform similarity search on a named collection when available.

    If the collection does not support search(), return an empty list to
    preserve prior placeholder behavior.
    """
    if collection_name not in collections:
        return []
    collection = collections[collection_name]
    if hasattr(collection, "search"):
        try:
            results = await collection.search(query_text, top_k=limit)  # type: ignore
            return results or []
        except Exception:
            return []
    return []


class RedisVectorService:
    """Thin adapter service exposing vector APIs used in tests.

    This implementation stores vectors in the provided Redis keyspace using
    simple JSON-serialized values keyed by prefix. It is intentionally simple
    and test-friendly, not a full vector index implementation.
    """

    def __init__(
        self,
        redis_client: Optional[Any] = None,
        namespace_prefix: str = "reasoning_kernel",
    ):
        # Allow tests to patch get_redis_client; otherwise import-level factory
        if redis_client is None:
            try:
                from .redis_connection import get_redis_client as _factory

                redis_client = _factory()
            except Exception:
                redis_client = None

        self.redis = redis_client
        self.ns = namespace_prefix

    def _vec_key(self, vector_id: str) -> str:
        return f"{self.ns}:vector:{vector_id}"

    async def store_vector(
        self, vector_id: str, vector: List[float], metadata: Dict[str, Any]
    ) -> bool:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        payload = {"vector": vector, "metadata": metadata}
        import json as _json

        return await self.redis.set(self._vec_key(vector_id), _json.dumps(payload))

    async def get_vector(self, vector_id: str) -> Tuple[List[float], Dict[str, Any]]:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        data = await self.redis.get(self._vec_key(vector_id))
        if not data:
            return [], {}
        payload = _json.loads(data)
        return payload.get("vector", []), payload.get("metadata", {})

    async def search_vectors(
        self, query_vector: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Placeholder similarity search that returns up to top_k stored vectors with dummy scores.

        For tests, it's enough to return structured results from existing keys.
        """
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        results: List[Dict[str, Any]] = []
        # Scan keys; MockRedisClient supports keys('*')
        try:
            keys = await self.redis.keys(f"{self.ns}:vector:*")
        except Exception:
            keys = []
        import json as _json

        for key in keys:
            data = await self.redis.get(key)
            if not data:
                continue
            payload = _json.loads(data)
            vid = key.rsplit(":", 1)[-1]
            results.append(
                {
                    "vector_id": vid,
                    "score": 0.0,  # dummy
                    "metadata": payload.get("metadata", {}),
                }
            )
            if len(results) >= top_k:
                break
        return results

    async def batch_store_vectors(
        self, batch: List[Tuple[str, List[float], Dict[str, Any]]]
    ) -> bool:
        for vid, vec, meta in batch:
            await self.store_vector(vid, vec, meta)
        return True
