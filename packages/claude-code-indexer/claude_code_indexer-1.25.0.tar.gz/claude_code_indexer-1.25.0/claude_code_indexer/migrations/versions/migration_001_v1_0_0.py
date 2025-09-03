"""Initial database schema - v1.0.0."""

from ..base_migration import BaseMigration


class MigrationV1_0_0(BaseMigration):
    """Create initial database schema."""
    
    @property
    def version(self) -> str:
        return '1.0.0'
    
    @property
    def description(self) -> str:
        return 'Initial database schema with core tables'
    
    def up(self, conn) -> None:
        """Create initial tables."""
        # Create code_nodes table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS code_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                summary TEXT,
                importance_score REAL DEFAULT 0.0,
                relevance_tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create relationships table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS relationships (
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id, relationship_type),
                FOREIGN KEY (source_id) REFERENCES code_nodes(id),
                FOREIGN KEY (target_id) REFERENCES code_nodes(id)
            )
        """)
        
        # Create indexing_metadata table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS indexing_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_code_nodes_type ON code_nodes(node_type)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_code_nodes_path ON code_nodes(path)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id)")
    
    def down(self, conn) -> None:
        """Drop all tables."""
        self.execute_sql(conn, "DROP TABLE IF EXISTS relationships")
        self.execute_sql(conn, "DROP TABLE IF EXISTS code_nodes")
        self.execute_sql(conn, "DROP TABLE IF EXISTS indexing_metadata")