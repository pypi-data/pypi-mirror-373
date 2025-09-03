#!/usr/bin/env python3
"""
Comprehensive tests for MCP ProjectManager class
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import sqlite3
import tempfile

# Mock the MCP imports first
with patch('claude_code_indexer.mcp_server.FastMCP'):
    from claude_code_indexer.mcp_server import ProjectManager


class TestProjectManager:
    """Test suite for ProjectManager class"""
    
    @pytest.fixture
    def mock_storage_manager(self):
        """Create mock storage manager"""
        mock_storage = Mock()
        mock_storage.get_project_dir.return_value = Path("/tmp/test_project")
        return mock_storage
    
    @pytest.fixture
    def project_manager(self, mock_storage_manager):
        """Create ProjectManager instance with mocked dependencies"""
        with patch('claude_code_indexer.mcp_server.get_storage_manager', return_value=mock_storage_manager):
            return ProjectManager()
    
    def test_init(self, mock_storage_manager):
        """Test ProjectManager initialization"""
        with patch('claude_code_indexer.mcp_server.get_storage_manager', return_value=mock_storage_manager):
            pm = ProjectManager()
            
            assert pm.storage == mock_storage_manager
            assert pm.indexers == {}
            assert isinstance(pm.indexers, dict)
    
    def test_get_indexer_new_project(self, project_manager, mock_storage_manager):
        """Test getting indexer for new project"""
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer = Mock()
            mock_indexer_class.return_value = mock_indexer
            
            # Get indexer for new project
            project_path = "/test/project"
            indexer = project_manager.get_indexer(project_path)
            
            # Verify indexer created
            mock_indexer_class.assert_called_once_with(
                project_path=Path(project_path).resolve(),
                use_cache=True,
                parallel_workers=4,
                enable_optimizations=True
            )
            
            # Verify cached
            assert str(Path(project_path).resolve()) in project_manager.indexers
            assert project_manager.indexers[str(Path(project_path).resolve())] == mock_indexer
    
    def test_get_indexer_cached_project(self, project_manager):
        """Test getting cached indexer for existing project"""
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer = Mock()
            mock_indexer_class.return_value = mock_indexer
            
            # Get indexer twice
            project_path = "/test/project"
            indexer1 = project_manager.get_indexer(project_path)
            indexer2 = project_manager.get_indexer(project_path)
            
            # Should only create once
            mock_indexer_class.assert_called_once()
            
            # Should return same instance
            assert indexer1 is indexer2
    
    def test_get_indexer_with_custom_workers(self, project_manager):
        """Test getting indexer with custom worker count"""
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer = Mock()
            mock_indexer_class.return_value = mock_indexer
            
            # Get indexer with custom workers
            project_path = "/test/project"
            indexer = project_manager.get_indexer(project_path, workers=8)
            
            # Verify custom workers passed
            mock_indexer_class.assert_called_once_with(
                project_path=Path(project_path).resolve(),
                use_cache=True,
                parallel_workers=8,
                enable_optimizations=True
            )
    
    def test_get_indexer_different_projects(self, project_manager):
        """Test getting indexers for different projects"""
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer1 = Mock()
            mock_indexer2 = Mock()
            mock_indexer_class.side_effect = [mock_indexer1, mock_indexer2]
            
            # Get indexers for different projects
            indexer1 = project_manager.get_indexer("/project1")
            indexer2 = project_manager.get_indexer("/project2")
            
            # Should create two different indexers
            assert mock_indexer_class.call_count == 2
            assert indexer1 != indexer2
            
            # Both should be cached
            assert len(project_manager.indexers) == 2
    
    def test_get_indexer_path_resolution(self, project_manager):
        """Test path resolution in get_indexer"""
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer = Mock()
            mock_indexer_class.return_value = mock_indexer
            
            # Get indexer with relative path
            relative_path = "./relative/path"
            indexer = project_manager.get_indexer(relative_path)
            
            # Should resolve to absolute path
            expected_path = Path(relative_path).resolve()
            mock_indexer_class.assert_called_once()
            actual_path = mock_indexer_class.call_args[1]['project_path']
            assert actual_path == expected_path
    
    def test_get_indexer_symlink_handling(self, project_manager):
        """Test handling of symlinked paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create real directory and symlink
            real_dir = Path(tmpdir) / "real_project"
            real_dir.mkdir()
            symlink_dir = Path(tmpdir) / "symlink_project"
            symlink_dir.symlink_to(real_dir)
            
            with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
                mock_indexer = Mock()
                mock_indexer_class.return_value = mock_indexer
                
                # Get indexer via symlink
                indexer1 = project_manager.get_indexer(str(symlink_dir))
                # Get indexer via real path
                indexer2 = project_manager.get_indexer(str(real_dir))
                
                # Should resolve to same path and use cached indexer
                assert indexer1 is indexer2
                mock_indexer_class.assert_called_once()
    
    def test_indexer_cache_memory_management(self, project_manager):
        """Test memory management of indexer cache"""
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer_class.return_value = Mock()
            
            # Create many indexers
            for i in range(100):
                project_manager.get_indexer(f"/project_{i}")
            
            # Verify all cached (no eviction in current implementation)
            assert len(project_manager.indexers) == 100
    
    def test_concurrent_access(self, project_manager):
        """Test concurrent access to get_indexer"""
        import threading
        
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer = Mock()
            mock_indexer_class.return_value = mock_indexer
            
            results = []
            
            def get_indexer_thread():
                indexer = project_manager.get_indexer("/concurrent/project")
                results.append(indexer)
            
            # Create multiple threads
            threads = []
            for _ in range(10):
                t = threading.Thread(target=get_indexer_thread)
                threads.append(t)
                t.start()
            
            # Wait for all threads
            for t in threads:
                t.join()
            
            # Should only create one indexer
            mock_indexer_class.assert_called_once()
            
            # All results should be the same instance
            assert all(r is results[0] for r in results)


class TestProjectManagerIntegration:
    """Integration tests for ProjectManager with real components"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "test_project"
            project_dir.mkdir()
            
            # Create some Python files
            (project_dir / "main.py").write_text("def main(): pass")
            (project_dir / "utils.py").write_text("def helper(): pass")
            
            yield project_dir
    
    def test_integration_with_storage_manager(self, temp_project_dir):
        """Test integration with real storage manager"""
        from claude_code_indexer.storage_manager import get_storage_manager
        
        # Create project manager with real storage
        pm = ProjectManager()
        
        # Get indexer
        indexer = pm.get_indexer(str(temp_project_dir))
        
        # Verify indexer created
        assert indexer is not None
        assert str(temp_project_dir.resolve()) in pm.indexers
    
    @pytest.mark.skipif(True, reason="Requires full MCP setup")
    def test_mcp_tool_integration(self):
        """Test integration with MCP tools"""
        # This would test the actual MCP tool decorators
        # Skipped as it requires full MCP environment
        pass


class TestProjectManagerErrorHandling:
    """Test error handling in ProjectManager"""
    
    @pytest.fixture
    def mock_storage_manager(self):
        """Create mock storage manager"""
        mock_storage = Mock()
        mock_storage.get_project_dir.return_value = Path("/tmp/test_project")
        return mock_storage
    
    @pytest.fixture
    def project_manager(self, mock_storage_manager):
        """Create ProjectManager instance with mocked dependencies"""
        with patch('claude_code_indexer.mcp_server.get_storage_manager', return_value=mock_storage_manager):
            return ProjectManager()
    
    def test_invalid_project_path(self, project_manager):
        """Test handling of invalid project paths"""
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer_class.side_effect = Exception("Invalid path")
            
            with pytest.raises(Exception, match="Invalid path"):
                project_manager.get_indexer("/nonexistent/path")
    
    def test_storage_manager_failure(self):
        """Test handling of storage manager failures"""
        with patch('claude_code_indexer.mcp_server.get_storage_manager') as mock_get_storage:
            mock_get_storage.side_effect = Exception("Storage error")
            
            with pytest.raises(Exception, match="Storage error"):
                ProjectManager()
    
    def test_indexer_creation_failure(self, project_manager):
        """Test handling of indexer creation failures"""
        with patch('claude_code_indexer.mcp_server.CodeGraphIndexer') as mock_indexer_class:
            mock_indexer_class.side_effect = MemoryError("Out of memory")
            
            with pytest.raises(MemoryError, match="Out of memory"):
                project_manager.get_indexer("/test/project")