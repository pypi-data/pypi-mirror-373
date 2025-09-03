#!/usr/bin/env python3
"""
AutoIt Parser for Multi-Language Code Indexing
Uses regex-based parsing for AutoIt script analysis
"""

import re
import os
from typing import Dict, List, Optional, Set
from pathlib import Path

from .base_parser import BaseParser, CodeNode, CodeRelationship, ParseResult

class AutoItParser(BaseParser):
    """
    AutoIt language parser using regex
    Part of Composite Pattern - Leaf class
    """
    
    def __init__(self):
        super().__init__('autoit')
        self.supported_extensions = {'.au3', '.aut', '.a3x'}
        self.parse_errors = []  # Track parsing errors
        
        # AutoIt-specific regex patterns (case-insensitive)
        self.patterns = {
            # Include patterns
            'include': re.compile(r'#include\s+[<"]([^>"]+)[>"]', re.MULTILINE | re.IGNORECASE),
            'include_once': re.compile(r'#include-once', re.MULTILINE | re.IGNORECASE),
            
            # Function patterns
            'function': re.compile(r'Func\s+(\w+)\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            'endfunc': re.compile(r'EndFunc', re.MULTILINE | re.IGNORECASE),
            
            # Variable declarations
            'global_var': re.compile(r'Global\s+(?:Const\s+)?(\$\w+)(?:\s*=\s*[^;\r\n]+)?', re.MULTILINE | re.IGNORECASE),
            'local_var': re.compile(r'Local\s+(?:Const\s+)?(\$\w+)(?:\s*=\s*[^;\r\n]+)?', re.MULTILINE | re.IGNORECASE),
            'dim_var': re.compile(r'Dim\s+(\$\w+)(?:\s*=\s*[^;\r\n]+)?', re.MULTILINE | re.IGNORECASE),
            'static_var': re.compile(r'Static\s+(\$\w+)(?:\s*=\s*[^;\r\n]+)?', re.MULTILINE | re.IGNORECASE),
            
            # Function calls (basic pattern)
            'func_call': re.compile(r'(\w+)\s*\([^)]*\)', re.MULTILINE),
            
            # GUI patterns
            'gui_create': re.compile(r'GUICreate\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            'gui_ctrl': re.compile(r'GUICtrlCreate(\w+)\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            'gui_set': re.compile(r'GUISet(\w+)\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            
            # Registry patterns
            'reg_read': re.compile(r'RegRead\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            'reg_write': re.compile(r'RegWrite\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            
            # File operations
            'file_open': re.compile(r'FileOpen\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            'file_read': re.compile(r'FileRead(?:Line)?\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            'file_write': re.compile(r'FileWrite(?:Line)?\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            
            # Hotkey patterns
            'hotkey_set': re.compile(r'HotKeySet\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            
            # COM object patterns
            'obj_create': re.compile(r'ObjCreate\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            'obj_get': re.compile(r'ObjGet\s*\([^)]*\)', re.MULTILINE | re.IGNORECASE),
            
            # Control structures
            'if_stmt': re.compile(r'If\s+[^Then]*Then', re.MULTILINE | re.IGNORECASE),
            'while_loop': re.compile(r'While\s+[^;\r\n]+', re.MULTILINE | re.IGNORECASE),
            'for_loop': re.compile(r'For\s+\$\w+\s*=\s*[^To]*To\s*[^;\r\n]+', re.MULTILINE | re.IGNORECASE),
            'select_case': re.compile(r'Select\s*$', re.MULTILINE | re.IGNORECASE),
            
            # Comments
            'comment_single': re.compile(r';.*$', re.MULTILINE),
            'comment_block': re.compile(r'#(?:comments-start|cs).*?#(?:comments-end|ce)', re.DOTALL | re.IGNORECASE),
        }
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions
    
    def get_supported_extensions(self) -> Set[str]:
        """Get file extensions supported by this parser"""
        return self.supported_extensions
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse an AutoIt file and return nodes and relationships"""
        self.parse_errors = []  # Reset errors for this file
        
        # Check if file exists first
        if not os.path.exists(file_path):
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message="File not found"
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
        
        # Remove comments to avoid false matches
        content = self._remove_comments(content)
        
        nodes = {}
        relationships = []
        
        # Create file node
        file_node = self._create_node(
            node_type='file',
            name=os.path.basename(file_path),
            path=file_path,
            summary=f"AutoIt file: {os.path.basename(file_path)}",
            language=self.language
        )
        nodes[file_node.id] = file_node
        
        # Parse different elements
        self._parse_includes(content, file_node, file_path, nodes, relationships)
        self._parse_functions(content, file_node, file_path, nodes, relationships)
        self._parse_variables(content, file_node, file_path, nodes, relationships)
        self._parse_gui_elements(content, file_node, file_path, nodes, relationships)
        self._parse_com_objects(content, file_node, file_path, nodes, relationships)
        self._parse_hotkeys(content, file_node, file_path, nodes, relationships)
        
        return ParseResult(
            file_path=file_path,
            language=self.language,
            nodes=nodes,
            relationships=relationships,
            success=True
        )
    
    def _remove_comments(self, content: str) -> str:
        """Remove comments from AutoIt code"""
        # Remove block comments first
        content = self.patterns['comment_block'].sub('', content)
        # Remove single-line comments
        content = self.patterns['comment_single'].sub('', content)
        return content
    
    def _parse_includes(self, content: str, parent_node: CodeNode, file_path: str,
                       nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse #include statements"""
        for match in self.patterns['include'].finditer(content):
            include_file = match.group(1)
            include_node = self._create_node(
                node_type='import',
                name=include_file,
                path=file_path,
                summary=f"Include: {include_file}",
                line_number=content[:match.start()].count('\n') + 1,
                language=self.language
            )
            nodes[include_node.id] = include_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=include_node.id,
                relationship_type='imports'
            )
            relationships.append(rel)
    
    def _parse_functions(self, content: str, parent_node: CodeNode, file_path: str,
                        nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse function definitions"""
        for match in self.patterns['function'].finditer(content):
            func_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Try to find the function end to get a better summary
            func_start = match.start()
            func_end_match = None
            pos = func_start
            bracket_count = 0
            in_func = False
            
            # Simple bracket counting to find function end
            for i, char in enumerate(content[func_start:], func_start):
                if not in_func and char == '(':
                    in_func = True
                elif in_func:
                    if char == '(':
                        bracket_count += 1
                    elif char == ')':
                        bracket_count -= 1
                        if bracket_count == 0:
                            # Look for EndFunc
                            remaining = content[i:]
                            end_match = self.patterns['endfunc'].search(remaining)
                            if end_match:
                                func_end_match = end_match
                            break
            
            func_node = self._create_node(
                node_type='function',
                name=func_name,
                path=file_path,
                summary=f"Function: {func_name}",
                line_number=line_num,
                language=self.language
            )
            nodes[func_node.id] = func_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=func_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _parse_variables(self, content: str, parent_node: CodeNode, file_path: str,
                        nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse variable declarations"""
        var_patterns = {
            'global': self.patterns['global_var'],
            'local': self.patterns['local_var'],
            'dim': self.patterns['dim_var'],
            'static': self.patterns['static_var']
        }
        
        for scope, pattern in var_patterns.items():
            for match in pattern.finditer(content):
                var_name = match.group(1)
                var_node = self._create_node(
                    node_type='variable',
                    name=var_name,
                    path=file_path,
                    summary=f"{scope.title()} variable: {var_name}",
                    line_number=content[:match.start()].count('\n') + 1,
                    language=self.language,
                    scope=scope
                )
                nodes[var_node.id] = var_node
                
                rel = self._create_relationship(
                    source_id=parent_node.id,
                    target_id=var_node.id,
                    relationship_type='contains'
                )
                relationships.append(rel)
    
    def _parse_gui_elements(self, content: str, parent_node: CodeNode, file_path: str,
                           nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse GUI creation and control elements"""
        # GUI Create
        for match in self.patterns['gui_create'].finditer(content):
            gui_node = self._create_node(
                node_type='gui_window',
                name='GUI_Window',
                path=file_path,
                summary="GUI Window creation",
                line_number=content[:match.start()].count('\n') + 1,
                language=self.language
            )
            nodes[gui_node.id] = gui_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=gui_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
        
        # GUI Controls
        for match in self.patterns['gui_ctrl'].finditer(content):
            ctrl_type = match.group(1)
            ctrl_node = self._create_node(
                node_type='gui_control',
                name=f"GUICtrl{ctrl_type}",
                path=file_path,
                summary=f"GUI Control: {ctrl_type}",
                line_number=content[:match.start()].count('\n') + 1,
                language=self.language,
                control_type=ctrl_type
            )
            nodes[ctrl_node.id] = ctrl_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=ctrl_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _parse_com_objects(self, content: str, parent_node: CodeNode, file_path: str,
                          nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse COM object operations"""
        com_patterns = {
            'create': self.patterns['obj_create'],
            'get': self.patterns['obj_get']
        }
        
        for action, pattern in com_patterns.items():
            for match in pattern.finditer(content):
                com_node = self._create_node(
                    node_type='com_object',
                    name=f"COM_{action}",
                    path=file_path,
                    summary=f"COM Object {action}",
                    line_number=content[:match.start()].count('\n') + 1,
                    language=self.language,
                    action=action
                )
                nodes[com_node.id] = com_node
                
                rel = self._create_relationship(
                    source_id=parent_node.id,
                    target_id=com_node.id,
                    relationship_type='contains'
                )
                relationships.append(rel)
    
    def _parse_hotkeys(self, content: str, parent_node: CodeNode, file_path: str,
                      nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Parse hotkey definitions"""
        for match in self.patterns['hotkey_set'].finditer(content):
            hotkey_node = self._create_node(
                node_type='hotkey',
                name='HotKey',
                path=file_path,
                summary="Hotkey definition",
                line_number=content[:match.start()].count('\n') + 1,
                language=self.language
            )
            nodes[hotkey_node.id] = hotkey_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=hotkey_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)