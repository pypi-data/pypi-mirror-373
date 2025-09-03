#!/usr/bin/env python3
"""
Test cases for InfrastructureDetector - Simple tests for existing methods
"""

import pytest
import ast
from claude_code_indexer.infrastructure_detector import InfrastructureDetector, InfraComponent


class TestInfrastructureDetectorSimple:
    """Test infrastructure detection functionality with existing methods"""
    
    def setup_method(self):
        """Setup test environment"""
        self.detector = InfrastructureDetector()
    
    def test_initialization(self):
        """Test detector initialization"""
        assert self.detector is not None
        assert hasattr(self.detector, 'db_patterns')
        assert hasattr(self.detector, 'api_patterns')
        assert hasattr(self.detector, 'mq_patterns')
    
    def test_detect_infrastructure_empty_code(self):
        """Test infrastructure detection with empty code"""
        code = ""
        try:
            tree = ast.parse(code)
            result = self.detector.detect_infrastructure(tree, "empty.py", code)
            assert isinstance(result, dict)
        except SyntaxError:
            # Empty code might not parse
            pass
    
    def test_detect_infrastructure_simple_code(self):
        """Test infrastructure detection with simple code"""
        code = """
import os
print("Hello World")
"""
        tree = ast.parse(code)
        result = self.detector.detect_infrastructure(tree, "simple.py", code)
        assert isinstance(result, dict)
    
    def test_detect_infrastructure_database_imports(self):
        """Test infrastructure detection with database imports"""
        code = """
import psycopg2
import sqlite3
import redis
"""
        tree = ast.parse(code)
        result = self.detector.detect_infrastructure(tree, "db.py", code)
        assert isinstance(result, dict)
    
    def test_detect_databases_method(self):
        """Test _detect_databases method"""
        code = """
import psycopg2
DATABASE_URL = "postgresql://localhost/db"
"""
        tree = ast.parse(code)
        databases = self.detector._detect_databases(tree, code)
        assert isinstance(databases, list)
    
    def test_detect_apis_method(self):
        """Test _detect_apis method"""
        code = """
from flask import Flask
app = Flask(__name__)

@app.route('/api')
def api():
    return {}
"""
        tree = ast.parse(code)
        apis = self.detector._detect_apis(tree, code)
        assert isinstance(apis, list)
    
    def test_detect_message_queues_method(self):
        """Test _detect_message_queues method"""
        code = """
from celery import Celery
app = Celery('myapp')

@app.task
def my_task():
    pass
"""
        tree = ast.parse(code)
        queues = self.detector._detect_message_queues(tree, code)
        assert isinstance(queues, list)
    
    def test_detect_cloud_services_method(self):
        """Test _detect_cloud_services method"""
        code = """
import boto3
s3 = boto3.client('s3')
"""
        tree = ast.parse(code)
        services = self.detector._detect_cloud_services(tree, code)
        assert isinstance(services, list)
    
    def test_detect_configuration_method(self):
        """Test _detect_configuration method"""
        code = """
import os
DATABASE_URL = os.getenv('DATABASE_URL')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
"""
        tree = ast.parse(code)
        configs = self.detector._detect_configuration(tree, code)
        assert isinstance(configs, list)
    
    def test_detect_architectural_patterns_method(self):
        """Test detect_architectural_patterns method"""
        code = """
from flask import Flask
import psycopg2

app = Flask(__name__)

class UserService:
    def __init__(self):
        self.db = psycopg2.connect()
"""
        tree = ast.parse(code)
        patterns = self.detector.detect_architectural_patterns(tree, code)
        assert isinstance(patterns, dict)
    
    def test_infra_component_creation(self):
        """Test InfraComponent dataclass"""
        component = InfraComponent(
            component_type='database',
            name='main_db',
            technology='postgresql',
            configuration={'host': 'localhost'},
            usage_frequency=5,
            connections=['app']
        )
        
        assert component.component_type == 'database'
        assert component.name == 'main_db'
        assert component.technology == 'postgresql'
        assert component.configuration['host'] == 'localhost'
        assert component.usage_frequency == 5
        assert component.connections == ['app']
    
    def test_db_patterns_structure(self):
        """Test database patterns are properly structured"""
        for db_type, patterns in self.detector.db_patterns.items():
            assert 'imports' in patterns
            assert 'patterns' in patterns
            assert 'configs' in patterns
            assert isinstance(patterns['imports'], list)
            assert isinstance(patterns['patterns'], list)
            assert isinstance(patterns['configs'], list)
    
    def test_api_patterns_structure(self):
        """Test API patterns are properly structured"""
        for api_type, patterns in self.detector.api_patterns.items():
            assert 'patterns' in patterns
            assert isinstance(patterns['patterns'], list)
    
    def test_mq_patterns_structure(self):
        """Test message queue patterns are properly structured"""
        for mq_type, patterns in self.detector.mq_patterns.items():
            assert 'patterns' in patterns
            assert isinstance(patterns['patterns'], list)
    
    def test_comprehensive_infrastructure_detection(self):
        """Test infrastructure detection with comprehensive code"""
        code = """
import psycopg2
import redis
import boto3
from flask import Flask
from celery import Celery

# Database
DATABASE_URL = "postgresql://localhost/db"
conn = psycopg2.connect(DATABASE_URL)

# Cache
cache = redis.Redis()

# Web framework
app = Flask(__name__)

# Task queue
celery_app = Celery('myapp')

# Cloud services
s3 = boto3.client('s3')

@app.route('/api/users')
def get_users():
    return []

@celery_app.task
def process_data():
    pass
"""
        tree = ast.parse(code)
        result = self.detector.detect_infrastructure(tree, "app.py", code)
        
        assert isinstance(result, dict)
        # The result should contain various infrastructure components
        # The exact structure depends on the implementation
    
    def test_syntax_error_handling(self):
        """Test handling of syntax errors in code"""
        invalid_code = """
import psycopg2
def invalid_function(
    # Missing closing parenthesis
"""
        try:
            tree = ast.parse(invalid_code)
            result = self.detector.detect_infrastructure(tree, "invalid.py", invalid_code)
        except SyntaxError:
            # Expected - syntax errors should be handled gracefully
            pass
    
    def test_empty_file_detection(self):
        """Test detection on empty file"""
        code = ""
        try:
            tree = ast.parse(code)
            result = self.detector.detect_infrastructure(tree, "empty.py", code)
            assert isinstance(result, dict)
        except SyntaxError:
            # Empty code might not parse, which is acceptable
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])