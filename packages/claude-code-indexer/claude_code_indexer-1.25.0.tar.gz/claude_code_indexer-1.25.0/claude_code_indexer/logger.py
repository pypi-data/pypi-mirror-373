#!/usr/bin/env python3
"""
Logging utilities for Claude Code Indexer
Handles output to stderr for MCP server compatibility
"""

import sys
import os


def is_mcp_server():
    """Check if running as MCP server"""
    # Check if module was called from mcp_server
    import inspect
    stack = inspect.stack()
    for frame in stack:
        if 'mcp_server' in frame.filename:
            return True
    # Also check environment variable
    return os.environ.get('MCP_SERVER_MODE') == '1'


def log_info(message: str):
    """Log info message (to stderr if MCP server, stdout otherwise)"""
    if is_mcp_server():
        print(message, file=sys.stderr)
    else:
        print(message)


def log_warning(message: str):
    """Log warning message (always to stderr)"""
    print(f"Warning: {message}", file=sys.stderr)


def log_error(message: str):
    """Log error message (always to stderr)"""
    print(f"Error: {message}", file=sys.stderr)


def log_debug(message: str):
    """Log debug message (to stderr if MCP server)"""
    if is_mcp_server():
        print(f"Debug: {message}", file=sys.stderr)