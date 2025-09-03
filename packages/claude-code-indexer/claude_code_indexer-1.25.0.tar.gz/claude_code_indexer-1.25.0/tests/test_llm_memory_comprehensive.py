"""Comprehensive test suite for LLM Memory Storage - showcasing all capabilities."""

import pytest
import tempfile
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from claude_code_indexer.llm_memory_storage import LLMMemoryStorage


@pytest.fixture
def comprehensive_db():
    """Create a database with comprehensive test data."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    # Create comprehensive test schema
    conn = sqlite3.connect(str(db_path))
    
    # Create code_nodes table with realistic data
    conn.execute("""
        CREATE TABLE code_nodes (
            id INTEGER PRIMARY KEY,
            name TEXT,
            node_type TEXT,
            path TEXT
        )
    """)
    
    # Insert realistic test nodes
    test_nodes = [
        (1, 'UserService', 'class', 'src/services/user_service.py'),
        (2, 'authenticate_user', 'method', 'src/services/user_service.py'),
        (3, 'DatabaseConnection', 'class', 'src/db/connection.py'),
        (4, 'PaymentProcessor', 'class', 'src/payment/processor.py'),
        (5, 'encrypt_password', 'function', 'src/auth/crypto.py'),
        (6, 'APIController', 'class', 'src/api/controller.py'),
        (7, 'validate_input', 'function', 'src/utils/validation.py'),
        (8, 'CacheManager', 'class', 'src/cache/manager.py'),
        (9, 'send_notification', 'function', 'src/notifications/email.py'),
        (10, 'SecurityMiddleware', 'class', 'src/middleware/security.py')
    ]
    
    conn.executemany("INSERT INTO code_nodes (id, name, node_type, path) VALUES (?, ?, ?, ?)", test_nodes)
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    db_path.unlink()


@pytest.fixture
def memory_storage_with_data(comprehensive_db):
    """Create LLMMemoryStorage with pre-populated realistic data."""
    storage = LLMMemoryStorage(comprehensive_db)
    
    # Populate with realistic LLM memories
    realistic_memories = [
        # Security Analysis
        {
            'node_id': 1, 'llm_name': 'claude-3-opus', 'memory_type': 'analysis',
            'content': 'UserService class implements proper dependency injection pattern. Uses repository pattern for data access with clean separation of concerns. Authentication logic is centralized and follows security best practices.',
            'metadata': {'confidence': 0.95, 'analysis_type': 'architectural', 'security_reviewed': True},
            'tags': ['architecture', 'security', 'dependency-injection', 'repository-pattern']
        },
        {
            'node_id': 2, 'llm_name': 'claude-3-opus', 'memory_type': 'warning',
            'content': 'authenticate_user method lacks rate limiting protection. Potential vulnerability to brute force attacks. Should implement exponential backoff and account lockout after failed attempts.',
            'metadata': {'severity': 'high', 'cve_risk': True, 'requires_immediate_action': True},
            'tags': ['security', 'vulnerability', 'rate-limiting', 'brute-force']
        },
        {
            'node_id': 3, 'llm_name': 'claude-3-opus', 'memory_type': 'insight',
            'content': 'DatabaseConnection class uses connection pooling effectively. Pool size is configurable but defaults to 10 connections. Connection timeout set to 30 seconds which is appropriate for most use cases.',
            'metadata': {'performance_impact': 'positive', 'scalability': 'good'},
            'tags': ['database', 'performance', 'connection-pooling', 'scalability']
        },
        {
            'node_id': 4, 'llm_name': 'claude-3-opus', 'memory_type': 'todo',
            'content': 'PaymentProcessor needs to implement retry logic for failed transactions. Currently fails immediately on network errors. Should implement exponential backoff with jitter for better reliability.',
            'metadata': {'priority': 'medium', 'effort_estimate': '2-3 days', 'business_impact': 'medium'},
            'tags': ['payment', 'reliability', 'retry-logic', 'network-errors']
        },
        {
            'node_id': 5, 'llm_name': 'claude-3-opus', 'memory_type': 'analysis',
            'content': 'encrypt_password function uses bcrypt with proper salt rounds (12). Implementation follows OWASP guidelines. Password validation includes length, complexity, and common password checks.',
            'metadata': {'security_compliance': 'OWASP', 'algorithm': 'bcrypt', 'salt_rounds': 12},
            'tags': ['security', 'encryption', 'password', 'owasp', 'bcrypt']
        },
        # Performance Analysis
        {
            'node_id': 6, 'llm_name': 'claude-3-sonnet', 'memory_type': 'insight',
            'content': 'APIController shows signs of performance bottlenecks in bulk operations. Processes requests sequentially instead of batching. Could benefit from async processing for I/O bound operations.',
            'metadata': {'performance_impact': 'negative', 'optimization_potential': 'high'},
            'tags': ['performance', 'api', 'async', 'optimization', 'bottleneck']
        },
        {
            'node_id': 7, 'llm_name': 'claude-3-sonnet', 'memory_type': 'warning',
            'content': 'validate_input function has regex complexity vulnerability. Complex regex patterns could lead to ReDoS attacks with malicious input. Should implement input length limits and timeout.',
            'metadata': {'vulnerability_type': 'ReDoS', 'severity': 'medium', 'mitigation': 'input_limits'},
            'tags': ['security', 'regex', 'redos', 'validation', 'vulnerability']
        },
        {
            'node_id': 8, 'llm_name': 'claude-3-haiku', 'memory_type': 'analysis',
            'content': 'CacheManager implements LRU eviction policy with TTL support. Memory usage is well-controlled with configurable size limits. Cache hit ratio averages 85% in production workloads.',
            'metadata': {'cache_type': 'LRU', 'hit_ratio': 0.85, 'memory_controlled': True},
            'tags': ['caching', 'performance', 'lru', 'memory-management']
        },
        # Business Logic
        {
            'node_id': 9, 'llm_name': 'claude-3-opus', 'memory_type': 'context',
            'content': 'send_notification function is part of critical user journey for password resets and security alerts. Integrates with multiple providers (email, SMS, push). Failure impacts user experience significantly.',
            'metadata': {'business_critical': True, 'user_journey': 'authentication', 'providers': ['email', 'sms', 'push']},
            'tags': ['notifications', 'user-experience', 'critical-path', 'multi-channel']
        },
        {
            'node_id': 10, 'llm_name': 'claude-3-opus', 'memory_type': 'todo',
            'content': 'SecurityMiddleware should implement CSP headers for XSS protection. Currently missing Content-Security-Policy and other security headers. Also needs CSRF protection for state-changing operations.',
            'metadata': {'security_gap': 'headers', 'priority': 'high', 'compliance_required': True},
            'tags': ['security', 'csp', 'xss', 'csrf', 'headers', 'middleware']
        }
    ]
    
    # Store all realistic memories
    for memory in realistic_memories:
        storage.store_memory(**memory)
    
    return storage


def test_comprehensive_memory_analysis_workflow(memory_storage_with_data):
    """Test complete workflow: analyze → store → retrieve → update → search."""
    
    # 1. Store new analysis (simulating LLM analyzing new code)
    analysis_id = memory_storage_with_data.store_memory(
        node_id=1,
        llm_name='claude-3-opus',
        memory_type='insight',
        content='Code review reveals excellent error handling patterns. All exceptions are properly caught and logged with sufficient context for debugging.',
        metadata={'code_review': True, 'error_handling_score': 9.5},
        tags=['code-review', 'error-handling', 'quality']
    )
    
    assert analysis_id > 0
    
    # 2. Retrieve and verify storage
    memories = memory_storage_with_data.get_memories(node_id=1, memory_type='insight')
    assert len(memories) == 1
    assert 'error handling patterns' in memories[0]['content']
    assert memories[0]['metadata']['error_handling_score'] == 9.5
    
    # 3. Update analysis with new findings
    memory_storage_with_data.store_memory(
        node_id=1,
        llm_name='claude-3-opus',
        memory_type='insight',
        content='UPDATED: Code review reveals excellent error handling patterns with comprehensive logging. However, discovered potential memory leak in cleanup methods that needs investigation.',
        metadata={'code_review': True, 'error_handling_score': 8.0, 'memory_leak_risk': True},
        tags=['code-review', 'error-handling', 'quality', 'memory-leak']
    )
    
    # 4. Verify update (should still be only 1 memory)
    updated_memories = memory_storage_with_data.get_memories(node_id=1, memory_type='insight')
    assert len(updated_memories) == 1
    assert 'memory leak' in updated_memories[0]['content']
    assert updated_memories[0]['metadata']['memory_leak_risk'] is True
    assert 'memory-leak' in updated_memories[0]['tags']


def test_security_vulnerability_tracking(memory_storage_with_data):
    """Test comprehensive security vulnerability tracking across codebase."""
    
    # Get all security-related memories
    security_memories = memory_storage_with_data.get_memories(tags=['security'])
    
    # Should find multiple security-related entries
    assert len(security_memories) >= 3
    
    # Search for specific vulnerability types
    xss_memories = memory_storage_with_data.search_memories('XSS')
    brute_force_memories = memory_storage_with_data.search_memories('brute force')
    redos_memories = memory_storage_with_data.search_memories('ReDoS')
    
    assert len(xss_memories) >= 1
    assert len(brute_force_memories) >= 1
    assert len(redos_memories) >= 1
    
    # Verify high-severity warnings
    high_severity = [m for m in security_memories if m.get('metadata', {}).get('severity') == 'high']
    assert len(high_severity) >= 1
    
    # Check for CVE risk tracking
    cve_risks = [m for m in security_memories if m.get('metadata', {}).get('cve_risk') is True]
    assert len(cve_risks) >= 1


def test_performance_optimization_tracking(memory_storage_with_data):
    """Test performance analysis and optimization tracking."""
    
    # Get performance-related memories
    perf_memories = memory_storage_with_data.get_memories(tags=['performance'])
    assert len(perf_memories) >= 2
    
    # Check for bottleneck identification
    bottleneck_memories = memory_storage_with_data.search_memories('bottleneck')
    assert len(bottleneck_memories) >= 1
    
    # Verify optimization potential tracking
    high_optimization = [
        m for m in perf_memories 
        if m.get('metadata', {}).get('optimization_potential') == 'high'
    ]
    assert len(high_optimization) >= 1
    
    # Check caching analysis
    cache_memories = memory_storage_with_data.search_memories('cache')
    assert len(cache_memories) >= 1
    
    # Verify cache hit ratio tracking
    cache_metrics = [
        m for m in cache_memories 
        if 'hit_ratio' in m.get('metadata', {})
    ]
    assert len(cache_metrics) >= 1


def test_architectural_decision_tracking(memory_storage_with_data):
    """Test architectural analysis and decision tracking."""
    
    # Get architectural memories
    arch_memories = memory_storage_with_data.get_memories(tags=['architecture'])
    assert len(arch_memories) >= 1
    
    # Check for design patterns
    pattern_memories = memory_storage_with_data.search_memories('pattern')
    assert len(pattern_memories) >= 1
    
    # Verify dependency injection tracking
    di_memories = memory_storage_with_data.get_memories(tags=['dependency-injection'])
    assert len(di_memories) >= 1
    
    # Check repository pattern tracking
    repo_memories = memory_storage_with_data.get_memories(tags=['repository-pattern'])
    assert len(repo_memories) >= 1


def test_todo_and_action_item_management(memory_storage_with_data):
    """Test TODO and action item tracking across codebase."""
    
    # Get all TODOs
    todos = memory_storage_with_data.get_memories(memory_type='todo')
    assert len(todos) >= 2
    
    # Check priority classification
    high_priority = [t for t in todos if t.get('metadata', {}).get('priority') == 'high']
    medium_priority = [t for t in todos if t.get('metadata', {}).get('priority') == 'medium']
    
    assert len(high_priority) >= 1
    assert len(medium_priority) >= 1
    
    # Verify effort estimation
    effort_estimated = [t for t in todos if 'effort_estimate' in t.get('metadata', {})]
    assert len(effort_estimated) >= 1
    
    # Check business impact tracking
    business_impact = [t for t in todos if 'business_impact' in t.get('metadata', {})]
    assert len(business_impact) >= 1


def test_multi_llm_collaboration(memory_storage_with_data):
    """Test memories from different LLM models working together."""
    
    # Get memories by different LLMs
    opus_memories = memory_storage_with_data.get_memories(llm_name='claude-3-opus')
    sonnet_memories = memory_storage_with_data.get_memories(llm_name='claude-3-sonnet')
    haiku_memories = memory_storage_with_data.get_memories(llm_name='claude-3-haiku')
    
    assert len(opus_memories) >= 3  # Opus does deep analysis
    assert len(sonnet_memories) >= 1  # Sonnet does balanced analysis
    assert len(haiku_memories) >= 1  # Haiku does quick analysis
    
    # Verify different LLMs can analyze same node
    node_1_memories = memory_storage_with_data.get_memories(node_id=1)
    llm_names = {m['llm_name'] for m in node_1_memories}
    assert 'claude-3-opus' in llm_names


def test_advanced_search_and_analytics(memory_storage_with_data):
    """Test advanced search and analytics capabilities."""
    
    # Complex search scenarios
    auth_related = memory_storage_with_data.search_memories('authentication')
    assert len(auth_related) >= 1
    
    password_related = memory_storage_with_data.search_memories('password')
    assert len(password_related) >= 1
    
    connection_related = memory_storage_with_data.search_memories('connection')
    assert len(connection_related) >= 1
    
    # Tag-based complex queries
    security_and_vulnerability = memory_storage_with_data.get_memories(
        tags=['security', 'vulnerability']
    )
    assert len(security_and_vulnerability) >= 1
    
    performance_optimization = memory_storage_with_data.get_memories(
        tags=['performance', 'optimization']
    )
    assert len(performance_optimization) >= 1


def test_metadata_richness_and_querying(memory_storage_with_data):
    """Test rich metadata storage and complex querying."""
    
    all_memories = memory_storage_with_data.get_memories(limit=100)
    
    # Verify metadata richness
    memories_with_confidence = [
        m for m in all_memories 
        if 'confidence' in m.get('metadata', {})
    ]
    assert len(memories_with_confidence) >= 1
    
    # Check security compliance tracking
    owasp_compliant = [
        m for m in all_memories 
        if m.get('metadata', {}).get('security_compliance') == 'OWASP'
    ]
    assert len(owasp_compliant) >= 1
    
    # Verify business criticality tracking
    business_critical = [
        m for m in all_memories 
        if m.get('metadata', {}).get('business_critical') is True
    ]
    assert len(business_critical) >= 1
    
    # Check algorithm/implementation details
    bcrypt_usage = [
        m for m in all_memories 
        if m.get('metadata', {}).get('algorithm') == 'bcrypt'
    ]
    assert len(bcrypt_usage) >= 1


def test_comprehensive_node_insights(memory_storage_with_data):
    """Test comprehensive insights for individual nodes."""
    
    # Get comprehensive summary for UserService (node 1)
    user_service_summary = memory_storage_with_data.get_node_summary(1)
    
    assert user_service_summary['node_id'] == 1
    assert user_service_summary['total_memories'] >= 1
    assert 'analysis' in user_service_summary['by_type']
    assert 'claude-3-opus' in user_service_summary['by_llm']
    assert len(user_service_summary['tags']) >= 3
    
    # Verify different memory types for same node
    assert len(user_service_summary['by_type']) >= 1
    
    # Check for security analysis
    security_tags = [tag for tag in user_service_summary['tags'] if 'security' in tag.lower()]
    assert len(security_tags) >= 1


def test_memory_evolution_and_updates(memory_storage_with_data):
    """Test how memories evolve and get updated over time."""
    
    node_id = 3  # DatabaseConnection
    
    # Store initial analysis
    memory_storage_with_data.store_memory(
        node_id=node_id,
        llm_name='claude-3-opus',
        memory_type='analysis',
        content='Initial analysis: Basic database connection implementation.',
        metadata={'version': 1, 'completeness': 0.5}
    )
    
    # Update with more detailed analysis
    memory_storage_with_data.store_memory(
        node_id=node_id,
        llm_name='claude-3-opus',
        memory_type='analysis',
        content='Updated analysis: Sophisticated database connection with pooling, retry logic, and proper error handling. Implements connection health monitoring.',
        metadata={'version': 2, 'completeness': 0.9, 'features_discovered': ['pooling', 'retry', 'monitoring']}
    )
    
    # Verify only latest version exists
    analyses = memory_storage_with_data.get_memories(node_id=node_id, memory_type='analysis')
    opus_analyses = [a for a in analyses if a['llm_name'] == 'claude-3-opus']
    assert len(opus_analyses) == 1
    assert opus_analyses[0]['metadata']['version'] == 2
    assert 'Sophisticated database connection' in opus_analyses[0]['content']


def test_cross_node_relationship_insights(memory_storage_with_data):
    """Test insights that span multiple related nodes."""
    
    # Store relationship insight
    memory_storage_with_data.store_memory(
        node_id=1,  # UserService
        llm_name='claude-3-opus',
        memory_type='insight',
        content='UserService has strong coupling with DatabaseConnection (node 3) and PaymentProcessor (node 4). Changes to authentication logic may impact payment flow validation.',
        metadata={'related_nodes': [3, 4], 'coupling_strength': 'high', 'impact_analysis': True},
        tags=['architecture', 'coupling', 'impact-analysis', 'relationships']
    )
    
    # Verify relationship tracking
    relationship_memories = memory_storage_with_data.search_memories('coupling')
    assert len(relationship_memories) >= 1
    
    impact_memories = memory_storage_with_data.get_memories(tags=['impact-analysis'])
    assert len(impact_memories) >= 1
    
    # Check related nodes metadata
    relationship_memory = relationship_memories[0]
    assert 'related_nodes' in relationship_memory['metadata']
    assert 3 in relationship_memory['metadata']['related_nodes']
    assert 4 in relationship_memory['metadata']['related_nodes']


def test_compliance_and_audit_tracking(memory_storage_with_data):
    """Test compliance and audit trail capabilities."""
    
    # Get all compliance-related memories
    all_memories = memory_storage_with_data.get_memories(limit=100)
    
    # Find OWASP compliance
    owasp_memories = [
        m for m in all_memories 
        if m.get('metadata', {}).get('security_compliance') == 'OWASP'
    ]
    assert len(owasp_memories) >= 1
    
    # Find compliance requirements
    compliance_required = [
        m for m in all_memories 
        if m.get('metadata', {}).get('compliance_required') is True
    ]
    assert len(compliance_required) >= 1
    
    # Check audit trail (all memories should have timestamps)
    for memory in all_memories:
        assert 'created_at' in memory
        assert 'updated_at' in memory
        assert memory['created_at'] is not None
        assert memory['updated_at'] is not None


def test_llm_confidence_and_reliability_tracking(memory_storage_with_data):
    """Test LLM confidence scoring and reliability metrics."""
    
    all_memories = memory_storage_with_data.get_memories(limit=100)
    
    # Find memories with confidence scores
    confident_memories = [
        m for m in all_memories 
        if 'confidence' in m.get('metadata', {})
    ]
    assert len(confident_memories) >= 1
    
    # Verify confidence scores are valid (0.0 to 1.0)
    for memory in confident_memories:
        confidence = memory['metadata']['confidence']
        assert 0.0 <= confidence <= 1.0
    
    # Find high-confidence analysis
    high_confidence = [
        m for m in confident_memories 
        if m['metadata']['confidence'] >= 0.9
    ]
    assert len(high_confidence) >= 1


def test_memory_storage_scalability(memory_storage_with_data):
    """Test that memory storage can handle large volumes of data."""
    
    # Add many memories to test scalability
    for i in range(50):
        memory_storage_with_data.store_memory(
            node_id=(i % 10) + 1,  # Distribute across existing nodes
            llm_name=f'test-llm-{i % 3}',
            memory_type=['analysis', 'insight', 'todo', 'warning'][i % 4],
            content=f'Scalability test memory {i}: This is test content for performance evaluation.',
            metadata={'test_batch': True, 'batch_id': i // 10, 'index': i},
            tags=[f'test-{i % 5}', 'scalability', 'performance-test']
        )
    
    # Verify all memories were stored
    test_memories = memory_storage_with_data.get_memories(limit=1000)
    test_batch_memories = [
        m for m in test_memories 
        if m.get('metadata', {}).get('test_batch') is True
    ]
    assert len(test_batch_memories) == 50
    
    # Test search performance with large dataset
    search_results = memory_storage_with_data.search_memories('scalability')
    assert len(search_results) >= 50
    
    # Test tag-based retrieval performance
    tag_results = memory_storage_with_data.get_memories(tags=['scalability'])
    assert len(tag_results) >= 50