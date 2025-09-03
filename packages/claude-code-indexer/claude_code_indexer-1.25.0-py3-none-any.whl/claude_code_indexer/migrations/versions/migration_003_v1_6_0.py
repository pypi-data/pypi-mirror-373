"""Migration to v1.6.0 - Add language support and location tracking."""

from ..base_migration import BaseMigration


class MigrationV1_6_0(BaseMigration):
    """Add language, line_number, and column_number columns."""
    
    @property
    def version(self) -> str:
        return '1.6.0'
    
    @property
    def description(self) -> str:
        return 'Add language support and precise location tracking'
    
    def up(self, conn) -> None:
        """Apply migration."""
        # Add language column
        if not self.column_exists(conn, 'code_nodes', 'language'):
            self.execute_sql(conn, """
                ALTER TABLE code_nodes 
                ADD COLUMN language TEXT DEFAULT 'python'
            """)
        
        # Add line_number column
        if not self.column_exists(conn, 'code_nodes', 'line_number'):
            self.execute_sql(conn, """
                ALTER TABLE code_nodes 
                ADD COLUMN line_number INTEGER DEFAULT 0
            """)
        
        # Add column_number column
        if not self.column_exists(conn, 'code_nodes', 'column_number'):
            self.execute_sql(conn, """
                ALTER TABLE code_nodes 
                ADD COLUMN column_number INTEGER DEFAULT 0
            """)
        
        # Create index for language queries
        self.execute_sql(conn, """
            CREATE INDEX IF NOT EXISTS idx_code_nodes_language 
            ON code_nodes(language)
        """)
    
    def down(self, conn) -> None:
        """Rollback migration."""
        # Note: SQLite doesn't support dropping columns easily
        # Would need to recreate the table without these columns
        pass