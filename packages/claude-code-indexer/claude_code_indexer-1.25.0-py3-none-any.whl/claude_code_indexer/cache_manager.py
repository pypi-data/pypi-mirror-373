#!/usr/bin/env python3
"""
Caching system for faster re-indexing with integrated memory cache
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
# import pickle  # Removed for security - using JSON instead
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from .logger import log_info
from .memory_cache import MemoryCache, CachePolicy
from .cache_utils import CacheKeyGenerator


@dataclass
class FileCache:
    """Cache entry for a single file"""
    file_path: str
    file_hash: str
    last_modified: float
    file_size: int
    nodes: Dict
    edges: List
    patterns: List
    libraries: Dict
    infrastructure: Dict
    cached_at: float


class CacheManager:
    """Manage file-level caching with integrated memory cache for faster re-indexing"""
    
    def __init__(self, project_path: Optional[Path] = None, cache_dir: Optional[str] = None,
                 enable_memory_cache: bool = True, memory_cache_mb: int = 100):
        # Use centralized storage manager
        from .storage_manager import get_storage_manager
        storage = get_storage_manager()
        
        if project_path:
            # Use project-specific cache directory
            self.cache_dir = storage.get_cache_dir(project_path)
        elif cache_dir:
            # Use provided cache directory (for backward compatibility)
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(exist_ok=True, parents=True)
        else:
            # Default to current project
            project_path = storage.get_project_from_cwd()
            self.cache_dir = storage.get_cache_dir(project_path)
        
        self.cache_db = self.cache_dir / "file_cache.db"
        self._init_cache_db()
        
        # Initialize memory cache if enabled
        self.enable_memory_cache = enable_memory_cache
        if enable_memory_cache:
            self.memory_cache = MemoryCache(
                max_size_mb=memory_cache_mb,
                default_ttl_days=3.0,
                access_ttl_days=3.0,
                cleanup_interval_seconds=300
            )
            self.cache_policy = CachePolicy()
        else:
            self.memory_cache = None
            self.cache_policy = None
    
    def _init_cache_db(self):
        """Initialize cache database"""
        conn = sqlite3.connect(str(self.cache_db))
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_cache (
            file_path TEXT PRIMARY KEY,
            file_hash TEXT NOT NULL,
            last_modified REAL NOT NULL,
            file_size INTEGER NOT NULL,
            cached_at REAL NOT NULL,
            cache_data BLOB NOT NULL
        )
        ''')
        
        # Index for faster lookups
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_file_hash 
        ON file_cache(file_hash)
        ''')
        
        conn.commit()
        conn.close()
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate fast hash of file content"""
        try:
            stat = os.stat(file_path)
            # Use file size + mtime for fast check
            content_hint = f"{stat.st_size}_{stat.st_mtime}_{file_path}"
            
            # For small files, hash content directly
            if stat.st_size < 10000:  # 10KB
                with open(file_path, 'rb') as f:
                    content = f.read()
                return hashlib.md5(content).hexdigest()
            else:
                # For large files, hash first/last chunks + size + mtime
                with open(file_path, 'rb') as f:
                    start_chunk = f.read(1024)
                    f.seek(-1024, 2) if stat.st_size > 1024 else f.seek(0)
                    end_chunk = f.read(1024)
                
                combined = start_chunk + end_chunk + content_hint.encode()
                return hashlib.md5(combined).hexdigest()
                
        except (OSError, IOError):
            return ""
    
    def is_file_cached(self, file_path: str) -> bool:
        """Check if file is cached and up-to-date (memory or disk)"""
        # Check memory cache first if enabled
        if self.enable_memory_cache and self.memory_cache:
            cache_key = CacheKeyGenerator.file_key(file_path)
            if self.memory_cache.get(cache_key) is not None:
                return True
        
        # Check disk cache
        try:
            stat = os.stat(file_path)
            current_hash = self.get_file_hash(file_path)
            
            conn = sqlite3.connect(str(self.cache_db))
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT file_hash, last_modified FROM file_cache WHERE file_path = ?",
                (file_path,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                cached_hash, cached_mtime = result
                return (cached_hash == current_hash and 
                       abs(cached_mtime - stat.st_mtime) < 1.0)
            
            return False
            
        except (OSError, sqlite3.Error):
            return False
    
    def get_cached_result(self, file_path: str) -> Optional[FileCache]:
        """Get cached processing result for file (memory first, then disk)"""
        # Try memory cache first if enabled
        if self.enable_memory_cache and self.memory_cache:
            cache_key = CacheKeyGenerator.file_key(file_path)
            memory_result = self.memory_cache.get(cache_key)
            if memory_result:
                # Convert dict back to FileCache if needed
                if isinstance(memory_result, dict):
                    return FileCache(**memory_result)
                return memory_result
        
        # Fall back to disk cache
        if not self.is_file_cached(file_path):
            return None
        
        try:
            conn = sqlite3.connect(str(self.cache_db))
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT cache_data FROM file_cache WHERE file_path = ?",
                (file_path,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                cache_data = json.loads(result[0])
                file_cache = FileCache(**cache_data)
                
                # Warm memory cache with disk data
                if self.enable_memory_cache and self.memory_cache:
                    cache_key = CacheKeyGenerator.file_key(file_path)
                    self.memory_cache.put(
                        cache_key, 
                        asdict(file_cache),
                        entity_type="file"
                    )
                
                return file_cache
            
            return None
            
        except (sqlite3.Error, json.JSONDecodeError):
            return None
    
    def cache_file_result(self, file_path: str, nodes: Dict, edges: List, 
                         patterns: List, libraries: Dict, infrastructure: Dict):
        """Cache processing result for file (both memory and disk)"""
        try:
            stat = os.stat(file_path)
            file_hash = self.get_file_hash(file_path)
            
            cache_entry = FileCache(
                file_path=file_path,
                file_hash=file_hash,
                last_modified=stat.st_mtime,
                file_size=stat.st_size,
                nodes=nodes,
                edges=edges,
                patterns=patterns,
                libraries=libraries,
                infrastructure=infrastructure,
                cached_at=time.time()
            )
            
            # Custom JSON encoder to handle sets
            cache_dict = asdict(cache_entry)
            # Convert any sets to lists for JSON serialization
            def convert_sets(obj):
                if isinstance(obj, set):
                    return list(obj)
                elif isinstance(obj, dict):
                    return {k: convert_sets(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_sets(v) for v in obj]
                return obj
            
            cache_dict = convert_sets(cache_dict)
            
            # Cache in memory if enabled
            if self.enable_memory_cache and self.memory_cache:
                cache_key = CacheKeyGenerator.file_key(file_path)
                self.memory_cache.put(
                    cache_key,
                    cache_dict,
                    entity_type="file"
                )
            
            # Also cache to disk for persistence
            cache_data = json.dumps(cache_dict).encode('utf-8')
            
            conn = sqlite3.connect(str(self.cache_db))
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO file_cache 
            (file_path, file_hash, last_modified, file_size, cached_at, cache_data)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                file_path, file_hash, stat.st_mtime, stat.st_size,
                cache_entry.cached_at, cache_data
            ))
            
            conn.commit()
            conn.close()
            
        except (OSError, sqlite3.Error, json.JSONDecodeError, ValueError):
            pass  # Silent fail for caching
    
    def clear_cache(self, older_than_days: int = 30):
        """Clear old cache entries"""
        cutoff_time = time.time() - (older_than_days * 24 * 3600)
        
        try:
            conn = sqlite3.connect(str(self.cache_db))
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM file_cache WHERE cached_at < ?",
                (cutoff_time,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            log_info(f"🗑️  Cleared {deleted_count} old cache entries")
            
        except sqlite3.Error:
            pass
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics including memory cache"""
        disk_stats = {}
        try:
            conn = sqlite3.connect(str(self.cache_db))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM file_cache")
            total_entries = cursor.fetchone()[0]
            
            cursor.execute(
                "SELECT COUNT(*) FROM file_cache WHERE cached_at > ?",
                (time.time() - 24 * 3600,)  # Last 24 hours
            )
            recent_entries = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(file_size) FROM file_cache")
            total_size = cursor.fetchone()[0] or 0
            
            conn.close()
            
            cache_db_size = self.cache_db.stat().st_size
            
            disk_stats = {
                'total_entries': total_entries,
                'recent_entries': recent_entries,
                'total_file_size': total_size,
                'cache_db_size': cache_db_size,
                'cache_dir': str(self.cache_dir)
            }
            
        except (sqlite3.Error, OSError):
            disk_stats = {
                'total_entries': 0,
                'recent_entries': 0,
                'total_file_size': 0,
                'cache_db_size': 0,
                'cache_dir': str(self.cache_dir)
            }
        
        # Include memory cache stats if enabled
        if self.enable_memory_cache and self.memory_cache:
            memory_stats = self.memory_cache.get_stats()
            return {
                'disk': disk_stats,
                'memory': memory_stats,
                'combined': {
                    'total_entries': disk_stats['total_entries'],
                    'memory_hit_rate': memory_stats['hit_rate'],
                    'memory_size_mb': memory_stats['size_mb'],
                    'cache_dir': str(self.cache_dir)
                }
            }
        else:
            return disk_stats
    
    def print_cache_stats(self):
        """Print cache statistics"""
        stats = self.get_cache_stats()
        
        if isinstance(stats, dict) and 'disk' in stats:
            # We have both memory and disk stats
            log_info(f"💾 Cache Statistics:")
            log_info(f"   Memory Cache:")
            log_info(f"     Hit rate: {stats['memory']['hit_rate']:.1f}%")
            log_info(f"     Size: {stats['memory']['size_mb']:.1f} MB / {stats['memory']['max_size_mb']} MB")
            log_info(f"     Entries: {stats['memory']['entry_count']}")
            log_info(f"   Disk Cache:")
            log_info(f"     Total entries: {stats['disk']['total_entries']}")
            log_info(f"     Recent (24h): {stats['disk']['recent_entries']}")
            log_info(f"     Total file size: {stats['disk']['total_file_size'] / 1024 / 1024:.1f} MB")
            log_info(f"     Cache DB size: {stats['disk']['cache_db_size'] / 1024:.1f} KB")
            log_info(f"   Cache location: {stats['disk']['cache_dir']}")
        else:
            # Only disk stats (backward compatibility)
            log_info(f"💾 Cache Statistics:")
            log_info(f"   Total entries: {stats['total_entries']}")
            log_info(f"   Recent (24h): {stats['recent_entries']}")
            log_info(f"   Total file size: {stats['total_file_size'] / 1024 / 1024:.1f} MB")
            log_info(f"   Cache DB size: {stats['cache_db_size'] / 1024:.1f} KB")
            log_info(f"   Cache location: {stats['cache_dir']}")


class IncrementalIndexer:
    """Incremental indexing using cache"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        
    def get_files_to_process(self, file_paths: List[str]) -> Tuple[List[str], List[str]]:
        """Split files into cached and needs-processing"""
        cached_files = []
        process_files = []
        
        # Use threading for faster cache checks
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.cache.is_file_cached, fp): fp 
                for fp in file_paths
            }
            
            for future in futures:
                file_path = futures[future]
                try:
                    is_cached = future.result()
                    if is_cached:
                        cached_files.append(file_path)
                    else:
                        process_files.append(file_path)
                except:
                    process_files.append(file_path)  # Process if cache check fails
        
        return cached_files, process_files
    
    def load_cached_results(self, cached_files: List[str]) -> List[FileCache]:
        """Load results from cache for multiple files"""
        results = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.cache.get_cached_result, fp): fp
                for fp in cached_files
            }
            
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except:
                    pass  # Skip failed cache loads
        
        return results