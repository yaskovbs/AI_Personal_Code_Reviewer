"""
Code Analyzer Module
מנתח קוד ראשי - מנתח את הקוד ומחלץ מידע חשוב
"""

import ast
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class CodeAnalysisResult:
    """תוצאת ניתוח קוד"""
    file_path: str
    language: str
    metrics: Dict[str, Any]
    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    style_patterns: Dict[str, Any]

class CodeAnalyzer:
    """מנתח קוד ראשי"""
    
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'java', 'cpp', 'csharp']
        self.analysis_cache = {}
        
    def analyze_code(self, code: str, language: str = 'python', 
                     file_path: str = None) -> CodeAnalysisResult:
        """
        מנתח קוד ומחזיר תוצאות מפורטות
        """
        if language not in self.supported_languages:
            language = self.detect_language(code)
        
        # Check cache
        cache_key = f"{file_path}:{hash(code)}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Perform analysis based on language
        if language == 'python':
            result = self._analyze_python(code, file_path)
        else:
            result = self._analyze_generic(code, language, file_path)
        
        # Cache result
        self.analysis_cache[cache_key] = result
        return result
    
    def _analyze_python(self, code: str, file_path: str) -> CodeAnalysisResult:
        """ניתוח קוד Python"""
        metrics = self._calculate_python_metrics(code)
        issues = self._find_python_issues(code)
        suggestions = self._generate_python_suggestions(code, metrics, issues)
        style_patterns = self._extract_style_patterns(code)
        
        return CodeAnalysisResult(
            file_path=file_path or "unnamed.py",
            language="python",
            metrics=metrics,
            issues=issues,
            suggestions=suggestions,
            style_patterns=style_patterns
        )
    
    def _calculate_python_metrics(self, code: str) -> Dict[str, Any]:
        """חישוב מטריקות לקוד Python"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {'error': str(e)}
        
        metrics = {
            'lines_of_code': len(code.splitlines()),
            'num_functions': 0,
            'num_classes': 0,
            'num_imports': 0,
            'complexity': 0,
            'max_line_length': max(len(line) for line in code.splitlines()) if code else 0,
            'num_comments': len(re.findall(r'#.*', code)),
            'docstring_coverage': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['num_functions'] += 1
                metrics['complexity'] += self._calculate_complexity(node)
                if ast.get_docstring(node):
                    metrics['docstring_coverage'] += 1
            elif isinstance(node, ast.ClassDef):
                metrics['num_classes'] += 1
                if ast.get_docstring(node):
                    metrics['docstring_coverage'] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics['num_imports'] += 1
        
        # Calculate docstring coverage percentage
        total_definitions = metrics['num_functions'] + metrics['num_classes']
        if total_definitions > 0:
            metrics['docstring_coverage'] = (metrics['docstring_coverage'] / total_definitions) * 100
        
        return metrics
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """חישוב מורכבות ציקלומטית"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _find_python_issues(self, code: str) -> List[Dict[str, Any]]:
        """מציאת בעיות בקוד Python"""
        issues = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [{'type': 'syntax_error', 'message': str(e), 'severity': 'error'}]
        
        # Check for common issues
        for node in ast.walk(tree):
            # Unused imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not self._is_name_used(alias.name, tree):
                        issues.append({
                            'type': 'unused_import',
                            'message': f"Unused import: {alias.name}",
                            'line': node.lineno,
                            'severity': 'warning'
                        })
            
            # Empty except blocks
            if isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    issues.append({
                        'type': 'empty_except',
                        'message': "Empty except block",
                        'line': node.lineno,
                        'severity': 'warning'
                    })
        
        # Check for long lines
        for i, line in enumerate(code.splitlines(), 1):
            if len(line) > 100:
                issues.append({
                    'type': 'long_line',
                    'message': f"Line too long ({len(line)} > 100)",
                    'line': i,
                    'severity': 'info'
                })
        
        return issues
    
    def _is_name_used(self, name: str, tree: ast.AST) -> bool:
        """בדיקה האם שם משתמש בקוד"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == name:
                return True
        return False
    
    def _generate_python_suggestions(self, code: str, metrics: Dict, 
                                    issues: List) -> List[Dict[str, Any]]:
        """יצירת המלצות לשיפור קוד Python"""
        suggestions = []
        
        # Complexity suggestions
        if metrics.get('complexity', 0) > 10:
            suggestions.append({
                'type': 'refactor',
                'message': 'Consider breaking down complex functions',
                'priority': 'high'
            })
        
        # Documentation suggestions
        if metrics.get('docstring_coverage', 0) < 50:
            suggestions.append({
                'type': 'documentation',
                'message': 'Add docstrings to functions and classes',
                'priority': 'medium'
            })
        
        # Import organization
        if metrics.get('num_imports', 0) > 10:
            suggestions.append({
                'type': 'organization',
                'message': 'Consider organizing imports',
                'priority': 'low'
            })
        
        return suggestions
    
    def _extract_style_patterns(self, code: str) -> Dict[str, Any]:
        """חילוץ דפוסי סגנון מהקוד"""
        patterns = {
            'naming_convention': self._detect_naming_convention(code),
            'indentation': self._detect_indentation(code),
            'quote_style': self._detect_quote_style(code),
            'spacing': self._detect_spacing_style(code)
        }
        return patterns
    
    def _detect_naming_convention(self, code: str) -> str:
        """זיהוי סגנון שמות"""
        snake_case = len(re.findall(r'\b[a-z]+_[a-z]+\b', code))
        camel_case = len(re.findall(r'\b[a-z]+[A-Z][a-z]+\b', code))
        
        if snake_case > camel_case:
            return 'snake_case'
        elif camel_case > snake_case:
            return 'camelCase'
        return 'mixed'
    
    def _detect_indentation(self, code: str) -> str:
        """זיהוי סגנון הזחה"""
        spaces_2 = len(re.findall(r'\n  [^ ]', code))
        spaces_4 = len(re.findall(r'\n    [^ ]', code))
        tabs = len(re.findall(r'\n\t', code))
        
        if tabs > spaces_2 and tabs > spaces_4:
            return 'tabs'
        elif spaces_4 > spaces_2:
            return '4_spaces'
        return '2_spaces'
    
    def _detect_quote_style(self, code: str) -> str:
        """זיהוי סגנון מרכאות"""
        single = len(re.findall(r"'[^']*'", code))
        double = len(re.findall(r'"[^"]*"', code))
        
        if single > double:
            return 'single'
        return 'double'
    
    def _detect_spacing_style(self, code: str) -> Dict[str, bool]:
        """זיהוי סגנון רווחים"""
        return {
            'spaces_around_operators': bool(re.search(r'\s[+\-*/=]\s', code)),
            'spaces_after_comma': bool(re.search(r',\s', code)),
            'blank_lines_between_functions': bool(re.search(r'\n\n\s*def\s', code))
        }
    
    def _analyze_generic(self, code: str, language: str, 
                        file_path: str) -> CodeAnalysisResult:
        """ניתוח גנרי לשפות אחרות"""
        metrics = {
            'lines_of_code': len(code.splitlines()),
            'max_line_length': max(len(line) for line in code.splitlines()) if code else 0,
            'language': language
        }
        
        return CodeAnalysisResult(
            file_path=file_path or f"unnamed.{language}",
            language=language,
            metrics=metrics,
            issues=[],
            suggestions=[],
            style_patterns={}
        )
    
    def detect_language(self, code: str) -> str:
        """זיהוי שפת התכנות"""
        if 'def ' in code or 'import ' in code:
            return 'python'
        elif 'function' in code or 'const ' in code or 'let ' in code:
            return 'javascript'
        elif 'public class' in code or 'public static void' in code:
            return 'java'
        elif '#include' in code or 'int main(' in code:
            return 'cpp'
        elif 'using System' in code or 'namespace ' in code:
            return 'csharp'
        return 'unknown'
    
    def is_ready(self) -> bool:
        """בדיקת מוכנות המנתח"""
        return True
