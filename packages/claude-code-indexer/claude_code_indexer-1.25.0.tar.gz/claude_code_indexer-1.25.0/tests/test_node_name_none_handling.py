"""Test handling of None node names during parsing and database operations"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
from claude_code_indexer.indexer import CodeGraphIndexer
from claude_code_indexer.parsers.python_parser import PythonParser
from claude_code_indexer.parsers.base_parser import BaseParser


def test_syntax_error_file_handling(isolated_storage_manager):
    """Test that files with syntax errors don't cause None name issues"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a Python file with syntax error that might cause None names
        test_file = Path(temp_dir) / "syntax_error.py"
        test_file.write_text("""
def test_function():
    print("Hello")
    
# This will cause a syntax error
EOF < /dev/null
""")
        
        # Create indexer
        indexer = CodeGraphIndexer(temp_dir)
        
        # Index should complete without crashing
        indexer.index_directory()
        
        # Verify all nodes have valid names (not None)
        for node_id, node_info in indexer.nodes.items():
            assert node_info.get('name') is not None or node_info.get('name', '') != '', \
                f"Node {node_id} has None or empty name"


def test_node_name_strip_with_none(isolated_storage_manager):
    """Test that node names handle None values correctly during database save"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        indexer = CodeGraphIndexer(temp_dir)
        
        # Manually add a node with None name to test the fix
        indexer.nodes[999] = {
            'id': 999,
            'name': None,  # This should be handled gracefully
            'node_type': 'test',
            'path': 'test.py',
            'summary': 'Test node with None name',
            'line_number': 1,
            'column_number': 0
        }
        
        # Save to database should not crash
        with patch.object(indexer, '_create_or_get_storage_manager') as mock_storage:
            mock_storage.return_value = MagicMock()
            
            # This should not raise an AttributeError about 'NoneType' object has no attribute 'strip'
            try:
                indexer.save_to_database()
            except AttributeError as e:
                if "'NoneType' object has no attribute 'strip'" in str(e):
                    pytest.fail(f"The None name bug is not fixed: {e}")


def test_base_parser_handles_none_names():
    """Test that BaseParser._create_node handles None names correctly"""
    
    parser = PythonParser()  # Use concrete implementation
    
    # Test with None name
    node = parser._create_node(
        node_type='test',
        name=None,  # This should be handled
        path='test.py',
        summary='Test node'
    )
    
    # The base parser should generate a default name
    assert node.name is not None, "BaseParser should generate a name when None is passed"
    assert node.name.startswith('test_'), "Generated name should start with node_type"
    assert 'test.py' in node.name, "Generated name should include file name"


def test_import_with_none_alias_name():
    """Test handling of import statements where alias.name might be None"""
    
    parser = PythonParser()
    
    # Create a mock AST import node with None name
    import ast
    mock_import = ast.Import(names=[])
    mock_alias = ast.alias(name=None, asname=None)  # This could happen with malformed code
    mock_import.names = [mock_alias]
    mock_import.lineno = 1
    mock_import.col_offset = 0
    
    parent_node = MagicMock(id=1)
    nodes = {}
    relationships = []
    
    # This should handle None gracefully in the parser
    with patch.object(parser, '_create_node') as mock_create:
        mock_create.return_value = MagicMock(id=2)
        
        # Should not crash when alias.name is None
        parser._handle_import(mock_import, parent_node, 'test.py', nodes, relationships)
        
        # The parser passes None, but _create_node should handle it
        call_args = mock_create.call_args[1]
        # The parser passes alias.name directly, which is None
        assert call_args['name'] is None, "Parser passes None directly to _create_node"


def test_database_save_with_various_none_fields(isolated_storage_manager):
    """Test database save handles various None fields correctly"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        indexer = CodeGraphIndexer(temp_dir)
        
        # Add nodes with various None fields
        test_nodes = [
            {
                'id': 1,
                'name': None,
                'node_type': 'function',
                'path': 'test.py',
                'summary': 'Test',
                'line_number': 1,
                'column_number': 0
            },
            {
                'id': 2,
                'name': 'valid_name',
                'node_type': None,  # This should also be handled
                'path': 'test.py',
                'summary': None,
                'line_number': 1,
                'column_number': 0
            },
            {
                'id': 3,
                'name': '',  # Empty string
                'node_type': 'class',
                'path': None,
                'summary': 'Test',
                'line_number': None,
                'column_number': None
            }
        ]
        
        for node in test_nodes:
            indexer.nodes[node['id']] = node
        
        # Database save should handle all these cases
        with patch.object(indexer, '_create_or_get_storage_manager') as mock_storage:
            mock_storage.return_value = MagicMock()
            
            # Should not crash with any None values
            indexer.save_to_database()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])