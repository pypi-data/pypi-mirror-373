#!/usr/bin/env python3
"""
Design Pattern Detection for Code Indexer
"""

import ast
import re
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from .logger import log_warning


@dataclass
class PatternMatch:
    pattern_type: str
    confidence: float
    description: str
    nodes: List[str]
    location: str


class PatternDetector:
    """Detect common design patterns in code"""
    
    def __init__(self):
        self.patterns = []
        
    def detect_patterns(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect all patterns in AST"""
        patterns = []
        
        # Handle None or invalid AST
        if tree is None:
            return patterns
        
        try:
            # Detect various patterns
            patterns.extend(self._detect_singleton(tree, file_path))
            patterns.extend(self._detect_factory(tree, file_path))
            patterns.extend(self._detect_observer(tree, file_path))
            patterns.extend(self._detect_builder(tree, file_path))
            patterns.extend(self._detect_strategy(tree, file_path))
            patterns.extend(self._detect_decorator_pattern(tree, file_path))
            patterns.extend(self._detect_adapter(tree, file_path))
            patterns.extend(self._detect_mvc(tree, file_path))
        except (AttributeError, TypeError) as e:
            # Handle malformed AST gracefully
            log_warning(f"Could not detect patterns in {file_path}: {e}")
        
        return patterns
    
    def _detect_singleton(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect Singleton pattern"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for singleton characteristics
                has_instance_var = False
                has_new_override = False
                has_instance_method = False
                
                for item in node.body:
                    # Check for __new__ method override
                    if isinstance(item, ast.FunctionDef) and item.name == "__new__":
                        has_new_override = True
                    
                    # Check for getInstance or similar method
                    if isinstance(item, ast.FunctionDef) and any(keyword in item.name.lower() 
                                                               for keyword in ['instance', 'singleton']):
                        has_instance_method = True
                    
                    # Check for class variable to store instance
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and 'instance' in target.id.lower():
                                has_instance_var = True
                
                # Determine confidence
                confidence = 0.0
                if has_new_override:
                    confidence += 0.5
                if has_instance_method:
                    confidence += 0.3
                if has_instance_var:
                    confidence += 0.2
                
                if confidence >= 0.5:
                    patterns.append(PatternMatch(
                        pattern_type="Singleton",
                        confidence=confidence,
                        description=f"Class {node.name} implements Singleton pattern",
                        nodes=[node.name],
                        location=file_path
                    ))
        
        return patterns
    
    def _detect_factory(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect Factory pattern"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for factory characteristics
                has_create_method = False
                has_factory_in_name = 'factory' in node.name.lower()
                create_methods = []
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name.lower()
                        if any(keyword in method_name for keyword in ['create', 'make', 'build', 'factory']):
                            has_create_method = True
                            create_methods.append(item.name)
                
                # Check if methods return different types/classes
                confidence = 0.0
                if has_factory_in_name:
                    confidence += 0.4
                if has_create_method:
                    confidence += 0.4
                if len(create_methods) > 1:
                    confidence += 0.2
                
                if confidence >= 0.6:
                    patterns.append(PatternMatch(
                        pattern_type="Factory",
                        confidence=confidence,
                        description=f"Class {node.name} implements Factory pattern with methods: {', '.join(create_methods)}",
                        nodes=[node.name] + create_methods,
                        location=file_path
                    ))
        
        return patterns
    
    def _detect_observer(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect Observer pattern"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for observer characteristics
                has_observers_list = False
                has_notify_method = False
                has_subscribe_method = False
                observer_methods = []
                
                for item in node.body:
                    # Check in __init__ method for observers list
                    if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                        for stmt in item.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute):
                                        if hasattr(target, 'attr') and any(keyword in target.attr.lower() 
                                              for keyword in ['observer', 'listener', 'subscriber']):
                                            has_observers_list = True
                    
                    # Also check class-level assignments
                    if isinstance(item, ast.Assign):
                        # Check for observers/listeners list
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if any(keyword in target.id.lower() 
                                      for keyword in ['observer', 'listener', 'subscriber']):
                                    has_observers_list = True
                    
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name.lower()
                        if any(keyword in method_name 
                              for keyword in ['notify', 'update', 'broadcast', 'emit']):
                            has_notify_method = True
                            observer_methods.append(item.name)
                        if any(keyword in method_name 
                              for keyword in ['subscribe', 'attach', 'add_observer', 'register']):
                            has_subscribe_method = True
                            observer_methods.append(item.name)
                
                confidence = 0.0
                if has_observers_list:
                    confidence += 0.4
                if has_notify_method:
                    confidence += 0.3
                if has_subscribe_method:
                    confidence += 0.3
                
                if confidence >= 0.6:
                    patterns.append(PatternMatch(
                        pattern_type="Observer",
                        confidence=confidence,
                        description=f"Class {node.name} implements Observer pattern",
                        nodes=[node.name] + observer_methods,
                        location=file_path
                    ))
        
        return patterns
    
    def _detect_builder(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect Builder pattern"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_builder_name = 'builder' in node.name.lower()
                has_build_method = False
                has_fluent_interface = False
                builder_methods = []
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name.lower()
                        
                        if 'build' in method_name:
                            has_build_method = True
                            builder_methods.append(item.name)
                        
                        # Check for fluent interface (methods returning self)
                        for stmt in item.body:
                            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Name):
                                if stmt.value.id == 'self':
                                    has_fluent_interface = True
                                    builder_methods.append(item.name)
                
                confidence = 0.0
                if has_builder_name:
                    confidence += 0.3
                if has_build_method:
                    confidence += 0.4
                if has_fluent_interface:
                    confidence += 0.3
                
                if confidence >= 0.6:
                    patterns.append(PatternMatch(
                        pattern_type="Builder",
                        confidence=confidence,
                        description=f"Class {node.name} implements Builder pattern",
                        nodes=[node.name] + builder_methods,
                        location=file_path
                    ))
        
        return patterns
    
    def _detect_strategy(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect Strategy pattern"""
        patterns = []
        
        # Look for interfaces/abstract classes with execute/run methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_strategy_name = 'strategy' in node.name.lower()
                has_execute_method = False
                has_abstract_methods = False
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name.lower()
                        if any(keyword in method_name 
                              for keyword in ['execute', 'run', 'perform', 'apply']):
                            has_execute_method = True
                        
                        # Check for abstract method decorators
                        for decorator in item.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                                has_abstract_methods = True
                
                confidence = 0.0
                if has_strategy_name:
                    confidence += 0.4
                if has_execute_method:
                    confidence += 0.3
                if has_abstract_methods:
                    confidence += 0.3
                
                if confidence >= 0.5:
                    patterns.append(PatternMatch(
                        pattern_type="Strategy",
                        confidence=confidence,
                        description=f"Class {node.name} implements Strategy pattern",
                        nodes=[node.name],
                        location=file_path
                    ))
        
        return patterns
    
    def _detect_decorator_pattern(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect Decorator pattern (not Python decorators)"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_decorator_name = 'decorator' in node.name.lower()
                has_component_attr = False
                has_wrapped_calls = False
                
                for item in node.body:
                    # Check in __init__ for component attribute
                    if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                        for stmt in item.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute):
                                        if hasattr(target, 'attr') and any(keyword in target.attr.lower() 
                                              for keyword in ['component', 'wrapped', 'inner']):
                                            has_component_attr = True
                    
                    if isinstance(item, ast.Assign):
                        # Check for component/wrapped object
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if any(keyword in target.id.lower() 
                                      for keyword in ['component', 'wrapped', 'inner']):
                                    has_component_attr = True
                    
                    if isinstance(item, ast.FunctionDef):
                        # Check for method delegation
                        for stmt in item.body:
                            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
                                if isinstance(stmt.value.func, ast.Attribute):
                                    if hasattr(stmt.value.func.value, 'attr') and \
                                       stmt.value.func.value.attr in ['component', 'wrapped']:
                                        has_wrapped_calls = True
                            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                                if isinstance(stmt.value.func, ast.Attribute):
                                    has_wrapped_calls = True
                
                confidence = 0.0
                if has_decorator_name:
                    confidence += 0.4
                if has_component_attr:
                    confidence += 0.3
                if has_wrapped_calls:
                    confidence += 0.3
                
                if confidence >= 0.6:
                    patterns.append(PatternMatch(
                        pattern_type="Decorator",
                        confidence=confidence,
                        description=f"Class {node.name} implements Decorator pattern",
                        nodes=[node.name],
                        location=file_path
                    ))
        
        return patterns
    
    def _detect_adapter(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect Adapter pattern"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_adapter_name = 'adapter' in node.name.lower()
                has_adaptee_attr = False
                has_conversion_methods = False
                
                for item in node.body:
                    # Check in __init__ for adaptee attribute
                    if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                        for stmt in item.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute):
                                        if hasattr(target, 'attr') and any(keyword in target.attr.lower() 
                                              for keyword in ['adaptee', 'adapted', 'legacy', 'xml_parser', 'adapter']):
                                            has_adaptee_attr = True
                    
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if any(keyword in target.id.lower() 
                                      for keyword in ['adaptee', 'adapted', 'legacy']):
                                    has_adaptee_attr = True
                    
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name.lower()
                        if any(keyword in method_name 
                              for keyword in ['convert', 'adapt', 'translate', 'parse']):
                            has_conversion_methods = True
                
                confidence = 0.0
                if has_adapter_name:
                    confidence += 0.5
                if has_adaptee_attr:
                    confidence += 0.3
                if has_conversion_methods:
                    confidence += 0.2
                
                if confidence >= 0.6:
                    patterns.append(PatternMatch(
                        pattern_type="Adapter",
                        confidence=confidence,
                        description=f"Class {node.name} implements Adapter pattern",
                        nodes=[node.name],
                        location=file_path
                    ))
        
        return patterns
    
    def _detect_mvc(self, tree: ast.AST, file_path: str) -> List[PatternMatch]:
        """Detect MVC pattern components"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()
                
                # Model detection
                if any(keyword in class_name for keyword in ['model', 'entity', 'data']):
                    has_data_methods = any(
                        isinstance(item, ast.FunctionDef) and 
                        any(keyword in item.name.lower() for keyword in ['save', 'load', 'get', 'set'])
                        for item in node.body
                    )
                    
                    if has_data_methods:
                        patterns.append(PatternMatch(
                            pattern_type="MVC-Model",
                            confidence=0.7,
                            description=f"Class {node.name} appears to be MVC Model",
                            nodes=[node.name],
                            location=file_path
                        ))
                
                # View detection
                elif any(keyword in class_name for keyword in ['view', 'ui', 'template', 'widget']):
                    has_render_methods = any(
                        isinstance(item, ast.FunctionDef) and 
                        any(keyword in item.name.lower() for keyword in ['render', 'display', 'show', 'draw'])
                        for item in node.body
                    )
                    
                    if has_render_methods:
                        patterns.append(PatternMatch(
                            pattern_type="MVC-View",
                            confidence=0.7,
                            description=f"Class {node.name} appears to be MVC View",
                            nodes=[node.name],
                            location=file_path
                        ))
                
                # Controller detection
                elif any(keyword in class_name for keyword in ['controller', 'handler', 'service']):
                    has_action_methods = any(
                        isinstance(item, ast.FunctionDef) and 
                        any(keyword in item.name.lower() for keyword in ['handle', 'process', 'action', 'execute'])
                        for item in node.body
                    )
                    
                    if has_action_methods:
                        patterns.append(PatternMatch(
                            pattern_type="MVC-Controller",
                            confidence=0.7,
                            description=f"Class {node.name} appears to be MVC Controller",
                            nodes=[node.name],
                            location=file_path
                        ))
        
        return patterns