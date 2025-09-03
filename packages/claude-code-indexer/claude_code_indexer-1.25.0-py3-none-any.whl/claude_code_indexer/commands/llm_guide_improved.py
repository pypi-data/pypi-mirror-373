"""Enhanced LLM Guide Command with MCP-style descriptions"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def get_mcp_style_guide(version):
    """Generate MCP-style tool catalog"""
    return f"""🤖 Claude Code Indexer v{version} - MCP-Style Tool Catalog

## Available Tools

### cci_init
Description: Initialize project with CLAUDE.md configuration
When to use: First time in any project, creates AI-friendly documentation
Parameters: --force (overwrite existing)
Output: CLAUDE.md file with tool catalog + database setup
Example: cci init

### cci_index
Description: Index source code into graph database
When to use: After init or when code changes significantly  
Parameters: path (directory), --force (ignore cache)
Output: Graph with nodes (3000+) and edges (relationships)
Performance: ~50 files/sec with cache
Example: cci index .

### cci_query
Description: Query indexed entities with smart filters
When to use: To understand project structure and find key components
Parameters:
  --important: Show critical components (PageRank algorithm)
  --type [class|function|method]: Filter by entity type
  --limit N: Limit results
Output: Ranked table with importance scores
Example: cci query --important --limit 10

### cci_search
Description: Full-text search across entire codebase
When to use: Finding specific code, functions, or patterns
Parameters:
  keywords: Space-separated terms (OR search by default)
  --mode all: Require ALL keywords (AND search)
Output: Matching entities with file paths and line numbers
Example: cci search authentication login

### cci_stats
Description: Show comprehensive project statistics
When to use: Quick project overview and health check
Output: Languages, file counts, cache performance, graph metrics
Performance: 0.1s (cached)
Example: cci stats

### cci_insights
Description: AI-powered architectural analysis
When to use: Assess code quality, structure, and get recommendations
Output: Health score (0-1), layer distribution, improvement tips
Example: cci insights

### cci_critical
Description: Find most critical components using graph analysis
When to use: Identify key files that need attention
Parameters: --limit N (default 10)
Output: Critical paths and high-impact dependencies
Example: cci critical --limit 5

### cci_enhance
Description: Add AI-powered metadata (requires API)
When to use: Deep architectural understanding (NO SECRETS!)
Parameters: 
  path: Directory to enhance
  --limit N: Number of nodes to analyze
  --force: Re-analyze cached nodes
Warnings: NO sensitive data, start with --limit 5
Output: Adds layer, domain, complexity metadata
Example: cci enhance . --limit 10

### cci_enhanced
Description: Query AI-enhanced metadata
When to use: After running enhance, for architectural queries
Parameters:
  --layer [service|controller|model]: Architecture layer
  --complexity '>0.7': Complexity filter
  --domain [auth|payment]: Business domain
Output: Filtered entities with AI metadata
Example: cci enhanced --layer service --complexity '>0.8'

### cci_state
Description: Manage codebase state and memory
Subcommands:
  capture: Save current snapshot
  diff: Show changes since last capture
  tasks: List development history
When to use: Track project evolution, before major changes
Example: cci state capture

### cci_cache
Description: Manage indexing cache for performance
Subcommands:
  stats: Show cache performance metrics
  clean: Remove old entries
When to use: Optimize re-indexing speed
Output: Cache hit rates, memory usage
Example: cci cache stats

### cci_mcp_install
Description: Setup MCP server for Claude Desktop/Code
When to use: Enable real-time code queries in Claude
Output: Updates Claude configuration files
Example: cci mcp install

### cci_mcp_daemon
Description: Background service for instant queries
Subcommands: start, stop, status, restart
When to use: Zero-latency responses (100x faster)
Benefits: Persistent connection, no startup overhead
Example: cci mcp-daemon start

## Quick Workflows

### Understanding New Codebase
cci init && cci index . && cci query --important && cci insights

### Finding Specific Code
cci search "function_name" && cci critical --limit 5

### Deep Analysis (if no secrets)
cci enhance . --limit 10 && cci enhanced --layer service

## Performance Benchmarks
- Init: 1-2s (one-time)
- Index: 5-10s first, 0.5s cached (95% hit rate)
- Query: 0.05-0.1s
- Search: 0.1-0.2s
- Enhance: 2-5s per node (API calls)"""

def get_json_catalog(version):
    """Generate JSON tool catalog"""
    return {
        "cci_version": version,
        "tools": {
            "cci_init": {
                "description": "Initialize project with AI configuration",
                "parameters": ["--force"],
                "output": "CLAUDE.md + database",
                "performance": "1-2s"
            },
            "cci_index": {
                "description": "Index code into graph database",
                "parameters": ["path", "--force"],
                "output": "Graph with nodes and edges",
                "performance": "50 files/sec"
            },
            "cci_query": {
                "description": "Query indexed entities",
                "parameters": ["--important", "--type", "--limit"],
                "output": "Ranked entities table",
                "performance": "0.05s"
            },
            "cci_search": {
                "description": "Full-text code search",
                "parameters": ["keywords", "--mode"],
                "output": "Matching entities",
                "performance": "0.1s"
            },
            "cci_stats": {
                "description": "Project statistics",
                "parameters": [],
                "output": "Metrics and counts",
                "performance": "0.1s cached"
            },
            "cci_insights": {
                "description": "Architectural analysis",
                "parameters": [],
                "output": "Health score and recommendations",
                "performance": "0.2s"
            },
            "cci_critical": {
                "description": "Find critical components",
                "parameters": ["--limit"],
                "output": "Key dependencies",
                "performance": "0.1s"
            },
            "cci_enhance": {
                "description": "AI-powered metadata",
                "parameters": ["path", "--limit", "--force"],
                "warnings": ["NO_SECRETS", "API_COSTS"],
                "output": "Enhanced metadata",
                "performance": "2-5s/node"
            },
            "cci_enhanced": {
                "description": "Query enhanced metadata",
                "parameters": ["--layer", "--complexity", "--domain"],
                "output": "Filtered entities",
                "performance": "0.05s"
            },
            "cci_state": {
                "description": "Codebase state management",
                "subcommands": ["capture", "diff", "tasks"],
                "output": "State snapshots",
                "performance": "0.1s"
            },
            "cci_cache": {
                "description": "Cache management",
                "subcommands": ["stats", "clean"],
                "output": "Cache metrics",
                "performance": "instant"
            },
            "cci_mcp_install": {
                "description": "Setup MCP for Claude",
                "parameters": ["--force"],
                "output": "Config updates",
                "performance": "2s"
            },
            "cci_mcp_daemon": {
                "description": "Background service",
                "subcommands": ["start", "stop", "status"],
                "benefits": "100x faster queries",
                "performance": "instant"
            }
        },
        "workflows": {
            "understand_new_codebase": [
                "cci init",
                "cci index .",
                "cci query --important",
                "cci insights"
            ],
            "find_specific_code": [
                "cci search <term>",
                "cci critical --limit 5"
            ],
            "deep_analysis": [
                "cci enhance . --limit 10",
                "cci enhanced --layer service"
            ]
        }
    }

def get_interactive_guide():
    """Generate interactive table-based guide"""
    table = Table(title="🤖 CCI Tool Catalog - Interactive Guide", show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="green", width=20)
    table.add_column("Description", width=40)
    table.add_column("When to Use", width=40)
    
    tools = [
        ("cci init", "Initialize project", "First time setup"),
        ("cci index", "Build code graph", "After init or major changes"),
        ("cci query", "Query entities", "Understand structure"),
        ("cci search", "Full-text search", "Find specific code"),
        ("cci stats", "Project metrics", "Quick overview"),
        ("cci insights", "AI analysis", "Architecture assessment"),
        ("cci critical", "Key components", "Find important files"),
        ("cci enhance", "Add AI metadata", "Deep understanding (NO SECRETS)"),
        ("cci state", "Save snapshots", "Track evolution"),
        ("cci mcp-daemon", "Background service", "100x faster queries"),
    ]
    
    for tool, desc, when in tools:
        table.add_row(tool, desc, when)
    
    return table

@click.command()
@click.option('--format', type=click.Choice(['text', 'mcp', 'json', 'interactive']), 
              default='interactive', help='Output format (interactive is best for LLMs)')
@click.option('--tool', help='Get detailed help for specific tool')
def llm_guide_enhanced(format, tool):
    """🤖 Enhanced guide for LLMs with MCP-style descriptions
    
    Provides comprehensive tool catalog in multiple formats:
    - interactive: Rich table view (default, best for LLMs)
    - mcp: MCP-style tool descriptions
    - json: Machine-readable catalog
    - text: Simple text guide
    
    Use --tool for detailed help on specific commands.
    """
    from .. import __version__
    
    if tool:
        # Provide detailed help for specific tool
        tool_help = get_tool_details(tool)
        console.print(Panel(tool_help, title=f"🔧 {tool} - Detailed Guide"))
        return
    
    if format == 'mcp':
        console.print(get_mcp_style_guide(__version__))
    elif format == 'json':
        console.print(json.dumps(get_json_catalog(__version__), indent=2))
    elif format == 'interactive':
        console.print(get_interactive_guide())
        console.print("\n💡 [bold yellow]Pro Tip:[/bold yellow] Use --format mcp for MCP-style descriptions")
        console.print("📚 [bold cyan]Workflow:[/bold cyan] cci init → cci index . → cci query --important")
    else:
        # Default text format
        console.print(get_text_guide(__version__))

def get_tool_details(tool):
    """Get detailed help for a specific tool"""
    tools_detail = {
        "init": """cci init - Initialize CCI in your project

Purpose: Sets up Claude Code Indexer for the first time
Creates: CLAUDE.md with comprehensive tool catalog
Database: Initializes graph database for code analysis

Usage: cci init [--force]
  --force: Overwrite existing CLAUDE.md

Best Practice: Run once per project, at the root directory
Next Step: Run 'cci index .' to build the code graph""",
        
        "index": """cci index - Build code graph database

Purpose: Analyzes all source files and builds relationship graph
Detects: Classes, functions, imports, dependencies
Languages: Python, JS, TS, Java, Go, Rust, and 20+ more

Usage: cci index [path] [--force]
  path: Directory to index (default: current)
  --force: Ignore cache, re-index everything

Performance: ~50 files/sec with cache, 95% cache hit rate
Cache: Smart caching - only re-indexes changed files""",
        
        "query": """cci query - Smart entity search with filters

Purpose: Find and understand code structure
Algorithm: PageRank-based importance scoring
Filters: Type, importance, custom queries

Usage: cci query [options]
  --important: Show most critical components
  --type [class|function|method]: Filter by type
  --limit N: Limit results (default: 20)

Output: Ranked table with importance scores
Best For: Understanding project architecture""",
        
        "search": """cci search - Full-text code search

Purpose: Find specific code, functions, or patterns
Method: Fast full-text search across all indexed files

Usage: cci search <keywords> [--mode all]
  keywords: Space-separated terms
  --mode all: Require ALL keywords (AND search)
  (default: OR search - any keyword matches)

Examples:
  cci search authentication  # Find auth code
  cci search db connection --mode all  # Both terms

Output: Matching entities with file:line references"""
    }
    
    return tools_detail.get(tool, f"No detailed help available for '{tool}'. Try: init, index, query, search")

def get_text_guide(version):
    """Generate simple text guide"""
    return f"""🤖 Claude Code Indexer v{version} - LLM Guide

QUICK START:
1. cci init              # One-time setup
2. cci index .           # Build code graph
3. cci query --important # Find key components
4. cci search <term>     # Search for code

KEY TOOLS:
• cci stats - Project overview
• cci insights - Architecture analysis
• cci critical - Key dependencies
• cci enhance - AI metadata (NO SECRETS!)
• cci state capture - Save snapshots

PERFORMANCE:
• Index: 50 files/sec (cached)
• Query: 0.05s
• Search: 0.1s

Try: cci llm-guide --format mcp for detailed descriptions"""