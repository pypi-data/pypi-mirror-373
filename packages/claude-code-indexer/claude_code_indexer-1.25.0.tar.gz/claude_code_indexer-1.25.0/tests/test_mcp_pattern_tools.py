"""Tests for MCP Pattern & Best Practices Tools functionality."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from claude_code_indexer.mcp_server import (
    store_coding_pattern, store_best_practice, get_coding_patterns,
    get_best_practices, search_patterns_and_practices, get_project_standards_summary
)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with database."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        db_path = project_path / ".claude_code_indexer" / "code_graph.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create basic database structure
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE code_nodes (
                id INTEGER PRIMARY KEY,
                name TEXT,
                node_type TEXT,
                path TEXT
            )
        """)
        conn.execute("INSERT INTO code_nodes (id, name, node_type, path) VALUES (0, 'ProjectRoot', 'project', '.')")
        conn.execute("INSERT INTO code_nodes (id, name, node_type, path) VALUES (1, 'TestClass', 'class', 'test.py')")
        conn.commit()
        conn.close()
        
        yield str(project_path)


def test_store_coding_pattern_basic(temp_project_dir):
    """Test basic coding pattern storage via MCP tool."""
    result = store_coding_pattern(
        project_path=temp_project_dir,
        pattern_type="architecture",
        title="Service Layer Pattern",
        description="Separate business logic into service classes"
    )
    
    assert isinstance(result, str)
    assert "✅ Coding pattern stored successfully" in result
    assert "Service Layer Pattern" in result
    assert "architecture" in result


def test_store_coding_pattern_comprehensive(temp_project_dir):
    """Test comprehensive coding pattern storage with all parameters."""
    result = store_coding_pattern(
        project_path=temp_project_dir,
        pattern_type="security",
        title="JWT Authentication Pattern",
        description="Implement secure JWT-based authentication",
        example_code="""
@jwt_required
def protected_route():
    user_id = get_jwt_identity()
    return {'user_id': user_id}
        """,
        anti_pattern="""
# AVOID: Plain text tokens
def bad_auth():
    token = "plain_text_token"
    return token
        """,
        when_to_use="Use for stateless API authentication in microservices",
        benefits=["Stateless authentication", "Scalable across services", "Standard compliant"],
        trade_offs=["Token management complexity", "Requires secure key storage"],
        tags=["security", "jwt", "authentication", "api"],
        llm_name="claude-sonnet",
        confidence=0.92
    )
    
    assert isinstance(result, str)
    assert "✅ Coding pattern stored successfully" in result
    assert "JWT Authentication Pattern" in result
    assert "security" in result
    assert "0.92" in result
    
    # Verify storage by retrieving
    patterns = get_coding_patterns(
        project_path=temp_project_dir,
        pattern_type="security"
    )
    
    assert isinstance(patterns, str)
    assert "JWT Authentication Pattern" in patterns
    assert "security" in patterns


def test_store_best_practice_basic(temp_project_dir):
    """Test basic best practice storage via MCP tool."""
    result = store_best_practice(
        project_path=temp_project_dir,
        category="team_standards",
        title="Use Descriptive Variable Names",
        description="Variables should clearly indicate their purpose and usage",
        rationale="Improves code readability and reduces cognitive load for developers"
    )
    
    assert isinstance(result, str)
    assert "✅ Best practice stored successfully" in result
    assert "Use Descriptive Variable Names" in result
    assert "team_standards" in result


def test_store_best_practice_comprehensive(temp_project_dir):
    """Test comprehensive best practice storage with all parameters."""
    result = store_best_practice(
        project_path=temp_project_dir,
        category="company_policy",
        title="Input Validation and Sanitization",
        description="Always validate and sanitize user inputs to prevent security vulnerabilities",
        rationale="Unvalidated inputs are the primary attack vector for injection attacks",
        examples=[
            "def safe_query(user_input): return sanitize_sql(user_input)",
            "validator = EmailValidator(); validator.validate(email)",
            "cleaned_data = bleach.clean(user_html_input)"
        ],
        counter_examples=[
            "query = f'SELECT * FROM users WHERE name = {user_input}'",
            "eval(user_code_input)",
            "os.system(user_command)"
        ],
        enforcement_level="must",
        scope="company",
        tools_required=["sqlalchemy", "bleach", "validators"],
        tags=["security", "validation", "sanitization", "injection-prevention"],
        priority="high",
        llm_name="claude-opus"
    )
    
    assert isinstance(result, str)
    assert "✅ Best practice stored successfully" in result
    assert "Input Validation and Sanitization" in result
    assert "company_policy" in result
    assert "high" in result
    
    # Verify storage by retrieving
    practices = get_best_practices(
        project_path=temp_project_dir,
        category="company_policy"
    )
    
    assert isinstance(practices, str)
    assert "Input Validation and Sanitization" in practices
    assert "company_policy" in practices


def test_get_coding_patterns_filtering(temp_project_dir):
    """Test coding pattern retrieval with various filters."""
    # Store multiple patterns
    store_coding_pattern(
        temp_project_dir, "architecture", "MVC Pattern", 
        "Model-View-Controller architecture", tags=["architecture", "mvc"]
    )
    store_coding_pattern(
        temp_project_dir, "security", "OAuth2 Flow",
        "Secure authorization flow", tags=["security", "oauth"], confidence=0.95
    )
    store_coding_pattern(
        temp_project_dir, "performance", "Caching Strategy",
        "Implement effective caching", tags=["performance", "cache"], confidence=0.88
    )
    
    # Test no filters - get all
    all_patterns = get_coding_patterns(temp_project_dir)
    assert isinstance(all_patterns, str)
    assert "MVC Pattern" in all_patterns
    assert "OAuth2 Flow" in all_patterns
    assert "Caching Strategy" in all_patterns
    
    # Test pattern type filter
    arch_patterns = get_coding_patterns(temp_project_dir, pattern_type="architecture")
    assert isinstance(arch_patterns, str)
    assert "MVC Pattern" in arch_patterns
    assert "OAuth2 Flow" not in arch_patterns  # Should not be in architecture results
    
    # Test tag filter
    security_patterns = get_coding_patterns(temp_project_dir, tags=["security"])
    assert isinstance(security_patterns, str)
    assert "OAuth2 Flow" in security_patterns
    assert "MVC Pattern" not in security_patterns  # Should not be in security results
    
    # Test confidence filter
    high_conf_patterns = get_coding_patterns(temp_project_dir, min_confidence=0.9)
    assert isinstance(high_conf_patterns, str)
    assert "OAuth2 Flow" in high_conf_patterns  # 0.95 confidence
    assert "Caching Strategy" not in high_conf_patterns  # 0.88 confidence


def test_get_best_practices_filtering(temp_project_dir):
    """Test best practice retrieval with various filters."""
    # Store multiple practices
    store_best_practice(
        temp_project_dir, "team_standards", "Code Formatting",
        "Use consistent code formatting", "Improves readability", priority="medium"
    )
    store_best_practice(
        temp_project_dir, "company_policy", "Secure Headers",
        "Always use security headers", "Prevents common attacks", 
        enforcement_level="must", priority="high"
    )
    store_best_practice(
        temp_project_dir, "tool_usage", "Linting Rules",
        "Use automated linting", "Catches errors early",
        scope="team", priority="medium"
    )
    
    # Test no filters - get all
    all_practices = get_best_practices(temp_project_dir)
    assert isinstance(all_practices, str)
    assert "Code Formatting" in all_practices
    assert "Secure Headers" in all_practices
    assert "Linting Rules" in all_practices
    
    # Test category filter
    team_practices = get_best_practices(temp_project_dir, category="team_standards")
    assert isinstance(team_practices, str)
    assert "Code Formatting" in team_practices
    assert "Secure Headers" not in team_practices  # Should not be in team_standards
    
    # Test priority filter
    high_priority = get_best_practices(temp_project_dir, priority="high")
    assert isinstance(high_priority, str)
    assert "Secure Headers" in high_priority
    assert "Code Formatting" not in high_priority  # Medium priority
    
    # Test enforcement level filter
    must_practices = get_best_practices(temp_project_dir, enforcement_level="must")
    assert isinstance(must_practices, str)
    assert "Secure Headers" in must_practices
    assert "Code Formatting" not in must_practices  # Default "should"


def test_search_patterns_and_practices(temp_project_dir):
    """Test comprehensive search across patterns and practices."""
    # Store searchable content
    store_coding_pattern(
        temp_project_dir, "security", "Authentication Flow",
        "Secure user authentication process", tags=["security", "auth"]
    )
    store_best_practice(
        temp_project_dir, "company_policy", "Authentication Standards",
        "Follow authentication best practices", "Security is critical",
        tags=["security", "auth"]
    )
    store_coding_pattern(
        temp_project_dir, "performance", "Database Optimization",
        "Optimize database queries for performance", tags=["performance", "database"]
    )
    
    # Search for "authentication"
    auth_results = search_patterns_and_practices(temp_project_dir, "authentication")
    assert isinstance(auth_results, str)
    assert "Authentication Flow" in auth_results
    assert "Authentication Standards" in auth_results
    
    # Search for "database"
    db_results = search_patterns_and_practices(temp_project_dir, "database")
    assert isinstance(db_results, str)
    assert "Database Optimization" in db_results
    
    # Search with include/exclude flags
    patterns_only = search_patterns_and_practices(
        temp_project_dir, "authentication", include_practices=False
    )
    assert isinstance(patterns_only, str)
    assert "Authentication Flow" in patterns_only
    
    practices_only = search_patterns_and_practices(
        temp_project_dir, "authentication", include_patterns=False
    )
    assert isinstance(practices_only, str)
    assert "Authentication Standards" in practices_only


def test_get_project_standards_summary(temp_project_dir):
    """Test project standards summary generation."""
    # Store diverse patterns and practices
    store_coding_pattern(
        temp_project_dir, "architecture", "Microservices Pattern",
        "Service-oriented architecture", confidence=0.95
    )
    store_coding_pattern(
        temp_project_dir, "security", "HTTPS Only",
        "Always use HTTPS", confidence=0.98
    )
    
    store_best_practice(
        temp_project_dir, "team_standards", "Code Review",
        "All code must be reviewed", "Quality assurance", priority="high"
    )
    store_best_practice(
        temp_project_dir, "company_policy", "Security Testing",
        "Test for security vulnerabilities", "Prevent breaches", priority="high"
    )
    store_best_practice(
        temp_project_dir, "tool_usage", "Automated Testing",
        "Use automated test suites", "Prevent regressions", priority="medium"
    )
    
    # Get summary
    summary = get_project_standards_summary(temp_project_dir)
    
    assert isinstance(summary, str)
    assert "Project Standards Summary" in summary
    assert "Patterns" in summary
    assert "Practices" in summary
    assert "architecture" in summary  # Pattern type should be listed
    assert "Code Review" in summary


def test_invalid_project_path():
    """Test error handling for invalid project paths."""
    invalid_path = "/nonexistent/path"
    
    result = store_coding_pattern(
        invalid_path, "architecture", "Test Pattern", "Test description"
    )
    assert isinstance(result, str)
    assert "❌" in result
    assert "does not exist" in result
    
    result = get_coding_patterns(invalid_path)
    assert isinstance(result, str)
    assert "❌" in result


def test_invalid_enum_values(temp_project_dir):
    """Test error handling for invalid enum values."""
    # Test invalid pattern type
    result = store_coding_pattern(
        temp_project_dir, "invalid_type", "Test Pattern", "Test description"
    )
    assert isinstance(result, str)
    assert "❌" in result
    assert "Invalid pattern type" in result
    
    # Test invalid category
    result = store_best_practice(
        temp_project_dir, "invalid_category", "Test Practice",
        "Test description", "Test rationale"
    )
    assert isinstance(result, str)
    assert "❌" in result
    assert "Invalid category" in result


def test_empty_and_none_values(temp_project_dir):
    """Test handling of empty and None values."""
    # Test with minimal required fields
    result = store_coding_pattern(
        temp_project_dir, "testing", "Minimal Pattern", "Basic description"
    )
    assert isinstance(result, str)
    assert "✅" in result
    assert "Minimal Pattern" in result
    
    # Test with empty lists
    result = store_coding_pattern(
        temp_project_dir, "testing", "Empty Lists Pattern", "Description",
        benefits=[], trade_offs=[], tags=[]
    )
    assert isinstance(result, str)
    assert "✅" in result
    assert "Empty Lists Pattern" in result
    
    # Verify empty lists are handled correctly
    patterns = get_coding_patterns(temp_project_dir, pattern_type="testing")
    assert isinstance(patterns, str)
    assert "Minimal Pattern" in patterns
    assert "Empty Lists Pattern" in patterns


def test_special_characters_and_unicode(temp_project_dir):
    """Test handling of special characters and Unicode content."""
    # Test with Unicode characters
    result = store_coding_pattern(
        temp_project_dir, "documentation", "国际化 Pattern 🌐",
        "Support for múltiple languages and spéciål çhars",
        tags=["国际化", "unicode", "特殊字符"]
    )
    assert isinstance(result, str)
    assert "✅" in result
    assert "国际化 Pattern 🌐" in result
    
    # Test with code containing special characters
    result = store_best_practice(
        temp_project_dir, "code_review", "特殊字符 Handling",
        "Handle special characters in code reviews",
        "Important for international applications",
        examples=["# Comment with émojis 🎯", "var_name = 'Spéciål string'"]
    )
    assert isinstance(result, str)
    assert "✅" in result
    assert "特殊字符 Handling" in result
    
    # Verify retrieval works with Unicode
    search_results = search_patterns_and_practices(temp_project_dir, "国际化")
    assert isinstance(search_results, str)
    assert "国际化 Pattern 🌐" in search_results


def test_large_content_storage(temp_project_dir):
    """Test storage of large content via MCP tools."""
    # Create large content
    large_description = "A" * 5000  # 5KB description
    large_code = "# " + "Long comment " * 200  # Large code example
    
    result = store_coding_pattern(
        temp_project_dir, "performance", "Large Content Pattern",
        large_description, example_code=large_code
    )
    assert isinstance(result, str)
    assert "✅" in result
    assert "Large Content Pattern" in result
    
    # Verify retrieval
    patterns = get_coding_patterns(temp_project_dir, pattern_type="performance")
    assert isinstance(patterns, str)
    assert "Large Content Pattern" in patterns


def test_mcp_tool_response_format(temp_project_dir):
    """Test that all MCP tools return properly formatted responses."""
    # Store some test data
    store_coding_pattern(
        temp_project_dir, "testing", "Response Format Test",
        "Tests response formatting"
    )
    store_best_practice(
        temp_project_dir, "testing", "Response Format Practice",
        "Tests response formatting", "Important for API consistency"
    )
    
    # Test all MCP tools return proper format
    tools_to_test = [
        lambda: get_coding_patterns(temp_project_dir),
        lambda: get_best_practices(temp_project_dir),
        lambda: search_patterns_and_practices(temp_project_dir, "test"),
        lambda: get_project_standards_summary(temp_project_dir)
    ]
    
    for tool_func in tools_to_test:
        result = tool_func()
        assert isinstance(result, str)
        assert len(result) > 0  # Should return non-empty string
        
        # Should not have error indicators for successful operations
        if "❌" not in result:  # If no error
            # Should contain some meaningful content
            assert len(result.strip()) > 10  # More than just whitespace


def test_concurrent_access(temp_project_dir):
    """Test concurrent access to pattern storage (basic simulation)."""
    # Simulate concurrent access by rapid successive calls
    results = []
    
    for i in range(10):
        result = store_coding_pattern(
            temp_project_dir, "testing", f"Concurrent Pattern {i}",
            f"Pattern stored concurrently {i}"
        )
        results.append(result)
    
    # All should succeed
    for i, result in enumerate(results):
        assert isinstance(result, str)
        assert "✅" in result
        assert f"Concurrent Pattern {i}" in result
    
    # Verify all patterns were stored
    patterns = get_coding_patterns(temp_project_dir, pattern_type="testing")
    assert isinstance(patterns, str)
    # Should contain multiple concurrent patterns
    concurrent_count = patterns.count("Concurrent Pattern")
    assert concurrent_count == 10


def test_comprehensive_workflow(temp_project_dir):
    """Test a comprehensive workflow using all MCP tools."""
    # 1. Store various patterns
    arch_result = store_coding_pattern(
        temp_project_dir, "architecture", "Clean Architecture",
        "Layered architecture with dependency inversion",
        tags=["architecture", "clean", "layers"], confidence=0.95
    )
    assert isinstance(arch_result, str)
    assert "✅" in arch_result
    
    sec_result = store_coding_pattern(
        temp_project_dir, "security", "Defense in Depth",
        "Multiple security layers", tags=["security", "defense"], confidence=0.90
    )
    assert isinstance(sec_result, str)
    assert "✅" in sec_result
    
    # 2. Store best practices
    review_result = store_best_practice(
        temp_project_dir, "code_review", "Security Review Checklist",
        "Always review code for security issues", "Prevent vulnerabilities",
        priority="high", tags=["security", "review"]
    )
    assert isinstance(review_result, str)
    assert "✅" in review_result
    
    # 3. Search across both
    security_results = search_patterns_and_practices(temp_project_dir, "security")
    assert isinstance(security_results, str)
    assert "Defense in Depth" in security_results
    assert "Security Review Checklist" in security_results
    
    # 4. Get filtered results
    high_conf_patterns = get_coding_patterns(temp_project_dir, min_confidence=0.92)
    assert isinstance(high_conf_patterns, str)
    assert "Clean Architecture" in high_conf_patterns  # 0.95 confidence
    assert "Defense in Depth" not in high_conf_patterns  # 0.90 confidence
    
    # 5. Get project summary
    summary = get_project_standards_summary(temp_project_dir)
    assert isinstance(summary, str)
    assert "Project Standards Summary" in summary
    assert "architecture" in summary  # Pattern types should be listed
    assert "Security Review Checklist" in summary