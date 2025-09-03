#!/usr/bin/env python3
"""
Hybrid cache system combining memory and disk caching
Provides seamless fallback and cache warming strategies
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from concurrent.futures import ThreadPoolExecutor
import json
from dataclasses import asdict

from typing import TYPE_CHECKING

from .memory_cache import MemoryCache, CachePolicy
from .cache_utils import CacheKeyGenerator
from .logger import log_info, log_warning

if TYPE_CHECKING:
    from .cache_manager import CacheManager, FileCache


class HybridCache:
    """
    Unified cache interface combining memory and disk caching
    
    Features:
    - Transparent memory + disk cache
    - Automatic cache warming
    - Background synchronization
    - Policy-based caching decisions
    """
    
    def __init__(self, 
                 memory_cache: Optional[MemoryCache] = None,
                 disk_cache: Optional['CacheManager'] = None,
                 cache_policy: Optional[CachePolicy] = None,
                 enable_warming: bool = True):
        """
        Initialize hybrid cache
        
        Args:
            memory_cache: Memory cache instance
            disk_cache: Disk cache instance
            cache_policy: Cache policy for entity types
            enable_warming: Enable cache warming on startup
        """
        self.memory = memory_cache or MemoryCache()
        self.disk = disk_cache
        self.policy = cache_policy or CachePolicy()
        self.enable_warming = enable_warming
        
        # Background executor for async operations
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="HybridCache")
        
        # Cache warming queue
        self._warm_queue = asyncio.Queue() if enable_warming else None
        self._warming_task = None
        
        if enable_warming:
            self._start_cache_warming()
    
    def get(self, key: str, entity_type: str = "unknown") -> Optional[Any]:
        """
        Get value from cache (memory first, then disk)
        
        Args:
            key: Cache key
            entity_type: Type of entity for metrics
            
        Returns:
            Cached value or None
        """
        # Try memory cache first
        value = self.memory.get(key)
        if value is not None:
            return value
        
        # Try disk cache if available
        if self.disk:
            try:
                cached_file = self.disk.get_cached_result(key)
                if cached_file:
                    # Convert FileCache to dict for compatibility
                    value = self._file_cache_to_dict(cached_file)
                    
                    # Warm memory cache with disk data
                    self._warm_memory_cache(key, value, entity_type)
                    
                    return value
            except Exception as e:
                log_warning(f"Disk cache error: {e}")
        
        return None
    
    
    def put(self, key: str, value: Any, entity_type: str = "unknown") -> bool:
        """
        Put value in cache (both memory and disk based on policy)
        
        Args:
            key: Cache key
            value: Value to cache
            entity_type: Type of entity
            
        Returns:
            True if cached successfully
        """
        # Check size and policy
        size_mb = self.memory._size_estimator.estimate_size(value) / 1024 / 1024
        
        if not self.policy.should_cache(entity_type, size_mb):
            return False
        
        # Put in memory cache with entity-specific TTL
        ttl_days = self.policy.get_ttl_days(entity_type)
        memory_success = self.memory.put(key, value, ttl_days=ttl_days, entity_type=entity_type)
        
        # Put in disk cache if available
        disk_success = True
        if self.disk and isinstance(value, dict):
            try:
                # For file-based keys, use disk cache
                if key.startswith("file:") or entity_type == "file":
                    nodes = value.get('nodes', {})
                    edges = value.get('edges', [])
                    patterns = value.get('patterns', [])
                    libraries = value.get('libraries', {})
                    infrastructure = value.get('infrastructure', {})
                    
                    self.disk.cache_file_result(
                        key.replace("file:", ""),
                        nodes, edges, patterns, libraries, infrastructure
                    )
            except Exception as e:
                log_warning(f"Disk cache write error: {e}")
                disk_success = False
        
        return memory_success or disk_success
    
    
    def invalidate(self, key: str) -> bool:
        """Remove entry from both caches"""
        memory_removed = self.memory.remove(key)
        
        # Note: Current disk cache doesn't have remove method
        # This would need to be implemented in CacheManager
        
        return memory_removed
    
    def warm_cache(self, keys: List[str], entity_types: Optional[List[str]] = None):
        """
        Warm memory cache with specific keys from disk
        
        Args:
            keys: List of cache keys to warm
            entity_types: Optional list of entity types
        """
        if not self.disk or not self.enable_warming:
            return
        
        entity_types = entity_types or ["unknown"] * len(keys)
        
        for key, entity_type in zip(keys, entity_types):
            if self.memory.get(key) is None:  # Not already in memory
                value = self.get(key, entity_type)  # This will warm the cache
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined cache statistics"""
        memory_stats = self.memory.get_stats()
        
        disk_stats = {}
        if self.disk:
            disk_stats = self.disk.get_cache_stats()
        
        return {
            'memory': memory_stats,
            'disk': disk_stats,
            'hybrid': {
                'memory_priority_hits': memory_stats.get('hits', 0),
                'disk_fallback_hits': disk_stats.get('total_entries', 0),
                'total_size_mb': memory_stats.get('size_mb', 0) + disk_stats.get('cache_db_size', 0) / 1024 / 1024
            }
        }
    
    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()
        
        log_info("📊 Hybrid Cache Statistics:")
        log_info(f"  Memory Cache:")
        log_info(f"    Hit rate: {stats['memory']['hit_rate']:.1f}%")
        log_info(f"    Size: {stats['memory']['size_mb']:.1f}MB / {stats['memory']['max_size_mb']}MB")
        log_info(f"    Entries: {stats['memory']['entry_count']}")
        
        if stats['disk']:
            log_info(f"  Disk Cache:")
            log_info(f"    Entries: {stats['disk']['total_entries']}")
            log_info(f"    Size: {stats['disk']['cache_db_size'] / 1024:.1f}KB")
    
    def _file_cache_to_dict(self, file_cache: 'FileCache') -> Dict[str, Any]:
        """Convert FileCache object to dict"""
        return {
            'file_path': file_cache.file_path,
            'nodes': file_cache.nodes,
            'edges': file_cache.edges,
            'patterns': file_cache.patterns,
            'libraries': file_cache.libraries,
            'infrastructure': file_cache.infrastructure,
            'cached_at': file_cache.cached_at
        }
    
    def _warm_memory_cache(self, key: str, value: Any, entity_type: str):
        """Warm memory cache with value from disk"""
        try:
            ttl_days = self.policy.get_ttl_days(entity_type)
            self.memory.put(key, value, ttl_days=ttl_days, entity_type=entity_type)
        except Exception as e:
            log_warning(f"Failed to warm memory cache: {e}")
    
    def _start_cache_warming(self):
        """Start background cache warming task"""
        # This could be enhanced to pre-warm frequently accessed items
        # For now, it's a placeholder for future implementation
        pass
    
    def shutdown(self):
        """Shutdown hybrid cache"""
        self.memory.shutdown()
        self._executor.shutdown(wait=True)
        log_info("🔄 Hybrid cache shutdown complete")




# Singleton instance for global access
_hybrid_cache_instance = None


def get_hybrid_cache(memory_size_mb: int = 100,
                    ttl_days: float = 3.0,
                    project_path: Optional[str] = None) -> HybridCache:
    """
    Get or create hybrid cache instance
    
    Args:
        memory_size_mb: Memory cache size limit
        ttl_days: Default TTL in days
        project_path: Optional project path for disk cache
        
    Returns:
        HybridCache instance
    """
    global _hybrid_cache_instance
    
    if _hybrid_cache_instance is None:
        memory_cache = MemoryCache(
            max_size_mb=memory_size_mb,
            default_ttl_days=ttl_days
        )
        
        disk_cache = None
        if project_path:
            try:
                from pathlib import Path
                disk_cache = CacheManager(Path(project_path))
            except Exception as e:
                log_warning(f"Failed to initialize disk cache: {e}")
        
        _hybrid_cache_instance = HybridCache(
            memory_cache=memory_cache,
            disk_cache=disk_cache
        )
    
    return _hybrid_cache_instance