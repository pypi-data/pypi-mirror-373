"""
Enhanced Redis Connection Manager for MSA Reasoning Kernel
=========================================================

Provides optimized Redis connection management with advanced pooling,
health monitoring, failover support, and performance optimization.
Enhanced version of the original connection helpers.
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

try:
    from redis import asyncio as aioredis
    from redis.asyncio import ConnectionPool, Redis
    from redis.exceptions import ConnectionError, RedisError, TimeoutError

    REDIS_AVAILABLE = True
except Exception:
    aioredis = None
    ConnectionPool = None  # type: ignore[assignment]
    Redis = None  # type: ignore[assignment]
    ConnectionError = Exception
    TimeoutError = Exception
    RedisError = Exception
    REDIS_AVAILABLE = False

from ..core.exceptions import MSAError
from ..core.logging_config import get_logger


class RedisUnavailableError(MSAError):
    """Raised when Redis is unavailable"""

    pass


@dataclass
class ConnectionPoolMetrics:
    """Metrics for connection pool monitoring"""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_errors: int = 0
    average_response_time_ms: float = 0.0
    last_health_check: float = field(default_factory=time.time)

    @property
    def utilization_rate(self) -> float:
        """Calculate connection pool utilization rate"""
        if self.total_connections == 0:
            return 0.0
        return self.active_connections / self.total_connections


@dataclass
class RedisConnectionConfig:
    """Enhanced Redis connection configuration"""

    # Basic connection settings
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    redis_url: Optional[str] = None

    # Pool settings
    max_connections: int = 100
    min_connections: int = 10
    connection_timeout: float = 5.0
    socket_timeout: float = 5.0
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(
        default_factory=lambda: {
            1: 1,
            2: 3,
            3: 5,
        }  # TCP_KEEPIDLE  # TCP_KEEPINTVL  # TCP_KEEPCNT
    )

    # Health monitoring
    health_check_interval: float = 30.0
    max_connection_age: float = 3600.0  # 1 hour
    retry_on_timeout: bool = True
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Performance settings
    decode_responses: bool = True
    encoding: str = "utf-8"
    encoding_errors: str = "strict"


def build_connection_pool(
    *,
    redis_url: Optional[str],
    host: str,
    port: int,
    db: int,
    password: Optional[str],
    max_connections: int,
    connection_kwargs: Dict[str, Any],
):
    """Create an aioredis ConnectionPool from URL or host params.

    Returns a pool instance or raises RedisUnavailableError if redis is missing.
    """
    if aioredis is None:
        raise RedisUnavailableError("redis asyncio client not available")

    if redis_url:
        return aioredis.ConnectionPool.from_url(
            redis_url, max_connections=max_connections, **connection_kwargs
        )
    return aioredis.ConnectionPool(
        host=host,
        port=port,
        db=db,
        password=password,
        max_connections=max_connections,
        **connection_kwargs,
    )


def build_redis_client(pool):
    """Create an aioredis.Redis from a pool."""
    if aioredis is None:
        raise RedisUnavailableError("redis asyncio client not available")
    return aioredis.Redis(connection_pool=pool)


def get_redis_client(config: Optional[RedisConnectionConfig] = None):
    """Return a Redis asyncio client using the enhanced connection builder.

    This small factory exists so tests can patch it easily. In production
    it builds a client with sensible defaults from RedisConnectionConfig.
    """
    if not REDIS_AVAILABLE:
        raise RedisUnavailableError("Redis is not available - install redis-py")

    cfg = config or RedisConnectionConfig()
    connection_kwargs = {
        "decode_responses": cfg.decode_responses,
        "socket_connect_timeout": cfg.connection_timeout,
        "socket_timeout": cfg.socket_timeout,
        "retry_on_timeout": cfg.retry_on_timeout,
    }

    pool = build_connection_pool(
        redis_url=cfg.redis_url,
        host=cfg.host,
        port=cfg.port,
        db=cfg.db,
        password=cfg.password,
        max_connections=cfg.max_connections,
        connection_kwargs=connection_kwargs,
    )
    return build_redis_client(pool)


class EnhancedConnectionPool:
    """Enhanced Redis connection pool with monitoring and health checks"""

    def __init__(self, config: RedisConnectionConfig):
    self.config = config
    self._logger = get_logger(__name__)

    # Connection pool
    # Use Any here to avoid type issues when redis is not installed
    self._pool: Optional[Any] = None
    self._client: Optional[Any] = None
    self._is_healthy = False

    # Metrics and monitoring
    self._metrics = ConnectionPoolMetrics()
    self._response_times: List[float] = []
    self._max_response_history = 100

    # Health monitoring
    self._health_check_task: Optional[asyncio.Task] = None
    self._last_health_check = 0.0

    async def initialize(self) -> None:
        """Initialize the enhanced connection pool"""
        if not REDIS_AVAILABLE:
            raise RedisUnavailableError("Redis is not available - install redis-py")

        try:
            # Build connection pool with optimized settings using helper
            connection_kwargs = {
                "socket_timeout": self.config.socket_timeout,
                "socket_connect_timeout": self.config.connection_timeout,
                "socket_keepalive": self.config.socket_keepalive,
                "socket_keepalive_options": self.config.socket_keepalive_options,
                "retry_on_timeout": self.config.retry_on_timeout,
                "health_check_interval": self.config.health_check_interval,
                "decode_responses": self.config.decode_responses,
                "encoding": self.config.encoding,
                "encoding_errors": self.config.encoding_errors,
            }

            self._pool = build_connection_pool(
                redis_url=self.config.redis_url,
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                connection_kwargs=connection_kwargs,
            )

            # Create Redis client
            self._client = build_redis_client(self._pool)

            # Test initial connection
            await self._perform_health_check()

            # Start health monitoring
            self._health_check_task = asyncio.create_task(self._health_monitor())

            self._logger.info("Enhanced Redis connection pool initialized successfully")

        except Exception as e:
            self._logger.error(f"Failed to initialize Redis connection pool: {str(e)}")
            raise RedisUnavailableError(
                f"Redis pool initialization failed: {str(e)}"
            ) from e

    async def get_client(self) -> Any:
        """Get Redis client with health check"""
        if not self._is_healthy:
            await self._perform_health_check()

        if not self._is_healthy:
            raise RedisUnavailableError("Redis connection pool is unhealthy")

        return self._client

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool with automatic cleanup"""
        connection = None
        start_time = time.time()

        try:
            # Provide a dummy command name required by redis-py's get_connection signature
            connection = await self._pool.get_connection("PING")
            yield connection

            # Record successful operation
            response_time = (time.time() - start_time) * 1000
            self._record_response_time(response_time)

        except Exception as e:
            self._metrics.connection_errors += 1
            self._logger.error(f"Connection error: {str(e)}")
            raise
        finally:
            if connection:
                await self._pool.release(connection)

    async def _perform_health_check(self) -> bool:
        """Perform health check on Redis connection"""
        try:
            start_time = time.time()

            # Simple ping test
            await self._client.ping()

            # Record response time
            response_time = (time.time() - start_time) * 1000
            self._record_response_time(response_time)

            # Update metrics
            self._update_pool_metrics()

            self._is_healthy = True
            self._last_health_check = time.time()
            self._metrics.last_health_check = self._last_health_check

            return True

        except Exception as e:
            self._is_healthy = False
            self._metrics.connection_errors += 1
            self._logger.warning(f"Redis health check failed: {str(e)}")
            return False

    async def _health_monitor(self) -> None:
        """Background task for continuous health monitoring"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Health monitor error: {str(e)}")

    def _record_response_time(self, response_time_ms: float) -> None:
        """Record response time for metrics"""
        self._response_times.append(response_time_ms)

        # Keep only recent response times
        if len(self._response_times) > self._max_response_history:
            self._response_times = self._response_times[-self._max_response_history :]

        # Update average response time
        if self._response_times:
            self._metrics.average_response_time_ms = sum(self._response_times) / len(
                self._response_times
            )

    def _update_pool_metrics(self) -> None:
        """Update connection pool metrics"""
        if self._pool:
            # Get pool statistics (limited to public attributes)
            self._metrics.total_connections = getattr(
                self._pool, "max_connections", 0
            )
            # Avoid relying on private attributes that may not exist
            self._metrics.active_connections = 0
            self._metrics.idle_connections = 0

    def get_metrics(self) -> ConnectionPoolMetrics:
        """Get current connection pool metrics"""
        self._update_pool_metrics()
        return self._metrics

    async def cleanup(self) -> None:
        """Cleanup connection pool and background tasks"""
        # Cancel health check task
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Close Redis client and pool
        if self._client:
            await self._client.close()

        if self._pool:
            await self._pool.disconnect()

        self._is_healthy = False
        self._logger.info("Enhanced Redis connection pool cleanup completed")
