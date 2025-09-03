#!/usr/bin/env python3
"""
Command-line interface for Claude Code Indexer
"""

import os
import sys
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
from rich.panel import Panel
from rich.table import Table

# Core imports with fallback
try:
    import click
except ImportError:
    print("Error: click not installed. Run: pip install click")
    sys.exit(1)

# Version info - always available
__version__ = "1.25.0"
__app_name__ = "Claude Code Indexer"

# Import state manager for testing
try:
    from .state_manager import CodebaseStateManager
except ImportError:
    CodebaseStateManager = None

# Import storage manager for testing
try:
    from .storage_manager import get_storage_manager
except ImportError:
    get_storage_manager = None

# Safe import helper
def safe_import(module_path: str, attribute: Optional[str] = None, fallback: Any = None) -> Any:
    """Safely import with fallback support"""
    try:
        if module_path.startswith('.'):
            # Relative import - handle different execution contexts
            package = __package__ or 'claude_code_indexer'
            
            # If running as script, ensure the package is properly set up
            if package == '__main__' or not package:
                # Try to determine package from file location
                import os
                current_file = os.path.abspath(__file__)
                if 'claude_code_indexer' in current_file:
                    package = 'claude_code_indexer'
            
            from importlib import import_module
            module = import_module(module_path, package=package)
        else:
            # Absolute import
            __import__(module_path)
            module = sys.modules[module_path]
        
        if attribute:
            return getattr(module, attribute, fallback)
        return module
    except ImportError:
        return fallback
    except Exception:
        return fallback

# Import with fallbacks
Console = safe_import('rich.console', 'Console')
if Console:
    console = Console()
else:
    # Fallback console
    class SimpleConsole:
        def print(self, text, **kwargs):
            # Strip rich markup
            text = str(text)
            for tag in ['[red]', '[/red]', '[green]', '[/green]', '[bold]', '[/bold]', 
                       '[cyan]', '[/cyan]', '[dim]', '[/dim]', '[yellow]', '[/yellow]']:
                text = text.replace(tag, '')
            print(text)
    console = SimpleConsole()

# Lazy imports
Table = safe_import('rich.table', 'Table')
Progress = safe_import('rich.progress', 'Progress')
Text = safe_import('rich.text', 'Text')

# Local imports with error handling - delay indexer import to avoid circular dependency
CodeGraphIndexer = None  # Will be imported on demand
Updater = safe_import('.updater', 'Updater')
check_and_notify_update = safe_import('.updater', 'check_and_notify_update')
validate_file_path = safe_import('.security', 'validate_file_path')
SecurityError = safe_import('.security', 'SecurityError', Exception)
suggest_github_issue = safe_import('.github_reporter', 'suggest_github_issue')
# god_mode removed during cleanup
# god_mode_group = safe_import('.commands.god_mode', 'god_mode_group')
god_mode_group = None
migrate_command = safe_import('.cli_migrate', 'migrate')
install_crash_handler = safe_import('.crash_handler', 'install_crash_handler')
crash_group = safe_import('.commands.crash', 'crash')


def get_code_graph_indexer():
    """Get CodeGraphIndexer with fallback import"""
    global CodeGraphIndexer
    if CodeGraphIndexer is None:
        try:
            # Try relative import first
            from .indexer import CodeGraphIndexer as _CodeGraphIndexer
            CodeGraphIndexer = _CodeGraphIndexer
        except (ImportError, ModuleNotFoundError) as e1:
            try:
                # Try absolute import as fallback
                from claude_code_indexer.indexer import CodeGraphIndexer as _CodeGraphIndexer
                CodeGraphIndexer = _CodeGraphIndexer
            except (ImportError, ModuleNotFoundError, AttributeError) as e2:
                # Check if we're in a test environment with mocked modules
                if 'ensmallen' in sys.modules and sys.modules['ensmallen'] is None:
                    # This is a known issue in some test environments
                    # Try to work around it by removing the None entry
                    del sys.modules['ensmallen']
                    try:
                        from claude_code_indexer.indexer import CodeGraphIndexer as _CodeGraphIndexer
                        CodeGraphIndexer = _CodeGraphIndexer
                    except (ImportError, ModuleNotFoundError) as e3:
                        console.print(f"❌ [bold red]Failed to import indexer module:[/bold red]")
                        console.print(f"  Import error: {e3}")
                        console.print("This might be a test environment issue.")
                        sys.exit(1)
                else:
                    console.print(f"❌ [bold red]Failed to import indexer module:[/bold red]")
                    console.print(f"  Relative import error: {e1}")
                    console.print(f"  Absolute import error: {e2}")
                    console.print("Try reinstalling: pip install -e .")
                    # Add more detailed error info
                    import traceback
                    console.print("\n[dim]Detailed error trace:[/dim]")
                    traceback.print_exc()
                    sys.exit(1)
    return CodeGraphIndexer


def show_app_header():
    """Display application name and version header"""
    console.print(f"\n[bold cyan]{__app_name__} v{__version__}[/bold cyan]")
    console.print("[dim]Multi-language code indexing with graph database[/dim]\n")


@click.group()
@click.version_option(version=__version__, prog_name=__app_name__)
def cli():
    """Claude Code Indexer (cci) - Index source code as graph database
    
    💡 Pro tip: Use 'cci' instead of 'claude-code-indexer' for all commands!
    
    🚀 Powerful code analysis tool for LLM-assisted development
    🐛 Report issues: https://github.com/tuannx/claude-prompts/issues
    
    For LLMs: If you encounter errors, use this command to report:
    gh issue create --repo tuannx/claude-prompts --title "[Bug] Error description" --label bug
    """
    pass


@cli.command()
@click.option('--force', is_flag=True, help='Force overwrite existing files')
def init(force):
    """Initialize Claude Code Indexer in current directory
    
    🚀 Creates CLAUDE.md with instructions for LLMs
    📊 Sets up database for code graph analysis
    🔒 Adds code_index.db to .gitignore for safety
    
    Perfect for LLM-assisted development with Claude/ChatGPT/etc.
    
    🐛 Report issues: https://github.com/tuannx/claude-prompts/issues
    """
    cwd = Path.cwd()
    claude_md_path = cwd / "CLAUDE.md"
    
    show_app_header()
    console.print("🚀 [bold blue]Initializing project...[/bold blue]")
    
    # Check if CLAUDE.md exists
    if claude_md_path.exists():
        console.print(f"✓ Found existing CLAUDE.md at {claude_md_path}")
        
        # Read existing content
        with open(claude_md_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Check if our section already exists
        if "## Code Indexing with Graph Database" in existing_content:
            if not force:
                console.print("⚠️  Code indexing section already exists in CLAUDE.md")
                console.print("Use --force to overwrite, or manually remove the section")
                return
            else:
                console.print("🔄 Updating existing section...")
                # Remove existing section
                lines = existing_content.split('\n')
                new_lines = []
                skip_section = False
                
                for line in lines:
                    if line.strip() == "## Code Indexing with Graph Database":
                        skip_section = True
                        continue
                    elif skip_section and line.startswith("## ") and "Code Indexing" not in line:
                        skip_section = False
                        new_lines.append(line)
                    elif not skip_section:
                        new_lines.append(line)
                
                existing_content = '\n'.join(new_lines)
        
        # Append our template
        template_path = Path(__file__).parent / "templates" / "claude_md_template.md"
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Combine content
        updated_content = existing_content.rstrip() + '\n\n' + template_content
        
        # Write back
        with open(claude_md_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        console.print("✓ Updated CLAUDE.md with code indexing instructions")
    
    else:
        console.print("⚠️  CLAUDE.md not found")
        create_new = click.confirm("Create new CLAUDE.md with code indexing setup?")
        
        if create_new:
            # Create new CLAUDE.md with comprehensive template
            template_path = Path(__file__).parent / "templates" / "claude_md_template.md"
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace version placeholder
            template_content = template_content.replace("{{VERSION}}", __version__)
            
            with open(claude_md_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            console.print(f"✓ Created new CLAUDE.md at {claude_md_path}")
        else:
            console.print("❌ Initialization cancelled")
            return
    
    # Create initial database in centralized storage
    from .storage_manager import get_storage_manager
    storage = get_storage_manager()
    project_path = storage.get_project_from_cwd()
    
    _CodeGraphIndexer = get_code_graph_indexer()
    indexer = _CodeGraphIndexer(project_path=project_path)
    console.print(f"✓ Initialized code index database in {storage.app_home}")
    
    # Create .gitignore entry
    gitignore_path = cwd / ".gitignore"
    gitignore_entry = "code_index.db"
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        if gitignore_entry not in gitignore_content:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write(f"\n# Claude Code Indexer\n{gitignore_entry}\n")
            console.print("✓ Added code_index.db to .gitignore")
    else:
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(f"# Claude Code Indexer\n{gitignore_entry}\n")
        console.print("✓ Created .gitignore with code_index.db")
    
    console.print("\n🎉 [bold green]Initialization complete![/bold green]")
    console.print("Next steps:")
    console.print("1. Run [bold]cci index .[/bold] to index current directory")
    console.print("2. Run [bold]cci query --important[/bold] to see key components")
    console.print("3. Run [bold]cci stats[/bold] to view indexing statistics")


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--patterns', default=None, 
              help='File patterns to index (comma-separated) [default: auto-detect from supported languages]')
@click.option('--db', default=None, help='Database file path (default: centralized storage)')
@click.option('--no-cache', is_flag=True, help='Disable caching for faster re-indexing')
@click.option('--force', is_flag=True, help='Force re-index all files (ignore cache)')
@click.option('--workers', type=int, help='Number of parallel workers (default: auto)')
@click.option('--no-optimize', is_flag=True, help='Disable database optimizations')
@click.option('--benchmark', is_flag=True, help='Run performance benchmark')
@click.option('--custom-ignore', multiple=True, help='Additional ignore patterns (can be used multiple times)')
@click.option('--show-ignored', is_flag=True, help='Show what patterns are being ignored')
@click.option('--verbose', is_flag=True, help='Show detailed parsing progress and errors')
@click.option('--track-task', '-t', help='Associate indexing with a task description')
def index(path, patterns, db, no_cache, force, workers, no_optimize, benchmark, custom_ignore, show_ignored, verbose, track_task):
    """Index source code in the specified directory with performance optimizations
    
    🔍 Deep code analysis with:
    - Multi-language AST parsing (Python, JS, TS, Java, AutoIt)
    - Graph relationship mapping (imports, calls, inheritance)
    - Importance scoring via PageRank algorithm
    - Smart caching (64.6x faster re-indexing)
    - State tracking for task correlation
    
    💡 LLM Tip: Run this first to understand any codebase!
    
    🐛 Report issues: https://github.com/tuannx/claude-prompts/issues
    """
    # Validate path for security
    try:
        safe_path = validate_file_path(path)
    except SecurityError as e:
        console.print(f"❌ [red]Security error: {e}[/red]")
        sys.exit(1)
    
    show_app_header()
    
    # Track task if specified
    task_id = None
    if track_task:
        try:
            if CodebaseStateManager is None:
                raise ImportError("State manager not available")
            manager = CodebaseStateManager(safe_path)
            task_id = manager.track_task({"description": track_task})
            console.print(f"[cyan]📋 Tracking task: {task_id} - {track_task}[/cyan]\n")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not track task: {e}[/yellow]\n")
    
    console.print(f"📁 [bold blue]Indexing code in {safe_path}...[/bold blue]")
    
    # Check if indexer is available
    _CodeGraphIndexer = get_code_graph_indexer()
    if not _CodeGraphIndexer:
        console.print("[red]❌ Error: Indexer module not available[/red]")
        console.print("\n💡 Try these solutions:")
        console.print("1. Reinstall: pip install -e .")
        console.print("2. Check imports: python -m claude_code_indexer.cli doctor")
        console.print("3. Use Python directly: python -m claude_code_indexer.cli index")
        sys.exit(1)
    
    # Parse patterns - use None to auto-detect from supported languages
    pattern_list = None if patterns is None else [p.strip() for p in patterns.split(',')]
    
    # Show performance settings
    if not no_cache:
        console.print("💾 [green]Caching enabled[/green] - unchanged files will be skipped")
    if not no_optimize:
        console.print("🚀 [green]Database optimizations enabled[/green] - using APSW and connection pooling")
    if workers:
        console.print(f"⚡ [green]Parallel processing enabled[/green] - using {workers} workers")
    elif not no_optimize:
        console.print("⚡ [green]Auto parallel processing enabled[/green] - workers will be determined automatically")
    
    # Show ignore patterns if requested
    if show_ignored:
        from .ignore_handler import IgnoreHandler
        ignore_handler = IgnoreHandler(path, list(custom_ignore) if custom_ignore else None)
        console.print("\n📝 [bold blue]Active Ignore Patterns:[/bold blue]")
        patterns = ignore_handler.get_patterns()
        console.print(f"Total patterns: {len(patterns)}")
        console.print("\nTop patterns:")
        for pattern in patterns[:20]:
            console.print(f"  • {pattern}")
        if len(patterns) > 20:
            console.print(f"  ... and {len(patterns) - 20} more")
        console.print()
    
    # Run benchmark if requested
    if benchmark:
        from .db_optimizer import DatabaseBenchmark
        console.print("🔥 [yellow]Running performance benchmark...[/yellow]")
        DatabaseBenchmark.benchmark_insert_performance(db + "_benchmark")
    
    # Create indexer with performance options
    project_path = Path(safe_path).resolve()
    _CodeGraphIndexer = get_code_graph_indexer()
    indexer = _CodeGraphIndexer(
        db_path=db,  # Can be None to use centralized storage
        use_cache=not no_cache,
        parallel_workers=workers,
        enable_optimizations=not no_optimize,
        project_path=project_path
    )
    
    # Index with progress
    with Progress() as progress:
        task = progress.add_task("Indexing files...", total=None)
        
        try:
            # Pass verbose flag to indexer
            indexer.verbose = verbose
            indexer.index_directory(safe_path, patterns=pattern_list, force_reindex=force, 
                                  custom_ignore=list(custom_ignore) if custom_ignore else None)
            progress.update(task, completed=100)
            
            # Show parsing errors if verbose mode
            if verbose and hasattr(indexer, 'parsing_errors') and indexer.parsing_errors:
                console.print("\n⚠️  [yellow]Parsing Warnings:[/yellow]")
                for error in indexer.parsing_errors[:10]:  # Show first 10 errors
                    console.print(f"  • {error}")
                if len(indexer.parsing_errors) > 10:
                    console.print(f"  ... and {len(indexer.parsing_errors) - 10} more")
                    
        except Exception as e:
            console.print(f"❌ [bold red]Error during indexing: {e}[/bold red]")
            if verbose:
                import traceback
                traceback.print_exc()
            # Suggest GitHub issue reporting
            suggest_github_issue(
                error_type=type(e).__name__,
                error_message=str(e),
                command=f"index {path}",
                traceback=traceback.format_exc() if verbose else None
            )
            sys.exit(1)
    
    console.print(f"✅ [bold green]Indexing complete![/bold green]")


@cli.command()
@click.option('--important', is_flag=True, help='Show only important nodes')
@click.option('--type', help='Filter by node type (file, class, method, function)')
@click.option('--limit', default=20, help='Maximum number of results')
@click.option('--db', default=None, help='Database file path (default: centralized storage)')
@click.option('--project', help='Project name/path to query (default: current directory)')
@click.option('--with-state', is_flag=True, help='Include state information in query')
@click.option('--task-id', help='Show code related to specific task')
def query(important, type, limit, db, project, with_state, task_id):
    """Query indexed code entities
    
    🎯 Perfect for LLMs to understand codebase structure!
    
    Examples:
    - cci query --important     # Key components
    - cci query --type class    # All classes
    - cci query --limit 50      # Top 50 nodes
    - cci query --with-state    # Include state info
    - cci query --task-id xxx   # Task-specific code
    
    🐛 Report issues: https://github.com/tuannx/claude-prompts/issues
    """
    show_app_header()
    
    # Handle task-specific query
    if task_id:
        try:
            if CodebaseStateManager is None:
                raise ImportError("State manager not available")
            manager = CodebaseStateManager(project or os.getcwd())
            task = manager.get_task(task_id)
            
            if not task:
                console.print(f"[red]❌ Task {task_id} not found[/red]")
                sys.exit(1)
            
            console.print(Panel.fit(
                f"[cyan]📋 Task: {task['description']}[/cyan]\n"
                f"Status: {task['status']}\n"
                f"Created: {task['created_at'][:19]}",
                title="[bold]Task Information[/bold]"
            ))
            
            if task.get('changes'):
                changes = task['changes']
                if changes.get('files_modified') or changes.get('files_added'):
                    console.print("\n[yellow]Files affected by this task:[/yellow]")
                    for file in changes.get('files_modified', [])[:10]:
                        console.print(f"  📝 {file}")
                    for file in changes.get('files_added', [])[:10]:
                        console.print(f"  ➕ {file}")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load task info: {e}[/yellow]")
    
    # Determine project path
    from .storage_manager import get_storage_manager
    storage = get_storage_manager()
    
    if project:
        # Find project by name or path
        project_info = storage.find_project_by_name(project)
        if project_info:
            project_path = Path(project_info['path'])
        else:
            project_path = Path(project).resolve()
    else:
        project_path = storage.get_project_from_cwd()
    
    # Create indexer with project path
    _CodeGraphIndexer = get_code_graph_indexer()
    indexer = _CodeGraphIndexer(db_path=db, project_path=project_path)
    
    # Check if database exists
    actual_db_path = db or indexer.db_path
    if not os.path.exists(actual_db_path):
        console.print(f"❌ [bold red]Database not found for {project_path}. Run 'cci index' first.[/bold red]")
        sys.exit(1)
    
    if important:
        console.print("🔍 [bold blue]Most important code entities:[/bold blue]")
        # First try with high importance threshold
        nodes = indexer.query_important_nodes(min_score=0.1, limit=limit, node_type=type)
        
        if not nodes:
            # Fallback: get any nodes but keep the type filter
            nodes = indexer.query_important_nodes(min_score=0.0, limit=limit, node_type=type)
            if nodes:
                console.print("⚠️  No high-importance entities found. Showing top entities by score...")
                console.print(f"ℹ️  Highest score: {nodes[0]['importance_score']:.3f}")
    else:
        console.print("📋 [bold blue]All code entities:[/bold blue]")
        nodes = indexer.query_important_nodes(min_score=0.0, limit=limit, node_type=type)
    
    if not nodes:
        if type:
            console.print(f"❌ No entities found of type '{type}'.")
        else:
            console.print("❌ No entities found.")
        return
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="bold")
    table.add_column("Type", style="cyan")
    table.add_column("Importance", style="green")
    table.add_column("Tags", style="yellow")
    table.add_column("Path", style="dim")
    
    for node in nodes:
        importance = f"{node['importance_score']:.3f}"
        tags = ", ".join(node['relevance_tags']) if node['relevance_tags'] else "-"
        table.add_row(
            node['name'],
            node['node_type'],
            importance,
            tags,
            node['path']
        )
    
    console.print(table)
    
    # Show state information if requested
    if with_state:
        try:
            if CodebaseStateManager is None:
                raise ImportError("State manager not available")
            manager = CodebaseStateManager(project_path)
            state = manager.get_current_state()
            
            if state:
                console.print("\n[cyan]📊 Codebase State:[/cyan]")
                console.print(f"  Last captured: {state['timestamp'][:19]}")
                console.print(f"  Total files: {state['stats']['total_files']}")
                console.print(f"  Total lines: {state['stats']['total_lines']:,}")
                
                # Show active tasks
                active_tasks = manager.get_active_tasks()
                if active_tasks:
                    console.print(f"\n[yellow]🔄 Active Tasks ({len(active_tasks)}):[/yellow]")
                    for task in active_tasks[:3]:
                        console.print(f"  • {task['id']}: {task['description'][:50]}")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load state info: {e}[/yellow]")


@cli.command()
@click.argument('terms', nargs=-1, required=True)
@click.option('--db', default=None, help='Database file path (default: centralized storage)')
@click.option('--mode', type=click.Choice(['any', 'all']), default='any', help='Search mode: any (OR) or all (AND)')
@click.option('--limit', default=20, help='Maximum number of results')
@click.option('--type', type=click.Choice(['file', 'class', 'method', 'function', 'import', 'interface']), 
              help='Filter by node type')
@click.option('--project', help='Project name/path to search (default: current directory)')
def search(terms, db, mode, limit, type, project):
    """Search for code entities by name. Supports multiple keywords.
    
    Examples:
        cci search auth
        cci search auth user login --mode any
        cci search database connection --mode all
        cci search service firestore --type class --limit 10
        cci search process --type function
    """
    show_app_header()
    
    # Determine project path
    from .storage_manager import get_storage_manager
    storage = get_storage_manager()
    
    if project:
        # Find project by name or path
        project_info = storage.find_project_by_name(project)
        if project_info:
            project_path = Path(project_info['path'])
        else:
            project_path = Path(project).resolve()
    else:
        project_path = storage.get_project_from_cwd()
    
    # Create indexer with project path
    _CodeGraphIndexer = get_code_graph_indexer()
    indexer = _CodeGraphIndexer(db_path=db, project_path=project_path)
    
    # Check if database exists
    actual_db_path = db or indexer.db_path
    if not os.path.exists(actual_db_path):
        console.print(f"❌ [bold red]Database not found for {project_path}. Run 'cci index' first.[/bold red]")
        sys.exit(1)
    
    import sqlite3
    conn = sqlite3.connect(actual_db_path)
    cursor = conn.cursor()
    
    # Build query based on mode
    if mode == 'any':
        # OR logic - match any keyword
        conditions = []
        params = []
        for term in terms:
            conditions.append("(name LIKE ? OR path LIKE ? OR summary LIKE ?)")
            params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])
        where_clause = " OR ".join(conditions)
    else:
        # AND logic - must match all keywords
        conditions = []
        params = []
        for term in terms:
            conditions.append("(name LIKE ? OR path LIKE ? OR summary LIKE ?)")
            params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])
        where_clause = " AND ".join(conditions)
    
    # Add type filter if specified
    where_conditions = [f"({where_clause})"]
    if type:
        where_conditions.append("node_type = ?")
        params.append(type)
    
    final_where_clause = " AND ".join(where_conditions)
    
    query = f'''
    SELECT name, node_type, path, importance_score, relevance_tags
    FROM code_nodes
    WHERE {final_where_clause}
    ORDER BY importance_score DESC
    LIMIT {limit}
    '''
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    search_desc = ' '.join(terms)
    filter_desc = f"mode: {mode}"
    if type:
        filter_desc += f", type: {type}"
    
    if not results:
        console.print(f"No entities found matching '{search_desc}' ({filter_desc})")
        return
    
    console.print(f"🔍 [bold blue]Search results for '{search_desc}' ({filter_desc}):[/bold blue]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="bold")
    table.add_column("Type", style="cyan")
    table.add_column("Importance", style="green")
    table.add_column("Path", style="dim")
    
    for name, node_type, path, importance, tags in results:
        table.add_row(
            name,
            node_type,
            f"{importance:.3f}",
            path
        )
    
    console.print(table)


@cli.command()
@click.option('--db', default=None, help='Database file path (default: centralized storage)')
@click.option('--cache', is_flag=True, help='Show cache statistics')
@click.option('--project', help='Project name/path for stats (default: current directory)')
def stats(db, cache, project):
    """Show indexing statistics
    
    📊 Quick overview for LLMs:
    - Total nodes and relationships
    - Node type distribution
    - Last indexed timestamp
    - Cache performance metrics
    
    🐛 Report issues: https://github.com/tuannx/claude-prompts/issues
    """
    show_app_header()
    
    # Determine project path
    from .storage_manager import get_storage_manager
    storage = get_storage_manager()
    
    if project:
        # Find project by name or path
        project_info = storage.find_project_by_name(project)
        if project_info:
            project_path = Path(project_info['path'])
        else:
            project_path = Path(project).resolve()
    else:
        project_path = storage.get_project_from_cwd()
    
    # Create indexer with project path
    _CodeGraphIndexer = get_code_graph_indexer()
    indexer = _CodeGraphIndexer(db_path=db, project_path=project_path)
    
    # Check if database exists
    actual_db_path = db or indexer.db_path
    if not os.path.exists(actual_db_path):
        console.print(f"❌ [bold red]Database not found for {project_path}. Run 'cci index' first.[/bold red]")
        sys.exit(1)
    
    # Show cache stats if requested
    if cache:
        from .cache_manager import CacheManager
        cache_manager = CacheManager(project_path=project_path)
        cache_manager.print_cache_stats()
        console.print()  # Add spacing
    stats = indexer.get_stats()
    
    console.print("📊 [bold blue]Code Indexing Statistics[/bold blue]")
    
    # Basic stats
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Metric", style="cyan")
    info_table.add_column("Value", style="bold green")
    
    info_table.add_row("Last indexed", stats.get('last_indexed', 'Never'))
    info_table.add_row("Total nodes", stats.get('total_nodes', '0'))
    info_table.add_row("Total edges", stats.get('total_edges', '0'))
    
    console.print(info_table)
    
    # Node types
    if 'node_types' in stats:
        console.print("\n📋 [bold blue]Node Types:[/bold blue]")
        type_table = Table(show_header=True, header_style="bold magenta")
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", style="bold green")
        
        for node_type, count in stats['node_types'].items():
            type_table.add_row(node_type, str(count))
        
        console.print(type_table)
    
    # Relationship types
    if 'relationship_types' in stats:
        console.print("\n🔗 [bold blue]Relationship Types:[/bold blue]")
        rel_table = Table(show_header=True, header_style="bold magenta")
        rel_table.add_column("Type", style="cyan")
        rel_table.add_column("Count", style="bold green")
        
        for rel_type, count in stats['relationship_types'].items():
            rel_table.add_row(rel_type, str(count))
        
        console.print(rel_table)


@cli.command()
@click.option('--clear', is_flag=True, help='Clear old cache entries (older than 30 days)')
@click.option('--days', type=int, default=30, help='Days threshold for clearing cache')
def cache(clear, days):
    """Manage indexing cache for faster re-indexing"""
    from .cache_manager import CacheManager
    
    cache_manager = CacheManager()
    
    if clear:
        console.print(f"🗑️ [yellow]Clearing cache entries older than {days} days...[/yellow]")
        cache_manager.clear_cache(older_than_days=days)
        console.print("✅ [green]Cache cleared successfully![/green]")
    
    console.print("💾 [bold blue]Cache Statistics[/bold blue]")
    cache_manager.print_cache_stats()


@cli.command()
@click.option('--records', type=int, default=1000, help='Number of test records')
def benchmark(records):
    """Run performance benchmarks"""
    from .db_optimizer import DatabaseBenchmark
    
    console.print(f"🔥 [bold blue]Running performance benchmark with {records} records...[/bold blue]")
    
    sqlite3_time, optimized_time = DatabaseBenchmark.benchmark_insert_performance(
        "benchmark_test.db", num_records=records
    )
    
    console.print(f"\n📊 [bold blue]Benchmark Results:[/bold blue]")
    
    benchmark_table = Table(show_header=True, header_style="bold magenta")
    benchmark_table.add_column("Database Type", style="cyan")
    benchmark_table.add_column("Time (seconds)", style="bold green")
    benchmark_table.add_column("Records/second", style="bold yellow")
    
    benchmark_table.add_row("Standard SQLite3", f"{sqlite3_time:.2f}", f"{records/sqlite3_time:.0f}")
    benchmark_table.add_row("Optimized APSW", f"{optimized_time:.2f}", f"{records/optimized_time:.0f}")
    
    console.print(benchmark_table)
    
    speedup = sqlite3_time / optimized_time
    console.print(f"\n🚀 [bold green]Speedup: {speedup:.1f}x faster with optimizations![/bold green]")


@cli.command()
@click.option('--check-only', is_flag=True, help='Only check for updates without installing')
def update(check_only):
    """Check for and install updates"""
    updater = Updater()
    
    if check_only:
        updater.auto_update(check_only=True)
    else:
        if updater.auto_update(check_only=False):
            # Also sync CLAUDE.md after update
            updater.sync_claude_md()
            console.print("\n🎉 [bold green]Update complete![/bold green]")


@cli.group()
def background():
    """Manage background indexing service"""
    pass


@background.command()
def start():
    """Start the background indexing service"""
    from .background_service import get_background_service
    
    service = get_background_service()
    service.start()
    
    if service.is_running():
        console.print("✅ [green]Background indexing service started successfully![/green]")
    else:
        console.print("❌ [red]Failed to start background indexing service[/red]")


@background.command()
def stop():
    """Stop the background indexing service"""
    from .background_service import get_background_service
    
    service = get_background_service()
    service.stop()
    console.print("✅ [green]Background indexing service stopped[/green]")


@background.command()
def restart():
    """Restart the background indexing service"""
    from .background_service import get_background_service
    
    service = get_background_service()
    service.restart()
    console.print("✅ [green]Background indexing service restarted[/green]")


@background.command()
def status():
    """Show background indexing service status"""
    show_app_header()
    
    from .background_service import get_background_service
    
    service = get_background_service()
    status = service.get_status()
    
    console.print("\n📊 [bold blue]Background Indexing Service Status[/bold blue]\n")
    
    # General status
    console.print(f"Enabled: {'✅ Yes' if status['enabled'] else '❌ No'}")
    console.print(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
    console.print(f"Default interval: {status['default_interval']}s ({status['default_interval'] / 60:.1f} minutes)")
    
    if status['projects']:
        console.print("\n📁 [bold blue]Project Status:[/bold blue]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Project", style="cyan")
        table.add_column("Interval", style="green")
        table.add_column("Last Indexed", style="yellow")
        table.add_column("Next Index", style="blue")
        table.add_column("Status", style="bold")
        
        for project_path, project_status in status['projects'].items():
            interval_str = f"{project_status['interval']}s" if project_status['interval'] > 0 else "Disabled"
            status_str = "🔄 Indexing..." if project_status['indexing'] else "⏸️  Waiting"
            
            # Show full path for managed projects
            project_display = project_path if len(project_path) < 40 else "..." + project_path[-37:]
            
            table.add_row(
                project_display,
                interval_str,
                project_status['last_indexed'][:16] + "…" if len(project_status['last_indexed']) > 16 else project_status['last_indexed'],
                project_status['next_index'][:16] + "…" if len(project_status['next_index']) > 16 else project_status['next_index'],
                status_str
            )
        
        console.print(table)
    else:
        console.print("\n[dim]No projects configured for background indexing[/dim]")


@background.command()
@click.option('--enable/--disable', default=True, help='Enable or disable the service')
def config(enable):
    """Enable or disable background indexing service"""
    from .background_service import get_background_service
    
    service = get_background_service()
    
    if enable:
        service.enable()
        console.print("✅ [green]Background indexing service enabled[/green]")
    else:
        service.disable()
        console.print("❌ [yellow]Background indexing service disabled[/yellow]")


@background.command()
@click.option('--project', help='Project path (default: current directory)')
@click.option('--interval', type=int, default=300, help='Interval in seconds (default: 300, -1 to disable)')
def set_interval(project, interval):
    """Set background indexing interval for a project"""
    from .background_service import get_background_service
    from .storage_manager import get_storage_manager
    
    service = get_background_service()
    
    if project:
        # Set for specific project
        project_path = Path(project).resolve()
        if not project_path.exists():
            console.print(f"❌ [red]Project path does not exist: {project}[/red]")
            return
        
        service.set_project_interval(str(project_path), interval)
        
        if interval == -1:
            console.print(f"❌ [yellow]Disabled background indexing for {project_path}[/yellow]")
        else:
            console.print(f"✅ [green]Set background indexing interval to {interval}s for {project_path}[/green]")
    else:
        # Set default interval
        service.set_default_interval(interval)
        console.print(f"✅ [green]Set default background indexing interval to {interval}s[/green]")
@cli.command()
def sync():
    """Sync CLAUDE.md with latest template"""
    updater = Updater()
    if updater.sync_claude_md(force=True):
        console.print("✅ [bold green]CLAUDE.md synchronized![/bold green]")
    else:
        console.print("✓ CLAUDE.md is already up to date")


@cli.group()
def mcp():
    """MCP (Model Context Protocol) management commands for Claude Desktop/Code integration"""
    pass


@mcp.command("install")
@click.option("--force", is_flag=True, help="Force installation even if Claude Desktop/Code not found")
def mcp_install(force):
    """Install MCP server for Claude Desktop or Claude Code integration"""
    from .mcp_installer import install_mcp
    install_mcp(force=force)


@mcp.command("uninstall")
def mcp_uninstall():
    """Remove MCP server from Claude Desktop or Claude Code"""
    from .mcp_installer import uninstall_mcp
    uninstall_mcp()


@mcp.command("status")
def mcp_status():
    """Show MCP installation status"""
    from .mcp_installer import show_mcp_status
    show_mcp_status()


@cli.command()
@click.option('--all', is_flag=True, help='Show all projects including non-existent')
def projects(all):
    """List all indexed projects"""
    from .storage_manager import get_storage_manager
    storage = get_storage_manager()
    
    projects = storage.list_projects()
    
    if not projects:
        console.print("📭 [yellow]No indexed projects found.[/yellow]")
        console.print("Run 'cci index <path>' to index a project.")
        return
    
    console.print("📚 [bold blue]Indexed Projects[/bold blue]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Last Indexed", style="yellow")
    table.add_column("Size", style="blue")
    table.add_column("Status", style="white")
    
    for project in projects:
        if not all and not project.get('exists', True):
            continue
            
        name = project['name']
        path = project['path']
        last_indexed = project.get('last_indexed', 'Never')
        if last_indexed and last_indexed != 'Never':
            # Format date nicely
            dt = datetime.fromisoformat(last_indexed)
            last_indexed = dt.strftime('%Y-%m-%d %H:%M')
        
        size = project.get('db_size', 0)
        size_str = f"{size / 1024 / 1024:.1f} MB" if size > 0 else "-"
        
        status = "✓" if project.get('exists', True) else "✗ Missing"
        
        table.add_row(name, path, last_indexed, size_str, status)
    
    console.print(table)
    
    # Show storage stats
    stats = storage.get_storage_stats()
    console.print(f"\n💾 Storage: {stats['app_home']}")
    console.print(f"   Total projects: {stats['project_count']}")
    console.print(f"   Total size: {stats['total_size_mb']:.1f} MB")


@cli.command()
@click.argument('project', required=True)
@click.option('--force', is_flag=True, help='Force removal without confirmation')
def remove(project, force):
    """Remove an indexed project"""
    from .storage_manager import get_storage_manager
    storage = get_storage_manager()
    
    # Find project
    project_info = storage.find_project_by_name(project)
    if not project_info:
        # Try as path
        project_path = Path(project).resolve()
        if storage.get_project_id(project_path) in storage.metadata['projects']:
            project_info = {
                'path': str(project_path),
                'name': project_path.name
            }
        else:
            console.print(f"❌ [bold red]Project '{project}' not found.[/bold red]")
            return
    
    # Confirm
    if not force:
        confirm = click.confirm(f"Remove index for '{project_info['name']}' ({project_info['path']})?")
        if not confirm:
            console.print("❌ Removal cancelled.")
            return
    
    # Remove
    removed = storage.remove_project(Path(project_info['path']))
    if removed:
        console.print(f"✅ [bold green]Removed index for '{project_info['name']}'[/bold green]")
    else:
        console.print(f"❌ [bold red]Failed to remove project.[/bold red]")


@cli.command()
def clean():
    """Clean up orphaned project indexes"""
    from .storage_manager import get_storage_manager
    storage = get_storage_manager()
    
    console.print("🔍 [bold blue]Scanning for orphaned projects...[/bold blue]")
    
    removed = storage.clean_orphaned_projects()
    
    if removed:
        console.print(f"✅ [bold green]Cleaned {len(removed)} orphaned projects:[/bold green]")
        for path in removed:
            console.print(f"   • {path}")
    else:
        console.print("✨ [green]No orphaned projects found.[/green]")


# LLM Metadata Enhancement Commands

@cli.command(name='enhance')
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--limit', type=int, help='Limit number of nodes to analyze')
@click.option('--force', is_flag=True, help='Force re-analysis even if cached')
@click.option('--project', help='Project name/path (default: current directory)')
def enhance_metadata(path, limit, force, project):
    """Enhance codebase metadata using LLM analysis
    
    🤖 LLM Enhancement - Powerful AI-driven code analysis
    
    ⚠️  SECURITY WARNING:
    - Do NOT use on code containing secrets, API keys, or sensitive data
    - Recommended for open source or development code only
    - Start with --limit 5-10 to test before full analysis
    
    📊 Features:
    - Architectural layer detection (service, model, controller, etc.)
    - Business domain classification
    - Complexity scoring (0.0-1.0)
    - Criticality assessment
    - Role tagging and pattern detection
    
    💡 Best Practices:
    1. Test with: cci enhance . --limit 5
    2. Review results before scaling up
    3. Use insights command to query enhanced data
    
    🐛 Report issues: https://github.com/tuannx/claude-prompts/issues
    """
    show_app_header()
    
    try:
        path = validate_file_path(path)
    except SecurityError as e:
        console.print(f"❌ [bold red]Security error: {e}[/bold red]")
        sys.exit(1)
    
    console.print(f"🤖 [bold blue]Starting LLM metadata enhancement for: {path}[/bold blue]")
    
    try:
        _CodeGraphIndexer = get_code_graph_indexer()
        indexer = _CodeGraphIndexer(project_path=Path(path))
        
        with Progress() as progress:
            task = progress.add_task("Analyzing codebase...", total=None)
            result = indexer.enhance_metadata(limit=limit, force_refresh=force)
            progress.update(task, completed=100, total=100)
        
        # Display results
        console.print("\n📊 [bold green]Enhancement Complete![/bold green]")
        
        analyzed = result.get('analyzed_count', 0)
        total = result.get('total_nodes', 0)
        duration = result.get('analysis_duration', 'N/A')
        speed = result.get('nodes_per_second', 'N/A')
        
        table = Table(title="Analysis Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Analyzed Nodes", str(analyzed))
        table.add_row("Total Nodes", str(total))
        table.add_row("Duration", duration)
        table.add_row("Speed", f"{speed} nodes/sec")
        
        console.print(table)
        
        # Show architectural layers
        layers = result.get('architectural_layers', {})
        if layers:
            console.print("\n🏗️ [bold]Architectural Layers:[/bold]")
            for layer, count in sorted(layers.items(), key=lambda x: x[1], reverse=True):
                console.print(f"  • {layer}: {count} components")
        
        # Show criticality distribution
        criticality = result.get('criticality_distribution', {})
        if criticality:
            console.print("\n⚠️ [bold]Criticality Distribution:[/bold]")
            for level, count in sorted(criticality.items(), key=lambda x: x[1], reverse=True):
                console.print(f"  • {level}: {count} components")
        
        # Show business domains
        domains = result.get('business_domains', {})
        if domains:
            console.print("\n🏢 [bold]Business Domains:[/bold]")
            for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
                console.print(f"  • {domain}: {count} components")
        
    except Exception as e:
        console.print(f"❌ [bold red]Enhancement failed: {e}[/bold red]")
        # Suggest GitHub issue reporting
        import traceback
        suggest_github_issue(
            error_type=type(e).__name__,
            error_message=str(e),
            command=f"enhance {path} --limit {limit}",
            traceback=traceback.format_exc()
        )
        sys.exit(1)


@cli.command(name='insights')
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--project', help='Project name/path (default: current directory)')
def get_insights(path, project):
    """Get comprehensive codebase insights and health assessment"""
    try:
        path = validate_file_path(path)
    except SecurityError as e:
        console.print(f"❌ [bold red]Security error: {e}[/bold red]")
        sys.exit(1)
    
    console.print(f"📊 [bold blue]Getting codebase insights for: {path}[/bold blue]")
    
    try:
        _CodeGraphIndexer = get_code_graph_indexer()
        indexer = _CodeGraphIndexer(project_path=Path(path))
        insights = indexer.get_analysis_insights()
        
        if not insights:
            console.print("ℹ️ [yellow]No enhanced metadata found. Run 'cci enhance' first.[/yellow]")
            return
        
        # Codebase health
        health = insights.get('codebase_health', {})
        if health:
            console.print("\n🏥 [bold]Codebase Health:[/bold]")
            
            overall_score = health.get('overall_score', 0)
            color = "green" if overall_score > 0.7 else "yellow" if overall_score > 0.5 else "red"
            console.print(f"  Overall Score: [{color}]{overall_score:.3f}/1.0[/{color}]")
            
            complexity_health = health.get('complexity_health', 'unknown')
            testability_health = health.get('testability_health', 'unknown')
            console.print(f"  Complexity: {complexity_health}")
            console.print(f"  Testability: {testability_health}")
            
            recommendations = health.get('recommendations', [])
            if recommendations:
                console.print("  [bold]Recommendations:[/bold]")
                for rec in recommendations:
                    console.print(f"    - {rec}")
        
        # Architectural overview
        arch = insights.get('architectural_overview', {})
        if arch:
            console.print("\n🏗️ [bold]Architecture Overview:[/bold]")
            
            layer_dist = arch.get('layer_distribution', {})
            if layer_dist:
                console.print("  Layer Distribution:")
                for layer, count in sorted(layer_dist.items(), key=lambda x: x[1], reverse=True):
                    console.print(f"    - {layer}: {count} components")
            
            layer_balance = arch.get('layer_balance', 'unknown')
            domain_focus = arch.get('domain_focus', 'unknown')
            console.print(f"  Layer Balance: {layer_balance}")
            console.print(f"  Primary Domain: {domain_focus}")
        
        # Complexity hotspots
        hotspots = insights.get('complexity_hotspots', [])
        if hotspots:
            console.print("\n🔥 [bold]Complexity Hotspots:[/bold]")
            for i, hotspot in enumerate(hotspots[:5], 1):  # Top 5
                console.print(f"  {i}. {hotspot['name']} ({hotspot['layer']})")
                console.print(f"     📁 {hotspot['path']}")
                console.print(f"     📊 Complexity: {hotspot['complexity']:.3f}")
        
        # Improvement suggestions
        suggestions = insights.get('improvement_suggestions', [])
        if suggestions:
            console.print("\n💡 [bold]Improvement Suggestions:[/bold]")
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"  {i}. {suggestion}")
    
    except Exception as e:
        console.print(f"❌ [bold red]Failed to get insights: {e}[/bold red]")
        # Suggest GitHub issue reporting
        import traceback
        suggest_github_issue(
            error_type=type(e).__name__,
            error_message=str(e),
            command=f"insights {path}",
            traceback=traceback.format_exc()
        )
        sys.exit(1)


@cli.command(name='enhanced')
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--layer', help='Filter by architectural layer (controller, service, model, etc.)')
@click.option('--domain', help='Filter by business domain (authentication, payment, etc.)')
@click.option('--criticality', help='Filter by criticality level (critical, important, normal, low)')
@click.option('--min-complexity', type=float, help='Filter by minimum complexity score (0.0-1.0)')
@click.option('--limit', type=int, default=20, help='Maximum number of results')
@click.option('--project', help='Project name/path (default: current directory)')
def query_enhanced(path, layer, domain, criticality, min_complexity, limit, project):
    """Query nodes with enhanced metadata and filters"""
    try:
        path = validate_file_path(path)
    except SecurityError as e:
        console.print(f"❌ [bold red]Security error: {e}[/bold red]")
        sys.exit(1)
    
    console.print(f"🔍 [bold blue]Querying enhanced nodes for: {path}[/bold blue]")
    
    try:
        _CodeGraphIndexer = get_code_graph_indexer()
        indexer = _CodeGraphIndexer(project_path=Path(path))
        
        nodes = indexer.query_enhanced_nodes(
            architectural_layer=layer,
            business_domain=domain,
            criticality_level=criticality,
            min_complexity=min_complexity,
            limit=limit
        )
        
        if not nodes:
            console.print("ℹ️ [yellow]No enhanced nodes found matching criteria. Run 'cci enhance' first.[/yellow]")
            return
        
        # Show filter info
        filters = []
        if layer:
            filters.append(f"Layer: {layer}")
        if domain:
            filters.append(f"Domain: {domain}")
        if criticality:
            filters.append(f"Criticality: {criticality}")
        if min_complexity:
            filters.append(f"Min Complexity: {min_complexity}")
        
        if filters:
            console.print(f"🎯 [cyan]Filters: {', '.join(filters)}[/cyan]")
        
        console.print(f"📊 Found {len(nodes)} nodes (limit: {limit})\n")
        
        # Create table
        table = Table(title="Enhanced Nodes")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Layer", style="green")
        table.add_column("Domain", style="blue")
        table.add_column("Criticality", style="red")
        table.add_column("Complexity", style="magenta")
        table.add_column("Importance", style="bright_white")
        
        for node in nodes:
            name = node['name'][:25] + "..." if len(node['name']) > 25 else node['name']
            node_type = node['node_type']
            layer = node.get('architectural_layer', 'unknown')
            domain = node.get('business_domain', 'general')
            criticality_val = node.get('criticality_level', 'normal')
            complexity = f"{node.get('complexity_score', 0):.3f}"
            importance = f"{node.get('importance_score', 0):.3f}"
            
            table.add_row(name, node_type, layer, domain, criticality_val, complexity, importance)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [bold red]Query failed: {e}[/bold red]")
        # Suggest GitHub issue reporting
        import traceback
        suggest_github_issue(
            error_type=type(e).__name__,
            error_message=str(e),
            command=f"enhanced {path}",
            traceback=traceback.format_exc()
        )
        sys.exit(1)


@cli.command(name='critical')
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--limit', type=int, default=15, help='Maximum number of components to show')
@click.option('--project', help='Project name/path (default: current directory)')
def get_critical_components(path, limit, project):
    """Get most critical components in the codebase"""
    try:
        path = validate_file_path(path)
    except SecurityError as e:
        console.print(f"❌ [bold red]Security error: {e}[/bold red]")
        sys.exit(1)
    
    console.print(f"⚠️ [bold blue]Getting critical components for: {path}[/bold blue]")
    
    try:
        _CodeGraphIndexer = get_code_graph_indexer()
        indexer = _CodeGraphIndexer(project_path=Path(path))
        critical_components = indexer.get_critical_components(limit=limit)
        
        if not critical_components:
            console.print("ℹ️ [yellow]No critical components found. Run 'cci enhance' first.[/yellow]")
            return
        
        console.print(f"\n⚠️ [bold red]Critical Components (Top {len(critical_components)}):[/bold red]\n")
        
        for i, comp in enumerate(critical_components, 1):
            console.print(f"{i}. [bold]{comp['name']}[/bold] ({comp['node_type']})")
            console.print(f"   📁 Path: {comp['path']}")
            console.print(f"   🏗️ Layer: {comp.get('architectural_layer', 'unknown')}")
            console.print(f"   🏢 Domain: {comp.get('business_domain', 'general')}")
            console.print(f"   📊 Complexity: {comp.get('complexity_score', 0):.3f}")
            console.print(f"   🎯 Importance: {comp.get('importance_score', 0):.3f}")
            console.print(f"   💥 Impact: {comp.get('dependencies_impact', 0):.3f}")
            
            # Role tags
            role_tags = comp.get('role_tags', [])
            if role_tags:
                console.print(f"   🏷️ Tags: {', '.join(role_tags)}")
            
            # LLM summary
            summary = comp.get('llm_summary', '')
            if summary:
                truncated = summary[:80] + "..." if len(summary) > 80 else summary
                console.print(f"   📝 Summary: {truncated}")
            
            console.print()
    
    except Exception as e:
        console.print(f"❌ [bold red]Failed to get critical components: {e}[/bold red]")
        # Suggest GitHub issue reporting
        import traceback
        suggest_github_issue(
            error_type=type(e).__name__,
            error_message=str(e),
            command=f"critical {path} --limit {limit}",
            traceback=traceback.format_exc()
        )
        sys.exit(1)


# Register god-mode command group
if god_mode_group is not None:
    cli.add_command(god_mode_group)

# Register migrate command
if migrate_command is not None:
    cli.add_command(migrate_command)

# Register crash management commands
if crash_group is not None:
    cli.add_command(crash_group)


@cli.command(name='llm-guide')
def llm_guide():
    """🤖 Guide for LLMs using claude-code-indexer (cci)
    
    Special command providing comprehensive usage instructions
    for AI assistants like Claude, ChatGPT, etc.
    """
    guide = """🤖 Claude Code Indexer - LLM Usage Guide

🌟 QUICK START for understanding any codebase:
1. cci index .          # Index the codebase (4-5s)
2. cci stats            # View overview (0.1s cached)
3. cci query --important # See key components
4. cci search <term>    # Find specific code

⚠️  SECURITY WARNINGS:
- NEVER use 'enhance' on code with secrets/API keys
- Check for .env files before indexing: find . -name "*.env"
- Safe for open source and development code

🚀 ADVANCED FEATURES:
1. LLM Enhancement (use carefully):
   cci enhance . --limit 5  # Test first!
   cci insights             # View AI analysis
   
2. Multi-keyword search:
   cci search auth user login  # OR search
   cci search db conn --mode all # AND search

3. Architecture analysis:
   cci enhanced --layer service
   cci critical --limit 10

🐛 ERROR REPORTING for LLMs:
If you encounter errors, create GitHub issue:

gh issue create --repo tuannx/claude-prompts \\
  --title "[Bug] Error description" \\
  --body "Error details..." \\
  --label bug,auto-reported

📊 PERFORMANCE:
- Fresh index: ~5s for 1000+ files
- Cached queries: ~0.1s (64x faster)
- Enhancement: ~1000 nodes/sec

🎯 BEST PRACTICES:
1. Always run 'index' first on new projects
2. Use 'stats' to verify indexing success
3. Start 'enhance' with --limit 5-10
4. Report issues to help improve the tool

📝 More info: https://github.com/tuannx/claude-prompts
"""
    console.print(guide)


# Add mcp-daemon command group
@cli.group(name='mcp-daemon')
def mcp_daemon():
    """Manage MCP persistent daemon for better performance"""
    pass


# Import daemon commands and register them
try:
    from .commands.mcp_daemon import start, stop, restart, status as daemon_status, logs, config as daemon_config
    
    mcp_daemon.add_command(start)
    mcp_daemon.add_command(stop)
    mcp_daemon.add_command(restart)
    mcp_daemon.add_command(daemon_status, name='status')
    mcp_daemon.add_command(logs)
    mcp_daemon.add_command(daemon_config, name='config')
except ImportError:
    pass  # MCP daemon commands not available


@cli.group()
def state():
    """Manage codebase state (single source of truth)."""
    pass

@state.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
def capture(project):
    """Capture current codebase state."""
    if CodebaseStateManager is None:
        click.secho("Error: State manager not available", fg="red")
        return
    
    project_path = project or os.getcwd()
    manager = CodebaseStateManager(project_path)
    state = manager.capture_state()
    
    console.print(Panel.fit(
        f"[green]✅ State captured[/green]\n\n"
        f"📁 Project: {state['project_path']}\n"
        f"🕐 Timestamp: {state['timestamp']}\n"
        f"📊 Files: {state['stats']['total_files']}\n"
        f"📝 Lines: {state['stats']['total_lines']:,}\n"
        f"🔀 Git: {state['git']['branch']} @ {(state['git']['commit'] or 'N/A')[:8]}",
        title="[bold cyan]Codebase State[/bold cyan]"
    ))

@state.command()
@click.option('--task', '-t', required=True, help='Task description')
@click.option('--project', '-p', help='Project path (default: current directory)')
def begin(task, project):
    """Begin tracking a new development task."""
    if CodebaseStateManager is None:
        click.secho("Error: State manager not available", fg="red")
        return
    
    project_path = project or os.getcwd()
    manager = CodebaseStateManager(project_path)
    task_id = manager.track_task({"description": task})
    
    console.print(Panel.fit(
        f"[green]✅ Task started[/green]\n\n"
        f"📋 ID: {task_id}\n"
        f"📝 Description: {task}\n"
        f"⏱️ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"[yellow]Remember to run '[bold]cci state complete --id {task_id}[/bold]' when done![/yellow]",
        title="[bold cyan]Task Tracking[/bold cyan]"
    ))

@state.command()
@click.option('--id', '-i', 'task_id', required=True, help='Task ID to complete')
@click.option('--project', '-p', help='Project path (default: current directory)')
def complete(task_id, project):
    """Mark task as complete and capture changes."""
    if CodebaseStateManager is None:
        click.secho("Error: State manager not available", fg="red")
        return
    
    project_path = project or os.getcwd()
    manager = CodebaseStateManager(project_path)
    
    try:
        changes = manager.complete_task(task_id)
        
        # Create summary table
        table = Table(title="Task Changes Summary")
        table.add_column("Change Type", style="cyan")
        table.add_column("Count", style="green")
        
        table.add_row("Files Added", str(len(changes.get('files_added', []))))
        table.add_row("Files Modified", str(len(changes.get('files_modified', []))))
        table.add_row("Files Removed", str(len(changes.get('files_removed', []))))
        
        console.print(table)
        console.print(f"\n[green]✅ Task {task_id} completed successfully![/green]")
        
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")

@state.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
@click.option('--format', '-f', type=click.Choice(['simple', 'detailed']), default='simple')
def diff(project, format):
    """Show differences from last captured state."""
    if CodebaseStateManager is None:
        click.secho("Error: State manager not available", fg="red")
        return
    
    project_path = project or os.getcwd()
    manager = CodebaseStateManager(project_path)
    diff_result = manager.diff_from_last()
    
    if not diff_result:
        console.print("[yellow]No previous state to compare with[/yellow]")
        return
    
    table = Table(title="State Differences")
    table.add_column("Change Type", style="cyan")
    table.add_column("Files", style="green")
    
    if diff_result['files_added']:
        table.add_row("Added", ", ".join(diff_result['files_added'][:5]))
    if diff_result['files_modified']:
        table.add_row("Modified", ", ".join(diff_result['files_modified'][:5]))
    if diff_result['files_removed']:
        table.add_row("Removed", ", ".join(diff_result['files_removed'][:5]))
    
    console.print(table)

@state.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
@click.option('--limit', '-l', default=10, help='Number of tasks to show')
def tasks(project, limit):
    """List recent tasks and their status."""
    if CodebaseStateManager is None:
        click.secho("Error: State manager not available", fg="red")
        return
    
    project_path = project or os.getcwd()
    manager = CodebaseStateManager(project_path)
    tasks = manager.get_task_history(limit)
    
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return
    
    table = Table(title="Recent Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")
    table.add_column("Created", style="yellow")
    
    for task in tasks:
        status_color = "green" if task['status'] == 'completed' else "yellow"
        table.add_row(
            task['id'],
            task['description'][:40] + ('...' if len(task['description']) > 40 else ''),
            f"[{status_color}]{task['status']}[/{status_color}]",
            task['created_at'][:19]
        )
    
    console.print(table)

@state.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
@click.option('--format', '-f', type=click.Choice(['json', 'summary']), default='summary')
def export(project, format):
    """Export current state in specified format."""
    if CodebaseStateManager is None:
        click.secho("Error: State manager not available", fg="red")
        return
    
    project_path = project or os.getcwd()
    manager = CodebaseStateManager(project_path)
    output = manager.export_state(format)
    
    if format == 'json':
        # Write to file
        filename = f"codebase_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            f.write(output)
        console.print(f"[green]✅ State exported to {filename}[/green]")
    else:
        console.print(output)

@state.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
def validate(project):
    """Validate current codebase state against saved state."""
    if CodebaseStateManager is None:
        click.secho("Error: State manager not available", fg="red")
        return
    
    project_path = project or os.getcwd()
    manager = CodebaseStateManager(project_path)
    validation = manager.validate_state()
    
    if validation['valid']:
        console.print("[green]✅ Codebase state is valid and consistent[/green]")
    else:
        console.print(f"[red]❌ State validation failed: {validation.get('reason', 'Unknown')}[/red]")
        if validation.get('unexpected_changes'):
            console.print("\n[yellow]Unexpected changes detected in:[/yellow]")
            for file in validation['unexpected_changes'][:10]:
                console.print(f"  - {file}")

@cli.command()
def doctor():
    """Diagnose import and installation issues"""
    show_app_header()
    console.print("🔍 Running diagnostics...\n")
    
    # Check Python version
    console.print(f"[bold]Python:[/bold] {sys.version}")
    console.print(f"[bold]Executable:[/bold] {sys.executable}\n")
    
    # Check critical imports
    modules = {
        'claude_code_indexer': ('✅', '❌', 'Main package'),
        'claude_code_indexer.indexer': ('✅', '❌', 'Indexer module'),
        'claude_code_indexer.parsers': ('✅', '❌', 'Parser module'),
        'click': ('✅', '❌', 'CLI framework'),
        'rich': ('✅', '⚠️', 'Terminal UI (optional)'),
        'networkx': ('✅', '⚠️', 'Graph library (optional)'),
        'ensmallen': ('✅', '⚠️', 'Graph processing (optional)'),
    }
    
    console.print("[bold]Import Status:[/bold]")
    all_critical_ok = True
    
    for module, (ok_icon, fail_icon, desc) in modules.items():
        try:
            __import__(module)
            console.print(f"  {ok_icon} {module} - {desc}")
        except ImportError as e:
            is_critical = fail_icon == '❌'
            console.print(f"  {fail_icon} {module} - {desc}")
            if is_critical:
                all_critical_ok = False
                console.print(f"     [red]Error: {e}[/red]")
    
    # Check working directory
    console.print(f"\n[bold]Working Directory:[/bold] {os.getcwd()}")
    
    # Recommendations
    console.print(f"\n[bold]Status:[/bold]")
    if all_critical_ok:
        console.print("  [green]✅ All critical imports successful[/green]")
    else:
        console.print("  [red]❌ Critical imports failed[/red]")
        console.print("\n[bold]Recommended Actions:[/bold]")
        console.print("  1. Reinstall: pip install -e .")
        console.print("  2. Check virtual environment")
        console.print("  3. Run from project root")
        console.print("  4. Try: python -m pip install --force-reinstall -e .")


def main():
    """Main CLI entry point with error handling and auto-repair"""
    # Ensure proper package setup for installed scripts
    import os
    if not __package__:
        # Running as a script, fix the package context
        file_path = os.path.abspath(__file__)
        if 'site-packages' in file_path:
            # Installed package
            sys.path.insert(0, os.path.dirname(os.path.dirname(file_path)))
    
    # Debug: Print import status
    if '--trace' in sys.argv:
        print(f"DEBUG: __package__ = {__package__}")
        print(f"DEBUG: __file__ = {__file__}")
        print(f"DEBUG: sys.path[0] = {sys.path[0]}")
        print(f"DEBUG: cli = {cli}")
        print(f"DEBUG: CodeGraphIndexer = {CodeGraphIndexer}")
        print(f"DEBUG: console = {console}")
        sys.argv.remove('--trace')
    
    # First, ensure we're in the right environment
    try:
        # Add project root to path if in development
        file_path = Path(__file__).resolve()
        project_root = file_path.parent.parent
        if (project_root / 'pyproject.toml').exists() and str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
    except:
        pass
    
    try:
        # Install crash handler if available
        if install_crash_handler:
            install_crash_handler()
        
        # Check for updates if available
        if check_and_notify_update:
            check_and_notify_update()
        
        # Ensure cli is not None
        if cli is None:
            raise ImportError("CLI module failed to initialize properly")
        
        cli()
    except ImportError as e:
        # Import error - try to fix
        print(f"\n{__app_name__} v{__version__}")
        print(f"Import error detected: {e}")
        
        if '--no-fix' not in sys.argv:
            print("\nAttempting auto-fix...")
            import subprocess
            try:
                # Try to reinstall
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-e', '.'])
                print("Fix successful! Please run the command again.")
            except:
                print("Auto-fix failed.")
                print("\nManual fix options:")
                print("  1. cd to project root and run: pip install -e .")
                print("  2. Or run: python -m claude_code_indexer.cli")
        
        sys.exit(1)
    except Exception as e:
        # Other errors
        print(f"\n{__app_name__} v{__version__}")
        print(f"Error: {e}")
        
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        
        print("\nFor help: python -m claude_code_indexer.cli doctor")
        sys.exit(1)


if __name__ == "__main__":
    main()