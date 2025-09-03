"""
Indexer interface for dependency injection
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set
from pathlib import Path


class IIndexer(ABC):
    """Interface for code indexing operations"""
    
    @abstractmethod
    def index_directory(self, directory: Path, file_patterns: Optional[List[str]] = None,
                       ignore_patterns: Optional[List[str]] = None, use_cache: bool = True) -> Dict:
        """Index a directory and return statistics"""
        pass
    
    @abstractmethod
    def get_all_files(self, directory: Path, file_extensions: Set[str],
                     ignore_patterns: List[str]) -> List[Path]:
        """Get all files to be indexed"""
        pass
    
    @abstractmethod
    def process_file(self, file_path: Path) -> Optional[Dict]:
        """Process a single file"""
        pass
    
    @abstractmethod
    def build_graph(self) -> None:
        """Build the code graph from parsed data"""
        pass
    
    @abstractmethod
    def calculate_importance_scores(self, graph: Optional[Any] = None) -> None:
        """Calculate importance scores for nodes"""
        pass
    
    @abstractmethod
    def save_to_db(self) -> bool:
        """Save indexed data to database"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict:
        """Get indexing statistics"""
        pass