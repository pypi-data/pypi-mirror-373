#!/usr/bin/env python3
"""
Base Parser Interface for Multi-Language Code Indexing
Uses Composite Pattern for extensible language support
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from pathlib import Path

try:
    from ..interfaces.parser_interface import IParser
except ImportError:
    # Fallback for backward compatibility
    class IParser(ABC):
        pass

@dataclass
class CodeNode:
    """Represents a code entity (class, function, variable, etc.)"""
    id: int
    node_type: str  # 'file', 'class', 'function', 'method', 'variable', 'import', 'interface', 'enum'
    name: str
    path: str
    summary: str
    line_number: int = 0
    column_number: int = 0
    language: str = 'unknown'
    parent_id: Optional[int] = None
    children_ids: List[int] = None
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
        if self.attributes is None:
            self.attributes = {}

@dataclass
class CodeRelationship:
    """Represents a relationship between code entities"""
    source_id: int
    target_id: int
    relationship_type: str  # 'imports', 'calls', 'inherits', 'implements', 'contains', 'uses'
    weight: float = 1.0
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

@dataclass
class ParseResult:
    """Result of parsing a code file"""
    file_path: str
    language: str
    nodes: Dict[int, CodeNode]
    relationships: List[CodeRelationship]
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.nodes is None:
            self.nodes = {}
        if self.relationships is None:
            self.relationships = []

class BaseParser(IParser):
    """
    Abstract base class for all language parsers
    Part of Composite Pattern - Component interface
    """
    
    def __init__(self, language: str):
        self.language = language
        self.node_counter = 0
        self.supported_extensions: Set[str] = set()
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        pass
    
    @abstractmethod
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a single file and return nodes and relationships"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> Set[str]:
        """Get file extensions supported by this parser"""
        pass
    
    def _create_node(self, node_type: str, name: str, path: str, summary: str, 
                    line_number: int = 0, column_number: int = 0, 
                    parent_id: Optional[int] = None, **kwargs) -> CodeNode:
        """Helper method to create a code node"""
        node_id = self.node_counter
        self.node_counter += 1
        
        # Validate name - ensure it's not None or empty
        if not name or name == 'None' or (isinstance(name, str) and not name.strip()):
            # Generate a meaningful default name
            file_name = Path(path).name if path else 'unknown'
            name = f"{node_type}_{node_id}_in_{file_name}"
        
        return CodeNode(
            id=node_id,
            node_type=node_type,
            name=name,
            path=path,
            summary=summary if summary else f"{node_type}: {name}",
            line_number=line_number,
            column_number=column_number,
            language=self.language,
            parent_id=parent_id,
            attributes=kwargs
        )
    
    def _create_relationship(self, source_id: int, target_id: int, 
                           relationship_type: str, weight: float = 1.0, 
                           **kwargs) -> CodeRelationship:
        """Helper method to create a relationship"""
        return CodeRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            weight=weight,
            attributes=kwargs
        )
    
    def _read_file_safely(self, file_path: str) -> Optional[str]:
        """Safely read file content with encoding detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'utf-8-sig']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            return None
        except (IOError, OSError):
            return None
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except (IOError, OSError):
            return True

class CompositeParser(BaseParser):
    """
    Composite parser that manages multiple language parsers
    Part of Composite Pattern - Composite class
    """
    
    def __init__(self):
        super().__init__('composite')
        self.parsers: List[BaseParser] = []
        self.parser_by_language: Dict[str, BaseParser] = {}
    
    def add_parser(self, parser: BaseParser):
        """Add a language parser to the composite"""
        self.parsers.append(parser)
        self.parser_by_language[parser.language] = parser
        self.supported_extensions.update(parser.get_supported_extensions())
    
    def remove_parser(self, parser: BaseParser):
        """Remove a language parser from the composite"""
        if parser in self.parsers:
            self.parsers.remove(parser)
            if parser.language in self.parser_by_language:
                del self.parser_by_language[parser.language]
            # Rebuild supported extensions
            self.supported_extensions.clear()
            for p in self.parsers:
                self.supported_extensions.update(p.get_supported_extensions())
    
    def can_parse(self, file_path: str) -> bool:
        """Check if any parser can handle the given file"""
        return any(parser.can_parse(file_path) for parser in self.parsers)
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse file using the appropriate language parser"""
        # Find the first parser that can handle this file
        for parser in self.parsers:
            if parser.can_parse(file_path):
                result = parser.parse_file(file_path)
                # Update node counter to avoid ID conflicts
                self.node_counter = max(self.node_counter, parser.node_counter)
                return result
        
        # No parser found
        return ParseResult(
            file_path=file_path,
            language='unknown',
            nodes={},
            relationships=[],
            success=False,
            error_message=f"No parser available for file: {file_path}"
        )
    
    def get_supported_extensions(self) -> Set[str]:
        """Get all supported file extensions"""
        return self.supported_extensions
    
    def get_parser_for_language(self, language: str) -> Optional[BaseParser]:
        """Get parser for a specific language"""
        return self.parser_by_language.get(language)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.parser_by_language.keys())
    
    def parse_directory(self, directory: str, file_patterns: List[str] = None, 
                       ignored_patterns: Set[str] = None) -> Dict[str, ParseResult]:
        """Parse all supported files in a directory"""
        if file_patterns is None:
            file_patterns = [f"*{ext}" for ext in self.supported_extensions]
        
        if ignored_patterns is None:
            ignored_patterns = set()
        
        results = {}
        
        # Collect all files
        for pattern in file_patterns:
            for file_path in Path(directory).rglob(pattern):
                if file_path.is_file():
                    file_str = str(file_path)
                    
                    # Skip ignored files
                    if any(ignore_pattern in file_str for ignore_pattern in ignored_patterns):
                        continue
                    
                    # Parse file
                    if self.can_parse(file_str):
                        result = self.parse_file(file_str)
                        results[file_str] = result
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about supported languages and parsers"""
        return {
            'total_parsers': len(self.parsers),
            'supported_languages': self.get_supported_languages(),
            'supported_extensions': sorted(list(self.supported_extensions)),
            'parsers': [
                {
                    'language': parser.language,
                    'extensions': sorted(list(parser.get_supported_extensions()))
                }
                for parser in self.parsers
            ]
        }