#!/usr/bin/env python3
"""
High-performance in-memory cache with LRU eviction and TTL support
Provides 10-100x faster access than disk-based cache for hot data
"""

import time
import sys
import threading
from collections import OrderedDict
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import weakref
import heapq
from .logger import log_info, log_warning


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    key: str
    value: Any
    size: int
    created_at: float
    last_accessed: float
    ttl: float  # Time-to-live in seconds
    access_count: int = 0
    entity_type: str = "unknown"
    
    def is_expired(self) -> bool:
        """Check if entry has expired based on TTL"""
        return time.time() > self.created_at + self.ttl
    
    def is_stale(self, access_ttl: float) -> bool:
        """Check if entry is stale based on last access time"""
        return time.time() > self.last_accessed + access_ttl
    
    def touch(self):
        """Update last accessed time and increment access count"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    total_size: int = 0
    entry_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def size_mb(self) -> float:
        """Get total size in MB"""
        return self.total_size / (1024 * 1024)


class SizeEstimator:
    """Estimate memory size of Python objects"""
    
    @staticmethod
    def estimate_size(obj: Any) -> int:
        """Estimate object size in bytes"""
        # Use sys.getsizeof with recursive calculation for containers
        return SizeEstimator._deep_sizeof(obj)
    
    @staticmethod
    def _deep_sizeof(obj, seen=None):
        """Recursively calculate object size"""
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        
        seen.add(obj_id)
        
        if isinstance(obj, dict):
            size += sum(SizeEstimator._deep_sizeof(k, seen) + 
                       SizeEstimator._deep_sizeof(v, seen) 
                       for k, v in obj.items())
        elif hasattr(obj, '__dict__'):
            size += SizeEstimator._deep_sizeof(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            try:
                size += sum(SizeEstimator._deep_sizeof(i, seen) for i in obj)
            except TypeError:
                pass
                
        return size


class MemoryCache:
    """
    Thread-safe LRU memory cache with TTL and size limits
    
    Features:
    - LRU eviction when size limit reached
    - TTL-based expiration
    - Entity-specific cache policies
    - Automatic cleanup of expired entries
    - Performance statistics
    """
    
    def __init__(self, 
                 max_size_mb: int = 100,
                 default_ttl_days: float = 3.0,
                 access_ttl_days: float = 3.0,
                 cleanup_interval_seconds: int = 300):
        """
        Initialize memory cache
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            default_ttl_days: Default TTL for entries in days
            access_ttl_days: TTL based on last access time
            cleanup_interval_seconds: Interval for cleanup task
        """
        self.max_size = max_size_mb * 1024 * 1024  # Convert to bytes
        self.default_ttl = default_ttl_days * 86400  # Convert to seconds
        self.access_ttl = access_ttl_days * 86400
        self.cleanup_interval = cleanup_interval_seconds
        
        # Main cache storage - OrderedDict for LRU
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = CacheStats()
        
        # Background cleanup
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        self._start_cleanup_thread()
        
        # Size estimator
        self._size_estimator = SizeEstimator()
        
        # Log initialization only in debug mode
        # log_info(f"💾 Memory cache initialized: {max_size_mb}MB, {default_ttl_days} days TTL")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache with LRU update
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self.stats.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired() or entry.is_stale(self.access_ttl):
                self._remove_entry(key)
                self.stats.expirations += 1
                self.stats.misses += 1
                return None
            
            # Update access time and move to end (most recently used)
            entry.touch()
            self._cache.move_to_end(key)
            
            self.stats.hits += 1
            return entry.value
    
    def put(self, key: str, value: Any, 
            ttl_days: Optional[float] = None,
            entity_type: str = "unknown") -> bool:
        """
        Put value in cache with size tracking
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_days: Optional TTL override in days
            entity_type: Type of entity for policy application
            
        Returns:
            True if cached successfully
        """
        # Estimate size
        size = self._size_estimator.estimate_size(value)
        
        # Check if single item exceeds max size
        if size > self.max_size:
            log_warning(f"Item too large for cache: {size / 1024 / 1024:.1f}MB > {self.max_size / 1024 / 1024}MB")
            return False
        
        with self._lock:
            # Remove existing entry if present
            if key in self._cache:
                self._remove_entry(key)
            
            # Evict entries until we have space
            while self.stats.total_size + size > self.max_size and self._cache:
                self._evict_lru()
            
            # Create new entry
            ttl_seconds = (ttl_days * 86400) if ttl_days else self.default_ttl
            entry = CacheEntry(
                key=key,
                value=value,
                size=size,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl_seconds,
                entity_type=entity_type
            )
            
            # Add to cache
            self._cache[key] = entry
            self.stats.total_size += size
            self.stats.entry_count += 1
            
            return True
    
    def remove(self, key: str) -> bool:
        """Remove entry from cache"""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self.stats = CacheStats()
            log_info("🗑️  Memory cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                'hits': self.stats.hits,
                'misses': self.stats.misses,
                'hit_rate': self.stats.hit_rate,
                'evictions': self.stats.evictions,
                'expirations': self.stats.expirations,
                'size_mb': self.stats.size_mb,
                'max_size_mb': self.max_size / 1024 / 1024,
                'entry_count': self.stats.entry_count,
                'entries_by_type': self._get_entries_by_type()
            }
    
    def _remove_entry(self, key: str):
        """Remove entry and update stats (must be called with lock)"""
        if key in self._cache:
            entry = self._cache[key]
            self.stats.total_size -= entry.size
            self.stats.entry_count -= 1
            del self._cache[key]
    
    def _evict_lru(self):
        """Evict least recently used entry (must be called with lock)"""
        if self._cache:
            # First item is LRU in OrderedDict
            key, entry = self._cache.popitem(last=False)
            self.stats.total_size -= entry.size
            self.stats.entry_count -= 1
            self.stats.evictions += 1
    
    def _cleanup_expired(self):
        """Remove expired entries (runs in background)"""
        with self._lock:
            expired_keys = []
            current_time = time.time()
            
            for key, entry in self._cache.items():
                if entry.is_expired() or entry.is_stale(self.access_ttl):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
                self.stats.expirations += 1
            
            if expired_keys:
                log_info(f"🧹 Cleaned {len(expired_keys)} expired cache entries")
    
    def _cleanup_thread_func(self):
        """Background cleanup thread"""
        while not self._stop_cleanup.wait(self.cleanup_interval):
            try:
                self._cleanup_expired()
            except Exception as e:
                log_warning(f"Cache cleanup error: {e}")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_thread_func,
            daemon=True,
            name="MemoryCache-Cleanup"
        )
        self._cleanup_thread.start()
    
    def _get_entries_by_type(self) -> Dict[str, int]:
        """Get count of entries by entity type"""
        counts = {}
        for entry in self._cache.values():
            counts[entry.entity_type] = counts.get(entry.entity_type, 0) + 1
        return counts
    
    def shutdown(self):
        """Shutdown cache and cleanup thread"""
        self._stop_cleanup.set()
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        self.clear()
        log_info("💾 Memory cache shutdown complete")


class CachePolicy:
    """
    Entity-specific cache policies
    
    Defines TTL and size limits per entity type
    """
    
    # Default policies per entity type
    DEFAULT_POLICIES = {
        'file': {
            'ttl_days': 7.0,      # Files change less frequently
            'max_size_mb': 10.0,  # Files can be large
            'cache_priority': 0.8
        },
        'function': {
            'ttl_days': 3.0,      # Functions change moderately
            'max_size_mb': 5.0,   # Functions are medium-sized
            'cache_priority': 0.9
        },
        'class': {
            'ttl_days': 5.0,      # Classes are relatively stable
            'max_size_mb': 8.0,   # Classes can be complex
            'cache_priority': 0.85
        },
        'method': {
            'ttl_days': 3.0,      # Methods change with classes
            'max_size_mb': 3.0,   # Methods are smaller
            'cache_priority': 0.8
        },
        'import': {
            'ttl_days': 1.0,      # Imports change frequently
            'max_size_mb': 2.0,   # Imports are small
            'cache_priority': 0.6
        },
        'pattern': {
            'ttl_days': 14.0,     # Patterns are stable
            'max_size_mb': 15.0,  # Pattern data can be large
            'cache_priority': 0.7
        },
        'metadata': {
            'ttl_days': 1.0,      # Metadata updates frequently
            'max_size_mb': 5.0,   # Metadata is medium-sized
            'cache_priority': 0.5
        }
    }
    
    def __init__(self, custom_policies: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize cache policy
        
        Args:
            custom_policies: Optional custom policies to override defaults
        """
        self.policies = self.DEFAULT_POLICIES.copy()
        if custom_policies:
            self.policies.update(custom_policies)
    
    def get_ttl_days(self, entity_type: str) -> float:
        """Get TTL in days for entity type"""
        policy = self.policies.get(entity_type, self.policies.get('file'))
        return policy['ttl_days']
    
    def get_max_size_mb(self, entity_type: str) -> float:
        """Get max size in MB for entity type"""
        policy = self.policies.get(entity_type, self.policies.get('file'))
        return policy['max_size_mb']
    
    def should_cache(self, entity_type: str, size_mb: float) -> bool:
        """Check if entity should be cached based on policy"""
        max_size = self.get_max_size_mb(entity_type)
        return size_mb <= max_size
    
    def get_priority(self, entity_type: str) -> float:
        """Get cache priority for entity type (0.0-1.0)"""
        policy = self.policies.get(entity_type, self.policies.get('file'))
        return policy.get('cache_priority', 0.5)