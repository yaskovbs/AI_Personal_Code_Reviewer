"""
Style Learner Module
לומד את סגנון הקוד האישי של המשתמש
"""

import json
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class StyleLearner:
    """לומד ומנתח סגנון קוד אישי"""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.style_profile = self._load_or_create_profile()
        self.learning_history = []
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.style_clusters = None
        
    def _load_or_create_profile(self) -> Dict[str, Any]:
        """טעינה או יצירת פרופיל סגנון"""
        profile_path = f"data/profiles/{self.user_id}_style.json"
        
        if os.path.exists(profile_path):
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'user_id': self.user_id,
            'created_at': datetime.now().isoformat(),
            'patterns': {
                'naming': defaultdict(int),
                'structure': defaultdict(int),
                'formatting': defaultdict(int),
                'comments': defaultdict(int)
            },
            'preferences': {},
            'common_patterns': [],
            'anti_patterns': []
        }
    
    def learn_from_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """למידה מקוד חדש"""
        # Extract style features
        features = self._extract_style_features(code, language)
        
        # Update profile
        self._update_profile(features)
        
        # Add to learning history
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'language': language
        })
        
        # Identify patterns
        patterns = self._identify_patterns(features)
        
        # Save profile
        self._save_profile()
        
        return {
            'features_learned': features,
            'patterns_identified': patterns,
            'profile_updated': True
        }
    
    def _extract_style_features(self, code: str, language: str) -> Dict[str, Any]:
        """חילוץ מאפייני סגנון מהקוד"""
        features = {
            'naming': self._extract_naming_features(code),
            'structure': self._extract_structure_features(code),
            'formatting': self._extract_formatting_features(code),
            'comments': self._extract_comment_features(code),
            'complexity': self._extract_complexity_features(code)
        }
        return features
    
    def _extract_naming_features(self, code: str) -> Dict[str, Any]:
        """חילוץ מאפייני שמות"""
        import re
        
        features = {
            'variable_style': [],
            'function_style': [],
            'class_style': [],
            'constant_style': []
        }
        
        # Variable names
        variables = re.findall(r'\b([a-z_][a-z0-9_]*)\s*=', code)
        for var in variables:
            if '_' in var:
                features['variable_style'].append('snake_case')
            elif any(c.isupper() for c in var[1:]):
                features['variable_style'].append('camelCase')
            else:
                features['variable_style'].append('lowercase')
        
        # Function names
        functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
        for func in functions:
            if '_' in func:
                features['function_style'].append('snake_case')
            elif any(c.isupper() for c in func[1:]):
                features['function_style'].append('camelCase')
        
        # Class names
        classes = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
        for cls in classes:
            if cls[0].isupper():
                features['class_style'].append('PascalCase')
            else:
                features['class_style'].append('other')
        
        # Constants
        constants = re.findall(r'\b([A-Z_][A-Z0-9_]*)\s*=', code)
        if constants:
            features['constant_style'].append('UPPER_SNAKE_CASE')
        
        return features
    
    def _extract_structure_features(self, code: str) -> Dict[str, Any]:
        """חילוץ מאפייני מבנה"""
        lines = code.splitlines()
        
        features = {
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'max_line_length': max(len(line) for line in lines) if lines else 0,
            'empty_lines_ratio': len([l for l in lines if not l.strip()]) / len(lines) if lines else 0,
            'indentation_levels': self._count_indentation_levels(lines),
            'function_length_avg': self._calculate_avg_function_length(code)
        }
        
        return features
    
    def _extract_formatting_features(self, code: str) -> Dict[str, Any]:
        """חילוץ מאפייני פורמט"""
        import re
        
        features = {
            'spaces_around_operators': bool(re.search(r'\s[+\-*/=]\s', code)),
            'spaces_after_comma': bool(re.search(r',\s', code)),
            'trailing_commas': bool(re.search(r',\s*[\]\}]', code)),
            'quote_style': 'single' if code.count("'") > code.count('"') else 'double',
            'semicolons': bool(re.search(r';\s*$', code, re.MULTILINE)),
            'blank_lines_between_functions': bool(re.search(r'\n\n\s*def\s', code))
        }
        
        return features
    
    def _extract_comment_features(self, code: str) -> Dict[str, Any]:
        """חילוץ מאפייני הערות"""
        import re
        
        lines = code.splitlines()
        comment_lines = [l for l in lines if l.strip().startswith('#')]
        docstrings = re.findall(r'""".*?"""', code, re.DOTALL)
        
        features = {
            'comment_ratio': len(comment_lines) / len(lines) if lines else 0,
            'avg_comment_length': sum(len(c) for c in comment_lines) / len(comment_lines) if comment_lines else 0,
            'has_docstrings': len(docstrings) > 0,
            'docstring_style': 'triple_quotes' if docstrings else None,
            'inline_comments': bool(re.search(r'\s+#\s+\w+', code))
        }
        
        return features
    
    def _extract_complexity_features(self, code: str) -> Dict[str, Any]:
        """חילוץ מאפייני מורכבות"""
        import re
        
        features = {
            'nested_loops': len(re.findall(r'for.*:\s*\n.*for.*:', code)),
            'nested_conditions': len(re.findall(r'if.*:\s*\n.*if.*:', code)),
            'try_except_blocks': len(re.findall(r'try:', code)),
            'list_comprehensions': len(re.findall(r'\[.*for.*in.*\]', code)),
            'lambda_functions': len(re.findall(r'lambda\s+\w+:', code))
        }
        
        return features
    
    def _count_indentation_levels(self, lines: List[str]) -> int:
        """ספירת רמות הזחה"""
        max_level = 0
        for line in lines:
            if line.strip():
                spaces = len(line) - len(line.lstrip())
                level = spaces // 4  # Assuming 4 spaces per level
                max_level = max(max_level, level)
        return max_level
    
    def _calculate_avg_function_length(self, code: str) -> float:
        """חישוב אורך ממוצע של פונקציות"""
        import re
        
        functions = re.split(r'\ndef\s+\w+', code)[1:]
        if not functions:
            return 0
        
        lengths = []
        for func in functions:
            lines = func.splitlines()
            # Count lines until next function or end
            func_lines = 0
            for line in lines:
                if line.strip() and not line.startswith('def '):
                    func_lines += 1
                elif line.startswith('def '):
                    break
            lengths.append(func_lines)
        
        return sum(lengths) / len(lengths) if lengths else 0
    
    def _update_profile(self, features: Dict[str, Any]):
        """עדכון פרופיל הסגנון"""
        for category, values in features.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, list):
                        for item in value:
                            self.style_profile['patterns'][category][str(item)] += 1
                    else:
                        self.style_profile['patterns'][category][str(key)] = value
    
    def _identify_patterns(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """זיהוי דפוסים בסגנון"""
        patterns = []
        
        # Check for consistent naming
        if 'naming' in features:
            for style_type, styles in features['naming'].items():
                if styles:
                    most_common = Counter(styles).most_common(1)[0][0]
                    patterns.append({
                        'type': 'naming_convention',
                        'category': style_type,
                        'pattern': most_common,
                        'confidence': Counter(styles)[most_common] / len(styles)
                    })
        
        # Check for formatting preferences
        if 'formatting' in features:
            for key, value in features['formatting'].items():
                patterns.append({
                    'type': 'formatting_preference',
                    'category': key,
                    'pattern': value,
                    'confidence': 0.8  # Default confidence
                })
        
        return patterns
    
    def get_style_recommendations(self, code: str) -> List[Dict[str, Any]]:
        """קבלת המלצות סגנון מותאמות אישית"""
        recommendations = []
        features = self._extract_style_features(code, 'python')
        
        # Compare with learned style
        for category, patterns in self.style_profile['patterns'].items():
            if patterns:
                # Find most common pattern
                most_common = max(patterns.items(), key=lambda x: x[1])
                
                # Check if current code matches
                if category in features:
                    current = features[category]
                    if isinstance(current, dict):
                        for key, value in current.items():
                            if str(value) != most_common[0]:
                                recommendations.append({
                                    'type': 'style_mismatch',
                                    'category': category,
                                    'current': str(value),
                                    'suggested': most_common[0],
                                    'confidence': most_common[1] / sum(patterns.values())
                                })
        
        return recommendations
    
    def _save_profile(self):
        """שמירת הפרופיל"""
        os.makedirs('data/profiles', exist_ok=True)
        profile_path = f"data/profiles/{self.user_id}_style.json"
        
        # Convert defaultdict to regular dict for JSON serialization
        save_data = {
            'user_id': self.style_profile['user_id'],
            'created_at': self.style_profile['created_at'],
            'updated_at': datetime.now().isoformat(),
            'patterns': {
                category: dict(patterns) 
                for category, patterns in self.style_profile['patterns'].items()
            },
            'preferences': self.style_profile['preferences'],
            'common_patterns': self.style_profile['common_patterns'],
            'anti_patterns': self.style_profile['anti_patterns']
        }
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    def is_ready(self) -> bool:
        """בדיקת מוכנות"""
        return True
