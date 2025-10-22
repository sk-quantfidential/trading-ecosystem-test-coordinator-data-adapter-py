"""Stub cache repository implementation."""
import structlog
import orjson
from datetime import datetime, UTC, timedelta
from typing import Any, Dict, List, Optional

from test_coordinator_data_adapter.interfaces import CacheRepository

logger = structlog.get_logger(__name__)


class CacheEntry:
    """Cache entry with value and expiration."""

    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = datetime.now(UTC)
        self.expires_at = (
            self.created_at + timedelta(seconds=ttl) if ttl is not None else None
        )

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def get_ttl(self) -> Optional[int]:
        """Get remaining TTL in seconds."""
        if self.expires_at is None:
            return None
        remaining = (self.expires_at - datetime.now(UTC)).total_seconds()
        return max(0, int(remaining))


class StubCacheRepository(CacheRepository):
    """In-memory stub implementation of cache repository."""

    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        logger.info("stub_cache_repository_initialized", storage="in-memory")

    def _clean_expired(self):
        """Remove expired entries."""
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]

    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        self._clean_expired()
        entry = self._cache.get(key)
        if entry is None or entry.is_expired():
            logger.debug("cache_miss", key=key)
            return None
        logger.debug("cache_hit", key=key)
        return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value with optional TTL in seconds."""
        self._cache[key] = CacheEntry(value, ttl)
        logger.debug("cache_set", key=key, has_ttl=ttl is not None)
        return True

    async def delete(self, key: str) -> bool:
        """Delete value by key."""
        if key in self._cache:
            del self._cache[key]
            logger.debug("cache_deleted", key=key)
            return True
        logger.debug("cache_delete_not_found", key=key)
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        self._clean_expired()
        exists = key in self._cache and not self._cache[key].is_expired()
        logger.debug("cache_exists_check", key=key, exists=exists)
        return exists

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on existing key."""
        entry = self._cache.get(key)
        if entry is None:
            logger.debug("cache_expire_not_found", key=key)
            return False
        entry.expires_at = datetime.now(UTC) + timedelta(seconds=ttl)
        logger.debug("cache_expire_set", key=key, ttl=ttl)
        return True

    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        ttl = entry.get_ttl()
        logger.debug("cache_ttl_retrieved", key=key, ttl=ttl)
        return ttl

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value."""
        entry = self._cache.get(key)
        if entry is None:
            self._cache[key] = CacheEntry(amount)
            logger.debug("cache_increment_new", key=key, value=amount)
            return amount

        if not isinstance(entry.value, int):
            raise ValueError(f"Value for key {key} is not an integer")

        entry.value += amount
        logger.debug("cache_incremented", key=key, new_value=entry.value)
        return entry.value

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement numeric value."""
        return await self.increment(key, -amount)

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values by keys."""
        self._clean_expired()
        result = {}
        for key in keys:
            entry = self._cache.get(key)
            if entry is not None and not entry.is_expired():
                result[key] = entry.value
        logger.debug("cache_get_many", requested=len(keys), found=len(result))
        return result

    async def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple key-value pairs."""
        for key, value in items.items():
            self._cache[key] = CacheEntry(value, ttl)
        logger.debug("cache_set_many", count=len(items), has_ttl=ttl is not None)
        return True

    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys, return count deleted."""
        count = 0
        for key in keys:
            if key in self._cache:
                del self._cache[key]
                count += 1
        logger.debug("cache_delete_many", requested=len(keys), deleted=count)
        return count

    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        self._clean_expired()
        # Simple pattern matching: * matches any characters
        import re
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(f"^{regex_pattern}$")

        matching_keys = [k for k in self._cache.keys() if regex.match(k)]
        logger.debug("cache_keys_pattern", pattern=pattern, count=len(matching_keys))
        return matching_keys

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        keys_to_delete = await self.keys(pattern)
        return await self.delete_many(keys_to_delete)

    async def flush_all(self) -> bool:
        """Flush all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.debug("cache_flushed", count=count)
        return True

    async def get_json(self, key: str) -> Optional[Dict]:
        """Get JSON value by key."""
        value = await self.get(key)
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        # If stored as string, parse it
        if isinstance(value, (str, bytes)):
            try:
                return orjson.loads(value)
            except orjson.JSONDecodeError:
                logger.warning("cache_json_decode_error", key=key)
                return None
        return None

    async def set_json(self, key: str, value: Dict, ttl: Optional[int] = None) -> bool:
        """Set JSON value with optional TTL."""
        # Store as dict directly in memory
        return await self.set(key, value, ttl)
