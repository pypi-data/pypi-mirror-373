#!/usr/bin/env python3
"""
Comprehensive tests for PatternDetector
Goal: Increase coverage from 10% to 80%+
"""

import ast
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Mock ensmallen before importing to avoid logger conflicts
sys.modules['ensmallen'] = MagicMock()

from claude_code_indexer.pattern_detector import PatternDetector, PatternMatch


class TestPatternDetector:
    """Test suite for PatternDetector"""
    
    @pytest.fixture
    def detector(self):
        """Create PatternDetector instance"""
        return PatternDetector()
    
    def test_initialization(self, detector):
        """Test PatternDetector initialization"""
        assert detector is not None
        assert detector.patterns == []
    
    def test_detect_patterns_with_none(self, detector):
        """Test pattern detection with None AST"""
        patterns = detector.detect_patterns(None, "test.py")
        assert patterns == []
    
    def test_detect_patterns_with_invalid_ast(self, detector):
        """Test pattern detection with invalid AST"""
        # Pass invalid object
        patterns = detector.detect_patterns("not an AST", "test.py")
        assert patterns == []
    
    def test_detect_singleton_pattern(self, detector):
        """Test Singleton pattern detection"""
        code = '''
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_instance(cls):
        return cls._instance
'''
        tree = ast.parse(code)
        patterns = detector._detect_singleton(tree, "test.py")
        
        assert len(patterns) > 0
        assert patterns[0].pattern_type == "Singleton"
        assert patterns[0].confidence >= 0.5
        assert "DatabaseConnection" in patterns[0].nodes
    
    def test_detect_factory_pattern(self, detector):
        """Test Factory pattern detection"""
        code = '''
class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
            
class ProductFactory:
    def create_product(self, product_type):
        return Product(product_type)
'''
        tree = ast.parse(code)
        patterns = detector._detect_factory(tree, "test.py")
        
        assert len(patterns) >= 1
        assert any(p.pattern_type == "Factory" for p in patterns)
    
    def test_detect_observer_pattern(self, detector):
        """Test Observer pattern detection"""
        code = '''
class Subject:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def detach(self, observer):
        self.observers.remove(observer)
    
    def notify(self):
        for observer in self.observers:
            observer.update(self)

class EventEmitter:
    def subscribe(self, listener):
        pass
    
    def unsubscribe(self, listener):
        pass
    
    def emit(self, event):
        pass
'''
        tree = ast.parse(code)
        patterns = detector._detect_observer(tree, "test.py")
        
        assert len(patterns) >= 1
        assert any(p.pattern_type == "Observer" for p in patterns)
    
    def test_detect_builder_pattern(self, detector):
        """Test Builder pattern detection"""
        code = '''
class QueryBuilder:
    def __init__(self):
        self.query = ""
    
    def select(self, columns):
        self.query += f"SELECT {columns} "
        return self
    
    def where(self, condition):
        self.query += f"WHERE {condition} "
        return self
    
    def build(self):
        return self.query

class CarBuilder:
    def with_engine(self, engine):
        self.engine = engine
        return self
    
    def with_color(self, color):
        self.color = color
        return self
    
    def build(self):
        return Car(self.engine, self.color)
'''
        tree = ast.parse(code)
        patterns = detector._detect_builder(tree, "test.py")
        
        assert len(patterns) >= 1
        assert any(p.pattern_type == "Builder" for p in patterns)
    
    def test_detect_strategy_pattern(self, detector):
        """Test Strategy pattern detection"""
        code = '''
class PaymentStrategy:
    def execute(self, amount):
        raise NotImplementedError

class CreditCardStrategy(PaymentStrategy):
    def execute(self, amount):
        return f"Paid {amount} with credit card"

class PayPalStrategy(PaymentStrategy):
    def execute(self, amount):
        return f"Paid {amount} with PayPal"

class PaymentProcessor:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def process(self, amount):
        return self.strategy.execute(amount)
'''
        tree = ast.parse(code)
        patterns = detector._detect_strategy(tree, "test.py")
        
        assert len(patterns) >= 1
        assert any(p.pattern_type == "Strategy" for p in patterns)
    
    def test_detect_decorator_pattern(self, detector):
        """Test Decorator pattern detection"""
        code = '''
class Component:
    def operation(self):
        pass

class BaseDecorator(Component):
    def __init__(self, component):
        self.component = component
    
    def operation(self):
        return self.component.operation()

class ConcreteDecorator(BaseDecorator):
    def operation(self):
        result = super().operation()
        return f"Decorated({result})"
'''
        tree = ast.parse(code)
        patterns = detector._detect_decorator_pattern(tree, "test.py")
        
        assert len(patterns) >= 1
        assert any(p.pattern_type == "Decorator" for p in patterns)
    
    def test_detect_adapter_pattern(self, detector):
        """Test Adapter pattern detection"""
        code = '''
class OldInterface:
    def old_method(self):
        pass

class NewInterface:
    def new_method(self):
        pass

class Adapter(NewInterface):
    def __init__(self, adaptee):
        self.adaptee = adaptee
    
    def new_method(self):
        return self.adaptee.old_method()

class XMLToJSONAdapter:
    def __init__(self, xml_parser):
        self.xml_parser = xml_parser
        self.adapter = "adapter"
    
    def parse(self):
        xml_data = self.xml_parser.parse_xml()
        return self.convert_to_json(xml_data)
'''
        tree = ast.parse(code)
        patterns = detector._detect_adapter(tree, "test.py")
        
        assert len(patterns) >= 1
        assert any(p.pattern_type == "Adapter" for p in patterns)
    
    def test_detect_mvc_pattern(self, detector):
        """Test MVC pattern detection"""
        code = '''
class UserModel:
    def get_user(self, id):
        return {"id": id, "name": "John"}

class UserView:
    def render(self, user):
        return f"User: {user['name']}"

class UserController:
    def __init__(self):
        self.model = UserModel()
        self.view = UserView()
    
    def show_user(self, id):
        user = self.model.get_user(id)
        return self.view.render(user)
'''
        tree = ast.parse(code)
        patterns = detector._detect_mvc(tree, "test.py")
        
        assert len(patterns) >= 1
        assert any(p.pattern_type.startswith("MVC") for p in patterns)
    
    def test_detect_all_patterns(self, detector):
        """Test detecting all patterns in one file"""
        code = '''
# Singleton
class Config:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Factory
class ShapeFactory:
    def create_shape(self, shape_type):
        if shape_type == "circle":
            return Circle()
        return Square()

# Observer
class EventManager:
    def __init__(self):
        self.observers = []
    
    def subscribe(self, observer):
        self.observers.append(observer)
    
    def notify(self):
        for obs in self.observers:
            obs.update()
'''
        tree = ast.parse(code)
        patterns = detector.detect_patterns(tree, "test.py")
        
        # Should detect multiple patterns
        assert len(patterns) >= 3
        pattern_types = {p.pattern_type for p in patterns}
        assert "Singleton" in pattern_types
        assert "Factory" in pattern_types
        assert "Observer" in pattern_types
    
    def test_pattern_match_dataclass(self):
        """Test PatternMatch dataclass"""
        match = PatternMatch(
            pattern_type="Singleton",
            confidence=0.8,
            description="Test pattern",
            nodes=["TestClass"],
            location="test.py"
        )
        
        assert match.pattern_type == "Singleton"
        assert match.confidence == 0.8
        assert match.description == "Test pattern"
        assert match.nodes == ["TestClass"]
        assert match.location == "test.py"
    
    def test_malformed_ast_handling(self, detector):
        """Test handling of malformed AST"""
        # Create a mock AST that will cause AttributeError
        class BadAST:
            def __iter__(self):
                raise AttributeError("Malformed AST")
        
        patterns = detector.detect_patterns(BadAST(), "test.py")
        assert patterns == []
    
    def test_singleton_variations(self, detector):
        """Test different variations of Singleton pattern"""
        # Variation 1: Using getInstance method
        code1 = '''
class Logger:
    _instance = None
    
    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance
'''
        tree = ast.parse(code1)
        patterns = detector._detect_singleton(tree, "test.py")
        assert len(patterns) > 0
        
        # Variation 2: Using __instance private variable
        code2 = '''
class Database:
    __instance = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
'''
        tree = ast.parse(code2)
        patterns = detector._detect_singleton(tree, "test.py")
        assert len(patterns) > 0
    
    def test_factory_variations(self, detector):
        """Test different variations of Factory pattern"""
        # Abstract Factory
        code = '''
class AbstractFactory:
    def create_product_a(self):
        raise NotImplementedError
    
    def create_product_b(self):
        raise NotImplementedError

class ConcreteFactory1(AbstractFactory):
    def create_product_a(self):
        return ProductA1()
    
    def create_product_b(self):
        return ProductB1()
'''
        tree = ast.parse(code)
        patterns = detector._detect_factory(tree, "test.py")
        assert len(patterns) >= 1
    
    def test_empty_file(self, detector):
        """Test pattern detection on empty file"""
        tree = ast.parse("")
        patterns = detector.detect_patterns(tree, "empty.py")
        assert patterns == []
    
    def test_no_patterns_file(self, detector):
        """Test file with no design patterns"""
        code = '''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

x = 10
y = 20
result = add(x, y)
'''
        tree = ast.parse(code)
        patterns = detector.detect_patterns(tree, "simple.py")
        assert patterns == []
    
    def test_confidence_calculation(self, detector):
        """Test confidence calculation for patterns"""
        # High confidence Singleton
        code = '''
class HighConfidenceSingleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        return cls._instance
'''
        tree = ast.parse(code)
        patterns = detector._detect_singleton(tree, "test.py")
        assert len(patterns) > 0
        assert patterns[0].confidence >= 0.8  # Should have high confidence
    
    def test_pattern_location(self, detector):
        """Test that pattern location is correctly set"""
        code = '''
class TestPattern:
    def create(self, type):
        return Object(type)
'''
        tree = ast.parse(code)
        patterns = detector._detect_factory(tree, "/path/to/file.py")
        
        if patterns:
            assert patterns[0].location == "/path/to/file.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])