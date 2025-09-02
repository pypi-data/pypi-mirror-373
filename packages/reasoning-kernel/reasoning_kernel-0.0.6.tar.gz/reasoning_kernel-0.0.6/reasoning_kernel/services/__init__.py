"""
Services for MSA Reasoning Engine
"""

from .unified_redis_service import create_unified_redis_service as create_production_redis_manager
from .unified_redis_service import create_unified_redis_service as create_development_redis_manager
from .unified_redis_service import UnifiedRedisService as ProductionRedisManager

# Fallback imports for compatibility
try:
    from .redis_service import RedisMemoryService, RedisRetrievalService
except ImportError:
    # Fallback to unified service if old services don't exist
    from .unified_redis_service import UnifiedRedisService as RedisMemoryService
    from .unified_redis_service import UnifiedRedisService as RedisRetrievalService


__all__ = [
    "RedisMemoryService",
    "RedisRetrievalService",
    "ProductionRedisManager",
    "create_production_redis_manager",
    "create_development_redis_manager",
]
