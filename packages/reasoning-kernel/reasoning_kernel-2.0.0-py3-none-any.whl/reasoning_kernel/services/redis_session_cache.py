"""
Session and model cache helpers for UnifiedRedisService.

Provide create/get session and cache_model_result/get_cached_model_result with
in-memory cache interaction preserved.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from reasoning_kernel.core.constants import DEFAULT_CACHE_TTL


def get_redis_client():
    """Factory used by tests to patch a mock client.

    In production, delegates to the shared redis_connection helper.
    """
    try:
        from .redis_connection import get_redis_client as _factory

        return _factory()
    except Exception:
        return None


async def create_session(
    *,
    redis_client: Any,
    namespace_prefix: str,
    session_id: str,
    session_data: Dict[str, Any],
    ttl: Optional[int],
    memory_cache: Dict[str, Any],
    memory_cache_ttl: Dict[str, float],
) -> bool:
    key = f"{namespace_prefix}:session:{session_id}"
    enhanced_data = {
        **session_data,
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_accessed": datetime.now(timezone.utc).isoformat(),
    }
    serialized_data = json.dumps(enhanced_data, default=str)

    if ttl:
        await redis_client.setex(key, ttl, serialized_data)
    else:
        await redis_client.set(key, serialized_data)

    cache_key = f"session:{session_id}"
    memory_cache[cache_key] = enhanced_data
    memory_cache_ttl[cache_key] = time.time()

    return True


async def get_session(
    *,
    redis_client: Any,
    namespace_prefix: str,
    session_id: str,
    memory_cache: Dict[str, Any],
    memory_cache_ttl: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    cache_key = f"session:{session_id}"
    if cache_key in memory_cache:
        if time.time() - memory_cache_ttl.get(cache_key, 0) < DEFAULT_CACHE_TTL:
            return memory_cache[cache_key]
        else:
            del memory_cache[cache_key]
            del memory_cache_ttl[cache_key]

    key = f"{namespace_prefix}:session:{session_id}"
    data = await redis_client.get(key)
    if not data:
        return None

    session_data = json.loads(data)
    session_data["last_accessed"] = datetime.now(timezone.utc).isoformat()
    await redis_client.set(key, json.dumps(session_data, default=str))

    memory_cache[cache_key] = session_data
    memory_cache_ttl[cache_key] = time.time()
    return session_data


async def cache_model_result(
    *,
    redis_client: Any,
    namespace_prefix: str,
    model_name: str,
    input_hash: str,
    result: Dict[str, Any],
    ttl: Optional[int],
    memory_cache: Dict[str, Any],
    memory_cache_ttl: Dict[str, float],
) -> bool:
    key = f"{namespace_prefix}:cache:model:{model_name}:{input_hash}"
    payload = {
        "result": result,
        "model_name": model_name,
        "input_hash": input_hash,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    serialized = json.dumps(payload, default=str)
    ttl = ttl or DEFAULT_CACHE_TTL
    await redis_client.setex(key, ttl, serialized)

    cache_key = f"model_cache:{model_name}:{input_hash}"
    memory_cache[cache_key] = result
    memory_cache_ttl[cache_key] = time.time()

    return True


async def get_cached_model_result(
    *,
    redis_client: Any,
    namespace_prefix: str,
    model_name: str,
    input_hash: str,
    memory_cache: Dict[str, Any],
    memory_cache_ttl: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    cache_key = f"model_cache:{model_name}:{input_hash}"
    if cache_key in memory_cache:
        if time.time() - memory_cache_ttl.get(cache_key, 0) < DEFAULT_CACHE_TTL:
            return memory_cache[cache_key]
        else:
            del memory_cache[cache_key]
            del memory_cache_ttl[cache_key]

    key = f"{namespace_prefix}:cache:model:{model_name}:{input_hash}"
    data = await redis_client.get(key)
    if not data:
        return None

    payload = json.loads(data)
    result = payload.get("result")

    memory_cache[cache_key] = result
    memory_cache_ttl[cache_key] = time.time()
    return result


class RedisSessionCache:
    """Redis-based session cache implementation"""

    def __init__(self, redis_client=None, namespace_prefix: str = "reasoning_kernel"):
        self.redis_client: Any = redis_client or get_redis_client()
        self.namespace_prefix = namespace_prefix
        self.memory_cache: Dict[str, Any] = {}
        self.memory_cache_ttl: Dict[str, float] = {}

    async def create_session(
        self, session_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Create a new session"""
        return await create_session(
            redis_client=self.redis_client,
            namespace_prefix=self.namespace_prefix,
            session_id=session_id,
            session_data=session_data,
            ttl=ttl,
            memory_cache=self.memory_cache,
            memory_cache_ttl=self.memory_cache_ttl,
        )

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return await get_session(
            redis_client=self.redis_client,
            namespace_prefix=self.namespace_prefix,
            session_id=session_id,
            memory_cache=self.memory_cache,
            memory_cache_ttl=self.memory_cache_ttl,
        )

    async def store_session(
        self, session_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Compatibility wrapper expected by tests (alias of create_session)."""
        return await self.create_session(
            session_id=session_id, session_data=session_data, ttl=ttl
        )

    async def update_session(
        self, session_id: str, updated_data: Dict[str, Any]
    ) -> bool:
        """Merge updates into existing session and persist back to Redis and memory cache."""
        existing = await self.get_session(session_id)
        if existing is None:
            return False
        existing.update(updated_data)
        key = f"{self.namespace_prefix}:session:{session_id}"
        await self.redis_client.set(key, json.dumps(existing, default=str))
        self.memory_cache[f"session:{session_id}"] = existing
        self.memory_cache_ttl[f"session:{session_id}"] = time.time()
        return True

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis and memory cache."""
        key = f"{self.namespace_prefix}:session:{session_id}"
        try:
            await self.redis_client.delete(key)
            cache_key = f"session:{session_id}"
            self.memory_cache.pop(cache_key, None)
            self.memory_cache_ttl.pop(cache_key, None)
            return True
        except Exception:
            return False

    async def cache_model_result(
        self,
        model_name: str,
        input_hash: str,
        result: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """Cache model result"""
        return await cache_model_result(
            redis_client=self.redis_client,
            namespace_prefix=self.namespace_prefix,
            model_name=model_name,
            input_hash=input_hash,
            result=result,
            ttl=ttl,
            memory_cache=self.memory_cache,
            memory_cache_ttl=self.memory_cache_ttl,
        )

    async def get_cached_model_result(
        self, model_name: str, input_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached model result"""
        return await get_cached_model_result(
            redis_client=self.redis_client,
            namespace_prefix=self.namespace_prefix,
            model_name=model_name,
            input_hash=input_hash,
            memory_cache=self.memory_cache,
            memory_cache_ttl=self.memory_cache_ttl,
        )
