#!/usr/bin/env python3
"""
Security utilities for input validation and sanitization
"""

import os
import re
from pathlib import Path
from typing import Optional, List
import subprocess
import shlex


class SecurityError(Exception):
    """Security-related errors"""
    pass


def validate_file_path(path: str, base_dir: Optional[str] = None) -> str:
    """
    Validate and sanitize file path to prevent directory traversal attacks
    
    Args:
        path: The path to validate
        base_dir: Optional base directory to restrict access to
        
    Returns:
        Normalized absolute path
        
    Raises:
        SecurityError: If path is invalid or attempts directory traversal
    """
    if not path:
        raise SecurityError("Empty path provided")
    
    # Convert to Path object for proper handling
    try:
        path_obj = Path(path)
    except (ValueError, OSError) as e:
        raise SecurityError(f"Invalid path: {e}")
    
    # Check for null bytes
    if '\x00' in str(path):
        raise SecurityError("Path contains null bytes")
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'\.\./',  # Parent directory traversal
        r'\.\.\\',  # Windows parent directory
        r'^~',  # Home directory expansion
        r'^\$',  # Environment variable
        r'^/',  # Absolute path when base_dir is set
    ]
    
    path_str = str(path_obj)
    for pattern in suspicious_patterns:
        if re.search(pattern, path_str):
            # Allow absolute paths only if no base_dir restriction
            if pattern == r'^/' and base_dir is None:
                continue
            raise SecurityError(f"Suspicious path pattern detected: {pattern}")
    
    # Resolve to absolute path
    if base_dir:
        base_path = Path(base_dir).resolve()
        try:
            # Combine with base directory and resolve
            full_path = (base_path / path_obj).resolve()
            
            # Ensure the resolved path is within base directory
            if not str(full_path).startswith(str(base_path)):
                raise SecurityError(f"Path traversal detected: {path} escapes base directory")
                
            return str(full_path)
        except (ValueError, OSError) as e:
            raise SecurityError(f"Invalid path resolution: {e}")
    else:
        # Just resolve the path
        try:
            return str(path_obj.resolve())
        except (ValueError, OSError) as e:
            raise SecurityError(f"Invalid path resolution: {e}")


def validate_glob_pattern(pattern: str) -> str:
    """
    Validate glob pattern to ensure it's safe
    
    Args:
        pattern: Glob pattern to validate
        
    Returns:
        Validated pattern
        
    Raises:
        SecurityError: If pattern is invalid
    """
    if not pattern:
        raise SecurityError("Empty pattern provided")
    
    # Check for null bytes
    if '\x00' in pattern:
        raise SecurityError("Pattern contains null bytes")
    
    # Limit pattern length to prevent DoS
    if len(pattern) > 1000:
        raise SecurityError("Pattern too long (max 1000 characters)")
    
    # Check for excessive wildcards that could cause performance issues
    if pattern.count('*') > 10 or pattern.count('?') > 20:
        raise SecurityError("Pattern contains too many wildcards")
    
    return pattern


def sanitize_command_arg(arg: str) -> str:
    """
    Sanitize command line argument for subprocess
    
    Args:
        arg: Argument to sanitize
        
    Returns:
        Sanitized argument
        
    Raises:
        SecurityError: If argument is invalid
    """
    if not arg:
        return ""
    
    # Check for null bytes
    if '\x00' in arg:
        raise SecurityError("Argument contains null bytes")
    
    # Use shlex to properly quote the argument
    return shlex.quote(arg)


def validate_sql_identifier(identifier: str) -> str:
    """
    Validate SQL identifier (table/column name) to prevent SQL injection
    
    Args:
        identifier: SQL identifier to validate
        
    Returns:
        Validated identifier
        
    Raises:
        SecurityError: If identifier is invalid
    """
    if not identifier:
        raise SecurityError("Empty identifier provided")
    
    # Only allow alphanumeric, underscore, and dash
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', identifier):
        raise SecurityError(f"Invalid SQL identifier: {identifier}")
    
    # Check against SQL keywords (basic list)
    sql_keywords = {
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
        'ALTER', 'GRANT', 'REVOKE', 'UNION', 'WHERE', 'FROM'
    }
    
    if identifier.upper() in sql_keywords:
        raise SecurityError(f"SQL keyword used as identifier: {identifier}")
    
    return identifier


def safe_subprocess_run(cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Safely run subprocess with security checks
    
    Args:
        cmd: Command list to run
        **kwargs: Additional arguments for subprocess.run
        
    Returns:
        CompletedProcess instance
        
    Raises:
        SecurityError: If command is invalid
    """
    if not cmd:
        raise SecurityError("Empty command provided")
    
    # Validate each argument
    safe_cmd = []
    for arg in cmd:
        if not isinstance(arg, str):
            raise SecurityError(f"Non-string argument: {arg}")
        safe_cmd.append(sanitize_command_arg(arg))
    
    # Set safe defaults
    safe_kwargs = {
        'shell': False,  # Never use shell=True
        'capture_output': True,
        'text': True,
        'timeout': 30,  # Default timeout
    }
    
    # Override with user kwargs (except shell)
    for key, value in kwargs.items():
        if key == 'shell' and value:
            raise SecurityError("shell=True is not allowed for security reasons")
        safe_kwargs[key] = value
    
    return subprocess.run(safe_cmd, **safe_kwargs)


def validate_file_size(file_path: str, max_size_mb: int = 100) -> None:
    """
    Validate file size to prevent resource exhaustion
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum allowed size in MB
        
    Raises:
        SecurityError: If file is too large
    """
    try:
        size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if size > max_size_bytes:
            raise SecurityError(
                f"File too large: {size / 1024 / 1024:.1f}MB "
                f"(max {max_size_mb}MB)"
            )
    except OSError as e:
        raise SecurityError(f"Cannot check file size: {e}")