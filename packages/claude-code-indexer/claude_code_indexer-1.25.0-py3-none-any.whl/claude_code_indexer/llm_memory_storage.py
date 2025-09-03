#!/usr/bin/env python3
"""
LLM Memory Storage System
Allows LLMs (like Claude) to store and retrieve their own analysis, insights, and context
as metadata attached to code nodes.
"""

import json
import sqlite3
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from .logger import log_info, log_warning, log_error


@dataclass
class LLMMemory:
    """Structure for LLM memory entries"""
    node_id: int
    llm_name: str  # e.g., "claude-3", "gpt-4"
    memory_type: str  # "analysis", "insight", "context", "todo", "warning", etc.
    content: str  # The actual memory content
    metadata: Dict[str, Any]  # Additional structured data
    created_at: str
    updated_at: str
    session_id: Optional[str] = None  # Track which conversation/session
    relevance_score: float = 1.0  # How relevant this memory is (0.0-1.0)


class LLMMemoryStorage:
    """Manages LLM memory storage and retrieval"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Initialize LLM memory tables"""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Create llm_memories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id INTEGER NOT NULL,
                    llm_name TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,  -- JSON
                    session_id TEXT,
                    relevance_score REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (node_id) REFERENCES code_nodes(id),
                    UNIQUE(node_id, llm_name, memory_type, session_id)
                )
            """)
            
            # Create indexes for efficient queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_llm_memories_node_id 
                ON llm_memories(node_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_llm_memories_type 
                ON llm_memories(memory_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_llm_memories_session 
                ON llm_memories(session_id)
            """)
            
            # Create memory tags table for categorization
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_memory_tags (
                    memory_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (memory_id) REFERENCES llm_memories(id),
                    PRIMARY KEY (memory_id, tag)
                )
            """)
    
    def store_memory(
        self,
        node_id: int,
        llm_name: str,
        memory_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Store a memory entry for a code node
        
        Args:
            node_id: The code node this memory relates to
            llm_name: Name/version of the LLM (e.g., "claude-3-opus")
            memory_type: Type of memory (analysis, insight, context, todo, etc.)
            content: The actual memory content
            metadata: Additional structured data
            session_id: Optional session/conversation ID
            tags: Optional list of tags for categorization
            
        Returns:
            The memory entry ID
        """
        metadata = metadata or {}
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Check if memory already exists (update vs insert)
            cursor.execute("""
                SELECT id FROM llm_memories 
                WHERE node_id = ? AND llm_name = ? AND memory_type = ? 
                AND (session_id = ? OR (session_id IS NULL AND ? IS NULL))
            """, (node_id, llm_name, memory_type, session_id, session_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing memory
                memory_id = existing[0]
                cursor.execute("""
                    UPDATE llm_memories 
                    SET content = ?, metadata = ?, updated_at = ?
                    WHERE id = ?
                """, (content, json.dumps(metadata), timestamp, memory_id))
                
                # Clear old tags
                cursor.execute("DELETE FROM llm_memory_tags WHERE memory_id = ?", (memory_id,))
            else:
                # Insert new memory
                cursor.execute("""
                    INSERT INTO llm_memories 
                    (node_id, llm_name, memory_type, content, metadata, session_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    node_id, llm_name, memory_type, content,
                    json.dumps(metadata), session_id, timestamp, timestamp
                ))
                memory_id = cursor.lastrowid
            
            # Add tags if provided
            if tags:
                for tag in tags:
                    cursor.execute("""
                        INSERT OR IGNORE INTO llm_memory_tags (memory_id, tag)
                        VALUES (?, ?)
                    """, (memory_id, tag))
            
            conn.commit()
            return memory_id
    
    def get_memories(
        self,
        node_id: Optional[int] = None,
        memory_type: Optional[str] = None,
        llm_name: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories based on filters
        
        Args:
            node_id: Filter by specific node
            memory_type: Filter by memory type
            llm_name: Filter by LLM name
            session_id: Filter by session
            tags: Filter by tags (any match)
            limit: Maximum number of results
            
        Returns:
            List of memory entries
        """
        query = """
            SELECT DISTINCT m.*, n.name as node_name, n.node_type, n.path as file_path
            FROM llm_memories m
            JOIN code_nodes n ON m.node_id = n.id
        """
        
        conditions = []
        params = []
        
        if tags:
            query += " JOIN llm_memory_tags t ON m.id = t.memory_id"
            tag_conditions = " OR ".join(["t.tag = ?" for _ in tags])
            conditions.append(f"({tag_conditions})")
            params.extend(tags)
        
        if node_id is not None:
            conditions.append("m.node_id = ?")
            params.append(node_id)
        
        if memory_type:
            conditions.append("m.memory_type = ?")
            params.append(memory_type)
        
        if llm_name:
            conditions.append("m.llm_name = ?")
            params.append(llm_name)
        
        if session_id:
            conditions.append("m.session_id = ?")
            params.append(session_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY m.updated_at DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                memory = dict(row)
                # Parse JSON metadata
                if memory['metadata']:
                    memory['metadata'] = json.loads(memory['metadata'])
                else:
                    memory['metadata'] = {}
                
                # Get tags for this memory
                cursor.execute("""
                    SELECT tag FROM llm_memory_tags WHERE memory_id = ?
                """, (memory['id'],))
                memory['tags'] = [r[0] for r in cursor.fetchall()]
                
                results.append(memory)
            
            return results
    
    def get_node_summary(self, node_id: int) -> Dict[str, Any]:
        """
        Get a summary of all memories for a specific node
        
        Args:
            node_id: The node to summarize
            
        Returns:
            Summary with memories grouped by type
        """
        memories = self.get_memories(node_id=node_id)
        
        summary = {
            'node_id': node_id,
            'total_memories': len(memories),
            'by_type': {},
            'by_llm': {},
            'latest_update': None,
            'tags': set()
        }
        
        for memory in memories:
            # Group by type
            mem_type = memory['memory_type']
            if mem_type not in summary['by_type']:
                summary['by_type'][mem_type] = []
            summary['by_type'][mem_type].append(memory)
            
            # Group by LLM
            llm = memory['llm_name']
            if llm not in summary['by_llm']:
                summary['by_llm'][llm] = []
            summary['by_llm'][llm].append(memory)
            
            # Collect tags
            summary['tags'].update(memory.get('tags', []))
            
            # Track latest update
            if not summary['latest_update'] or memory['updated_at'] > summary['latest_update']:
                summary['latest_update'] = memory['updated_at']
        
        summary['tags'] = list(summary['tags'])
        return summary
    
    def search_memories(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search memories by content
        
        Args:
            search_term: Term to search for in memory content
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        query = """
            SELECT m.*, n.name as node_name, n.node_type, n.path as file_path
            FROM llm_memories m
            JOIN code_nodes n ON m.node_id = n.id
            WHERE m.content LIKE ?
            ORDER BY m.updated_at DESC
            LIMIT ?
        """
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (f'%{search_term}%', limit))
            
            results = []
            for row in cursor.fetchall():
                memory = dict(row)
                if memory['metadata']:
                    memory['metadata'] = json.loads(memory['metadata'])
                results.append(memory)
            
            return results
    
    def get_related_memories(self, node_id: int, relationship_types: List[str]) -> List[Dict[str, Any]]:
        """
        Get memories for nodes related to the given node
        
        Args:
            node_id: The source node
            relationship_types: Types of relationships to follow
            
        Returns:
            Memories from related nodes
        """
        # First get related node IDs
        placeholders = ','.join(['?' for _ in relationship_types])
        query = f"""
            SELECT DISTINCT target_node_id as related_id
            FROM edges 
            WHERE source_node_id = ? AND edge_type IN ({placeholders})
            UNION
            SELECT DISTINCT source_node_id as related_id
            FROM edges
            WHERE target_node_id = ? AND edge_type IN ({placeholders})
        """
        
        params = [node_id] + relationship_types + [node_id] + relationship_types
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            related_ids = [row[0] for row in cursor.fetchall()]
            
            if not related_ids:
                return []
            
            # Get memories for related nodes
            results = []
            for related_id in related_ids:
                memories = self.get_memories(node_id=related_id)
                for memory in memories:
                    memory['related_from_node_id'] = node_id
                    results.append(memory)
            
            return results
    
    def cleanup_old_memories(self, days_old: int = 30, keep_important: bool = True):
        """
        Clean up old memories
        
        Args:
            days_old: Remove memories older than this many days
            keep_important: Keep memories marked as important in metadata
        """
        cutoff_date = datetime.utcnow().timestamp() - (days_old * 24 * 3600)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            if keep_important:
                # Keep memories marked as important
                conn.execute("""
                    DELETE FROM llm_memories 
                    WHERE updated_at < ? 
                    AND (metadata IS NULL OR json_extract(metadata, '$.important') != true)
                """, (cutoff_date,))
            else:
                conn.execute("""
                    DELETE FROM llm_memories 
                    WHERE updated_at < ?
                """, (cutoff_date,))
            
            deleted = conn.total_changes
            conn.commit()
            
            if deleted > 0:
                log_info(f"Cleaned up {deleted} old memory entries")