"""
Maintenance and scanning helpers for UnifiedRedisService.

Includes memory cache cleanup, expired key TTL assignment, and SCAN-based utilities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import time
import json

from reasoning_kernel.core.constants import DEFAULT_CACHE_TTL


def cleanup_expired_memory_cache(memory_cache: Dict[str, Any], memory_cache_ttl: Dict[str, float]) -> None:
    current_time = time.time()
    expired_keys = []
    for key, timestamp in memory_cache_ttl.items():
        if current_time - timestamp >= DEFAULT_CACHE_TTL:
            expired_keys.append(key)
    for key in expired_keys:
        del memory_cache[key]
        del memory_cache_ttl[key]


def should_assign_ttl(key: str) -> bool:
    parts = key.split(":")
    if len(parts) > 2:
        key_type = parts[1]
        return key_type in ["cache", "session"]
    return False


async def cleanup_expired_keys(*, redis_client: Any, pattern: str) -> int:
    expired_count = 0
    cursor = 0
    while True:
        cursor, keys = await redis_client.scan(cursor, match=pattern, count=100)
        if not keys:
            if cursor == 0:
                break
        for key in keys:
            ttl = await redis_client.ttl(key)
            if ttl == -1 and should_assign_ttl(key):
                await redis_client.expire(key, DEFAULT_CACHE_TTL)
                expired_count += 1
        if cursor == 0:
            break
    return expired_count


async def scan_world_models(*, redis_client: Any, namespace_prefix: str) -> List[Tuple[str, dict]]:
    from ..core.async_utils import with_timeout

    pattern = f"{namespace_prefix}:world_model:*"
    cursor = 0
    out: List[Tuple[str, dict]] = []
    while True:
        cursor, keys = await with_timeout(redis_client.scan(cursor, match=pattern, count=100), 5.0)
        for key in keys:
            model_data = await with_timeout(redis_client.get(key), 5.0)
            if model_data:
                out.append((key, json.loads(model_data)))
        if cursor == 0:
            break
    return out
