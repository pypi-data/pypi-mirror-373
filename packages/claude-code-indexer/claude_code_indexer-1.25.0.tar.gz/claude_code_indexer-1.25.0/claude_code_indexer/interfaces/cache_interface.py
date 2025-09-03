"""
Cache interface for dependency injection
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from pathlib import Path


class ICache(ABC):
    """Interface for caching operations"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache with optional TTL"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete item from cache"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        pass