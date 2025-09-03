#!/usr/bin/env python3
"""
Rust Parser for Multi-Language Code Indexing
Using tree-sitter-rust for accurate parsing
"""

import os
from typing import Dict, List, Optional, Set
from pathlib import Path

from .base_parser import BaseParser, CodeNode, CodeRelationship, ParseResult

class RustParser(BaseParser):
    """
    Rust language parser using tree-sitter
    Provides accurate parsing of Rust code structures
    """
    
    def __init__(self):
        super().__init__('rust')
        self.supported_extensions = {'.rs'}
        self._parser = None
        self._language = None
    
    def _init_tree_sitter(self):
        """Initialize tree-sitter parser lazily"""
        if self._parser is not None:
            return True
            
        try:
            import tree_sitter
            import tree_sitter_rust
            
            # Initialize the parser
            self._language = tree_sitter.Language(tree_sitter_rust.language())
            self._parser = tree_sitter.Parser(self._language)
            return True
        except ImportError:
            return False
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions
    
    def get_supported_extensions(self) -> Set[str]:
        """Get file extensions supported by this parser"""
        return self.supported_extensions
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a Rust file and return nodes and relationships"""
        # Check if file exists first
        if not os.path.exists(file_path):
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message="Could not read file"
            )
        
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
        
        # Try to use tree-sitter if available
        if self._init_tree_sitter():
            return self._parse_with_tree_sitter(file_path, content)
        else:
            # Fallback to regex-based parsing
            return self._parse_with_regex(file_path, content)
    
    def _parse_with_tree_sitter(self, file_path: str, content: str) -> ParseResult:
        """Parse using tree-sitter for accurate AST parsing"""
        try:
            tree = self._parser.parse(bytes(content, 'utf8'))
            nodes = {}
            relationships = []
            imports = set()
            
            # Create file node
            file_name = os.path.basename(file_path)
            file_node = self._create_node(
                node_type='file',
                name=file_name,
                path=file_path,
                summary=f"Rust file: {file_name}"
            )
            nodes[file_node.id] = file_node
            
            # Walk the tree and extract nodes
            self._walk_tree(tree.root_node, file_path, content.encode('utf8'), nodes, relationships, imports, file_node.id)
            
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes=nodes,
                relationships=relationships,
                success=True
            )
        except Exception as e:
            # Fallback to regex parsing if tree-sitter fails
            return self._parse_with_regex(file_path, content)
    
    def _walk_tree(self, node, file_path: str, content: bytes, nodes: Dict, relationships: List, 
                   imports: Set, parent_id: int, class_context: Optional[str] = None):
        """Recursively walk the tree-sitter AST"""
        node_type = node.type
        
        # Function definitions
        if node_type == 'function_item':
            name_node = self._find_child_by_type(node, 'identifier')
            if name_node:
                func_name = self._get_node_text(content, name_node)
                func_id = self._create_function_node(
                    func_name, node.start_point[0] + 1, file_path, content,
                    nodes, relationships, parent_id, class_context
                )
                # Process function body
                body_node = self._find_child_by_type(node, 'block')
                if body_node:
                    self._walk_tree(body_node, file_path, content, nodes, relationships, 
                                  imports, func_id, class_context)
        
        # Struct definitions
        elif node_type == 'struct_item':
            name_node = self._find_child_by_type(node, 'type_identifier')
            if name_node:
                struct_name = self._get_node_text(content, name_node)
                struct_id = self._create_class_node(
                    struct_name, node.start_point[0] + 1, file_path, content,
                    nodes, relationships, parent_id
                )
                # Process struct fields and impl blocks
                for child in node.children:
                    self._walk_tree(child, file_path, content, nodes, relationships,
                                  imports, struct_id, struct_name)
        
        # Impl blocks
        elif node_type == 'impl_item':
            # Get the type being implemented
            type_node = self._find_child_by_type(node, 'type_identifier')
            if type_node:
                impl_type = self._get_node_text(content, type_node)
                # Process methods in impl block
                for child in node.children:
                    if child.type == 'declaration_list':
                        for method in child.children:
                            self._walk_tree(method, file_path, content, nodes, relationships,
                                          imports, parent_id, impl_type)
        
        # Trait definitions
        elif node_type == 'trait_item':
            name_node = self._find_child_by_type(node, 'type_identifier')
            if name_node:
                trait_name = self._get_node_text(content, name_node)
                trait_id = self._create_class_node(
                    trait_name, node.start_point[0] + 1, file_path, content,
                    nodes, relationships, parent_id, is_interface=True
                )
                # Process trait methods
                for child in node.children:
                    self._walk_tree(child, file_path, content, nodes, relationships,
                                  imports, trait_id, trait_name)
        
        # Enum definitions
        elif node_type == 'enum_item':
            name_node = self._find_child_by_type(node, 'type_identifier')
            if name_node:
                enum_name = self._get_node_text(content, name_node)
                enum_id = self._create_class_node(
                    enum_name, node.start_point[0] + 1, file_path, content,
                    nodes, relationships, parent_id
                )
        
        # Use statements (imports)
        elif node_type == 'use_declaration':
            use_path = self._extract_use_path(node, content)
            if use_path:
                imports.add(use_path)
                self._create_import_node(
                    use_path, node.start_point[0] + 1, file_path, content,
                    nodes, relationships, parent_id
                )
        
        # Mod declarations
        elif node_type == 'mod_item':
            name_node = self._find_child_by_type(node, 'identifier')
            if name_node:
                mod_name = self._get_node_text(content, name_node)
                mod_id = self._create_module_node(
                    mod_name, node.start_point[0] + 1, file_path, content,
                    nodes, relationships, parent_id
                )
                # Process module contents
                for child in node.children:
                    self._walk_tree(child, file_path, content, nodes, relationships,
                                  imports, mod_id, class_context)
        
        # Recursively process children for other node types
        else:
            for child in node.children:
                self._walk_tree(child, file_path, content, nodes, relationships,
                              imports, parent_id, class_context)
    
    def _parse_with_regex(self, file_path: str, content: str) -> ParseResult:
        """Fallback regex-based parsing when tree-sitter is not available"""
        import re
        
        nodes = {}
        relationships = []
        imports = []
        
        # Create file node
        file_name = os.path.basename(file_path)
        file_node = self._create_node(
            node_type='file',
            name=file_name,
            path=file_path,
            summary=f"Rust file: {file_name}"
        )
        nodes[file_node.id] = file_node
        
        lines = content.split('\n')
        
        # Regex patterns for Rust constructs
        patterns = {
            'function': r'^\s*(?:pub\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            'struct': r'^\s*(?:pub\s+)?struct\s+([A-Z][a-zA-Z0-9_]*)',
            'enum': r'^\s*(?:pub\s+)?enum\s+([A-Z][a-zA-Z0-9_]*)',
            'trait': r'^\s*(?:pub\s+)?trait\s+([A-Z][a-zA-Z0-9_]*)',
            'impl': r'^\s*impl(?:\s+<[^>]+>)?\s+(?:([A-Z][a-zA-Z0-9_]*)|<[^>]+>)',
            'use': r'^\s*use\s+([a-zA-Z0-9_:]+(?:::\{[^}]+\})?)',
            'mod': r'^\s*(?:pub\s+)?mod\s+([a-z_][a-z0-9_]*)',
        }
        
        current_impl = None
        
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('//'):
                continue
            
            # Functions
            match = re.match(patterns['function'], line)
            if match:
                func_name = match.group(1)
                func_node = self._create_node(
                    node_type='method' if current_impl else 'function',
                    name=func_name,
                    path=file_path,
                    summary=f"{'Method' if current_impl else 'Function'}: {func_name}",
                    line_number=i
                )
                nodes[func_node.id] = func_node
                
                # Add relationship
                parent_id = current_impl if current_impl else file_node.id
                rel = self._create_relationship(
                    source_id=parent_id,
                    target_id=func_node.id,
                    relationship_type='contains'
                )
                relationships.append(rel)
                continue
            
            # Structs
            match = re.match(patterns['struct'], line)
            if match:
                struct_name = match.group(1)
                struct_node = self._create_node(
                    node_type='class',
                    name=struct_name,
                    path=file_path,
                    summary=f"Struct: {struct_name}",
                    line_number=i
                )
                nodes[struct_node.id] = struct_node
                rel = self._create_relationship(
                    source_id=file_node.id,
                    target_id=struct_node.id,
                    relationship_type='contains'
                )
                relationships.append(rel)
                continue
            
            # Enums
            match = re.match(patterns['enum'], line)
            if match:
                enum_name = match.group(1)
                enum_node = self._create_node(
                    node_type='class',
                    name=enum_name,
                    path=file_path,
                    summary=f"Enum: {enum_name}",
                    line_number=i,
                    rust_type='enum'
                )
                nodes[enum_node.id] = enum_node
                rel = self._create_relationship(
                    source_id=file_node.id,
                    target_id=enum_node.id,
                    relationship_type='contains'
                )
                relationships.append(rel)
                continue
            
            # Traits
            match = re.match(patterns['trait'], line)
            if match:
                trait_name = match.group(1)
                trait_node = self._create_node(
                    node_type='interface',
                    name=trait_name,
                    path=file_path,
                    summary=f"Trait: {trait_name}",
                    line_number=i
                )
                nodes[trait_node.id] = trait_node
                rel = self._create_relationship(
                    source_id=file_node.id,
                    target_id=trait_node.id,
                    relationship_type='contains'
                )
                relationships.append(rel)
                continue
            
            # Impl blocks
            match = re.match(patterns['impl'], line)
            if match:
                impl_type = match.group(1) if match.group(1) else 'impl'
                # Try to find the corresponding struct/enum
                for node_id, node in nodes.items():
                    if node.name == impl_type and node.node_type == 'class':
                        current_impl = node_id
                        break
                continue
            
            # End of impl block
            if current_impl and line.strip() == '}':
                current_impl = None
                continue
            
            # Use statements
            match = re.match(patterns['use'], line)
            if match:
                import_path = match.group(1)
                imports.append(import_path)
                import_node = self._create_node(
                    node_type='import',
                    name=import_path,
                    path=file_path,
                    summary=f"Import: {import_path}",
                    line_number=i
                )
                nodes[import_node.id] = import_node
                rel = self._create_relationship(
                    source_id=file_node.id,
                    target_id=import_node.id,
                    relationship_type='imports'
                )
                relationships.append(rel)
                continue
            
            # Modules
            match = re.match(patterns['mod'], line)
            if match:
                mod_name = match.group(1)
                mod_node = self._create_node(
                    node_type='module',
                    name=mod_name,
                    path=file_path,
                    summary=f"Module: {mod_name}",
                    line_number=i
                )
                nodes[mod_node.id] = mod_node
                rel = self._create_relationship(
                    source_id=file_node.id,
                    target_id=mod_node.id,
                    relationship_type='contains'
                )
                relationships.append(rel)
        
        return ParseResult(
            file_path=file_path,
            language=self.language,
            nodes=nodes,
            relationships=relationships,
            success=True
        )
    
    # Helper methods for tree-sitter parsing
    def _find_child_by_type(self, node, child_type: str):
        """Find first child node of specific type"""
        for child in node.children:
            if child.type == child_type:
                return child
        return None
    
    def _get_node_text(self, content: bytes, node):
        """Get text content of a node"""
        return content[node.start_byte:node.end_byte].decode('utf8')
    
    def _extract_use_path(self, node, content: bytes):
        """Extract the import path from a use statement"""
        for child in node.children:
            if child.type in ['use_tree', 'scoped_identifier', 'identifier']:
                return self._get_node_text(content, child).replace('use ', '').replace(';', '').strip()
        return None
    
    def _create_function_node(self, name: str, line: int, file_path: str, content: bytes,
                             nodes: Dict, relationships: List, parent_id: int,
                             class_context: Optional[str] = None) -> int:
        """Create a function/method node"""
        node_type = 'method' if class_context else 'function'
        full_name = f"{class_context}::{name}" if class_context else name
        
        func_node = self._create_node(
            node_type=node_type,
            name=full_name,
            path=file_path,
            summary=f"{'Method' if class_context else 'Function'}: {full_name}",
            line_number=line,
            parent_id=parent_id
        )
        nodes[func_node.id] = func_node
        
        rel = self._create_relationship(
            source_id=parent_id,
            target_id=func_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
        
        return func_node.id
    
    def _create_class_node(self, name: str, line: int, file_path: str, content: bytes,
                          nodes: Dict, relationships: List, parent_id: int,
                          is_interface: bool = False) -> int:
        """Create a class/struct/trait node"""
        node_type = 'interface' if is_interface else 'class'
        
        class_node = self._create_node(
            node_type=node_type,
            name=name,
            path=file_path,
            summary=f"{'Trait' if is_interface else 'Struct'}: {name}",
            line_number=line,
            parent_id=parent_id
        )
        nodes[class_node.id] = class_node
        
        rel = self._create_relationship(
            source_id=parent_id,
            target_id=class_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
        
        return class_node.id
    
    def _create_import_node(self, import_path: str, line: int, file_path: str, content: bytes,
                           nodes: Dict, relationships: List, parent_id: int) -> int:
        """Create an import node"""
        import_node = self._create_node(
            node_type='import',
            name=import_path,
            path=file_path,
            summary=f"Import: {import_path}",
            line_number=line,
            parent_id=parent_id
        )
        nodes[import_node.id] = import_node
        
        rel = self._create_relationship(
            source_id=parent_id,
            target_id=import_node.id,
            relationship_type='imports'
        )
        relationships.append(rel)
        
        return import_node.id
    
    def _create_module_node(self, name: str, line: int, file_path: str, content: bytes,
                           nodes: Dict, relationships: List, parent_id: int) -> int:
        """Create a module node"""
        mod_node = self._create_node(
            node_type='module',
            name=name,
            path=file_path,
            summary=f"Module: {name}",
            line_number=line,
            parent_id=parent_id
        )
        nodes[mod_node.id] = mod_node
        
        rel = self._create_relationship(
            source_id=parent_id,
            target_id=mod_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
        
        return mod_node.id