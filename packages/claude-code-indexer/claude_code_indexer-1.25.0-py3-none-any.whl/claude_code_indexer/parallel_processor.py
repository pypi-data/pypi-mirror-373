#!/usr/bin/env python3
"""
Parallel processing for faster file indexing
"""

import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
import ast
import os
from pathlib import Path
import time
from dataclasses import dataclass
from .logger import log_info, log_warning, log_error

from .pattern_detector import PatternDetector
from .library_detector import LibraryDetector
from .infrastructure_detector import InfrastructureDetector
from .parsers import create_default_parser


@dataclass
class FileProcessingResult:
    """Result from processing a single file"""
    file_path: str
    nodes: Dict[int, Dict]
    edges: List[Tuple]
    patterns: List
    libraries: Dict
    infrastructure: Dict
    processing_time: float
    success: bool
    error_message: str = ""


class ParallelFileProcessor:
    """Process multiple files in parallel"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(mp.cpu_count(), 8)
        self.pattern_detector = PatternDetector()
        self.library_detector = LibraryDetector()
        self.infrastructure_detector = InfrastructureDetector()
        self.parser = create_default_parser()
    
    def process_files_parallel(self, file_paths: List[str]) -> List[FileProcessingResult]:
        """Process multiple files in parallel using multiprocessing"""
        if len(file_paths) <= 2:
            # For small numbers, sequential is faster due to overhead
            return [self._process_single_file(fp) for fp in file_paths]
        
        log_info(f"🚀 Processing {len(file_paths)} files with {self.max_workers} workers...")
        
        # Split into chunks for better load balancing
        chunk_size = max(1, len(file_paths) // self.max_workers)
        file_chunks = [file_paths[i:i + chunk_size] 
                      for i in range(0, len(file_paths), chunk_size)]
        
        results = []
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_chunk = {
                executor.submit(process_file_chunk, chunk): chunk 
                for chunk in file_chunks
            }
            
            for future in as_completed(future_to_chunk):
                chunk_results = future.result()
                results.extend(chunk_results)
        
        return results
    
    
    def _process_single_file(self, file_path: str) -> FileProcessingResult:
        """Process a single code file using multi-language parser"""
        start_time = time.time()
        
        try:
            # Use multi-language parser
            parse_result = self.parser.parse_file(file_path)
            
            if not parse_result.success:
                return FileProcessingResult(
                    file_path=file_path,
                    nodes={}, edges=[], patterns=[], libraries={}, infrastructure={},
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=parse_result.error_message or "Parse failed"
                )
            
            # Convert parser nodes to dict format
            nodes = {}
            node_counter = 0
            parser_to_local_id = {}
            
            for parser_node_id, parser_node in parse_result.nodes.items():
                nodes[node_counter] = {
                    'id': node_counter,
                    'node_type': parser_node.node_type,
                    'name': parser_node.name,
                    'path': parser_node.path,
                    'summary': parser_node.summary,
                    'language': parser_node.language,
                    'line_number': parser_node.line_number,
                    'column_number': parser_node.column_number,
                    'importance_score': 0.0,
                    'relevance_tags': []
                }
                
                # Add language-specific attributes
                if parser_node.attributes:
                    nodes[node_counter].update(parser_node.attributes)
                
                parser_to_local_id[parser_node_id] = node_counter
                node_counter += 1
            
            # Convert relationships
            edges = []
            for relationship in parse_result.relationships:
                source_id = parser_to_local_id.get(relationship.source_id)
                target_id = parser_to_local_id.get(relationship.target_id)
                
                if source_id is not None and target_id is not None:
                    edges.append((source_id, target_id, relationship.relationship_type))
            
            # For Python files, still do pattern/library detection
            patterns = []
            libraries = {}
            infrastructure = {}
            
            if parse_result.language == 'python':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    patterns = self.pattern_detector.detect_patterns(tree, file_path)
                    libraries = self.library_detector.extract_libraries(tree)
                    infrastructure = self.infrastructure_detector.detect_infrastructure(tree)
                except:
                    pass  # Continue even if pattern detection fails
            
            return FileProcessingResult(
                file_path=file_path,
                nodes=nodes,
                edges=edges,
                patterns=patterns,
                libraries=libraries,
                infrastructure=infrastructure,
                processing_time=time.time() - start_time,
                success=True
            )
            
        except Exception as e:
            return FileProcessingResult(
                file_path=file_path,
                nodes={}, edges=[], patterns=[], libraries={}, infrastructure={},
                processing_time=time.time() - start_time,
                success=False,
                error_message=f"Unexpected error: {e}"
            )
    
    def _extract_nodes_and_edges(self, tree: ast.AST, file_path: str) -> Tuple[Dict, List]:
        """Extract nodes and edges from AST (optimized version)"""
        nodes = {}
        edges = []
        node_counter = 0
        
        # Create file node
        file_node_id = node_counter
        nodes[file_node_id] = {
            'id': file_node_id,
            'node_type': 'file',
            'name': os.path.basename(file_path),
            'path': file_path,
            'summary': f"Python file: {os.path.basename(file_path)}",
            'importance_score': 0.0,
            'relevance_tags': []
        }
        node_counter += 1
        
        # Fast AST traversal
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_node_id = node_counter
                    nodes[import_node_id] = {
                        'id': import_node_id,
                        'node_type': 'import',
                        'name': alias.name,
                        'path': file_path,
                        'summary': f"Import: {alias.name}",
                        'importance_score': 0.0,
                        'relevance_tags': []
                    }
                    edges.append((file_node_id, import_node_id, 'imports'))
                    node_counter += 1
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_node_id = node_counter
                    nodes[import_node_id] = {
                        'id': import_node_id,
                        'node_type': 'import',
                        'name': node.module,
                        'path': file_path,
                        'summary': f"Import from: {node.module}",
                        'importance_score': 0.0,
                        'relevance_tags': []
                    }
                    edges.append((file_node_id, import_node_id, 'imports'))
                    node_counter += 1
            
            elif isinstance(node, ast.ClassDef):
                class_node_id = node_counter
                nodes[class_node_id] = {
                    'id': class_node_id,
                    'node_type': 'class',
                    'name': node.name,
                    'path': file_path,
                    'summary': f"Class: {node.name}",
                    'importance_score': 0.0,
                    'relevance_tags': []
                }
                edges.append((file_node_id, class_node_id, 'contains'))
                node_counter += 1
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_node_id = node_counter
                        nodes[method_node_id] = {
                            'id': method_node_id,
                            'node_type': 'method',
                            'name': f"{node.name}.{item.name}",
                            'path': file_path,
                            'summary': f"Method: {node.name}.{item.name}",
                            'importance_score': 0.0,
                            'relevance_tags': []
                        }
                        edges.append((class_node_id, method_node_id, 'contains'))
                        node_counter += 1
            
            elif isinstance(node, ast.FunctionDef):
                func_node_id = node_counter
                nodes[func_node_id] = {
                    'id': func_node_id,
                    'node_type': 'function',
                    'name': node.name,
                    'path': file_path,
                    'summary': f"Function: {node.name}",
                    'importance_score': 0.0,
                    'relevance_tags': []
                }
                edges.append((file_node_id, func_node_id, 'contains'))
                node_counter += 1
        
        return nodes, edges


def process_file_chunk(file_paths: List[str]) -> List[FileProcessingResult]:
    """Process a chunk of files (for multiprocessing)"""
    processor = ParallelFileProcessor()
    return [processor._process_single_file(fp) for fp in file_paths]


class ProcessingStats:
    """Track processing statistics"""
    
    def __init__(self):
        self.total_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.total_time = 0.0
        self.files_per_second = 0.0
    
    def update(self, results: List[FileProcessingResult]):
        """Update stats from processing results"""
        self.total_files = len(results)
        self.successful_files = sum(1 for r in results if r.success)
        self.failed_files = self.total_files - self.successful_files
        self.total_time = sum(r.processing_time for r in results)
        
        if self.total_time > 0:
            self.files_per_second = self.total_files / self.total_time
    
    def print_stats(self):
        """Print processing statistics"""
        log_info(f"📊 Processing Stats:")
        log_info(f"   Total files: {self.total_files}")
        log_info(f"   Successful: {self.successful_files}")
        log_info(f"   Failed: {self.failed_files}")
        log_info(f"   Total time: {self.total_time:.2f}s")
        log_info(f"   Speed: {self.files_per_second:.1f} files/sec")