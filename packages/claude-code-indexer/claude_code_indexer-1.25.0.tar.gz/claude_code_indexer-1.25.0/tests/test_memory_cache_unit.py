#!/usr/bin/env python3
"""
Unit tests for memory cache implementation
Focus on edge cases and specific functionality
"""

import pytest
import time
import threading
import sys
from unittest.mock import Mock, patch

sys.path.insert(0, '../claude_code_indexer')
from claude_code_indexer.memory_cache import MemoryCache, CachePolicy, SizeEstimator, CacheEntry
from claude_code_indexer.hybrid_cache import HybridCache, CacheKeyGenerator


class TestMemoryCache:
    """Unit tests for MemoryCache class"""
    
    def test_initialization(self):
        """Test cache initialization with various parameters"""
        cache = MemoryCache(max_size_mb=50, default_ttl_days=2.0)
        
        assert cache.max_size == 50 * 1024 * 1024
        assert cache.default_ttl == 2.0 * 86400
        assert cache.stats.hits == 0
        assert cache.stats.misses == 0
    
    def test_put_and_get_basic(self):
        """Test basic put and get operations"""
        cache = MemoryCache(max_size_mb=10)
        
        # Put a value
        assert cache.put("key1", {"data": "value1"}) is True
        
        # Get the value
        value = cache.get("key1")
        assert value == {"data": "value1"}
        assert cache.stats.hits == 1
        
        # Get non-existent key
        assert cache.get("key2") is None
        assert cache.stats.misses == 1
    
    def test_ttl_expiration(self):
        """Test TTL expiration"""
        cache = MemoryCache(max_size_mb=10)
        
        # Put with very short TTL
        cache.put("expire_key", "value", ttl_days=0.00001)  # ~1 second
        
        # Should be available immediately
        assert cache.get("expire_key") == "value"
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should be expired
        assert cache.get("expire_key") is None
        assert cache.stats.expirations >= 1
    
    def test_lru_eviction(self):
        """Test LRU eviction behavior"""
        cache = MemoryCache(max_size_mb=1)  # Very small cache
        
        # Fill cache with entries that exceed the limit
        for i in range(10):
            data = "x" * 200000  # ~200KB each (total 2MB > 1MB limit)
            cache.put(f"key{i}", data)
        
        # First keys should be evicted
        assert cache.get("key0") is None
        assert cache.get("key1") is None
        
        # Recent keys should still be there
        assert cache.get("key9") is not None
        assert cache.stats.evictions > 0
    
    def test_access_updates_lru(self):
        """Test that accessing an entry updates its LRU position"""
        cache = MemoryCache(max_size_mb=1)
        
        # Add entries - use larger sizes to ensure eviction
        cache.put("key1", "x" * 200000)  # ~200KB
        cache.put("key2", "x" * 200000)  # ~200KB
        cache.put("key3", "x" * 200000)  # ~200KB
        
        # Access key1 to make it recently used (moves to end of OrderedDict)
        cache.get("key1")
        
        # Add more to trigger eviction - need to exceed 1MB limit
        cache.put("key4", "x" * 200000)  # ~200KB
        cache.put("key5", "x" * 200000)  # ~200KB
        cache.put("key6", "x" * 200000)  # ~200KB - This should trigger eviction
        
        # key1 should still be there (was accessed, so more recently used)
        assert cache.get("key1") is not None
        # key2 should be evicted (least recently used - not accessed after initial put)
        assert cache.get("key2") is None
    
    def test_oversized_entry_rejection(self):
        """Test rejection of entries larger than cache size"""
        cache = MemoryCache(max_size_mb=1)
        
        # Try to add 2MB entry to 1MB cache
        huge_data = "x" * (2 * 1024 * 1024)
        assert cache.put("huge_key", huge_data) is False
        assert cache.get("huge_key") is None
    
    def test_clear_cache(self):
        """Test cache clearing"""
        cache = MemoryCache(max_size_mb=10)
        
        # Add some entries
        for i in range(10):
            cache.put(f"key{i}", f"value{i}")
        
        assert cache.stats.entry_count == 10
        
        # Clear cache
        cache.clear()
        
        assert cache.stats.entry_count == 0
        assert cache.stats.total_size == 0
        assert cache.get("key0") is None
    
    def test_remove_specific_entry(self):
        """Test removing specific cache entry"""
        cache = MemoryCache(max_size_mb=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Remove key1
        assert cache.remove("key1") is True
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        
        # Try to remove non-existent key
        assert cache.remove("key3") is False
    
    def test_stats_accuracy(self):
        """Test statistics accuracy"""
        cache = MemoryCache(max_size_mb=10)
        
        # Perform operations
        cache.put("key1", "value1")  # Put
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        cache.put("key2", "value2")  # Put
        cache.get("key2")  # Hit
        
        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] == pytest.approx(66.67, rel=0.1)
        assert stats['entry_count'] == 2
    
    def test_entity_type_tracking(self):
        """Test tracking of entity types"""
        cache = MemoryCache(max_size_mb=10)
        
        # Add different entity types
        cache.put("file1", "data", entity_type="file")
        cache.put("func1", "data", entity_type="function")
        cache.put("func2", "data", entity_type="function")
        cache.put("class1", "data", entity_type="class")
        
        stats = cache.get_stats()
        entries_by_type = stats['entries_by_type']
        
        assert entries_by_type['file'] == 1
        assert entries_by_type['function'] == 2
        assert entries_by_type['class'] == 1
    
    def test_background_cleanup(self):
        """Test background cleanup thread"""
        cache = MemoryCache(max_size_mb=10, cleanup_interval_seconds=1)
        
        # Add entries with short TTL
        for i in range(5):
            cache.put(f"key{i}", "value", ttl_days=0.00001)  # ~1 second
        
        # Wait for cleanup
        time.sleep(2.5)
        
        # All should be cleaned up
        for i in range(5):
            assert cache.get(f"key{i}") is None
    
    def test_thread_safety(self):
        """Test thread safety with concurrent operations"""
        cache = MemoryCache(max_size_mb=10)
        errors = []
        
        def writer_thread(thread_id):
            """Thread that writes to cache"""
            try:
                for i in range(100):
                    cache.put(f"t{thread_id}_k{i}", f"value_{i}")
            except Exception as e:
                errors.append(e)
        
        def reader_thread(thread_id):
            """Thread that reads from cache"""
            try:
                for i in range(100):
                    cache.get(f"t{thread_id % 5}_k{i}")
            except Exception as e:
                errors.append(e)
        
        # Start threads
        threads = []
        for i in range(5):
            t1 = threading.Thread(target=writer_thread, args=(i,))
            t2 = threading.Thread(target=reader_thread, args=(i,))
            threads.extend([t1, t2])
            t1.start()
            t2.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Should have no errors
        assert len(errors) == 0
    
    def test_shutdown(self):
        """Test cache shutdown"""
        cache = MemoryCache(max_size_mb=10)
        
        # Add some data
        cache.put("key1", "value1")
        
        # Shutdown
        cache.shutdown()
        
        # Cache should be cleared
        assert cache.stats.entry_count == 0


class TestCachePolicy:
    """Unit tests for CachePolicy class"""
    
    def test_default_policies(self):
        """Test default cache policies"""
        policy = CachePolicy()
        
        # Test file policy
        assert policy.get_ttl_days("file") == 7.0
        assert policy.get_max_size_mb("file") == 10.0
        
        # Test function policy
        assert policy.get_ttl_days("function") == 3.0
        assert policy.get_max_size_mb("function") == 5.0
    
    def test_custom_policies(self):
        """Test custom cache policies"""
        custom = {
            "file": {"ttl_days": 14.0, "max_size_mb": 20.0},
            "custom_type": {"ttl_days": 1.0, "max_size_mb": 1.0}
        }
        
        policy = CachePolicy(custom_policies=custom)
        
        # Custom policy should override default
        assert policy.get_ttl_days("file") == 14.0
        
        # New type should work
        assert policy.get_ttl_days("custom_type") == 1.0
    
    def test_should_cache_decision(self):
        """Test caching decision based on size"""
        policy = CachePolicy()
        
        # Within limit
        assert policy.should_cache("file", 5.0) is True
        
        # Exceeds limit
        assert policy.should_cache("file", 15.0) is False
        
        # Edge case - exactly at limit
        assert policy.should_cache("file", 10.0) is True
    
    def test_unknown_entity_type(self):
        """Test handling of unknown entity types"""
        policy = CachePolicy()
        
        # Should fall back to file policy
        assert policy.get_ttl_days("unknown_type") == 7.0
        assert policy.get_max_size_mb("unknown_type") == 10.0


class TestSizeEstimator:
    """Unit tests for SizeEstimator class"""
    
    def test_simple_types(self):
        """Test size estimation for simple types"""
        estimator = SizeEstimator()
        
        # String
        size = estimator.estimate_size("hello")
        assert size > 0
        
        # List
        size = estimator.estimate_size([1, 2, 3, 4, 5])
        assert size > sys.getsizeof([])
        
        # Dict
        size = estimator.estimate_size({"key": "value"})
        assert size > sys.getsizeof({})
    
    def test_nested_structures(self):
        """Test size estimation for nested structures"""
        estimator = SizeEstimator()
        
        nested = {
            "list": [1, 2, 3],
            "dict": {"inner": "value"},
            "nested_list": [[1, 2], [3, 4]]
        }
        
        size = estimator.estimate_size(nested)
        
        # Should be larger than sum of individual components
        individual_sum = (
            sys.getsizeof(nested) +
            sys.getsizeof([1, 2, 3]) +
            sys.getsizeof({"inner": "value"}) +
            sys.getsizeof([[1, 2], [3, 4]])
        )
        
        assert size >= individual_sum * 0.8  # Allow some variance
    
    def test_circular_references(self):
        """Test handling of circular references"""
        estimator = SizeEstimator()
        
        # Create circular reference
        obj1 = {"name": "obj1"}
        obj2 = {"name": "obj2", "ref": obj1}
        obj1["ref"] = obj2
        
        # Should not infinite loop
        size = estimator.estimate_size(obj1)
        assert size > 0
        assert size < 10000  # Should not be huge due to circular ref


class TestCacheKeyGenerator:
    """Unit tests for CacheKeyGenerator"""
    
    def test_file_key_generation(self):
        """Test file key generation"""
        key = CacheKeyGenerator.file_key("/path/to/file.py")
        assert key == "file:/path/to/file.py"
    
    def test_node_key_generation(self):
        """Test node key generation"""
        key = CacheKeyGenerator.node_key("function", 123, "/path/file.py")
        assert key == "node:function:123:/path/file.py"
    
    def test_pattern_key_generation(self):
        """Test pattern key generation"""
        key = CacheKeyGenerator.pattern_key("singleton", "/path/file.py")
        assert key == "pattern:singleton:/path/file.py"
    
    def test_key_parsing(self):
        """Test parsing of cache keys"""
        # File key
        parsed = CacheKeyGenerator.parse_key("file:/path/to/file.py")
        assert parsed["type"] == "file"
        assert parsed["path"] == "/path/to/file.py"
        
        # Node key
        parsed = CacheKeyGenerator.parse_key("node:function:123:/path/file.py")
        assert parsed["type"] == "node"
        assert parsed["node_type"] == "function"
        assert parsed["node_id"] == "123"
        assert parsed["path"] == "/path/file.py"
        
        # Unknown key
        parsed = CacheKeyGenerator.parse_key("unknown_format")
        assert parsed["type"] == "unknown"


class TestHybridCache:
    """Unit tests for HybridCache"""
    
    def test_memory_first_strategy(self):
        """Test that memory cache is checked first"""
        memory_cache = Mock(spec=MemoryCache)
        disk_cache = Mock()
        
        hybrid = HybridCache(memory_cache=memory_cache, disk_cache=disk_cache)
        
        # Memory cache has the value
        memory_cache.get.return_value = "memory_value"
        
        result = hybrid.get("key1")
        
        assert result == "memory_value"
        memory_cache.get.assert_called_once_with("key1")
        # Disk cache should not be called
        disk_cache.get_cached_result.assert_not_called()
    
    def test_disk_fallback(self):
        """Test fallback to disk cache"""
        memory_cache = Mock(spec=MemoryCache)
        disk_cache = Mock()
        
        hybrid = HybridCache(memory_cache=memory_cache, disk_cache=disk_cache)
        
        # Memory cache miss
        memory_cache.get.return_value = None
        
        # Disk cache has value
        file_cache = Mock()
        file_cache.nodes = {"node1": "data"}
        file_cache.edges = []
        file_cache.patterns = []
        file_cache.libraries = {}
        file_cache.infrastructure = {}
        file_cache.file_path = "test.py"
        file_cache.cached_at = time.time()
        
        disk_cache.get_cached_result.return_value = file_cache
        memory_cache.put.return_value = True
        
        result = hybrid.get("key1", "file")
        
        assert result is not None
        assert "nodes" in result
        
        # Should warm memory cache
        memory_cache.put.assert_called_once()
    
    def test_put_to_both_caches(self):
        """Test putting to both memory and disk cache"""
        memory_cache = Mock(spec=MemoryCache)
        disk_cache = Mock()
        policy = Mock(spec=CachePolicy)
        
        hybrid = HybridCache(
            memory_cache=memory_cache, 
            disk_cache=disk_cache,
            cache_policy=policy
        )
        
        # Setup mocks
        memory_cache._size_estimator = SizeEstimator()
        memory_cache.put.return_value = True
        policy.should_cache.return_value = True
        policy.get_ttl_days.return_value = 3.0
        
        # Put file data
        file_data = {
            'nodes': {"node1": "data"},
            'edges': [],
            'patterns': [],
            'libraries': {},
            'infrastructure': {}
        }
        
        result = hybrid.put("file:/test.py", file_data, "file")
        
        assert result is True
        memory_cache.put.assert_called_once()
        disk_cache.cache_file_result.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])