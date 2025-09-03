"""
Database interface for dependency injection
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path


class IDatabase(ABC):
    """Interface for database operations"""
    
    @abstractmethod
    def connect(self, db_path: Path) -> None:
        """Connect to the database"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    def execute(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Execute a database query"""
        pass
    
    @abstractmethod
    def executemany(self, query: str, params: List[Tuple]) -> None:
        """Execute multiple queries"""
        pass
    
    @abstractmethod
    def fetchall(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """Fetch all results from a query"""
        pass
    
    @abstractmethod
    def fetchone(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """Fetch one result from a query"""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction"""
        pass
    
    @abstractmethod
    def create_tables(self, schema: Dict[str, str]) -> None:
        """Create database tables from schema"""
        pass