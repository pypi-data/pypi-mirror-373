#!/usr/bin/env python3
"""
Integration tests for memory cache with existing functionality
Ensures backward compatibility and proper integration
"""

import pytest
import tempfile
import os
import time
from pathlib import Path

from claude_code_indexer.cache_manager import CacheManager, FileCache
from claude_code_indexer.indexer import CodeGraphIndexer


class TestMemoryCacheIntegration:
    """Test memory cache integration with existing components"""
    
    def test_cache_manager_backward_compatibility(self):
        """Test that CacheManager works with and without memory cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with memory cache disabled
            cache_no_mem = CacheManager(
                cache_dir=tmpdir,
                enable_memory_cache=False
            )
            
            # Should work as before
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, 'w') as f:
                f.write("print('hello')")
            
            # Cache some data
            cache_no_mem.cache_file_result(
                test_file,
                nodes={'node1': 'data'},
                edges=[],
                patterns=[],
                libraries={},
                infrastructure={}
            )
            
            # Retrieve should work
            result = cache_no_mem.get_cached_result(test_file)
            assert result is not None
            assert result.nodes == {'node1': 'data'}
            
            # Stats should work (no memory stats)
            stats = cache_no_mem.get_cache_stats()
            assert 'total_entries' in stats
            assert 'memory' not in stats
    
    def test_cache_manager_with_memory_cache(self):
        """Test CacheManager with memory cache enabled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with memory cache enabled
            cache_with_mem = CacheManager(
                cache_dir=tmpdir,
                enable_memory_cache=True,
                memory_cache_mb=10
            )
            
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, 'w') as f:
                f.write("print('hello')")
            
            # Cache some data
            cache_with_mem.cache_file_result(
                test_file,
                nodes={'node1': 'data'},
                edges=[],
                patterns=[],
                libraries={},
                infrastructure={}
            )
            
            # First retrieve should hit memory cache
            result1 = cache_with_mem.get_cached_result(test_file)
            assert result1 is not None
            assert result1.nodes == {'node1': 'data'}
            
            # Check stats show memory cache
            stats = cache_with_mem.get_cache_stats()
            assert 'memory' in stats
            assert 'disk' in stats
            assert stats['memory']['entry_count'] > 0
    
    def test_memory_cache_performance(self):
        """Test that memory cache improves performance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(
                cache_dir=tmpdir,
                enable_memory_cache=True,
                memory_cache_mb=10
            )
            
            # Create test file
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, 'w') as f:
                f.write("def test(): pass")
            
            # Cache data
            test_data = {
                'nodes': {str(i): f'node_{i}' for i in range(100)},
                'edges': [(str(i), str(i+1)) for i in range(99)],
                'patterns': ['pattern1', 'pattern2'],
                'libraries': {'lib1': 'v1', 'lib2': 'v2'},
                'infrastructure': {'db': 'postgres'}
            }
            
            cache.cache_file_result(
                test_file,
                **test_data
            )
            
            # Time disk-only access (simulate cold cache)
            cache.memory_cache.clear() if cache.memory_cache else None
            
            start = time.time()
            for _ in range(10):
                result = cache.get_cached_result(test_file)
            disk_time = time.time() - start
            
            # Time memory cache access (warm cache)
            # First access to warm the cache
            cache.get_cached_result(test_file)
            
            start = time.time()
            for _ in range(10):
                result = cache.get_cached_result(test_file)
            memory_time = time.time() - start
            
            # Memory cache should be faster
            # Allow some variance but expect significant improvement
            assert memory_time < disk_time * 0.5, f"Memory cache not faster: {memory_time:.3f}s vs {disk_time:.3f}s"
    
    def test_indexer_with_memory_cache(self):
        """Test that CodeGraphIndexer works with memory cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test Python file
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, 'w') as f:
                f.write("""
def hello():
    return "world"

class TestClass:
    def method(self):
        return hello()
""")
            
            # Index with cache
            db_path = os.path.join(tmpdir, "test.db")
            indexer = CodeGraphIndexer(
                db_path=db_path,
                use_cache=True,
                project_path=Path(tmpdir)
            )
            
            # First indexing
            indexer.index_directory(tmpdir)
            
            # Check cache manager has memory cache
            assert indexer.cache_manager.enable_memory_cache
            assert indexer.cache_manager.memory_cache is not None
            
            # Check stats
            stats = indexer.cache_manager.get_cache_stats()
            assert 'memory' in stats
            assert stats['disk']['total_entries'] > 0
            
            # Second indexing should use cache
            start = time.time()
            indexer.index_directory(tmpdir)
            cached_time = time.time() - start
            
            # Should be very fast due to cache
            assert cached_time < 0.5  # Should complete in under 0.5s
    
    def test_cache_expiration_and_eviction(self):
        """Test TTL expiration and LRU eviction"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Small memory cache to test eviction
            cache = CacheManager(
                cache_dir=tmpdir,
                enable_memory_cache=True,
                memory_cache_mb=1  # Very small
            )
            
            # Create multiple files with large data to force eviction
            for i in range(20):
                test_file = os.path.join(tmpdir, f"test{i}.py")
                with open(test_file, 'w') as f:
                    f.write(f"# File {i}\n" * 1000)  # Make it sizeable
                
                # Cache with large node data to consume memory
                large_nodes = {f'node{j}': f'data{j}' * 1000 for j in range(100)}
                
                cache.cache_file_result(
                    test_file,
                    nodes=large_nodes,
                    edges=[],
                    patterns=[],
                    libraries={},
                    infrastructure={}
                )
            
            # Check eviction occurred due to size limit
            stats = cache.memory_cache.get_stats()
            # Should have evictions or be at size limit
            assert stats['evictions'] > 0 or stats['size_mb'] >= 0.9
            assert stats['size_mb'] <= 1.1  # Allow small overhead
    
    def test_cache_stats_api_compatibility(self):
        """Test that cache stats API remains compatible"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Old style usage should still work
            cache = CacheManager(cache_dir=tmpdir)
            
            # get_cache_stats should work
            stats = cache.get_cache_stats()
            
            # For new cache, returns nested structure
            if cache.enable_memory_cache:
                assert 'memory' in stats
                assert 'disk' in stats
            else:
                # For old cache, returns flat structure
                assert 'total_entries' in stats
                assert 'cache_dir' in stats
            
            # print_cache_stats should work without errors
            cache.print_cache_stats()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])