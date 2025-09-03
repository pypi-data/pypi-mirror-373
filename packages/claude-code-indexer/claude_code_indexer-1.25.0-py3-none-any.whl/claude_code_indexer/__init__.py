"""
Claude Code Indexer - Code indexing tool using Ensmallen graph database
"""

try:
    from importlib.metadata import version
    __version__ = version("claude-code-indexer")
except:
    __version__ = "1.25.0"

__app_name__ = "Claude Code Indexer"
__author__ = "Tony Nguyen"
__email__ = "tony@startupascent.net"

__all__ = ["CodeGraphIndexer", "main"]