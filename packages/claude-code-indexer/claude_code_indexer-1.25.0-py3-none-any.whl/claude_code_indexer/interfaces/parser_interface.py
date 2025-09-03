"""
Parser interface for dependency injection
"""
from abc import ABC, abstractmethod
from typing import Set
from pathlib import Path

from ..parsers.base_parser import ParseResult


class IParser(ABC):
    """Interface for all language parsers"""
    
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
    
    @property
    @abstractmethod
    def language(self) -> str:
        """Get the language this parser handles"""
        pass