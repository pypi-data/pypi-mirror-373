"""
Parser factory for creating language parsers
"""
from typing import List, Optional
from ..interfaces.parser_interface import IParser
from ..parsers import (
    PythonParser,
    JavaScriptParser, 
    JavaParser,
    AutoItParser,
    CompositeParser
)


class ParserFactory:
    """Factory for creating parser instances"""
    
    @staticmethod
    def create_parser(language: str) -> Optional[IParser]:
        """Create a specific language parser"""
        parsers = {
            'python': PythonParser,
            'javascript': JavaScriptParser,
            'java': JavaParser,
            'autoit': AutoItParser
        }
        
        parser_class = parsers.get(language.lower())
        if parser_class:
            return parser_class()
        return None
    
    @staticmethod
    def create_composite_parser(languages: Optional[List[str]] = None) -> IParser:
        """Create a composite parser with specified or all available languages"""
        composite = CompositeParser()
        
        if languages:
            # Add only specified languages
            for lang in languages:
                parser = ParserFactory.create_parser(lang)
                if parser:
                    composite.add_parser(parser)
        else:
            # Add all available parsers
            composite.add_parser(PythonParser())
            composite.add_parser(JavaScriptParser())
            composite.add_parser(JavaParser())
            composite.add_parser(AutoItParser())
        
        return composite