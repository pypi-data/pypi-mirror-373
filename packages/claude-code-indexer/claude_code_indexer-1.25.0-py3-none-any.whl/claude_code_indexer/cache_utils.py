#!/usr/bin/env python3
"""
Cache utilities and key generation
"""

from typing import Dict


class CacheKeyGenerator:
    """
    Generate consistent cache keys for different entity types
    
    Ensures cache keys are unique and descriptive
    """
    
    @staticmethod
    def file_key(file_path: str) -> str:
        """Generate key for file cache"""
        return f"file:{file_path}"
    
    @staticmethod
    def node_key(node_type: str, node_id: int, file_path: str) -> str:
        """Generate key for code node"""
        return f"node:{node_type}:{node_id}:{file_path}"
    
    @staticmethod
    def pattern_key(pattern_type: str, file_path: str) -> str:
        """Generate key for pattern detection"""
        return f"pattern:{pattern_type}:{file_path}"
    
    @staticmethod
    def metadata_key(entity_type: str, entity_id: str) -> str:
        """Generate key for metadata"""
        return f"metadata:{entity_type}:{entity_id}"
    
    @staticmethod
    def stats_key(project_path: str) -> str:
        """Generate key for project statistics"""
        return f"stats:{project_path}"
    
    @staticmethod
    def parse_key(key: str) -> Dict[str, str]:
        """Parse cache key to extract components"""
        parts = key.split(":", 1)
        if len(parts) < 2:
            return {"type": "unknown", "key": key}
        
        key_type = parts[0]
        if key_type == "file":
            return {"type": "file", "path": parts[1] if len(parts) > 1 else ""}
        elif key_type == "node":
            # For node keys, we expect format: node:node_type:node_id:path
            # parts[1] contains "node_type:node_id:path"
            sub_parts = parts[1].split(":", 2) if len(parts) > 1 else []
            return {
                "type": "node",
                "node_type": sub_parts[0] if len(sub_parts) > 0 else "",
                "node_id": sub_parts[1] if len(sub_parts) > 1 else "",
                "path": sub_parts[2] if len(sub_parts) > 2 else ""
            }
        elif key_type == "pattern":
            # For pattern keys, we expect format: pattern:pattern_type:path
            sub_parts = parts[1].split(":", 1) if len(parts) > 1 else []
            return {
                "type": "pattern",
                "pattern_type": sub_parts[0] if len(sub_parts) > 0 else "",
                "path": sub_parts[1] if len(sub_parts) > 1 else ""
            }
        else:
            return {"type": key_type, "key": ":".join(parts[1:])}