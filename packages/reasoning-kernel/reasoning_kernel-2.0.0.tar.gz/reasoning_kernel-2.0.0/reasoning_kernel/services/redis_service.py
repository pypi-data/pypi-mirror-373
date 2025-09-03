"""
Redis Service - Unified Redis Operations
========================================

Consolidated Redis service following SK-native patterns.
"""

from typing import Any, Dict, List, Optional
import logging
import json
import redis.asyncio as redis
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RedisService:
    """Unified Redis service for caching, storage, and knowledge management."""

    def __init__(self, settings):
        """Initialize Redis service with settings."""
        self.settings = settings
        self._client = None

    async def get_client(self) -> redis.Redis:
        """Get async Redis client."""
        if self._client is None:
            self._client = redis.Redis.from_url(self.settings.redis_url, decode_responses=True, retry_on_timeout=True)
        return self._client

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair with optional TTL."""
        try:
            client = await self.get_client()
            serialized = json.dumps(value) if not isinstance(value, str) else value
            if ttl:
                return await client.setex(key, ttl, serialized)
            return await client.set(key, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value by key."""
        try:
            client = await self.get_client()
            value = await client.get(key)
            if value is None:
                return default
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return default

    async def delete(self, key: str) -> bool:
        """Delete a key."""
        try:
            client = await self.get_client()
            return await client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            client = await self.get_client()
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    async def hset(self, key: str, field: str, value: Any) -> bool:
        """Set hash field."""
        try:
            client = await self.get_client()
            serialized = json.dumps(value) if not isinstance(value, str) else value
            return await client.hset(key, field, serialized) > 0
        except Exception as e:
            logger.error(f"Redis hset error: {e}")
            return False

    async def hget(self, key: str, field: str, default: Any = None) -> Any:
        """Get hash field."""
        try:
            client = await self.get_client()
            value = await client.hget(key, field)
            if value is None:
                return default
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Redis hget error: {e}")
            return default

    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to list head."""
        try:
            client = await self.get_client()
            serialized_values = [json.dumps(v) if not isinstance(v, str) else v for v in values]
            return await client.lpush(key, *serialized_values)
        except Exception as e:
            logger.error(f"Redis lpush error: {e}")
            return 0

    async def rpush(self, key: str, *values: Any) -> int:
        """Push values to list tail."""
        try:
            client = await self.get_client()
            serialized_values = [json.dumps(v) if not isinstance(v, str) else v for v in values]
            return await client.rpush(key, *serialized_values)
        except Exception as e:
            logger.error(f"Redis rpush error: {e}")
            return 0

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get list range."""
        try:
            client = await self.get_client()
            values = await client.lrange(key, start, end)
            result = []
            for v in values:
                try:
                    result.append(json.loads(v))
                except json.JSONDecodeError:
                    result.append(v)
            return result
        except Exception as e:
            logger.error(f"Redis lrange error: {e}")
            return []

    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
