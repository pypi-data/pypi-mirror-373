#!/usr/bin/env python3
"""
Crash management commands for Claude Code Indexer
"""

import click
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from ..crash_handler import CrashHandler
from ..github_reporter import GitHubIssueReporter


console = Console()


@click.group()
def crash():
    """Manage crash reports and recovery"""
    pass


@crash.command()
@click.option('--all', 'show_all', is_flag=True, help='Show all crash reports')
@click.option('--last', 'last_n', type=int, default=5, help='Show last N crashes')
def list(show_all, last_n):
    """List recent crash reports
    
    Shows crash reports stored locally with options to view details
    or create GitHub issues for unresolved crashes.
    """
    handler = CrashHandler()
    crash_files = sorted(handler.crash_dir.glob("crash_*.json"), reverse=True)
    
    if not crash_files:
        console.print("[green]✓ No crash reports found![/green]")
        return
        
    # Limit number of crashes shown
    if not show_all:
        crash_files = crash_files[:last_n]
        
    # Create table
    table = Table(title="Crash Reports", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Date/Time", style="dim")
    table.add_column("Error Type", style="red")
    table.add_column("Message", style="yellow")
    table.add_column("Command")
    
    crashes = []
    for crash_file in crash_files:
        try:
            with open(crash_file, 'r') as f:
                crash_data = json.load(f)
                crashes.append((crash_file, crash_data))
                
                # Format timestamp
                timestamp = crash_data.get('timestamp', 'Unknown')
                if timestamp != 'Unknown':
                    try:
                        dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                        
                # Truncate message
                message = crash_data.get('error_message', 'Unknown')
                if len(message) > 40:
                    message = message[:37] + "..."
                    
                # Truncate command
                command = crash_data.get('command', 'Unknown')
                if len(command) > 30:
                    command = "..." + command[-27:]
                    
                table.add_row(
                    crash_data.get('crash_id', crash_file.stem)[:20],
                    timestamp,
                    crash_data.get('error_type', 'Unknown'),
                    message,
                    command
                )
        except Exception as e:
            console.print(f"[red]Error reading {crash_file}: {e}[/red]")
            
    console.print(table)
    
    if crashes:
        console.print(f"\n[dim]Showing {len(crashes)} of {len(list(handler.crash_dir.glob('crash_*.json')))} total crashes[/dim]")
        console.print("\nUse 'claude-code-indexer crash show <ID>' to view details")
        console.print("Use 'claude-code-indexer crash report <ID>' to create GitHub issue")


@crash.command()
@click.argument('crash_id')
def show(crash_id):
    """Show details of a specific crash report"""
    handler = CrashHandler()
    
    # Find crash file
    crash_file = None
    for f in handler.crash_dir.glob("crash_*.json"):
        if crash_id in f.stem:
            crash_file = f
            break
            
    if not crash_file:
        console.print(f"[red]Crash report '{crash_id}' not found[/red]")
        return
        
    try:
        with open(crash_file, 'r') as f:
            crash_data = json.load(f)
            
        # Display crash details
        console.print(Panel.fit(
            f"[bold]Crash Report: {crash_data['crash_id']}[/bold]",
            border_style="red"
        ))
        
        console.print(f"\n[bold]Error Type:[/bold] [red]{crash_data['error_type']}[/red]")
        console.print(f"[bold]Error Message:[/bold] {crash_data['error_message']}")
        console.print(f"[bold]Command:[/bold] {crash_data['command']}")
        console.print(f"[bold]Timestamp:[/bold] {crash_data['timestamp']}")
        console.print(f"[bold]Version:[/bold] {crash_data['version']}")
        
        # System info
        console.print("\n[bold]System Information:[/bold]")
        for key, value in crash_data.get('system_info', {}).items():
            console.print(f"  {key}: {value}")
            
        # Traceback
        console.print("\n[bold]Traceback:[/bold]")
        console.print(Panel(crash_data['traceback'], border_style="red"))
        
        # Options
        if Confirm.ask("\nWould you like to create a GitHub issue for this crash?", default=True):
            reporter = GitHubIssueReporter()
            handler.create_github_issue(crash_data)
            
    except Exception as e:
        console.print(f"[red]Error reading crash report: {e}[/red]")


@crash.command()
@click.argument('crash_id')
def report(crash_id):
    """Create a GitHub issue for a crash report"""
    handler = CrashHandler()
    
    # Find crash file
    crash_file = None
    for f in handler.crash_dir.glob("crash_*.json"):
        if crash_id in f.stem:
            crash_file = f
            break
            
    if not crash_file:
        console.print(f"[red]Crash report '{crash_id}' not found[/red]")
        return
        
    try:
        with open(crash_file, 'r') as f:
            crash_data = json.load(f)
            
        handler.create_github_issue(crash_data)
        
    except Exception as e:
        console.print(f"[red]Error creating issue: {e}[/red]")


@crash.command()
@click.option('--all', is_flag=True, help='Delete all crash reports')
@click.option('--older-than', type=int, help='Delete crashes older than N days')
def clean(all, older_than):
    """Clean up old crash reports"""
    handler = CrashHandler()
    crash_files = list(handler.crash_dir.glob("crash_*.json"))
    
    if not crash_files:
        console.print("[green]✓ No crash reports to clean[/green]")
        return
        
    if all:
        if Confirm.ask(f"Delete all {len(crash_files)} crash reports?", default=False):
            for f in crash_files:
                f.unlink()
            console.print(f"[green]✓ Deleted {len(crash_files)} crash reports[/green]")
    elif older_than:
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=older_than)
        deleted = 0
        
        for crash_file in crash_files:
            try:
                # Extract timestamp from filename
                timestamp_str = crash_file.stem.split('_')[1] + '_' + crash_file.stem.split('_')[2]
                file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if file_time < cutoff:
                    crash_file.unlink()
                    deleted += 1
            except:
                pass
                
        console.print(f"[green]✓ Deleted {deleted} crash reports older than {older_than} days[/green]")
    else:
        console.print("[yellow]Please specify --all or --older-than[/yellow]")


@crash.command()
def recover():
    """Check for crash recovery options
    
    Helps recover from recent crashes by checking for incomplete
    operations and suggesting recovery actions.
    """
    handler = CrashHandler()
    crash_files = sorted(handler.crash_dir.glob("crash_*.json"), reverse=True)
    
    if not crash_files:
        console.print("[green]✓ No recent crashes detected[/green]")
        return
        
    # Check most recent crash
    with open(crash_files[0], 'r') as f:
        crash_data = json.load(f)
        
    console.print(Panel.fit(
        f"[bold yellow]Recent Crash Detected[/bold yellow]\n"
        f"Crash ID: {crash_data['crash_id']}",
        border_style="yellow"
    ))
    
    console.print(f"\n[bold]Last Command:[/bold] {crash_data['command']}")
    console.print(f"[bold]Error:[/bold] {crash_data['error_type']}: {crash_data['error_message']}")
    
    # Suggest recovery based on command
    command_parts = crash_data['command'].split()
    if 'index' in command_parts:
        console.print("\n[bold cyan]Recovery Suggestion:[/bold cyan]")
        console.print("The indexing process may have been interrupted.")
        console.print("You can try running the command again:")
        console.print(f"\n  [green]{crash_data['command']}[/green]")
        console.print("\nThe indexer will resume from where it left off.")
    elif 'enhance' in command_parts:
        console.print("\n[bold cyan]Recovery Suggestion:[/bold cyan]")
        console.print("The enhancement process was interrupted.")
        console.print("Your database should still be intact.")
        console.print("You can safely re-run the enhance command.")
    else:
        console.print("\n[bold cyan]Recovery Suggestion:[/bold cyan]")
        console.print("You can try running the command again.")
        console.print("If the error persists, please create a GitHub issue.")
        
    console.print("\n[dim]Run 'claude-code-indexer crash show {crash_id}' for full details[/dim]")
    
    if Confirm.ask("\nWould you like to report this crash?", default=True):
        handler.create_github_issue(crash_data)