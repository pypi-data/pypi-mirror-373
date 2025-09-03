#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Claude Code Indexer
Provides code indexing capabilities directly to Claude Desktop
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

# Set MCP server mode for proper logging
os.environ['MCP_SERVER_MODE'] = '1'

# MCP SDK imports
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)

from .indexer import CodeGraphIndexer
from .cache_manager import CacheManager
from .parallel_processor import ParallelFileProcessor
from .storage_manager import get_storage_manager
from .llm_memory_storage import LLMMemoryStorage
from .pattern_memory_manager import PatternMemoryManager, PatternType, BestPracticeCategory
# Feedback and error tracking modules removed during cleanup
# from .feedback_tool import get_feedback_client, FeedbackType, FeedbackPriority
# from .error_tracker import get_error_tracker, auto_track_errors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create the MCP server
mcp = FastMCP("claude-code-indexer")

# Dictionary to store tool functions for fallback mode
TOOLS = {}

# Wrapper for mcp.tool that also registers for fallback
original_tool = mcp.tool

def tool(*args, **kwargs):
    """Enhanced tool decorator that registers for fallback mode"""
    def decorator(func):
        # Register with MCP
        mcp_decorated = original_tool(*args, **kwargs)(func)
        # Register for fallback
        TOOLS[func.__name__] = func
        return mcp_decorated
    return decorator

# Replace mcp.tool with our enhanced version
mcp.tool = tool

# Project management for MCP server using centralized storage
class ProjectManager:
    """Manages project-specific databases and caches using centralized storage"""
    
    def __init__(self):
        self.storage = get_storage_manager()
        self.indexers = {}  # Cache indexers per project
    
    def get_indexer(self, project_path: str, **kwargs) -> CodeGraphIndexer:
        """Get or create indexer for a project"""
        project_path_obj = Path(project_path).resolve()
        path_str = str(project_path_obj)
        
        if path_str not in self.indexers:
            self.indexers[path_str] = CodeGraphIndexer(
                project_path=project_path_obj,
                use_cache=True,
                parallel_workers=kwargs.get('workers', 4),
                enable_optimizations=True
            )
        
        return self.indexers[path_str]

# Global project manager
project_manager = ProjectManager()
    
@mcp.tool()
def index_codebase(project_path: Optional[str] = None, path: Optional[str] = None,
                  workers: int = 4, force: bool = False, 
                  custom_ignore: Optional[List[str]] = None) -> str:
    """Index Python codebase with graph analysis.
    
    Args:
        project_path: Project directory path to index (preferred)
        path: Alternative parameter name for project_path (backward compatibility)
        workers: Number of parallel workers (default: 4)
        force: Force re-index all files (default: False)
        custom_ignore: Additional ignore patterns beyond .gitignore (optional)
    
    Returns:
        Summary of indexing results
    """
    # Handle both parameter names for backward compatibility
    if project_path is None and path is not None:
        project_path = path
    elif project_path is None and path is None:
        return "❌ Error: Either 'project_path' or 'path' parameter is required"
    
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    if not os.path.isdir(project_path):
        return f"❌ Project path is not a directory: {project_path}"
    
    # Get project-specific indexer
    indexer = project_manager.get_indexer(project_path, workers=workers)
    project_dir = project_manager.storage.get_project_dir(Path(project_path))
    
    # Run indexing
    start_time = datetime.now()
    try:
        indexer.index_directory(project_path, force_reindex=force, custom_ignore=custom_ignore)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        stats = indexer.get_stats()
        return f"""✅ Indexing Complete!
📂 Project: {project_path}
📁 Total files: {stats.get('total_files', 0)}
🔗 Total nodes: {stats.get('total_nodes', 0)}
↔️ Total edges: {stats.get('total_edges', 0)}
⏱️ Time: {elapsed:.2f}s
🚀 Speed: {stats.get('total_files', 0) / elapsed:.1f} files/sec
💾 Database: {project_dir / 'code_index.db'}"""
    except Exception as e:
        return f"❌ Indexing failed: {str(e)}"
    
@mcp.tool()
def get_project_stats(project_path: str) -> str:
    """Get code indexing statistics and project overview.
    
    Args:
        project_path: Project directory path (required)
    
    Returns:
        Formatted statistics about the indexed codebase
    """
    # Validate project path - use Path.resolve() for consistency with storage_manager
    project_path = Path(os.path.expanduser(project_path)).resolve()
    project_dir = project_manager.storage.get_project_dir(project_path)
    db_path = project_dir / "code_index.db"
    
    if not db_path.exists():
        return f"❌ No indexed data found for project: {project_path}\nRun index_codebase first."
    
    indexer = project_manager.get_indexer(project_path)
    cache_manager = CacheManager(project_path=Path(project_path))
    
    stats = indexer.get_stats()
    cache_stats = cache_manager.get_cache_stats()
    
    # Handle different cache stats structures
    if isinstance(cache_stats, dict) and 'disk' in cache_stats:
        # New hybrid cache structure
        total_entries = cache_stats['disk']['total_entries']
        recent_entries = cache_stats['disk']['recent_entries']
        cache_db_size = cache_stats['disk']['cache_db_size']
    else:
        # Old flat structure
        total_entries = cache_stats.get('total_entries', 0)
        recent_entries = cache_stats.get('recent_entries', 0)
        cache_db_size = cache_stats.get('cache_db_size', 0)
    
    return f"""📊 Code Indexing Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Project: {project_path}
📅 Last indexed: {stats.get('last_indexed', 'Never')}
📁 Total files: {stats.get('total_files', 0)}
🔗 Total nodes: {stats.get('total_nodes', 0)}
↔️ Total edges: {stats.get('total_edges', 0)}

📋 Node Types:
{_format_node_types(stats.get('node_types', {}))}

🔗 Relationships:
{_format_relationships(stats.get('relationship_types', {}))}

💾 Cache Statistics:
• Total entries: {total_entries}
• Recent (24h): {recent_entries}
• Cache size: {cache_db_size / 1024:.1f} KB"""
    
@mcp.tool()
def query_important_code(project_path: str, limit: int = 20, node_type: Optional[str] = None) -> str:
    """Get most important code entities (classes, functions).
    
    Args:
        project_path: Project directory path (required)
        limit: Number of results to return (default: 20)
        node_type: Filter by type - 'class', 'function', 'method', 'file', or 'import'
    
    Returns:
        List of most important code entities with scores and tags
    """
    # Validate project path - use Path.resolve() for consistency with storage_manager
    project_path = Path(os.path.expanduser(project_path)).resolve()
    project_dir = project_manager.storage.get_project_dir(project_path)
    db_path = project_dir / "code_index.db"
    
    if not db_path.exists():
        return f"❌ No indexed data found for project: {project_path}\nRun index_codebase first."
    
    indexer = project_manager.get_indexer(project_path)
    
    # Get all nodes
    all_nodes = indexer.query_important_nodes(min_score=0.0, limit=1000)
    
    # Filter by type if specified
    if node_type:
        all_nodes = [n for n in all_nodes if n['node_type'] == node_type]
    
    # Sort by importance with type priority
    def sort_key(node):
        type_priority = {
            'class': 1000,
            'function': 100,
            'method': 10,
            'file': 1,
            'import': 0
        }.get(node['node_type'], 0)
        return node['importance_score'] + type_priority
    
    nodes = sorted(all_nodes, key=sort_key, reverse=True)[:limit]
    
    if not nodes:
        return "No entities found matching criteria."
    
    # Format results
    result = "🔍 Most important code entities:\n\n"
    for i, node in enumerate(nodes, 1):
        tags = ", ".join(node['relevance_tags']) if node['relevance_tags'] else "-"
        result += f"{i}. **{node['name']}** ({node['node_type']})\n"
        result += f"   📊 Score: {node['importance_score']:.3f}\n"
        result += f"   🏷️ Tags: {tags}\n"
        result += f"   📁 Path: {node['path']}\n\n"
    
    return result
    
@mcp.tool()
def search_code(project_path: str, terms: str, limit: int = 10, mode: str = "any", use_fts: bool = True) -> str:
    """Search for code entities by name or pattern. Supports multiple keywords.
    
    Args:
        project_path: Project directory path (required)
        terms: Search terms separated by spaces (e.g., "auth user login")
        limit: Number of results to return (default: 10)
        mode: Search mode - 'any' (OR logic) or 'all' (AND logic) (default: 'any')
        use_fts: Use FTS5 full-text search if available (default: True)
    
    Returns:
        Search results with matching code entities
    
    Examples:
        search_code("/path/to/project", "auth")  # Single keyword
        search_code("/path/to/project", "auth user", mode="any")  # Match ANY keyword
        search_code("/path/to/project", "database connection", mode="all")  # Match ALL keywords
    """
    # Validate project path - use Path.resolve() for consistency with storage_manager
    project_path = Path(os.path.expanduser(project_path)).resolve()
    project_dir = project_manager.storage.get_project_dir(project_path)
    db_path = str(project_dir / "code_index.db")
    
    if not os.path.exists(db_path):
        return f"❌ No indexed data found for project: {project_path}\nRun index_codebase first."
    
    indexer = project_manager.get_indexer(str(project_path))
    
    # Parse multiple keywords
    keywords = terms.strip().split()
    if not keywords:
        return "❌ No search terms provided"
    
    # Validate keywords to prevent SQL injection
    for keyword in keywords:
        # Check for SQL injection patterns
        if any(dangerous in keyword.upper() for dangerous in ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE', '--', ';', '/*', '*/']):
            return f"❌ Invalid search term detected: '{keyword}'. Please use alphanumeric characters only."
        # Limit keyword length to prevent buffer overflow attacks
        if len(keyword) > 100:
            return f"❌ Search term too long: '{keyword}'. Maximum 100 characters per term."
    
    # Check cache first
    cache_key = f"search:{project_path}:{terms}:{mode}:{limit}:{use_fts}"
    if hasattr(indexer, 'cache_manager') and indexer.cache_manager.memory_cache:
        cached_result = indexer.cache_manager.memory_cache.get(cache_key)
        if cached_result and isinstance(cached_result, str):
            return cached_result + "\n(from cache)"
    
    # Search in database
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if FTS5 table exists
    has_fts = False
    if use_fts:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='code_nodes_fts'")
        has_fts = cursor.fetchone() is not None
    
    # Build query based on FTS5 availability and mode
    if has_fts and use_fts:
        # Escape special characters for FTS5
        def escape_fts_term(term):
            """Escape special characters in FTS5 search terms"""
            # Escape double quotes and special FTS5 operators
            term = term.replace('"', '""')
            # Wrap in quotes to treat as literal if it contains special chars
            if any(c in term for c in ['OR', 'AND', 'NOT', '-', '+', '*', '(', ')', ':']):
                return f'"{term}"'
            return f'"{term}"'  # Always quote for safety
        
        # Use FTS5 for faster search
        escaped_keywords = [escape_fts_term(k) for k in keywords]
        if mode == 'any':
            # OR logic - match any keyword
            fts_query = " OR ".join(escaped_keywords)
        else:
            # AND logic - must match all keywords
            fts_query = " AND ".join(escaped_keywords)
        
        query = """
            SELECT cn.* FROM code_nodes cn
            JOIN code_nodes_fts fts ON cn.id = fts.rowid
            WHERE code_nodes_fts MATCH ?
            ORDER BY cn.importance_score DESC
            LIMIT ?
        """
        params = [fts_query, limit]
    else:
        # Fallback to LIKE queries
        if mode == 'any':
            # OR logic - match any keyword
            conditions = []
            params = []
            for keyword in keywords:
                conditions.append("(name LIKE ? OR path LIKE ? OR summary LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
            where_clause = " OR ".join(conditions)
        else:
            # AND logic - must match all keywords
            conditions = []
            params = []
            for keyword in keywords:
                conditions.append("(name LIKE ? OR path LIKE ? OR summary LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
            where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT * FROM code_nodes 
            WHERE {where_clause}
            ORDER BY importance_score DESC
            LIMIT ?
        """
        params.append(limit)
    
    cursor.execute(query, params)
    
    columns = [desc[0] for desc in cursor.description]
    results = []
    for row in cursor.fetchall():
        node = dict(zip(columns, row))
        if node.get('relevance_tags'):
            node['relevance_tags'] = json.loads(node['relevance_tags'])
        results.append(node)
    
    conn.close()
    
    if not results:
        return f"No results found for '{terms}' (mode: {mode})"
    
    # Format results
    output = f"🔍 Search results for '{terms}' (mode: {mode})"
    if has_fts and use_fts:
        output += " [FTS5]"
    output += ":\n\n"
    
    for i, node in enumerate(results, 1):
        output += f"{i}. **{node['name']}** ({node['node_type']})\n"
        output += f"   📊 Score: {node['importance_score']:.3f}\n"
        output += f"   📁 Path: {node['path']}\n\n"
    
    # Cache the result
    if hasattr(indexer, 'cache_manager') and indexer.cache_manager.memory_cache:
        indexer.cache_manager.memory_cache.put(cache_key, output, entity_type="search")
    
    return output
    
@mcp.tool()
def list_indexed_projects(limit: int = 20, include_stats: bool = True) -> str:
    """List all indexed projects with optional limiting and stats.
    
    Args:
        limit: Maximum number of projects to return (default: 20)
        include_stats: Whether to include detailed stats (default: True) 
    
    Returns:
        List of indexed projects with their stats
    """
    storage = get_storage_manager()
    projects = storage.list_projects()
    
    if not projects:
        return "📂 No indexed projects found."
    
    # Limit number of projects to prevent response size issues
    limited_projects = projects[:limit]
    total_projects = len(projects)
    
    output = f"📚 **Indexed Projects** ({len(limited_projects)}"
    if total_projects > limit:
        output += f" of {total_projects}, use limit parameter for more"
    output += ")\n\n"
    
    for project in limited_projects:
        output += f"📁 **{project['name']}**\n"
        output += f"   Path: {project['path']}\n"
        output += f"   Status: {'✓ Exists' if project.get('exists', True) else '✗ Missing'}\n"
        
        if include_stats:
            if project.get('last_indexed'):
                output += f"   Last indexed: {project['last_indexed']}\n"
            
            if project.get('stats'):
                stats = project['stats']
                output += f"   Nodes: {stats.get('nodes', 0)}\n"
                output += f"   Files: {stats.get('files', 0)}\n"
            
            if project.get('db_size', 0) > 0:
                size_mb = project['db_size'] / 1024 / 1024
                output += f"   Size: {size_mb:.1f} MB\n"
        
        output += "\n"
    
    # Add storage stats (summary only to keep response manageable)
    if include_stats:
        storage_stats = storage.get_storage_stats()
        output += f"💾 **Storage Summary**:\n"
        output += f"   Total projects: {storage_stats['project_count']}\n"
        output += f"   Total size: {storage_stats['total_size_mb']:.1f} MB\n"
    
    return output
    
@mcp.tool()
def manage_cache(project_path: str, action: str, days: int = 30) -> str:
    """Manage code indexing cache.
    
    Args:
        project_path: Project directory path (required)
        action: Cache action - 'stats' to view statistics or 'clear' to clear old entries
        days: Days threshold for clearing cache (default: 30, only used with 'clear' action)
    
    Returns:
        Cache statistics or confirmation of cache clearing
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    project_path_obj = Path(project_path)
    cache_manager = CacheManager(project_path=project_path_obj)
    if action == "stats":
        stats = cache_manager.get_cache_stats()
        return f"""💾 Cache Statistics:
• Total entries: {stats['total_entries']}
• Recent (24h): {stats['recent_entries']}
• Total file size: {stats['total_file_size'] / 1024 / 1024:.1f} MB
• Cache DB size: {stats['cache_db_size'] / 1024:.1f} KB
• Location: {stats['cache_dir']}
• Project: {project_path}"""
    
    elif action == "clear":
        cache_manager.clear_cache(older_than_days=days)
        return f"✅ Cleared cache entries older than {days} days"
    
    return "❌ Unknown cache action. Use 'stats' or 'clear'"
    
@mcp.tool()
def get_ignore_patterns(project_path: str) -> str:
    """Get active ignore patterns for a project.
    
    Args:
        project_path: Project directory path (required)
    
    Returns:
        List of active ignore patterns
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    # Create ignore handler to get patterns
    from .ignore_handler import IgnoreHandler
    ignore_handler = IgnoreHandler(project_path)
    patterns = ignore_handler.get_patterns()
    
    # Check for .gitignore
    gitignore_exists = (Path(project_path) / '.gitignore').exists()
    dockerignore_exists = (Path(project_path) / '.dockerignore').exists()
    
    output = f"📝 Ignore Patterns for: {project_path}\n\n"
    
    if gitignore_exists:
        output += "✅ Using .gitignore\n"
    if dockerignore_exists:
        output += "✅ Using .dockerignore\n"
    
    output += f"\n📋 Total patterns: {len(patterns)}\n\n"
    output += "🚫 Ignored patterns:\n"
    
    # Group patterns by category
    categories = {
        'Dependencies': ['node_modules/', 'vendor/', 'packages/', 'bower_components/'],
        'Python': ['__pycache__/', '*.pyc', 'venv/', '.env/', 'env/'],
        'Build': ['build/', 'dist/', 'target/', '*.egg-info/'],
        'Version Control': ['.git/', '.svn/', '.hg/'],
        'IDE': ['.idea/', '.vscode/', '*.swp'],
        'Other': []
    }
    
    categorized = {cat: [] for cat in categories}
    
    for pattern in patterns:
        found = False
        for cat, cat_patterns in categories.items():
            if cat == 'Other':
                continue
            for cp in cat_patterns:
                if pattern == cp or pattern.startswith(cp.rstrip('/')):
                    categorized[cat].append(pattern)
                    found = True
                    break
            if found:
                break
        if not found:
            categorized['Other'].append(pattern)
    
    # Display by category
    for cat, items in categorized.items():
        if items:
            output += f"\n**{cat}:**\n"
            for item in sorted(items)[:10]:  # Show max 10 per category
                output += f"  • {item}\n"
            if len(items) > 10:
                output += f"  • ... and {len(items) - 10} more\n"
    
    return output
    
# Helper functions
def _format_node_types(node_types: Dict[str, int]) -> str:
    """Format node types for display"""
    if not node_types:
        return "• No data"
    
    lines = []
    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"• {node_type}: {count}")
    return "\n".join(lines)


def _format_relationships(rel_types: Dict[str, int]) -> str:
    """Format relationship types for display"""
    if not rel_types:
        return "• No data"
    
    lines = []
    for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"• {rel_type}: {count}")
    return "\n".join(lines)


# LLM Metadata Enhancement Tools

@mcp.tool()
def enhance_metadata(project_path: str, limit: Optional[int] = None, force_refresh: bool = False) -> str:
    """Enhance codebase metadata using LLM analysis.
    
    Args:
        project_path: Project directory path (required)
        limit: Maximum number of nodes to analyze (optional)
        force_refresh: Force re-analysis even if cached (default: False)
    
    Returns:
        Analysis summary with enhanced metadata statistics
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        
        # Perform LLM enhancement
        result = indexer.enhance_metadata(limit=limit, force_refresh=force_refresh)
        
        output = f"🤖 LLM Metadata Enhancement Complete\n\n"
        output += f"📊 Analysis Summary:\n"
        output += f"• Analyzed nodes: {result.get('analyzed_count', 0)}\n"
        output += f"• Total nodes: {result.get('total_nodes', 0)}\n"
        output += f"• Duration: {result.get('analysis_duration', 'N/A')}\n"
        output += f"• Speed: {result.get('nodes_per_second', 'N/A')} nodes/sec\n\n"
        
        # Architectural layers
        layers = result.get('architectural_layers', {})
        if layers:
            output += f"🏗️ Architectural Layers:\n"
            for layer, count in sorted(layers.items(), key=lambda x: x[1], reverse=True):
                output += f"• {layer}: {count} components\n"
            output += "\n"
        
        # Criticality distribution
        criticality = result.get('criticality_distribution', {})
        if criticality:
            output += f"⚠️ Criticality Distribution:\n"
            for level, count in sorted(criticality.items(), key=lambda x: x[1], reverse=True):
                output += f"• {level}: {count} components\n"
            output += "\n"
        
        # Business domains
        domains = result.get('business_domains', {})
        if domains:
            output += f"🏢 Business Domains:\n"
            for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
                output += f"• {domain}: {count} components\n"
            output += "\n"
        
        # Average scores
        avg_scores = result.get('average_scores', {})
        if avg_scores:
            output += f"📈 Average Scores:\n"
            output += f"• Complexity: {avg_scores.get('complexity', 0):.3f}\n"
            output += f"• Dependencies Impact: {avg_scores.get('dependencies_impact', 0):.3f}\n"
            output += f"• Testability: {avg_scores.get('testability', 0):.3f}\n"
            output += "\n"
        
        # Detected patterns
        patterns = result.get('detected_patterns', {})
        if patterns:
            output += f"🎨 Design Patterns Detected:\n"
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                output += f"• {pattern}: {count} instances\n"
        
        return output
        
    except Exception as e:
        return f"❌ Enhancement failed: {str(e)}"


@mcp.tool()
def query_enhanced_nodes(project_path: str, 
                        architectural_layer: Optional[str] = None,
                        business_domain: Optional[str] = None,
                        criticality_level: Optional[str] = None,
                        min_complexity: Optional[float] = None,
                        limit: int = 20) -> str:
    """Query nodes with enhanced metadata and filters.
    
    Args:
        project_path: Project directory path (required)
        architectural_layer: Filter by layer (controller, service, model, etc.)
        business_domain: Filter by domain (authentication, payment, etc.)
        criticality_level: Filter by criticality (critical, important, normal, low)
        min_complexity: Filter by minimum complexity score (0.0-1.0)
        limit: Maximum number of results (default: 20)
    
    Returns:
        List of enhanced nodes with metadata
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        
        nodes = indexer.query_enhanced_nodes(
            architectural_layer=architectural_layer,
            business_domain=business_domain,
            criticality_level=criticality_level,
            min_complexity=min_complexity,
            limit=limit
        )
        
        if not nodes:
            return "ℹ️ No enhanced nodes found matching the criteria"
        
        output = f"🔍 Enhanced Nodes Query Results\n\n"
        
        # Add filter info
        filters = []
        if architectural_layer:
            filters.append(f"Layer: {architectural_layer}")
        if business_domain:
            filters.append(f"Domain: {business_domain}")
        if criticality_level:
            filters.append(f"Criticality: {criticality_level}")
        if min_complexity:
            filters.append(f"Min Complexity: {min_complexity}")
        
        if filters:
            output += f"🎯 Filters: {', '.join(filters)}\n"
        
        output += f"📊 Found {len(nodes)} nodes (limit: {limit})\n\n"
        
        for i, node in enumerate(nodes, 1):
            output += f"{i}. **{node['name']}** ({node['node_type']})\n"
            output += f"   📁 Path: {node['path']}\n"
            output += f"   🏗️ Layer: {node.get('architectural_layer', 'unknown')}\n"
            output += f"   🏢 Domain: {node.get('business_domain', 'general')}\n"
            output += f"   ⚠️ Criticality: {node.get('criticality_level', 'normal')}\n"
            output += f"   📊 Complexity: {node.get('complexity_score', 0):.3f}\n"
            output += f"   🎯 Importance: {node.get('importance_score', 0):.3f}\n"
            
            # Role tags
            role_tags = node.get('role_tags', [])
            if role_tags:
                output += f"   🏷️ Tags: {', '.join(role_tags)}\n"
            
            # LLM summary
            summary = node.get('llm_summary', '')
            if summary:
                output += f"   📝 Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}\n"
            
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Query failed: {str(e)}"


@mcp.tool()
def get_codebase_insights(project_path: str) -> str:
    """Get comprehensive codebase insights and health assessment.
    
    Args:
        project_path: Project directory path (required)
    
    Returns:
        Detailed insights about codebase health, architecture, and recommendations
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        
        # Check if enhanced metadata is available
        try:
            insights = indexer.get_analysis_insights()
        except Exception as e:
            if "architectural_layer" in str(e):
                return f"❌ Enhanced metadata not available for project: {project_path}\nRun 'enhance_metadata' first to enable insights analysis."
            else:
                raise e
        
        output = f"📊 Codebase Insights for: {project_path}\n\n"
        
        # Codebase health
        health = insights.get('codebase_health', {})
        if health:
            output += f"🏥 Codebase Health:\n"
            output += f"• Overall Score: {health.get('overall_score', 0):.3f}/1.0\n"
            output += f"• Complexity Health: {health.get('complexity_health', 'unknown')}\n"
            output += f"• Testability Health: {health.get('testability_health', 'unknown')}\n"
            
            recommendations = health.get('recommendations', [])
            if recommendations:
                output += f"• Recommendations:\n"
                for rec in recommendations:
                    output += f"  - {rec}\n"
            output += "\n"
        
        # Architectural overview
        arch = insights.get('architectural_overview', {})
        if arch:
            output += f"🏗️ Architecture Overview:\n"
            
            layer_dist = arch.get('layer_distribution', {})
            if layer_dist:
                output += f"• Layer Distribution:\n"
                for layer, count in sorted(layer_dist.items(), key=lambda x: x[1], reverse=True):
                    output += f"  - {layer}: {count} components\n"
            
            domain_dist = arch.get('domain_distribution', {})
            if domain_dist:
                output += f"• Domain Distribution:\n"
                for domain, count in sorted(domain_dist.items(), key=lambda x: x[1], reverse=True):
                    output += f"  - {domain}: {count} components\n"
            
            layer_balance = arch.get('layer_balance', 'unknown')
            domain_focus = arch.get('domain_focus', 'unknown')
            output += f"• Layer Balance: {layer_balance}\n"
            output += f"• Primary Domain: {domain_focus}\n\n"
        
        # Complexity hotspots
        hotspots = insights.get('complexity_hotspots', [])
        if hotspots:
            output += f"🔥 Complexity Hotspots:\n"
            for i, hotspot in enumerate(hotspots[:5], 1):  # Top 5
                output += f"{i}. {hotspot['name']} ({hotspot['layer']})\n"
                output += f"   📁 {hotspot['path']}\n"
                output += f"   📊 Complexity: {hotspot['complexity']:.3f}\n\n"
        
        # Improvement suggestions
        suggestions = insights.get('improvement_suggestions', [])
        if suggestions:
            output += f"💡 Improvement Suggestions:\n"
            for i, suggestion in enumerate(suggestions, 1):
                output += f"{i}. {suggestion}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Insights generation failed: {str(e)}"


@mcp.tool()
def get_critical_components(project_path: str, limit: int = 15) -> str:
    """Get most critical components in the codebase.
    
    Args:
        project_path: Project directory path (required)
        limit: Maximum number of components to return (default: 15)
    
    Returns:
        List of critical components with metadata
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        critical_components = indexer.get_critical_components(limit=limit)
        
        if not critical_components:
            return "ℹ️ No critical components found. Run 'enhance_metadata' first."
        
        output = f"🎯 Top {len(critical_components)} Critical Components\n\n"
        
        for i, comp in enumerate(critical_components, 1):
            output += f"{i}. **{comp['name']}** ({comp['node_type']})\n"
            output += f"   📁 Path: {comp['path']}\n"
            output += f"   🏗️ Layer: {comp.get('architectural_layer', 'unknown')}\n"
            output += f"   🏢 Domain: {comp.get('business_domain', 'general')}\n"
            output += f"   📊 Complexity: {comp.get('complexity_score', 0):.3f}\n"
            output += f"   🎯 Importance: {comp.get('importance_score', 0):.3f}\n"
            output += f"   💥 Impact: {comp.get('dependencies_impact', 0):.3f}\n"
            
            # LLM summary
            summary = comp.get('llm_summary', '')
            if summary:
                output += f"   📝 Summary: {summary[:80]}{'...' if len(summary) > 80 else ''}\n"
            
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Critical components query failed: {str(e)}"


@mcp.tool()
def update_node_metadata(project_path: str, node_id: int, updates: Dict[str, Any]) -> str:
    """Update enhanced metadata for a specific node.
    
    Args:
        project_path: Project directory path (required)
        node_id: ID of the node to update
        updates: Dictionary of field updates (role_tags, complexity_score, etc.)
    
    Returns:
        Success/failure message
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        
        # Convert string JSON to dict if needed
        if isinstance(updates, str):
            updates = json.loads(updates)
        
        success = indexer.update_node_metadata(node_id, updates)
        
        if success:
            output = f"✅ Successfully updated metadata for node {node_id}\n\n"
            output += f"📝 Updates applied:\n"
            for field, value in updates.items():
                output += f"• {field}: {value}\n"
            return output
        else:
            return f"❌ Failed to update metadata for node {node_id}"
        
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON in updates: {str(e)}"
    except Exception as e:
        return f"❌ Update failed: {str(e)}"


@mcp.tool()
def store_llm_memory(
    project_path: str,
    node_id: int,
    memory_type: str,
    content: str,
    llm_name: str = "claude",
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None
) -> str:
    """Store LLM analysis/insights as memory attached to a code node.
    
    This allows LLMs like Claude to build up contextual understanding over time
    by storing their analysis, insights, TODOs, warnings, etc.
    
    Args:
        project_path: Project directory path (required)
        node_id: ID of the code node this memory relates to
        memory_type: Type of memory - "analysis", "insight", "context", "todo", "warning", "explanation"
        content: The actual memory content to store
        llm_name: Name/version of the LLM (default: "claude")
        metadata: Optional structured metadata as JSON dict
        tags: Optional list of tags for categorization
    
    Returns:
        Success message with memory ID
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        memory_storage = LLMMemoryStorage(indexer.db_path)
        
        # Handle metadata conversion
        if metadata and isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        # Store the memory
        memory_id = memory_storage.store_memory(
            node_id=node_id,
            llm_name=llm_name,
            memory_type=memory_type,
            content=content,
            metadata=metadata,
            tags=tags
        )
        
        return f"✅ Memory stored successfully (ID: {memory_id})\n\n📝 Type: {memory_type}\n🤖 LLM: {llm_name}\n🏷️ Tags: {', '.join(tags or [])}"
        
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON in metadata: {str(e)}"
    except Exception as e:
        return f"❌ Failed to store memory: {str(e)}"


@mcp.tool()
def get_llm_memories(
    project_path: str,
    node_id: Optional[int] = None,
    memory_type: Optional[str] = None,
    limit: int = 50
) -> str:
    """Retrieve LLM memories for code understanding.
    
    Args:
        project_path: Project directory path (required)
        node_id: Filter by specific node ID (optional)
        memory_type: Filter by type - "analysis", "insight", "context", "todo", "warning", etc. (optional)
        limit: Maximum number of memories to return (default: 50)
    
    Returns:
        Formatted list of memories with context
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        memory_storage = LLMMemoryStorage(indexer.db_path)
        
        # Retrieve memories
        memories = memory_storage.get_memories(
            node_id=node_id,
            memory_type=memory_type,
            limit=limit
        )
        
        if not memories:
            return "ℹ️ No memories found matching the criteria."
        
        output = f"🧠 Found {len(memories)} LLM Memories\n\n"
        
        # Group by node for better readability
        by_node = {}
        for memory in memories:
            nid = memory['node_id']
            if nid not in by_node:
                by_node[nid] = {
                    'node_name': memory['node_name'],
                    'node_type': memory['node_type'],
                    'file_path': memory['file_path'],
                    'memories': []
                }
            by_node[nid]['memories'].append(memory)
        
        for nid, node_data in by_node.items():
            output += f"📁 **{node_data['node_name']}** ({node_data['node_type']})\n"
            output += f"   Path: {node_data['file_path']}\n\n"
            
            for mem in node_data['memories']:
                output += f"   • [{mem['memory_type'].upper()}] by {mem['llm_name']}\n"
                output += f"     {mem['content']}\n"
                if mem.get('tags'):
                    output += f"     🏷️ Tags: {', '.join(mem['tags'])}\n"
                output += f"     ⏰ Updated: {mem['updated_at']}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Failed to retrieve memories: {str(e)}"


@mcp.tool()
def search_llm_memories(project_path: str, search_term: str, limit: int = 30) -> str:
    """Search through LLM memories by content.
    
    Args:
        project_path: Project directory path (required)
        search_term: Term to search for in memory content
        limit: Maximum results (default: 30)
    
    Returns:
        Matching memories with context
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        memory_storage = LLMMemoryStorage(indexer.db_path)
        
        # Search memories
        memories = memory_storage.search_memories(search_term, limit=limit)
        
        if not memories:
            return f"ℹ️ No memories found containing '{search_term}'."
        
        output = f"🔍 Found {len(memories)} memories containing '{search_term}'\n\n"
        
        for i, mem in enumerate(memories, 1):
            output += f"{i}. **{mem['node_name']}** - {mem['memory_type']}\n"
            output += f"   📁 {mem['file_path']}\n"
            
            # Highlight search term in content
            content = mem['content']
            if len(content) > 200:
                # Find position of search term and show context
                pos = content.lower().find(search_term.lower())
                if pos > -1:
                    start = max(0, pos - 50)
                    end = min(len(content), pos + len(search_term) + 50)
                    content = f"...{content[start:end]}..."
            
            output += f"   💭 {content}\n"
            output += f"   🤖 By: {mem['llm_name']} | ⏰ {mem['updated_at']}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Failed to search memories: {str(e)}"


@mcp.tool()
def get_node_memory_summary(project_path: str, node_id: int) -> str:
    """Get a comprehensive summary of all LLM memories for a specific node.
    
    Args:
        project_path: Project directory path (required)
        node_id: The node ID to get memory summary for
    
    Returns:
        Summary of all memories grouped by type and LLM
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        memory_storage = LLMMemoryStorage(indexer.db_path)
        
        # Get node info first
        node_info = indexer.get_node_info(node_id)
        if not node_info:
            return f"❌ Node {node_id} not found."
        
        # Get memory summary
        summary = memory_storage.get_node_summary(node_id)
        
        output = f"🧠 Memory Summary for **{node_info['name']}**\n"
        output += f"📁 Path: {node_info['file_path']}\n"
        output += f"📊 Total memories: {summary['total_memories']}\n\n"
        
        if summary['total_memories'] == 0:
            output += "ℹ️ No memories stored for this node yet."
            return output
        
        # Show memories by type
        output += "**By Type:**\n"
        for mem_type, memories in summary['by_type'].items():
            output += f"• {mem_type}: {len(memories)} entries\n"
            # Show latest entry for each type
            latest = max(memories, key=lambda m: m['updated_at'])
            output += f"  Latest: {latest['content'][:100]}...\n\n"
        
        # Show memories by LLM
        output += "**By LLM:**\n"
        for llm, memories in summary['by_llm'].items():
            output += f"• {llm}: {len(memories)} entries\n"
        
        # Show tags
        if summary['tags']:
            output += f"\n🏷️ **Tags:** {', '.join(summary['tags'])}\n"
        
        output += f"\n⏰ **Last updated:** {summary['latest_update']}"
        
        return output
        
    except Exception as e:
        return f"❌ Failed to get memory summary: {str(e)}"


@mcp.tool()
def store_coding_pattern(
    project_path: str,
    pattern_type: str,
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
    """Store a coding pattern for reuse across the project.
    
    This allows LLMs to build up a library of proven patterns, architectural decisions,
    and coding standards that can be consistently applied.
    
    Args:
        project_path: Project directory path (required)
        pattern_type: Type of pattern - "architecture", "design_pattern", "code_style", 
                     "naming_convention", "error_handling", "security", "performance", 
                     "testing", "api_design", "database", "deployment", "documentation"
        title: Short descriptive title for the pattern
        description: Detailed description of the pattern
        example_code: Code example demonstrating the pattern (optional)
        anti_pattern: Example of what NOT to do (optional)
        when_to_use: Guidelines on when to apply this pattern (optional)
        benefits: List of benefits from using this pattern (optional)
        trade_offs: List of trade-offs to consider (optional)
        tags: List of tags for categorization (optional)
        llm_name: Name of the LLM storing this pattern (default: "claude")
        confidence: Confidence score 0.0-1.0 (default: 1.0)
    
    Returns:
        Success message with pattern ID
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        pattern_manager = PatternMemoryManager(indexer.db_path)
        
        # Validate pattern type
        try:
            pattern_type_enum = PatternType(pattern_type.lower())
        except ValueError:
            valid_types = [pt.value for pt in PatternType]
            return f"❌ Invalid pattern type '{pattern_type}'. Valid types: {', '.join(valid_types)}"
        
        # Store the pattern
        pattern_id = pattern_manager.store_pattern(
            pattern_type=pattern_type_enum,
            title=title,
            description=description,
            example_code=example_code,
            anti_pattern=anti_pattern,
            when_to_use=when_to_use,
            benefits=benefits,
            trade_offs=trade_offs,
            tags=tags,
            llm_name=llm_name,
            confidence=confidence
        )
        
        return f"✅ Coding pattern stored successfully!\n\n📋 Pattern ID: {pattern_id}\n🏷️ Type: {pattern_type}\n📝 Title: {title}\n🏷️ Tags: {', '.join(tags or [])}\n🎯 Confidence: {confidence}"
        
    except Exception as e:
        return f"❌ Failed to store coding pattern: {str(e)}"


@mcp.tool()
def store_best_practice(
    project_path: str,
    category: str,
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
    """Store a best practice for consistent application across the project.
    
    This enables LLMs to establish and maintain coding standards, team practices,
    and project-specific guidelines.
    
    Args:
        project_path: Project directory path (required)
        category: Category of best practice - "team_standards", "project_rules",
                 "industry_best", "company_policy", "tool_usage", "code_review",
                 "refactoring", "maintenance"
        title: Short title for the best practice
        description: Detailed description of the practice
        rationale: Why this is considered a best practice
        examples: List of good implementation examples (optional)
        counter_examples: List of what to avoid (optional)
        enforcement_level: "must", "should", "could", or "avoid" (default: "should")
        scope: "project", "team", "company", or "global" (default: "project")
        tools_required: List of tools needed to implement (optional)
        tags: List of tags for categorization (optional)
        priority: "high", "medium", or "low" (default: "medium")
        llm_name: Name of the LLM storing this practice (default: "claude")
    
    Returns:
        Success message with practice ID
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        pattern_manager = PatternMemoryManager(indexer.db_path)
        
        # Validate category
        try:
            category_enum = BestPracticeCategory(category.lower())
        except ValueError:
            valid_categories = [cat.value for cat in BestPracticeCategory]
            return f"❌ Invalid category '{category}'. Valid categories: {', '.join(valid_categories)}"
        
        # Validate enforcement level and priority
        valid_enforcement = ["must", "should", "could", "avoid"]
        valid_priorities = ["high", "medium", "low"]
        
        if enforcement_level not in valid_enforcement:
            return f"❌ Invalid enforcement level '{enforcement_level}'. Valid levels: {', '.join(valid_enforcement)}"
        
        if priority not in valid_priorities:
            return f"❌ Invalid priority '{priority}'. Valid priorities: {', '.join(valid_priorities)}"
        
        # Store the best practice
        practice_id = pattern_manager.store_best_practice(
            category=category_enum,
            title=title,
            description=description,
            rationale=rationale,
            examples=examples,
            counter_examples=counter_examples,
            enforcement_level=enforcement_level,
            scope=scope,
            tools_required=tools_required,
            tags=tags,
            priority=priority,
            llm_name=llm_name
        )
        
        return f"✅ Best practice stored successfully!\n\n📋 Practice ID: {practice_id}\n🏷️ Category: {category}\n📝 Title: {title}\n⚖️ Enforcement: {enforcement_level}\n🎯 Priority: {priority}\n🏷️ Tags: {', '.join(tags or [])}"
        
    except Exception as e:
        return f"❌ Failed to store best practice: {str(e)}"


@mcp.tool()
def get_coding_patterns(
    project_path: str,
    pattern_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    min_confidence: float = 0.0,
    limit: int = 20
) -> str:
    """Retrieve coding patterns stored for the project.
    
    Args:
        project_path: Project directory path (required)
        pattern_type: Filter by pattern type (optional)
        tags: Filter by tags (optional)
        min_confidence: Minimum confidence score (default: 0.0)
        limit: Maximum number of patterns to return (default: 20)
    
    Returns:
        Formatted list of coding patterns
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        pattern_manager = PatternMemoryManager(indexer.db_path)
        
        # Convert pattern_type string to enum if provided
        pattern_type_enum = None
        if pattern_type:
            try:
                pattern_type_enum = PatternType(pattern_type.lower())
            except ValueError:
                valid_types = [pt.value for pt in PatternType]
                return f"❌ Invalid pattern type '{pattern_type}'. Valid types: {', '.join(valid_types)}"
        
        patterns = pattern_manager.get_patterns(
            pattern_type=pattern_type_enum,
            tags=tags,
            min_confidence=min_confidence,
            limit=limit
        )
        
        if not patterns:
            return "ℹ️ No coding patterns found matching the criteria."
        
        output = f"🎯 Found {len(patterns)} Coding Patterns\n\n"
        
        for i, pattern in enumerate(patterns, 1):
            output += f"{i}. **{pattern['title']}** ({pattern['pattern_type']})\n"
            output += f"   📝 {pattern['description'][:100]}{'...' if len(pattern['description']) > 100 else ''}\n"
            output += f"   🎯 Confidence: {pattern['confidence']:.2f} | 📊 Used: {pattern['usage_frequency']} times\n"
            
            if pattern['tags']:
                output += f"   🏷️ Tags: {', '.join(pattern['tags'])}\n"
            
            if pattern['example_code']:
                output += f"   💻 Has code example\n"
            
            if pattern['when_to_use']:
                output += f"   📋 When to use: {pattern['when_to_use'][:80]}{'...' if len(pattern['when_to_use']) > 80 else ''}\n"
            
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Failed to retrieve coding patterns: {str(e)}"


@mcp.tool()
def get_best_practices(
    project_path: str,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    enforcement_level: Optional[str] = None,
    scope: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 20
) -> str:
    """Retrieve best practices stored for the project.
    
    Args:
        project_path: Project directory path (required)
        category: Filter by category (optional)
        priority: Filter by priority - "high", "medium", "low" (optional)
        enforcement_level: Filter by enforcement - "must", "should", "could", "avoid" (optional)
        scope: Filter by scope - "project", "team", "company", "global" (optional)
        tags: Filter by tags (optional)
        limit: Maximum number of practices to return (default: 20)
    
    Returns:
        Formatted list of best practices
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        pattern_manager = PatternMemoryManager(indexer.db_path)
        
        # Convert category string to enum if provided
        category_enum = None
        if category:
            try:
                category_enum = BestPracticeCategory(category.lower())
            except ValueError:
                valid_categories = [cat.value for cat in BestPracticeCategory]
                return f"❌ Invalid category '{category}'. Valid categories: {', '.join(valid_categories)}"
        
        practices = pattern_manager.get_best_practices(
            category=category_enum,
            priority=priority,
            enforcement_level=enforcement_level,
            scope=scope,
            tags=tags,
            limit=limit
        )
        
        if not practices:
            return "ℹ️ No best practices found matching the criteria."
        
        output = f"⭐ Found {len(practices)} Best Practices\n\n"
        
        for i, practice in enumerate(practices, 1):
            output += f"{i}. **{practice['title']}** ({practice['category']})\n"
            output += f"   📝 {practice['description'][:100]}{'...' if len(practice['description']) > 100 else ''}\n"
            output += f"   ⚖️ {practice['enforcement_level'].upper()} | 🎯 Priority: {practice['priority']} | 📏 Scope: {practice['scope']}\n"
            
            if practice['rationale']:
                output += f"   💡 Why: {practice['rationale'][:80]}{'...' if len(practice['rationale']) > 80 else ''}\n"
            
            if practice['tags']:
                output += f"   🏷️ Tags: {', '.join(practice['tags'])}\n"
            
            if practice['tools_required']:
                output += f"   🔧 Tools: {', '.join(practice['tools_required'])}\n"
            
            if practice['examples']:
                output += f"   ✅ Has {len(practice['examples'])} example(s)\n"
            
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Failed to retrieve best practices: {str(e)}"


@mcp.tool()
def search_patterns_and_practices(
    project_path: str,
    search_term: str,
    include_patterns: bool = True,
    include_practices: bool = True,
    limit: int = 15
) -> str:
    """Search across both coding patterns and best practices.
    
    Args:
        project_path: Project directory path (required)
        search_term: Term to search for in titles, descriptions, and content
        include_patterns: Whether to include coding patterns in results (default: True)
        include_practices: Whether to include best practices in results (default: True)
        limit: Maximum results per category (default: 15)
    
    Returns:
        Combined search results from patterns and practices
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        pattern_manager = PatternMemoryManager(indexer.db_path)
        
        results = pattern_manager.search_patterns_and_practices(
            search_term=search_term,
            include_patterns=include_patterns,
            include_practices=include_practices,
            limit=limit
        )
        
        output = f"🔍 Search Results for '{search_term}'\n\n"
        
        if include_patterns and results['patterns']:
            output += f"🎯 **Coding Patterns** ({len(results['patterns'])} found)\n\n"
            for i, pattern in enumerate(results['patterns'], 1):
                output += f"{i}. **{pattern['title']}** ({pattern['pattern_type']})\n"
                output += f"   📝 {pattern['description'][:80]}{'...' if len(pattern['description']) > 80 else ''}\n"
                output += f"   🎯 Confidence: {pattern['confidence']:.2f}\n\n"
        
        if include_practices and results['best_practices']:
            output += f"⭐ **Best Practices** ({len(results['best_practices'])} found)\n\n"
            for i, practice in enumerate(results['best_practices'], 1):
                output += f"{i}. **{practice['title']}** ({practice['category']})\n"
                output += f"   📝 {practice['description'][:80]}{'...' if len(practice['description']) > 80 else ''}\n"
                output += f"   ⚖️ {practice['enforcement_level'].upper()} | 🎯 {practice['priority']}\n\n"
        
        if not results['patterns'] and not results['best_practices']:
            output += f"ℹ️ No patterns or practices found containing '{search_term}'."
        
        return output
        
    except Exception as e:
        return f"❌ Failed to search patterns and practices: {str(e)}"


@mcp.tool()
def get_project_standards_summary(project_path: str) -> str:
    """Get a comprehensive summary of all project standards, patterns, and practices.
    
    Args:
        project_path: Project directory path (required)
    
    Returns:
        Summary of project coding standards and established patterns
    """
    # Validate project path
    project_path = os.path.abspath(os.path.expanduser(project_path))
    if not os.path.exists(project_path):
        return f"❌ Project path does not exist: {project_path}"
    
    try:
        indexer = project_manager.get_indexer(project_path)
        pattern_manager = PatternMemoryManager(indexer.db_path)
        
        summary = pattern_manager.get_project_standards_summary()
        
        output = f"📊 **Project Standards Summary**\n\n"
        
        # Overall statistics
        stats = summary['summary']
        output += f"📈 **Overview**\n"
        output += f"• Total Patterns: {stats['total_patterns']}\n"
        output += f"• Total Practices: {stats['total_practices']}\n"
        output += f"• Avg Pattern Confidence: {stats['avg_pattern_confidence']:.2f}\n"
        output += f"• Avg Practice Compliance: {stats['avg_practice_compliance']:.2f}\n\n"
        
        # Pattern breakdown
        if summary['pattern_statistics']:
            output += f"🎯 **Patterns by Type**\n"
            for pattern_type, data in summary['pattern_statistics'].items():
                output += f"• {pattern_type}: {data['count']} patterns (avg confidence: {data['avg_confidence']:.2f})\n"
            output += "\n"
        
        # Practice breakdown
        if summary['practice_statistics']:
            output += f"⭐ **Practices by Category**\n"
            for category, data in summary['practice_statistics'].items():
                output += f"• {category}: {data['count']} practices (avg compliance: {data['avg_compliance']:.2f})\n"
            output += "\n"
        
        # High priority practices
        if summary['high_priority_practices']:
            output += f"🚨 **High Priority Practices**\n"
            for practice in summary['high_priority_practices'][:5]:
                output += f"• **{practice['title']}** ({practice['category']}) - {practice['enforcement_level']}\n"
            output += "\n"
        
        # Popular patterns
        if summary['popular_patterns']:
            output += f"🔥 **Most Used Patterns**\n"
            for pattern in summary['popular_patterns'][:5]:
                output += f"• **{pattern['title']}** ({pattern['pattern_type']}) - used {pattern['usage_frequency']} times\n"
            output += "\n"
        
        if stats['total_patterns'] == 0 and stats['total_practices'] == 0:
            output += "ℹ️ No patterns or practices have been established yet.\n"
            output += "💡 Use `store_coding_pattern()` and `store_best_practice()` to build your project standards!"
        
        return output
        
    except Exception as e:
        return f"❌ Failed to get project standards summary: {str(e)}"


@mcp.tool()
def submit_feedback(
    title: str,
    description: str,
    feedback_type: str = "improvement",
    priority: str = "medium",
    tool_name: str = "claude-code-indexer",
    context: Optional[str] = None
) -> str:
    """Submit feedback or feature request for tools.
    
    Args:
        title: Short title describing the feedback
        description: Detailed description of the issue or request
        feedback_type: Type - bug, feature, improvement, question, praise (default: improvement)
        priority: Priority - low, medium, high, critical (default: medium)
        tool_name: Name of the tool (default: claude-code-indexer)
        context: Additional context as JSON string (optional)
    
    Returns:
        Confirmation message with feedback ID
    
    Examples:
        submit_feedback("Search needs escaping", "FTS5 queries fail with special chars", "bug", "high")
        submit_feedback("Add export feature", "Need ability to export index to JSON", "feature")
    """
    try:
        # Parse context if provided
        context_dict = {}
        if context:
            try:
                context_dict = json.loads(context)
            except:
                context_dict = {'raw_context': context}
        
        # Get feedback client
        client = get_feedback_client()
        
        # Submit feedback
        result = client.submit_feedback(
            tool_name=tool_name,
            title=title,
            description=description,
            feedback_type=feedback_type,
            priority=priority,
            context=context_dict
        )
        
        if result['success']:
            output = f"✅ Feedback submitted successfully!\n\n"
            output += f"📝 ID: {result['feedback_id']}\n"
            output += f"📌 Title: {title}\n"
            output += f"🏷️ Type: {feedback_type}\n"
            output += f"⚡ Priority: {priority}\n"
            
            if result.get('synced'):
                output += f"☁️ Status: Synced to cloud\n"
            else:
                output += f"💾 Status: Saved locally (will sync later)\n"
            
            output += f"\nThank you for your feedback! It helps improve the tools."
            return output
        else:
            return f"❌ Failed to submit feedback: {result.get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error submitting feedback: {str(e)}"


@mcp.tool()
def list_feedback(project_path: Optional[str] = None, status: str = "all", limit: int = 10) -> str:
    """List recent feedback submissions.
    
    Args:
        project_path: Optional project path to filter feedback
        status: Filter by status - all, new, reviewed, resolved (default: all)
        limit: Maximum number of items to return (default: 10)
    
    Returns:
        List of recent feedback items
    """
    try:
        from .feedback_tool import LocalFeedbackStore
        
        # Get local feedback store
        store = LocalFeedbackStore()
        
        # Query feedback
        conn = sqlite3.connect(store.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM feedback"
        params = []
        
        conditions = []
        if project_path:
            conditions.append("tool_name = ?")
            params.append(project_path)
        
        if status != "all":
            conditions.append("status = ?")
            params.append(status)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "ℹ️ No feedback found matching criteria."
        
        output = f"📋 Recent Feedback ({len(rows)} items)\n\n"
        
        for row in rows:
            feedback = dict(zip(columns, row))
            
            # Parse context if it's JSON
            if feedback.get('context'):
                try:
                    feedback['context'] = json.loads(feedback['context'])
                except:
                    pass
            
            # Format status emoji
            status_emoji = {
                'new': '🆕',
                'reviewed': '👀',
                'in_progress': '🔄',
                'resolved': '✅',
                'wont_fix': '❌'
            }.get(feedback['status'], '❓')
            
            # Format priority color
            priority_emoji = {
                'low': '🟢',
                'medium': '🟡',
                'high': '🟠',
                'critical': '🔴'
            }.get(feedback['priority'], '⚪')
            
            output += f"{status_emoji} **{feedback['title']}**\n"
            output += f"   ID: {feedback['id']}\n"
            output += f"   Type: {feedback['feedback_type']} {priority_emoji} {feedback['priority']}\n"
            output += f"   Tool: {feedback['tool_name']}\n"
            
            if feedback.get('description'):
                desc_lines = feedback['description'].split('\n')
                output += f"   Description: {desc_lines[0]}\n"
                if len(desc_lines) > 1:
                    output += f"   {'...(more)'}\n"
            
            output += f"   Date: {feedback['created_at']}\n"
            
            if feedback.get('synced'):
                output += f"   ☁️ Synced\n"
            else:
                output += f"   💾 Local only\n"
            
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error listing feedback: {str(e)}"


@mcp.tool()
def get_error_stats() -> str:
    """Get statistics about tracked errors.
    
    Returns:
        Summary of error tracking statistics
    """
    try:
        tracker = get_error_tracker()
        stats = tracker.get_error_stats()
        
        output = "📊 Error Tracking Statistics\n\n"
        output += f"Total Errors Tracked: {stats['total_errors']}\n"
        output += f"Unique Error Types: {stats['unique_errors']}\n"
        output += f"Reported to GitHub: {stats['reported_to_github']}\n\n"
        
        if stats['most_common']:
            output += "🔥 Most Common Errors:\n"
            for i, error in enumerate(stats['most_common'], 1):
                output += f"{i}. [{error['type']}] {error['message']}\n"
                output += f"   Occurrences: {error['count']}\n\n"
        
        output += "\n💡 Errors are automatically reported to GitHub Issues for improvement."
        output += "\n🔒 All sensitive data is sanitized before reporting."
        
        return output
        
    except Exception as e:
        return f"❌ Error getting statistics: {str(e)}"


@mcp.tool()
def sync_feedback() -> str:
    """Sync local feedback to cloud service.
    
    Returns:
        Status of sync operation
    """
    try:
        client = get_feedback_client()
        result = client.sync_pending_feedback()
        
        if result['success']:
            if result.get('synced_count', 0) > 0:
                output = f"✅ Successfully synced feedback to cloud!\n\n"
                output += f"📤 Synced: {result['synced_count']} items\n"
                output += f"💬 Message: {result['message']}"
            else:
                output = "ℹ️ No pending feedback to sync."
            return output
        else:
            return f"❌ Sync failed: {result.get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error syncing feedback: {str(e)}"


def main():
    """Main entry point for MCP server"""
    if not MCP_AVAILABLE:
        print("MCP SDK is required. Install with:", file=sys.stderr)
        print("pip install 'claude-code-indexer[mcp]'", file=sys.stderr)
        sys.exit(1)
    
    logger.info("Starting Claude Code Indexer MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()