"""
Redis Cloud Connector for Knowledge Stage

This module provides Redis Cloud integration for:
- Vector embeddings storage and retrieval
- Knowledge graph caching
- Session-based knowledge persistence
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import redis.asyncio as redis

from ..config import get_cloud_config

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Result from vector similarity search"""

    id: str
    content: str
    metadata: Dict[str, Any]
    score: float


@dataclass
class KnowledgeItem:
    """Knowledge item for storage and retrieval"""

    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    session_id: Optional[str] = None
    timestamp: Optional[str] = None


class RedisCloudConnector:
    """Redis Cloud connector for knowledge stage operations"""

    def __init__(self, connection_string: Optional[str] = None):
        self.config = get_cloud_config()
        redis_config = self.config.redis_cloud
        if connection_string:
            self.connection_string = connection_string
        else:
            # Build connection string from config
            auth = (
                f"{redis_config.username}:{redis_config.password}@"
                if redis_config.username and redis_config.password
                else ""
            )
            self.connection_string = (
                f"redis://{auth}{redis_config.host}:{redis_config.port}"
            )
        self.client: Optional[redis.Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
        self._is_connected = False

    async def connect(self) -> bool:
        """Establish connection to Redis Cloud"""
        try:
            if not self.connection_string:
                logger.error("Redis connection string not provided")
                return False

            redis_config = self.config.redis_cloud

            # Create connection pool
            pool_kwargs = {
                "max_connections": 20,
                "retry_on_timeout": True,
                "socket_timeout": redis_config.socket_timeout,
            }
            if redis_config.ssl:
                pool_kwargs.update(
                    {
                        "ssl": True,
                        "ssl_cert_reqs": redis_config.ssl_cert_reqs,
                        "ssl_ca_certs": redis_config.ssl_ca_certs,
                    }
                )
            self._connection_pool = redis.ConnectionPool.from_url(
                self.connection_string, **pool_kwargs
            )

            # Create Redis client
            self.client = redis.Redis(
                connection_pool=self._connection_pool, decode_responses=True
            )

            # Test connection
            await self.client.ping()
            self._is_connected = True

            logger.info("Successfully connected to Redis Cloud")

            # Initialize vector index if it doesn't exist
            await self._ensure_vector_index()

            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis Cloud: {e}")
            self._is_connected = False
            return False

    async def disconnect(self) -> None:
        """Close Redis Cloud connection"""
        if self.client:
            await self.client.close()
        if self._connection_pool:
            await self._connection_pool.disconnect()
        self._is_connected = False
        logger.info("Disconnected from Redis Cloud")

    async def is_healthy(self) -> bool:
        """Check if Redis Cloud connection is healthy"""
        if not self._is_connected or not self.client:
            return False

        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis Cloud health check failed: {e}")
            return False

    async def _ensure_vector_index(self) -> None:
        """Ensure vector search index exists"""
        try:
            # Check if index exists
            try:
                await self.client.ft(self.config.redis_cloud.vector_index_name).info()
                logger.info(
                    f"Vector index '{self.config.redis_cloud.vector_index_name}' already exists"
                )
                return
            except Exception:
                # Index doesn't exist, proceed to create it
                ...

            # Create vector index (handle redisearch module differences)
            try:
                from redis.commands.search.field import TagField, TextField, VectorField
                from redis.commands.search.indexDefinition import IndexDefinition, IndexType
            except Exception:
                from redis.commands.search.field import TagField, TextField, VectorField
                from redis.commands.search.index_definition import IndexDefinition, IndexType

            schema = [
                TextField("content"),
                TagField("session_id"),
                TagField("metadata"),
                VectorField(
                    "embedding",
                    "HNSW",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": self.config.redis_cloud.vector_dimension,
                        "DISTANCE_METRIC": self.config.redis_cloud.vector_distance_metric,
                        "INITIAL_CAP": 1000,
                        "M": 16,
                        "EF_CONSTRUCTION": 200,
                    },
                ),
            ]

            definition = IndexDefinition(
                prefix=["knowledge:"], index_type=IndexType.HASH
            )

            await self.client.ft(
                self.config.redis_cloud.vector_index_name
            ).create_index(schema, definition=definition)

            logger.info(
                f"Created vector index '{self.config.redis_cloud.vector_index_name}'"
            )

        except Exception as e:
            logger.error(f"Failed to create vector index: {e}")
            raise

    async def store_knowledge_item(self, item: KnowledgeItem) -> bool:
        """Store a knowledge item with vector embedding"""
        try:
            if not self._is_connected:
                await self.connect()

            # Prepare data for storage
            key = f"knowledge:{item.id}"

            # Convert embedding to bytes for Redis
            embedding_bytes = np.array(item.embedding, dtype=np.float32).tobytes()

            data = {
                "content": item.content,
                "embedding": embedding_bytes,
                "metadata": json.dumps(item.metadata),
                "session_id": item.session_id or "",
                "timestamp": item.timestamp or "",
            }

            # Store in Redis
            await self.client.hset(key, mapping=data)

            logger.debug(f"Stored knowledge item: {item.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store knowledge item {item.id}: {e}")
            return False

    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        session_id: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Perform vector similarity search"""
        try:
            if not self._is_connected:
                await self.connect()

            # Build search query
            query_vector = np.array(query_embedding, dtype=np.float32).tobytes()

            # Base query
            query_parts = ["*"]

            # Add session filter if provided
            if session_id:
                query_parts.append(f"@session_id:{session_id}")

            # Add metadata filters if provided
            if metadata_filter:
                for key, value in metadata_filter.items():
                    query_parts.append(f"@metadata:{key}={value}")

            query_string = " ".join(query_parts)

            # Perform vector search
            from redis.commands.search.query import Query

            search_query = (
                Query(query_string)
                .return_fields("content", "metadata", "session_id")
                .sort_by("__embedding_score")
                .paging(0, limit)
                .dialect(2)
            )

            # Use KNN search for vector similarity
            search_query = search_query.add_filter(
                f"@embedding:[KNN {limit} @embedding $query_vector AS __embedding_score]"
            )

            results = await self.client.ft(
                self.config.redis_cloud.vector_index_name
            ).search(search_query, query_params={"query_vector": query_vector})

            # Process results
            search_results = []
            for doc in results.docs:
                try:
                    metadata = (
                        json.loads(doc.metadata) if hasattr(doc, "metadata") else {}
                    )

                    result = VectorSearchResult(
                        id=doc.id.replace("knowledge:", ""),
                        content=doc.content,
                        metadata=metadata,
                        score=float(getattr(doc, "__embedding_score", 0.0)),
                    )
                    search_results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to process search result: {e}")
                    continue

            logger.debug(f"Vector search returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    async def get_knowledge_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """Retrieve a specific knowledge item"""
        try:
            if not self._is_connected:
                await self.connect()

            key = f"knowledge:{item_id}"
            data = await self.client.hgetall(key)

            if not data:
                return None

            # Convert embedding back from bytes
            embedding_bytes = data.get("embedding", b"")
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32).tolist()

            metadata = json.loads(data.get("metadata", "{}"))

            return KnowledgeItem(
                id=item_id,
                content=data.get("content", ""),
                embedding=embedding,
                metadata=metadata,
                session_id=data.get("session_id") or None,
                timestamp=data.get("timestamp") or None,
            )

        except Exception as e:
            logger.error(f"Failed to retrieve knowledge item {item_id}: {e}")
            return None

    async def delete_knowledge_item(self, item_id: str) -> bool:
        """Delete a knowledge item"""
        try:
            if not self._is_connected:
                await self.connect()

            key = f"knowledge:{item_id}"
            result = await self.client.delete(key)

            logger.debug(f"Deleted knowledge item: {item_id}")
            return bool(result)

        except Exception as e:
            logger.error(f"Failed to delete knowledge item {item_id}: {e}")
            return False

    async def clear_session_knowledge(self, session_id: str) -> int:
        """Clear all knowledge items for a session"""
        try:
            if not self._is_connected:
                await self.connect()

            # Find all keys for the session
            pattern = "knowledge:*"
            keys_to_delete = []

            async for key in self.client.scan_iter(match=pattern):
                data = await self.client.hget(key, "session_id")
                if data == session_id:
                    keys_to_delete.append(key)

            # Delete the keys
            if keys_to_delete:
                deleted_count = await self.client.delete(*keys_to_delete)
                logger.info(
                    f"Cleared {deleted_count} knowledge items for session {session_id}"
                )
                return deleted_count

            return 0

        except Exception as e:
            logger.error(f"Failed to clear session knowledge for {session_id}: {e}")
            return 0


# Global connector instance
_redis_connector: Optional[RedisCloudConnector] = None


async def get_redis_connector() -> RedisCloudConnector:
    """Get the global Redis Cloud connector"""
    global _redis_connector
    if _redis_connector is None:
        _redis_connector = RedisCloudConnector()
        await _redis_connector.connect()
    return _redis_connector


async def close_redis_connector() -> None:
    """Close the global Redis Cloud connector"""
    global _redis_connector
    if _redis_connector:
        await _redis_connector.disconnect()
        _redis_connector = None
