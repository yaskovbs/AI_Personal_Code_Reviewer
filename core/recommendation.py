"""
Recommendation Engine Module
מנוע המלצות חכם לשיפור קוד
"""

import ast
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Recommendation:
    """המלצה לשיפור קוד"""
    type: str
    title: str
    description: str
    severity: str  # 'info', 'warning', 'error'
    priority: str  # 'low', 'medium', 'high'
    original_code: str
    suggested_code: str
    line_start: int
    line_end: int
    confidence: float
    tags: List[str]

class RecommendationEngine:
    """מנוע המלצות לשיפור קוד"""
    
    def __init__(self):
        self.recommendation_templates = self._load_templates()
        self.refactoring_patterns = self._load_refactoring_patterns()
        
    def _load_templates(self) -> Dict[str, Any]:
        """טעינת תבניות המלצות"""
        return {
            'performance': {
                'list_comprehension': {
                    'title': 'Use list comprehension',
                    'description': 'List comprehensions are more efficient and readable',
                    'priority': 'medium'
                },
                'generator_expression': {
                    'title': 'Use generator expression',
                    'description': 'Generator expressions are memory efficient for large datasets',
                    'priority': 'medium'
                },
                'string_join': {
                    'title': 'Use string join instead of concatenation',
                    'description': 'String join is more efficient for multiple concatenations',
                    'priority': 'low'
                }
            },
            'readability': {
                'extract_method': {
                    'title': 'Extract method',
                    'description': 'Extract complex logic into a separate method',
                    'priority': 'high'
                },
                'rename_variable': {
                    'title': 'Improve variable naming',
                    'description': 'Use more descriptive variable names',
                    'priority': 'medium'
                },
                'add_docstring': {
                    'title': 'Add docstring',
                    'description': 'Add documentation to improve code understanding',
                    'priority': 'low'
                }
            },
            'best_practices': {
                'use_context_manager': {
                    'title': 'Use context manager',
                    'description': 'Use with statement for resource management',
                    'priority': 'high'
                },
                'handle_exceptions': {
                    'title': 'Add exception handling',
                    'description': 'Add proper exception handling',
                    'priority': 'high'
                },
                'remove_dead_code': {
                    'title': 'Remove dead code',
                    'description': 'Remove unused code to improve maintainability',
                    'priority': 'medium'
                }
            }
        }
    
    def _load_refactoring_patterns(self) -> List[Dict[str, Any]]:
        """טעינת דפוסי refactoring"""
        return [
            {
                'name': 'for_to_comprehension',
                'pattern': r'(\w+)\s*=\s*\[\]\s*\n\s*for\s+(\w+)\s+in\s+(\w+):\s*\n\s*\1\.append\(([^)]+)\)',
                'replacement': '{0} = [{3} for {1} in {2}]',
                'description': 'Convert for loop to list comprehension'
            },
            {
                'name': 'multiple_if_to_elif',
                'pattern': r'if\s+(.+):\s*\n(.+)\nif\s+(.+):\s*\n(.+)',
                'replacement': 'if {0}:\n{1}\nelif {2}:\n{3}',
                'description': 'Use elif instead of multiple if statements'
            },
            {
                'name': 'string_format',
                'pattern': r'"([^"]*)" \+ str\((\w+)\) \+ "([^"]*)"',
                'replacement': 'f"{0}{{{1}}}{2}"',
                'description': 'Use f-strings for string formatting'
            }
        ]
    
    def generate_recommendations(self, analysis_result: Dict[str, Any], 
                                style_profile: Dict[str, Any],
                                patterns_detected: Dict[str, Any]) -> List[Recommendation]:
        """יצירת המלצות מותאמות אישית"""
        recommendations = []
        
        # Generate recommendations based on analysis
        recommendations.extend(self._generate_from_analysis(analysis_result))
        
        # Generate style recommendations
        recommendations.extend(self._generate_style_recommendations(style_profile))
        
        # Generate pattern-based recommendations
        recommendations.extend(self._generate_pattern_recommendations(patterns_detected))
        
        # Generate refactoring recommendations
        if 'code' in analysis_result:
            recommendations.extend(self._generate_refactoring_recommendations(
                analysis_result['code']))
        
        # Sort by priority and confidence
        recommendations.sort(key=lambda r: (
            self._priority_score(r.priority),
            r.confidence
        ), reverse=True)
        
        return recommendations
    
    def _generate_from_analysis(self, analysis: Dict[str, Any]) -> List[Recommendation]:
        """יצירת המלצות מניתוח הקוד"""
        recommendations = []
        
        # Check metrics
        metrics = analysis.get('metrics', {})
        
        # Long functions
        if metrics.get('complexity', 0) > 10:
            recommendations.append(Recommendation(
                type='refactor',
                title='Reduce function complexity',
                description=f"Function complexity is {metrics['complexity']}. Consider breaking it down.",
                severity='warning',
                priority='high',
                original_code='',
                suggested_code='',
                line_start=0,
                line_end=0,
                confidence=0.9,
                tags=['complexity', 'maintainability']
            ))
        
        # Missing documentation
        if metrics.get('docstring_coverage', 100) < 50:
            recommendations.append(Recommendation(
                type='documentation',
                title='Add documentation',
                description=f"Only {metrics.get('docstring_coverage', 0):.0f}% of functions have docstrings",
                severity='info',
                priority='medium',
                original_code='',
                suggested_code='',
                line_start=0,
                line_end=0,
                confidence=0.8,
                tags=['documentation', 'maintainability']
            ))
        
        # Process issues
        for issue in analysis.get('issues', []):
            recommendations.append(Recommendation(
                type='fix',
                title=f"Fix {issue['type']}",
                description=issue['message'],
                severity=issue.get('severity', 'warning'),
                priority='high' if issue.get('severity') == 'error' else 'medium',
                original_code='',
                suggested_code='',
                line_start=issue.get('line', 0),
                line_end=issue.get('line', 0),
                confidence=0.95,
                tags=['bug_fix', issue['type']]
            ))
        
        return recommendations
    
    def _generate_style_recommendations(self, style_profile: Dict[str, Any]) -> List[Recommendation]:
        """יצירת המלצות סגנון"""
        recommendations = []
        
        # Check for style inconsistencies
        patterns = style_profile.get('patterns', {})
        
        for category, items in patterns.items():
            if items and isinstance(items, dict):
                # Find most common pattern
                if items:
                    most_common = max(items.items(), key=lambda x: x[1])
                    total = sum(items.values())
                    
                    # If there's inconsistency
                    if len(items) > 1 and most_common[1] / total < 0.8:
                        recommendations.append(Recommendation(
                            type='style',
                            title=f'Standardize {category}',
                            description=f'Inconsistent {category} detected. Consider using {most_common[0]} consistently',
                            severity='info',
                            priority='low',
                            original_code='',
                            suggested_code='',
                            line_start=0,
                            line_end=0,
                            confidence=most_common[1] / total,
                            tags=['style', 'consistency', category]
                        ))
        
        return recommendations
    
    def _generate_pattern_recommendations(self, patterns: Dict[str, Any]) -> List[Recommendation]:
        """יצירת המלצות מדפוסים שזוהו"""
        recommendations = []
        
        # Security issues
        for issue in patterns.get('security_issues', []):
            recommendations.append(Recommendation(
                type='security',
                title=f"Security: {issue['type']}",
                description=issue['suggestion'],
                severity='error',
                priority='high',
                original_code='',
                suggested_code='',
                line_start=0,
                line_end=0,
                confidence=0.95,
                tags=['security', issue['type']]
            ))
        
        # Code smells
        for smell in patterns.get('code_smells', []):
            recommendations.append(Recommendation(
                type='refactor',
                title=f"Code smell: {smell['type']}",
                description=smell.get('suggestion', 'Consider refactoring'),
                severity='warning',
                priority='medium',
                original_code='',
                suggested_code='',
                line_start=smell.get('line', 0),
                line_end=smell.get('line', 0),
                confidence=0.8,
                tags=['code_smell', smell['type']]
            ))
        
        # Anti-patterns
        for anti_pattern in patterns.get('anti_patterns', []):
            recommendations.append(Recommendation(
                type='refactor',
                title=f"Anti-pattern: {anti_pattern['type']}",
                description=anti_pattern['suggestion'],
                severity='warning',
                priority='high',
                original_code='',
                suggested_code='',
                line_start=0,
                line_end=0,
                confidence=0.85,
                tags=['anti_pattern', anti_pattern['type']]
            ))
        
        return recommendations
    
    def _generate_refactoring_recommendations(self, code: str) -> List[Recommendation]:
        """יצירת המלצות refactoring אוטומטיות"""
        recommendations = []
        
        for pattern in self.refactoring_patterns:
            matches = re.finditer(pattern['pattern'], code, re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                
                # Generate suggested code
                suggested = pattern['replacement']
                for i, group in enumerate(match.groups()):
                    suggested = suggested.replace(f'{{{i}}}', group)
                
                recommendations.append(Recommendation(
                    type='refactor',
                    title=pattern['name'],
                    description=pattern['description'],
                    severity='info',
                    priority='low',
                    original_code=match.group(),
                    suggested_code=suggested,
                    line_start=line_num,
                    line_end=line_num + match.group().count('\n'),
                    confidence=0.7,
                    tags=['refactoring', 'automation']
                ))
        
        # Python-specific refactoring
        recommendations.extend(self._python_specific_refactoring(code))
        
        return recommendations
    
    def _python_specific_refactoring(self, code: str) -> List[Recommendation]:
        """המלצות refactoring ספציפיות ל-Python"""
        recommendations = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return recommendations
        
        for node in ast.walk(tree):
            # Suggest using enumerate
            if isinstance(node, ast.For):
                if self._can_use_enumerate(node):
                    recommendations.append(Recommendation(
                        type='refactor',
                        title='Use enumerate',
                        description='Consider using enumerate() for index tracking',
                        severity='info',
                        priority='low',
                        original_code='',
                        suggested_code='for i, item in enumerate(items):',
                        line_start=node.lineno,
                        line_end=node.lineno,
                        confidence=0.6,
                        tags=['pythonic', 'readability']
                    ))
            
            # Suggest using with statement
            if isinstance(node, ast.Call):
                if self._should_use_context_manager(node):
                    recommendations.append(Recommendation(
                        type='best_practice',
                        title='Use context manager',
                        description='Use "with" statement for file operations',
                        severity='warning',
                        priority='high',
                        original_code='',
                        suggested_code='with open(filename) as f:',
                        line_start=node.lineno,
                        line_end=node.lineno,
                        confidence=0.9,
                        tags=['resource_management', 'best_practice']
                    ))
        
        return recommendations
    
    def _can_use_enumerate(self, node: ast.For) -> bool:
        """בדיקה האם אפשר להשתמש ב-enumerate"""
        # Simplified check - in real implementation would be more sophisticated
        return hasattr(node, 'iter') and isinstance(node.iter, ast.Call)
    
    def _should_use_context_manager(self, node: ast.Call) -> bool:
        """בדיקה האם צריך להשתמש ב-context manager"""
        if hasattr(node.func, 'id'):
            return node.func.id in ['open', 'connect', 'lock']
        return False
    
    def _priority_score(self, priority: str) -> int:
        """המרת עדיפות למספר"""
        scores = {'low': 1, 'medium': 2, 'high': 3}
        return scores.get(priority, 0)
    
    def apply_recommendation(self, code: str, recommendation: Recommendation) -> str:
        """החלת המלצה על הקוד"""
        if not recommendation.suggested_code:
            return code
        
        lines = code.splitlines()
        
        # Simple replacement (in real implementation would be more sophisticated)
        if recommendation.line_start > 0 and recommendation.line_end > 0:
            # Replace the specified lines
            before = lines[:recommendation.line_start - 1]
            after = lines[recommendation.line_end:]
            new_lines = before + [recommendation.suggested_code] + after
            return '\n'.join(new_lines)
        
        # Pattern-based replacement
        if recommendation.original_code:
            return code.replace(recommendation.original_code, recommendation.suggested_code)
        
        return code
    
    def get_recommendation_summary(self, recommendations: List[Recommendation]) -> Dict[str, Any]:
        """סיכום ההמלצות"""
        summary = {
            'total': len(recommendations),
            'by_type': {},
            'by_priority': {},
            'by_severity': {},
            'top_issues': []
        }
        
        for rec in recommendations:
            # Count by type
            summary['by_type'][rec.type] = summary['by_type'].get(rec.type, 0) + 1
            
            # Count by priority
            summary['by_priority'][rec.priority] = summary['by_priority'].get(rec.priority, 0) + 1
            
            # Count by severity
            summary['by_severity'][rec.severity] = summary['by_severity'].get(rec.severity, 0) + 1
        
        # Get top 5 issues
        summary['top_issues'] = [
            {
                'title': rec.title,
                'description': rec.description,
                'priority': rec.priority
            }
            for rec in recommendations[:5]
        ]
        
        return summary
