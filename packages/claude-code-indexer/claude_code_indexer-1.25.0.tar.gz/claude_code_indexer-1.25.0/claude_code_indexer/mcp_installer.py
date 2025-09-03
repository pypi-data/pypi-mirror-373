#!/usr/bin/env python3
"""
MCP Installation Helper for Claude Desktop and Claude Code
Automatically configures Claude Desktop/Code to use claude-code-indexer
"""

import json
import os
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

console = Console()


class MCPInstaller:
    """Handle MCP installation for Claude Desktop and Claude Code"""
    
    def __init__(self):
        self.platform = platform.system()
        self.desktop_config_path = self._get_desktop_config_path()
        self.code_config_path = self._get_code_config_path()
        # Default to desktop config for backward compatibility
        self.config_path = self.desktop_config_path
        
    def _get_desktop_config_path(self) -> Optional[Path]:
        """Get Claude Desktop config path based on platform"""
        if self.platform == "Darwin":  # macOS
            return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        elif self.platform == "Windows":
            return Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
        elif self.platform == "Linux":
            return Path.home() / ".config/Claude/claude_desktop_config.json"
        else:
            return None
    
    def _get_code_config_path(self) -> Optional[Path]:
        """Get Claude Code config path based on platform"""
        if self.platform == "Darwin":  # macOS
            return Path.home() / "Library/Application Support/Claude Code/claude_desktop_config.json"
        elif self.platform == "Windows":
            return Path.home() / "AppData/Roaming/Claude Code/claude_desktop_config.json"
        elif self.platform == "Linux":
            return Path.home() / ".config/Claude Code/claude_desktop_config.json"
        else:
            return None
    
    def check_claude_desktop(self) -> bool:
        """Check if Claude Desktop is installed"""
        if not self.desktop_config_path:
            return False
            
        # Check if Claude Desktop directory exists
        claude_dir = self.desktop_config_path.parent
        return claude_dir.exists()
    
    def check_claude_code(self) -> bool:
        """Check if Claude Code is installed"""
        if not self.code_config_path:
            return False
            
        # Check if Claude Code directory exists
        claude_code_dir = self.code_config_path.parent
        return claude_code_dir.exists()
    
    def detect_claude_app(self) -> str:
        """Detect which Claude app is installed"""
        has_desktop = self.check_claude_desktop()
        has_code = self.check_claude_code()
        
        if has_code:
            self.config_path = self.code_config_path
            return "code"
        elif has_desktop:
            self.config_path = self.desktop_config_path
            return "desktop"
        else:
            return "none"
    
    def load_config(self) -> Dict[str, Any]:
        """Load existing Claude Desktop config"""
        if not self.config_path or not self.config_path.exists():
            return {"mcpServers": {}}
            
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"mcpServers": {}}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save Claude Desktop config"""
        if not self.config_path:
            return False
            
        # Create directory if needed
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix('.json.backup')
            shutil.copy2(self.config_path, backup_path)
            console.print(f"💾 Backed up existing config to: {backup_path}")
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except IOError as e:
            console.print(f"[red]❌ Failed to save config: {e}[/red]")
            return False
    
    def install(self, force: bool = False) -> bool:
        """Install MCP server configuration"""
        # Detect which Claude app is installed
        app_type = self.detect_claude_app()
        
        if app_type == "none":
            console.print("[red]❌ Neither Claude Desktop nor Claude Code found[/red]")
            if self.desktop_config_path:
                console.print(f"Expected Claude Desktop at: {self.desktop_config_path.parent}")
            if self.code_config_path:
                console.print(f"Expected Claude Code at: {self.code_config_path.parent}")
            if not force and not Confirm.ask("Continue anyway?"):
                return False
        else:
            app_name = "Claude Code" if app_type == "code" else "Claude Desktop"
            console.print(f"[green]✅ Found {app_name}[/green]")
        
        # Load existing config
        config = self.load_config()
        
        # Check if already installed
        if "claude-code-indexer" in config.get("mcpServers", {}):
            console.print("[yellow]⚠️  claude-code-indexer MCP server already configured[/yellow]")
            if not force and not Confirm.ask("Update existing configuration?"):
                return False
        
        # Add our MCP server
        if "mcpServers" not in config:
            config["mcpServers"] = {}
            
        # Use Python to run the MCP proxy which auto-starts daemon
        import sys
        config["mcpServers"]["claude-code-indexer"] = {
            "command": sys.executable,
            "args": ["-m", "claude_code_indexer.mcp_proxy"],
            "env": {
                "MCP_SERVER_URL": "ws://127.0.0.1:8765",
                "PYTHONPATH": str(Path(sys.executable).parent.parent / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages")
            },
            "autoStart": True,
            "capabilities": {
                "tools": True,
                "resources": True
            }
        }
        
        # Save config
        if self.save_config(config):
            app_name = "Claude Code" if app_type == "code" else "Claude Desktop"
            console.print(f"[green]✅ MCP server configured successfully for {app_name}![/green]")
            console.print(f"📁 Config location: {self.config_path}")
            
            console.print("\n[bold cyan]🚀 NEW: Persistent Daemon Mode[/bold cyan]")
            console.print("• MCP daemon will auto-start when needed")
            console.print("• 10x faster responses after first use")
            console.print("• No manual setup required!")
            
            console.print(f"\n[yellow]⚠️  Please restart {app_name} for changes to take effect[/yellow]")
            return True
        else:
            return False
    
    def uninstall(self) -> bool:
        """Remove MCP server configuration"""
        # Detect which app is installed to use the right config path
        app_type = self.detect_claude_app()
        
        if not self.config_path or not self.config_path.exists():
            console.print("[yellow]No configuration found[/yellow]")
            return True
            
        config = self.load_config()
        
        if "claude-code-indexer" not in config.get("mcpServers", {}):
            console.print("[yellow]claude-code-indexer not found in config[/yellow]")
            return True
        
        # Remove our server
        del config["mcpServers"]["claude-code-indexer"]
        
        # Save config
        if self.save_config(config):
            console.print("[green]✅ MCP server removed successfully[/green]")
            return True
        else:
            return False
    
    def status(self) -> None:
        """Show MCP installation status"""
        table = Table(title="MCP Installation Status")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")
        
        # Platform check
        platform_supported = self.desktop_config_path is not None or self.code_config_path is not None
        table.add_row(
            "Platform",
            "✅ Supported" if platform_supported else "❌ Not Supported",
            self.platform
        )
        
        # Claude Desktop check
        desktop_installed = self.check_claude_desktop()
        table.add_row(
            "Claude Desktop",
            "✅ Found" if desktop_installed else "❌ Not Found",
            str(self.desktop_config_path.parent) if self.desktop_config_path else "N/A"
        )
        
        # Claude Code check
        code_installed = self.check_claude_code()
        table.add_row(
            "Claude Code",
            "✅ Found" if code_installed else "❌ Not Found",
            str(self.code_config_path.parent) if self.code_config_path else "N/A"
        )
        
        # Config check
        config_exists = self.config_path and self.config_path.exists()
        table.add_row(
            "Config File",
            "✅ Exists" if config_exists else "❌ Not Found",
            str(self.config_path) if self.config_path else "N/A"
        )
        
        # MCP server check
        if config_exists:
            config = self.load_config()
            mcp_configured = "claude-code-indexer" in config.get("mcpServers", {})
            if mcp_configured:
                server_config = config["mcpServers"]["claude-code-indexer"]
                uses_daemon = "mcp_proxy" in str(server_config.get("args", []))
                mode = "Persistent Daemon" if uses_daemon else "Legacy Mode"
                table.add_row(
                    "MCP Server",
                    "✅ Configured",
                    mode
                )
            else:
                table.add_row(
                    "MCP Server",
                    "❌ Not Configured",
                    "Not installed"
                )
        else:
            table.add_row("MCP Server", "❌ Not Configured", "Config not found")
        
        # Daemon status check
        try:
            from .commands.mcp_daemon import is_daemon_running
            daemon_pid = is_daemon_running()
            if daemon_pid:
                table.add_row(
                    "MCP Daemon",
                    "✅ Running",
                    f"PID: {daemon_pid}"
                )
            else:
                table.add_row(
                    "MCP Daemon",
                    "⏸️  Not Running",
                    "Will auto-start when needed"
                )
        except:
            pass
        
        console.print(table)
        
        # Show instructions if not fully configured
        if not platform_supported:
            console.print("\n[yellow]Your platform is not supported for automatic installation.[/yellow]")
            console.print("Please manually configure Claude Desktop or Claude Code.")
        elif not desktop_installed and not code_installed:
            console.print("\n[yellow]Neither Claude Desktop nor Claude Code found. Please install one:[/yellow]")
            console.print("Claude Desktop: https://claude.ai/desktop")
            console.print("Claude Code: https://www.anthropic.com/news/claude-code")
        elif not config_exists or not mcp_configured:
            console.print("\n[cyan]To install MCP server:[/cyan]")
            console.print("claude-code-indexer mcp install")


def install_mcp(force: bool = False) -> None:
    """Install MCP server for Claude Desktop/Code"""
    installer = MCPInstaller()
    
    console.print("[bold cyan]🤖 Claude Code Indexer MCP Installer[/bold cyan]\n")
    
    # Check if MCP dependencies are installed
    try:
        import mcp
        console.print("✅ MCP SDK is installed")
    except ImportError:
        console.print("[red]❌ MCP SDK not installed[/red]")
        console.print("\nInstall with: pip install 'claude-code-indexer[mcp]'")
        return
    
    # Run installation
    if installer.install(force=force):
        console.print("\n[green]🎉 Installation complete![/green]")
        console.print("\nNext steps:")
        app_type = installer.detect_claude_app()
        app_name = "Claude Code" if app_type == "code" else "Claude Desktop"
        console.print(f"1. Restart {app_name}")
        console.print("2. Open a Python project")
        console.print("3. Claude will have access to code indexing tools automatically!")
    else:
        console.print("\n[red]Installation failed[/red]")


def uninstall_mcp() -> None:
    """Uninstall MCP server from Claude Desktop/Code"""
    installer = MCPInstaller()
    
    console.print("[bold cyan]🤖 Claude Code Indexer MCP Uninstaller[/bold cyan]\n")
    
    app_type = installer.detect_claude_app()
    app_name = "Claude Code" if app_type == "code" else "Claude Desktop" if app_type == "desktop" else "Claude"
    
    if Confirm.ask(f"Remove claude-code-indexer from {app_name}?"):
        if installer.uninstall():
            console.print("\n[green]Successfully removed![/green]")
        else:
            console.print("\n[red]Uninstall failed[/red]")


def show_mcp_status() -> None:
    """Show MCP installation status"""
    installer = MCPInstaller()
    installer.status()


if __name__ == "__main__":
    # Test the installer
    show_mcp_status()