#!/usr/bin/env python3
"""
Crash Handler for Claude Code Indexer
Intercepts uncaught exceptions and helps users report crashes
"""

import sys
import traceback
import tempfile
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.text import Text

from .github_reporter import GitHubIssueReporter
from .logger import log_error, log_info
from . import __version__


console = Console()


class CrashHandler:
    """Handles application crashes and helps users report them"""
    
    def __init__(self):
        self.crash_dir = Path.home() / ".claude-code-indexer" / "crashes"
        self.crash_dir.mkdir(parents=True, exist_ok=True)
        self.reporter = GitHubIssueReporter()
        self._original_excepthook = sys.excepthook
        self._crash_id = None
        
    def save_crash_dump(self, exc_type, exc_value, exc_traceback) -> Path:
        """Save crash information to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._crash_id = f"crash_{timestamp}_{id(exc_value)}"
        crash_file = self.crash_dir / f"{self._crash_id}.json"
        
        # Get the full traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)
        
        # Get system info
        system_info = self.reporter.get_system_info()
        
        # Get command line args
        import sys
        command = ' '.join(sys.argv)
        
        crash_data = {
            "crash_id": self._crash_id,
            "timestamp": timestamp,
            "version": __version__,
            "error_type": exc_type.__name__,
            "error_message": str(exc_value),
            "traceback": tb_text,
            "command": command,
            "system_info": system_info,
        }
        
        # Save crash dump
        with open(crash_file, 'w') as f:
            json.dump(crash_data, f, indent=2)
            
        return crash_file
        
    def prompt_user_action(self, crash_data: Dict[str, Any]) -> bool:
        """Prompt user for action after crash"""
        console.print()
        console.print(Panel.fit(
            Text("💥 Application Crashed!", style="bold red"),
            subtitle=f"Crash ID: {crash_data['crash_id']}",
            border_style="red"
        ))
        
        console.print(f"\n[bold red]Error Type:[/bold red] {crash_data['error_type']}")
        console.print(f"[bold red]Error Message:[/bold red] {crash_data['error_message']}")
        console.print(f"\n[dim]A crash dump has been saved to:[/dim]")
        crash_file_path = self.crash_dir / f'{crash_data["crash_id"]}.json'
        console.print(f"[dim]{crash_file_path}[/dim]")
        
        # Show options
        console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
        console.print("1. [green]Create a GitHub issue[/green] (recommended)")
        console.print("2. [yellow]View crash details[/yellow]")
        console.print("3. [dim]Exit without reporting[/dim]")
        
        choice = Prompt.ask(
            "\nSelect an option",
            choices=["1", "2", "3"],
            default="1"
        )
        
        if choice == "2":
            # Show crash details
            console.print("\n[bold]Crash Details:[/bold]")
            console.print(Panel(crash_data['traceback'], title="Traceback", border_style="red"))
            
            # Ask again
            if Confirm.ask("\nWould you like to create a GitHub issue?", default=True):
                choice = "1"
            else:
                choice = "3"
                
        if choice == "1":
            return True
        return False
        
    def handle_crash(self, exc_type, exc_value, exc_traceback):
        """Main crash handler"""
        # Don't handle KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            self._original_excepthook(exc_type, exc_value, exc_traceback)
            return
            
        # Save crash dump
        try:
            crash_file = self.save_crash_dump(exc_type, exc_value, exc_traceback)
            
            # Load crash data
            with open(crash_file, 'r') as f:
                crash_data = json.load(f)
                
            # Check if we're in a terminal
            if sys.stdin.isatty() and sys.stdout.isatty():
                # Interactive mode - prompt user
                if self.prompt_user_action(crash_data):
                    self.create_github_issue(crash_data)
            else:
                # Non-interactive mode - just show error and suggestion
                console.print(f"\n[bold red]💥 CRASH DETECTED[/bold red]")
                console.print(f"Error: {exc_type.__name__}: {exc_value}")
                console.print(f"\nCrash dump saved to: {crash_file}")
                console.print("\nTo report this issue:")
                self.show_reporting_instructions(crash_data)
                
        except Exception as e:
            # If crash handler fails, fall back to default
            log_error(f"Crash handler failed: {e}")
            self._original_excepthook(exc_type, exc_value, exc_traceback)
            
    def create_github_issue(self, crash_data: Dict[str, Any]):
        """Create or suggest creating a GitHub issue"""
        console.print("\n[bold cyan]Creating GitHub Issue...[/bold cyan]")
        
        # Prepare issue content
        title = f"[Crash] {crash_data['error_type']}: {crash_data['error_message'][:50]}..."
        
        additional_info = f"""### Crash Information
- **Crash ID**: `{crash_data['crash_id']}`
- **Timestamp**: {crash_data['timestamp']}
- **Command**: `{crash_data['command']}`

### Crash Context
This crash was automatically detected and reported by the crash handler.
"""
        
        # Try to create issue
        success = self.reporter.report_issue(
            error_type=crash_data['error_type'],
            error_message=crash_data['error_message'],
            command=crash_data['command'],
            traceback=crash_data['traceback'],
            additional_info=additional_info,
            auto_create=False  # Always show instructions, don't auto-create
        )
        
        if not success:
            console.print("\n[yellow]💡 Tip:[/yellow] You can attach the crash dump file when creating the issue:")
            console.print(f"[dim]{self.crash_dir / f'{crash_data["crash_id"]}.json'}[/dim]")
            
    def show_reporting_instructions(self, crash_data: Dict[str, Any]):
        """Show instructions for reporting the crash"""
        if self.reporter.gh_available:
            console.print("\n[bold cyan]Using GitHub CLI:[/bold cyan]")
            title = f"[Crash] {crash_data['error_type']}: {crash_data['error_message'][:50]}..."
            console.print(f"gh issue create --repo tuannx/claude-prompts --title \"{title}\" --label bug,crash")
            
        console.print("\n[bold cyan]Or report manually:[/bold cyan]")
        console.print("https://github.com/tuannx/claude-prompts/issues/new")
        console.print(f"\n[dim]Include crash ID: {crash_data['crash_id']}[/dim]")
        
    def install(self):
        """Install the crash handler"""
        sys.excepthook = self.handle_crash
        log_info("Crash handler installed")
        
    def uninstall(self):
        """Uninstall the crash handler"""
        sys.excepthook = self._original_excepthook
        log_info("Crash handler uninstalled")


def install_crash_handler():
    """Convenience function to install crash handler"""
    handler = CrashHandler()
    handler.install()
    return handler