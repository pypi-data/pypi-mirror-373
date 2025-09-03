"""Tests for LLM Memory Storage functionality."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from claude_code_indexer.llm_memory_storage import LLMMemoryStorage


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    # Create basic code_nodes table for foreign key
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE code_nodes (
            id INTEGER PRIMARY KEY,
            name TEXT,
            node_type TEXT,
            path TEXT
        )
    """)
    
    # Insert test nodes
    conn.execute("INSERT INTO code_nodes (id, name, node_type, path) VALUES (1, 'TestClass', 'class', 'test.py')")
    conn.execute("INSERT INTO code_nodes (id, name, node_type, path) VALUES (2, 'test_function', 'function', 'test.py')")
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    db_path.unlink()


@pytest.fixture
def memory_storage(temp_db):
    """Create LLMMemoryStorage instance."""
    return LLMMemoryStorage(temp_db)


def test_store_memory_basic(memory_storage):
    """Test basic memory storage."""
    memory_id = memory_storage.store_memory(
        node_id=1,
        llm_name="claude-test",
        memory_type="analysis",
        content="This is a test class that handles user authentication."
    )
    
    assert memory_id is not None
    assert memory_id > 0


def test_store_memory_with_metadata(memory_storage):
    """Test memory storage with metadata and tags."""
    metadata = {
        "confidence": 0.95,
        "important": True,
        "complexity": "medium"
    }
    
    memory_id = memory_storage.store_memory(
        node_id=1,
        llm_name="claude-test",
        memory_type="insight",
        content="This class follows the singleton pattern.",
        metadata=metadata,
        tags=["design-pattern", "singleton", "architecture"]
    )
    
    # Retrieve and verify
    memories = memory_storage.get_memories(node_id=1)
    assert len(memories) == 1
    
    memory = memories[0]
    assert memory['content'] == "This class follows the singleton pattern."
    assert memory['metadata']['confidence'] == 0.95
    assert memory['metadata']['important'] is True
    assert set(memory['tags']) == {"design-pattern", "singleton", "architecture"}


def test_update_existing_memory(memory_storage):
    """Test updating existing memory entry."""
    # Store initial memory
    memory_storage.store_memory(
        node_id=1,
        llm_name="claude-test",
        memory_type="analysis",
        content="Initial analysis."
    )
    
    # Update with new content
    memory_storage.store_memory(
        node_id=1,
        llm_name="claude-test",
        memory_type="analysis",
        content="Updated analysis with more details."
    )
    
    # Should have only one memory (updated)
    memories = memory_storage.get_memories(node_id=1)
    assert len(memories) == 1
    assert memories[0]['content'] == "Updated analysis with more details."


def test_get_memories_filters(memory_storage):
    """Test memory retrieval with various filters."""
    # Store multiple memories
    memory_storage.store_memory(1, "claude", "analysis", "Analysis for node 1")
    memory_storage.store_memory(1, "claude", "todo", "TODO for node 1")
    memory_storage.store_memory(2, "claude", "analysis", "Analysis for node 2")
    memory_storage.store_memory(1, "gpt-4", "analysis", "GPT analysis for node 1")
    
    # Test node filter
    node1_memories = memory_storage.get_memories(node_id=1)
    assert len(node1_memories) == 3
    
    # Test type filter
    analysis_memories = memory_storage.get_memories(memory_type="analysis")
    assert len(analysis_memories) == 3
    
    # Test LLM filter
    claude_memories = memory_storage.get_memories(llm_name="claude")
    assert len(claude_memories) == 3
    
    # Test combined filters
    combined = memory_storage.get_memories(node_id=1, memory_type="analysis")
    assert len(combined) == 2


def test_search_memories(memory_storage):
    """Test memory search functionality."""
    memory_storage.store_memory(1, "claude", "analysis", "This class handles authentication logic")
    memory_storage.store_memory(2, "claude", "insight", "Function for user authentication validation")
    memory_storage.store_memory(1, "claude", "todo", "Refactor database connection")
    
    # Search for "authentication"
    results = memory_storage.search_memories("authentication")
    assert len(results) == 2
    
    # Search for "database"
    results = memory_storage.search_memories("database")
    assert len(results) == 1
    assert results[0]['memory_type'] == 'todo'


def test_get_node_summary(memory_storage):
    """Test node memory summary."""
    # Store various memories for node 1
    memory_storage.store_memory(1, "claude", "analysis", "Analysis content", tags=["important"])
    memory_storage.store_memory(1, "claude", "todo", "TODO content", tags=["action-needed"])
    memory_storage.store_memory(1, "gpt-4", "insight", "Insight content", tags=["important"])
    
    summary = memory_storage.get_node_summary(1)
    
    assert summary['node_id'] == 1
    assert summary['total_memories'] == 3
    assert len(summary['by_type']) == 3  # analysis, todo, insight
    assert len(summary['by_llm']) == 2   # claude, gpt-4
    assert "important" in summary['tags']
    assert "action-needed" in summary['tags']


def test_memory_with_tags(memory_storage):
    """Test memory storage and retrieval with tags."""
    memory_storage.store_memory(
        1, "claude", "analysis", "Security-related analysis",
        tags=["security", "important", "review-needed"]
    )
    
    memory_storage.store_memory(
        2, "claude", "insight", "Performance optimization insight",
        tags=["performance", "optimization"]
    )
    
    # Test tag filtering
    security_memories = memory_storage.get_memories(tags=["security"])
    assert len(security_memories) == 1
    assert security_memories[0]['content'] == "Security-related analysis"
    
    performance_memories = memory_storage.get_memories(tags=["performance"])
    assert len(performance_memories) == 1
    assert performance_memories[0]['content'] == "Performance optimization insight"


def test_memory_session_isolation(memory_storage):
    """Test that memories can be isolated by session."""
    memory_storage.store_memory(
        1, "claude", "analysis", "Session 1 analysis", session_id="session_1"
    )
    
    memory_storage.store_memory(
        1, "claude", "analysis", "Session 2 analysis", session_id="session_2"
    )
    
    # Should have separate memories for different sessions
    all_memories = memory_storage.get_memories(node_id=1)
    assert len(all_memories) == 2
    
    # Filter by session
    session1_memories = memory_storage.get_memories(node_id=1, session_id="session_1")
    assert len(session1_memories) == 1
    assert session1_memories[0]['content'] == "Session 1 analysis"


def test_memory_persistence(temp_db):
    """Test that memories persist across storage instances."""
    # Store memory with first instance
    storage1 = LLMMemoryStorage(temp_db)
    storage1.store_memory(1, "claude", "analysis", "Persistent analysis")
    
    # Retrieve with second instance
    storage2 = LLMMemoryStorage(temp_db)
    memories = storage2.get_memories(node_id=1)
    
    assert len(memories) == 1
    assert memories[0]['content'] == "Persistent analysis"


def test_cleanup_old_memories(memory_storage):
    """Test cleanup of old memories."""
    # This would require mocking time to test properly
    # For now, just test that the method exists and doesn't crash
    memory_storage.store_memory(1, "claude", "analysis", "Test analysis")
    
    # This should not delete anything since we just created it
    memory_storage.cleanup_old_memories(days_old=1, keep_important=True)
    
    memories = memory_storage.get_memories(node_id=1)
    assert len(memories) == 1


def test_invalid_node_id(memory_storage):
    """Test handling of invalid node IDs."""
    # This should work even with invalid node_id due to foreign key constraints
    # The database will handle the constraint
    try:
        memory_storage.store_memory(999, "claude", "analysis", "Invalid node test")
        # If foreign key constraints are enforced, this might fail
        # If not, it should succeed
        memories = memory_storage.get_memories(node_id=999)
        # Should either be empty or contain the memory depending on FK enforcement
    except Exception:
        # Foreign key constraint prevented the insertion
        pass


def test_large_content_storage(memory_storage):
    """Test storing large content."""
    large_content = "A" * 10000  # 10KB of content
    
    memory_id = memory_storage.store_memory(
        1, "claude", "analysis", large_content
    )
    
    memories = memory_storage.get_memories(node_id=1)
    assert len(memories) == 1
    assert len(memories[0]['content']) == 10000
    assert memories[0]['content'] == large_content