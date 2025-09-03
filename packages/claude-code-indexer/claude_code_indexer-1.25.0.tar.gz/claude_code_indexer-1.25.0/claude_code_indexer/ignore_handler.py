#!/usr/bin/env python3
"""
Handle ignore patterns from .gitignore, .dockerignore and custom patterns
"""

import os
from pathlib import Path
from typing import List, Set, Optional
import fnmatch
import re


class IgnoreHandler:
    """Handle file ignore patterns from various sources"""
    
    # Default patterns to always ignore
    DEFAULT_IGNORE_PATTERNS = [
        # Version control
        '.git/', '.svn/', '.hg/', '.bzr/',
        
        # Dependencies
        'node_modules/', 'bower_components/', 'jspm_packages/',
        'vendor/', 'packages/', '.npm/', '.yarn/',
        
        # Python
        '__pycache__/', '*.pyc', '*.pyo', '*.pyd', '.Python',
        'pip-log.txt', 'pip-delete-this-directory.txt',
        '.tox/', '.nox/', '.coverage', '.coverage.*',
        '.pytest_cache/', '.mypy_cache/', '.hypothesis/',
        'venv/', 'env/', 'ENV/', '.venv/', '.env/',
        
        # Build outputs
        'build/', 'dist/', 'out/', 'target/', '*.egg-info/',
        '.eggs/', '*.egg', '*.whl',
        
        # IDE
        '.idea/', '.vscode/', '*.swp', '*.swo', '*~',
        '.project', '.classpath', '.settings/',
        
        # OS
        '.DS_Store', 'Thumbs.db', 'desktop.ini',
        
        # Logs and databases
        '*.log', '*.sqlite', '*.db',
        'logs/', 'tmp/', 'temp/',
        
        # Archives
        '*.zip', '*.tar', '*.tar.gz', '*.rar', '*.7z',
        
        # Media files (usually not code)
        '*.jpg', '*.jpeg', '*.png', '*.gif', '*.ico',
        '*.pdf', '*.doc', '*.docx',
        
        # Other
        '.cache/', '.sass-cache/', '*.min.js', '*.min.css',
    ]
    
    def __init__(self, root_dir: str, custom_patterns: Optional[List[str]] = None):
        self.root_dir = Path(root_dir).resolve()
        self.ignore_patterns: Set[str] = set()
        self.regex_patterns: List[re.Pattern] = []
        
        # Add default patterns
        self.ignore_patterns.update(self.DEFAULT_IGNORE_PATTERNS)
        
        # Add custom patterns if provided
        if custom_patterns:
            self.ignore_patterns.update(custom_patterns)
        
        # Load .gitignore patterns
        self._load_gitignore()
        
        # Load .dockerignore patterns
        self._load_dockerignore()
        
        # Compile regex patterns
        self._compile_patterns()
    
    def _load_gitignore(self):
        """Load patterns from .gitignore file"""
        gitignore_path = self.root_dir / '.gitignore'
        if gitignore_path.exists():
            self._load_ignore_file(gitignore_path)
    
    def _load_dockerignore(self):
        """Load patterns from .dockerignore file"""
        dockerignore_path = self.root_dir / '.dockerignore'
        if dockerignore_path.exists():
            self._load_ignore_file(dockerignore_path)
    
    def _load_ignore_file(self, file_path: Path):
        """Load patterns from an ignore file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        # Handle negation patterns (starting with !)
                        if line.startswith('!'):
                            # TODO: Implement negation logic if needed
                            continue
                        self.ignore_patterns.add(line)
        except Exception:
            pass  # Silently ignore read errors
    
    def _compile_patterns(self):
        """Compile patterns into regex for efficient matching"""
        for pattern in self.ignore_patterns:
            # Convert glob patterns to regex
            regex = self._glob_to_regex(pattern)
            if regex:
                self.regex_patterns.append(re.compile(regex))
    
    def _glob_to_regex(self, pattern: str) -> Optional[str]:
        """Convert a gitignore pattern to regex"""
        # Handle directory patterns
        if pattern.endswith('/'):
            # Match directory at any level
            return f".*/{re.escape(pattern[:-1])}(/.*)?$"
        
        # Handle patterns starting with /
        if pattern.startswith('/'):
            # Match from root only
            pattern = pattern[1:]
            return f"^{re.escape(pattern)}(/.*)?$"
        
        # Convert glob to regex
        # Replace ** with temporary placeholder
        pattern = pattern.replace('**', '\x00')
        # Escape special regex chars except * and ?
        pattern = re.escape(pattern)
        # Replace escaped * and ? with regex equivalents
        pattern = pattern.replace(r'\*', '[^/]*')
        pattern = pattern.replace(r'\?', '[^/]')
        # Replace temporary placeholder with .*
        pattern = pattern.replace('\x00', '.*')
        
        # Match at any level
        return f"(^|.*/){pattern}(/.*)?$"
    
    def should_ignore(self, file_path: str) -> bool:
        """Check if a file should be ignored"""
        # Convert to Path and make relative to root
        path = Path(file_path)
        try:
            relative_path = path.relative_to(self.root_dir)
        except ValueError:
            # If not under root_dir, use absolute path
            relative_path = path
        
        # Convert to string with forward slashes
        path_str = str(relative_path).replace('\\', '/')
        
        # Check against compiled patterns
        for regex in self.regex_patterns:
            if regex.match(path_str):
                return True
        
        # Check simple patterns with fnmatch
        for pattern in self.ignore_patterns:
            if not pattern.endswith('/') and not '*' in pattern:
                # Simple file name match
                if path.name == pattern:
                    return True
            
            # Check if any parent directory matches a directory pattern
            for parent in path.parents:
                try:
                    parent_relative = parent.relative_to(self.root_dir)
                    parent_name = parent_relative.name
                    if pattern.endswith('/') and parent_name == pattern[:-1]:
                        return True
                except ValueError:
                    continue
        
        return False
    
    def filter_files(self, file_paths: List[str]) -> List[str]:
        """Filter out ignored files from a list"""
        return [f for f in file_paths if not self.should_ignore(f)]
    
    def get_patterns(self) -> List[str]:
        """Get all active ignore patterns"""
        return sorted(list(self.ignore_patterns))