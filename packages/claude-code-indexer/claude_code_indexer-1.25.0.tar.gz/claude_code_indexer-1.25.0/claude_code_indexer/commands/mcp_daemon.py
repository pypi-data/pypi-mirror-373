"""
MCP Daemon management commands
"""

import click
import os
import sys
import json
import psutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional

from ..storage_manager import get_storage_manager


def get_daemon_pid_file() -> Path:
    """Get daemon PID file path"""
    storage = get_storage_manager()
    return storage.app_home / "mcp_daemon.pid"


def get_daemon_log_file() -> Path:
    """Get daemon log file path"""
    storage = get_storage_manager()
    return storage.app_home / "mcp_daemon.log"


def is_daemon_running() -> Optional[int]:
    """Check if daemon is running, return PID if running"""
    pid_file = get_daemon_pid_file()
    
    if not pid_file.exists():
        return None
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        if psutil.pid_exists(pid):
            try:
                proc = psutil.Process(pid)
                # Check if it's our process
                if 'mcp_persistent_server' in ' '.join(proc.cmdline()):
                    return pid
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
    except (ValueError, IOError):
        pass
    
    # Clean up stale PID file
    if pid_file.exists():
        pid_file.unlink()
    
    return None


@click.group(name='mcp-daemon')
def mcp_daemon():
    """Manage MCP persistent daemon for better performance"""
    pass


@mcp_daemon.command()
@click.option('--port', default=8765, help='Port to run server on')
@click.option('--protocol', type=click.Choice(['websocket', 'http']), default='websocket',
              help='Protocol to use')
def start(port: int, protocol: str):
    """Start MCP persistent daemon"""
    
    # Check if already running
    pid = is_daemon_running()
    if pid:
        click.echo(f"❌ MCP daemon is already running (PID: {pid})")
        return
    
    # Start daemon
    log_file = get_daemon_log_file()
    pid_file = get_daemon_pid_file()
    
    # Create command
    cmd = [
        sys.executable,
        '-m', 'claude_code_indexer.mcp_persistent_server',
        '--port', str(port),
        '--protocol', protocol
    ]
    
    # Start process in background
    with open(log_file, 'w') as log:
        process = subprocess.Popen(
            cmd,
            stdout=log,
            stderr=log,
            start_new_session=True
        )
    
    # Save PID
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))
    
    # Wait a moment to check if it started successfully
    time.sleep(1)
    
    if is_daemon_running():
        click.echo(f"✅ MCP daemon started on {protocol}://127.0.0.1:{port} (PID: {process.pid})")
        click.echo(f"📝 Logs: {log_file}")
    else:
        click.echo("❌ Failed to start MCP daemon. Check logs for details.")
        if log_file.exists():
            with open(log_file, 'r') as f:
                click.echo(f.read())


@mcp_daemon.command()
def stop():
    """Stop MCP persistent daemon"""
    
    pid = is_daemon_running()
    if not pid:
        click.echo("❌ MCP daemon is not running")
        return
    
    try:
        # Send SIGTERM
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to stop
        for _ in range(10):
            if not is_daemon_running():
                break
            time.sleep(0.5)
        
        # Force kill if still running
        if is_daemon_running():
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
        
        # Clean up PID file
        pid_file = get_daemon_pid_file()
        if pid_file.exists():
            pid_file.unlink()
        
        click.echo("✅ MCP daemon stopped")
        
    except Exception as e:
        click.echo(f"❌ Error stopping daemon: {e}")


@mcp_daemon.command()
def restart():
    """Restart MCP persistent daemon"""
    
    # Stop if running
    if is_daemon_running():
        click.echo("Stopping existing daemon...")
        ctx = click.get_current_context()
        ctx.invoke(stop)
        time.sleep(1)
    
    # Start new instance
    click.echo("Starting new daemon...")
    ctx = click.get_current_context()
    ctx.invoke(start)


@mcp_daemon.command()
def status():
    """Check MCP daemon status"""
    
    pid = is_daemon_running()
    
    if pid:
        try:
            proc = psutil.Process(pid)
            create_time = proc.create_time()
            uptime = time.time() - create_time
            
            # Format uptime
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            
            click.echo(f"✅ MCP daemon is running")
            click.echo(f"   PID: {pid}")
            click.echo(f"   Uptime: {hours}h {minutes}m {seconds}s")
            click.echo(f"   Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
            click.echo(f"   CPU: {proc.cpu_percent(interval=0.1):.1f}%")
            
        except Exception as e:
            click.echo(f"✅ MCP daemon is running (PID: {pid})")
    else:
        click.echo("❌ MCP daemon is not running")
    
    # Show log file info
    log_file = get_daemon_log_file()
    if log_file.exists():
        size = log_file.stat().st_size / 1024
        click.echo(f"\n📝 Log file: {log_file} ({size:.1f} KB)")


@mcp_daemon.command()
def logs():
    """Show MCP daemon logs"""
    
    log_file = get_daemon_log_file()
    
    if not log_file.exists():
        click.echo("❌ No log file found")
        return
    
    # Show last 50 lines
    with open(log_file, 'r') as f:
        lines = f.readlines()
        last_lines = lines[-50:] if len(lines) > 50 else lines
        
        click.echo("📝 MCP Daemon Logs (last 50 lines):")
        click.echo("-" * 60)
        for line in last_lines:
            click.echo(line.rstrip())


@mcp_daemon.command()
@click.pass_context
def config(ctx):
    """Generate Claude Desktop config for persistent MCP"""
    
    # Check if daemon is running
    if not is_daemon_running():
        click.echo("⚠️  MCP daemon is not running. Starting it now...")
        ctx.invoke(start)
    
    config = {
        "mcpServers": {
            "claude-code-indexer": {
                "command": sys.executable,
                "args": [
                    "-m", "claude_code_indexer.mcp_proxy"
                ],
                "env": {
                    "MCP_SERVER_URL": "ws://127.0.0.1:8765"
                }
            }
        }
    }
    
    click.echo("\n📋 Add this to your Claude Desktop config:")
    click.echo("-" * 60)
    click.echo(json.dumps(config, indent=2))
    click.echo("-" * 60)
    click.echo("\n✅ This config uses the persistent daemon for better performance!")