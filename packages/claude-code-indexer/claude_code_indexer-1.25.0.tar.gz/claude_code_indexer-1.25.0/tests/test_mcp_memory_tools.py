"""Tests for MCP LLM Memory tools."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from claude_code_indexer.mcp_server import (
    store_llm_memory, get_llm_memories, search_llm_memories, 
    get_node_memory_summary, project_manager
)


@pytest.fixture
def temp_project():
    """Create a temporary project with indexed code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create a test Python file
        test_file = project_path / "test_module.py"
        test_file.write_text("""
class TestClass:
    def test_method(self):
        return "test"

def test_function():
    return "function"
""")
        
        # Index the project
        indexer = project_manager.get_indexer(str(project_path))
        indexer.index_directory(str(project_path))
        
        # Get node IDs for testing
        important_nodes = indexer.query_important_nodes(limit=10)
        
        yield str(project_path), [node['id'] for node in important_nodes]


def test_store_llm_memory_basic(temp_project):
    """Test basic memory storage via MCP tool."""
    project_path, node_ids = temp_project
    
    if not node_ids:
        pytest.skip("No nodes found in indexed project")
    
    result = store_llm_memory(
        project_path=project_path,
        node_id=node_ids[0],
        memory_type="analysis",
        content="This is a test analysis of the code structure.",
        llm_name="test-claude"
    )
    
    assert "✅ Memory stored successfully" in result
    assert "analysis" in result
    assert "test-claude" in result


def test_store_llm_memory_with_metadata_and_tags(temp_project):
    """Test memory storage with metadata and tags."""
    project_path, node_ids = temp_project
    
    if not node_ids:
        pytest.skip("No nodes found in indexed project")
    
    result = store_llm_memory(
        project_path=project_path,
        node_id=node_ids[0],
        memory_type="insight",
        content="Security consideration: This code needs input validation.",
        llm_name="test-claude",
        metadata={"priority": "high", "confidence": 0.9},
        tags=["security", "validation", "high-priority"]
    )
    
    assert "✅ Memory stored successfully" in result
    assert "insight" in result
    assert "security, validation, high-priority" in result


def test_get_llm_memories(temp_project):
    """Test memory retrieval via MCP tool."""
    project_path, node_ids = temp_project
    
    if not node_ids:
        pytest.skip("No nodes found in indexed project")
    
    # Store a memory first
    store_llm_memory(
        project_path=project_path,
        node_id=node_ids[0],
        memory_type="todo",
        content="TODO: Add error handling to this function.",
        tags=["error-handling", "improvement"]
    )
    
    # Retrieve memories
    result = get_llm_memories(
        project_path=project_path,
        node_id=node_ids[0]
    )
    
    assert "🧠 Found" in result
    assert "TODO: Add error handling" in result
    assert "error-handling, improvement" in result


def test_get_llm_memories_by_type(temp_project):
    """Test memory retrieval filtered by type."""
    project_path, node_ids = temp_project
    
    if not node_ids:
        pytest.skip("No nodes found in indexed project")
    
    # Store different types of memories
    store_llm_memory(project_path, node_ids[0], "analysis", "Analysis content")
    store_llm_memory(project_path, node_ids[0], "warning", "Warning content")
    
    # Get only warnings
    result = get_llm_memories(
        project_path=project_path,
        memory_type="warning"
    )
    
    assert "Warning content" in result
    assert "Analysis content" not in result


def test_search_llm_memories(temp_project):
    """Test memory search functionality."""
    project_path, node_ids = temp_project
    
    if not node_ids:
        pytest.skip("No nodes found in indexed project")
    
    # Store memories with searchable content
    store_llm_memory(project_path, node_ids[0], "analysis", "This function handles authentication logic")
    if len(node_ids) > 1:
        store_llm_memory(project_path, node_ids[1], "insight", "Performance bottleneck in database queries")
    
    # Search for "authentication"
    result = search_llm_memories(
        project_path=project_path,
        search_term="authentication"
    )
    
    assert "🔍 Found" in result
    assert "authentication logic" in result


def test_get_node_memory_summary(temp_project):
    """Test node memory summary functionality."""
    project_path, node_ids = temp_project
    
    if not node_ids:
        pytest.skip("No nodes found in indexed project")
    
    node_id = node_ids[0]
    
    # Store multiple memories for the node
    store_llm_memory(project_path, node_id, "analysis", "Architectural analysis")
    store_llm_memory(project_path, node_id, "todo", "Performance TODO")
    store_llm_memory(project_path, node_id, "warning", "Security warning")
    
    # Get summary
    result = get_node_memory_summary(
        project_path=project_path,
        node_id=node_id
    )
    
    assert "🧠 Memory Summary" in result
    assert "Total memories: 3" in result
    assert "analysis: 1 entries" in result
    assert "todo: 1 entries" in result
    assert "warning: 1 entries" in result


def test_memory_update_existing(temp_project):
    """Test that storing memory with same type updates existing entry."""
    project_path, node_ids = temp_project
    
    if not node_ids:
        pytest.skip("No nodes found in indexed project")
    
    node_id = node_ids[0]
    
    # Store initial memory
    store_llm_memory(project_path, node_id, "analysis", "Initial analysis")
    
    # Update with new content
    store_llm_memory(project_path, node_id, "analysis", "Updated analysis with more details")
    
    # Should have only one memory (updated)
    result = get_llm_memories(project_path=project_path, node_id=node_id)
    
    assert "Updated analysis with more details" in result
    assert "Initial analysis" not in result
    assert result.count("[ANALYSIS]") == 1  # Only one analysis entry


def test_invalid_project_path():
    """Test handling of invalid project paths."""
    result = store_llm_memory(
        project_path="/nonexistent/path",
        node_id=1,
        memory_type="analysis", 
        content="Test"
    )
    
    assert "❌ Project path does not exist" in result


def test_empty_memories_response(temp_project):
    """Test response when no memories exist."""
    project_path, node_ids = temp_project
    
    # Try to get memories for non-existent node
    result = get_llm_memories(
        project_path=project_path,
        node_id=99999
    )
    
    assert "ℹ️ No memories found" in result


def test_search_no_results(temp_project):
    """Test search with no matching results."""
    project_path, node_ids = temp_project
    
    result = search_llm_memories(
        project_path=project_path,
        search_term="nonexistent_term_xyz"
    )
    
    assert "ℹ️ No memories found containing" in result
    assert "nonexistent_term_xyz" in result


def test_memory_with_special_characters(temp_project):
    """Test memory storage with special characters and formatting."""
    project_path, node_ids = temp_project
    
    if not node_ids:
        pytest.skip("No nodes found in indexed project")
    
    special_content = """
    This analysis contains:
    - Special chars: "quotes", 'apostrophes', & symbols
    - Code examples: `function()` and ```python\nprint("hello")\n```
    - Unicode: 🔒 security issue, ⚡ performance
    """
    
    result = store_llm_memory(
        project_path=project_path,
        node_id=node_ids[0],
        memory_type="analysis",
        content=special_content
    )
    
    assert "✅ Memory stored successfully" in result
    
    # Retrieve and verify
    memories = get_llm_memories(project_path=project_path, node_id=node_ids[0])
    assert "Special chars" in memories
    assert "🔒 security" in memories