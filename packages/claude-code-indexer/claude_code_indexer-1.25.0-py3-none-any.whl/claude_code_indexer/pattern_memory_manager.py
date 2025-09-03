#!/usr/bin/env python3
"""
Pattern & Best Practices Memory Manager
Specialized system for LLMs to store and retrieve coding patterns, best practices,
architectural decisions, and project-specific guidelines.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum

from .llm_memory_storage import LLMMemoryStorage
from .logger import log_info, log_warning


class PatternType(Enum):
    """Types of patterns that can be stored."""
    ARCHITECTURE = "architecture"           # High-level architecture patterns
    DESIGN_PATTERN = "design_pattern"       # GoF and other design patterns
    CODE_STYLE = "code_style"               # Code formatting and style rules
    NAMING_CONVENTION = "naming_convention" # Variable, function, class naming
    ERROR_HANDLING = "error_handling"       # Error handling patterns
    SECURITY = "security"                   # Security best practices
    PERFORMANCE = "performance"             # Performance optimization patterns
    TESTING = "testing"                     # Testing patterns and practices
    API_DESIGN = "api_design"               # API design patterns
    DATABASE = "database"                   # Database patterns and practices
    DEPLOYMENT = "deployment"               # Deployment and infrastructure
    DOCUMENTATION = "documentation"         # Documentation standards


class BestPracticeCategory(Enum):
    """Categories of best practices."""
    TEAM_STANDARDS = "team_standards"       # Team-specific coding standards
    PROJECT_RULES = "project_rules"         # Project-specific rules
    INDUSTRY_BEST = "industry_best"         # Industry standard best practices
    COMPANY_POLICY = "company_policy"       # Company-wide policies
    TOOL_USAGE = "tool_usage"               # How to use specific tools/frameworks
    CODE_REVIEW = "code_review"             # Code review guidelines
    REFACTORING = "refactoring"             # Refactoring guidelines
    MAINTENANCE = "maintenance"             # Code maintenance practices


@dataclass
class PatternMemory:
    """Structure for storing coding patterns."""
    pattern_id: str                         # Unique pattern identifier
    pattern_type: PatternType              # Type of pattern
    title: str                             # Short descriptive title
    description: str                       # Detailed description
    example_code: Optional[str] = None     # Code example
    anti_pattern: Optional[str] = None     # What NOT to do
    when_to_use: Optional[str] = None      # Usage guidelines
    benefits: List[str] = None             # Benefits of using this pattern
    trade_offs: List[str] = None           # Trade-offs to consider
    related_patterns: List[str] = None     # Related pattern IDs
    tags: List[str] = None                 # Categorization tags
    confidence: float = 1.0                # LLM confidence in this pattern
    usage_frequency: int = 0               # How often this pattern is used
    last_applied: Optional[str] = None     # Last time pattern was applied
    created_by: str = "llm"                # Who created this pattern
    created_at: str = None                 # Creation timestamp
    updated_at: str = None                 # Last update timestamp


@dataclass  
class BestPractice:
    """Structure for storing best practices."""
    practice_id: str                       # Unique practice identifier
    category: BestPracticeCategory         # Category of best practice
    title: str                             # Short title
    description: str                       # Detailed description
    rationale: str                         # Why this is a best practice
    examples: List[str] = None             # Examples of good implementation
    counter_examples: List[str] = None     # Examples of what to avoid
    enforcement_level: str = "should"      # must/should/could/avoid
    scope: str = "project"                 # project/team/company/global
    tools_required: List[str] = None       # Tools needed to implement
    metrics: Dict[str, Any] = None         # How to measure compliance
    exceptions: List[str] = None           # When exceptions are allowed
    tags: List[str] = None                 # Categorization tags
    priority: str = "medium"               # high/medium/low
    compliance_score: float = 0.0          # Current compliance score
    created_by: str = "llm"                # Who created this practice
    created_at: str = None                 # Creation timestamp
    updated_at: str = None                 # Last update timestamp


class PatternMemoryManager:
    """Manages patterns and best practices for LLMs."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.memory_storage = LLMMemoryStorage(db_path)
        self._init_pattern_tables()
    
    def _init_pattern_tables(self):
        """Initialize pattern-specific tables."""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Create patterns table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coding_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    example_code TEXT,
                    anti_pattern TEXT,
                    when_to_use TEXT,
                    benefits TEXT,  -- JSON array
                    trade_offs TEXT,  -- JSON array
                    related_patterns TEXT,  -- JSON array
                    tags TEXT,  -- JSON array
                    confidence REAL DEFAULT 1.0,
                    usage_frequency INTEGER DEFAULT 0,
                    last_applied TIMESTAMP,
                    created_by TEXT DEFAULT 'llm',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create best practices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS best_practices (
                    practice_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    examples TEXT,  -- JSON array
                    counter_examples TEXT,  -- JSON array
                    enforcement_level TEXT DEFAULT 'should',
                    scope TEXT DEFAULT 'project',
                    tools_required TEXT,  -- JSON array
                    metrics TEXT,  -- JSON object
                    exceptions TEXT,  -- JSON array
                    tags TEXT,  -- JSON array
                    priority TEXT DEFAULT 'medium',
                    compliance_score REAL DEFAULT 0.0,
                    created_by TEXT DEFAULT 'llm',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create pattern usage tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT NOT NULL,
                    node_id INTEGER,
                    file_path TEXT,
                    usage_context TEXT,
                    applied_by TEXT DEFAULT 'llm',
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    effectiveness_score REAL,
                    notes TEXT,
                    FOREIGN KEY (pattern_id) REFERENCES coding_patterns(pattern_id),
                    FOREIGN KEY (node_id) REFERENCES code_nodes(id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_type ON coding_patterns(pattern_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_tags ON coding_patterns(tags)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_practices_category ON best_practices(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_practices_priority ON best_practices(priority)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_pattern ON pattern_usage(pattern_id)")
    
    def store_pattern(
        self,
        pattern_type: PatternType,
        title: str,
        description: str,
        example_code: Optional[str] = None,
        anti_pattern: Optional[str] = None,
        when_to_use: Optional[str] = None,
        benefits: Optional[List[str]] = None,
        trade_offs: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        llm_name: str = "claude",
        confidence: float = 1.0
    ) -> str:
        """Store a coding pattern.
        
        Returns:
            pattern_id for the stored pattern
        """
        timestamp = datetime.utcnow().isoformat()
        pattern_id = f"{pattern_type.value}_{title.lower().replace(' ', '_')}_{timestamp[:10]}"
        
        # Convert lists to JSON
        benefits_json = json.dumps(benefits or [])
        trade_offs_json = json.dumps(trade_offs or [])
        tags_json = json.dumps(tags or [])
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO coding_patterns (
                    pattern_id, pattern_type, title, description, example_code,
                    anti_pattern, when_to_use, benefits, trade_offs, tags,
                    confidence, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id, pattern_type.value, title, description, example_code,
                anti_pattern, when_to_use, benefits_json, trade_offs_json, tags_json,
                confidence, llm_name, timestamp, timestamp
            ))
        
        # Also store in LLM memory for searchability
        self.memory_storage.store_memory(
            node_id=0,  # Special node for project-level patterns
            llm_name=llm_name,
            memory_type="pattern",
            content=f"Pattern: {title}\n\n{description}",
            metadata={
                "pattern_id": pattern_id,
                "pattern_type": pattern_type.value,
                "confidence": confidence
            },
            tags=tags
        )
        
        log_info(f"✅ Stored coding pattern: {title}")
        return pattern_id
    
    def store_best_practice(
        self,
        category: BestPracticeCategory,
        title: str,
        description: str,
        rationale: str,
        examples: Optional[List[str]] = None,
        counter_examples: Optional[List[str]] = None,
        enforcement_level: str = "should",
        scope: str = "project",
        tools_required: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        priority: str = "medium",
        llm_name: str = "claude"
    ) -> str:
        """Store a best practice.
        
        Returns:
            practice_id for the stored practice
        """
        timestamp = datetime.utcnow().isoformat()
        practice_id = f"{category.value}_{title.lower().replace(' ', '_')}_{timestamp[:10]}"
        
        # Convert lists to JSON
        examples_json = json.dumps(examples or [])
        counter_examples_json = json.dumps(counter_examples or [])
        tools_json = json.dumps(tools_required or [])
        tags_json = json.dumps(tags or [])
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO best_practices (
                    practice_id, category, title, description, rationale,
                    examples, counter_examples, enforcement_level, scope,
                    tools_required, tags, priority, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                practice_id, category.value, title, description, rationale,
                examples_json, counter_examples_json, enforcement_level, scope,
                tools_json, tags_json, priority, llm_name, timestamp, timestamp
            ))
        
        # Also store in LLM memory
        self.memory_storage.store_memory(
            node_id=0,  # Special node for project-level practices
            llm_name=llm_name,
            memory_type="best_practice",
            content=f"Best Practice: {title}\n\n{description}\n\nRationale: {rationale}",
            metadata={
                "practice_id": practice_id,
                "category": category.value,
                "enforcement_level": enforcement_level,
                "priority": priority
            },
            tags=tags
        )
        
        log_info(f"✅ Stored best practice: {title}")
        return practice_id
    
    def get_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        tags: Optional[List[str]] = None,
        min_confidence: float = 0.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve coding patterns with filters."""
        query = "SELECT * FROM coding_patterns WHERE confidence >= ?"
        params = [min_confidence]
        
        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type.value)
        
        if tags:
            # Search for any of the provided tags
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            query += f" AND ({' OR '.join(tag_conditions)})"
        
        query += " ORDER BY usage_frequency DESC, confidence DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            patterns = []
            for row in cursor.fetchall():
                pattern = dict(row)
                # Parse JSON fields
                pattern['benefits'] = json.loads(pattern['benefits'] or '[]')
                pattern['trade_offs'] = json.loads(pattern['trade_offs'] or '[]')
                pattern['tags'] = json.loads(pattern['tags'] or '[]')
                patterns.append(pattern)
            
            return patterns
    
    def get_best_practices(
        self,
        category: Optional[BestPracticeCategory] = None,
        priority: Optional[str] = None,
        enforcement_level: Optional[str] = None,
        scope: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve best practices with filters."""
        query = "SELECT * FROM best_practices WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        if enforcement_level:
            query += " AND enforcement_level = ?"
            params.append(enforcement_level)
        
        if scope:
            query += " AND scope = ?"
            params.append(scope)
        
        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            query += f" AND ({' OR '.join(tag_conditions)})"
        
        query += " ORDER BY priority DESC, compliance_score DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            practices = []
            for row in cursor.fetchall():
                practice = dict(row)
                # Parse JSON fields
                practice['examples'] = json.loads(practice['examples'] or '[]')
                practice['counter_examples'] = json.loads(practice['counter_examples'] or '[]')
                practice['tools_required'] = json.loads(practice['tools_required'] or '[]')
                practice['tags'] = json.loads(practice['tags'] or '[]')
                if practice['metrics']:
                    practice['metrics'] = json.loads(practice['metrics'])
                practices.append(practice)
            
            return practices
    
    def search_patterns_and_practices(
        self,
        search_term: str,
        include_patterns: bool = True,
        include_practices: bool = True,
        limit: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search across both patterns and best practices."""
        results = {
            'patterns': [],
            'best_practices': []
        }
        
        if include_patterns:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM coding_patterns 
                    WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
                    ORDER BY confidence DESC 
                    LIMIT ?
                """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', limit))
                
                for row in cursor.fetchall():
                    pattern = dict(row)
                    pattern['benefits'] = json.loads(pattern['benefits'] or '[]')
                    pattern['trade_offs'] = json.loads(pattern['trade_offs'] or '[]')
                    pattern['tags'] = json.loads(pattern['tags'] or '[]')
                    results['patterns'].append(pattern)
        
        if include_practices:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM best_practices 
                    WHERE title LIKE ? OR description LIKE ? OR rationale LIKE ? OR tags LIKE ?
                    ORDER BY priority DESC, compliance_score DESC 
                    LIMIT ?
                """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', limit))
                
                for row in cursor.fetchall():
                    practice = dict(row)
                    practice['examples'] = json.loads(practice['examples'] or '[]')
                    practice['counter_examples'] = json.loads(practice['counter_examples'] or '[]')
                    practice['tools_required'] = json.loads(practice['tools_required'] or '[]')
                    practice['tags'] = json.loads(practice['tags'] or '[]')
                    if practice['metrics']:
                        practice['metrics'] = json.loads(practice['metrics'])
                    results['best_practices'].append(practice)
        
        return results
    
    def record_pattern_usage(
        self,
        pattern_id: str,
        node_id: Optional[int] = None,
        file_path: Optional[str] = None,
        usage_context: Optional[str] = None,
        effectiveness_score: Optional[float] = None,
        applied_by: str = "llm",
        notes: Optional[str] = None
    ):
        """Record when a pattern is applied to track effectiveness."""
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(str(self.db_path)) as conn:
            # Record usage
            conn.execute("""
                INSERT INTO pattern_usage (
                    pattern_id, node_id, file_path, usage_context,
                    applied_by, applied_at, effectiveness_score, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id, node_id, file_path, usage_context,
                applied_by, timestamp, effectiveness_score, notes
            ))
            
            # Update pattern usage frequency
            conn.execute("""
                UPDATE coding_patterns 
                SET usage_frequency = usage_frequency + 1, last_applied = ?
                WHERE pattern_id = ?
            """, (timestamp, pattern_id))
    
    def get_pattern_recommendations(
        self,
        node_id: int,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pattern recommendations for a specific code node."""
        # Get node information
        node_info = self.memory_storage.get_memories(node_id=node_id, limit=10)
        
        # Extract relevant tags and content for pattern matching
        relevant_tags = set()
        relevant_content = ""
        
        for memory in node_info:
            relevant_tags.update(memory.get('tags', []))
            relevant_content += " " + memory.get('content', '')
        
        # Find patterns that match the context
        patterns = self.get_patterns(limit=100)  # Get all patterns
        
        recommendations = []
        for pattern in patterns:
            score = 0
            
            # Score based on tag overlap
            pattern_tags = set(pattern.get('tags', []))
            tag_overlap = len(relevant_tags.intersection(pattern_tags))
            score += tag_overlap * 2
            
            # Score based on content relevance (simple keyword matching)
            pattern_keywords = pattern['title'].lower().split() + pattern['description'].lower().split()
            content_words = relevant_content.lower().split()
            keyword_matches = sum(1 for word in pattern_keywords if word in content_words)
            score += keyword_matches
            
            # Boost score for high-confidence patterns
            score *= pattern['confidence']
            
            if score > 0:
                pattern['recommendation_score'] = score
                recommendations.append(pattern)
        
        # Sort by recommendation score and return top recommendations
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return recommendations[:10]
    
    def get_project_standards_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of project standards and patterns."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get pattern statistics
            cursor.execute("""
                SELECT pattern_type, COUNT(*) as count, AVG(confidence) as avg_confidence
                FROM coding_patterns 
                GROUP BY pattern_type
            """)
            pattern_stats = {row['pattern_type']: {
                'count': row['count'], 
                'avg_confidence': row['avg_confidence']
            } for row in cursor.fetchall()}
            
            # Get best practice statistics
            cursor.execute("""
                SELECT category, COUNT(*) as count, AVG(compliance_score) as avg_compliance
                FROM best_practices 
                GROUP BY category
            """)
            practice_stats = {row['category']: {
                'count': row['count'], 
                'avg_compliance': row['avg_compliance']
            } for row in cursor.fetchall()}
            
            # Get high-priority practices
            cursor.execute("""
                SELECT title, category, enforcement_level 
                FROM best_practices 
                WHERE priority = 'high' 
                ORDER BY compliance_score DESC
            """)
            high_priority_practices = [dict(row) for row in cursor.fetchall()]
            
            # Get most used patterns
            cursor.execute("""
                SELECT title, pattern_type, usage_frequency 
                FROM coding_patterns 
                WHERE usage_frequency > 0 
                ORDER BY usage_frequency DESC 
                LIMIT 10
            """)
            popular_patterns = [dict(row) for row in cursor.fetchall()]
            
            return {
                'pattern_statistics': pattern_stats,
                'practice_statistics': practice_stats,
                'high_priority_practices': high_priority_practices,
                'popular_patterns': popular_patterns,
                'summary': {
                    'total_patterns': sum(stats['count'] for stats in pattern_stats.values()),
                    'total_practices': sum(stats['count'] for stats in practice_stats.values()),
                    'avg_pattern_confidence': sum(stats['avg_confidence'] for stats in pattern_stats.values()) / len(pattern_stats) if pattern_stats else 0,
                    'avg_practice_compliance': sum(stats['avg_compliance'] for stats in practice_stats.values()) / len(practice_stats) if practice_stats else 0
                }
            }