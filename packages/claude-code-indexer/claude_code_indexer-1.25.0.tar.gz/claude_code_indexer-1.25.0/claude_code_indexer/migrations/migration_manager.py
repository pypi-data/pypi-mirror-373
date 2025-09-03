"""Migration manager for handling database schema updates."""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import importlib
import pkgutil
import hashlib

from ..logger import log_info, log_warning, log_error
from .base_migration import BaseMigration


class MigrationManager:
    """Manages database migrations with automatic backup and rollback."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.backup_dir = self.db_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def detect_schema_version(self) -> Optional[str]:
        """Detect the current schema version of the database."""
        if not self.db_path.exists():
            return None
            
        conn = sqlite3.connect(str(self.db_path))
        try:
            # First, check if schema_version is stored in metadata
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM indexing_metadata 
                WHERE key = 'schema_version'
            """)
            result = cursor.fetchone()
            if result:
                return result[0]
            
            # If no version metadata, detect based on schema
            return self._infer_version_from_schema(conn)
            
        except sqlite3.Error:
            # If indexing_metadata doesn't exist, it's a very old version
            return self._infer_version_from_schema(conn)
        finally:
            conn.close()
    
    def _infer_version_from_schema(self, conn: sqlite3.Connection) -> str:
        """Infer database version from existing schema."""
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        # Check for v1.1.0+ tables
        if {'patterns', 'libraries', 'infrastructure'}.issubset(tables):
            # Check for v1.6.0+ columns
            cursor.execute("PRAGMA table_info(code_nodes)")
            columns = {row[1] for row in cursor.fetchall()}
            
            if {'language', 'line_number', 'column_number'}.issubset(columns):
                return '1.6.0'
            elif {'weight', 'frequency_score', 'usage_stats'}.issubset(columns):
                return '1.1.0'
        
        # Basic schema only
        if {'code_nodes', 'relationships', 'indexing_metadata'}.issubset(tables):
            return '1.0.0'
        
        # Unknown or empty database
        return '0.0.0'
    
    def get_available_migrations(self) -> List[BaseMigration]:
        """Get all available migration classes sorted by version."""
        migrations = []
        
        # Import all migration modules
        migrations_package = importlib.import_module('claude_code_indexer.migrations.versions')
        for _, module_name, _ in pkgutil.iter_modules(migrations_package.__path__):
            module = importlib.import_module(f'claude_code_indexer.migrations.versions.{module_name}')
            
            # Find migration class in module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseMigration) and 
                    attr != BaseMigration):
                    migrations.append(attr())
        
        # Sort by version
        migrations.sort(key=lambda m: tuple(map(int, m.version.split('.'))))
        return migrations
    
    def get_pending_migrations(self, current_version: str, target_version: str) -> List[BaseMigration]:
        """Get migrations that need to be applied."""
        all_migrations = self.get_available_migrations()
        pending = []
        
        current_tuple = tuple(map(int, current_version.split('.')))
        target_tuple = tuple(map(int, target_version.split('.')))
        
        for migration in all_migrations:
            migration_tuple = tuple(map(int, migration.version.split('.')))
            if current_tuple < migration_tuple <= target_tuple:
                pending.append(migration)
        
        return pending
    
    def create_backup(self) -> str:
        """Create a backup of the current database."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        backup_path = self.backup_dir / f"backup_{timestamp}.db"
        
        if self.db_path.exists():
            shutil.copy2(self.db_path, backup_path)
            log_info(f"Created database backup: {backup_path}")
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str) -> None:
        """Restore database from backup."""
        if not Path(backup_path).exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        shutil.copy2(backup_path, self.db_path)
        log_info(f"Restored database from backup: {backup_path}")
    
    def apply_migration(self, migration: BaseMigration, conn: sqlite3.Connection) -> None:
        """Apply a single migration."""
        log_info(f"Applying migration {migration.version}: {migration.description}")
        
        # Apply the migration
        migration.up(conn)
        
        # Record migration in database
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO migration_history (version, applied_at, checksum)
            VALUES (?, ?, ?)
        """, (migration.version, datetime.now().isoformat(), self._get_migration_checksum(migration)))
        
        # Update schema version
        cursor.execute("""
            INSERT OR REPLACE INTO indexing_metadata (key, value)
            VALUES ('schema_version', ?)
        """, (migration.version,))
        
        conn.commit()
    
    def _get_migration_checksum(self, migration: BaseMigration) -> str:
        """Calculate checksum for migration to detect changes."""
        content = f"{migration.version}:{migration.description}:{migration.up.__code__.co_code}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def migrate(self, target_version: str) -> Tuple[bool, str]:
        """
        Perform database migration to target version.
        
        Returns:
            Tuple of (success, message)
        """
        current_version = self.detect_schema_version() or '0.0.0'
        
        if current_version == target_version:
            return True, f"Database already at version {target_version}"
        
        # Get pending migrations
        pending = self.get_pending_migrations(current_version, target_version)
        
        if not pending:
            return True, f"No migrations needed from {current_version} to {target_version}"
        
        # Create backup
        backup_path = self.create_backup()
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            # Ensure migration history table exists
            self._ensure_migration_history_table(conn)
            
            # Apply each migration
            for migration in pending:
                try:
                    self.apply_migration(migration, conn)
                except Exception as e:
                    log_error(f"Migration {migration.version} failed: {e}")
                    conn.close()
                    # Restore from backup
                    self.restore_backup(backup_path)
                    return False, f"Migration failed at version {migration.version}: {str(e)}"
            
            conn.close()
            return True, f"Successfully migrated from {current_version} to {target_version}"
            
        except Exception as e:
            log_error(f"Migration process failed: {e}")
            conn.close()
            # Restore from backup
            self.restore_backup(backup_path)
            return False, f"Migration failed: {str(e)}"
    
    def _ensure_migration_history_table(self, conn: sqlite3.Connection) -> None:
        """Ensure migration history table exists."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (
                version VARCHAR(50) PRIMARY KEY,
                applied_at TIMESTAMP,
                checksum VARCHAR(64)
            )
        """)
        conn.commit()
    
    def clean_old_backups(self, keep_last: int = 5) -> None:
        """Clean old backup files, keeping only the most recent ones."""
        backups = sorted(self.backup_dir.glob("backup_*.db"), 
                        key=lambda p: p.stat().st_mtime, 
                        reverse=True)
        
        for backup in backups[keep_last:]:
            backup.unlink()
            log_info(f"Removed old backup: {backup}")