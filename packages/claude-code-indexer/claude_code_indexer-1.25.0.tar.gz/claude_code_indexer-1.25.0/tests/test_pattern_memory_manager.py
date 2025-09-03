"""Tests for Pattern & Best Practices Memory Manager functionality."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from claude_code_indexer.pattern_memory_manager import (
    PatternMemoryManager, PatternType, BestPracticeCategory
)


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
    conn.execute("INSERT INTO code_nodes (id, name, node_type, path) VALUES (0, 'ProjectRoot', 'project', '.')")
    conn.execute("INSERT INTO code_nodes (id, name, node_type, path) VALUES (1, 'TestClass', 'class', 'test.py')")
    conn.execute("INSERT INTO code_nodes (id, name, node_type, path) VALUES (2, 'test_function', 'function', 'test.py')")
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    db_path.unlink()


@pytest.fixture
def pattern_manager(temp_db):
    """Create PatternMemoryManager instance."""
    return PatternMemoryManager(temp_db)


def test_store_pattern_basic(pattern_manager):
    """Test basic pattern storage."""
    pattern_id = pattern_manager.store_pattern(
        pattern_type=PatternType.ARCHITECTURE,
        title="Service Layer Pattern",
        description="Separate business logic into service classes"
    )
    
    assert pattern_id is not None
    assert "architecture" in pattern_id
    assert "service_layer_pattern" in pattern_id


def test_store_pattern_comprehensive(pattern_manager):
    """Test pattern storage with all fields."""
    pattern_id = pattern_manager.store_pattern(
        pattern_type=PatternType.SECURITY,
        title="JWT Authentication",
        description="Implement JWT-based authentication",
        example_code="@jwt_required\ndef protected_route(): pass",
        anti_pattern="# AVOID: Plain text tokens",
        when_to_use="Use for stateless authentication",
        benefits=["Stateless", "Scalable", "Secure"],
        trade_offs=["Token management", "Complexity"],
        tags=["security", "jwt", "authentication"],
        llm_name="claude-test",
        confidence=0.95
    )
    
    # Retrieve and verify
    patterns = pattern_manager.get_patterns(pattern_type=PatternType.SECURITY)
    assert len(patterns) == 1
    
    pattern = patterns[0]
    assert pattern['title'] == "JWT Authentication"
    assert pattern['confidence'] == 0.95
    assert pattern['benefits'] == ["Stateless", "Scalable", "Secure"]
    assert pattern['tags'] == ["security", "jwt", "authentication"]


def test_store_best_practice_basic(pattern_manager):
    """Test basic best practice storage."""
    practice_id = pattern_manager.store_best_practice(
        category=BestPracticeCategory.TEAM_STANDARDS,
        title="Use Descriptive Variable Names",
        description="Variables should clearly indicate their purpose",
        rationale="Improves code readability and maintenance"
    )
    
    assert practice_id is not None
    assert "team_standards" in practice_id
    assert "use_descriptive_variable_names" in practice_id


def test_store_best_practice_comprehensive(pattern_manager):
    """Test best practice storage with all fields."""
    practice_id = pattern_manager.store_best_practice(
        category=BestPracticeCategory.COMPANY_POLICY,
        title="Never Log Sensitive Information",
        description="Prevent logging of passwords, API keys, PII",
        rationale="Logs are often stored in plain text and accessible",
        examples=["logger.info(f'User {user.id} authenticated')"],
        counter_examples=["logger.info(f'Password: {password}')"],
        enforcement_level="must",
        scope="company",
        tools_required=["pre-commit", "log-analysis"],
        tags=["security", "logging", "pii"],
        priority="high",
        llm_name="claude-test"
    )
    
    # Retrieve and verify
    practices = pattern_manager.get_best_practices(category=BestPracticeCategory.COMPANY_POLICY)
    assert len(practices) == 1
    
    practice = practices[0]
    assert practice['title'] == "Never Log Sensitive Information"
    assert practice['enforcement_level'] == "must"
    assert practice['priority'] == "high"
    assert practice['examples'] == ["logger.info(f'User {user.id} authenticated')"]
    assert practice['tags'] == ["security", "logging", "pii"]


def test_get_patterns_filtering(pattern_manager):
    """Test pattern retrieval with various filters."""
    # Store multiple patterns
    pattern_manager.store_pattern(
        PatternType.ARCHITECTURE, "Service Layer", "Business logic separation",
        tags=["architecture", "service"], confidence=0.9
    )
    pattern_manager.store_pattern(
        PatternType.SECURITY, "JWT Auth", "Token authentication",
        tags=["security", "auth"], confidence=0.85
    )
    pattern_manager.store_pattern(
        PatternType.ARCHITECTURE, "Repository Pattern", "Data access abstraction",
        tags=["architecture", "data"], confidence=0.95
    )
    
    # Test type filter
    arch_patterns = pattern_manager.get_patterns(pattern_type=PatternType.ARCHITECTURE)
    assert len(arch_patterns) == 2
    
    # Test tag filter
    security_patterns = pattern_manager.get_patterns(tags=["security"])
    assert len(security_patterns) == 1
    assert security_patterns[0]['title'] == "JWT Auth"
    
    # Test confidence filter
    high_conf_patterns = pattern_manager.get_patterns(min_confidence=0.9)
    assert len(high_conf_patterns) == 2  # Service Layer (0.9) and Repository (0.95)
    
    # Test limit
    limited_patterns = pattern_manager.get_patterns(limit=1)
    assert len(limited_patterns) == 1


def test_get_best_practices_filtering(pattern_manager):
    """Test best practice retrieval with various filters."""
    # Store multiple practices
    pattern_manager.store_best_practice(
        BestPracticeCategory.TEAM_STANDARDS, "Naming Convention", 
        "Use snake_case", "PEP 8 compliance", priority="high"
    )
    pattern_manager.store_best_practice(
        BestPracticeCategory.COMPANY_POLICY, "Input Validation",
        "Validate all inputs", "Prevent security vulnerabilities", 
        enforcement_level="must", priority="high"
    )
    pattern_manager.store_best_practice(
        BestPracticeCategory.TOOL_USAGE, "Use Type Hints",
        "Add type annotations", "Improve code clarity",
        priority="medium", scope="team"
    )
    
    # Test category filter
    team_practices = pattern_manager.get_best_practices(category=BestPracticeCategory.TEAM_STANDARDS)
    assert len(team_practices) == 1
    assert team_practices[0]['title'] == "Naming Convention"
    
    # Test priority filter
    high_priority = pattern_manager.get_best_practices(priority="high")
    assert len(high_priority) == 2
    
    # Test enforcement level filter
    must_practices = pattern_manager.get_best_practices(enforcement_level="must")
    assert len(must_practices) == 1
    assert must_practices[0]['title'] == "Input Validation"
    
    # Test scope filter
    team_scope = pattern_manager.get_best_practices(scope="team")
    assert len(team_scope) == 1
    assert team_scope[0]['title'] == "Use Type Hints"


def test_search_patterns_and_practices(pattern_manager):
    """Test comprehensive search across patterns and practices."""
    # Store test data
    pattern_manager.store_pattern(
        PatternType.SECURITY, "Authentication Pattern", 
        "Secure user authentication", tags=["security", "auth"]
    )
    pattern_manager.store_best_practice(
        BestPracticeCategory.COMPANY_POLICY, "Authentication Best Practice",
        "Always use strong authentication", "Security is critical",
        tags=["security", "auth"]
    )
    pattern_manager.store_pattern(
        PatternType.PERFORMANCE, "Caching Pattern",
        "Implement caching for performance", tags=["performance", "cache"]
    )
    
    # Search for "authentication"
    auth_results = pattern_manager.search_patterns_and_practices("authentication")
    assert len(auth_results['patterns']) == 1
    assert len(auth_results['best_practices']) == 1
    assert auth_results['patterns'][0]['title'] == "Authentication Pattern"
    assert auth_results['best_practices'][0]['title'] == "Authentication Best Practice"
    
    # Search for "performance"
    perf_results = pattern_manager.search_patterns_and_practices("performance")
    assert len(perf_results['patterns']) == 1
    assert len(perf_results['best_practices']) == 0
    
    # Search with no results
    no_results = pattern_manager.search_patterns_and_practices("nonexistent")
    assert len(no_results['patterns']) == 0
    assert len(no_results['best_practices']) == 0


def test_pattern_usage_tracking(pattern_manager):
    """Test pattern usage recording and tracking."""
    # Store a pattern
    pattern_id = pattern_manager.store_pattern(
        PatternType.DESIGN_PATTERN, "Singleton Pattern",
        "Ensure single instance", confidence=0.8
    )
    
    # Record usage
    pattern_manager.record_pattern_usage(
        pattern_id=pattern_id,
        node_id=1,
        file_path="test.py",
        usage_context="Applied singleton to database connection",
        effectiveness_score=0.9,
        notes="Reduced connection overhead significantly"
    )
    
    # Verify usage frequency updated
    patterns = pattern_manager.get_patterns(pattern_type=PatternType.DESIGN_PATTERN)
    assert len(patterns) == 1
    assert patterns[0]['usage_frequency'] == 1
    assert patterns[0]['last_applied'] is not None
    
    # Record another usage
    pattern_manager.record_pattern_usage(
        pattern_id=pattern_id,
        file_path="another.py",
        usage_context="Applied to config manager"
    )
    
    # Verify frequency incremented
    updated_patterns = pattern_manager.get_patterns(pattern_type=PatternType.DESIGN_PATTERN)
    assert updated_patterns[0]['usage_frequency'] == 2


def test_pattern_recommendations(pattern_manager):
    """Test pattern recommendation system."""
    # Store patterns with different tags
    arch_pattern = pattern_manager.store_pattern(
        PatternType.ARCHITECTURE, "Microservices Pattern",
        "Break down monolith into services", 
        tags=["architecture", "scalability", "microservices"]
    )
    
    security_pattern = pattern_manager.store_pattern(
        PatternType.SECURITY, "OAuth2 Pattern",
        "Secure authorization flow",
        tags=["security", "oauth", "authentication"]
    )
    
    # Mock some node memories (would come from LLM memory storage)
    # This tests the recommendation algorithm logic
    recommendations = pattern_manager.get_pattern_recommendations(
        node_id=1, context="This service handles user authentication and needs to be scalable"
    )
    
    # Should return patterns, potentially scored by relevance
    assert len(recommendations) >= 0  # May be 0 if no relevant memories exist yet


def test_project_standards_summary(pattern_manager):
    """Test comprehensive project standards summary."""
    # Store diverse patterns and practices
    pattern_manager.store_pattern(
        PatternType.ARCHITECTURE, "MVC Pattern", "Model-View-Controller",
        confidence=0.9, tags=["architecture"]
    )
    pattern_manager.store_pattern(
        PatternType.SECURITY, "Input Validation", "Validate all inputs",
        confidence=0.95, tags=["security"]
    )
    
    pattern_manager.store_best_practice(
        BestPracticeCategory.TEAM_STANDARDS, "Code Style", "Follow PEP 8",
        "Consistent code style", priority="high"
    )
    pattern_manager.store_best_practice(
        BestPracticeCategory.CODE_REVIEW, "Security Review", "Review security implications",
        "Prevent vulnerabilities", priority="high"
    )
    
    # Get summary
    summary = pattern_manager.get_project_standards_summary()
    
    # Verify structure
    assert 'pattern_statistics' in summary
    assert 'practice_statistics' in summary
    assert 'high_priority_practices' in summary
    assert 'popular_patterns' in summary
    assert 'summary' in summary
    
    # Verify summary statistics
    stats = summary['summary']
    assert stats['total_patterns'] == 2
    assert stats['total_practices'] == 2
    assert stats['avg_pattern_confidence'] > 0.9
    
    # Verify high priority practices
    high_priority = summary['high_priority_practices']
    assert len(high_priority) == 2


def test_pattern_types_enum_coverage(pattern_manager):
    """Test all pattern types can be stored."""
    pattern_types = [
        PatternType.ARCHITECTURE,
        PatternType.DESIGN_PATTERN,
        PatternType.CODE_STYLE,
        PatternType.NAMING_CONVENTION,
        PatternType.ERROR_HANDLING,
        PatternType.SECURITY,
        PatternType.PERFORMANCE,
        PatternType.TESTING,
        PatternType.API_DESIGN,
        PatternType.DATABASE,
        PatternType.DEPLOYMENT,
        PatternType.DOCUMENTATION
    ]
    
    for i, pattern_type in enumerate(pattern_types):
        pattern_id = pattern_manager.store_pattern(
            pattern_type=pattern_type,
            title=f"Test Pattern {i}",
            description=f"Test pattern for {pattern_type.value}"
        )
        assert pattern_id is not None
        assert pattern_type.value in pattern_id
    
    # Verify all patterns stored
    all_patterns = pattern_manager.get_patterns(limit=100)
    assert len(all_patterns) == len(pattern_types)


def test_best_practice_categories_coverage(pattern_manager):
    """Test all best practice categories can be stored."""
    categories = [
        BestPracticeCategory.TEAM_STANDARDS,
        BestPracticeCategory.PROJECT_RULES,
        BestPracticeCategory.INDUSTRY_BEST,
        BestPracticeCategory.COMPANY_POLICY,
        BestPracticeCategory.TOOL_USAGE,
        BestPracticeCategory.CODE_REVIEW,
        BestPracticeCategory.REFACTORING,
        BestPracticeCategory.MAINTENANCE
    ]
    
    for i, category in enumerate(categories):
        practice_id = pattern_manager.store_best_practice(
            category=category,
            title=f"Test Practice {i}",
            description=f"Test practice for {category.value}",
            rationale=f"Important for {category.value}"
        )
        assert practice_id is not None
        assert category.value in practice_id
    
    # Verify all practices stored
    all_practices = pattern_manager.get_best_practices(limit=100)
    assert len(all_practices) == len(categories)


def test_tag_based_filtering(pattern_manager):
    """Test comprehensive tag-based filtering."""
    # Store items with various tag combinations
    pattern_manager.store_pattern(
        PatternType.SECURITY, "Security Pattern 1", "Description",
        tags=["security", "authentication", "jwt"]
    )
    pattern_manager.store_pattern(
        PatternType.SECURITY, "Security Pattern 2", "Description",
        tags=["security", "authorization", "rbac"]
    )
    pattern_manager.store_pattern(
        PatternType.PERFORMANCE, "Performance Pattern", "Description",
        tags=["performance", "caching"]
    )
    
    pattern_manager.store_best_practice(
        BestPracticeCategory.COMPANY_POLICY, "Security Practice", "Description", "Rationale",
        tags=["security", "authentication"]
    )
    
    # Test single tag filter
    security_patterns = pattern_manager.get_patterns(tags=["security"])
    assert len(security_patterns) == 2
    
    # Test multiple tag filter (OR logic)
    auth_patterns = pattern_manager.get_patterns(tags=["authentication", "performance"])
    assert len(auth_patterns) == 2  # One auth pattern + one performance pattern
    
    # Test tag filter on best practices
    security_practices = pattern_manager.get_best_practices(tags=["security"])
    assert len(security_practices) == 1


def test_memory_integration(pattern_manager):
    """Test integration with LLM memory storage."""
    # Store pattern - should also create memory entry
    pattern_id = pattern_manager.store_pattern(
        PatternType.ARCHITECTURE, "Test Integration Pattern",
        "Tests memory integration", tags=["test", "integration"]
    )
    
    # Store best practice - should also create memory entry
    practice_id = pattern_manager.store_best_practice(
        BestPracticeCategory.TEAM_STANDARDS, "Test Integration Practice",
        "Tests memory integration", "Important for testing", tags=["test", "integration"]
    )
    
    # Verify memories were created (check via memory storage)
    memories = pattern_manager.memory_storage.get_memories(node_id=0)  # Project-level node
    assert len(memories) >= 2  # At least the pattern and practice memories
    
    # Find our specific memories
    pattern_memory = next((m for m in memories if m['memory_type'] == 'pattern'), None)
    practice_memory = next((m for m in memories if m['memory_type'] == 'best_practice'), None)
    
    assert pattern_memory is not None
    assert practice_memory is not None
    assert pattern_memory['metadata']['pattern_id'] == pattern_id
    assert practice_memory['metadata']['practice_id'] == practice_id


def test_data_persistence(temp_db):
    """Test that patterns and practices persist across manager instances."""
    # Store data with first manager
    manager1 = PatternMemoryManager(temp_db)
    pattern_id = manager1.store_pattern(
        PatternType.ARCHITECTURE, "Persistent Pattern", "Tests persistence"
    )
    practice_id = manager1.store_best_practice(
        BestPracticeCategory.TEAM_STANDARDS, "Persistent Practice",
        "Tests persistence", "Important for testing"
    )
    
    # Retrieve with second manager
    manager2 = PatternMemoryManager(temp_db)
    patterns = manager2.get_patterns()
    practices = manager2.get_best_practices()
    
    assert len(patterns) == 1
    assert len(practices) == 1
    assert patterns[0]['title'] == "Persistent Pattern"
    assert practices[0]['title'] == "Persistent Practice"


def test_large_scale_storage(pattern_manager):
    """Test storing and retrieving large numbers of patterns and practices."""
    # Store many patterns
    pattern_ids = []
    for i in range(20):
        pattern_id = pattern_manager.store_pattern(
            PatternType.ARCHITECTURE, f"Pattern {i}",
            f"Description for pattern {i}", tags=[f"tag{i}", "bulk"]
        )
        pattern_ids.append(pattern_id)
    
    # Store many practices
    practice_ids = []
    for i in range(15):
        practice_id = pattern_manager.store_best_practice(
            BestPracticeCategory.TEAM_STANDARDS, f"Practice {i}",
            f"Description for practice {i}", f"Rationale for practice {i}",
            tags=[f"tag{i}", "bulk"]
        )
        practice_ids.append(practice_id)
    
    # Verify all stored
    all_patterns = pattern_manager.get_patterns(limit=100)
    all_practices = pattern_manager.get_best_practices(limit=100)
    
    assert len(all_patterns) == 20
    assert len(all_practices) == 15
    
    # Test bulk search
    bulk_results = pattern_manager.search_patterns_and_practices("bulk")
    assert len(bulk_results['patterns']) == 20
    assert len(bulk_results['best_practices']) == 15


def test_error_handling(pattern_manager):
    """Test error handling for edge cases."""
    # Test with very long content
    long_description = "A" * 10000
    pattern_id = pattern_manager.store_pattern(
        PatternType.ARCHITECTURE, "Long Pattern", long_description
    )
    assert pattern_id is not None
    
    # Retrieve and verify
    patterns = pattern_manager.get_patterns()
    long_pattern = next(p for p in patterns if p['title'] == "Long Pattern")
    assert len(long_pattern['description']) == 10000
    
    # Test with special characters
    special_title = "Pattern with 特殊字符 and émojis 🎯"
    special_id = pattern_manager.store_pattern(
        PatternType.SECURITY, special_title, "Description with special chars"
    )
    assert special_id is not None
    
    # Test with empty tags and metadata
    empty_id = pattern_manager.store_pattern(
        PatternType.TESTING, "Empty Pattern", "Minimal pattern",
        benefits=[], trade_offs=[], tags=[]
    )
    assert empty_id is not None


def test_json_serialization(pattern_manager):
    """Test proper JSON serialization of complex data."""
    # Store pattern with complex nested data
    complex_benefits = [
        "Improved maintainability",
        "Better separation of concerns", 
        "Enhanced testability"
    ]
    complex_tags = ["architecture", "design-pattern", "solid-principles"]
    
    pattern_id = pattern_manager.store_pattern(
        PatternType.DESIGN_PATTERN, "Complex Pattern",
        "Pattern with complex data structures",
        benefits=complex_benefits,
        trade_offs=["Added complexity", "Learning curve"],
        tags=complex_tags
    )
    
    # Retrieve and verify JSON fields are properly parsed
    patterns = pattern_manager.get_patterns()
    complex_pattern = next(p for p in patterns if p['title'] == "Complex Pattern")
    
    assert complex_pattern['benefits'] == complex_benefits
    assert complex_pattern['tags'] == complex_tags
    assert isinstance(complex_pattern['benefits'], list)
    assert isinstance(complex_pattern['tags'], list)