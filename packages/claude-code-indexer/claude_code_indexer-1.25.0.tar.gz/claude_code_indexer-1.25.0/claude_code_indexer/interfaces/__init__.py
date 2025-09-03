"""
Interfaces for dependency injection and testability
"""

from .parser_interface import IParser
from .database_interface import IDatabase
from .indexer_interface import IIndexer
from .cache_interface import ICache

__all__ = [
    'IParser',
    'IDatabase', 
    'IIndexer',
    'ICache'
]