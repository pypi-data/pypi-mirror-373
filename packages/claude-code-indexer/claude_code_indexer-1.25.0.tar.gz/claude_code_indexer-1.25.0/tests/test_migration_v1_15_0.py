"""Test migration v1.15.0 handles different database states correctly."""

import sqlite3
import tempfile
from pathlib import Path
import pytest
from claude_code_indexer.migrations.versions.migration_005_v1_15_0 import MigrationV1_15_0


def test_migration_v1_15_0_with_description_column():
    """Test migration when enhanced_metadata has description column (v1.14.0 schema)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        
        # Create code_nodes table (required for foreign key)
        conn.execute("""
            CREATE TABLE code_nodes (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        
        # Create v1.14.0 schema with description column
        conn.execute("""
            CREATE TABLE enhanced_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id INTEGER NOT NULL,
                description TEXT,
                business_context TEXT,
                design_patterns TEXT,
                quality_notes TEXT,
                tech_debt_indicators TEXT,
                relationships TEXT,
                complexity_factors TEXT,
                security_considerations TEXT,
                performance_notes TEXT,
                maintainability_score REAL,
                test_coverage_estimate REAL,
                role TEXT,
                layer TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES code_nodes(id)
            )
        """)
        
        # Insert test data
        conn.execute("INSERT INTO code_nodes (id, name) VALUES (1, 'test_node')")
        conn.execute("""
            INSERT INTO enhanced_metadata (node_id, description, role, layer, tags)
            VALUES (1, 'Test description', 'backend', 'service', '["api","rest"]')
        """)
        conn.commit()
        
        # Run migration
        migration = MigrationV1_15_0()
        migration.up(conn)
        
        # Verify new schema
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(enhanced_metadata)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Should have new columns
        assert 'llm_summary' in columns
        assert 'architectural_layer' in columns
        assert 'role_tags' in columns
        
        # Should not have old columns
        assert 'description' not in columns
        assert 'role' not in columns
        assert 'tags' not in columns
        
        # Verify data migration
        cursor.execute("SELECT llm_summary, architectural_layer, role_tags FROM enhanced_metadata WHERE node_id = 1")
        result = cursor.fetchone()
        assert result[0] == 'Test description'  # llm_summary from description
        assert result[1] == 'service'  # architectural_layer from layer
        assert result[2] == '["api","rest"]'  # role_tags from tags
        
        conn.close()


def test_migration_v1_15_0_without_description_column():
    """Test migration when enhanced_metadata exists but without description column."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        
        # Create code_nodes table
        conn.execute("""
            CREATE TABLE code_nodes (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        
        # Create enhanced_metadata with minimal/different schema
        conn.execute("""
            CREATE TABLE enhanced_metadata (
                node_id INTEGER PRIMARY KEY,
                some_other_field TEXT
            )
        """)
        
        # Insert test data
        conn.execute("INSERT INTO code_nodes (id, name) VALUES (1, 'test_node')")
        conn.execute("INSERT INTO enhanced_metadata (node_id) VALUES (1)")
        conn.commit()
        
        # Run migration - should not crash
        migration = MigrationV1_15_0()
        migration.up(conn)
        
        # Verify new schema
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(enhanced_metadata)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Should have all new columns
        assert 'llm_summary' in columns
        assert 'architectural_layer' in columns
        assert 'role_tags' in columns
        
        # Verify node_id was preserved
        cursor.execute("SELECT node_id FROM enhanced_metadata")
        result = cursor.fetchone()
        assert result[0] == 1
        
        conn.close()


def test_migration_v1_15_0_no_table():
    """Test migration when enhanced_metadata table doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        
        # Create code_nodes table
        conn.execute("""
            CREATE TABLE code_nodes (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        conn.commit()
        
        # Run migration - should create table
        migration = MigrationV1_15_0()
        migration.up(conn)
        
        # Verify table was created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_metadata'")
        assert cursor.fetchone() is not None
        
        # Verify schema
        cursor.execute("PRAGMA table_info(enhanced_metadata)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Should have all required columns
        expected_columns = {
            'node_id', 'llm_summary', 'role_tags', 'complexity_score',
            'quality_metrics', 'architectural_layer', 'business_domain',
            'criticality_level', 'dependencies_impact', 'testability_score',
            'last_analyzed', 'analysis_version'
        }
        assert expected_columns.issubset(columns)
        
        conn.close()


def test_migration_v1_15_0_rollback():
    """Test migration rollback (down method)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        
        # Create code_nodes table
        conn.execute("""
            CREATE TABLE code_nodes (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        
        # Create new schema
        conn.execute("""
            CREATE TABLE enhanced_metadata (
                node_id INTEGER PRIMARY KEY,
                llm_summary TEXT,
                role_tags TEXT,
                architectural_layer TEXT,
                business_domain TEXT,
                last_analyzed TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES code_nodes(id)
            )
        """)
        
        # Insert test data
        conn.execute("INSERT INTO code_nodes (id, name) VALUES (1, 'test_node')")
        conn.execute("""
            INSERT INTO enhanced_metadata (node_id, llm_summary, role_tags, architectural_layer, business_domain)
            VALUES (1, 'Summary text', '["tag1"]', 'service', 'backend')
        """)
        conn.commit()
        
        # Run rollback
        migration = MigrationV1_15_0()
        migration.down(conn)
        
        # Verify old schema
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(enhanced_metadata)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Should have old columns
        assert 'description' in columns
        assert 'role' in columns
        assert 'layer' in columns
        assert 'tags' in columns
        
        # Verify data was migrated back
        cursor.execute("SELECT description, role, layer, tags FROM enhanced_metadata WHERE node_id = 1")
        result = cursor.fetchone()
        assert result[0] == 'Summary text'  # description from llm_summary
        assert result[1] == 'backend'  # role from business_domain
        assert result[2] == 'service'  # layer from architectural_layer
        assert result[3] == '["tag1"]'  # tags from role_tags
        
        conn.close()