"""Base class for database migrations."""

from abc import ABC, abstractmethod
from typing import Any
import sqlite3


class BaseMigration(ABC):
    """Abstract base class for database migrations."""
    
    def __init__(self):
        self._version = None
        self._description = None
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Return the migration version (e.g., '1.1.0')."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this migration does."""
        pass
    
    @abstractmethod
    def up(self, conn: sqlite3.Connection) -> None:
        """Apply the migration."""
        pass
    
    @abstractmethod
    def down(self, conn: sqlite3.Connection) -> None:
        """Rollback the migration."""
        pass
    
    def execute_sql(self, conn: sqlite3.Connection, sql: str, params: Any = None) -> None:
        """Helper method to execute SQL statements."""
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
    
    def table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        """Check if a table exists."""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def column_exists(self, conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns