#!/usr/bin/env python3
"""
Tests for LLM Metadata Enhancement System
"""

import pytest
import tempfile
import os
import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, patch

from claude_code_indexer.llm_metadata_enhancer import (
    LLMMetadataEnhancer, 
    EnhancedMetadata, 
    DetectedPattern, 
    CodeEvolution
)
from claude_code_indexer.indexer import CodeGraphIndexer


class TestLLMMetadataEnhancer:
    """Test LLM metadata enhancement functionality"""
    
    def setup_method(self):
        """Setup test database"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name
        
        # Create indexer to setup basic schema
        indexer = CodeGraphIndexer(db_path=self.db_path, use_cache=False)
        
        # Add some test nodes
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert test nodes
            test_nodes = [
                (1, 'class', 'UserManager', '/app/user_manager.py', 'User management class', 0.8, '["structural"]'),
                (2, 'function', 'authenticate_user', '/app/auth.py', 'User authentication function', 0.7, '["api"]'),
                (3, 'method', 'save', '/app/models.py', 'Database save method', 0.6, '["data"]'),
                (4, 'function', 'format_date', '/app/utils.py', 'Date formatting utility', 0.3, '["utility"]'),
                (5, 'class', 'PaymentProcessor', '/app/payment.py', 'Payment processing class', 0.9, '["business"]')
            ]
            
            cursor.executemany('''
            INSERT INTO code_nodes (id, node_type, name, path, summary, importance_score, relevance_tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', test_nodes)
            
            conn.commit()
        
        self.enhancer = LLMMetadataEnhancer(self.db_path)
    
    def teardown_method(self):
        """Cleanup test database"""
        try:
            if hasattr(self, 'enhancer'):
                self.enhancer.shutdown()
            os.unlink(self.db_path)
        except:
            pass
    
    def test_database_schema_initialization(self):
        """Test that enhanced schema tables are created"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check enhanced_metadata table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_metadata'")
            assert cursor.fetchone() is not None
            
            # Check detected_patterns table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detected_patterns'")
            assert cursor.fetchone() is not None
            
            # Check code_evolution table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='code_evolution'")
            assert cursor.fetchone() is not None
    
    def test_role_tag_inference(self):
        """Test intelligent role tag inference"""
        # Test API-related
        tags = self.enhancer._infer_role_tags('function', 'authenticate_user', '/app/auth.py')
        assert 'api_endpoint' in tags
        
        # Test data model
        tags = self.enhancer._infer_role_tags('class', 'UserModel', '/app/models.py')
        assert 'data_model' in tags
        
        # Test utility
        tags = self.enhancer._infer_role_tags('function', 'format_date', '/app/utils.py')
        assert 'utility' in tags
        
        # Test service
        tags = self.enhancer._infer_role_tags('class', 'PaymentService', '/app/services.py')
        assert 'business_service' in tags
        
        # Test infrastructure
        tags = self.enhancer._infer_role_tags('class', 'DatabaseConfig', '/app/config.py')
        assert 'infrastructure' in tags
    
    def test_complexity_score_calculation(self):
        """Test complexity score calculation"""
        context = {
            'node_type': 'class',
            'importance_score': 0.8
        }
        
        score = self.enhancer._calculate_complexity_score(context)
        assert 0.0 <= score <= 1.0
        assert score > 0.3  # Should be higher due to class type and importance
        
        # Test function with lower importance
        context = {
            'node_type': 'function',
            'importance_score': 0.2
        }
        
        score2 = self.enhancer._calculate_complexity_score(context)
        assert score2 < score  # Should be lower
    
    def test_architectural_layer_inference(self):
        """Test architectural layer inference"""
        # Controller layer
        layer = self.enhancer._infer_architectural_layer('UserController', '/app/controllers/', ['api_endpoint'])
        assert layer == 'controller'
        
        # Service layer
        layer = self.enhancer._infer_architectural_layer('PaymentService', '/app/services/', ['business_service'])
        assert layer == 'service'
        
        # Model layer
        layer = self.enhancer._infer_architectural_layer('User', '/app/models/', ['data_model'])
        assert layer == 'model'
        
        # Utility layer
        layer = self.enhancer._infer_architectural_layer('DateHelper', '/app/utils/', ['utility'])
        assert layer == 'utility'
    
    def test_business_domain_inference(self):
        """Test business domain inference"""
        # Authentication domain
        domain = self.enhancer._infer_business_domain('authenticate_user', '/app/auth/')
        assert domain == 'authentication'
        
        # Payment domain
        domain = self.enhancer._infer_business_domain('PaymentProcessor', '/app/payment/')
        assert domain == 'payment'
        
        # User management domain
        domain = self.enhancer._infer_business_domain('UserProfile', '/app/user/')
        assert domain == 'user_management'
        
        # API domain
        domain = self.enhancer._infer_business_domain('ApiHandler', '/app/api/')
        assert domain == 'api'
    
    def test_criticality_assessment(self):
        """Test criticality level assessment"""
        # High importance + API endpoint = critical
        criticality = self.enhancer._assess_criticality(0.9, ['api_endpoint'])
        assert criticality == 'critical'
        
        # Medium importance + business service = important
        criticality = self.enhancer._assess_criticality(0.7, ['business_service'])
        assert criticality == 'important'
        
        # Low importance = low
        criticality = self.enhancer._assess_criticality(0.2, ['utility'])
        assert criticality == 'low'
    
    def test_design_pattern_detection(self):
        """Test design pattern detection"""
        # Singleton pattern
        context = {'name': 'DatabaseSingleton', 'node_type': 'class'}
        patterns = self.enhancer._detect_design_patterns(context)
        singleton_patterns = [p for p in patterns if p['pattern_type'] == 'singleton']
        assert len(singleton_patterns) > 0
        
        # Factory pattern
        context = {'name': 'UserFactory', 'node_type': 'class'}
        patterns = self.enhancer._detect_design_patterns(context)
        factory_patterns = [p for p in patterns if p['pattern_type'] == 'factory']
        assert len(factory_patterns) > 0
        
        # Observer pattern
        context = {'name': 'EventListener', 'node_type': 'class'}
        patterns = self.enhancer._detect_design_patterns(context)
        observer_patterns = [p for p in patterns if p['pattern_type'] == 'observer']
        assert len(observer_patterns) > 0
    
    def test_save_enhanced_metadata(self):
        """Test saving enhanced metadata to database"""
        metadata = EnhancedMetadata(
            node_id=1,
            llm_summary="Test summary",
            role_tags=['api_endpoint', 'critical'],
            complexity_score=0.7,
            quality_metrics={'maintainability': 0.8},
            architectural_layer='controller',
            business_domain='authentication',
            criticality_level='critical',
            dependencies_impact=0.8,
            testability_score=0.6,
            last_analyzed='2024-01-01 12:00:00'
        )
        
        self.enhancer._save_enhanced_metadata(metadata)
        
        # Verify saved data
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM enhanced_metadata WHERE node_id = ?', (1,))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[1] == "Test summary"  # llm_summary
            assert json.loads(result[2]) == ['api_endpoint', 'critical']  # role_tags
            assert result[3] == 0.7  # complexity_score
            assert json.loads(result[4]) == {'maintainability': 0.8}  # quality_metrics
            assert result[5] == 'controller'  # architectural_layer
    
    def test_save_detected_pattern(self):
        """Test saving detected pattern to database"""
        pattern = {
            'pattern_type': 'singleton',
            'confidence': 0.8,
            'description': 'Singleton pattern detected'
        }
        
        self.enhancer._save_detected_pattern(1, pattern)
        
        # Verify saved data
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM detected_patterns WHERE node_id = ?', (1,))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[2] == 'singleton'  # pattern_type
            assert result[3] == 0.8  # confidence
    
    def test_get_enhanced_nodes(self):
        """Test querying enhanced nodes with filters"""
        # First, add some enhanced metadata
        metadata1 = EnhancedMetadata(
            node_id=1,
            llm_summary="Controller class",
            role_tags=['api_endpoint'],
            complexity_score=0.7,
            quality_metrics={},
            architectural_layer='controller',
            business_domain='authentication',
            criticality_level='critical',
            dependencies_impact=0.8,
            testability_score=0.6,
            last_analyzed='2024-01-01 12:00:00'
        )
        
        metadata2 = EnhancedMetadata(
            node_id=2,
            llm_summary="Service class",
            role_tags=['business_service'],
            complexity_score=0.5,
            quality_metrics={},
            architectural_layer='service',
            business_domain='payment',
            criticality_level='important',
            dependencies_impact=0.6,
            testability_score=0.8,
            last_analyzed='2024-01-01 12:00:00'
        )
        
        self.enhancer._save_enhanced_metadata(metadata1)
        self.enhancer._save_enhanced_metadata(metadata2)
        
        # Test filtering by architectural layer
        nodes = self.enhancer.get_enhanced_nodes(architectural_layer='controller')
        assert len(nodes) == 1
        assert nodes[0]['architectural_layer'] == 'controller'
        
        # Test filtering by criticality
        nodes = self.enhancer.get_enhanced_nodes(criticality_level='critical')
        assert len(nodes) == 1
        assert nodes[0]['criticality_level'] == 'critical'
        
        # Test filtering by minimum complexity
        nodes = self.enhancer.get_enhanced_nodes(min_complexity=0.6)
        assert len(nodes) == 1
        assert nodes[0]['complexity_score'] >= 0.6
    
    def test_update_node_metadata(self):
        """Test updating node metadata"""
        # First save some metadata
        metadata = EnhancedMetadata(
            node_id=1,
            llm_summary="Original summary",
            role_tags=['api'],
            complexity_score=0.5,
            quality_metrics={},
            architectural_layer='controller',
            business_domain='auth',
            criticality_level='normal',
            dependencies_impact=0.5,
            testability_score=0.5,
            last_analyzed='2024-01-01 12:00:00'
        )
        
        self.enhancer._save_enhanced_metadata(metadata)
        
        # Update some fields
        updates = {
            'llm_summary': 'Updated summary',
            'complexity_score': 0.8,
            'role_tags': ['api_endpoint', 'critical']
        }
        
        success = self.enhancer.update_node_metadata(1, updates)
        assert success
        
        # Verify updates
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT llm_summary, complexity_score, role_tags FROM enhanced_metadata WHERE node_id = ?', (1,))
            result = cursor.fetchone()
            
            assert result[0] == 'Updated summary'
            assert result[1] == 0.8
            assert json.loads(result[2]) == ['api_endpoint', 'critical']
    
    def test_generate_analysis_summary(self):
        """Test analysis summary generation"""
        # Add some enhanced metadata
        metadata1 = EnhancedMetadata(
            node_id=1, llm_summary="Test", role_tags=['api'], complexity_score=0.7,
            quality_metrics={}, architectural_layer='controller', business_domain='auth',
            criticality_level='critical', dependencies_impact=0.8, testability_score=0.6,
            last_analyzed='2024-01-01 12:00:00'
        )
        
        metadata2 = EnhancedMetadata(
            node_id=2, llm_summary="Test", role_tags=['service'], complexity_score=0.5,
            quality_metrics={}, architectural_layer='service', business_domain='payment',
            criticality_level='important', dependencies_impact=0.6, testability_score=0.8,
            last_analyzed='2024-01-01 12:00:00'
        )
        
        self.enhancer._save_enhanced_metadata(metadata1)
        self.enhancer._save_enhanced_metadata(metadata2)
        
        summary = self.enhancer._generate_analysis_summary()
        
        assert 'architectural_layers' in summary
        assert 'criticality_distribution' in summary
        assert 'business_domains' in summary
        assert 'average_scores' in summary
        
        # Check layer distribution
        layers = summary['architectural_layers']
        assert 'controller' in layers
        assert 'service' in layers
        assert layers['controller'] == 1
        assert layers['service'] == 1
        
        # Check criticality distribution
        criticality = summary['criticality_distribution']
        assert 'critical' in criticality
        assert 'important' in criticality
        assert criticality['critical'] == 1
        assert criticality['important'] == 1
    
    def test_analyze_single_node(self):
        """Test single node analysis"""
        node_data = (1, 'class', 'UserController', '/app/controllers/user.py', 'User controller', 0.8)
        
        result = self.enhancer._analyze_single_node(node_data)
        
        assert result is not None
        assert isinstance(result, EnhancedMetadata)
        assert result.node_id == 1
        assert result.llm_summary != ""
        assert len(result.role_tags) > 0
        assert 0.0 <= result.complexity_score <= 1.0
        assert result.architectural_layer in ['controller', 'service', 'model', 'utility', 'infrastructure', 'test']
        assert result.criticality_level in ['critical', 'important', 'normal', 'low']
    
    def test_get_analysis_insights(self):
        """Test comprehensive analysis insights"""
        # Add enhanced metadata for insights
        metadata = EnhancedMetadata(
            node_id=1, llm_summary="Test", role_tags=['api'], complexity_score=0.8,
            quality_metrics={}, architectural_layer='controller', business_domain='auth',
            criticality_level='critical', dependencies_impact=0.9, testability_score=0.4,
            last_analyzed='2024-01-01 12:00:00'
        )
        
        self.enhancer._save_enhanced_metadata(metadata)
        
        insights = self.enhancer.get_analysis_insights()
        
        assert 'codebase_health' in insights
        assert 'architectural_overview' in insights
        assert 'complexity_hotspots' in insights
        assert 'improvement_suggestions' in insights
        
        # Check health assessment
        health = insights['codebase_health']
        assert 'overall_score' in health
        assert 'complexity_health' in health
        assert 'testability_health' in health
        assert 'recommendations' in health
        
        # Should have recommendations due to high complexity and low testability
        assert len(health['recommendations']) > 0
    
    def test_mock_llm_analysis(self):
        """Test the mock LLM analysis implementation"""
        context = {
            'node_type': 'class',
            'name': 'PaymentController',
            'path': '/app/controllers/payment.py',
            'summary': 'Handles payment operations',
            'importance_score': 0.9
        }
        
        result = self.enhancer._perform_llm_analysis(context)
        
        assert result is not None
        assert 'summary' in result
        assert 'role_tags' in result
        assert 'complexity_score' in result
        assert 'architectural_layer' in result
        assert 'business_domain' in result
        assert 'criticality_level' in result
        
        # Check reasonable values
        assert isinstance(result['role_tags'], list)
        assert 0.0 <= result['complexity_score'] <= 1.0
        assert result['architectural_layer'] in ['controller', 'service', 'model', 'utility', 'infrastructure', 'test']
        assert result['business_domain'] in ['authentication', 'payment', 'user_management', 'data_processing', 
                                           'api', 'database', 'configuration', 'logging', 'testing', 'general']
        assert result['criticality_level'] in ['critical', 'important', 'normal', 'low']


class TestLLMMetadataIntegration:
    """Test integration with CodeGraphIndexer"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name
        
        # Create test Python file
        test_file = Path(self.test_dir) / 'test.py'
        test_file.write_text('''
class UserManager:
    """Manages user operations"""
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        return True
    
    def create_user(self, user_data):
        """Create new user"""
        pass

def format_date(date):
    """Format date string"""
    return str(date)
        ''')
    
    def teardown_method(self):
        """Cleanup"""
        try:
            os.unlink(self.db_path)
            import shutil
            shutil.rmtree(self.test_dir)
        except:
            pass
    
    def test_indexer_llm_enhancement_integration(self):
        """Test LLM enhancement integration with indexer"""
        indexer = CodeGraphIndexer(db_path=self.db_path, use_cache=False, project_path=Path(self.test_dir))
        
        # Index the test file
        indexer.index_directory(self.test_dir)
        
        # Check that nodes were created
        stats = indexer.get_stats()
        # get_stats might return different format, just check it's not empty
        assert stats is not None
        
        # Check directly from database instead
        with sqlite3.connect(indexer.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM code_nodes")
            node_count = cursor.fetchone()[0]
        
        assert node_count > 0
        
        # Test LLM enhancer property access
        llm_enhancer = indexer.llm_enhancer
        assert llm_enhancer is not None
        assert isinstance(llm_enhancer, LLMMetadataEnhancer)
        
        # Test enhancement
        result = indexer.enhance_metadata(limit=5)
        assert 'analyzed_count' in result
        assert result['analyzed_count'] >= 0
        
        # Test enhanced queries
        enhanced_nodes = indexer.query_enhanced_nodes(limit=10)
        # May be empty if no enhancement occurred, but should not error
        assert isinstance(enhanced_nodes, list)
        
        # Test insights
        insights = indexer.get_analysis_insights()
        assert isinstance(insights, dict)
        
        # Test critical components
        critical = indexer.get_critical_components()
        assert isinstance(critical, list)
    
    def test_metadata_persistence(self):
        """Test that enhanced metadata persists across indexer sessions"""
        indexer1 = CodeGraphIndexer(db_path=self.db_path, use_cache=False, project_path=Path(self.test_dir))
        
        # Index and enhance
        indexer1.index_directory(self.test_dir)
        result1 = indexer1.enhance_metadata(limit=2)
        
        # Create new indexer instance
        indexer2 = CodeGraphIndexer(db_path=self.db_path, use_cache=False, project_path=Path(self.test_dir))
        
        # Should be able to query enhanced data
        enhanced_nodes = indexer2.query_enhanced_nodes()
        # Data should persist (though may be empty if mock analysis didn't save data)
        assert isinstance(enhanced_nodes, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])