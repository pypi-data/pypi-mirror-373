#!/usr/bin/env python3
"""
Library, SDK, and Infrastructure Detection
"""

import ast
import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import json
from .logger import log_warning


@dataclass
class LibraryUsage:
    name: str
    version: Optional[str]
    category: str  # 'web', 'ml', 'db', 'testing', 'cloud', etc.
    usage_count: int
    usage_contexts: List[str]
    import_statements: List[str]


class LibraryDetector:
    """Detect library/SDK usage and infrastructure patterns"""
    
    def __init__(self):
        # Known libraries categorized
        self.library_categories = {
            # Web frameworks
            'web': {
                'flask', 'django', 'fastapi', 'tornado', 'pyramid', 'bottle',
                'requests', 'httpx', 'aiohttp', 'urllib3', 'selenium',
                'streamlit', 'dash', 'gradio'
            },
            
            # Machine Learning
            'ml': {
                'tensorflow', 'pytorch', 'sklearn', 'scikit-learn', 'pandas',
                'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly',
                'transformers', 'huggingface_hub', 'openai', 'anthropic',
                'langchain', 'llamaindex', 'chromadb', 'pinecone'
            },
            
            # Database
            'database': {
                'sqlalchemy', 'pymongo', 'redis', 'psycopg2', 'mysql-connector',
                'sqlite3', 'elasticsearch', 'neo4j', 'cassandra-driver',
                'motor', 'asyncpg', 'aiomysql'
            },
            
            # Cloud & Infrastructure
            'cloud': {
                'boto3', 'azure', 'google-cloud', 'kubernetes', 'docker',
                'terraform', 'ansible', 'packer', 'consul', 'vault'
            },
            
            # Testing
            'testing': {
                'pytest', 'unittest', 'nose', 'mock', 'coverage',
                'hypothesis', 'factory_boy', 'faker', 'responses'
            },
            
            # API & Communication
            'api': {
                'grpc', 'protobuf', 'graphql', 'strawberry', 'ariadne',
                'celery', 'rq', 'kombu', 'pika', 'kafka-python'
            },
            
            # Data Processing
            'data': {
                'spark', 'dask', 'ray', 'polars', 'pyarrow', 'openpyxl',
                'xlsxwriter', 'beautifulsoup4', 'lxml', 'scrapy'
            },
            
            # Security
            'security': {
                'cryptography', 'pycryptodome', 'passlib', 'bcrypt',
                'pyjwt', 'authlib', 'oauthlib'
            },
            
            # Configuration & Logging
            'config': {
                'pydantic', 'marshmallow', 'cerberus', 'voluptuous',
                'loguru', 'structlog', 'python-dotenv', 'configparser'
            }
        }
        
        # Infrastructure patterns
        self.infra_patterns = {
            'database_connections': [
                r'connect\(',
                r'engine\s*=',
                r'Session\(',
                r'connection\s*=',
                r'client\s*=.*Client\('
            ],
            'api_endpoints': [
                r'@app\.route',
                r'@router\.',
                r'@api\.',
                r'app\.add_url_rule',
                r'@get\(|@post\(|@put\(|@delete\('
            ],
            'config_loading': [
                r'\.env',
                r'config\.py',
                r'settings\.py',
                r'os\.environ',
                r'getenv\(',
                r'load_dotenv\('
            ],
            'logging_setup': [
                r'logging\.getLogger',
                r'logger\s*=',
                r'log\.',
                r'\.info\(|\.error\(|\.debug\(|\.warning\('
            ]
        }
    
    def detect_libraries(self, tree: ast.AST, file_path: str, file_content: str) -> Dict[str, LibraryUsage]:
        """Detect all library usage in the file"""
        libraries = {}
        
        # Handle None or invalid AST
        if tree is None:
            return libraries
        
        try:
            # Extract imports
            import_info = self._extract_imports(tree)
            
            # Categorize and count usage
            for import_name, import_details in import_info.items():
                category = self._categorize_library(import_name)
                usage_count = self._count_usage(import_name, file_content)
                version = self._extract_version(import_name, file_content)
                contexts = self._extract_usage_contexts(import_name, tree)
                
                libraries[import_name] = LibraryUsage(
                    name=import_name,
                    version=version,
                    category=category,
                    usage_count=usage_count,
                    usage_contexts=contexts,
                    import_statements=import_details['statements']
                )
        except (AttributeError, TypeError) as e:
            # Handle malformed AST gracefully
            log_warning(f"Could not detect libraries in {file_path}: {e}")
        
        return libraries
    
    def detect_infrastructure(self, tree: ast.AST, file_content: str) -> Dict[str, List[str]]:
        """Detect infrastructure patterns"""
        infra = {}
        
        for pattern_type, patterns in self.infra_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, file_content, re.IGNORECASE | re.MULTILINE)
                matches.extend(found)
            
            if matches:
                infra[pattern_type] = list(set(matches))  # Remove duplicates
        
        return infra
    
    def _extract_imports(self, tree: ast.AST) -> Dict[str, Dict]:
        """Extract all import statements and their details"""
        imports = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base_name = alias.name.split('.')[0]
                    if base_name not in imports:
                        imports[base_name] = {
                            'full_name': alias.name,
                            'alias': alias.asname,
                            'statements': []
                        }
                    imports[base_name]['statements'].append(f"import {alias.name}")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base_name = node.module.split('.')[0]
                    if base_name not in imports:
                        imports[base_name] = {
                            'full_name': node.module,
                            'alias': None,
                            'statements': []
                        }
                    
                    for alias in node.names:
                        stmt = f"from {node.module} import {alias.name}"
                        if alias.asname:
                            stmt += f" as {alias.asname}"
                        imports[base_name]['statements'].append(stmt)
        
        return imports
    
    def _categorize_library(self, library_name: str) -> str:
        """Categorize library by type"""
        library_lower = library_name.lower().replace('-', '').replace('_', '')
        
        for category, libraries in self.library_categories.items():
            for lib in libraries:
                lib_clean = lib.lower().replace('-', '').replace('_', '')
                if lib_clean in library_lower or library_lower in lib_clean:
                    return category
        
        return 'other'
    
    def _count_usage(self, library_name: str, file_content: str) -> int:
        """Count how many times library is used"""
        # Count direct usage patterns
        patterns = [
            rf'\b{re.escape(library_name)}\.',  # library.method()
            rf'\b{re.escape(library_name)}\[',  # library[key]
            rf'\b{re.escape(library_name)}\(',  # library()
        ]
        
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, file_content, re.IGNORECASE))
        
        return count
    
    def _extract_version(self, library_name: str, file_content: str) -> Optional[str]:
        """Try to extract version information"""
        # Look for version strings
        version_patterns = [
            rf'{re.escape(library_name)}[=<>!]+([0-9.]+)',
            rf'version\s*=\s*["\']([0-9.]+)["\']',
            rf'__version__\s*=\s*["\']([0-9.]+)["\']'
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, file_content, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_usage_contexts(self, library_name: str, tree: ast.AST) -> List[str]:
        """Extract contexts where library is used"""
        contexts = []
        
        for node in ast.walk(tree):
            # Check function definitions that use the library
            if isinstance(node, ast.FunctionDef):
                func_source = ast.unparse(node) if hasattr(ast, 'unparse') else ''
                if library_name in func_source:
                    contexts.append(f"function:{node.name}")
            
            # Check class definitions
            elif isinstance(node, ast.ClassDef):
                class_source = ast.unparse(node) if hasattr(ast, 'unparse') else ''
                if library_name in class_source:
                    contexts.append(f"class:{node.name}")
        
        return list(set(contexts))  # Remove duplicates
    
    def detect_sdk_patterns(self, tree: ast.AST, file_content: str) -> Dict[str, Dict]:
        """Detect SDK usage patterns"""
        sdk_patterns = {}
        
        # Common SDK patterns
        patterns = {
            'aws': {
                'keywords': ['boto3', 'aws', 's3', 'lambda', 'dynamodb', 'ec2'],
                'patterns': [r'boto3\.client\(', r'aws_', r'\.s3\.', r'\.lambda\.']
            },
            'gcp': {
                'keywords': ['google-cloud', 'gcp', 'bigquery', 'firestore'],
                'patterns': [r'google\.cloud', r'gcp_', r'bigquery\.', r'firestore\.']
            },
            'azure': {
                'keywords': ['azure', 'microsoft'],
                'patterns': [r'azure\.', r'microsoft\.', r'azure_']
            },
            'openai': {
                'keywords': ['openai', 'gpt', 'chatgpt'],
                'patterns': [r'openai\.', r'ChatCompletion', r'gpt-']
            },
            'anthropic': {
                'keywords': ['anthropic', 'claude'],
                'patterns': [r'anthropic\.', r'claude', r'messages\.create']
            }
        }
        
        for sdk_name, config in patterns.items():
            matches = []
            
            # Check keywords in imports and code
            for keyword in config['keywords']:
                if keyword.lower() in file_content.lower():
                    matches.append(f"keyword:{keyword}")
            
            # Check patterns
            for pattern in config['patterns']:
                found = re.findall(pattern, file_content, re.IGNORECASE)
                matches.extend([f"pattern:{p}" for p in found])
            
            if matches:
                sdk_patterns[sdk_name] = {
                    'usage_count': len(matches),
                    'contexts': matches[:10]  # Limit to first 10
                }
        
        return sdk_patterns