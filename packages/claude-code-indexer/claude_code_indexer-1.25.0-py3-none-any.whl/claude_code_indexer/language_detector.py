#!/usr/bin/env python3
"""
Language Detection for Multi-Language Code Indexing
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

@dataclass
class LanguageInfo:
    """Information about a programming language"""
    name: str
    extensions: List[str]
    comment_styles: List[str]
    keywords: List[str]
    parser_available: bool = False

class LanguageDetector:
    """Detects programming languages and provides language-specific information"""
    
    def __init__(self):
        self.languages = {
            'python': LanguageInfo(
                name='Python',
                extensions=['.py', '.pyx', '.pyi', '.pyw'],
                comment_styles=['#'],
                keywords=['def', 'class', 'import', 'from', 'if', 'else', 'for', 'while', 'try', 'except'],
                parser_available=True
            ),
            'javascript': LanguageInfo(
                name='JavaScript',
                extensions=['.js', '.mjs', '.cjs'],
                comment_styles=['//', '/*'],
                keywords=['function', 'class', 'const', 'let', 'var', 'import', 'export', 'if', 'else', 'for', 'while', 'try', 'catch'],
                parser_available=True
            ),
            'typescript': LanguageInfo(
                name='TypeScript',
                extensions=['.ts', '.tsx'],
                comment_styles=['//', '/*'],
                keywords=['function', 'class', 'interface', 'type', 'const', 'let', 'var', 'import', 'export', 'if', 'else', 'for', 'while', 'try', 'catch'],
                parser_available=True
            ),
            'java': LanguageInfo(
                name='Java',
                extensions=['.java'],
                comment_styles=['//', '/*'],
                keywords=['public', 'private', 'class', 'interface', 'import', 'package', 'if', 'else', 'for', 'while', 'try', 'catch'],
                parser_available=True
            ),
            'csharp': LanguageInfo(
                name='C#',
                extensions=['.cs'],
                comment_styles=['//', '/*'],
                keywords=['public', 'private', 'class', 'interface', 'using', 'namespace', 'if', 'else', 'for', 'while', 'try', 'catch']
            ),
            'cpp': LanguageInfo(
                name='C++',
                extensions=['.cpp', '.cc', '.cxx', '.hpp', '.h'],
                comment_styles=['//', '/*'],
                keywords=['class', 'struct', 'namespace', 'include', 'if', 'else', 'for', 'while', 'try', 'catch']
            ),
            'c': LanguageInfo(
                name='C',
                extensions=['.c', '.h'],
                comment_styles=['/*'],
                keywords=['struct', 'typedef', 'include', 'if', 'else', 'for', 'while']
            ),
            'go': LanguageInfo(
                name='Go',
                extensions=['.go'],
                comment_styles=['//', '/*'],
                keywords=['func', 'type', 'struct', 'interface', 'package', 'import', 'if', 'else', 'for', 'range']
            ),
            'rust': LanguageInfo(
                name='Rust',
                extensions=['.rs'],
                comment_styles=['//', '/*'],
                keywords=['fn', 'struct', 'enum', 'impl', 'trait', 'use', 'mod', 'if', 'else', 'for', 'while', 'match'],
                parser_available=True
            ),
            'ruby': LanguageInfo(
                name='Ruby',
                extensions=['.rb'],
                comment_styles=['#'],
                keywords=['def', 'class', 'module', 'require', 'if', 'else', 'for', 'while', 'begin', 'rescue']
            ),
            'php': LanguageInfo(
                name='PHP',
                extensions=['.php', '.phtml'],
                comment_styles=['//', '/*', '#'],
                keywords=['function', 'class', 'interface', 'require', 'include', 'if', 'else', 'for', 'while', 'try', 'catch']
            ),
            'swift': LanguageInfo(
                name='Swift',
                extensions=['.swift'],
                comment_styles=['//', '/*'],
                keywords=['func', 'class', 'struct', 'protocol', 'import', 'if', 'else', 'for', 'while', 'do', 'try', 'catch']
            ),
            'kotlin': LanguageInfo(
                name='Kotlin',
                extensions=['.kt', '.kts'],
                comment_styles=['//', '/*'],
                keywords=['fun', 'class', 'interface', 'object', 'import', 'package', 'if', 'else', 'for', 'while', 'try', 'catch']
            ),
            'scala': LanguageInfo(
                name='Scala',
                extensions=['.scala'],
                comment_styles=['//', '/*'],
                keywords=['def', 'class', 'object', 'trait', 'import', 'package', 'if', 'else', 'for', 'while', 'try', 'catch']
            ),
            'dart': LanguageInfo(
                name='Dart',
                extensions=['.dart'],
                comment_styles=['//', '/*'],
                keywords=['class', 'abstract', 'interface', 'import', 'library', 'if', 'else', 'for', 'while', 'try', 'catch']
            )
        }
        
        # Build reverse mapping from extensions to languages
        self.extension_to_language = {}
        for lang_id, lang_info in self.languages.items():
            for ext in lang_info.extensions:
                self.extension_to_language[ext] = lang_id
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect the programming language of a file"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # First try extension-based detection
        if extension in self.extension_to_language:
            return self.extension_to_language[extension]
        
        # For files without extensions, try content-based detection
        if not extension:
            return self._detect_by_content(file_path)
        
        return None
    
    def _detect_by_content(self, file_path: str) -> Optional[str]:
        """Detect language by analyzing file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 characters
        except (UnicodeDecodeError, IOError):
            return None
        
        # Look for shebangs
        if content.startswith('#!'):
            first_line = content.split('\n')[0]
            if 'python' in first_line:
                return 'python'
            elif 'node' in first_line:
                return 'javascript'
            elif 'ruby' in first_line:
                return 'ruby'
            elif 'php' in first_line:
                return 'php'
        
        # Score languages based on keyword frequency
        scores = {}
        for lang_id, lang_info in self.languages.items():
            score = 0
            for keyword in lang_info.keywords:
                score += content.lower().count(keyword.lower())
            if score > 0:
                scores[lang_id] = score
        
        # Return language with highest score
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def get_language_info(self, language: str) -> Optional[LanguageInfo]:
        """Get information about a specific language"""
        return self.languages.get(language)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.languages.keys())
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions"""
        extensions = []
        for lang_info in self.languages.values():
            extensions.extend(lang_info.extensions)
        return sorted(set(extensions))
    
    def is_supported_file(self, file_path: str) -> bool:
        """Check if a file is supported for indexing"""
        return self.detect_language(file_path) is not None
    
    def get_files_by_language(self, directory: str, ignored_patterns: Set[str] = None) -> Dict[str, List[str]]:
        """Get all supported files in a directory grouped by language"""
        if ignored_patterns is None:
            ignored_patterns = set()
        
        files_by_language = {}
        
        for root, dirs, files in os.walk(directory):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in ignored_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip ignored files
                if any(pattern in file_path for pattern in ignored_patterns):
                    continue
                
                language = self.detect_language(file_path)
                if language:
                    if language not in files_by_language:
                        files_by_language[language] = []
                    files_by_language[language].append(file_path)
        
        return files_by_language
    
    def get_language_statistics(self, directory: str, ignored_patterns: Set[str] = None) -> Dict[str, Dict[str, int]]:
        """Get statistics about languages in a directory"""
        files_by_language = self.get_files_by_language(directory, ignored_patterns)
        
        stats = {}
        for language, files in files_by_language.items():
            lang_info = self.get_language_info(language)
            stats[language] = {
                'name': lang_info.name,
                'file_count': len(files),
                'total_size': sum(os.path.getsize(f) for f in files if os.path.exists(f))
            }
        
        return stats