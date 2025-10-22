"""Cache repository interface."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class CacheRepository(ABC):
    """Abstract repository for caching operations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value with optional TTL in seconds."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value by key."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on existing key."""
        pass

    @abstractmethod
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key."""
        pass

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value."""
        pass

    @abstractmethod
    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement numeric value."""
        pass

    @abstractmethod
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values by keys."""
        pass

    @abstractmethod
    async def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple key-value pairs."""
        pass

    @abstractmethod
    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys, return count deleted."""
        pass

    @abstractmethod
    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        pass

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        pass

    @abstractmethod
    async def flush_all(self) -> bool:
        """Flush all cache entries."""
        pass

    @abstractmethod
    async def get_json(self, key: str) -> Optional[Dict]:
        """Get JSON value by key."""
        pass

    @abstractmethod
    async def set_json(self, key: str, value: Dict, ttl: Optional[int] = None) -> bool:
        """Set JSON value with optional TTL."""
        pass
