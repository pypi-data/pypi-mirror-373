#!/usr/bin/env python3
"""
LLM-Driven Metadata Enhancement System
Enables intelligent analysis and dynamic updating of code metadata
"""

import asyncio
import json
import sqlite3
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading

from .logger import log_info, log_warning, log_error


@dataclass 
class EnhancedMetadata:
    """Enhanced metadata for code entities"""
    node_id: int
    llm_summary: str
    role_tags: List[str]  # e.g., ['api_endpoint', 'data_model', 'utility']
    complexity_score: float  # 0.0 to 1.0
    quality_metrics: Dict[str, Any]  # JSON object with various metrics
    architectural_layer: str  # 'controller', 'service', 'model', 'utility', etc.
    business_domain: str  # 'authentication', 'payment', 'user_management', etc.
    criticality_level: str  # 'critical', 'important', 'normal', 'low'
    dependencies_impact: float  # How much this affects other components
    testability_score: float  # How testable this component is
    last_analyzed: str
    analysis_version: str = "1.0"


@dataclass
class DetectedPattern:
    """Design pattern detection result"""
    node_id: int
    pattern_type: str  # 'singleton', 'factory', 'observer', etc.
    confidence: float  # 0.0 to 1.0
    details: Dict[str, Any]
    detected_at: str


@dataclass
class CodeEvolution:
    """Code evolution tracking"""
    node_id: int
    change_type: str  # 'added', 'modified', 'deleted', 'refactored'
    impact_score: float  # Estimated impact on codebase
    change_summary: str
    timestamp: str


class LLMMetadataEnhancer:
    """
    LLM-driven code analysis and metadata enhancement system
    
    Features:
    - Intelligent role detection and tagging
    - Complexity and quality analysis
    - Pattern recognition
    - Evolution tracking
    - Proactive metadata updates
    """
    
    def __init__(self, db_path: str, llm_provider: str = "anthropic"):
        self.db_path = db_path
        self.llm_provider = llm_provider
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="LLMEnhancer")
        
        # Initialize database schema
        self._init_enhanced_schema()
        
        # Analysis cache
        self._analysis_cache = {}
        
        # Tag taxonomy
        self.role_taxonomy = {
            "api": ["endpoint", "route", "handler", "controller"],
            "data": ["model", "entity", "dto", "schema", "repository"],
            "business": ["service", "manager", "processor", "calculator"],
            "utility": ["helper", "util", "formatter", "validator"],
            "infrastructure": ["config", "logger", "database", "cache"],
            "test": ["unit_test", "integration_test", "mock", "fixture"]
        }
        
        self.complexity_factors = {
            "cyclomatic": 0.3,  # Cyclomatic complexity
            "cognitive": 0.25,   # Cognitive load
            "dependencies": 0.2,  # Number of dependencies
            "size": 0.15,        # Lines of code
            "nesting": 0.1       # Nesting level
        }
    
    def _init_enhanced_schema(self):
        """Initialize enhanced metadata tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Enhanced metadata table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_metadata (
                node_id INTEGER PRIMARY KEY,
                llm_summary TEXT,
                role_tags TEXT,  -- JSON array
                complexity_score REAL,
                quality_metrics TEXT,  -- JSON object
                architectural_layer TEXT,
                business_domain TEXT,
                criticality_level TEXT,
                dependencies_impact REAL,
                testability_score REAL,
                last_analyzed TIMESTAMP,
                analysis_version TEXT,
                FOREIGN KEY (node_id) REFERENCES code_nodes(id)
            )
            ''')
            
            # Pattern detection table
            cursor.execute('''
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
            ''')
            
            # Evolution tracking table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_evolution (
                id INTEGER PRIMARY KEY,
                node_id INTEGER,
                change_type TEXT,
                impact_score REAL,
                change_summary TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES code_nodes(id)
            )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_node_id ON enhanced_metadata(node_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_detected_patterns_node_id ON detected_patterns(node_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_code_evolution_node_id ON code_evolution(node_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_role_tags ON enhanced_metadata(role_tags)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_enhanced_metadata_layer ON enhanced_metadata(architectural_layer)')
            
            conn.commit()
    
    def analyze_codebase(self, limit: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Analyze entire codebase with LLM enhancement
        
        Args:
            limit: Limit number of nodes to analyze
            force_refresh: Force re-analysis even if cached
            
        Returns:
            Analysis summary with statistics
        """
        start_time = time.time()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get nodes that need analysis
            if force_refresh:
                query = """
                SELECT id, node_type, name, path, summary, importance_score 
                FROM code_nodes 
                ORDER BY importance_score DESC
                """
                if limit:
                    query += f" LIMIT {limit}"
            else:
                query = """
                SELECT cn.id, cn.node_type, cn.name, cn.path, cn.summary, cn.importance_score
                FROM code_nodes cn
                LEFT JOIN enhanced_metadata em ON cn.id = em.node_id
                WHERE em.node_id IS NULL OR em.last_analyzed < datetime('now', '-7 days')
                ORDER BY cn.importance_score DESC
                """
                if limit:
                    query += f" LIMIT {limit}"
            
            cursor.execute(query)
            nodes_to_analyze = cursor.fetchall()
        
        if not nodes_to_analyze:
            return {"message": "All nodes are up to date", "analyzed_count": 0}
        
        log_info(f"🔍 Analyzing {len(nodes_to_analyze)} nodes with LLM enhancement...")
        
        # Process nodes in batches
        batch_size = 10
        total_analyzed = 0
        
        for i in range(0, len(nodes_to_analyze), batch_size):
            batch = nodes_to_analyze[i:i + batch_size]
            
            # Process batch in parallel
            futures = []
            for node_data in batch:
                future = self._executor.submit(self._analyze_single_node, node_data)
                futures.append(future)
            
            # Wait for batch completion
            for future in futures:
                try:
                    result = future.result(timeout=30)  # 30s timeout per node
                    if result:
                        total_analyzed += 1
                except Exception as e:
                    log_warning(f"Node analysis failed: {e}")
        
        duration = time.time() - start_time
        
        # Generate summary statistics
        summary = self._generate_analysis_summary()
        summary.update({
            "analyzed_count": total_analyzed,
            "total_nodes": len(nodes_to_analyze),
            "analysis_duration": f"{duration:.2f}s",
            "nodes_per_second": f"{total_analyzed / duration:.1f}" if duration > 0 else "∞"
        })
        
        log_info(f"✅ Analysis complete: {total_analyzed} nodes in {duration:.1f}s")
        return summary
    
    def _analyze_single_node(self, node_data: Tuple) -> Optional[EnhancedMetadata]:
        """Analyze a single node with LLM"""
        node_id, node_type, name, path, summary, importance_score = node_data
        
        try:
            # Prepare context for LLM analysis
            context = {
                "node_type": node_type,
                "name": name,
                "path": path,
                "summary": summary or "",
                "importance_score": importance_score
            }
            
            # Get source code context if available
            source_context = self._get_source_context(node_id)
            if source_context:
                context.update(source_context)
            
            # Perform LLM analysis
            analysis_result = self._perform_llm_analysis(context)
            
            if analysis_result:
                # Create enhanced metadata
                enhanced_metadata = EnhancedMetadata(
                    node_id=node_id,
                    llm_summary=analysis_result.get("summary", ""),
                    role_tags=analysis_result.get("role_tags", []),
                    complexity_score=analysis_result.get("complexity_score", 0.5),
                    quality_metrics=analysis_result.get("quality_metrics", {}),
                    architectural_layer=analysis_result.get("architectural_layer", "unknown"),
                    business_domain=analysis_result.get("business_domain", "general"),
                    criticality_level=analysis_result.get("criticality_level", "normal"),
                    dependencies_impact=analysis_result.get("dependencies_impact", 0.5),
                    testability_score=analysis_result.get("testability_score", 0.5),
                    last_analyzed=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # Save to database
                self._save_enhanced_metadata(enhanced_metadata)
                
                # Detect patterns
                patterns = analysis_result.get("patterns", [])
                for pattern in patterns:
                    self._save_detected_pattern(node_id, pattern)
                
                return enhanced_metadata
                
        except Exception as e:
            log_error(f"Failed to analyze node {node_id}: {e}")
            return None
    
    def _perform_llm_analysis(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform LLM analysis on code context
        
        For now, this is a mock implementation that demonstrates the structure.
        In a real implementation, this would call LLM APIs (OpenAI, Anthropic, etc.)
        """
        
        # Mock analysis based on code patterns and context
        node_type = context.get("node_type", "")
        name = context.get("name", "")
        path = context.get("path", "")
        
        # Mock intelligent analysis
        role_tags = self._infer_role_tags(node_type, name, path)
        complexity_score = self._calculate_complexity_score(context)
        
        # Mock architectural layer detection
        architectural_layer = self._infer_architectural_layer(name, path, role_tags)
        
        # Mock business domain detection
        business_domain = self._infer_business_domain(name, path)
        
        # Mock criticality assessment
        criticality_level = self._assess_criticality(context.get("importance_score", 0), role_tags)
        
        return {
            "summary": f"Enhanced analysis of {name}: {node_type} in {architectural_layer} layer",
            "role_tags": role_tags,
            "complexity_score": complexity_score,
            "quality_metrics": {
                "maintainability": 0.8,
                "readability": 0.7,
                "testability": 0.6,
                "performance": 0.8
            },
            "architectural_layer": architectural_layer,
            "business_domain": business_domain,
            "criticality_level": criticality_level,
            "dependencies_impact": min(context.get("importance_score", 0) * 1.2, 1.0),
            "testability_score": 0.7 if "test" in role_tags else 0.5,
            "patterns": self._detect_design_patterns(context)
        }
    
    def _infer_role_tags(self, node_type: str, name: str, path: str) -> List[str]:
        """Infer role tags based on naming patterns and structure"""
        tags = []
        
        name_lower = name.lower()
        path_lower = path.lower()
        
        # API-related (including authentication functions)
        if any(keyword in name_lower for keyword in ["endpoint", "route", "handler", "controller", "api", "authenticate", "login", "logout", "signin", "signup"]):
            tags.append("api_endpoint")
        
        # Data-related
        if any(keyword in name_lower for keyword in ["model", "entity", "dto", "schema", "save", "load", "persist"]):
            tags.append("data_model")
        
        # Service layer
        if any(keyword in name_lower for keyword in ["service", "manager", "processor", "factory", "builder"]):
            tags.append("business_service")
        
        # Utility functions
        if any(keyword in name_lower for keyword in ["util", "helper", "formatter", "validator", "format", "parse", "convert"]):
            tags.append("utility")
        
        # Test-related
        if any(keyword in path_lower for keyword in ["test", "spec"]) or node_type == "test":
            tags.append("test")
        
        # Infrastructure
        if any(keyword in name_lower for keyword in ["config", "logger", "database", "cache", "db", "redis", "mongo"]):
            tags.append("infrastructure")
        
        # Authentication specific
        if any(keyword in name_lower for keyword in ["auth", "password", "token", "session", "credential"]):
            if "api_endpoint" not in tags:
                tags.append("api_endpoint")
        
        # Payment specific
        if any(keyword in name_lower for keyword in ["payment", "pay", "billing", "invoice", "charge", "transaction"]):
            if "business_service" not in tags:
                tags.append("business_service")
        
        return tags or ["general"]
    
    def _calculate_complexity_score(self, context: Dict[str, Any]) -> float:
        """Calculate complexity score based on various factors"""
        # Mock calculation - in real implementation would analyze AST
        base_score = 0.3
        
        # Adjust based on node type
        node_type = context.get("node_type", "")
        if node_type == "class":
            base_score += 0.2
        elif node_type == "function":
            base_score += 0.1
        
        # Adjust based on importance
        importance = context.get("importance_score", 0)
        base_score += importance * 0.3
        
        return min(base_score, 1.0)
    
    def _infer_architectural_layer(self, name: str, path: str, role_tags: List[str]) -> str:
        """Infer architectural layer from context"""
        path_lower = path.lower()
        name_lower = name.lower()
        
        if "api_endpoint" in role_tags or any(keyword in path_lower for keyword in ["controller", "handler", "route"]):
            return "controller"
        elif "business_service" in role_tags or any(keyword in path_lower for keyword in ["service", "business"]):
            return "service"
        elif "data_model" in role_tags or any(keyword in path_lower for keyword in ["model", "entity", "repository"]):
            return "model"
        elif "infrastructure" in role_tags:
            return "infrastructure"
        elif "test" in role_tags:
            return "test"
        else:
            return "utility"
    
    def _infer_business_domain(self, name: str, path: str) -> str:
        """Infer business domain from naming patterns"""
        text = f"{name} {path}".lower()
        
        domain_keywords = {
            "authentication": ["auth", "login", "signin", "signup", "session", "credential"],
            "payment": ["payment", "billing", "invoice", "charge", "transaction"],
            "user_management": ["user", "profile", "account", "member", "userprofile", "usermanager"],
            "data_processing": ["process", "transform", "parse", "analyze"],
            "api": ["api", "endpoint", "route", "handler"],
            "database": ["db", "database", "repository", "dao"],
            "configuration": ["config", "setting", "environment"],
            "logging": ["log", "logger", "audit", "trace"],
            "testing": ["test", "spec", "mock", "fixture"]
        }
        
        # Check more specific domains first
        for domain, keywords in domain_keywords.items():
            if any(keyword in text for keyword in keywords):
                # For user domain, check if it's actually user management specific
                if domain == "user_management" and any(specific in text for specific in ["userprofile", "usermanager", "profile"]):
                    return domain
                elif domain != "user_management":
                    return domain
        
        # Fallback check for user_management with generic "user" 
        if "user" in text and not any(auth_kw in text for auth_kw in ["auth", "login", "signin", "signup", "session", "credential"]):
            return "user_management"
        
        return "general"
    
    def _assess_criticality(self, importance_score: float, role_tags: List[str]) -> str:
        """Assess criticality level"""
        if importance_score > 0.8 or "api_endpoint" in role_tags:
            return "critical"
        elif importance_score > 0.6 or "business_service" in role_tags:
            return "important"
        elif importance_score > 0.3:
            return "normal"
        else:
            return "low"
    
    def _detect_design_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect design patterns in code context"""
        patterns = []
        
        name = context.get("name", "").lower()
        node_type = context.get("node_type", "")
        
        # Singleton pattern
        if "singleton" in name or ("instance" in name and node_type == "class"):
            patterns.append({
                "pattern_type": "singleton",
                "confidence": 0.7,
                "description": "Potential singleton pattern detected"
            })
        
        # Factory pattern
        if any(keyword in name for keyword in ["factory", "creator", "builder"]):
            patterns.append({
                "pattern_type": "factory",
                "confidence": 0.6,
                "description": "Factory pattern detected"
            })
        
        # Observer pattern
        if any(keyword in name for keyword in ["observer", "listener", "subscriber"]):
            patterns.append({
                "pattern_type": "observer",
                "confidence": 0.8,
                "description": "Observer pattern detected"
            })
        
        return patterns
    
    def _get_source_context(self, node_id: int) -> Optional[Dict[str, Any]]:
        """Get additional source code context for a node"""
        # This would fetch relationship data, dependencies, etc.
        # For now, return basic context
        return {
            "has_dependencies": True,
            "dependency_count": 3,
            "is_dependency": True
        }
    
    def _save_enhanced_metadata(self, metadata: EnhancedMetadata):
        """Save enhanced metadata to database"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT OR REPLACE INTO enhanced_metadata 
                (node_id, llm_summary, role_tags, complexity_score, quality_metrics,
                 architectural_layer, business_domain, criticality_level, 
                 dependencies_impact, testability_score, last_analyzed, analysis_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metadata.node_id,
                    metadata.llm_summary,
                    json.dumps(metadata.role_tags),
                    metadata.complexity_score,
                    json.dumps(metadata.quality_metrics),
                    metadata.architectural_layer,
                    metadata.business_domain,
                    metadata.criticality_level,
                    metadata.dependencies_impact,
                    metadata.testability_score,
                    metadata.last_analyzed,
                    metadata.analysis_version
                ))
                conn.commit()
    
    def _save_detected_pattern(self, node_id: int, pattern: Dict[str, Any]):
        """Save detected pattern to database"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO detected_patterns 
                (node_id, pattern_type, confidence_score, implementation_details)
                VALUES (?, ?, ?, ?)
                ''', (
                    node_id,
                    pattern["pattern_type"],
                    pattern.get("confidence", 0.0),
                    json.dumps(pattern)
                ))
                conn.commit()
    
    def _generate_analysis_summary(self) -> Dict[str, Any]:
        """Generate analysis summary from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count by architectural layers
            cursor.execute('''
            SELECT architectural_layer, COUNT(*) 
            FROM enhanced_metadata 
            GROUP BY architectural_layer
            ''')
            layers = dict(cursor.fetchall())
            
            # Count by criticality
            cursor.execute('''
            SELECT criticality_level, COUNT(*) 
            FROM enhanced_metadata 
            GROUP BY criticality_level
            ''')
            criticality = dict(cursor.fetchall())
            
            # Count by business domain
            cursor.execute('''
            SELECT business_domain, COUNT(*) 
            FROM enhanced_metadata 
            GROUP BY business_domain
            ''')
            domains = dict(cursor.fetchall())
            
            # Average scores
            cursor.execute('''
            SELECT 
                AVG(complexity_score) as avg_complexity,
                AVG(dependencies_impact) as avg_impact,
                AVG(testability_score) as avg_testability
            FROM enhanced_metadata
            ''')
            avg_scores = cursor.fetchone()
            
            # Pattern counts
            cursor.execute('''
            SELECT pattern_type, COUNT(*) 
            FROM detected_patterns 
            GROUP BY pattern_type
            ''')
            patterns = dict(cursor.fetchall())
        
        return {
            "architectural_layers": layers,
            "criticality_distribution": criticality,
            "business_domains": domains,
            "average_scores": {
                "complexity": round(avg_scores[0] or 0, 3),
                "dependencies_impact": round(avg_scores[1] or 0, 3),
                "testability": round(avg_scores[2] or 0, 3)
            },
            "detected_patterns": patterns
        }
    
    def get_enhanced_nodes(self, 
                          architectural_layer: Optional[str] = None,
                          business_domain: Optional[str] = None,
                          criticality_level: Optional[str] = None,
                          min_complexity: Optional[float] = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """
        Query enhanced metadata with filters
        
        Args:
            architectural_layer: Filter by layer (controller, service, model, etc.)
            business_domain: Filter by domain (authentication, payment, etc.)
            criticality_level: Filter by criticality (critical, important, normal, low)
            min_complexity: Filter by minimum complexity score
            limit: Maximum results to return
            
        Returns:
            List of enhanced node data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
            SELECT cn.id, cn.name, cn.path, cn.node_type, cn.importance_score,
                   em.llm_summary, em.role_tags, em.complexity_score,
                   em.architectural_layer, em.business_domain, em.criticality_level,
                   em.dependencies_impact, em.testability_score
            FROM code_nodes cn
            JOIN enhanced_metadata em ON cn.id = em.node_id
            WHERE 1=1
            '''
            
            params = []
            
            if architectural_layer:
                query += " AND em.architectural_layer = ?"
                params.append(architectural_layer)
            
            if business_domain:
                query += " AND em.business_domain = ?"
                params.append(business_domain)
            
            if criticality_level:
                query += " AND em.criticality_level = ?"
                params.append(criticality_level)
            
            if min_complexity:
                query += " AND em.complexity_score >= ?"
                params.append(min_complexity)
            
            query += " ORDER BY cn.importance_score DESC, em.complexity_score DESC"
            query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert to dictionaries
            columns = [desc[0] for desc in cursor.description]
            nodes = []
            for row in results:
                node_dict = dict(zip(columns, row))
                # Parse JSON fields
                if node_dict.get('role_tags'):
                    node_dict['role_tags'] = json.loads(node_dict['role_tags'])
                nodes.append(node_dict)
            
            return nodes
    
    def update_node_metadata(self, node_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update specific metadata fields for a node
        
        Args:
            node_id: ID of the node to update
            updates: Dictionary of field updates
            
        Returns:
            True if successful
        """
        allowed_fields = {
            'llm_summary', 'role_tags', 'complexity_score', 'quality_metrics',
            'architectural_layer', 'business_domain', 'criticality_level',
            'dependencies_impact', 'testability_score'
        }
        
        # Filter to allowed fields
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not filtered_updates:
            return False
        
        try:
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Build dynamic update query
                    set_clauses = []
                    params = []
                    
                    for field, value in filtered_updates.items():
                        if field in ['role_tags', 'quality_metrics'] and isinstance(value, (list, dict)):
                            set_clauses.append(f"{field} = ?")
                            params.append(json.dumps(value))
                        else:
                            set_clauses.append(f"{field} = ?")
                            params.append(value)
                    
                    set_clauses.append("last_analyzed = ?")
                    params.append(time.strftime("%Y-%m-%d %H:%M:%S"))
                    params.append(node_id)
                    
                    query = f"UPDATE enhanced_metadata SET {', '.join(set_clauses)} WHERE node_id = ?"
                    cursor.execute(query, params)
                    
                    return cursor.rowcount > 0
                    
        except Exception as e:
            log_error(f"Failed to update metadata for node {node_id}: {e}")
            return False
    
    def get_analysis_insights(self) -> Dict[str, Any]:
        """Get high-level insights from the enhanced metadata"""
        summary = self._generate_analysis_summary()
        
        insights = {
            "codebase_health": self._assess_codebase_health(summary),
            "architectural_overview": self._get_architectural_insights(summary),
            "complexity_hotspots": self._identify_complexity_hotspots(),
            "improvement_suggestions": self._generate_improvement_suggestions(summary)
        }
        
        return insights
    
    def _assess_codebase_health(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall codebase health"""
        avg_scores = summary.get("average_scores", {})
        complexity = avg_scores.get("complexity", 0.5)
        testability = avg_scores.get("testability", 0.5)
        
        health_score = (1 - complexity) * 0.4 + testability * 0.6
        
        return {
            "overall_score": round(health_score, 3),
            "complexity_health": "good" if complexity < 0.6 else "needs_attention" if complexity < 0.8 else "poor",
            "testability_health": "good" if testability > 0.7 else "needs_attention" if testability > 0.5 else "poor",
            "recommendations": self._get_health_recommendations(complexity, testability)
        }
    
    def _get_architectural_insights(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Get architectural insights"""
        layers = summary.get("architectural_layers", {})
        domains = summary.get("business_domains", {})
        
        return {
            "layer_distribution": layers,
            "domain_distribution": domains,
            "layer_balance": self._assess_layer_balance(layers),
            "domain_focus": max(domains.items(), key=lambda x: x[1])[0] if domains else "unknown"
        }
    
    def _identify_complexity_hotspots(self) -> List[Dict[str, Any]]:
        """Identify complexity hotspots"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT cn.name, cn.path, em.complexity_score, em.architectural_layer
            FROM code_nodes cn
            JOIN enhanced_metadata em ON cn.id = em.node_id
            WHERE em.complexity_score > 0.7
            ORDER BY em.complexity_score DESC
            LIMIT 10
            ''')
            
            hotspots = []
            for row in cursor.fetchall():
                hotspots.append({
                    "name": row[0],
                    "path": row[1],
                    "complexity": row[2],
                    "layer": row[3]
                })
            
            return hotspots
    
    def _generate_improvement_suggestions(self, summary: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        avg_scores = summary.get("average_scores", {})
        complexity = avg_scores.get("complexity", 0.5)
        testability = avg_scores.get("testability", 0.5)
        
        if complexity > 0.7:
            suggestions.append("Consider refactoring high-complexity components")
        
        if testability < 0.5:
            suggestions.append("Improve testability by reducing dependencies and adding interfaces")
        
        layers = summary.get("architectural_layers", {})
        if layers.get("controller", 0) > layers.get("service", 0) * 2:
            suggestions.append("Consider moving business logic from controllers to service layer")
        
        return suggestions
    
    def _get_health_recommendations(self, complexity: float, testability: float) -> List[str]:
        """Get health-based recommendations"""
        recommendations = []
        
        if complexity > 0.7:
            recommendations.append("Reduce complexity through refactoring and decomposition")
        
        if testability < 0.6:
            recommendations.append("Improve testability by adding dependency injection")
        
        return recommendations
    
    def _assess_layer_balance(self, layers: Dict[str, int]) -> str:
        """Assess architectural layer balance"""
        total = sum(layers.values())
        if total == 0:
            return "unknown"
        
        service_ratio = layers.get("service", 0) / total
        controller_ratio = layers.get("controller", 0) / total
        
        if service_ratio > 0.4:
            return "service_heavy"
        elif controller_ratio > 0.4:
            return "controller_heavy"
        else:
            return "balanced"
    
    def shutdown(self):
        """Shutdown the enhancer"""
        self._executor.shutdown(wait=True)
        log_info("🤖 LLM Metadata Enhancer shutdown complete")