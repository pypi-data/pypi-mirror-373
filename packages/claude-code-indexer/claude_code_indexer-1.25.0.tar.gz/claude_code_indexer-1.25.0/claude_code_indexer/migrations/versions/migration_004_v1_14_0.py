"""Migration to v1.14.0 - Add LLM enhancement tables."""

from ..base_migration import BaseMigration


class MigrationV1_14_0(BaseMigration):
    """Add LLM-enhanced metadata and pattern detection tables."""
    
    @property
    def version(self) -> str:
        return '1.14.0'
    
    @property
    def description(self) -> str:
        return 'Add LLM-enhanced metadata, detected patterns, and code evolution tables'
    
    def up(self, conn) -> None:
        """Apply migration."""
        # Create enhanced_metadata table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS enhanced_metadata (
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
        
        # Create detected_patterns table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS detected_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id INTEGER NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_name TEXT,
                confidence_score REAL,
                implementation_details TEXT,
                related_nodes TEXT,
                best_practices TEXT,
                potential_issues TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES code_nodes(id)
            )
        """)
        
        # Create code_evolution table
        self.execute_sql(conn, """
            CREATE TABLE IF NOT EXISTS code_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id INTEGER NOT NULL,
                change_frequency INTEGER DEFAULT 0,
                last_major_change TEXT,
                stability_score REAL,
                coupled_changes TEXT,
                refactoring_suggestions TEXT,
                evolution_patterns TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES code_nodes(id)
            )
        """)
        
        # Create indexes for better query performance
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_node_id ON enhanced_metadata(node_id)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_detected_patterns_node_id ON detected_patterns(node_id)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_code_evolution_node_id ON code_evolution(node_id)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_role_tags ON enhanced_metadata(role, tags)")
        self.execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_layer ON enhanced_metadata(layer)")
    
    def down(self, conn) -> None:
        """Rollback migration."""
        self.execute_sql(conn, "DROP TABLE IF EXISTS code_evolution")
        self.execute_sql(conn, "DROP TABLE IF EXISTS detected_patterns")
        self.execute_sql(conn, "DROP TABLE IF EXISTS enhanced_metadata")