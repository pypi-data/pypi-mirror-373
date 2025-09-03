"""Tests for database migration system."""

import os
import sqlite3
import tempfile
import shutil
from pathlib import Path
import pytest

from claude_code_indexer.migrations import MigrationManager, BaseMigration
from claude_code_indexer.migrations.versions.migration_001_v1_0_0 import MigrationV1_0_0
from claude_code_indexer.migrations.versions.migration_002_v1_1_0 import MigrationV1_1_0
from claude_code_indexer.migrations.versions.migration_003_v1_6_0 import MigrationV1_6_0
from claude_code_indexer.migrations.versions.migration_004_v1_14_0 import MigrationV1_14_0
from claude_code_indexer.migrations.versions.migration_005_v1_15_0 import MigrationV1_15_0
from claude_code_indexer.migrations.versions.migration_006_v1_16_0 import MigrationV1_16_0


class TestMigrationManager:
    """Test database migration functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        yield db_path
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def migration_manager(self, temp_db):
        """Create migration manager instance."""
        return MigrationManager(temp_db)
    
    def create_legacy_v1_0_0_db(self, db_path):
        """Create a database with v1.0.0 schema."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create basic tables
        cursor.execute('''
            CREATE TABLE code_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                summary TEXT,
                importance_score REAL DEFAULT 0.0,
                relevance_tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE relationships (
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id, relationship_type)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE indexing_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add some test data
        cursor.execute('''
            INSERT INTO code_nodes (node_type, name, path, summary)
            VALUES ('function', 'test_func', '/test.py', 'Test function')
        ''')
        
        conn.commit()
        conn.close()
    
    def create_legacy_v1_1_0_db(self, db_path):
        """Create a database with v1.1.0 schema."""
        self.create_legacy_v1_0_0_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add v1.1.0 columns and tables
        cursor.execute("ALTER TABLE code_nodes ADD COLUMN weight REAL DEFAULT 1.0")
        cursor.execute("ALTER TABLE code_nodes ADD COLUMN frequency_score REAL DEFAULT 0.0")
        cursor.execute("ALTER TABLE code_nodes ADD COLUMN usage_stats TEXT")
        
        cursor.execute('''
            CREATE TABLE patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                description TEXT,
                nodes TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE libraries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                name TEXT NOT NULL,
                version TEXT,
                category TEXT,
                usage_count INTEGER DEFAULT 0,
                usage_contexts TEXT,
                import_statements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE infrastructure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                component_type TEXT NOT NULL,
                name TEXT NOT NULL,
                technology TEXT,
                configuration TEXT,
                usage_frequency INTEGER DEFAULT 0,
                connections TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Set version
        cursor.execute('''
            INSERT INTO indexing_metadata (key, value)
            VALUES ('schema_version', '1.1.0')
        ''')
        
        conn.commit()
        conn.close()
    
    def test_detect_empty_database(self, migration_manager, temp_db):
        """Test detecting version of empty/non-existent database."""
        assert migration_manager.detect_schema_version() is None
    
    def test_detect_v1_0_0_schema(self, migration_manager, temp_db):
        """Test detecting v1.0.0 schema."""
        self.create_legacy_v1_0_0_db(temp_db)
        assert migration_manager.detect_schema_version() == '1.0.0'
    
    def test_detect_v1_1_0_schema(self, migration_manager, temp_db):
        """Test detecting v1.1.0 schema."""
        self.create_legacy_v1_1_0_db(temp_db)
        assert migration_manager.detect_schema_version() == '1.1.0'
    
    def test_get_available_migrations(self, migration_manager):
        """Test getting all available migrations."""
        migrations = migration_manager.get_available_migrations()
        
        # Check we have the expected migrations
        versions = [m.version for m in migrations]
        assert '1.0.0' in versions
        assert '1.1.0' in versions
        assert '1.6.0' in versions
        assert '1.14.0' in versions
        assert '1.15.0' in versions
        
        # Check they're sorted
        assert versions == sorted(versions, key=lambda v: tuple(map(int, v.split('.'))))
    
    def test_get_pending_migrations(self, migration_manager):
        """Test getting pending migrations."""
        # From 1.0.0 to 1.6.0
        pending = migration_manager.get_pending_migrations('1.0.0', '1.6.0')
        versions = [m.version for m in pending]
        assert versions == ['1.1.0', '1.6.0']
        
        # From 1.1.0 to 1.14.0
        pending = migration_manager.get_pending_migrations('1.1.0', '1.14.0')
        versions = [m.version for m in pending]
        assert versions == ['1.6.0', '1.14.0']
        
        # No migrations needed
        pending = migration_manager.get_pending_migrations('1.14.0', '1.14.0')
        assert len(pending) == 0
    
    def test_backup_and_restore(self, migration_manager, temp_db):
        """Test backup and restore functionality."""
        # Create a database with some data
        self.create_legacy_v1_0_0_db(temp_db)
        
        # Create backup
        backup_path = migration_manager.create_backup()
        assert os.path.exists(backup_path)
        
        # Modify the database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE code_nodes")
        conn.commit()
        conn.close()
        
        # Verify table is gone
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='code_nodes'")
        assert cursor.fetchone() is None
        conn.close()
        
        # Restore from backup
        migration_manager.restore_backup(backup_path)
        
        # Verify table is back
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='code_nodes'")
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_migrate_from_v1_0_0_to_v1_14_0(self, migration_manager, temp_db):
        """Test full migration from v1.0.0 to v1.14.0."""
        # Create v1.0.0 database
        self.create_legacy_v1_0_0_db(temp_db)
        
        # Migrate to v1.14.0
        success, message = migration_manager.migrate('1.14.0')
        assert success
        assert 'Successfully migrated' in message
        
        # Verify all tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Check v1.1.0 tables
        for table in ['patterns', 'libraries', 'infrastructure']:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            assert cursor.fetchone() is not None
        
        # Check v1.1.0 columns
        cursor.execute("PRAGMA table_info(code_nodes)")
        columns = {row[1] for row in cursor.fetchall()}
        assert 'weight' in columns
        assert 'frequency_score' in columns
        assert 'usage_stats' in columns
        
        # Check v1.6.0 columns
        assert 'language' in columns
        assert 'line_number' in columns
        assert 'column_number' in columns
        
        # Check v1.14.0 tables
        for table in ['enhanced_metadata', 'detected_patterns', 'code_evolution']:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            assert cursor.fetchone() is not None
        
        # Check migration history
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migration_history'")
        assert cursor.fetchone() is not None
        
        # Check schema version
        cursor.execute("SELECT value FROM indexing_metadata WHERE key='schema_version'")
        assert cursor.fetchone()[0] == '1.14.0'
        
        conn.close()
    
    def test_migrate_rollback_on_error(self, migration_manager, temp_db):
        """Test that migration rolls back on error."""
        # Create a broken migration
        class BrokenMigration(BaseMigration):
            @property
            def version(self):
                return '99.0.0'
            
            @property
            def description(self):
                return 'Broken migration for testing'
            
            def up(self, conn):
                raise Exception("Migration failed!")
            
            def down(self, conn):
                pass
        
        # Monkey patch to add broken migration
        original_get_migrations = migration_manager.get_available_migrations
        def mock_get_migrations():
            migrations = original_get_migrations()
            migrations.append(BrokenMigration())
            return sorted(migrations, key=lambda m: tuple(map(int, m.version.split('.'))))
        
        migration_manager.get_available_migrations = mock_get_migrations
        
        # Create v1.0.0 database
        self.create_legacy_v1_0_0_db(temp_db)
        
        # Try to migrate to broken version
        success, message = migration_manager.migrate('99.0.0')
        assert not success
        assert 'Migration failed' in message
        
        # Verify database is still at v1.0.0
        assert migration_manager.detect_schema_version() == '1.0.0'
    
    def test_clean_old_backups(self, migration_manager, temp_db):
        """Test cleaning old backup files."""
        # Create a test database first
        self.create_legacy_v1_0_0_db(temp_db)
        
        # Create multiple backups with slight time delays
        backups = []
        import time
        for i in range(10):
            backup_path = migration_manager.create_backup()
            backups.append(backup_path)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Clean old backups, keeping only 5
        migration_manager.clean_old_backups(keep_last=5)
        
        # Check that only 5 most recent backups remain
        backup_dir = Path(temp_db).parent / "backups"
        remaining_backups = list(backup_dir.glob("backup_*.db"))
        assert len(remaining_backups) == 5
    
    def test_migration_idempotency(self, migration_manager, temp_db):
        """Test that migrations are idempotent."""
        # Create v1.0.0 database
        self.create_legacy_v1_0_0_db(temp_db)
        
        # Migrate to v1.6.0
        success1, message1 = migration_manager.migrate('1.6.0')
        assert success1
        
        # Try to migrate again - should be no-op
        success2, message2 = migration_manager.migrate('1.6.0')
        assert success2
        assert 'already at version' in message2
    
    def test_partial_migration(self, migration_manager, temp_db):
        """Test migrating to intermediate versions."""
        # Create v1.0.0 database
        self.create_legacy_v1_0_0_db(temp_db)
        
        # Migrate to v1.1.0 only
        success, message = migration_manager.migrate('1.1.0')
        assert success
        assert migration_manager.detect_schema_version() == '1.1.0'
        
        # Then migrate to v1.6.0
        success, message = migration_manager.migrate('1.6.0')
        assert success
        assert migration_manager.detect_schema_version() == '1.6.0'
        
        # Finally to v1.14.0
        success, message = migration_manager.migrate('1.14.0')
        assert success
        assert migration_manager.detect_schema_version() == '1.14.0'
        
        # And finally to v1.15.0
        success, message = migration_manager.migrate('1.15.0')
        assert success
        assert migration_manager.detect_schema_version() == '1.15.0'
        
        # Verify enhanced_metadata has correct schema
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(enhanced_metadata)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Check for new schema columns
        assert 'llm_summary' in columns
        assert 'role_tags' in columns
        assert 'complexity_score' in columns
        assert 'architectural_layer' in columns
        assert 'business_domain' in columns
        
        # Check old schema columns are gone
        assert 'description' not in columns
        assert 'layer' not in columns
        assert 'role' not in columns
        
        conn.close()
    
    def test_migrate_to_v1_16_0(self, migration_manager, temp_db):
        """Test migration to v1.16.0 with search optimizations."""
        # Create v1.15.0 database
        self.create_legacy_v1_0_0_db(temp_db)
        
        # Migrate to v1.15.0 first
        success, message = migration_manager.migrate('1.15.0')
        assert success
        
        # Add some test data
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO code_nodes (node_type, name, path, summary, importance_score) 
            VALUES (?, ?, ?, ?, ?)
        """, ('function', 'test_function', '/test.py', 'Test summary', 0.8))
        conn.commit()
        
        # Migrate to v1.16.0
        success, message = migration_manager.migrate('1.16.0')
        assert success
        assert 'Successfully migrated' in message
        
        # Verify indexes exist
        cursor.execute("PRAGMA index_list(code_nodes)")
        indexes = {row[1] for row in cursor.fetchall()}
        assert 'idx_code_nodes_name' in indexes
        assert 'idx_code_nodes_importance_score' in indexes
        assert 'idx_code_nodes_search' in indexes
        
        # Verify FTS5 table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='code_nodes_fts'")
        assert cursor.fetchone() is not None
        
        # Verify FTS5 data was populated
        cursor.execute("SELECT COUNT(*) FROM code_nodes_fts")
        assert cursor.fetchone()[0] > 0
        
        # Test FTS5 search
        cursor.execute("SELECT * FROM code_nodes_fts WHERE code_nodes_fts MATCH 'test'")
        results = cursor.fetchall()
        assert len(results) > 0
        
        conn.close()