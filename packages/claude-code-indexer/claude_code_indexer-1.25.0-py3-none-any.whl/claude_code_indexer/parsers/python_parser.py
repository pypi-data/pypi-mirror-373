#!/usr/bin/env python3
"""
Python Parser for Multi-Language Code Indexing
Concrete implementation using AST parsing
"""

import ast
import os
from typing import Dict, List, Optional, Set
from pathlib import Path

from .base_parser import BaseParser, CodeNode, CodeRelationship, ParseResult

class PythonParser(BaseParser):
    """
    Python language parser using AST
    Part of Composite Pattern - Leaf class
    """
    
    def __init__(self):
        super().__init__('python')
        self.supported_extensions = {'.py', '.pyx', '.pyi', '.pyw'}
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions
    
    def get_supported_extensions(self) -> Set[str]:
        """Get file extensions supported by this parser"""
        return self.supported_extensions
    
    def parse_file(self, file_path: str) -> ParseResult:
        content = self._read_file_safely(file_path)
        if content is None:
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message="Could not read file"
            )
        
        try:
            tree = ast.parse(content)
        except (SyntaxError, ValueError) as e:
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message=f"Parse error: {str(e)}"
            )
        
        nodes = {}
        relationships = []
        
        # Create file node
        file_node = self._create_node(
            node_type='file',
            name=os.path.basename(file_path),
            path=file_path,
            summary=f"Python file: {os.path.basename(file_path)}"
        )
        nodes[file_node.id] = file_node
        
        # Parse AST nodes
        self._parse_ast_nodes(tree, file_node, file_path, nodes, relationships)
        
        return ParseResult(
            file_path=file_path,
            language=self.language,
            nodes=nodes,
            relationships=relationships,
            success=True
        )
    
    def _parse_ast_nodes(self, tree: ast.AST, parent_node: CodeNode, file_path: str, 
                        nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse AST nodes recursively"""
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self._handle_import(node, parent_node, file_path, nodes, relationships)
            
            elif isinstance(node, ast.ImportFrom):
                self._handle_import_from(node, parent_node, file_path, nodes, relationships)
            
            elif isinstance(node, ast.ClassDef):
                self._handle_class_def(node, parent_node, file_path, nodes, relationships)
            
            elif isinstance(node, ast.FunctionDef):
                self._handle_function_def(node, parent_node, file_path, nodes, relationships)
            
            elif isinstance(node, ast.AsyncFunctionDef):
                self._handle_async_function_def(node, parent_node, file_path, nodes, relationships)
    
    def _handle_import(self, node: ast.Import, parent_node: CodeNode, file_path: str,
                      nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Handle import statements"""
        for alias in node.names:
            import_node = self._create_node(
                node_type='import',
                name=alias.name,
                path=file_path,
                summary=f"Import: {alias.name}",
                line_number=node.lineno,
                column_number=node.col_offset,
                parent_id=parent_node.id,
                alias=alias.asname if alias.asname else None
            )
            nodes[import_node.id] = import_node
            
            # Create relationship
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=import_node.id,
                relationship_type='imports'
            )
            relationships.append(rel)
    
    def _handle_import_from(self, node: ast.ImportFrom, parent_node: CodeNode, file_path: str,
                           nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Handle from...import statements"""
        if node.module:
            import_node = self._create_node(
                node_type='import',
                name=node.module,
                path=file_path,
                summary=f"Import from: {node.module}",
                line_number=node.lineno,
                column_number=node.col_offset,
                parent_id=parent_node.id,
                import_type='from',
                names=[alias.name for alias in node.names]
            )
            nodes[import_node.id] = import_node
            
            # Create relationship
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=import_node.id,
                relationship_type='imports'
            )
            relationships.append(rel)
    
    def _handle_class_def(self, node: ast.ClassDef, parent_node: CodeNode, file_path: str,
                         nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Handle class definitions"""
        # Get base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(ast.unparse(base) if hasattr(ast, 'unparse') else str(base))
        
        class_node = self._create_node(
            node_type='class',
            name=node.name,
            path=file_path,
            summary=f"Class: {node.name}",
            line_number=node.lineno,
            column_number=node.col_offset,
            parent_id=parent_node.id,
            base_classes=base_classes,
            decorators=[ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
        )
        nodes[class_node.id] = class_node
        
        # Create relationship with parent
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=class_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
        
        # Parse methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._handle_method_def(item, class_node, file_path, nodes, relationships)
            elif isinstance(item, ast.AsyncFunctionDef):
                self._handle_async_method_def(item, class_node, file_path, nodes, relationships)
    
    def _handle_function_def(self, node: ast.FunctionDef, parent_node: CodeNode, file_path: str,
                            nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Handle function definitions"""
        # Skip if this is a method (handled separately)
        if isinstance(parent_node, CodeNode) and parent_node.node_type == 'class':
            return
        
        function_node = self._create_node(
            node_type='function',
            name=node.name,
            path=file_path,
            summary=f"Function: {node.name}",
            line_number=node.lineno,
            column_number=node.col_offset,
            parent_id=parent_node.id,
            args=[arg.arg for arg in node.args.args],
            decorators=[ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
        )
        nodes[function_node.id] = function_node
        
        # Create relationship with parent
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=function_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
    
    def _handle_async_function_def(self, node: ast.AsyncFunctionDef, parent_node: CodeNode, file_path: str,
                                  nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Handle async function definitions"""
        # Skip if this is a method (handled separately)
        if isinstance(parent_node, CodeNode) and parent_node.node_type == 'class':
            return
        
        function_node = self._create_node(
            node_type='function',
            name=node.name,
            path=file_path,
            summary=f"Async function: {node.name}",
            line_number=node.lineno,
            column_number=node.col_offset,
            parent_id=parent_node.id,
            is_async=True,
            args=[arg.arg for arg in node.args.args],
            decorators=[ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
        )
        nodes[function_node.id] = function_node
        
        # Create relationship with parent
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=function_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
    
    def _handle_method_def(self, node: ast.FunctionDef, class_node: CodeNode, file_path: str,
                          nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Handle method definitions within classes"""
        method_node = self._create_node(
            node_type='method',
            name=f"{class_node.name}.{node.name}",
            path=file_path,
            summary=f"Method: {class_node.name}.{node.name}",
            line_number=node.lineno,
            column_number=node.col_offset,
            parent_id=class_node.id,
            class_name=class_node.name,
            method_name=node.name,
            args=[arg.arg for arg in node.args.args],
            decorators=[ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
        )
        nodes[method_node.id] = method_node
        
        # Create relationship with class
        rel = self._create_relationship(
            source_id=class_node.id,
            target_id=method_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
    
    def _handle_async_method_def(self, node: ast.AsyncFunctionDef, class_node: CodeNode, file_path: str,
                                nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Handle async method definitions within classes"""
        method_node = self._create_node(
            node_type='method',
            name=f"{class_node.name}.{node.name}",
            path=file_path,
            summary=f"Async method: {class_node.name}.{node.name}",
            line_number=node.lineno,
            column_number=node.col_offset,
            parent_id=class_node.id,
            class_name=class_node.name,
            method_name=node.name,
            is_async=True,
            args=[arg.arg for arg in node.args.args],
            decorators=[ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
        )
        nodes[method_node.id] = method_node
        
        # Create relationship with class
        rel = self._create_relationship(
            source_id=class_node.id,
            target_id=method_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)