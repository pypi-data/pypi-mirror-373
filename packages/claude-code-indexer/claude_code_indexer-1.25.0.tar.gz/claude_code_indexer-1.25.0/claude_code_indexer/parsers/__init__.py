#!/usr/bin/env python3
"""
Parser system for Multi-Language Code Indexing
"""

import sys
import os

# Ensure the module can be found when running from installed script
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

try:
    from .base_parser import BaseParser, CompositeParser, CodeNode, CodeRelationship, ParseResult
    from .python_parser import PythonParser
    from .javascript_parser import JavaScriptParser
    from .java_parser import JavaParser
    from .autoit_parser import AutoItParser
    from .rust_parser import RustParser
except ImportError:
    # Fallback to direct import if relative import fails
    from base_parser import BaseParser, CompositeParser, CodeNode, CodeRelationship, ParseResult
    from python_parser import PythonParser
    from javascript_parser import JavaScriptParser
    from java_parser import JavaParser
    from autoit_parser import AutoItParser
    from rust_parser import RustParser

__all__ = [
    'BaseParser',
    'CompositeParser', 
    'CodeNode',
    'CodeRelationship',
    'ParseResult',
    'PythonParser',
    'JavaScriptParser',
    'JavaParser',
    'AutoItParser',
    'RustParser',
    'create_default_parser',
    'get_supported_extensions'
]

def create_default_parser() -> CompositeParser:
    """Create a composite parser with all available language parsers"""
    composite = CompositeParser()
    
    # Add all language parsers
    composite.add_parser(PythonParser())
    composite.add_parser(JavaScriptParser())
    composite.add_parser(JavaParser())
    composite.add_parser(AutoItParser())
    composite.add_parser(RustParser())
    
    return composite

def get_supported_extensions():
    """Get all supported file extensions"""
    parser = create_default_parser()
    extensions = set()
    for p in parser.parsers:
        extensions.update(p.supported_extensions)
    return extensions