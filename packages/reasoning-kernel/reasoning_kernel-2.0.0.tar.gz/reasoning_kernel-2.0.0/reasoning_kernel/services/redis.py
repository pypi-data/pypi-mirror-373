"""
Unified Redis Service
====================

Simplified Redis service for all caching and storage needs.
"""

import json
import logging
from typing import Optional, List, Dict, Any

import redis.asyncio as redis
from redis.exceptions import RedisError

from ..settings import Settings

logger = logging.getLogger(__name__)


class RedisService:
    """Unified Redis service for all storage and caching operations."""

    def __init__(self, settings: Settings):
        """Initialize Redis connection from settings."""
        self.settings = settings
        self.client: Optional[redis.Redis] = None
        self._is_connected = False
        self._connect()

    def _connect(self) -> None:
        """Establish Redis connection."""
        if not self.settings.enable_caching:
            logger.info("Redis caching disabled by configuration")
            return

        if not self.settings.redis_connection_string:
            logger.warning("No Redis connection string provided")
            return

        try:
            self.client = redis.from_url(
                self.settings.redis_connection_string,
                decode_responses=True,
                socket_timeout=self.settings.redis_timeout,
                socket_connect_timeout=self.settings.redis_timeout,
            )
            logger.info("Redis client initialized")
            self._is_connected = True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None
            self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._is_connected and self.client is not None

    async def ping(self) -> bool:
        """Test Redis connection."""
        if not self.client:
            return False

        try:
            await self.client.ping()
            return True
        except RedisError:
            return False

    # Basic key-value operations

    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self.is_connected or not self.client:
            return None

        try:
            return await self.client.get(key)
        except RedisError as e:
            logger.error(f"Redis get failed for key {key}: {e}")
            return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set key-value with optional TTL."""
        if not self.is_connected or not self.client:
            return False

        try:
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
            return True
        except RedisError as e:
            logger.error(f"Redis set failed for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key."""
        if not self.is_connected or not self.client:
            return False

        try:
            result = await self.client.delete(key)
            return result > 0
        except RedisError as e:
            logger.error(f"Redis delete failed for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.is_connected or not self.client:
            return False

        try:
            result = await self.client.exists(key)
            return result > 0
        except RedisError as e:
            logger.error(f"Redis exists check failed for key {key}: {e}")
            return False

    # Hash operations for structured data

    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field value."""
        if not self.is_connected or not self.client:
            return None

        try:
            return await self.client.hget(key, field)
        except RedisError as e:
            logger.error(f"Redis hget failed for {key}.{field}: {e}")
            return None

    async def hset(self, key: str, field: str, value: str) -> bool:
        """Set hash field value."""
        if not self.is_connected or not self.client:
            return False

        try:
            await self.client.hset(key, field, value)
            return True
        except RedisError as e:
            logger.error(f"Redis hset failed for {key}.{field}: {e}")
            return False

    async def hgetall(self, key: str) -> Dict[str, str]:
        """Get all hash fields."""
        if not self.is_connected or not self.client:
            return {}

        try:
            return await self.client.hgetall(key)
        except RedisError as e:
            logger.error(f"Redis hgetall failed for {key}: {e}")
            return {}

    # JSON operations for structured data

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value by key."""
        value = await self.get(key)
        if not value:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode failed for key {key}: {e}")
            return None

    async def set_json(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set JSON value with optional TTL."""
        try:
            json_str = json.dumps(value)
            return await self.set(key, json_str, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode failed for key {key}: {e}")
            return False

    # Search operations (simplified)

    async def search(self, query: str, namespace: str = "default", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for items matching query within namespace.

        This is a simplified search implementation. In production,
        consider using Redis Search module for advanced search capabilities.
        """
        if not self.is_connected or not self.client:
            return []

        try:
            # Simple pattern matching search
            pattern = f"{namespace}:*{query}*"
            keys = await self.client.keys(pattern)

            results = []
            for key in keys[:limit]:  # Limit results to prevent memory issues
                value = await self.get(key)
                if value:
                    try:
                        # Try to parse as JSON
                        doc = json.loads(value)
                        if isinstance(doc, dict):
                            doc["_key"] = key
                            results.append(doc)
                    except json.JSONDecodeError:
                        # Store as plain text
                        results.append({"_key": key, "content": value, "type": "text"})

            logger.debug(f"Search for '{query}' in '{namespace}' returned {len(results)} results")
            return results

        except RedisError as e:
            logger.error(f"Redis search failed for query '{query}': {e}")
            return []

    async def store(self, content: str, namespace: str = "default", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store content with metadata in the specified namespace.

        Returns:
            Document ID if successful, empty string if failed
        """
        if not self.is_connected:
            return ""

        try:
            import uuid

            doc_id = str(uuid.uuid4())
            key = f"{namespace}:{doc_id}"

            document = {
                "id": doc_id,
                "content": content,
                "metadata": metadata or {},
                "namespace": namespace,
                "created_at": self._get_timestamp(),
            }

            success = await self.set_json(key, document)
            if success:
                logger.debug(f"Stored document {doc_id} in namespace '{namespace}'")
                return doc_id
            else:
                return ""

        except Exception as e:
            logger.error(f"Store operation failed: {e}")
            return ""

    # Namespace operations

    async def list_namespaces(self) -> List[str]:
        """List all available namespaces."""
        if not self.is_connected or not self.client:
            return []

        try:
            keys = await self.client.keys("*:*")
            namespaces = set()
            for key in keys:
                if ":" in key:
                    namespace = key.split(":", 1)[0]
                    namespaces.add(namespace)
            return sorted(list(namespaces))
        except RedisError as e:
            logger.error(f"List namespaces failed: {e}")
            return []

    async def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace. Returns number of deleted keys."""
        if not self.is_connected or not self.client:
            return 0

        try:
            pattern = f"{namespace}:*"
            keys = await self.client.keys(pattern)
            if keys:
                deleted = await self.client.delete(*keys)
                logger.info(f"Cleared {deleted} keys from namespace '{namespace}'")
                return deleted
            return 0
        except RedisError as e:
            logger.error(f"Clear namespace '{namespace}' failed: {e}")
            return 0

    # Connection management

    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            try:
                await self.client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self.client = None
                self._is_connected = False

    async def info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        if not self.is_connected or not self.client:
            return {"status": "disconnected"}

        try:
            info = await self.client.info()
            return {
                "status": "connected",
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except RedisError as e:
            logger.error(f"Redis info failed: {e}")
            return {"status": "error", "error": str(e)}

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()


# Factory function for backward compatibility
def create_redis_service(settings: Settings) -> RedisService:
    """Create a Redis service instance."""
    return RedisService(settings)
