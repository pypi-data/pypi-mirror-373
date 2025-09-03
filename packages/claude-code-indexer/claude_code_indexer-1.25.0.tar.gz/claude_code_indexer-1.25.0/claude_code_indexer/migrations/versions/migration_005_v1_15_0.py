"""Migration to v1.15.0 - Fix enhanced_metadata schema."""

from ..base_migration import BaseMigration


class MigrationV1_15_0(BaseMigration):
    """Fix enhanced_metadata table schema to match LLM enhancer expectations."""
    
    @property
    def version(self) -> str:
        return '1.15.0'
    
    @property
    def description(self) -> str:
        return 'Fix enhanced_metadata table schema to align with LLM metadata enhancer'
    
    def up(self, conn) -> None:
        """Apply migration."""
        # First, backup existing data if any
        cursor = conn.cursor()
        
        # Check if enhanced_metadata table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='enhanced_metadata'
        """)
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Check which columns exist in the current table
            cursor.execute("PRAGMA table_info(enhanced_metadata)")
            columns = {row[1] for row in cursor.fetchall()}
            
            # Create temporary table with new schema
            self.execute_sql(conn, """
                CREATE TABLE enhanced_metadata_new (
                    node_id INTEGER PRIMARY KEY,
                    llm_summary TEXT,
                    role_tags TEXT,
                    complexity_score REAL,
                    quality_metrics TEXT,
                    architectural_layer TEXT,
                    business_domain TEXT,
                    criticality_level TEXT,
                    dependencies_impact REAL,
                    testability_score REAL,
                    last_analyzed TIMESTAMP,
                    analysis_version TEXT,
                    FOREIGN KEY (node_id) REFERENCES code_nodes(id)
                )
            """)
            
            # Build migration query based on existing columns
            if 'description' in columns:
                # v1.14.0 schema with description column
                self.execute_sql(conn, """
                    INSERT INTO enhanced_metadata_new (
                        node_id, 
                        llm_summary,
                        role_tags,
                        architectural_layer,
                        business_domain,
                        last_analyzed
                    )
                    SELECT 
                        node_id,
                        COALESCE(description, ''),
                        COALESCE(tags, '[]'),
                        COALESCE(layer, 'unknown'),
                        COALESCE(role, 'general'),
                        created_at
                    FROM enhanced_metadata
                """)
            else:
                # Handle case where table exists but without expected columns
                # This might happen if database is in an inconsistent state
                self.execute_sql(conn, """
                    INSERT INTO enhanced_metadata_new (node_id)
                    SELECT DISTINCT node_id FROM enhanced_metadata
                """)
            
            
            # Drop old table and rename new one
            self.execute_sql(conn, "DROP TABLE enhanced_metadata")
            self.execute_sql(conn, "ALTER TABLE enhanced_metadata_new RENAME TO enhanced_metadata")
        else:
            # Create table with correct schema if it doesn't exist
            self.execute_sql(conn, """
                CREATE TABLE IF NOT EXISTS enhanced_metadata (
                    node_id INTEGER PRIMARY KEY,
                    llm_summary TEXT,
                    role_tags TEXT,
                    complexity_score REAL,
                    quality_metrics TEXT,
                    architectural_layer TEXT,
                    business_domain TEXT,
                    criticality_level TEXT,
                    dependencies_impact REAL,
                    testability_score REAL,
                    last_analyzed TIMESTAMP,
                    analysis_version TEXT,
                    FOREIGN KEY (node_id) REFERENCES code_nodes(id)
                )
            """)
        
        # Create indexes
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_node_id ON enhanced_metadata(node_id)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_role_tags ON enhanced_metadata(role_tags)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_layer ON enhanced_metadata(architectural_layer)")
    
    def down(self, conn) -> None:
        """Rollback migration - restore v1.14.0 schema."""
        # Create old schema
        self.execute_sql(conn, """
            CREATE TABLE enhanced_metadata_old (
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
        
        # Migrate data back
        self.execute_sql(conn, """
            INSERT INTO enhanced_metadata_old (
                node_id,
                description,
                role,
                layer,
                tags,
                created_at
            )
            SELECT 
                node_id,
                llm_summary,
                business_domain,
                architectural_layer,
                role_tags,
                last_analyzed
            FROM enhanced_metadata
        """)
        
        # Drop new table and rename old one
        self.execute_sql(conn, "DROP TABLE enhanced_metadata")
        self.execute_sql(conn, "ALTER TABLE enhanced_metadata_old RENAME TO enhanced_metadata")