"""
Cloud Services Module
====================

Unified cloud services management for Redis and Daytona cloud providers.
Handles connection pooling, configuration management, and service initialization.
"""

import logging
from typing import Any, Dict, Optional

from ..config import get_config
from .daytona_cloud_connector import DaytonaCloudConnector, close_daytona_connector, get_daytona_connector
from .redis_cloud_connector import RedisCloudConnector, close_redis_connector, get_redis_connector

logger = logging.getLogger(__name__)


class CloudServicesManager:
    """Centralized cloud services management"""

    def __init__(self):
        self.config = get_config()
        self.redis_connector: Optional[RedisCloudConnector] = None
        self.daytona_connector: Optional[DaytonaCloudConnector] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize all cloud services"""
        try:
            # Initialize Redis connector
            self.redis_connector = await get_redis_connector()
            logger.info("Redis connector initialized")

            # Initialize Daytona connector if configured
            try:
                self.daytona_connector = await get_daytona_connector()
                logger.info("Daytona connector initialized")
            except Exception as e:
                logger.warning(f"Daytona connector initialization failed: {e}")

            self._initialized = True
            logger.info("Cloud services manager initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize cloud services: {e}")
            return False

    async def shutdown(self) -> None:
        """Shutdown all cloud services"""
        try:
            if self.redis_connector:
                await close_redis_connector()
                self.redis_connector = None

            if self.daytona_connector:
                await close_daytona_connector()
                self.daytona_connector = None

            self._initialized = False
            logger.info("Cloud services shutdown complete")

        except Exception as e:
            logger.error(f"Error during cloud services shutdown: {e}")

    @property
    def is_initialized(self) -> bool:
        """Check if cloud services are initialized"""
        return self._initialized

    def get_status(self) -> Dict[str, Any]:
        """Get status of all cloud services"""
        return {
            "initialized": self._initialized,
            "redis_connected": self.redis_connector is not None,
            "daytona_connected": self.daytona_connector is not None,
        }

    def get_redis_connector(self) -> Optional[RedisCloudConnector]:
        """Get Redis connector"""
        return self.redis_connector

    def get_daytona_connector(self) -> Optional[DaytonaCloudConnector]:
        """Get Daytona Cloud connector"""
        return self.daytona_connector


# Global cloud services manager
_cloud_manager: Optional[CloudServicesManager] = None


async def get_cloud_manager() -> CloudServicesManager:
    """Get the global cloud services manager"""
    global _cloud_manager
    if _cloud_manager is None:
        _cloud_manager = CloudServicesManager()
        await _cloud_manager.initialize()
    return _cloud_manager


async def shutdown_cloud_services() -> None:
    """Shutdown global cloud services"""
    global _cloud_manager
    if _cloud_manager:
        await _cloud_manager.shutdown()
        _cloud_manager = None


# Export main classes and functions
__all__ = [
    "CloudServicesManager",
    "RedisCloudConnector",
    "DaytonaCloudConnector",
    "get_cloud_manager",
    "shutdown_cloud_services",
    "get_redis_connector",
    "get_daytona_connector",
]
