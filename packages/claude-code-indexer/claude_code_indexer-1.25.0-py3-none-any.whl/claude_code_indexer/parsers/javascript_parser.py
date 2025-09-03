#!/usr/bin/env python3
"""
JavaScript/TypeScript Parser for Multi-Language Code Indexing
Uses regex-based parsing for basic code structure analysis
"""

import re
import os
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from .base_parser import BaseParser, CodeNode, CodeRelationship, ParseResult

class JavaScriptParser(BaseParser):
    """
    JavaScript/TypeScript language parser using regex
    Part of Composite Pattern - Leaf class
    """
    
    def __init__(self):
        super().__init__('javascript')
        self.supported_extensions = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
        self.parse_errors = []  # Track parsing errors
        
        # Enhanced regex patterns for modern JS/TS syntax
        self.patterns = {
            # Enhanced import patterns
            'import': re.compile(r'import\s+(?:(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)(?:\s*,\s*(?:\{[^}]*\}|\*\s+as\s+\w+|\w+))*\s+from\s+[\'"]([^\'"]+)[\'"]|import\s+[\'"]([^\'"]+)[\'"])', re.MULTILINE),
            'dynamic_import': re.compile(r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', re.MULTILINE),
            'require': re.compile(r'(?:const|let|var)\s+(?:\{[^}]*\}|\w+)\s*=\s*require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', re.MULTILINE),
            
            # Enhanced export patterns
            'export': re.compile(r'export\s+(?:default\s+)?(?:abstract\s+)?(?:class|function|const|let|var|interface|type|enum)\s+(\w+)', re.MULTILINE),
            'export_all': re.compile(r'export\s*\*\s*(?:as\s+(\w+)\s+)?from\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE),
            
            # Enhanced class patterns (including React components)
            'class': re.compile(r'(?:export\s+(?:default\s+)?)?(?:abstract\s+)?class\s+(\w+)(?:<[^>]+>)?(?:\s+extends\s+(\w+)(?:<[^>]+>)?)?(?:\s+implements\s+([^{]+))?\s*\{', re.MULTILINE),
            
            # Enhanced function patterns
            'function': re.compile(r'(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s*(?:\*\s*)?(\w+)?\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{', re.MULTILINE),
            'arrow_function': re.compile(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*(?::\s*[^=]+)?\s*=\s*(?:async\s+)?(?:<[^>]+>\s*)?\([^)]*\)\s*(?::\s*[^=]+)?\s*=>(?:\s*\{|[^;\n]+)', re.MULTILINE),
            'arrow_function_simple': re.compile(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(\w+)\s*=>(?:\s*\{|[^;\n]+)', re.MULTILINE),
            
            # Enhanced method patterns
            'method': re.compile(r'(?:(?:public|private|protected|static|readonly|async|get|set)\s+)*(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{', re.MULTILINE),
            'method_shorthand': re.compile(r'(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{', re.MULTILINE),
            
            # TypeScript specific patterns
            'interface': re.compile(r'(?:export\s+)?interface\s+(\w+)(?:<[^>]+>)?(?:\s+extends\s+([^{]+))?\s*\{', re.MULTILINE),
            'type': re.compile(r'(?:export\s+)?type\s+(\w+)(?:<[^>]+>)?\s*=', re.MULTILINE),
            'enum': re.compile(r'(?:export\s+)?(?:const\s+)?enum\s+(\w+)\s*\{', re.MULTILINE),
            'namespace': re.compile(r'(?:export\s+)?(?:namespace|module)\s+(\w+)\s*\{', re.MULTILINE),
            
            # React/JSX patterns
            'react_component': re.compile(r'(?:export\s+(?:default\s+)?)?(?:const|let|var|function)\s+(\w+)\s*(?::\s*(?:React\.)?(?:FC|FunctionComponent|Component)[^=]*)?\s*=\s*(?:\([^)]*\)\s*(?::\s*[^=]+)?\s*=>|function)', re.MULTILINE),
            'jsx_element': re.compile(r'<(\w+)(?:\s+[^>]*)?>(?:[^<]*<\/\1>)?', re.MULTILINE),
        }
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions
    
    def get_supported_extensions(self) -> Set[str]:
        """Get file extensions supported by this parser"""
        return self.supported_extensions
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a JavaScript/TypeScript file and return nodes and relationships"""
        self.parse_errors = []  # Reset errors for this file
        
        if self._is_binary_file(file_path):
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message="Binary file detected"
            )
        
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
        
        # Remove comments to avoid false matches
        content = self._remove_comments(content)
        
        nodes = {}
        relationships = []
        
        # Determine if it's TypeScript
        is_typescript = Path(file_path).suffix.lower() in {'.ts', '.tsx'}
        language = 'typescript' if is_typescript else 'javascript'
        
        # Create file node
        file_node = self._create_node(
            node_type='file',
            name=os.path.basename(file_path),
            path=file_path,
            summary=f"{language.title()} file: {os.path.basename(file_path)}",
            is_typescript=is_typescript
        )
        nodes[file_node.id] = file_node
        
        # Parse different constructs with error handling
        try:
            self._parse_imports(content, file_node, file_path, nodes, relationships)
        except Exception as e:
            self.parse_errors.append(f"Error parsing imports: {str(e)}")
            
        try:
            self._parse_classes(content, file_node, file_path, nodes, relationships)
        except Exception as e:
            self.parse_errors.append(f"Error parsing classes: {str(e)}")
            
        try:
            self._parse_functions(content, file_node, file_path, nodes, relationships)
        except Exception as e:
            self.parse_errors.append(f"Error parsing functions: {str(e)}")
            
        try:
            self._parse_react_components(content, file_node, file_path, nodes, relationships)
        except Exception as e:
            self.parse_errors.append(f"Error parsing React components: {str(e)}")
        
        if is_typescript:
            try:
                self._parse_interfaces(content, file_node, file_path, nodes, relationships)
            except Exception as e:
                self.parse_errors.append(f"Error parsing interfaces: {str(e)}")
                
            try:
                self._parse_types(content, file_node, file_path, nodes, relationships)
            except Exception as e:
                self.parse_errors.append(f"Error parsing types: {str(e)}")
                
            try:
                self._parse_enums(content, file_node, file_path, nodes, relationships)
            except Exception as e:
                self.parse_errors.append(f"Error parsing enums: {str(e)}")
                
            try:
                self._parse_namespaces(content, file_node, file_path, nodes, relationships)
            except Exception as e:
                self.parse_errors.append(f"Error parsing namespaces: {str(e)}")
        
        # Include any parsing errors in the result
        success = len(self.parse_errors) == 0
        error_message = '; '.join(self.parse_errors) if self.parse_errors else None
        
        return ParseResult(
            file_path=file_path,
            language=language,
            nodes=nodes,
            relationships=relationships,
            success=success,
            error_message=error_message
        )
    
    def _remove_comments(self, content: str) -> str:
        """Remove single-line and multi-line comments while preserving JSX"""
        # More careful comment removal to avoid breaking JSX
        # Remove single-line comments that aren't in strings
        content = re.sub(r'(?<!["\'`])//.*$', '', content, flags=re.MULTILINE)
        # Remove multi-line comments
        content = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', content, flags=re.DOTALL)
        return content
    
    def _get_line_number(self, content: str, position: int) -> int:
        """Get line number for a position in the content"""
        return content[:position].count('\\n') + 1
    
    def _parse_imports(self, content: str, parent_node: CodeNode, file_path: str,
                      nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse import statements"""
        # ES6 imports
        for match in self.patterns['import'].finditer(content):
            module_name = match.group(1) or match.group(2)
            if module_name:
                import_node = self._create_node(
                    node_type='import',
                    name=module_name,
                    path=file_path,
                    summary=f"Import: {module_name}",
                    line_number=self._get_line_number(content, match.start()),
                    parent_id=parent_node.id,
                    import_type='es6',
                    full_statement=match.group(0)
                )
                nodes[import_node.id] = import_node
                
                rel = self._create_relationship(
                    source_id=parent_node.id,
                    target_id=import_node.id,
                    relationship_type='imports'
                )
                relationships.append(rel)
        
        # CommonJS requires
        for match in self.patterns['require'].finditer(content):
            module_name = match.group(1)
            import_node = self._create_node(
                node_type='import',
                name=module_name,
                path=file_path,
                summary=f"Require: {module_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id,
                import_type='commonjs',
                full_statement=match.group(0)
            )
            nodes[import_node.id] = import_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=import_node.id,
                relationship_type='imports'
            )
            relationships.append(rel)
    
    def _parse_classes(self, content: str, parent_node: CodeNode, file_path: str,
                      nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse class definitions"""
        for match in self.patterns['class'].finditer(content):
            class_name = match.group(1)
            extends_class = match.group(2)
            implements_interfaces = match.group(3)
            
            class_node = self._create_node(
                node_type='class',
                name=class_name,
                path=file_path,
                summary=f"Class: {class_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id,
                extends=extends_class,
                implements=implements_interfaces.split(',') if implements_interfaces else []
            )
            nodes[class_node.id] = class_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=class_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
            
            # Parse methods within class
            self._parse_class_methods(content, class_node, file_path, nodes, relationships, match.start())
    
    def _parse_class_methods(self, content: str, class_node: CodeNode, file_path: str,
                            nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                            class_start: int):
        """Parse methods within a class"""
        # Find class body
        class_body_start = content.find('{', class_start)
        if class_body_start == -1:
            return
        
        # Find matching closing brace
        brace_count = 1
        class_body_end = class_body_start + 1
        while class_body_end < len(content) and brace_count > 0:
            if content[class_body_end] == '{':
                brace_count += 1
            elif content[class_body_end] == '}':
                brace_count -= 1
            class_body_end += 1
        
        class_body = content[class_body_start:class_body_end]
        
        # Parse methods
        for match in self.patterns['method'].finditer(class_body):
            method_name = match.group(1)
            
            # Skip constructor and common non-method patterns
            if method_name in ['constructor', 'if', 'for', 'while', 'switch', 'catch']:
                continue
            
            method_node = self._create_node(
                node_type='method',
                name=f"{class_node.name}.{method_name}",
                path=file_path,
                summary=f"Method: {class_node.name}.{method_name}",
                line_number=self._get_line_number(content, class_body_start + match.start()),
                parent_id=class_node.id,
                class_name=class_node.name,
                method_name=method_name
            )
            nodes[method_node.id] = method_node
            
            rel = self._create_relationship(
                source_id=class_node.id,
                target_id=method_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _parse_functions(self, content: str, parent_node: CodeNode, file_path: str,
                        nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse function definitions"""
        # Regular functions
        for match in self.patterns['function'].finditer(content):
            function_name = match.group(1)
            
            function_node = self._create_node(
                node_type='function',
                name=function_name,
                path=file_path,
                summary=f"Function: {function_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id,
                function_type='regular'
            )
            nodes[function_node.id] = function_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=function_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
        
        # Arrow functions
        for match in self.patterns['arrow_function'].finditer(content):
            function_name = match.group(1)
            
            function_node = self._create_node(
                node_type='function',
                name=function_name,
                path=file_path,
                summary=f"Arrow function: {function_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id,
                function_type='arrow'
            )
            nodes[function_node.id] = function_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=function_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _parse_react_components(self, content: str, parent_node: CodeNode, file_path: str,
                               nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse React components"""
        for match in self.patterns['react_component'].finditer(content):
            component_name = match.group(1)
            
            # Skip if already parsed as function/class
            if any(node.name == component_name for node in nodes.values() 
                   if node.node_type in ('class', 'function')):
                continue
            
            component_node = self._create_node(
                node_type='function',  # React components are functions
                name=component_name,
                path=file_path,
                summary=f"React Component: {component_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id,
                function_type='react_component'
            )
            nodes[component_node.id] = component_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=component_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _parse_interfaces(self, content: str, parent_node: CodeNode, file_path: str,
                         nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse TypeScript interface definitions"""
        for match in self.patterns['interface'].finditer(content):
            interface_name = match.group(1)
            extends_interfaces = match.group(2)
            
            interface_node = self._create_node(
                node_type='interface',
                name=interface_name,
                path=file_path,
                summary=f"Interface: {interface_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id,
                extends=extends_interfaces.split(',') if extends_interfaces else []
            )
            nodes[interface_node.id] = interface_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=interface_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _parse_types(self, content: str, parent_node: CodeNode, file_path: str,
                    nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse TypeScript type definitions"""
        for match in self.patterns['type'].finditer(content):
            type_name = match.group(1)
            
            type_node = self._create_node(
                node_type='type',
                name=type_name,
                path=file_path,
                summary=f"Type: {type_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id
            )
            nodes[type_node.id] = type_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=type_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _parse_enums(self, content: str, parent_node: CodeNode, file_path: str,
                    nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse TypeScript enum definitions"""
        for match in self.patterns['enum'].finditer(content):
            enum_name = match.group(1)
            
            enum_node = self._create_node(
                node_type='enum',
                name=enum_name,
                path=file_path,
                summary=f"Enum: {enum_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id
            )
            nodes[enum_node.id] = enum_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=enum_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _parse_namespaces(self, content: str, parent_node: CodeNode, file_path: str,
                         nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse TypeScript namespace definitions"""
        for match in self.patterns['namespace'].finditer(content):
            namespace_name = match.group(1)
            
            namespace_node = self._create_node(
                node_type='namespace',
                name=namespace_name,
                path=file_path,
                summary=f"Namespace: {namespace_name}",
                line_number=self._get_line_number(content, match.start()),
                parent_id=parent_node.id
            )
            nodes[namespace_node.id] = namespace_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=namespace_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)