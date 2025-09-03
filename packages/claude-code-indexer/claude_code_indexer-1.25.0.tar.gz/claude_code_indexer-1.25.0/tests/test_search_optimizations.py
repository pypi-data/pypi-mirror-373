"""Test search optimizations including FTS5 and caching."""

import os
import sqlite3
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock

from claude_code_indexer.mcp_server import search_code, project_manager
from claude_code_indexer.indexer import CodeGraphIndexer
from claude_code_indexer.migrations import MigrationManager


class TestSearchOptimizations:
    """Test search performance optimizations."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def setup_test_db(self, temp_project_dir):
        """Set up test database with search optimizations."""
        # Create .claude-code-indexer directory
        indexer_dir = os.path.join(temp_project_dir, '.claude-code-indexer')
        os.makedirs(indexer_dir, exist_ok=True)
        
        db_path = os.path.join(indexer_dir, 'code_index.db')
        
        # Create initial database
        indexer = CodeGraphIndexer(db_path)
        
        # Add test data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create basic schema if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                summary TEXT,
                importance_score REAL DEFAULT 0.0,
                relevance_tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                language TEXT,
                line_number INTEGER,
                column_number INTEGER
            )
        """)
        
        # Insert test data
        test_nodes = [
            ('function', 'authenticate_user', '/auth/user.py', 'User authentication function', 0.9),
            ('class', 'UserManager', '/auth/manager.py', 'Manages user operations', 0.85),
            ('function', 'login_handler', '/auth/login.py', 'Handles user login requests', 0.8),
            ('function', 'connect_database', '/db/connection.py', 'Database connection handler', 0.75),
            ('class', 'DatabasePool', '/db/pool.py', 'Database connection pooling', 0.7),
        ]
        
        for node_data in test_nodes:
            cursor.execute("""
                INSERT INTO code_nodes (node_type, name, path, summary, importance_score)
                VALUES (?, ?, ?, ?, ?)
            """, node_data)
        
        conn.commit()
        
        # Run migration to add search optimizations
        migration_manager = MigrationManager(db_path)
        migration_manager.migrate('1.16.0')
        
        conn.close()
        
        return temp_project_dir, db_path
    
    def test_fts5_search_single_keyword(self, setup_test_db):
        """Test FTS5 search with single keyword."""
        project_dir, db_path = setup_test_db
        
        with patch('claude_code_indexer.mcp_server.project_manager') as mock_pm:
            mock_pm.storage.get_project_dir.return_value = os.path.dirname(db_path)
            mock_indexer = Mock()
            mock_indexer.cache_manager = Mock()
            mock_indexer.cache_manager.get_from_memory_cache.return_value = None
            mock_pm.get_indexer.return_value = mock_indexer
            
            # Test FTS5 search
            result = search_code(project_dir, "auth", use_fts=True)
            
            assert "authenticate_user" in result
            assert "UserManager" in result
            assert "login_handler" in result
            assert "[FTS5]" in result  # Indicates FTS5 was used
    
    def test_fts5_search_multiple_keywords_any(self, setup_test_db):
        """Test FTS5 search with multiple keywords (OR logic)."""
        project_dir, db_path = setup_test_db
        
        with patch('claude_code_indexer.mcp_server.project_manager') as mock_pm:
            mock_pm.storage.get_project_dir.return_value = os.path.dirname(db_path)
            mock_indexer = Mock()
            mock_indexer.cache_manager = Mock()
            mock_indexer.cache_manager.get_from_memory_cache.return_value = None
            mock_pm.get_indexer.return_value = mock_indexer
            
            # Test FTS5 search with OR logic
            result = search_code(project_dir, "user database", mode="any", use_fts=True)
            
            # Should find both user-related and database-related items
            assert "authenticate_user" in result
            assert "connect_database" in result
            assert "[FTS5]" in result
    
    def test_fts5_search_multiple_keywords_all(self, setup_test_db):
        """Test FTS5 search with multiple keywords (AND logic)."""
        project_dir, db_path = setup_test_db
        
        with patch('claude_code_indexer.mcp_server.project_manager') as mock_pm:
            mock_pm.storage.get_project_dir.return_value = os.path.dirname(db_path)
            mock_indexer = Mock()
            mock_indexer.cache_manager = Mock()
            mock_indexer.cache_manager.get_from_memory_cache.return_value = None
            mock_pm.get_indexer.return_value = mock_indexer
            
            # Test FTS5 search with AND logic
            result = search_code(project_dir, "user auth", mode="all", use_fts=True)
            
            # Should only find items containing both words
            assert "authenticate_user" in result
            assert "database" not in result  # Doesn't contain "user"
            assert "[FTS5]" in result
    
    def test_fallback_to_like_when_fts_disabled(self, setup_test_db):
        """Test fallback to LIKE queries when FTS is disabled."""
        project_dir, db_path = setup_test_db
        
        with patch('claude_code_indexer.mcp_server.project_manager') as mock_pm:
            mock_pm.storage.get_project_dir.return_value = os.path.dirname(db_path)
            mock_indexer = Mock()
            mock_indexer.cache_manager = Mock()
            mock_indexer.cache_manager.get_from_memory_cache.return_value = None
            mock_pm.get_indexer.return_value = mock_indexer
            
            # Test with FTS disabled
            result = search_code(project_dir, "auth", use_fts=False)
            
            assert "authenticate_user" in result
            assert "[FTS5]" not in result  # Should not use FTS5
    
    def test_search_result_caching(self, setup_test_db):
        """Test that search results are cached."""
        project_dir, db_path = setup_test_db
        
        with patch('claude_code_indexer.mcp_server.project_manager') as mock_pm:
            mock_pm.storage.get_project_dir.return_value = os.path.dirname(db_path)
            mock_indexer = Mock()
            mock_cache = Mock()
            mock_cache.get_from_memory_cache.return_value = None
            mock_indexer.cache_manager = mock_cache
            mock_pm.get_indexer.return_value = mock_indexer
            
            # First search - should cache result
            result1 = search_code(project_dir, "auth")
            
            # Verify cache was called to store result
            mock_cache.add_to_memory_cache.assert_called_once()
            cache_key = mock_cache.add_to_memory_cache.call_args[0][0]
            cached_value = mock_cache.add_to_memory_cache.call_args[0][1]
            
            # Second search - should return from cache
            mock_cache.get_from_memory_cache.return_value = cached_value
            result2 = search_code(project_dir, "auth")
            
            assert "(from cache)" in result2
    
    def test_indexes_exist(self, setup_test_db):
        """Test that search optimization indexes are created."""
        project_dir, db_path = setup_test_db
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check indexes
        cursor.execute("PRAGMA index_list(code_nodes)")
        indexes = {row[1] for row in cursor.fetchall()}
        
        assert 'idx_code_nodes_name' in indexes
        assert 'idx_code_nodes_importance_score' in indexes
        assert 'idx_code_nodes_search' in indexes
        
        conn.close()
    
    def test_fts5_triggers_work(self, setup_test_db):
        """Test that FTS5 triggers keep data in sync."""
        project_dir, db_path = setup_test_db
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert new node
        cursor.execute("""
            INSERT INTO code_nodes (node_type, name, path, summary, importance_score)
            VALUES (?, ?, ?, ?, ?)
        """, ('function', 'new_function', '/test/new.py', 'New test function', 0.5))
        
        conn.commit()
        
        # Check if it's in FTS5 table
        cursor.execute("SELECT * FROM code_nodes_fts WHERE code_nodes_fts MATCH 'new_function'")
        results = cursor.fetchall()
        assert len(results) == 1
        
        # Update the node
        cursor.execute("""
            UPDATE code_nodes SET name = 'updated_function' 
            WHERE name = 'new_function'
        """)
        conn.commit()
        
        # Check if FTS5 was updated
        cursor.execute("SELECT * FROM code_nodes_fts WHERE code_nodes_fts MATCH 'updated_function'")
        results = cursor.fetchall()
        assert len(results) == 1
        
        conn.close()
    
    def test_search_performance_comparison(self, setup_test_db):
        """Compare performance between FTS5 and LIKE queries."""
        project_dir, db_path = setup_test_db
        
        # Add more test data for performance testing
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert 1000 test nodes
        for i in range(1000):
            cursor.execute("""
                INSERT INTO code_nodes (node_type, name, path, summary, importance_score)
                VALUES (?, ?, ?, ?, ?)
            """, ('function', f'test_func_{i}', f'/test/file{i}.py', f'Test function {i}', 0.5))
        
        conn.commit()
        conn.close()
        
        import time
        
        with patch('claude_code_indexer.mcp_server.project_manager') as mock_pm:
            mock_pm.storage.get_project_dir.return_value = os.path.dirname(db_path)
            mock_indexer = Mock()
            mock_indexer.cache_manager = None  # Disable caching for performance test
            mock_pm.get_indexer.return_value = mock_indexer
            
            # Test FTS5 performance
            start_fts = time.time()
            result_fts = search_code(project_dir, "test", limit=50, use_fts=True)
            time_fts = time.time() - start_fts
            
            # Test LIKE performance
            start_like = time.time()
            result_like = search_code(project_dir, "test", limit=50, use_fts=False)
            time_like = time.time() - start_like
            
            # FTS5 should be faster
            print(f"FTS5 time: {time_fts:.4f}s, LIKE time: {time_like:.4f}s")
            # We don't assert timing as it can vary, but log for manual verification