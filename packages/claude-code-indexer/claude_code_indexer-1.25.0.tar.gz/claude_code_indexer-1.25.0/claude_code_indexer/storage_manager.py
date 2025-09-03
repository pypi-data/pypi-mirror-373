#!/usr/bin/env python3
"""
Centralized storage manager for Claude Code Indexer
Manages all project data in ~/.claude-code-indexer/
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import json
from datetime import datetime
from .logger import log_info, log_warning


class StorageManager:
    """Manages centralized storage for all indexed projects"""
    
    def __init__(self, app_home: Optional[Path] = None):
        """Initialize storage manager with app home directory"""
        if app_home:
            self.app_home = Path(app_home)
        else:
            self.app_home = Path.home() / '.claude-code-indexer'
        
        # Create app home if it doesn't exist
        self.app_home.mkdir(exist_ok=True, parents=True)
        
        # Create subdirectories
        self.projects_dir = self.app_home / 'projects'
        self.projects_dir.mkdir(exist_ok=True)
        
        # Global metadata file
        self.metadata_file = self.app_home / 'projects.json'
        self._load_metadata()
    
    def _load_metadata(self):
        """Load project metadata from file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                'version': '1.0',
                'projects': {},
                'last_updated': None
            }
    
    def _save_metadata(self):
        """Save project metadata to file"""
        self.metadata['last_updated'] = datetime.now().isoformat()
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_project_id(self, project_path: Path) -> str:
        """Generate unique project ID from path"""
        # Normalize path to absolute
        abs_path = project_path.resolve()
        
        # Create hash from absolute path
        path_str = str(abs_path)
        project_id = hashlib.md5(path_str.encode()).hexdigest()[:12]
        
        return project_id
    
    def get_project_dir(self, project_path: Path) -> Path:
        """Get storage directory for a project"""
        project_id = self.get_project_id(project_path)
        project_dir = self.projects_dir / project_id
        
        # Create if doesn't exist
        project_dir.mkdir(exist_ok=True)
        
        # Update metadata
        if project_id not in self.metadata['projects']:
            self.metadata['projects'][project_id] = {
                'path': str(project_path.resolve()),
                'name': project_path.name,
                'created_at': datetime.now().isoformat(),
                'last_indexed': None,
                'stats': {}
            }
            self._save_metadata()
        
        return project_dir
    
    def get_database_path(self, project_path: Path) -> Path:
        """Get database file path for a project"""
        project_dir = self.get_project_dir(project_path)
        return project_dir / 'code_index.db'
    
    def get_cache_dir(self, project_path: Path) -> Path:
        """Get cache directory for a project"""
        project_dir = self.get_project_dir(project_path)
        cache_dir = project_dir / 'cache'
        cache_dir.mkdir(exist_ok=True)
        return cache_dir
    
    def list_projects(self) -> List[Dict]:
        """List all indexed projects"""
        projects = []
        
        for project_id, info in self.metadata['projects'].items():
            project_info = info.copy()
            project_info['id'] = project_id
            
            # Check if project still exists
            project_path = Path(info['path'])
            project_info['exists'] = project_path.exists()
            
            # Get database size
            db_path = self.projects_dir / project_id / 'code_index.db'
            if db_path.exists():
                project_info['db_size'] = db_path.stat().st_size
            else:
                project_info['db_size'] = 0
            
            projects.append(project_info)
        
        return sorted(projects, key=lambda x: x.get('last_indexed') or '', reverse=True)
    
    def update_project_stats(self, project_path: Path, stats: Dict):
        """Update project statistics"""
        project_id = self.get_project_id(project_path)
        
        if project_id in self.metadata['projects']:
            self.metadata['projects'][project_id]['stats'] = stats
            self.metadata['projects'][project_id]['last_indexed'] = datetime.now().isoformat()
            self._save_metadata()
    
    def remove_project(self, project_path: Path) -> bool:
        """Remove a project from storage"""
        project_id = self.get_project_id(project_path)
        project_dir = self.projects_dir / project_id
        
        # Remove directory
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
            
        # Remove from metadata
        if project_id in self.metadata['projects']:
            del self.metadata['projects'][project_id]
            self._save_metadata()
            return True
        
        return False
    
    def find_project_by_name(self, name: str) -> Optional[Dict]:
        """Find project by name (partial match)"""
        name_lower = name.lower()
        
        for project_id, info in self.metadata['projects'].items():
            if name_lower in info['name'].lower() or name_lower in info['path'].lower():
                project_info = info.copy()
                project_info['id'] = project_id
                return project_info
        
        return None
    
    def get_project_from_cwd(self) -> Path:
        """Get project path from current working directory"""
        return Path.cwd()
    
    def clean_orphaned_projects(self):
        """Remove projects whose source directories no longer exist"""
        removed = []
        
        for project_id, info in list(self.metadata['projects'].items()):
            project_path = Path(info['path'])
            if not project_path.exists():
                project_dir = self.projects_dir / project_id
                if project_dir.exists():
                    import shutil
                    shutil.rmtree(project_dir)
                del self.metadata['projects'][project_id]
                removed.append(info['path'])
        
        if removed:
            self._save_metadata()
            log_info(f"🗑️  Removed {len(removed)} orphaned projects")
        
        return removed
    
    def get_storage_stats(self) -> Dict:
        """Get overall storage statistics"""
        total_size = 0
        project_count = len(self.metadata['projects'])
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                for file in project_dir.rglob('*'):
                    if file.is_file():
                        total_size += file.stat().st_size
        
        return {
            'app_home': str(self.app_home),
            'project_count': project_count,
            'total_size': total_size,
            'total_size_mb': total_size / 1024 / 1024
        }


# Global instance
_storage_manager = None

def get_storage_manager() -> StorageManager:
    """Get global storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager