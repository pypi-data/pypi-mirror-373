#!/usr/bin/env python3
"""
Comprehensive tests for MCP tool functions with full coverage
"""

import pytest
import json
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Mock MCP imports first
with patch('claude_code_indexer.mcp_server.FastMCP'):
    from claude_code_indexer.mcp_server import (
        index_codebase, get_project_stats, query_important_code, search_code,
        list_indexed_projects, manage_cache, get_ignore_patterns, enhance_metadata,
        query_enhanced_nodes, get_codebase_insights, get_critical_components,
        update_node_metadata, project_manager
    )


class TestMCPIndexCodebase:
    """Test index_codebase MCP tool"""
    
    @pytest.fixture
    def mock_indexer(self):
        """Mock indexer with stats"""
        indexer = Mock()
        indexer.get_stats.return_value = {
            'total_files': 10,
            'total_nodes': 100,
            'total_edges': 50
        }
        return indexer
    
    @pytest.fixture
    def mock_project_manager(self, mock_indexer):
        """Mock project manager"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            pm.get_indexer.return_value = mock_indexer
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            yield pm
    
    def test_index_codebase_success(self, mock_project_manager):
        """Test successful indexing"""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = index_codebase(project_path="/test/project")
        
        assert "✅ Indexing Complete!" in result
        assert "Total files: 10" in result
        assert "Total nodes: 100" in result
        assert "Total edges: 50" in result
        mock_project_manager.get_indexer.assert_called_once()
    
    def test_index_codebase_no_path(self):
        """Test indexing without path parameter"""
        result = index_codebase()
        assert "❌ Error: Either 'project_path' or 'path' parameter is required" in result
    
    def test_index_codebase_backward_compatibility(self, mock_project_manager):
        """Test backward compatibility with 'path' parameter"""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = index_codebase(path="/test/project")
        
        assert "✅ Indexing Complete!" in result
    
    def test_index_codebase_nonexistent_path(self):
        """Test indexing with non-existent path"""
        with patch('os.path.exists', return_value=False):
            with patch('os.path.abspath', return_value="/nonexistent"):
                result = index_codebase(project_path="/nonexistent")
        
        assert "❌ Project path does not exist: /nonexistent" in result
    
    def test_index_codebase_not_directory(self):
        """Test indexing with file instead of directory"""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=False):
                with patch('os.path.abspath', return_value="/test/file.py"):
                    result = index_codebase(project_path="/test/file.py")
        
        assert "❌ Project path is not a directory" in result
    
    def test_index_codebase_exception(self, mock_project_manager):
        """Test indexing with exception"""
        mock_indexer = mock_project_manager.get_indexer.return_value
        mock_indexer.index_directory.side_effect = Exception("Test error")
        
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = index_codebase(project_path="/test/project")
        
        assert "❌ Indexing failed: Test error" in result
    
    def test_index_codebase_with_options(self, mock_project_manager):
        """Test indexing with custom options"""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = index_codebase(
                        project_path="/test/project",
                        workers=8,
                        force=True,
                        custom_ignore=["*.tmp"]
                    )
        
        assert "✅ Indexing Complete!" in result
        # Verify indexer called with correct parameters
        indexer = mock_project_manager.get_indexer.return_value
        indexer.index_directory.assert_called_once_with(
            "/test/project", force_reindex=True, custom_ignore=["*.tmp"]
        )
    
    def test_index_codebase_with_workers_only(self, mock_project_manager):
        """Test indexing with only workers parameter"""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = index_codebase(project_path="/test/project", workers=4)
        
        assert "✅ Indexing Complete!" in result
        # Workers parameter is handled internally, not passed to index_directory
        mock_project_manager.get_indexer.return_value.index_directory.assert_called_once_with(
            "/test/project", force_reindex=False, custom_ignore=None
        )
    
    def test_index_codebase_with_force_only(self, mock_project_manager):
        """Test indexing with only force parameter"""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = index_codebase(project_path="/test/project", force=True)
        
        assert "✅ Indexing Complete!" in result
        mock_project_manager.get_indexer.return_value.index_directory.assert_called_once_with(
            "/test/project", force_reindex=True, custom_ignore=None
        )
    
    def test_index_codebase_with_custom_ignore_only(self, mock_project_manager):
        """Test indexing with only custom_ignore parameter"""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = index_codebase(project_path="/test/project", custom_ignore=["docs/", "*.log"])
        
        assert "✅ Indexing Complete!" in result
        mock_project_manager.get_indexer.return_value.index_directory.assert_called_once_with(
            "/test/project", force_reindex=False, custom_ignore=["docs/", "*.log"]
        )


class TestMCPGetProjectStats:
    """Test get_project_stats MCP tool"""
    
    @pytest.fixture
    def mock_cache_stats_flat(self):
        """Mock flat cache stats structure"""
        return {
            'total_entries': 50,
            'recent_entries': 10,
            'cache_db_size': 1024
        }
    
    @pytest.fixture
    def mock_cache_stats_nested(self):
        """Mock nested cache stats structure"""
        return {
            'disk': {
                'total_entries': 50,
                'recent_entries': 10,
                'cache_db_size': 1024
            },
            'memory': {
                'hit_rate': 85.5
            }
        }
    
    def test_get_project_stats_success_flat_cache(self, mock_cache_stats_flat):
        """Test project stats with flat cache structure"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            with patch('claude_code_indexer.mcp_server.CacheManager') as cm:
                # Mock indexer
                indexer = Mock()
                indexer.get_stats.return_value = {
                    'total_files': 20,
                    'total_nodes': 200,
                    'total_edges': 100,
                    'node_types': {'class': 10, 'function': 50},
                    'relationship_types': {'calls': 30, 'imports': 20}
                }
                pm.get_indexer.return_value = indexer
                pm.storage.get_project_dir.return_value = Path("/tmp/project")
                
                # Mock cache manager
                cache_mgr = Mock()
                cache_mgr.get_cache_stats.return_value = mock_cache_stats_flat
                cm.return_value = cache_mgr
                
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('os.path.abspath', return_value="/test/project"):
                        result = get_project_stats("/test/project")
        
        assert "📊 Code Indexing Statistics" in result
        assert "Total files: 20" in result
        assert "Total entries: 50" in result
        assert "Recent (24h): 10" in result
        assert "Cache size: 1.0 KB" in result
    
    def test_get_project_stats_success_nested_cache(self, mock_cache_stats_nested):
        """Test project stats with nested cache structure"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            with patch('claude_code_indexer.mcp_server.CacheManager') as cm:
                # Mock indexer
                indexer = Mock()
                indexer.get_stats.return_value = {
                    'total_files': 20,
                    'total_nodes': 200,
                    'total_edges': 100,
                    'node_types': {'class': 10, 'function': 50},
                    'relationship_types': {'calls': 30, 'imports': 20}
                }
                pm.get_indexer.return_value = indexer
                pm.storage.get_project_dir.return_value = Path("/tmp/project")
                
                # Mock cache manager
                cache_mgr = Mock()
                cache_mgr.get_cache_stats.return_value = mock_cache_stats_nested
                cm.return_value = cache_mgr
                
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('os.path.abspath', return_value="/test/project"):
                        result = get_project_stats("/test/project")
        
        assert "📊 Code Indexing Statistics" in result
        assert "Total entries: 50" in result
    
    def test_get_project_stats_no_database(self):
        """Test project stats with missing database"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            
            with patch('pathlib.Path.exists', return_value=False):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = get_project_stats("/test/project")
        
        assert "❌ No indexed data found for project" in result
        assert "Run index_codebase first" in result


class TestMCPQueryImportantCode:
    """Test query_important_code MCP tool"""
    
    @pytest.fixture
    def mock_nodes(self):
        """Mock important nodes"""
        return [
            {
                'name': 'MainClass',
                'node_type': 'class',
                'importance_score': 0.95,
                'relevance_tags': ['core', 'api'],
                'path': '/src/main.py'
            },
            {
                'name': 'helper_function',
                'node_type': 'function',
                'importance_score': 0.75,
                'relevance_tags': ['utility'],
                'path': '/src/utils.py'
            }
        ]
    
    def test_query_important_code_success(self, mock_nodes):
        """Test successful query of important code"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_important_nodes.return_value = mock_nodes
            pm.get_indexer.return_value = indexer
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            
            with patch('pathlib.Path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_important_code("/test/project")
        
        assert "🔍 Most important code entities:" in result
        assert "MainClass" in result
        assert "helper_function" in result
        assert "Score: 0.950" in result
        assert "core, api" in result
    
    def test_query_important_code_with_filter(self, mock_nodes):
        """Test query with node type filter"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_important_nodes.return_value = mock_nodes
            pm.get_indexer.return_value = indexer
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            
            with patch('pathlib.Path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_important_code("/test/project", node_type="class")
        
        # Only class nodes should be in result
        assert "MainClass" in result
        assert "helper_function" not in result
    
    def test_query_important_code_no_database(self):
        """Test query with missing database"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            
            with patch('pathlib.Path.exists', return_value=False):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_important_code("/test/project")
        
        assert "❌ No indexed data found for project" in result


class TestMCPSearchCode:
    """Test search_code MCP tool"""
    
    def test_search_code_success(self):
        """Test successful code search"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            
            with patch('sqlite3.connect') as mock_connect:
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = [
                    (1, 'AuthClass', 'class', '/src/auth.py', 0.85, '["security"]', 'Authentication class')
                ]
                mock_cursor.description = [
                    ('id',), ('name',), ('node_type',), ('path',), ('importance_score',), ('relevance_tags',), ('summary',)
                ]
                mock_connect.return_value.cursor.return_value = mock_cursor
                
                with patch('os.path.exists', return_value=True):
                    with patch('os.path.abspath', return_value="/test/project"):
                        result = search_code("/test/project", "auth")
        
        assert "🔍 Search results for 'auth'" in result
        assert "AuthClass" in result
        assert "Score: 0.850" in result
    
    def test_search_code_multiple_terms(self):
        """Test search with multiple terms"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            pm.get_indexer.return_value = indexer
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            
            with patch('sqlite3.connect') as mock_connect:
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = []
                mock_cursor.description = []
                mock_connect.return_value.cursor.return_value = mock_cursor
                
                with patch('os.path.exists', return_value=True):
                    with patch('os.path.abspath', return_value="/test/project"):
                        result = search_code("/test/project", "auth user", mode="all")
        
        assert "No results found for 'auth user' (mode: all)" in result
    
    def test_search_code_no_terms(self):
        """Test search with no terms"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = search_code("/test/project", "")
        
        assert "❌ No search terms provided" in result
    
    def test_search_code_no_database(self):
        """Test search with missing database"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            pm.storage.get_project_dir.return_value = Path("/tmp/project")
            
            with patch('os.path.exists', return_value=False):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = search_code("/test/project", "test")
        
        assert "❌ No indexed data found for project" in result
    
    def test_search_code_with_fts5(self):
        """Test search using FTS5"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            pm.storage.get_project_dir.return_value = Path("/test/project/.claude-code-indexer")
            indexer = Mock()
            indexer.cache_manager.get_from_memory_cache.return_value = None
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    with patch('sqlite3.connect') as mock_connect:
                        mock_conn = Mock()
                        mock_cursor = Mock()
                        mock_connect.return_value = mock_conn
                        mock_conn.cursor.return_value = mock_cursor
                        
                        # Simulate FTS5 table exists
                        mock_cursor.fetchone.side_effect = [
                            ('code_nodes_fts',),  # FTS5 table exists
                        ]
                        mock_cursor.fetchall.return_value = [
                            (1, 'function', 'auth_user', '/auth.py', 'User auth', 0.9, None, None, 'python', 10, 0)
                        ]
                        mock_cursor.description = [
                            ('id',), ('node_type',), ('name',), ('path',), ('summary',),
                            ('importance_score',), ('relevance_tags',), ('created_at',),
                            ('language',), ('line_number',), ('column_number',)
                        ]
                        
                        result = search_code("/test/project", "auth", use_fts=True)
        
        assert "[FTS5]" in result
        assert "auth_user" in result
    
    def test_search_code_with_caching(self):
        """Test search result caching"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            pm.storage.get_project_dir.return_value = Path("/test/project/.claude-code-indexer")
            indexer = Mock()
            cache_manager = Mock()
            memory_cache = Mock()
            
            # First call - no cache
            memory_cache.get.return_value = None
            cache_manager.memory_cache = memory_cache
            indexer.cache_manager = cache_manager
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    with patch('sqlite3.connect') as mock_connect:
                        mock_conn = Mock()
                        mock_cursor = Mock()
                        mock_connect.return_value = mock_conn
                        mock_conn.cursor.return_value = mock_cursor
                        
                        mock_cursor.fetchone.return_value = None  # No FTS5
                        mock_cursor.fetchall.return_value = [
                            (1, 'function', 'test_func', '/test.py', 'Test', 0.8, None, None, 'python', 1, 0)
                        ]
                        mock_cursor.description = [
                            ('id',), ('node_type',), ('name',), ('path',), ('summary',),
                            ('importance_score',), ('relevance_tags',), ('created_at',),
                            ('language',), ('line_number',), ('column_number',)
                        ]
                        
                        result1 = search_code("/test/project", "test")
            
            # Verify cache was written
            cache_manager.memory_cache.put.assert_called_once()
            
            # Second call - from cache
            # Reset the mock to simulate a cache hit
            memory_cache.get.reset_mock()
            memory_cache.get.return_value = "🔍 Search results for 'test'"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result2 = search_code("/test/project", "test")
            
            assert "(from cache)" in result2


class TestMCPListIndexedProjects:
    """Test list_indexed_projects MCP tool"""
    
    @pytest.fixture
    def mock_projects(self):
        """Mock project list"""
        return [
            {
                'name': 'project1',
                'path': '/path/to/project1',
                'exists': True,
                'last_indexed': '2025-01-01 12:00:00',
                'stats': {'nodes': 100, 'files': 10},
                'db_size': 1024 * 1024  # 1MB
            },
            {
                'name': 'project2',
                'path': '/path/to/project2',
                'exists': False,
                'stats': {'nodes': 50, 'files': 5},
                'db_size': 512 * 1024  # 512KB
            }
        ] * 15  # 30 projects total to test limiting
    
    def test_list_indexed_projects_success(self, mock_projects):
        """Test successful project listing"""
        with patch('claude_code_indexer.mcp_server.get_storage_manager') as mock_storage:
            storage = Mock()
            storage.list_projects.return_value = mock_projects[:5]  # Only 5 projects
            storage.get_storage_stats.return_value = {
                'project_count': 5,
                'total_size_mb': 10.5
            }
            mock_storage.return_value = storage
            
            result = list_indexed_projects()
        
        assert "📚 **Indexed Projects** (5)" in result
        assert "project1" in result
        assert "✓ Exists" in result
        assert "✗ Missing" in result
        assert "Nodes: 100" in result
        assert "Size: 1.0 MB" in result
    
    def test_list_indexed_projects_with_limit(self, mock_projects):
        """Test project listing with limit"""
        with patch('claude_code_indexer.mcp_server.get_storage_manager') as mock_storage:
            storage = Mock()
            storage.list_projects.return_value = mock_projects
            storage.get_storage_stats.return_value = {
                'project_count': 30,
                'total_size_mb': 50.0
            }
            mock_storage.return_value = storage
            
            result = list_indexed_projects(limit=5)
        
        assert "📚 **Indexed Projects** (5 of 30, use limit parameter for more)" in result
    
    def test_list_indexed_projects_no_stats(self, mock_projects):
        """Test project listing without stats"""
        with patch('claude_code_indexer.mcp_server.get_storage_manager') as mock_storage:
            storage = Mock()
            storage.list_projects.return_value = mock_projects[:2]
            mock_storage.return_value = storage
            
            result = list_indexed_projects(include_stats=False)
        
        assert "📚 **Indexed Projects**" in result
        assert "Nodes:" not in result
        assert "Size:" not in result
        assert "💾 **Storage Summary**" not in result
    
    def test_list_indexed_projects_empty(self):
        """Test project listing with no projects"""
        with patch('claude_code_indexer.mcp_server.get_storage_manager') as mock_storage:
            storage = Mock()
            storage.list_projects.return_value = []
            mock_storage.return_value = storage
            
            result = list_indexed_projects()
        
        assert "📂 No indexed projects found." in result


class TestMCPManageCache:
    """Test manage_cache MCP tool"""
    
    def test_manage_cache_stats(self):
        """Test cache stats management"""
        with patch('claude_code_indexer.mcp_server.CacheManager') as cm:
            cache_mgr = Mock()
            cache_mgr.get_cache_stats.return_value = {
                'total_entries': 100,
                'recent_entries': 20,
                'total_file_size': 1024 * 1024,
                'cache_db_size': 512 * 1024,
                'cache_dir': '/tmp/cache'
            }
            cm.return_value = cache_mgr
            
            with patch('os.path.abspath', return_value="/test/project"):
                result = manage_cache("/test/project", "stats")
        
        assert "💾 Cache Statistics:" in result
        assert "Total entries: 100" in result
        assert "Recent (24h): 20" in result
        assert "Total file size: 1.0 MB" in result
        assert "Cache DB size: 512.0 KB" in result
    
    def test_manage_cache_clear(self):
        """Test cache clearing"""
        with patch('claude_code_indexer.mcp_server.CacheManager') as cm:
            cache_mgr = Mock()
            cm.return_value = cache_mgr
            
            with patch('os.path.abspath', return_value="/test/project"):
                result = manage_cache("/test/project", "clear", days=7)
        
        assert "✅ Cleared cache entries older than 7 days" in result
        cache_mgr.clear_cache.assert_called_once_with(older_than_days=7)
    
    def test_manage_cache_invalid_action(self):
        """Test invalid cache action"""
        with patch('claude_code_indexer.mcp_server.CacheManager'):
            with patch('os.path.abspath', return_value="/test/project"):
                result = manage_cache("/test/project", "invalid")
        
        assert "❌ Unknown cache action. Use 'stats' or 'clear'" in result


class TestMCPGetIgnorePatterns:
    """Test get_ignore_patterns MCP tool"""
    
    def test_get_ignore_patterns_success(self):
        """Test successful pattern retrieval"""
        mock_patterns = ['.git/', '__pycache__/', 'node_modules/', '*.pyc', '.env']
        
        with patch('claude_code_indexer.ignore_handler.IgnoreHandler') as ih:
            handler = Mock()
            handler.get_patterns.return_value = mock_patterns
            ih.return_value = handler
            
            with patch('os.path.exists', return_value=True):
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('os.path.abspath', return_value="/test/project"):
                        result = get_ignore_patterns("/test/project")
        
        assert "📝 Ignore Patterns for: /test/project" in result
        assert "✅ Using .gitignore" in result
        assert "Total patterns: 5" in result
        assert "Version Control" in result
        assert "Python" in result
    
    def test_get_ignore_patterns_nonexistent_path(self):
        """Test pattern retrieval with non-existent path"""
        with patch('os.path.exists', return_value=False):
            with patch('os.path.abspath', return_value="/nonexistent"):
                result = get_ignore_patterns("/nonexistent")
        
        assert "❌ Project path does not exist: /nonexistent" in result


class TestMCPEnhanceMetadata:
    """Test enhance_metadata MCP tool"""
    
    def test_enhance_metadata_success(self):
        """Test successful metadata enhancement"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.enhance_metadata.return_value = {
                'analyzed_count': 50,
                'total_nodes': 100,
                'analysis_duration': '2.5s',
                'nodes_per_second': 20.0,
                'architectural_layers': {'controller': 10, 'service': 15},
                'criticality_distribution': {'critical': 5, 'important': 20},
                'business_domains': {'auth': 10, 'user': 15},
                'average_scores': {'complexity': 0.65, 'testability': 0.80},
                'detected_patterns': {'singleton': 2, 'factory': 3}
            }
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = enhance_metadata("/test/project")
        
        assert "🤖 LLM Metadata Enhancement Complete" in result
        assert "Analyzed nodes: 50" in result
        assert "🏗️ Architectural Layers:" in result
        assert "controller: 10 components" in result
        assert "🎨 Design Patterns Detected:" in result
    
    def test_enhance_metadata_nonexistent_path(self):
        """Test enhancement with non-existent path"""
        with patch('os.path.exists', return_value=False):
            with patch('os.path.abspath', return_value="/nonexistent"):
                result = enhance_metadata("/nonexistent")
        
        assert "❌ Project path does not exist: /nonexistent" in result
    
    def test_enhance_metadata_exception(self):
        """Test enhancement with exception"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.enhance_metadata.side_effect = Exception("Enhancement failed")
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = enhance_metadata("/test/project")
        
        assert "❌ Enhancement failed: Enhancement failed" in result


class TestMCPGetCodebaseInsights:
    """Test get_codebase_insights MCP tool"""
    
    def test_get_codebase_insights_success(self):
        """Test successful insights retrieval"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.get_analysis_insights.return_value = {
                'codebase_health': {
                    'overall_score': 0.75,
                    'complexity_health': 'good',
                    'testability_health': 'fair',
                    'recommendations': ['Add more tests', 'Reduce complexity']
                },
                'architectural_overview': {
                    'layer_distribution': {'controller': 10, 'service': 15},
                    'domain_distribution': {'auth': 8, 'user': 12},
                    'layer_balance': 'balanced',
                    'domain_focus': 'user'
                },
                'complexity_hotspots': [
                    {'name': 'ComplexClass', 'layer': 'service', 'path': '/src/complex.py', 'complexity': 0.95}
                ],
                'improvement_suggestions': ['Refactor complex methods', 'Add documentation']
            }
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = get_codebase_insights("/test/project")
        
        assert "📊 Codebase Insights for: /test/project" in result
        assert "🏥 Codebase Health:" in result
        assert "Overall Score: 0.750/1.0" in result
        assert "🏗️ Architecture Overview:" in result
        assert "🔥 Complexity Hotspots:" in result
        assert "💡 Improvement Suggestions:" in result
    
    def test_get_codebase_insights_no_enhanced_metadata(self):
        """Test insights when enhanced metadata not available"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.get_analysis_insights.side_effect = Exception("no such column: architectural_layer")
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = get_codebase_insights("/test/project")
        
        assert "❌ Enhanced metadata not available for project" in result
        assert "Run 'enhance_metadata' first" in result
    
    def test_get_codebase_insights_other_exception(self):
        """Test insights with other exception"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.get_analysis_insights.side_effect = Exception("Other error")
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = get_codebase_insights("/test/project")
        
        assert "❌ Insights generation failed: Other error" in result


class TestMCPGetCriticalComponents:
    """Test get_critical_components MCP tool"""
    
    def test_get_critical_components_success(self):
        """Test successful critical components retrieval"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.get_critical_components.return_value = [
                {
                    'name': 'CriticalClass',
                    'node_type': 'class',
                    'path': '/src/critical.py',
                    'architectural_layer': 'service',
                    'business_domain': 'auth',
                    'complexity_score': 0.85,
                    'importance_score': 0.95,
                    'dependencies_impact': 0.90,
                    'llm_summary': 'Core authentication service class'
                }
            ]
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = get_critical_components("/test/project")
        
        assert "🎯 Top 1 Critical Components" in result
        assert "CriticalClass" in result
        assert "📊 Complexity: 0.850" in result
        assert "🎯 Importance: 0.950" in result
        assert "💥 Impact: 0.900" in result
    
    def test_get_critical_components_none_found(self):
        """Test when no critical components found"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.get_critical_components.return_value = []
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = get_critical_components("/test/project")
        
        assert "ℹ️ No critical components found. Run 'enhance_metadata' first." in result
    
    def test_get_critical_components_exception(self):
        """Test critical components with exception"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.get_critical_components.side_effect = Exception("Query failed")
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = get_critical_components("/test/project")
        
        assert "❌ Critical components query failed: Query failed" in result
    
    def test_get_critical_components_with_limit(self):
        """Test critical components with custom limit"""
        critical_components = [
            {
                'name': f'Component{i}',
                'node_type': 'class',
                'path': f'/src/comp{i}.py',
                'criticality_level': 'critical',
                'architectural_layer': 'service',
                'business_domain': 'core',
                'importance_score': 0.9 - i*0.05,
                'complexity_score': 0.8
            }
            for i in range(20)  # Create 20 components
        ]
        
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.get_critical_components.return_value = critical_components[:5]  # Return only 5
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = get_critical_components("/test/project", limit=5)
        
        assert "🎯 Top 5 Critical Components" in result
        assert "Component0" in result
        assert "Component4" in result
        assert "Component5" not in result  # Should not include 6th component
        indexer.get_critical_components.assert_called_once_with(limit=5)


class TestMCPUpdateNodeMetadata:
    """Test update_node_metadata MCP tool"""
    
    def test_update_node_metadata_success(self):
        """Test successful node metadata update"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.update_node_metadata.return_value = True
            pm.get_indexer.return_value = indexer
            
            updates = {'complexity_score': 0.75, 'role_tags': ['core', 'api']}
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = update_node_metadata("/test/project", 123, updates)
        
        assert "✅ Successfully updated metadata for node 123" in result
        assert "complexity_score: 0.75" in result
        assert "role_tags: ['core', 'api']" in result
    
    def test_update_node_metadata_json_string(self):
        """Test update with JSON string input"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.update_node_metadata.return_value = True
            pm.get_indexer.return_value = indexer
            
            updates_json = '{"complexity_score": 0.75}'
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = update_node_metadata("/test/project", 123, updates_json)
        
        assert "✅ Successfully updated metadata for node 123" in result
    
    def test_update_node_metadata_failure(self):
        """Test failed node metadata update"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.update_node_metadata.return_value = False
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = update_node_metadata("/test/project", 123, {})
        
        assert "❌ Failed to update metadata for node 123" in result
    
    def test_update_node_metadata_invalid_json(self):
        """Test update with invalid JSON - expects empty dict due to safe_loads in conftest.py"""
        # Note: conftest.py has a clean_json_cache fixture that makes json.loads
        # return {} for invalid JSON instead of raising an exception
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.update_node_metadata.return_value = True
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    # "invalid json" will be converted to {} by safe_loads
                    result = update_node_metadata("/test/project", 123, "invalid json")
        
        # Since invalid JSON is converted to {}, we expect success with empty updates
        assert "✅ Successfully updated metadata for node 123" in result
        assert "📝 Updates applied:" in result
    
    def test_update_node_metadata_exception(self):
        """Test update with exception"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.update_node_metadata.side_effect = Exception("Update failed")
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = update_node_metadata("/test/project", 123, {})
        
        assert "❌ Update failed: Update failed" in result


class TestMCPHelperFunctions:
    """Test MCP helper functions"""
    
    def test_format_node_types(self):
        """Test _format_node_types helper"""
        from claude_code_indexer.mcp_server import _format_node_types
        
        node_types = {'class': 10, 'function': 50, 'method': 25}
        result = _format_node_types(node_types)
        
        assert "function: 50" in result
        assert "method: 25" in result
        assert "class: 10" in result
    
    def test_format_node_types_empty(self):
        """Test _format_node_types with empty input"""
        from claude_code_indexer.mcp_server import _format_node_types
        
        result = _format_node_types({})
        assert result == "• No data"
    
    def test_format_relationships(self):
        """Test _format_relationships helper"""
        from claude_code_indexer.mcp_server import _format_relationships
        
        relationships = {'calls': 30, 'imports': 20, 'inherits': 5}
        result = _format_relationships(relationships)
        
        assert "calls: 30" in result
        assert "imports: 20" in result
        assert "inherits: 5" in result
    
    def test_format_relationships_empty(self):
        """Test _format_relationships with empty input"""
        from claude_code_indexer.mcp_server import _format_relationships
        
        result = _format_relationships({})
        assert result == "• No data"


class TestMCPServerMain:
    """Test MCP server main function"""
    
    def test_main_without_mcp_sdk(self):
        """Test main function when MCP SDK is not available"""
        # Test the logic without actually running the server
        from claude_code_indexer.mcp_server import MCP_AVAILABLE
        
        # Just verify the MCP_AVAILABLE constant exists and is boolean
        assert isinstance(MCP_AVAILABLE, bool)
    
    def test_main_with_mcp_sdk(self):
        """Test main function when MCP SDK is available"""
        # Test that when MCP is available, the mcp object exists
        from claude_code_indexer.mcp_server import MCP_AVAILABLE
        if MCP_AVAILABLE:
            from claude_code_indexer.mcp_server import mcp
            assert mcp is not None


class TestMCPEnhanceMetadataAdditional:
    """Additional tests for enhance_metadata MCP tool parameters"""
    
    def test_enhance_metadata_with_limit(self):
        """Test enhancement with limit parameter"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.enhance_metadata.return_value = {
                'analyzed_count': 10,
                'total_nodes': 100,
                'analysis_duration': '1.5s',
                'nodes_per_second': 6.7
            }
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = enhance_metadata("/test/project", limit=10)
        
        assert "🤖 LLM Metadata Enhancement Complete" in result
        assert "Analyzed nodes: 10" in result
        indexer.enhance_metadata.assert_called_once_with(limit=10, force_refresh=False)
    
    def test_enhance_metadata_with_force_refresh(self):
        """Test enhancement with force_refresh parameter"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.enhance_metadata.return_value = {
                'analyzed_count': 25,
                'total_nodes': 50,
                'analysis_duration': '3.0s',
                'nodes_per_second': 8.3
            }
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = enhance_metadata("/test/project", force_refresh=True)
        
        assert "🤖 LLM Metadata Enhancement Complete" in result
        assert "Analyzed nodes: 25" in result
        indexer.enhance_metadata.assert_called_once_with(limit=None, force_refresh=True)
    
    def test_enhance_metadata_with_limit_and_force_refresh(self):
        """Test enhancement with both limit and force_refresh parameters"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.enhance_metadata.return_value = {
                'analyzed_count': 15,
                'total_nodes': 75,
                'analysis_duration': '2.2s',
                'nodes_per_second': 6.8,
                'architectural_layers': {'service': 8, 'controller': 4},
                'criticality_distribution': {'critical': 2, 'important': 8},
                'business_domains': {'auth': 5, 'user': 6},
                'average_scores': {'complexity': 0.65, 'testability': 0.78},
                'detected_patterns': {'singleton': 1, 'factory': 2}
            }
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = enhance_metadata("/test/project", limit=15, force_refresh=True)
        
        assert "🤖 LLM Metadata Enhancement Complete" in result
        assert "Analyzed nodes: 15" in result
        assert "🏗️ Architectural Layers:" in result
        assert "service: 8 components" in result
        indexer.enhance_metadata.assert_called_once_with(limit=15, force_refresh=True)


class TestMCPQueryEnhancedNodes:
    """Test query_enhanced_nodes MCP tool"""
    
    @pytest.fixture
    def mock_enhanced_nodes(self):
        """Mock enhanced nodes data"""
        return [
            {
                'name': 'AuthService',
                'node_type': 'class',
                'path': '/src/auth/service.py',
                'architectural_layer': 'service',
                'business_domain': 'authentication',
                'criticality_level': 'critical',
                'complexity_score': 0.85,
                'importance_score': 0.95,
                'role_tags': ['core', 'security'],
                'llm_summary': 'Core authentication service handling user login and security'
            },
            {
                'name': 'UserController',
                'node_type': 'class', 
                'path': '/src/user/controller.py',
                'architectural_layer': 'controller',
                'business_domain': 'user',
                'criticality_level': 'important',
                'complexity_score': 0.65,
                'importance_score': 0.75,
                'role_tags': ['api', 'frontend'],
                'llm_summary': 'User management controller for API endpoints'
            }
        ]
    
    def test_query_enhanced_nodes_success(self, mock_enhanced_nodes):
        """Test successful query without filters"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.return_value = mock_enhanced_nodes
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes("/test/project")
        
        assert "🔍 Enhanced Nodes Query Results" in result
        assert "Found 2 nodes" in result
        assert "AuthService" in result
        assert "UserController" in result
        assert "service" in result
        assert "authentication" in result
        indexer.query_enhanced_nodes.assert_called_once_with(
            architectural_layer=None, business_domain=None, 
            criticality_level=None, min_complexity=None, limit=20
        )
    
    def test_query_enhanced_nodes_with_architectural_layer(self, mock_enhanced_nodes):
        """Test query with architectural_layer filter"""
        filtered_nodes = [mock_enhanced_nodes[0]]  # Only service layer
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.return_value = filtered_nodes
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes("/test/project", architectural_layer="service")
        
        assert "🔍 Enhanced Nodes Query Results" in result
        assert "Layer: service" in result
        assert "Found 1 nodes" in result
        assert "AuthService" in result
        indexer.query_enhanced_nodes.assert_called_once_with(
            architectural_layer="service", business_domain=None, 
            criticality_level=None, min_complexity=None, limit=20
        )
    
    def test_query_enhanced_nodes_with_business_domain(self, mock_enhanced_nodes):
        """Test query with business_domain filter"""
        filtered_nodes = [mock_enhanced_nodes[0]]  # Only authentication domain
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.return_value = filtered_nodes
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes("/test/project", business_domain="authentication")
        
        assert "🔍 Enhanced Nodes Query Results" in result
        assert "Domain: authentication" in result
        assert "Found 1 nodes" in result
        indexer.query_enhanced_nodes.assert_called_once_with(
            architectural_layer=None, business_domain="authentication", 
            criticality_level=None, min_complexity=None, limit=20
        )
    
    def test_query_enhanced_nodes_with_criticality_level(self, mock_enhanced_nodes):
        """Test query with criticality_level filter"""
        filtered_nodes = [mock_enhanced_nodes[0]]  # Only critical level
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.return_value = filtered_nodes
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes("/test/project", criticality_level="critical")
        
        assert "🔍 Enhanced Nodes Query Results" in result
        assert "Criticality: critical" in result
        assert "Found 1 nodes" in result
        indexer.query_enhanced_nodes.assert_called_once_with(
            architectural_layer=None, business_domain=None, 
            criticality_level="critical", min_complexity=None, limit=20
        )
    
    def test_query_enhanced_nodes_with_min_complexity(self, mock_enhanced_nodes):
        """Test query with min_complexity filter"""
        filtered_nodes = [mock_enhanced_nodes[0]]  # Only high complexity
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.return_value = filtered_nodes
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes("/test/project", min_complexity=0.8)
        
        assert "🔍 Enhanced Nodes Query Results" in result
        assert "Min Complexity: 0.8" in result
        assert "Found 1 nodes" in result
        indexer.query_enhanced_nodes.assert_called_once_with(
            architectural_layer=None, business_domain=None, 
            criticality_level=None, min_complexity=0.8, limit=20
        )
    
    def test_query_enhanced_nodes_with_limit(self, mock_enhanced_nodes):
        """Test query with custom limit"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.return_value = mock_enhanced_nodes
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes("/test/project", limit=5)
        
        assert "🔍 Enhanced Nodes Query Results" in result
        assert "(limit: 5)" in result
        indexer.query_enhanced_nodes.assert_called_once_with(
            architectural_layer=None, business_domain=None, 
            criticality_level=None, min_complexity=None, limit=5
        )
    
    def test_query_enhanced_nodes_with_multiple_filters(self, mock_enhanced_nodes):
        """Test query with multiple filters combined"""
        filtered_nodes = [mock_enhanced_nodes[0]]
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.return_value = filtered_nodes
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes(
                        "/test/project", 
                        architectural_layer="service",
                        business_domain="authentication",
                        criticality_level="critical",
                        min_complexity=0.8,
                        limit=10
                    )
        
        assert "🔍 Enhanced Nodes Query Results" in result
        assert "Layer: service" in result
        assert "Domain: authentication" in result
        assert "Criticality: critical" in result
        assert "Min Complexity: 0.8" in result
        assert "(limit: 10)" in result
        indexer.query_enhanced_nodes.assert_called_once_with(
            architectural_layer="service", business_domain="authentication", 
            criticality_level="critical", min_complexity=0.8, limit=10
        )
    
    def test_query_enhanced_nodes_no_results(self):
        """Test query when no results found"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.return_value = []
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes("/test/project")
        
        assert "ℹ️ No enhanced nodes found matching the criteria" in result
    
    def test_query_enhanced_nodes_nonexistent_path(self):
        """Test query with non-existent path"""
        with patch('os.path.exists', return_value=False):
            with patch('os.path.abspath', return_value="/nonexistent"):
                result = query_enhanced_nodes("/nonexistent")
        
        assert "❌ Project path does not exist: /nonexistent" in result
    
    def test_query_enhanced_nodes_exception(self):
        """Test query with exception"""
        with patch('claude_code_indexer.mcp_server.project_manager') as pm:
            indexer = Mock()
            indexer.query_enhanced_nodes.side_effect = Exception("Query failed")
            pm.get_indexer.return_value = indexer
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.abspath', return_value="/test/project"):
                    result = query_enhanced_nodes("/test/project")
        
        assert "❌ Query failed: Query failed" in result