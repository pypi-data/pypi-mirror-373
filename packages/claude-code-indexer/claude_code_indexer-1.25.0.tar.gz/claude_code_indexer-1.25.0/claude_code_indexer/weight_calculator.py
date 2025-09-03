#!/usr/bin/env python3
"""
Weight calculation based on usage frequency and relationships
"""

import ast
import re
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass
import networkx as nx


@dataclass
class WeightedRelationship:
    source: str
    target: str
    relationship_type: str
    weight: float
    frequency: int
    contexts: List[str]


class WeightCalculator:
    """Calculate weights for nodes and edges based on usage frequency"""
    
    def __init__(self):
        self.call_frequency = defaultdict(int)
        self.import_frequency = defaultdict(int)
        self.inheritance_frequency = defaultdict(int)
        self.method_calls = defaultdict(list)
        self.class_instantiations = defaultdict(int)
        self.function_calls = defaultdict(int)
        
    def calculate_weights(self, nodes: Dict, edges: List, all_files_content: Dict[str, str]) -> Tuple[Dict, List[WeightedRelationship]]:
        """Calculate weights for all nodes and edges"""
        
        # Count frequencies across all files
        self._count_frequencies(all_files_content, nodes)
        
        # Calculate node weights
        weighted_nodes = self._calculate_node_weights(nodes)
        
        # Calculate edge weights
        weighted_edges = self._calculate_edge_weights(edges, nodes)
        
        return weighted_nodes, weighted_edges
    
    def _count_frequencies(self, all_files_content: Dict[str, str], nodes: Dict):
        """Count usage frequencies across all files"""
        
        for file_path, content in all_files_content.items():
            try:
                tree = ast.parse(content)
                self._analyze_ast_for_frequencies(tree, content, nodes)
            except SyntaxError:
                continue  # Skip files with syntax errors
    
    def _analyze_ast_for_frequencies(self, tree: ast.AST, content: str, nodes: Dict):
        """Analyze AST to count frequencies"""
        
        for node in ast.walk(tree):
            # Count function calls
            if isinstance(node, ast.Call):
                func_name = self._extract_function_name(node)
                if func_name:
                    self.function_calls[func_name] += 1
                    
                    # Track method calls
                    if isinstance(node.func, ast.Attribute):
                        obj_name = self._extract_object_name(node.func.value)
                        if obj_name:
                            self.method_calls[obj_name].append(func_name)
            
            # Count class instantiations
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                class_name = node.func.id
                # Check if it's a class (starts with uppercase)
                if class_name[0].isupper():
                    self.class_instantiations[class_name] += 1
            
            # Count imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.import_frequency[alias.name] += 1
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.import_frequency[node.module] += 1
                    for alias in node.names:
                        self.import_frequency[f"{node.module}.{alias.name}"] += 1
            
            # Count inheritance
            elif isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        self.inheritance_frequency[base.id] += 1
    
    def _extract_function_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract function name from call node"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None
    
    def _extract_object_name(self, node: ast.AST) -> Optional[str]:
        """Extract object name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
    
    def _calculate_node_weights(self, nodes: Dict) -> Dict:
        """Calculate weights for nodes based on usage frequency"""
        weighted_nodes = {}
        
        # Find max frequencies for normalization
        max_call_freq = max(self.function_calls.values()) if self.function_calls else 1
        max_import_freq = max(self.import_frequency.values()) if self.import_frequency else 1
        max_class_freq = max(self.class_instantiations.values()) if self.class_instantiations else 1
        
        for node_id, node_info in nodes.items():
            node_name = node_info['name']
            node_type = node_info['node_type']
            
            # Base weight
            weight = node_info.get('importance_score', 0.0)
            
            # Add frequency-based weights
            frequency_weight = 0.0
            
            if node_type == 'function' or node_type == 'method':
                # Weight based on how often the function is called
                call_count = self.function_calls.get(node_name, 0)
                frequency_weight = (call_count / max_call_freq) * 0.3
                
            elif node_type == 'class':
                # Weight based on instantiation and inheritance
                instantiation_count = self.class_instantiations.get(node_name, 0)
                inheritance_count = self.inheritance_frequency.get(node_name, 0)
                
                frequency_weight = (
                    (instantiation_count / max_class_freq) * 0.2 +
                    (inheritance_count / max_class_freq) * 0.1
                )
                
            elif node_type == 'import':
                # Weight based on import frequency
                import_count = self.import_frequency.get(node_name, 0)
                frequency_weight = (import_count / max_import_freq) * 0.2
            
            elif node_type == 'file':
                # Weight based on how many other files import/reference it
                file_references = sum(1 for call in self.function_calls.keys() 
                                    if node_name.replace('.py', '') in call)
                frequency_weight = min(file_references / 10.0, 0.3)  # Cap at 0.3
            
            # Combine weights
            total_weight = min(weight + frequency_weight, 1.0)  # Cap at 1.0
            
            # Update node info
            weighted_node = node_info.copy()
            weighted_node['weight'] = total_weight
            weighted_node['frequency_score'] = frequency_weight
            weighted_node['usage_stats'] = self._get_usage_stats(node_name, node_type)
            
            weighted_nodes[node_id] = weighted_node
        
        return weighted_nodes
    
    def _get_usage_stats(self, node_name: str, node_type: str) -> Dict:
        """Get detailed usage statistics for a node"""
        stats = {
            'call_count': 0,
            'import_count': 0,
            'instantiation_count': 0,
            'inheritance_count': 0
        }
        
        if node_type in ['function', 'method']:
            stats['call_count'] = self.function_calls.get(node_name, 0)
        elif node_type == 'class':
            stats['instantiation_count'] = self.class_instantiations.get(node_name, 0)
            stats['inheritance_count'] = self.inheritance_frequency.get(node_name, 0)
        elif node_type == 'import':
            stats['import_count'] = self.import_frequency.get(node_name, 0)
        
        return stats
    
    def _calculate_edge_weights(self, edges: List, nodes: Dict) -> List[WeightedRelationship]:
        """Calculate weights for edges based on relationship frequency"""
        weighted_edges = []
        
        # Count edge frequencies
        edge_frequency = defaultdict(int)
        edge_contexts = defaultdict(list)
        
        for source, target, relationship_type in edges:
            edge_key = (source, target, relationship_type)
            edge_frequency[edge_key] += 1
            
            # Add context information
            source_node = nodes.get(source, {})
            target_node = nodes.get(target, {})
            context = f"{source_node.get('node_type', 'unknown')}→{target_node.get('node_type', 'unknown')}"
            edge_contexts[edge_key].append(context)
        
        # Calculate weights
        max_edge_freq = max(edge_frequency.values()) if edge_frequency else 1
        
        for (source, target, relationship_type), frequency in edge_frequency.items():
            # Base weight based on relationship type
            base_weights = {
                'imports': 0.3,
                'calls': 0.5,
                'inherits': 0.7,
                'contains': 0.4,
                'uses': 0.6
            }
            
            base_weight = base_weights.get(relationship_type, 0.3)
            
            # Frequency-based weight
            frequency_weight = (frequency / max_edge_freq) * 0.5
            
            # Node importance influence
            source_weight = nodes.get(source, {}).get('weight', 0.0)
            target_weight = nodes.get(target, {}).get('weight', 0.0)
            importance_weight = (source_weight + target_weight) / 4.0  # Average, scaled down
            
            # Combined weight
            total_weight = min(base_weight + frequency_weight + importance_weight, 1.0)
            
            weighted_edges.append(WeightedRelationship(
                source=source,
                target=target,
                relationship_type=relationship_type,
                weight=total_weight,
                frequency=frequency,
                contexts=list(set(edge_contexts[(source, target, relationship_type)]))
            ))
        
        return weighted_edges
    
    def calculate_centrality_weights(self, nodes: Dict, edges: List[WeightedRelationship]) -> Dict:
        """Calculate centrality-based weights using NetworkX"""
        
        # Create weighted graph
        G = nx.DiGraph()
        
        # Add nodes
        for node_id, node_info in nodes.items():
            G.add_node(node_id, **node_info)
        
        # Add weighted edges
        for edge in edges:
            G.add_edge(edge.source, edge.target, 
                      weight=edge.weight, 
                      relationship_type=edge.relationship_type)
        
        # Calculate various centrality measures
        centralities = {}
        
        try:
            # Weighted PageRank
            pagerank = nx.pagerank(G, weight='weight', alpha=0.85)
            centralities['pagerank'] = pagerank
        except:
            centralities['pagerank'] = {node: 0.0 for node in G.nodes()}
        
        try:
            # Betweenness centrality
            betweenness = nx.betweenness_centrality(G, weight='weight')
            centralities['betweenness'] = betweenness
        except:
            centralities['betweenness'] = {node: 0.0 for node in G.nodes()}
        
        try:
            # Closeness centrality
            closeness = nx.closeness_centrality(G, distance='weight')
            centralities['closeness'] = closeness
        except:
            centralities['closeness'] = {node: 0.0 for node in G.nodes()}
        
        try:
            # Eigenvector centrality
            eigenvector = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
            centralities['eigenvector'] = eigenvector
        except:
            centralities['eigenvector'] = {node: 0.0 for node in G.nodes()}
        
        # Combine centralities into final weights
        final_weights = {}
        for node_id in nodes.keys():
            # Weighted combination of centralities
            combined_centrality = (
                centralities['pagerank'].get(node_id, 0.0) * 0.4 +
                centralities['betweenness'].get(node_id, 0.0) * 0.3 +
                centralities['closeness'].get(node_id, 0.0) * 0.2 +
                centralities['eigenvector'].get(node_id, 0.0) * 0.1
            )
            
            # Combine with existing node weight
            existing_weight = nodes[node_id].get('weight', 0.0)
            final_weight = (existing_weight * 0.6 + combined_centrality * 0.4)
            
            final_weights[node_id] = {
                'final_weight': min(final_weight, 1.0),
                'centrality_scores': {
                    'pagerank': centralities['pagerank'].get(node_id, 0.0),
                    'betweenness': centralities['betweenness'].get(node_id, 0.0),
                    'closeness': centralities['closeness'].get(node_id, 0.0),
                    'eigenvector': centralities['eigenvector'].get(node_id, 0.0)
                }
            }
        
        return final_weights