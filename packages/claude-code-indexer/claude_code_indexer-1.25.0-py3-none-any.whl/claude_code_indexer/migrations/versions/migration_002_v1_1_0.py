"""Migration to v1.1.0 - Add pattern detection and analysis tables."""

from ..base_migration import BaseMigration


class MigrationV1_1_0(BaseMigration):
    """Add pattern detection, library usage, and infrastructure tables."""
    
    @property
    def version(self) -> str:
        return '1.1.0'
    
    @property
    def description(self) -> str:
        return 'Add pattern detection, library usage, infrastructure tables and new columns'
    
    def up(self, conn) -> None:
        """Apply migration."""
        # Add new columns to code_nodes
        if not self.column_exists(conn, 'code_nodes', 'weight'):
            self.execute_sql(conn, "ALTER TABLE code_nodes ADD COLUMN weight REAL DEFAULT 1.0")
        
        if not self.column_exists(conn, 'code_nodes', 'frequency_score'):
            self.execute_sql(conn, "ALTER TABLE code_nodes ADD COLUMN frequency_score REAL DEFAULT 0.0")
        
        if not self.column_exists(conn, 'code_nodes', 'usage_stats'):
            self.execute_sql(conn, "ALTER TABLE code_nodes ADD COLUMN usage_stats TEXT")
        
        # Create patterns table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                description TEXT,
                nodes TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create libraries table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS libraries (
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
        """)
        
        # Create infrastructure table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS infrastructure (
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
        """)
        
        # Create indexes
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_patterns_path ON patterns(file_path)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_libraries_path ON libraries(file_path)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_libraries_name ON libraries(name)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_infrastructure_path ON infrastructure(file_path)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_infrastructure_type ON infrastructure(component_type)")
    
    def down(self, conn) -> None:
        """Rollback migration."""
        # Drop tables
        self.execute_sql(conn, "DROP TABLE IF EXISTS patterns")
        self.execute_sql(conn, "DROP TABLE IF EXISTS libraries")
        self.execute_sql(conn, "DROP TABLE IF EXISTS infrastructure")
        
        # Note: We cannot easily remove columns in SQLite
        # Would need to recreate the table without those columns