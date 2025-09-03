#!/usr/bin/env python3
"""
Auto-update functionality for Claude Code Indexer
"""

import requests
import json
import subprocess
import sys
from pathlib import Path
from packaging import version
from rich.console import Console

from . import __version__
from .security import safe_subprocess_run, SecurityError

console = Console()


class Updater:
    """Handle package updates and CLAUDE.md synchronization"""
    
    PYPI_URL = "https://pypi.org/pypi/claude-code-indexer/json"
    
    def __init__(self):
        self.current_version = __version__
        
    def check_for_updates(self) -> tuple[bool, str]:
        """Check if a newer version is available on PyPI"""
        try:
            response = requests.get(self.PYPI_URL, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            latest_version = data["info"]["version"]
            
            if version.parse(latest_version) > version.parse(self.current_version):
                return True, latest_version
            
            return False, latest_version
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not check for updates: {e}[/yellow]")
            return False, self.current_version
    
    def update_package(self) -> bool:
        """Update the package using pip"""
        try:
            console.print("📦 [bold blue]Updating claude-code-indexer...[/bold blue]")
            
            # Use --upgrade flag to ensure we get the latest version
            # Use safe_subprocess_run for security
            result = safe_subprocess_run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "claude-code-indexer"],
                timeout=60  # Allow more time for pip install
            )
            
            if result.returncode == 0:
                console.print("✅ [bold green]Package updated successfully![/bold green]")
                return True
            else:
                console.print(f"❌ [bold red]Update failed: {result.stderr}[/bold red]")
                return False
                
        except SecurityError as e:
            console.print(f"❌ [bold red]Security error: {e}[/bold red]")
            return False
        except Exception as e:
            console.print(f"❌ [bold red]Update error: {e}[/bold red]")
            return False
    
    def sync_claude_md(self, force: bool = False) -> bool:
        """Update CLAUDE.md with latest template if needed"""
        claude_md_path = Path.cwd() / "CLAUDE.md"
        
        if not claude_md_path.exists() and not force:
            return False
        
        # Read template
        template_path = Path(__file__).parent / "templates" / "claude_md_template.md"
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        if claude_md_path.exists():
            # Read existing content
            with open(claude_md_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Check if our section exists
            section_marker = "## Code Indexing with Graph Database"
            
            if section_marker in existing_content:
                # Extract everything before our section
                lines = existing_content.split('\n')
                new_lines = []
                skip_section = False
                
                for line in lines:
                    if line.strip() == section_marker:
                        skip_section = True
                        continue
                    elif skip_section and line.startswith("## ") and "Code Indexing" not in line:
                        skip_section = False
                        new_lines.append(line)
                    elif not skip_section:
                        new_lines.append(line)
                
                # Rebuild content with updated section
                base_content = '\n'.join(new_lines).rstrip()
                updated_content = base_content + '\n\n' + template_content
                
                # Check if content changed
                if updated_content != existing_content:
                    with open(claude_md_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    console.print("✅ Updated CLAUDE.md with latest instructions")
                    return True
                else:
                    console.print("✓ CLAUDE.md already up to date")
                    return False
            else:
                # Append our section
                updated_content = existing_content.rstrip() + '\n\n' + template_content
                with open(claude_md_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                console.print("✅ Added code indexing section to CLAUDE.md")
                return True
        else:
            # Create new file
            with open(claude_md_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            console.print("✅ Created new CLAUDE.md with code indexing instructions")
            return True
    
    def auto_update(self, check_only: bool = False) -> bool:
        """Check and optionally perform auto-update"""
        has_update, latest_version = self.check_for_updates()
        
        if has_update:
            console.print(f"🆕 [bold]New version available: {latest_version} (current: {self.current_version})[/bold]")
            
            if check_only:
                console.print("Run [bold]claude-code-indexer update[/bold] to install")
                return False
            else:
                return self.update_package()
        else:
            console.print(f"✓ You're running the latest version ({self.current_version})")
            return False


def check_and_notify_update():
    """Check for updates and notify user (non-blocking)"""
    try:
        updater = Updater()
        has_update, latest_version = updater.check_for_updates()
        
        if has_update:
            console.print(f"\n💡 [yellow]Update available: {latest_version} (current: {updater.current_version})[/yellow]")
            console.print("   Run [bold]claude-code-indexer update[/bold] to upgrade\n")
    except:
        # Silently fail - don't interrupt user's workflow
        pass