"""
Pattern Detector Module
מזהה דפוסים חוזרים בבאגים ובקוד
"""

import re
import ast
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import json
import os

class PatternDetector:
    """מזהה דפוסים חוזרים בקוד ובבאגים"""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.bug_patterns = self._load_bug_patterns()
        self.code_patterns = self._load_code_patterns()
        self.pattern_history = []
        
    def _load_bug_patterns(self) -> Dict[str, List[Dict]]:
        """טעינת דפוסי באגים ידועים"""
        patterns_file = f"data/patterns/{self.user_id}_bugs.json"
        
        if os.path.exists(patterns_file):
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default bug patterns
        return {
            'null_reference': [
                {'pattern': r'\.(\w+)\s*\(', 'description': 'Potential null reference'},
                {'pattern': r'\[(\w+)\]', 'description': 'Potential index out of bounds'}
            ],
            'resource_leak': [
                {'pattern': r'open\([^)]+\)(?!.*\.close)', 'description': 'File not closed'},
                {'pattern': r'connect\([^)]+\)(?!.*\.close)', 'description': 'Connection not closed'}
            ],
            'infinite_loop': [
                {'pattern': r'while\s+True:', 'description': 'Potential infinite loop'},
                {'pattern': r'while\s+1:', 'description': 'Potential infinite loop'}
            ],
            'exception_handling': [
                {'pattern': r'except:\s*pass', 'description': 'Silent exception swallowing'},
                {'pattern': r'except\s+Exception:', 'description': 'Too broad exception handling'}
            ]
        }
    
    def _load_code_patterns(self) -> Dict[str, Any]:
        """טעינת דפוסי קוד נפוצים"""
        patterns_file = f"data/patterns/{self.user_id}_code.json"
        
        if os.path.exists(patterns_file):
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'common_structures': [],
            'recurring_mistakes': [],
            'improvement_opportunities': []
        }
    
    def detect_patterns(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """זיהוי דפוסים בקוד"""
        results = {
            'bug_patterns': self._detect_bug_patterns(code),
            'code_smells': self._detect_code_smells(code, language),
            'recurring_patterns': self._detect_recurring_patterns(code),
            'anti_patterns': self._detect_anti_patterns(code, language),
            'security_issues': self._detect_security_issues(code)
        }
        
        # Update history
        self.pattern_history.append({
            'timestamp': datetime.now().isoformat(),
            'patterns_found': results,
            'language': language
        })
        
        # Learn from detected patterns
        self._learn_from_patterns(results)
        
        return results
    
    def _detect_bug_patterns(self, code: str) -> List[Dict[str, Any]]:
        """זיהוי דפוסי באגים פוטנציאליים"""
        detected = []
        
        for bug_type, patterns in self.bug_patterns.items():
            for pattern_info in patterns:
                matches = re.finditer(pattern_info['pattern'], code)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    detected.append({
                        'type': bug_type,
                        'pattern': pattern_info['pattern'],
                        'description': pattern_info['description'],
                        'line': line_num,
                        'match': match.group(),
                        'severity': self._calculate_severity(bug_type)
                    })
        
        return detected
    
    def _detect_code_smells(self, code: str, language: str) -> List[Dict[str, Any]]:
        """זיהוי 'ריחות קוד' - קוד שצריך שיפור"""
        smells = []
        
        if language == 'python':
            smells.extend(self._detect_python_smells(code))
        
        # Generic smells
        smells.extend(self._detect_generic_smells(code))
        
        return smells
    
    def _detect_python_smells(self, code: str) -> List[Dict[str, Any]]:
        """זיהוי code smells ספציפיים ל-Python"""
        smells = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return smells
        
        for node in ast.walk(tree):
            # Long functions
            if isinstance(node, ast.FunctionDef):
                func_lines = self._count_function_lines(node)
                if func_lines > 50:
                    smells.append({
                        'type': 'long_function',
                        'name': node.name,
                        'lines': func_lines,
                        'suggestion': 'Consider breaking this function into smaller functions',
                        'line': node.lineno
                    })
            
            # Too many parameters
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 5:
                    smells.append({
                        'type': 'too_many_parameters',
                        'name': node.name,
                        'count': param_count,
                        'suggestion': 'Consider using a configuration object or reducing parameters',
                        'line': node.lineno
                    })
            
            # Nested loops
            if isinstance(node, ast.For):
                if self._has_nested_loop(node):
                    smells.append({
                        'type': 'nested_loops',
                        'suggestion': 'Consider extracting nested loops into separate functions',
                        'line': node.lineno
                    })
        
        return smells
    
    def _detect_generic_smells(self, code: str) -> List[Dict[str, Any]]:
        """זיהוי code smells גנריים"""
        smells = []
        lines = code.splitlines()
        
        # Duplicate code detection
        duplicates = self._find_duplicate_code(lines)
        for dup in duplicates:
            smells.append({
                'type': 'duplicate_code',
                'lines': dup['lines'],
                'suggestion': 'Consider extracting duplicate code into a function'
            })
        
        # Magic numbers
        magic_numbers = re.findall(r'\b\d{2,}\b', code)
        if magic_numbers:
            smells.append({
                'type': 'magic_numbers',
                'numbers': list(set(magic_numbers)),
                'suggestion': 'Consider using named constants instead of magic numbers'
            })
        
        # TODO comments
        todos = re.findall(r'#\s*TODO:?\s*(.*)', code, re.IGNORECASE)
        if todos:
            smells.append({
                'type': 'todo_comments',
                'todos': todos,
                'suggestion': 'Address TODO comments or track them in issue tracker'
            })
        
        return smells
    
    def _detect_recurring_patterns(self, code: str) -> List[Dict[str, Any]]:
        """זיהוי דפוסים חוזרים בקוד"""
        patterns = []
        
        # Find recurring code structures
        lines = code.splitlines()
        line_groups = defaultdict(list)
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) > 10:  # Ignore very short lines
                line_groups[stripped].append(i + 1)
        
        # Find lines that appear multiple times
        for line, occurrences in line_groups.items():
            if len(occurrences) > 2:
                patterns.append({
                    'type': 'recurring_line',
                    'line': line,
                    'occurrences': occurrences,
                    'count': len(occurrences)
                })
        
        return patterns
    
    def _detect_anti_patterns(self, code: str, language: str) -> List[Dict[str, Any]]:
        """זיהוי anti-patterns"""
        anti_patterns = []
        
        # God class/function detection
        if language == 'python':
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                        if method_count > 20:
                            anti_patterns.append({
                                'type': 'god_class',
                                'name': node.name,
                                'method_count': method_count,
                                'suggestion': 'Consider splitting this class into smaller, focused classes'
                            })
            except SyntaxError:
                pass
        
        # Spaghetti code detection (high complexity)
        complexity = self._calculate_code_complexity(code)
        if complexity > 15:
            anti_patterns.append({
                'type': 'spaghetti_code',
                'complexity': complexity,
                'suggestion': 'High complexity detected. Consider refactoring for better readability'
            })
        
        return anti_patterns
    
    def _detect_security_issues(self, code: str) -> List[Dict[str, Any]]:
        """זיהוי בעיות אבטחה פוטנציאליות"""
        issues = []
        
        # SQL injection vulnerability
        if re.search(r'(execute|query)\([^)]*%[^)]*\)', code):
            issues.append({
                'type': 'sql_injection',
                'severity': 'high',
                'suggestion': 'Use parameterized queries to prevent SQL injection'
            })
        
        # Hardcoded credentials
        if re.search(r'(password|api_key|secret)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            issues.append({
                'type': 'hardcoded_credentials',
                'severity': 'high',
                'suggestion': 'Use environment variables or secure vaults for credentials'
            })
        
        # Unsafe eval usage
        if re.search(r'\beval\s*\(', code):
            issues.append({
                'type': 'unsafe_eval',
                'severity': 'high',
                'suggestion': 'Avoid using eval() as it can execute arbitrary code'
            })
        
        # Weak cryptography
        if re.search(r'\b(md5|sha1)\s*\(', code):
            issues.append({
                'type': 'weak_cryptography',
                'severity': 'medium',
                'suggestion': 'Use stronger hashing algorithms like SHA-256 or bcrypt'
            })
        
        return issues
    
    def _count_function_lines(self, node: ast.FunctionDef) -> int:
        """ספירת שורות בפונקציה"""
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            return node.end_lineno - node.lineno + 1
        return 0
    
    def _has_nested_loop(self, node: ast.For) -> bool:
        """בדיקה האם יש לולאה מקוננת"""
        for child in ast.walk(node):
            if child != node and isinstance(child, (ast.For, ast.While)):
                return True
        return False
    
    def _find_duplicate_code(self, lines: List[str]) -> List[Dict[str, Any]]:
        """מציאת קוד כפול"""
        duplicates = []
        seen_blocks = defaultdict(list)
        
        # Check for duplicate blocks (3+ consecutive lines)
        for i in range(len(lines) - 2):
            block = '\n'.join(lines[i:i+3])
            if block.strip():
                seen_blocks[block].append(i + 1)
        
        for block, occurrences in seen_blocks.items():
            if len(occurrences) > 1:
                duplicates.append({
                    'lines': occurrences,
                    'block': block
                })
        
        return duplicates
    
    def _calculate_code_complexity(self, code: str) -> int:
        """חישוב מורכבות הקוד"""
        complexity = 1
        
        # Count decision points
        complexity += len(re.findall(r'\bif\b', code))
        complexity += len(re.findall(r'\belif\b', code))
        complexity += len(re.findall(r'\bfor\b', code))
        complexity += len(re.findall(r'\bwhile\b', code))
        complexity += len(re.findall(r'\btry\b', code))
        complexity += len(re.findall(r'\bexcept\b', code))
        
        return complexity
    
    def _calculate_severity(self, bug_type: str) -> str:
        """חישוב חומרת הבאג"""
        high_severity = ['null_reference', 'resource_leak', 'infinite_loop']
        medium_severity = ['exception_handling']
        
        if bug_type in high_severity:
            return 'high'
        elif bug_type in medium_severity:
            return 'medium'
        return 'low'
    
    def _learn_from_patterns(self, patterns: Dict[str, Any]):
        """למידה מהדפוסים שנמצאו"""
        # Update code patterns
        for pattern_type, detected in patterns.items():
            if detected and pattern_type not in ['security_issues']:
                if pattern_type not in self.code_patterns:
                    self.code_patterns[pattern_type] = []
                self.code_patterns[pattern_type].extend(detected)
        
        # Save updated patterns
        self._save_patterns()
    
    def _save_patterns(self):
        """שמירת הדפוסים שנלמדו"""
        os.makedirs('data/patterns', exist_ok=True)
        
        # Save bug patterns
        with open(f"data/patterns/{self.user_id}_bugs.json", 'w', encoding='utf-8') as f:
            json.dump(self.bug_patterns, f, indent=2, ensure_ascii=False)
        
        # Save code patterns
        with open(f"data/patterns/{self.user_id}_code.json", 'w', encoding='utf-8') as f:
            json.dump(self.code_patterns, f, indent=2, ensure_ascii=False, default=str)
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות על דפוסים"""
        stats = {
            'total_patterns_detected': len(self.pattern_history),
            'most_common_bugs': Counter([
                p['type'] for patterns in self.pattern_history 
                for p in patterns.get('bug_patterns', [])
            ]).most_common(5),
            'most_common_smells': Counter([
                p['type'] for patterns in self.pattern_history 
                for p in patterns.get('code_smells', [])
            ]).most_common(5)
        }
        return stats
