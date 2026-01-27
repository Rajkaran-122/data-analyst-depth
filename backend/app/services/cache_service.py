"""
Cache Service

Redis-based caching for performance optimization.
"""

from typing import Optional, Any
import json
import logging

import redis

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Service for caching data using Redis.
    
    Provides methods for getting, setting, and invalidating cached data.
    Falls back gracefully if Redis is unavailable.
    """
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._available = False
        self._connect()
    
    def _connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            self._client.ping()
            self._available = True
            logger.info("Cache service connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed, caching disabled: {e}")
            self._available = False
    
    @property
    def is_available(self) -> bool:
        """Check if cache is available."""
        return self._available
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self._available:
            return None
        
        try:
            value = self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                self._client.setex(key, ttl, serialized)
            else:
                self._client.set(key, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False
        
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Key pattern (e.g., "user:*:dashboard")
            
        Returns:
            Number of keys deleted
        """
        if not self._available:
            return 0
        
        try:
            keys = list(self._client.scan_iter(pattern))
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern failed for {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
        """
        if not self._available:
            return False
        
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.warning(f"Cache exists check failed for key {key}: {e}")
            return False
    
    def get_or_set(
        self,
        key: str,
        factory: callable,
        ttl: Optional[int] = None,
    ) -> Any:
        """
        Get value from cache or set it using factory function.
        
        Args:
            key: Cache key
            factory: Function to generate value if not cached
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            Cached or generated value
        """
        # Try to get from cache
        cached = self.get(key)
        if cached is not None:
            return cached
        
        # Generate value
        value = factory()
        
        # Cache it
        self.set(key, value, ttl)
        
        return value
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None if failed
        """
        if not self._available:
            return None
        
        try:
            return self._client.incrby(key, amount)
        except Exception as e:
            logger.warning(f"Cache increment failed for key {key}: {e}")
            return None
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        if not self._available:
            return None
        
        try:
            return self._client.ttl(key)
        except Exception as e:
            logger.warning(f"Cache TTL check failed for key {key}: {e}")
            return None
    
    def flush_all(self) -> bool:
        """
        Clear all cached data.
        
        Warning: Use with caution in production!
        
        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False
        
        try:
            self._client.flushdb()
            logger.warning("Cache flushed")
            return True
        except Exception as e:
            logger.error(f"Cache flush failed: {e}")
            return False


# Cache key builders for consistency
class CacheKeys:
    """Helper class for building consistent cache keys."""
    
    @staticmethod
    def dashboard_stats(user_id: str) -> str:
        return f"dashboard:stats:{user_id}"
    
    @staticmethod
    def dashboard_activity(user_id: str, limit: int) -> str:
        return f"dashboard:activity:{user_id}:{limit}"
    
    @staticmethod
    def analytics_trends(user_id: str, period: str, metric: str) -> str:
        return f"analytics:trends:{user_id}:{period}:{metric}"
    
    @staticmethod
    def analytics_insights(user_id: str) -> str:
        return f"analytics:insights:{user_id}"
    
    @staticmethod
    def user_settings(user_id: str) -> str:
        return f"settings:{user_id}"
    
    @staticmethod
    def dataset_preview(dataset_id: str, limit: int) -> str:
        return f"dataset:preview:{dataset_id}:{limit}"
    
    @staticmethod
    def report(report_id: str) -> str:
        return f"report:{report_id}"


# Global cache instance
cache = CacheService()
