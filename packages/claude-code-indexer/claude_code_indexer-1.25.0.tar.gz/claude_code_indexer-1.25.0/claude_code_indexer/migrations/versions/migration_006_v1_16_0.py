"""Migration to v1.16.0 - Add search performance optimizations."""

from ..base_migration import BaseMigration


class MigrationV1_16_0(BaseMigration):
    """Add indexes for search performance and FTS5 support."""
    
    @property
    def version(self) -> str:
        return '1.16.0'
    
    @property
    def description(self) -> str:
        return 'Add search optimization indexes and FTS5 full-text search support'
    
    def up(self, conn) -> None:
        """Apply migration - add search indexes and FTS5 table."""
        
        # Add indexes for search optimization
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_code_nodes_name ON code_nodes(name)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_code_nodes_importance_score ON code_nodes(importance_score DESC)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_code_nodes_search ON code_nodes(name, path, importance_score DESC)")
        
        # Create FTS5 virtual table for full-text search
        self.execute_sql(conn, """
            CREATE VIRTUAL TABLE IF NOT EXISTS code_nodes_fts USING fts5(
                name,
                path,
                summary,
                content='code_nodes',
                content_rowid='id',
                tokenize='porter unicode61'
            )
        """)
        
        # Populate FTS table with existing data
        self.execute_sql(conn, """
            INSERT INTO code_nodes_fts(rowid, name, path, summary)
            SELECT id, name, path, summary FROM code_nodes
        """)
        
        # Create triggers to keep FTS in sync with main table
        self.execute_sql(conn, """
            CREATE TRIGGER IF NOT EXISTS code_nodes_fts_insert 
            AFTER INSERT ON code_nodes
            BEGIN
                INSERT INTO code_nodes_fts(rowid, name, path, summary)
                VALUES (new.id, new.name, new.path, new.summary);
            END
        """)
        
        self.execute_sql(conn, """
            CREATE TRIGGER IF NOT EXISTS code_nodes_fts_update
            AFTER UPDATE ON code_nodes
            BEGIN
                UPDATE code_nodes_fts 
                SET name = new.name, path = new.path, summary = new.summary
                WHERE rowid = new.id;
            END
        """)
        
        self.execute_sql(conn, """
            CREATE TRIGGER IF NOT EXISTS code_nodes_fts_delete
            AFTER DELETE ON code_nodes
            BEGIN
                DELETE FROM code_nodes_fts WHERE rowid = old.id;
            END
        """)
        
        # Note: project_path index not needed as indexing_metadata doesn't have that column
    
    def down(self, conn) -> None:
        """Rollback migration - remove indexes and FTS5 table."""
        
        # Drop triggers
        self.execute_sql(conn, "DROP TRIGGER IF EXISTS code_nodes_fts_insert")
        self.execute_sql(conn, "DROP TRIGGER IF EXISTS code_nodes_fts_update")
        self.execute_sql(conn, "DROP TRIGGER IF EXISTS code_nodes_fts_delete")
        
        # Drop FTS5 table
        self.execute_sql(conn, "DROP TABLE IF EXISTS code_nodes_fts")
        
        # Drop indexes
        self.execute_sql(conn, "DROP INDEX IF EXISTS idx_code_nodes_name")
        self.execute_sql(conn, "DROP INDEX IF EXISTS idx_code_nodes_importance_score")
        self.execute_sql(conn, "DROP INDEX IF EXISTS idx_code_nodes_search")