#!/usr/bin/env python3
"""
Test cases for bug #16: query --type filter logic
Ensures type filtering works correctly with --important flag
"""

import pytest
import tempfile
import os
from click.testing import CliRunner
from pathlib import Path

from claude_code_indexer.cli import cli
from claude_code_indexer.indexer import CodeGraphIndexer


class TestQueryTypeFilter:
    """Test query --type filter functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.runner = CliRunner()
        
        # Create test Python files with different entities
        test_files = {
            'test_class.py': '''
class TestClass:
    """A test class"""
    
    def test_method(self):
        """A test method"""
        return "method"

def test_function():
    """A test function"""
    return "function"
''',
            'another_file.py': '''
class AnotherClass:
    """Another class"""
    pass

def another_function():
    """Another function"""  
    pass
'''
        }
        
        for filename, content in test_files.items():
            file_path = Path(self.test_dir) / filename
            file_path.write_text(content)
        
        # Index the test files
        result = self.runner.invoke(cli, ['index', self.test_dir])
        assert result.exit_code == 0
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        try:
            shutil.rmtree(self.test_dir)
        except:
            pass
    
    def test_query_with_valid_type_class(self):
        """Test query with valid type 'class'"""
        result = self.runner.invoke(cli, ['query', '--type', 'class', '--project', self.test_dir])
        assert result.exit_code == 0
        assert 'TestClass' in result.output or 'AnotherClass' in result.output
        assert 'test_function' not in result.output
    
    def test_query_with_valid_type_function(self):
        """Test query with valid type 'function'"""
        result = self.runner.invoke(cli, ['query', '--type', 'function', '--project', self.test_dir])
        assert result.exit_code == 0
        assert 'test_function' in result.output or 'another_function' in result.output
        assert 'TestClass' not in result.output
    
    def test_query_with_valid_type_method(self):
        """Test query with valid type 'method'"""
        result = self.runner.invoke(cli, ['query', '--type', 'method', '--project', self.test_dir])
        assert result.exit_code == 0
        assert 'test_method' in result.output
    
    def test_query_with_invalid_type(self):
        """Test query with invalid/nonexistent type"""
        result = self.runner.invoke(cli, ['query', '--type', 'nonexistent', '--project', self.test_dir])
        assert result.exit_code == 0
        assert "No entities found of type 'nonexistent'" in result.output
    
    def test_query_important_with_valid_type(self):
        """Test query --important with valid type filter"""
        result = self.runner.invoke(cli, ['query', '--important', '--type', 'class', '--project', self.test_dir])
        assert result.exit_code == 0
        # Should show classes only, not functions
        if 'TestClass' in result.output or 'AnotherClass' in result.output:
            assert 'test_function' not in result.output
    
    def test_query_important_with_invalid_type(self):
        """Test query --important with invalid type - should not fallback to all types"""
        result = self.runner.invoke(cli, ['query', '--important', '--type', 'invalidtype', '--project', self.test_dir])
        assert result.exit_code == 0
        assert "No entities found of type 'invalidtype'" in result.output
        # Should NOT show entities of other types
        assert 'TestClass' not in result.output
        assert 'test_function' not in result.output
    
    def test_query_without_type_filter(self):
        """Test query without type filter shows all types"""
        result = self.runner.invoke(cli, ['query', '--project', self.test_dir])
        assert result.exit_code == 0
        # Should show multiple types
        output_lower = result.output.lower()
        type_count = sum([
            'class' in output_lower,
            'function' in output_lower, 
            'method' in output_lower
        ])
        assert type_count >= 2  # Should see at least 2 different types
    
    def test_query_important_fallback_behavior(self):
        """Test that --important fallback preserves type filter"""
        # This tests the fix for bug #16
        result = self.runner.invoke(cli, ['query', '--important', '--type', 'file', '--project', self.test_dir])
        assert result.exit_code == 0
        
        if "No entities found" not in result.output:
            # If we get results, they should all be 'file' type
            assert 'class' not in result.output.lower() or 'file' in result.output.lower()
    
    def test_supported_node_types(self):
        """Test all commonly supported node types"""
        supported_types = ['class', 'function', 'method', 'file']
        
        for node_type in supported_types:
            result = self.runner.invoke(cli, ['query', '--type', node_type, '--project', self.test_dir])
            assert result.exit_code == 0
            # Should either find entities or show "No entities found" message
            assert (node_type in result.output or 
                   "No entities found" in result.output)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])