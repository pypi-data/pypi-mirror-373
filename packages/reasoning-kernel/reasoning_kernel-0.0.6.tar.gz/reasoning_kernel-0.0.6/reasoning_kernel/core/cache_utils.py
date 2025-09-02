"""
Cache Utilities
===============

Utilities for caching operations in the Reasoning Kernel.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CachePolicy:
    """Cache policy configuration"""

    max_size: int = 100
    default_ttl: Optional[float] = 300
    eviction_strategy: str = "lru"
    cleanup_interval: int = 60

    def should_evict(self, current_size: int) -> bool:
        """Check if cache should evict based on size"""
        if self.max_size is None:
            return False
        return current_size >= self.max_size

    def get_ttl(self, custom_ttl: Optional[float] = None) -> Optional[float]:
        """Get the TTL for cache entry (custom or default)"""
        if custom_ttl is not None:
            return custom_ttl
        return self.default_ttl


@dataclass
class CacheEntry:
    """Cache entry with metadata"""

    key: str
    value: Any
    created_at: float
    access_count: int = 0
    last_accessed: Optional[float] = None
    ttl: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if the cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def access(self) -> Any:
        """Access the cache entry and update metadata"""
        self.last_accessed = time.time()
        self.access_count += 1
        return self.value

    def touch(self) -> None:
        """Update last accessed time and increment access count"""
        self.last_accessed = time.time()
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "ttl": self.ttl,
        }


class CacheBounds:
    """Cache bounds configuration"""

    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: Optional[float] = None,
        default_ttl: Optional[float] = None,
    ):
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self.default_ttl = default_ttl


def enforce_bounds(cache: Dict[str, CacheEntry], bounds: CacheBounds) -> None:
    """
    Enforce cache bounds by removing entries if necessary

    Args:
        cache: Cache dictionary to enforce bounds on
        bounds: Cache bounds configuration
    """
    # Remove expired entries first
    expired_keys = [key for key, entry in cache.items() if entry.is_expired()]
    for key in expired_keys:
        del cache[key]
        logger.debug(f"Removed expired cache entry: {key}")

    # Check size bounds
    if len(cache) > bounds.max_size:
        # Remove oldest entries (FIFO policy for bounds enforcement)
        sorted_entries = sorted(cache.items(), key=lambda x: x[1].created_at)
        entries_to_remove = len(cache) - bounds.max_size

        for i in range(entries_to_remove):
            key = sorted_entries[i][0]
            del cache[key]
            logger.debug(f"Removed cache entry due to size bounds: {key}")


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        SHA256 hash of the arguments
    """
    # Create a deterministic string representation
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}

    # Convert to JSON string (handling non-serializable objects)
    try:
        key_string = json.dumps(key_data, sort_keys=True, default=str)
    except (TypeError, ValueError):
        # Fallback to string representation
        key_string = str(key_data)

    # Generate hash
    return hashlib.sha256(key_string.encode()).hexdigest()


def serialize_for_cache(obj: Any) -> str:
    """
    Serialize an object for caching

    Args:
        obj: Object to serialize

    Returns:
        Serialized string representation
    """
    try:
        return json.dumps(obj, default=str, sort_keys=True)
    except (TypeError, ValueError):
        return str(obj)


def calculate_memory_usage(obj: Any) -> float:
    """
    Estimate memory usage of an object in MB

    Args:
        obj: Object to measure

    Returns:
        Estimated memory usage in MB
    """
    import sys

    try:
        # Get size in bytes and convert to MB
        size_bytes = sys.getsizeof(obj)

        # For complex objects, try to get recursive size
        if hasattr(obj, "__dict__"):
            for attr_value in obj.__dict__.values():
                size_bytes += sys.getsizeof(attr_value)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                size_bytes += sys.getsizeof(item)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                size_bytes += sys.getsizeof(key) + sys.getsizeof(value)

        return size_bytes / (1024 * 1024)  # Convert to MB
    except Exception:
        # Fallback estimate
        return 0.001  # 1KB default


class CacheStats:
    """Cache statistics tracker"""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.errors = 0
        self._total_requests = 0
        self.puts = 0
        self.deletes = 0

    def record_hit(self) -> None:
        """Record a cache hit"""
        self.hits += 1
        self._total_requests += 1

    def record_miss(self) -> None:
        """Record a cache miss"""
        self.misses += 1
        self._total_requests += 1

    def record_eviction(self) -> None:
        """Record a cache eviction"""
        self.evictions += 1

    def record_error(self) -> None:
        """Record a cache error"""
        self.errors += 1

    def record_put(self) -> None:
        """Record a cache put operation"""
        self.puts += 1

    def record_delete(self) -> None:
        """Record a cache delete operation"""
        self.deletes += 1

    def hit_rate(self) -> float:
        """Get cache hit rate"""
        if self._total_requests == 0:
            return 0.0
        return self.hits / self._total_requests

    def miss_rate(self) -> float:
        """Get cache miss rate"""
        if self._total_requests == 0:
            return 0.0
        return self.misses / self._total_requests

    def total_requests(self) -> int:
        """Get total number of requests"""
        return self._total_requests

    def get_hit_rate(self) -> float:
        """Get cache hit rate"""
        if self._total_requests == 0:
            return 0.0
        return self.hits / self._total_requests

    def get_stats(self) -> Dict[str, Any]:
        """Get all cache statistics"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "errors": self.errors,
            "total_requests": self._total_requests,
            "puts": self.puts,
            "deletes": self.deletes,
            "hit_rate": self.get_hit_rate(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        return self.get_stats()

    def reset(self) -> None:
        """Reset all statistics"""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.errors = 0
        self._total_requests = 0
        self.puts = 0
        self.deletes = 0


def create_cache_entry(key: str, value: Any, ttl: Optional[float] = None) -> CacheEntry:
    """
    Create a new cache entry

    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds

    Returns:
        New cache entry
    """
    current_time = time.time()
    return CacheEntry(
        key=key,
        value=value,
        created_at=current_time,
        last_accessed=current_time,
        access_count=1,
        ttl=ttl,
    )


def validate_cache_key(key: str) -> bool:
    """
    Validate a cache key

    Args:
        key: Cache key to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(key, str):
        return False

    if len(key) == 0 or len(key) > 250:
        return False

    # Check for invalid characters
    invalid_chars = ["\n", "\r", "\t", "\0"]
    return not any(char in key for char in invalid_chars)


def cleanup_expired_entries(cache: Dict[str, CacheEntry]) -> int:
    """
    Remove expired entries from cache

    Args:
        cache: Cache dictionary to clean up

    Returns:
        Number of entries removed
    """
    expired_keys = [key for key, entry in cache.items() if entry.is_expired()]

    for key in expired_keys:
        del cache[key]

    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    return len(expired_keys)


def get_cache_info(cache: Dict[str, CacheEntry]) -> Dict[str, Any]:
    """
    Get information about cache contents

    Args:
        cache: Cache dictionary to analyze

    Returns:
        Cache information dictionary
    """
    if not cache:
        return {
            "size": 0,
            "memory_usage_mb": 0.0,
            "oldest_entry": None,
            "newest_entry": None,
            "expired_entries": 0,
        }

    current_time = time.time()
    entries = list(cache.values())

    # Calculate memory usage
    total_memory = sum(calculate_memory_usage(entry.value) for entry in entries)

    # Find oldest and newest entries
    oldest_entry = min(entries, key=lambda x: x.created_at)
    newest_entry = max(entries, key=lambda x: x.created_at)

    # Count expired entries
    expired_count = sum(1 for entry in entries if entry.is_expired())

    return {
        "size": len(cache),
        "memory_usage_mb": total_memory,
        "oldest_entry": {
            "key": oldest_entry.key,
            "age_seconds": current_time - oldest_entry.created_at,
        },
        "newest_entry": {
            "key": newest_entry.key,
            "age_seconds": current_time - newest_entry.created_at,
        },
        "expired_entries": expired_count,
    }


class LRUCache:
    """Least Recently Used (LRU) cache implementation"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []

    @property
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Put a value in the cache

        Returns:
            True if an eviction occurred, False otherwise
        """
        current_time = time.time()
        evicted = False

        if key in self.cache:
            # Update existing entry
            self.cache[key].value = value
            self.cache[key].ttl = ttl
            self.cache[key].touch()
            # Move to end of access order
            self._access_order.remove(key)
            self._access_order.append(key)
        else:
            # Create new entry
            entry = CacheEntry(key=key, value=value, created_at=current_time, ttl=ttl)
            self.cache[key] = entry
            self._access_order.append(key)

            # Evict if over capacity
            if len(self.cache) > self.max_size:
                # Remove least recently used
                lru_key = self._access_order.pop(0)
                del self.cache[lru_key]
                evicted = True

        return evicted

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache"""
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if entry.is_expired():
            # Remove expired entry
            del self.cache[key]
            self._access_order.remove(key)
            return None

        # Move to end of access order (most recently used)
        self._access_order.remove(key)
        self._access_order.append(key)

        return entry.access()

    def delete(self, key: str) -> bool:
        """Delete a key from the cache"""
        if key not in self.cache:
            return False

        del self.cache[key]
        self._access_order.remove(key)
        return True

    def clear(self) -> None:
        """Clear all entries from the cache"""
        self.cache.clear()
        self._access_order.clear()


class TTLCache:
    """Time To Live (TTL) cache implementation"""

    def __init__(self, default_ttl: Optional[float] = 300):
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put a value in the cache with TTL"""
        current_time = time.time()
        ttl_value = ttl if ttl is not None else self.default_ttl

        entry = CacheEntry(key=key, value=value, created_at=current_time, ttl=ttl_value)

        self.cache[key] = entry

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache"""
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if entry.is_expired():
            # Remove expired entry
            del self.cache[key]
            return None

        return entry.access()

    def delete(self, key: str) -> bool:
        """Delete a key from the cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all entries from the cache"""
        self.cache.clear()

    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count removed"""
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)


class CacheManager:
    """High-level cache manager with multiple cache types and namespaces"""

    def __init__(self, policy: "CachePolicy"):
        self.policy = policy
        self.caches: Dict[str, LRUCache] = {}
        self.stats = CacheStats()

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        namespace: str = "default",
    ) -> None:
        """Set a value in the cache"""
        if namespace not in self.caches:
            self.caches[namespace] = LRUCache(max_size=self.policy.max_size)

        cache = self.caches[namespace]
        evicted = cache.put(key, value, ttl)

        if evicted:
            self.stats.record_eviction()

        self.stats.record_put()

    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get a value from the cache"""
        if namespace not in self.caches:
            self.stats.record_miss()
            return None

        cache = self.caches[namespace]
        value = cache.get(key)

        if value is None:
            self.stats.record_miss()
        else:
            self.stats.record_hit()

        return value

    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete a key from the cache"""
        if namespace not in self.caches:
            return False

        cache = self.caches[namespace]
        deleted = cache.delete(key)

        if deleted:
            self.stats.record_delete()

        return deleted

    async def clear(self, namespace: Optional[str] = None) -> None:
        """Clear cache entries"""
        if namespace is None:
            # Clear all namespaces
            for cache in self.caches.values():
                cache.clear()
            self.caches.clear()
        else:
            # Clear specific namespace
            if namespace in self.caches:
                self.caches[namespace].clear()
                del self.caches[namespace]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        base_stats = self.stats.get_stats()
        base_stats["namespaces"] = len(self.caches)
        base_stats["total_entries"] = sum(cache.size for cache in self.caches.values())
        return base_stats
