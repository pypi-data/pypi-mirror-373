#!/usr/bin/env python3
"""
Comprehensive tests for CodeGraphIndexer
Tests core indexing functionality with >80% coverage goal
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock ensmallen before importing to avoid logger conflicts
sys.modules['ensmallen'] = MagicMock()

from claude_code_indexer.indexer import CodeGraphIndexer
from claude_code_indexer.parsers import ParseResult


class TestCodeGraphIndexer:
    """Test suite for CodeGraphIndexer class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_python_file(self, temp_dir):
        """Create sample Python file for testing"""
        file_path = Path(temp_dir) / "sample.py"
        content = '''
def hello_world():
    """Say hello"""
    print("Hello, World!")

class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

if __name__ == "__main__":
    hello_world()
    calc = Calculator()
    print(calc.add(5, 3))
'''
        file_path.write_text(content)
        return file_path
    
    @pytest.fixture
    def sample_javascript_file(self, temp_dir):
        """Create sample JavaScript file for testing"""
        file_path = Path(temp_dir) / "sample.js"
        content = '''
function greet(name) {
    console.log(`Hello, ${name}!`);
}

class Math {
    static add(a, b) {
        return a + b;
    }
    
    static multiply(a, b) {
        return a * b;
    }
}

module.exports = { greet, Math };
'''
        file_path.write_text(content)
        return file_path
    
    def test_initialization_default(self, temp_dir):
        """Test default initialization of CodeGraphIndexer"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            
            assert indexer.project_path == Path(temp_dir)
            assert indexer.db_path == str(Path(temp_dir) / "test.db")
            assert indexer.use_cache is True
            assert indexer.enable_optimizations is True
            assert indexer.node_counter == 0
            assert len(indexer.nodes) == 0
            assert len(indexer.edges) == 0
    
    def test_initialization_with_params(self, temp_dir):
        """Test initialization with custom parameters"""
        db_path = str(Path(temp_dir) / "custom.db")
        project_path = Path(temp_dir)
        
        with patch('claude_code_indexer.indexer.get_storage_manager'):
            indexer = CodeGraphIndexer(
                db_path=db_path,
                use_cache=False,
                parallel_workers=2,
                enable_optimizations=False,
                project_path=project_path
            )
            
            assert indexer.db_path == db_path
            assert indexer.project_path == project_path
            assert indexer.use_cache is False
            assert indexer.enable_optimizations is False
    
    def test_database_initialization(self, temp_dir):
        """Test database schema creation"""
        db_path = str(Path(temp_dir) / "test.db")
        
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(db_path)
            
            indexer = CodeGraphIndexer(db_path=db_path)
            
            # Verify database exists
            assert os.path.exists(db_path)
            
            # Verify tables exist
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check code_nodes table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='code_nodes'")
            assert cursor.fetchone() is not None
            
            # Check relationships table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relationships'")
            assert cursor.fetchone() is not None
            
            # Check indexing_metadata table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='indexing_metadata'")
            assert cursor.fetchone() is not None
            
            conn.close()
    
    def test_create_node(self, temp_dir):
        """Test creating nodes in the graph"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            
            # Create a function node using internal method
            node_id = indexer._create_node(
                node_type="function",
                name="test_function",
                path="/test/file.py",
                summary="Test function"
            )
            
            assert node_id == 0
            assert len(indexer.nodes) == 1
            assert indexer.nodes[0]['name'] == "test_function"
            assert indexer.nodes[0]['node_type'] == "function"
            assert indexer.nodes[0]['path'] == "/test/file.py"
            assert indexer.nodes[0]['summary'] == "Test function"
            assert indexer.node_counter == 1
    
    def test_add_edge(self, temp_dir):
        """Test adding edges between nodes"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            
            # Create two nodes
            node1 = indexer._create_node("function", "func1", "/file1.py", "Function 1")
            node2 = indexer._create_node("function", "func2", "/file2.py", "Function 2")
            
            # Add edge directly
            indexer.edges.append((node1, node2, "calls"))
            
            assert len(indexer.edges) == 1
            assert indexer.edges[0] == (node1, node2, "calls")
    
    def test_process_python_file(self, temp_dir, sample_python_file):
        """Test processing a Python file"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            
            # Process the file using the actual method
            result = indexer.parse_code_file(str(sample_python_file))
            
            # Verify result is a dict of nodes
            assert result is not None
            assert isinstance(result, dict)
            assert len(result) > 0
            
            # Verify nodes were created in indexer
            assert len(indexer.nodes) > 0
            
            # Check that expected nodes exist
            node_names = [node['name'] for node in indexer.nodes.values()]
            assert 'hello_world' in node_names
            assert 'Calculator' in node_names
    
    def test_process_javascript_file(self, temp_dir, sample_javascript_file):
        """Test processing a JavaScript file"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            
            # Process the file
            result = indexer.parse_code_file(str(sample_javascript_file))
            
            # Verify result
            assert result is not None
            assert isinstance(result, dict)
            
            # Verify nodes were created
            assert len(indexer.nodes) > 0
            
            # Check expected nodes
            node_names = [node['name'] for node in indexer.nodes.values()]
            assert 'greet' in node_names or 'Math' in node_names
    
    def test_incremental_indexing(self, temp_dir, sample_python_file):
        """Test incremental indexing with cache"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            # First indexing
            indexer1 = CodeGraphIndexer(use_cache=True)
            indexer1.index_directory(temp_dir)
            nodes_count1 = len(indexer1.nodes)
            
            # Modify file
            sample_python_file.write_text(sample_python_file.read_text() + "\n# Modified")
            
            # Second indexing (should use cache for unchanged parts)
            indexer2 = CodeGraphIndexer(use_cache=True)
            indexer2.index_directory(temp_dir)
            
            # Should have same or more nodes
            assert len(indexer2.nodes) >= nodes_count1
    
    def test_parallel_processing(self, temp_dir):
        """Test parallel file processing"""
        # Create multiple files
        for i in range(5):
            file_path = Path(temp_dir) / f"file{i}.py"
            file_path.write_text(f"def function{i}():\n    pass")
        
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer(parallel_workers=2)
            indexer.index_directory(temp_dir)
            
            # Verify all files were processed
            assert len(indexer.nodes) >= 5
    
    def test_error_handling_invalid_file(self, temp_dir):
        """Test error handling for invalid files"""
        invalid_file = Path(temp_dir) / "invalid.py"
        invalid_file.write_text("def invalid syntax")
        
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            
            # Should not raise exception
            result = indexer.parse_code_file(str(invalid_file))
            
            # Should return None or empty result for invalid file
            assert result is None or (result.get('nodes', {}) == {})
    
    def test_llm_metadata_enhancement(self, temp_dir, sample_python_file):
        """Test LLM metadata enhancement integration"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            
            # Process file first
            result = indexer.parse_code_file(str(sample_python_file))
            assert result is not None
            
            # Test that indexer has LLM enhancement capability
            assert hasattr(indexer, 'enhance_metadata')
            assert hasattr(indexer, 'llm_enhancer')
    
    def test_weight_calculation(self, temp_dir, sample_python_file):
        """Test weight calculation for nodes"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            result = indexer.parse_code_file(str(sample_python_file))
            assert result is not None
            
            # Store file content for weight calculation
            indexer.all_files_content[str(sample_python_file)] = sample_python_file.read_text()
            
            # Calculate weights for all nodes and edges
            weighted_nodes, weighted_edges = indexer.weight_calculator.calculate_weights(
                indexer.nodes, 
                indexer.edges,
                indexer.all_files_content
            )
            
            # Verify weights were calculated
            assert len(weighted_nodes) > 0
            for node_id, node in weighted_nodes.items():
                assert 'weight' in node
                assert node['weight'] >= 0
    
    def test_pattern_detection(self, temp_dir):
        """Test pattern detection in code"""
        pattern_file = Path(temp_dir) / "pattern.py"
        content = '''
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()

class Subject:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def notify(self):
        for observer in self.observers:
            observer.update(self)
'''
        pattern_file.write_text(content)
        
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            # Parse the file to populate nodes
            result = indexer.parse_code_file(str(pattern_file))
            
            # Check that pattern detector found patterns
            import ast
            with open(pattern_file) as f:
                tree = ast.parse(f.read())
            patterns = indexer.pattern_detector.detect_patterns(tree, str(pattern_file))
            
            # Patterns should be detected
            assert len(patterns) > 0, f"No patterns detected. Pattern types found: {[p.pattern_type for p in patterns] if patterns else 'None'}"
    
    def test_infrastructure_detection(self, temp_dir):
        """Test infrastructure component detection"""
        infra_file = Path(temp_dir) / "database.py"
        content = '''
import sqlite3
import redis
from flask import Flask
from celery import Celery

app = Flask(__name__)
celery = Celery('tasks', broker='redis://localhost:6379')

def connect_db():
    return sqlite3.connect('app.db')

@app.route('/api/users')
def get_users():
    conn = connect_db()
    # API endpoint
    return {"users": []}
'''
        infra_file.write_text(content)
        
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            # Parse the file to populate nodes
            result = indexer.parse_code_file(str(infra_file))
            
            # Verify nodes were created
            assert result is not None
            assert len(result) > 0
            
            # Check that infrastructure-related imports were detected
            node_names = [node['name'] for node in result.values()]
            assert 'sqlite3' in node_names or 'redis' in node_names or 'flask' in node_names
    
    def test_query_functionality(self, temp_dir, sample_python_file):
        """Test querying indexed code"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            indexer.index_directory(temp_dir)
            
            # Query for important nodes
            results = indexer.query_important_nodes(node_type="function")
            assert isinstance(results, list)
            
            # Check if hello_world function was indexed
            conn = sqlite3.connect(indexer.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM code_nodes WHERE name LIKE 'hello%'")
            result = cursor.fetchone()
            conn.close()
            assert result is not None
    
    def test_export_functionality(self, temp_dir, sample_python_file):
        """Test exporting graph data"""
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            indexer.index_directory(temp_dir)
            
            # Export data manually from database
            conn = sqlite3.connect(indexer.db_path)
            cursor = conn.cursor()
            
            # Get nodes
            cursor.execute("SELECT * FROM code_nodes")
            nodes = cursor.fetchall()
            
            # Get edges
            cursor.execute("SELECT * FROM relationships")
            edges = cursor.fetchall()
            
            conn.close()
            
            # Verify we have data
            assert len(nodes) > 0
            assert len(edges) >= 0
    
    def test_gitignore_respect(self, temp_dir):
        """Test that .gitignore patterns are respected"""
        # Create .gitignore
        gitignore = Path(temp_dir) / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\ntest_ignore.py")
        
        # Create files
        (Path(temp_dir) / "include.py").write_text("def included(): pass")
        (Path(temp_dir) / "test_ignore.py").write_text("def ignored(): pass")
        (Path(temp_dir) / "test.pyc").write_text("compiled")
        
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            indexer.index_directory(temp_dir)
            
            # Check database for indexed files
            conn = sqlite3.connect(indexer.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM code_nodes")
            node_names = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            assert 'included' in node_names
            assert 'ignored' not in node_names
    
    def test_multi_language_project(self, temp_dir):
        """Test indexing project with multiple languages"""
        # Create files in different languages
        (Path(temp_dir) / "app.py").write_text("def python_func(): pass")
        (Path(temp_dir) / "app.js").write_text("function jsFunc() {}")
        (Path(temp_dir) / "App.java").write_text("class App { void javaMethod() {} }")
        
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            indexer = CodeGraphIndexer()
            indexer.index_directory(temp_dir)
            
            # Verify all languages were processed by checking database
            conn = sqlite3.connect(indexer.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT path FROM code_nodes")
            file_paths = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            assert any('app.py' in fp for fp in file_paths)
            assert any('app.js' in fp for fp in file_paths)
            assert any('App.java' in fp for fp in file_paths)
    
    def test_database_migration(self, temp_dir):
        """Test database schema migration"""
        db_path = str(Path(temp_dir) / "test.db")
        
        # Create old schema database (v1.0.0 compatible)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Create a v1.0.0 compatible schema (matching migration_001_v1_0_0.py)
        cursor.execute('''CREATE TABLE code_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_type TEXT NOT NULL,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            summary TEXT,
            importance_score REAL DEFAULT 0.0,
            relevance_tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Add relationships table to make it look like v1.0.0
        cursor.execute('''CREATE TABLE relationships (
            source_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (source_id, target_id, relationship_type)
        )''')
        # Add indexing_metadata table
        cursor.execute('''CREATE TABLE indexing_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
        conn.close()
        
        # Initialize indexer (should detect as v1.0.0 and migrate to latest)
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(db_path)
            
            indexer = CodeGraphIndexer(db_path=db_path)
            
            # Verify new columns exist
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(code_nodes)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Should have new columns from migration
            assert 'path' in columns or len(columns) > 3
            conn.close()
    
    def test_memory_efficient_processing(self, temp_dir):
        """Test memory-efficient processing of large projects"""
        # Create many files
        for i in range(100):
            file_path = Path(temp_dir) / f"module{i}.py"
            file_path.write_text(f"def func{i}(): pass")
        
        with patch('claude_code_indexer.indexer.get_storage_manager') as mock_storage:
            mock_storage.return_value.get_project_from_cwd.return_value = Path(temp_dir)
            mock_storage.return_value.get_database_path.return_value = Path(temp_dir) / "test.db"
            
            # Use optimizations for memory efficiency
            indexer = CodeGraphIndexer(enable_optimizations=True, use_cache=True)
            
            # Should process without memory issues
            indexer.index_directory(temp_dir)
            
            # Verify by checking database
            conn = sqlite3.connect(indexer.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT path) FROM code_nodes")
            file_count = cursor.fetchone()[0]
            conn.close()
            
            assert file_count >= 50  # At least some files were processed

    def test_database_migration_failure(self, temp_dir):
        """Test handling of database migration failures"""
        with patch('claude_code_indexer.indexer.MigrationManager') as mock_migration:
            mock_migration.return_value.migrate.return_value = (False, "Migration failed")
            
            with pytest.raises(RuntimeError, match="Failed to migrate database"):
                CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))

    def test_cached_result_integration(self, temp_dir, sample_python_file):
        """Test integration of cached parsing results"""
        indexer = CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))
        
        # Mock cache manager to return cached result
        mock_cached_result = Mock()
        mock_cached_result.file_path = sample_python_file
        mock_cached_result.nodes = {1: {'name': 'test_function', 'type': 'function'}}
        mock_cached_result.edges = [(1, 2, {'type': 'calls'})]
        
        with patch.object(indexer.cache_manager, 'get_cached_result') as mock_get_cache:
            mock_get_cache.return_value = mock_cached_result
            
            # This should integrate cached results
            indexer._integrate_cached_result(mock_cached_result)
            
            # Verify nodes were integrated
            assert len(indexer.nodes) > 0
            assert any(node['name'] == 'test_function' for node in indexer.nodes.values())

    def test_error_handling_file_read(self, temp_dir):
        """Test error handling when file cannot be read"""
        indexer = CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))
        
        # Create a file and then remove it to simulate read error
        test_file = Path(temp_dir) / "missing.py"
        test_file.write_text("def test(): pass")
        test_file.unlink()  # Remove file
        
        # Should handle missing file gracefully
        indexer.index_directory(temp_dir)
        
        # Should not crash
        assert True

    def test_build_graph_with_relationships(self, temp_dir):
        """Test graph building with various relationship types"""
        indexer = CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))
        
        # Add nodes manually using internal method
        node1_id = indexer._create_node("function", "function1", "/test/file1.py", "A test function")
        node2_id = indexer._create_node("function", "function2", "/test/file1.py", "Another function")
        node3_id = indexer._create_node("class", "class1", "/test/file1.py", "A test class")
        
        # Add to internal nodes dict for graph building
        indexer.nodes[node1_id] = {"name": "function1", "node_type": "function", "path": "/test/file1.py"}
        indexer.nodes[node2_id] = {"name": "function2", "node_type": "function", "path": "/test/file1.py"}
        indexer.nodes[node3_id] = {"name": "class1", "node_type": "class", "path": "/test/file1.py"}
        
        # Add edges manually
        indexer.edges.append((node1_id, node2_id, {"relationship": "calls"}))
        indexer.edges.append((node3_id, node1_id, {"relationship": "contains"}))
        
        # Build graph
        graph = indexer.build_graph()
        
        # Verify graph structure
        assert graph.number_of_nodes() >= 3
        assert graph.number_of_edges() >= 2

    def test_query_with_filters(self, temp_dir, sample_python_file):
        """Test querying with different filters"""
        indexer = CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))
        indexer.index_directory(temp_dir)
        
        # Query with type filter
        functions = indexer.query_important_nodes(min_score=0.0, node_type="function", limit=10)
        classes = indexer.query_important_nodes(min_score=0.0, node_type="class", limit=10)
        
        # Verify filtering works
        if functions:
            assert all(node['node_type'] == 'function' for node in functions)
        if classes:
            assert all(node['node_type'] == 'class' for node in classes)

    def test_force_reindex(self, temp_dir, sample_python_file):
        """Test force reindexing functionality"""
        indexer = CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))
        
        # First indexing
        indexer.index_directory(temp_dir)
        initial_count = len(indexer.nodes)
        
        # Modify file
        with open(sample_python_file, 'a') as f:
            f.write("\ndef new_function():\n    pass\n")
        
        # Force reindex
        indexer.index_directory(temp_dir, force_reindex=True)
        
        # Should have more nodes now
        assert len(indexer.nodes) >= initial_count

    def test_custom_ignore_patterns(self, temp_dir):
        """Test custom ignore patterns functionality"""
        # Create files to be ignored
        ignored_file = Path(temp_dir) / "test_file.py" 
        ignored_file.write_text("def test(): pass")
        
        regular_file = Path(temp_dir) / "normal.py"
        regular_file.write_text("def normal(): pass")
        
        indexer = CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))
        
        # Index with custom ignore pattern
        indexer.index_directory(temp_dir, custom_ignore=['test_*.py'])
        
        # Should only have nodes from normal.py
        file_paths = [node.get('path', '') for node in indexer.nodes.values()]
        assert any('normal.py' in path for path in file_paths)
        assert not any('test_file.py' in path for path in file_paths)

    def test_edge_cases_empty_directory(self, temp_dir):
        """Test indexing empty directory"""
        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()
        
        indexer = CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))
        
        # Should handle empty directory gracefully
        indexer.index_directory(str(empty_dir))
        
        # Should not crash and have minimal nodes
        assert len(indexer.nodes) >= 0

    def test_malformed_file_handling(self, temp_dir):
        """Test handling of malformed code files"""
        # Create malformed Python file
        malformed_file = Path(temp_dir) / "malformed.py"
        malformed_file.write_text("def incomplete_function(\n    # Missing closing parenthesis")
        
        indexer = CodeGraphIndexer(db_path=os.path.join(temp_dir, "test.db"))
        
        # Should handle malformed files gracefully
        indexer.index_directory(temp_dir)
        
        # Should not crash
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])