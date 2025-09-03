#!/usr/bin/env python3
"""
Code Graph Indexer using Ensmallen
"""

import ast
import os
import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
import networkx as nx
import pandas as pd
from ensmallen import Graph
from .pattern_detector import PatternDetector
from .library_detector import LibraryDetector
from .infrastructure_detector import InfrastructureDetector
from .weight_calculator import WeightCalculator
from .db_optimizer import OptimizedDatabase, time_it
from .parallel_processor import ParallelFileProcessor, ProcessingStats
from .cache_manager import CacheManager, IncrementalIndexer
from .logger import log_info, log_warning, log_error
from .ignore_handler import IgnoreHandler
from .parsers import create_default_parser, ParseResult
from .storage_manager import get_storage_manager
from .security import validate_sql_identifier, SecurityError
from .llm_metadata_enhancer import LLMMetadataEnhancer
from .migrations import MigrationManager
from . import __version__


class CodeGraphIndexer:
    """Main code indexing class using Ensmallen graph database"""
    
    def __init__(self, db_path: str = None, use_cache: bool = True, 
                 parallel_workers: int = None, enable_optimizations: bool = True,
                 project_path: Path = None):
        # Use centralized storage manager
        self.storage_manager = get_storage_manager()
        
        # Determine project path
        if project_path:
            self.project_path = Path(project_path)
        else:
            self.project_path = self.storage_manager.get_project_from_cwd()
        
        # Get database path from storage manager
        if db_path:
            # Allow override for backward compatibility
            self.db_path = db_path
        else:
            self.db_path = str(self.storage_manager.get_database_path(self.project_path))
        
        self.nodes = {}  # node_id -> node_info
        self.edges = []  # List of (source, target, edge_type)
        self.node_counter = 0
        self.pattern_detector = PatternDetector()
        self.library_detector = LibraryDetector()
        self.infrastructure_detector = InfrastructureDetector()
        self.weight_calculator = WeightCalculator()
        self.all_files_content = {}  # Store file contents for weight calculation
        self.infrastructure_by_file = {}  # Store infrastructure data by file path
        
        # Multi-language parser system
        self.parser = create_default_parser()
        
        # Performance optimizations
        self.use_cache = use_cache
        self.enable_optimizations = enable_optimizations
        
        # Logging and debugging
        self.verbose = False
        self.parsing_errors = []
        
        if self.use_cache:
            # Initialize cache manager with integrated memory cache
            self.cache_manager = CacheManager(
                project_path=self.project_path,
                enable_memory_cache=True,
                memory_cache_mb=100  # 100MB default
            )
            self.incremental_indexer = IncrementalIndexer(self.cache_manager)
        
        if self.enable_optimizations:
            self.optimized_db = OptimizedDatabase(self.db_path)
        
        self.parallel_processor = ParallelFileProcessor(max_workers=parallel_workers)
        self.processing_stats = ProcessingStats()
        
        # Initialize LLM metadata enhancer (lazy initialization)
        self._llm_enhancer = None
        
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database with schema and handle migrations"""
        # Run automatic migrations first
        migration_manager = MigrationManager(self.db_path)
        
        # Get target version from package version
        target_version = self._get_schema_version_from_package()
        
        # Perform migration
        success, message = migration_manager.migrate(target_version)
        if success:
            log_info(f"Database migration: {message}")
        else:
            log_error(f"Database migration failed: {message}")
            raise RuntimeError(f"Failed to migrate database: {message}")
        
        # Now connect and ensure all tables exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Run legacy migration for compatibility
        self._migrate_database_schema(cursor)
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_nodes (
            id INTEGER PRIMARY KEY,
            node_type TEXT,
            name TEXT,
            path TEXT,
            summary TEXT,
            importance_score REAL,
            relevance_tags TEXT,
            weight REAL,
            frequency_score REAL,
            usage_stats TEXT,
            language TEXT DEFAULT 'python',
            line_number INTEGER DEFAULT 0,
            column_number INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            source_id INTEGER,
            target_id INTEGER,
            relationship_type TEXT,
            weight REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id) REFERENCES code_nodes(id),
            FOREIGN KEY (target_id) REFERENCES code_nodes(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS indexing_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Patterns table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY,
            file_path TEXT,
            pattern_type TEXT,
            confidence REAL,
            description TEXT,
            nodes TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Libraries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS libraries (
            id INTEGER PRIMARY KEY,
            file_path TEXT,
            name TEXT,
            version TEXT,
            category TEXT,
            usage_count INTEGER,
            usage_contexts TEXT,
            import_statements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Infrastructure table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS infrastructure (
            id INTEGER PRIMARY KEY,
            file_path TEXT,
            component_type TEXT,
            name TEXT,
            technology TEXT,
            configuration TEXT,
            usage_frequency INTEGER,
            connections TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _integrate_cached_result(self, cached_result):
        """Integrate cached processing result into current indexing session"""
        try:
            # Store file content for weight calculation
            with open(cached_result.file_path, 'r', encoding='utf-8') as f:
                self.all_files_content[cached_result.file_path] = f.read()
            
            # Integrate nodes
            for node_id, node_data in cached_result.nodes.items():
                new_id = self.node_counter
                self.nodes[new_id] = node_data.copy()
                self.nodes[new_id]['id'] = new_id
                self.node_counter += 1
            
            # Integrate edges (need to remap node IDs)
            node_id_mapping = {}
            start_id = self.node_counter - len(cached_result.nodes)
            for i, old_id in enumerate(cached_result.nodes.keys()):
                node_id_mapping[old_id] = start_id + i
            
            for edge in cached_result.edges:
                source, target, edge_type = edge
                if source in node_id_mapping and target in node_id_mapping:
                    self.edges.append((
                        node_id_mapping[source], 
                        node_id_mapping[target], 
                        edge_type
                    ))
        except Exception as e:
            log_warning(f"Failed to integrate cached result for {cached_result.file_path}: {e}")
    
    def _integrate_processing_result(self, result):
        """Integrate parallel processing result into current indexing session"""
        # Store file content
        try:
            with open(result.file_path, 'r', encoding='utf-8') as f:
                self.all_files_content[result.file_path] = f.read()
        except:
            pass
        
        # Integrate nodes
        node_id_mapping = {}
        for old_id, node_data in result.nodes.items():
            new_id = self.node_counter
            self.nodes[new_id] = node_data.copy()
            self.nodes[new_id]['id'] = new_id
            node_id_mapping[old_id] = new_id
            self.node_counter += 1
        
        # Integrate edges with remapped IDs
        for edge in result.edges:
            source, target, edge_type = edge
            if source in node_id_mapping and target in node_id_mapping:
                self.edges.append((
                    node_id_mapping[source], 
                    node_id_mapping[target], 
                    edge_type
                ))
    
    def parse_code_file(self, file_path: str) -> Dict:
        """Parse a code file using the appropriate language parser"""
        if self.verbose:
            log_info(f"Parsing {file_path}...")
            
        # Use the new multi-language parser
        parse_result = self.parser.parse_file(file_path)
        
        if not parse_result.success:
            error_msg = f"Failed to parse {file_path}: {parse_result.error_message}"
            log_warning(error_msg)
            self.parsing_errors.append(error_msg)
            return {}
            
        if self.verbose and parse_result.error_message:
            # Partial success with warnings
            self.parsing_errors.append(f"Warnings in {file_path}: {parse_result.error_message}")
        
        # Convert parser nodes to indexer format
        # Keep a mapping from parser node IDs to indexer node IDs
        parser_to_indexer_id = {}
        
        for parser_node_id, parser_node in parse_result.nodes.items():
            # Map parser node to indexer node format
            indexer_node = {
                'id': self.node_counter,
                'node_type': parser_node.node_type,
                'name': parser_node.name,
                'path': parser_node.path,
                'summary': parser_node.summary,
                'importance_score': 0.0,
                'relevance_tags': [],
                'language': parser_node.language,
                'line_number': parser_node.line_number,
                'column_number': parser_node.column_number
            }
            
            # Add language-specific attributes
            if parser_node.attributes:
                indexer_node.update(parser_node.attributes)
            
            # Store the mapping
            parser_to_indexer_id[parser_node_id] = self.node_counter
            
            self.nodes[self.node_counter] = indexer_node
            self.node_counter += 1
        
        # Convert parser relationships to indexer format using the mapping
        for relationship in parse_result.relationships:
            source_id = parser_to_indexer_id.get(relationship.source_id)
            target_id = parser_to_indexer_id.get(relationship.target_id)
            
            if source_id is not None and target_id is not None:
                self.edges.append((source_id, target_id, relationship.relationship_type))
        
        return self.nodes
    
    
    def _create_node(self, node_type: str, name: str, path: str, summary: str) -> int:
        """Create a node and return its ID"""
        node_id = self.node_counter
        self.nodes[node_id] = {
            'id': node_id,
            'node_type': node_type,
            'name': name,
            'path': path,
            'summary': summary,
            'importance_score': 0.0,
            'relevance_tags': []
        }
        self.node_counter += 1
        return node_id
    
    def build_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from nodes and edges"""
        nx_graph = nx.DiGraph()
        
        # Add nodes
        for node_id, node_info in self.nodes.items():
            nx_graph.add_node(
                node_id,
                node_type=node_info['node_type'],
                name=node_info['name']
            )
        
        # Add edges
        for source, target, edge_type in self.edges:
            nx_graph.add_edge(source, target, edge_type=edge_type)
        
        return nx_graph
    
    def build_ensmallen_graph(self) -> Optional[Graph]:
        """Build Ensmallen graph for advanced analysis"""
        if not self.edges:
            return None
        
        # Prepare edge data
        edges_data = []
        for source, target, edge_type in self.edges:
            edges_data.append([f"node_{source}", f"node_{target}"])
        
        # Save to temporary file
        edges_df = pd.DataFrame(edges_data, columns=["source", "destination"])
        
        # Always use home directory for temp files to avoid permission issues
        # This is especially important for MCP servers and read-only environments
        try:
            temp_dir = Path.home() / '.claude_code_indexer' / 'temp'
            temp_dir.mkdir(exist_ok=True, parents=True)
            temp_file = str(temp_dir / f"temp_edges_{os.getpid()}_{int(time.time() * 1000)}.tsv")
        except (OSError, PermissionError):
            # Final fallback: use system temp directory
            import tempfile
            temp_file = tempfile.mktemp(suffix='.tsv', prefix='temp_edges_')
            
        # Add debug logging to understand the actual file path being used
        log_info(f"Creating temp file: {temp_file}")
        edges_df.to_csv(temp_file, index=False, sep="\t", header=False)
        
        try:
            # Create ensmallen graph
            graph = Graph.from_csv(
                edge_path=temp_file,
                directed=True,
                verbose=False
            )
            return graph
        except Exception as e:
            log_warning(f"Could not create Ensmallen graph: {e}")
            return None
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def calculate_importance_scores(self, graph: nx.DiGraph):
        """Calculate importance scores for nodes using graph metrics"""
        # Calculate various centrality measures
        in_degree_centrality = nx.in_degree_centrality(graph)
        out_degree_centrality = nx.out_degree_centrality(graph)
        
        # Calculate PageRank for importance
        try:
            pagerank = nx.pagerank(graph, alpha=0.85)
        except:
            pagerank = {node: 0.0 for node in graph.nodes()}
        
        # Update node importance scores
        for node_id in self.nodes:
            if node_id in graph:
                # Combine different metrics
                in_score = in_degree_centrality.get(node_id, 0.0)
                out_score = out_degree_centrality.get(node_id, 0.0)
                pr_score = pagerank.get(node_id, 0.0)
                
                # Weighted importance score
                # Normalize scores for better distribution
                node_type = self.nodes[node_id]['node_type']
                
                # Base score from centrality measures
                base_score = (
                    0.4 * in_score +  # How many depend on this
                    0.2 * out_score + # Complexity
                    0.4 * pr_score    # Overall importance
                )
                
                # Boost scores based on node type
                type_boost = {
                    'class': 0.3,
                    'function': 0.1,
                    'method': 0.05,
                    'file': 0.0,
                    'import': 0.0
                }.get(node_type, 0.0)
                
                # Boost for nodes with many connections
                connection_boost = 0.0
                if graph.in_degree(node_id) > 5:
                    connection_boost = 0.2
                elif graph.in_degree(node_id) > 2:
                    connection_boost = 0.1
                
                # Calculate final score with boosts
                importance_score = base_score + type_boost + connection_boost
                
                # Normalize to 0-1 range with better distribution
                self.nodes[node_id]['importance_score'] = min(importance_score * 2, 1.0)
                
                # Add relevance tags
                tags = []
                if self.nodes[node_id]['node_type'] == 'class':
                    tags.append('structural')
                if graph.in_degree(node_id) > 3:
                    tags.append('highly-used')
                if graph.out_degree(node_id) > 3:
                    tags.append('complex')
                node_name = self.nodes[node_id].get('name', '')
                if node_name and 'test' in node_name.lower():
                    tags.append('test')
                if self.nodes[node_id]['node_type'] == 'file':
                    tags.append('module')
                
                # Add infrastructure and DevOps tags based on file path
                file_path = self.nodes[node_id].get('path', '')
                if file_path:
                    # Check if this node is from a file with infrastructure
                    if file_path in self.infrastructure_by_file:
                        infra_data = self.infrastructure_by_file[file_path]
                        
                        # Add infrastructure tags
                        if infra_data.get('databases'):
                            tags.append('infrastructure:database')
                        if infra_data.get('apis'):
                            tags.append('infrastructure:api')
                        if infra_data.get('message_queues'):
                            tags.append('infrastructure:messaging')
                        if infra_data.get('cloud_services'):
                            tags.append('infrastructure:cloud')
                            
                        # Add specific environment/profile tags
                        for comp in infra_data.get('configuration', []):
                            if comp.name == 'environment':
                                tags.append('devops:environment')
                                # Try to detect specific environments
                                if 'production' in str(comp.connections).lower():
                                    tags.append('profile:production')
                                if 'staging' in str(comp.connections).lower():
                                    tags.append('profile:staging')
                                if 'development' in str(comp.connections).lower():
                                    tags.append('profile:development')
                            elif comp.name == 'secrets':
                                tags.append('devops:security')
                        
                        # Add DevOps tags
                        if any('docker' in str(comp).lower() for comp in infra_data.values()):
                            tags.append('devops:containerization')
                        if any('kubernetes' in str(comp).lower() or 'k8s' in str(comp).lower() for comp in infra_data.values()):
                            tags.append('devops:orchestration')
                        if any('jenkins' in str(comp).lower() or 'github' in str(comp).lower() for comp in infra_data.values()):
                            tags.append('devops:ci/cd')
                
                self.nodes[node_id]['relevance_tags'] = tags
            else:
                self.nodes[node_id]['importance_score'] = 0.0
                self.nodes[node_id]['relevance_tags'] = []
    
    def save_to_db(self):
        """Save nodes and relationships to SQLite database with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
        except sqlite3.Error as e:
            log_error(f"Error connecting to database: {e}")
            return False
        
        try:
            # Clear existing data safely - use parameterized queries
            tables_to_clear = ["relationships", "code_nodes", "patterns", "libraries", "infrastructure"]
            for table in tables_to_clear:
                try:
                    # Use explicit table names to avoid SQL injection
                    if table == "relationships":
                        cursor.execute("DELETE FROM relationships")
                    elif table == "code_nodes":
                        cursor.execute("DELETE FROM code_nodes")
                    elif table == "patterns":
                        cursor.execute("DELETE FROM patterns")
                    elif table == "libraries":
                        cursor.execute("DELETE FROM libraries")
                    elif table == "infrastructure":
                        cursor.execute("DELETE FROM infrastructure")
                except sqlite3.Error as e:
                    log_warning(f"Could not clear table {table}: {e}")
            
            # Insert nodes with error handling
            for node_id, node_info in self.nodes.items():
                # Validate and provide defaults for required fields
                name_value = node_info.get('name', '')
                node_name = name_value.strip() if name_value else ''
                if not node_name:
                    # Generate a default name based on node type and ID
                    node_name = f"{node_info.get('node_type', 'unknown')}_{node_id}"
                    log_warning(f"Node {node_id} has no name, using default: {node_name}")
                
                try:
                    cursor.execute('''
                    INSERT INTO code_nodes (id, node_type, name, path, summary, importance_score, relevance_tags, weight, frequency_score, usage_stats, language, line_number, column_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        node_info['id'],
                        node_info['node_type'],
                        node_name,  # Use validated name
                        node_info['path'],
                        node_info.get('summary', ''),  # Ensure summary is not None
                        node_info['importance_score'],
                        json.dumps(node_info['relevance_tags']),
                        node_info.get('weight', 0.0),
                        node_info.get('frequency_score', 0.0),
                        json.dumps(node_info.get('usage_stats', {})),
                        node_info.get('language', 'python'),
                        node_info.get('line_number', 0),
                        node_info.get('column_number', 0)
                    ))
                except sqlite3.Error as e:
                    log_warning(f"Could not insert node {node_id}: {e}")
                    # Try fallback insertion without new columns
                    try:
                        cursor.execute('''
                        INSERT INTO code_nodes (id, node_type, name, path, summary, importance_score, relevance_tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            node_info['id'],
                            node_info['node_type'],
                            node_name,  # Use validated name
                            node_info['path'],
                            node_info.get('summary', ''),  # Ensure summary is not None
                            node_info['importance_score'],
                            json.dumps(node_info['relevance_tags'])
                        ))
                    except sqlite3.Error as fallback_error:
                        log_error(f"Could not insert node {node_id} even with fallback: {fallback_error}")
        
            # Insert edges with error handling
            for source, target, edge_type in self.edges:
                try:
                    cursor.execute('''
                    INSERT INTO relationships (source_id, target_id, relationship_type, weight)
                    VALUES (?, ?, ?, ?)
                    ''', (source, target, edge_type, 1.0))
                except sqlite3.Error as e:
                    log_warning(f"Could not insert edge {source}->{target}: {e}")
            
            # Update metadata with error handling
            metadata_updates = [
                ('last_indexed', 'datetime("now")'),
                ('total_nodes', str(len(self.nodes))),
                ('total_edges', str(len(self.edges))),
                ('schema_version', self._get_schema_version_from_package())
            ]
            
            for key, value in metadata_updates:
                try:
                    if key == 'last_indexed':
                        cursor.execute('''
                        INSERT OR REPLACE INTO indexing_metadata (key, value)
                        VALUES (?, datetime('now'))
                        ''', (key,))
                    else:
                        cursor.execute('''
                        INSERT OR REPLACE INTO indexing_metadata (key, value)
                        VALUES (?, ?)
                        ''', (key, value))
                except sqlite3.Error as e:
                    log_warning(f"Could not update metadata {key}: {e}")
            
            conn.commit()
            log_info("✅ Data saved successfully")
            return True
            
        except sqlite3.Error as e:
            log_error(f"Database error during save: {e}")
            return False
        except Exception as e:
            log_error(f"Unexpected error during save: {e}")
            return False
        finally:
            try:
                conn.close()
            except:
                pass
    
    @time_it
    def index_directory(self, directory: str, patterns: List[str] = None, 
                       force_reindex: bool = False, custom_ignore: List[str] = None):
        """Index all supported code files in a directory with performance optimizations
        
        Args:
            directory: Directory to index
            patterns: File patterns to include (default: auto-detect from supported languages)
            force_reindex: Force re-indexing all files
            custom_ignore: Additional ignore patterns beyond .gitignore
        """
        if patterns is None:
            # Auto-generate patterns from supported extensions
            extensions = self.parser.get_supported_extensions()
            patterns = [f"*{ext}" for ext in extensions]
        
        start_time = time.time()
        
        # Initialize ignore handler
        ignore_handler = IgnoreHandler(directory, custom_ignore)
        
        # Collect all supported code files
        all_files = []
        for pattern in patterns:
            for file_path in Path(directory).rglob(pattern):
                if file_path.is_file():
                    file_str = str(file_path)
                    # Only include files that can be parsed
                    if self.parser.can_parse(file_str):
                        all_files.append(file_str)
        
        # Filter out ignored files
        all_files = ignore_handler.filter_files(all_files)
        
        if not all_files:
            log_info(f"No supported code files found matching patterns {patterns} in {directory} (after applying ignore rules)")
            return
        
        # Get language statistics
        language_stats = {}
        for file_path in all_files:
            parse_result = self.parser.parse_file(file_path)
            if parse_result.success:
                lang = parse_result.language
                if lang not in language_stats:
                    language_stats[lang] = 0
                language_stats[lang] += 1
        
        log_info(f"🔍 Found {len(all_files)} code files")
        for lang, count in language_stats.items():
            log_info(f"   📝 {lang}: {count} files")
        
        # Use incremental indexing if cache is enabled
        files_to_process = all_files
        cached_results = []
        
        if self.use_cache and not force_reindex:
            log_info("📋 Checking cache for unchanged files...")
            cached_files, files_to_process = self.incremental_indexer.get_files_to_process(all_files)
            
            if cached_files:
                log_info(f"💾 Loading {len(cached_files)} files from cache")
                cached_results = self.incremental_indexer.load_cached_results(cached_files)
                
                # Integrate cached results
                for cached_result in cached_results:
                    self._integrate_cached_result(cached_result)
            
            log_info(f"🔄 Processing {len(files_to_process)} new/modified files")
        
        # Process files with parallel processing or sequentially
        if files_to_process:
            if len(files_to_process) > 3 and hasattr(self, 'parallel_processor'):
                # Use parallel processing for multiple files
                processing_results = self.parallel_processor.process_files_parallel(files_to_process)
                self.processing_stats.update(processing_results)
                
                # Integrate parallel results and cache them
                for result in processing_results:
                    if result.success:
                        self._integrate_processing_result(result)
                        
                        # Cache the result if caching is enabled
                        if self.use_cache:
                            self.cache_manager.cache_file_result(
                                result.file_path, result.nodes, result.edges,
                                result.patterns, result.libraries, result.infrastructure
                            )
            else:
                # Sequential processing for small number of files
                for file_path in files_to_process:
                    parsed_nodes = self.parse_code_file(file_path)
                    # The parse_code_file method already adds nodes to self.nodes
                    # but we should also cache the result
                    if self.use_cache and parsed_nodes:
                        # Extract relevant data for caching
                        file_nodes = {id: node for id, node in self.nodes.items() 
                                     if node.get('path') == file_path}
                        file_edges = [(s, t, type) for s, t, type in self.edges 
                                     if s in file_nodes or t in file_nodes]
                        
                        # Cache the parsed result
                        self.cache_manager.cache_file_result(
                            file_path, file_nodes, file_edges,
                            {}, {}, {}  # patterns, libraries, infrastructure
                        )
        
        total_indexed = len(all_files)
        
        if total_indexed == 0:
            log_info("No files to index")
            return
        
        log_info("🔗 Building graph...")
        graph = self.build_graph()
        
        log_info("⚖️  Calculating importance scores...")
        self.calculate_importance_scores(graph)
        
        log_info("📊 Calculating weights based on usage frequency...")
        weighted_nodes, weighted_edges = self.weight_calculator.calculate_weights(
            self.nodes, self.edges, self.all_files_content
        )
        
        # Update nodes with weight information
        for node_id, weighted_node in weighted_nodes.items():
            self.nodes[node_id].update(weighted_node)
        
        # Update edges with weighted edges
        if weighted_edges:
            log_info(f"   📊 Updating {len(weighted_edges)} weighted edges...")
            self.edges = [(int(edge.source), int(edge.target), edge.relationship_type) 
                          for edge in weighted_edges]
        else:
            log_info(f"   ⚠️  No weighted edges returned, keeping original {len(self.edges)} edges")
        
        log_info("💾 Saving to database...")
        if not self.save_to_db():
            log_error("❌ Failed to save data to database")
            return False
        
        # Print performance stats
        processing_time = time.time() - start_time
        
        log_info(f"\n✅ Indexing Complete!")
        log_info(f"   📁 Total files: {total_indexed}")
        log_info(f"   💾 From cache: {len(cached_results)}")
        log_info(f"   🔄 Processed: {len(files_to_process)}")
        log_info(f"   🔗 Nodes: {len(self.nodes)}")
        log_info(f"   ↔️  Edges: {len(self.edges)}")
        log_info(f"   ⏱️  Time: {processing_time:.2f}s")
        log_info(f"   🚀 Speed: {total_indexed/processing_time:.1f} files/sec")
        log_info(f"   💾 Database: {self.db_path}")
        
        # Update project stats in storage manager
        stats = {
            'nodes': len(self.nodes),
            'edges': len(self.edges),
            'files': total_indexed,
            'cached': len(cached_results),
            'processed': len(files_to_process),
            'time': processing_time
        }
        self.storage_manager.update_project_stats(self.project_path, stats)
        
        # Print processing stats if available
        if hasattr(self.processing_stats, 'print_stats') and files_to_process:
            self.processing_stats.print_stats()
        
        # Print cache stats if enabled
        if self.use_cache:
            self.cache_manager.print_cache_stats()
        
        # Try to build Ensmallen graph for advanced features
        ensmallen_graph = self.build_ensmallen_graph()
        if ensmallen_graph:
            log_info(f"✓ Ensmallen graph ready for advanced analysis")
    
    def query_important_nodes(self, min_score: float = 0.1, limit: int = 20, node_type: Optional[str] = None) -> List[Dict]:
        """Query nodes with high importance scores"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM code_nodes WHERE importance_score >= ?"
        params = [min_score]
        
        if node_type:
            query += " AND node_type = ?"
            params.append(node_type)
            
        query += " ORDER BY importance_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            node_dict = dict(zip(columns, row))
            node_dict['relevance_tags'] = json.loads(node_dict['relevance_tags'])
            results.append(node_dict)
        
        conn.close()
        return results
    
    def get_stats(self) -> Dict:
        """Get indexing statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Get metadata
        cursor.execute('SELECT key, value FROM indexing_metadata')
        for key, value in cursor.fetchall():
            stats[key] = value
        
        # Get node type counts
        cursor.execute('SELECT node_type, COUNT(*) FROM code_nodes GROUP BY node_type')
        stats['node_types'] = dict(cursor.fetchall())
        
        # Get relationship type counts
        cursor.execute('SELECT relationship_type, COUNT(*) FROM relationships GROUP BY relationship_type')
        stats['relationship_types'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    def get_node_info(self, node_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific node.
        
        Args:
            node_id: The node ID to retrieve
            
        Returns:
            Node information dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, node_type, path as file_path, summary as content, 
                       line_number as start_line, importance_score, 
                       created_at
                FROM code_nodes 
                WHERE id = ?
            """, (node_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Convert to dict
            node_info = dict(row)
            
            # Get enhanced metadata if available
            cursor.execute("""
                SELECT llm_summary, role_tags, architectural_layer, 
                       business_domain, complexity_score, criticality_level,
                       dependencies_impact, testability_score
                FROM enhanced_metadata 
                WHERE node_id = ?
            """, (node_id,))
            
            enhanced = cursor.fetchone()
            if enhanced:
                node_info.update(dict(enhanced))
            
            return node_info
            
        finally:
            conn.close()
    
    def _store_patterns(self, patterns: List, file_path: str):
        """Store detected patterns in database"""
        if not patterns:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern in patterns:
            cursor.execute('''
            INSERT INTO patterns (file_path, pattern_type, confidence, description, nodes, location)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                file_path,
                pattern.pattern_type,
                pattern.confidence,
                pattern.description,
                json.dumps(pattern.nodes),
                pattern.location
            ))
        
        conn.commit()
        conn.close()
    
    def _store_libraries(self, libraries: Dict, file_path: str):
        """Store detected libraries in database"""
        if not libraries:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for lib_name, lib_usage in libraries.items():
            cursor.execute('''
            INSERT INTO libraries (file_path, name, version, category, usage_count, usage_contexts, import_statements)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_path,
                lib_usage.name,
                lib_usage.version,
                lib_usage.category,
                lib_usage.usage_count,
                json.dumps(lib_usage.usage_contexts),
                json.dumps(lib_usage.import_statements)
            ))
        
        conn.commit()
        conn.close()
    
    def _store_infrastructure(self, infrastructure: Dict, file_path: str):
        """Store detected infrastructure in database"""
        if not infrastructure:
            return
            
        # Check if any category has components
        has_components = any(components for components in infrastructure.values())
        if not has_components:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for category, components in infrastructure.items():
                for component in components:
                    cursor.execute('''
                    INSERT INTO infrastructure (file_path, component_type, name, technology, configuration, usage_frequency, connections)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        file_path,
                        component.component_type,
                        component.name,
                        component.technology,
                        json.dumps(component.configuration),
                        component.usage_frequency,
                        json.dumps(component.connections)
                    ))
            
            conn.commit()
        except Exception as e:
            print(f"Error storing infrastructure: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _migrate_database_schema(self, cursor):
        """Migrate existing database schema to support new columns"""
        try:
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='code_nodes'")
            if not cursor.fetchone():
                return  # New database, no migration needed
            
            # Check existing columns
            cursor.execute("PRAGMA table_info(code_nodes)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            # Add missing columns for v1.1.0 and v1.6.0
            new_columns = {
                'weight': 'REAL DEFAULT 0.0',
                'frequency_score': 'REAL DEFAULT 0.0', 
                'usage_stats': 'TEXT DEFAULT "{}"',
                'language': 'TEXT DEFAULT "python"',
                'line_number': 'INTEGER DEFAULT 0',
                'column_number': 'INTEGER DEFAULT 0'
            }
            
            for column_name, column_def in new_columns.items():
                if column_name not in existing_columns:
                    try:
                        # Validate column name to prevent SQL injection
                        safe_column_name = validate_sql_identifier(column_name)
                        # Use DDL with safe column name
                        cursor.execute(f"ALTER TABLE code_nodes ADD COLUMN {safe_column_name} {column_def}")
                        log_info(f"✓ Added column '{safe_column_name}' to code_nodes table")
                    except SecurityError as e:
                        log_warning(f"Invalid column name '{column_name}': {e}")
                    except sqlite3.Error as e:
                        log_warning(f"Could not add column '{column_name}': {e}")
            
            # Migrate other tables if needed
            self._migrate_new_tables(cursor)
            
        except sqlite3.Error as e:
            log_warning(f"Database migration failed: {e}")
    
    def _migrate_new_tables(self, cursor):
        """Create new tables introduced in v1.1.0"""
        new_tables = {
            'patterns': '''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT,
                    pattern_type TEXT,
                    confidence REAL,
                    description TEXT,
                    nodes TEXT,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'libraries': '''
                CREATE TABLE IF NOT EXISTS libraries (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT,
                    name TEXT,
                    version TEXT,
                    category TEXT,
                    usage_count INTEGER,
                    usage_contexts TEXT,
                    import_statements TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'infrastructure': '''
                CREATE TABLE IF NOT EXISTS infrastructure (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT,
                    component_type TEXT,
                    name TEXT,
                    technology TEXT,
                    configuration TEXT,
                    usage_frequency INTEGER,
                    connections TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        }
        
        for table_name, create_sql in new_tables.items():
            try:
                # Validate table name to prevent SQL injection
                safe_table_name = validate_sql_identifier(table_name)
                # Use parameterized query for table existence check
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (safe_table_name,))
                if not cursor.fetchone():
                    cursor.execute(create_sql)
                    log_info(f"✓ Created new table '{safe_table_name}'")
            except SecurityError as e:
                log_warning(f"Invalid table name '{table_name}': {e}")
            except sqlite3.Error as e:
                log_warning(f"Could not create table '{table_name}': {e}")
    
    
    @property
    def llm_enhancer(self) -> LLMMetadataEnhancer:
        """Get or create LLM metadata enhancer (lazy initialization)"""
        if self._llm_enhancer is None:
            self._llm_enhancer = LLMMetadataEnhancer(self.db_path)
        return self._llm_enhancer
    
    def enhance_metadata(self, limit: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Enhance metadata using LLM analysis
        
        Args:
            limit: Limit number of nodes to analyze
            force_refresh: Force re-analysis even if cached
            
        Returns:
            Analysis summary with statistics
        """
        log_info("🤖 Starting LLM-driven metadata enhancement...")
        return self.llm_enhancer.analyze_codebase(limit=limit, force_refresh=force_refresh)
    
    def query_enhanced_nodes(self, 
                           architectural_layer: Optional[str] = None,
                           business_domain: Optional[str] = None,
                           criticality_level: Optional[str] = None,
                           min_complexity: Optional[float] = None,
                           limit: int = 50) -> List[Dict[str, Any]]:
        """
        Query nodes with enhanced metadata
        
        Args:
            architectural_layer: Filter by layer (controller, service, model, etc.)
            business_domain: Filter by domain (authentication, payment, etc.)
            criticality_level: Filter by criticality (critical, important, normal, low)
            min_complexity: Filter by minimum complexity score
            limit: Maximum results to return
            
        Returns:
            List of enhanced node data
        """
        return self.llm_enhancer.get_enhanced_nodes(
            architectural_layer=architectural_layer,
            business_domain=business_domain,
            criticality_level=criticality_level,
            min_complexity=min_complexity,
            limit=limit
        )
    
    def update_node_metadata(self, node_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update enhanced metadata for a specific node
        
        Args:
            node_id: ID of the node to update
            updates: Dictionary of field updates
            
        Returns:
            True if successful
        """
        return self.llm_enhancer.update_node_metadata(node_id, updates)
    
    def get_analysis_insights(self) -> Dict[str, Any]:
        """
        Get high-level insights from enhanced metadata analysis
        
        Returns:
            Comprehensive insights about codebase health and architecture
        """
        return self.llm_enhancer.get_analysis_insights()
    
    def get_complexity_hotspots(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get nodes with highest complexity scores
        
        Args:
            limit: Maximum number of hotspots to return
            
        Returns:
            List of complexity hotspots
        """
        insights = self.llm_enhancer.get_analysis_insights()
        return insights.get("complexity_hotspots", [])[:limit]
    
    def get_critical_components(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most critical components in the codebase
        
        Args:
            limit: Maximum number of components to return
            
        Returns:
            List of critical components
        """
        return self.query_enhanced_nodes(
            criticality_level="critical",
            limit=limit
        )
    
    def get_architectural_overview(self) -> Dict[str, Any]:
        """
        Get architectural overview of the codebase
        
        Returns:
            Architectural insights and layer distribution
        """
        insights = self.llm_enhancer.get_analysis_insights()
        return insights.get("architectural_overview", {})
    
    def get_codebase_health(self) -> Dict[str, Any]:
        """
        Get overall codebase health assessment
        
        Returns:
            Health metrics and recommendations
        """
        insights = self.llm_enhancer.get_analysis_insights()
        return insights.get("codebase_health", {})
    
    def _get_schema_version_from_package(self) -> str:
        """
        Determine the appropriate schema version based on package version.
        
        Returns:
            Schema version string (e.g., '1.14.0')
        """
        # Map package versions to schema versions
        # This allows us to control when schema changes happen
        package_version = __version__
        
        # Extract major.minor.patch
        try:
            parts = package_version.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            
            # Determine schema version based on features
            if major >= 1 and minor >= 16:
                return '1.16.0'  # Search optimizations and FTS5
            elif major >= 1 and minor >= 15:
                return '1.15.0'  # Fixed enhanced_metadata schema
            elif major >= 1 and minor >= 14:
                return '1.14.0'  # LLM enhancement tables
            elif major >= 1 and minor >= 6:
                return '1.6.0'   # Language support
            elif major >= 1 and minor >= 1:
                return '1.1.0'   # Pattern detection
            else:
                return '1.0.0'   # Basic schema
        except Exception:
            # Default to latest schema version
            return '1.16.0'