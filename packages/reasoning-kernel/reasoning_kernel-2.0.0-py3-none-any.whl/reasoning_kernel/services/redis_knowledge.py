"""
Knowledge operations helpers for UnifiedRedisService.

Encapsulates storing knowledge entries with tagging and retrieving by type,
including in-memory cache updates. Caller passes redis_client and cache maps.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from reasoning_kernel.core.constants import DEFAULT_CACHE_TTL


async def store_knowledge(
    *,
    redis_client: Any,
    namespace_prefix: str,
    knowledge_id: str,
    knowledge_data: Dict[str, Any],
    knowledge_type: str = "general",
    tags: Optional[Set[str]] = None,
    ttl: Optional[int] = None,
    memory_cache: Dict[str, Any],
    memory_cache_ttl: Dict[str, float],
) -> bool:
    key = f"{namespace_prefix}:knowledge:{knowledge_id}"

    enhanced_data = {
        **knowledge_data,
        "knowledge_type": knowledge_type,
        "tags": list(tags) if tags else [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "knowledge_id": knowledge_id,
    }
    serialized_data = json.dumps(enhanced_data, default=str)

    if ttl:
        await redis_client.setex(key, ttl, serialized_data)
    else:
        await redis_client.set(key, serialized_data)

    # Index by type and tags
    type_key = f"{namespace_prefix}:knowledge:type:{knowledge_type}"
    await redis_client.sadd(type_key, knowledge_id)

    if tags:
        for tag in tags:
            tag_key = f"{namespace_prefix}:knowledge:tag:{tag}"
            await redis_client.sadd(tag_key, knowledge_id)

    # Update in-memory cache
    cache_key = f"knowledge_type:{knowledge_type}"
    if cache_key in memory_cache:
        memory_cache[cache_key].append(enhanced_data)
        memory_cache_ttl[cache_key] = time.time()
    else:
        memory_cache[cache_key] = [enhanced_data]
        memory_cache_ttl[cache_key] = time.time()

    # Enforce bounds on knowledge type lists by capping list size
    try:
        # Trim list to last N entries to prevent unbounded growth
        MAX_KNOWLEDGE_PER_TYPE = 5000
        if len(memory_cache.get(cache_key, [])) > MAX_KNOWLEDGE_PER_TYPE:
            memory_cache[cache_key] = memory_cache[cache_key][-MAX_KNOWLEDGE_PER_TYPE:]
    except Exception:
        pass

    return True


async def retrieve_knowledge_by_type(
    *,
    redis_client: Any,
    namespace_prefix: str,
    knowledge_type: str,
    memory_cache: Dict[str, Any],
    memory_cache_ttl: Dict[str, float],
) -> List[Dict[str, Any]]:
    cache_key = f"knowledge_type:{knowledge_type}"

    # Use memory cache if fresh
    if cache_key in memory_cache:
        if time.time() - memory_cache_ttl.get(cache_key, 0) < DEFAULT_CACHE_TTL:
            return memory_cache[cache_key]

    type_key = f"{namespace_prefix}:knowledge:type:{knowledge_type}"
    knowledge_ids = await redis_client.smembers(type_key)

    results = []
    for knowledge_id in knowledge_ids:
        key = f"{namespace_prefix}:knowledge:{knowledge_id}"
        data = await redis_client.get(key)
        if data:
            results.append(json.loads(data))

    memory_cache[cache_key] = results
    memory_cache_ttl[cache_key] = time.time()

    return results


class RedisKnowledgeService:
    """Thin adapter exposing knowledge APIs used by tests.

    Stores JSON-serialized knowledge by ID and maintains simple type/tag indexes.
    """

    def __init__(
        self,
        redis_client: Optional[Any] = None,
        namespace_prefix: str = "reasoning_kernel",
    ):
        if redis_client is None:
            try:
                from .redis_connection import get_redis_client as _factory

                redis_client = _factory()
            except Exception:
                redis_client = None
        self.redis = redis_client
        self.ns = namespace_prefix

    def _key(self, knowledge_id: str) -> str:
        return f"{self.ns}:knowledge:{knowledge_id}"

    async def store_knowledge(
        self, knowledge_id: str, knowledge_data: Dict[str, Any]
    ) -> bool:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        return await self.redis.set(
            self._key(knowledge_id), _json.dumps(knowledge_data)
        )

    async def get_knowledge(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        data = await self.redis.get(self._key(knowledge_id))
        return _json.loads(data) if data else None

    async def search_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        results: List[Dict[str, Any]] = []
        try:
            keys = await self.redis.keys(f"{self.ns}:knowledge:*")
        except Exception:
            keys = []
        for key in keys:
            data = await self.redis.get(key)
            if not data:
                continue
            obj = _json.loads(data)
            if obj.get("domain") == domain:
                results.append(obj)
        return results

    async def search_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        want = set(tags)
        out: List[Dict[str, Any]] = []
        try:
            keys = await self.redis.keys(f"{self.ns}:knowledge:*")
        except Exception:
            keys = []
        for key in keys:
            data = await self.redis.get(key)
            if not data:
                continue
            obj = _json.loads(data)
            ktags = set(obj.get("tags", []))
            if want.issubset(ktags) or (want & ktags):
                out.append(obj)
        return out

    async def update_knowledge(
        self, knowledge_id: str, updated: Dict[str, Any]
    ) -> bool:
        current = await self.get_knowledge(knowledge_id)
        if current is None:
            return False
        current.update(updated)
        return await self.store_knowledge(knowledge_id, current)
