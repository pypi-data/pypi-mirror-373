#!/usr/bin/env python3
"""
Database optimization for faster SQLite operations
"""

import sqlite3
import apsw  # More performant SQLite wrapper
from contextlib import contextmanager
from typing import Optional, Dict, Any
import threading
import time
from .logger import log_info


class OptimizedDatabase:
    """High-performance database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection_pool = {}
        self._pool_lock = threading.Lock()
        
    @contextmanager
    def get_connection(self):
        """Get optimized database connection with performance settings"""
        thread_id = threading.get_ident()
        
        with self._pool_lock:
            if thread_id not in self._connection_pool:
                try:
                    # Try APSW first (faster than sqlite3)
                    conn = apsw.Connection(self.db_path)
                    self._configure_apsw_connection(conn)
                    self._connection_pool[thread_id] = ('apsw', conn)
                except ImportError:
                    # Fallback to sqlite3 with optimizations
                    conn = sqlite3.connect(self.db_path, check_same_thread=False)
                    self._configure_sqlite3_connection(conn)
                    self._connection_pool[thread_id] = ('sqlite3', conn)
            
            db_type, conn = self._connection_pool[thread_id]
        
        try:
            yield conn
        finally:
            pass  # Keep connection in pool
    
    def _configure_apsw_connection(self, conn):
        """Configure APSW connection for maximum performance"""
        cursor = conn.cursor()
        
        # Performance optimizations
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety/speed
        cursor.execute("PRAGMA cache_size=10000")  # Larger cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory map
        cursor.execute("PRAGMA optimize")  # Auto-optimize
        
    def _configure_sqlite3_connection(self, conn):
        """Configure sqlite3 connection for better performance"""
        cursor = conn.cursor()
        
        # Performance optimizations
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL") 
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        
        conn.commit()
    
    def execute_batch(self, statements_and_params):
        """Execute multiple statements in a single transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN IMMEDIATE")
                
                for statement, params in statements_and_params:
                    if params:
                        cursor.execute(statement, params)
                    else:
                        cursor.execute(statement)
                
                cursor.execute("COMMIT")
                return True
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
    
    def close_all_connections(self):
        """Close all pooled connections"""
        with self._pool_lock:
            for db_type, conn in self._connection_pool.values():
                try:
                    conn.close()
                except:
                    pass
            self._connection_pool.clear()


class DatabaseBenchmark:
    """Benchmark database operations"""
    
    @staticmethod
    def benchmark_insert_performance(db_path: str, num_records: int = 1000):
        """Benchmark insert performance"""
        log_info(f"🔥 Benchmarking {num_records} records...")
        
        # Test standard sqlite3
        start_time = time.time()
        conn = sqlite3.connect(db_path + "_test_sqlite3")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER, data TEXT)")
        
        for i in range(num_records):
            cursor.execute("INSERT INTO test VALUES (?, ?)", (i, f"data_{i}"))
        
        conn.commit()
        conn.close()
        sqlite3_time = time.time() - start_time
        
        # Test optimized database
        start_time = time.time()
        opt_db = OptimizedDatabase(db_path + "_test_optimized")
        
        statements = []
        for i in range(num_records):
            statements.append(
                ("INSERT INTO test VALUES (?, ?)", (i, f"data_{i}"))
            )
        
        with opt_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER, data TEXT)")
            
        opt_db.execute_batch(statements)
        optimized_time = time.time() - start_time
        
        # Cleanup
        import os
        try:
            os.remove(db_path + "_test_sqlite3")
            os.remove(db_path + "_test_optimized")
        except:
            pass
        
        log_info(f"📊 SQLite3: {sqlite3_time:.2f}s")
        log_info(f"📊 Optimized: {optimized_time:.2f}s")
        log_info(f"🚀 Speedup: {sqlite3_time/optimized_time:.1f}x faster")
        
        return sqlite3_time, optimized_time


# Performance monitoring decorator
def time_it(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        log_info(f"⏱️  {func.__name__}: {end - start:.2f}s")
        return result
    return wrapper