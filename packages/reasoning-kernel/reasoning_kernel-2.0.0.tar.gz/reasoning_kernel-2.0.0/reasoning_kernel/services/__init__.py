"""
Simplified Services Package - SK Native Structure
"""

# New simplified services
from .daytona import DaytonaExecutor, ExecutionRequest, ExecutionResult
from .redis import RedisService

# Compatibility aliases for legacy code
RedisMemoryService = RedisService
RedisRetrievalService = RedisService
ProductionRedisManager = RedisService


# Factory functions for backward compatibility
def create_production_redis_manager(settings):
    """Create Redis service for production."""
    return RedisService(settings)


def create_development_redis_manager(settings):
    """Create Redis service for development."""
    return RedisService(settings)


def create_unified_redis_service(settings):
    """Create unified Redis service."""
    return RedisService(settings)


__all__ = [
    # Core services
    "DaytonaExecutor",
    "RedisService",
    "ExecutionRequest",
    "ExecutionResult",
    # Compatibility aliases
    "RedisMemoryService",
    "RedisRetrievalService",
    "ProductionRedisManager",
    # Factory functions
    "create_production_redis_manager",
    "create_development_redis_manager",
    "create_unified_redis_service",
]
