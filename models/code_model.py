"""
Code Model Module
מודל נתונים לייצוג קוד
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import hashlib

@dataclass
class CodeFile:
    """ייצוג קובץ קוד"""
    path: str
    content: str
    language: str
    size: int
    last_modified: datetime
    hash: str = field(init=False)
    
    def __post_init__(self):
        """חישוב hash לקובץ"""
        self.hash = hashlib.md5(self.content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון"""
        return {
            'path': self.path,
            'language': self.language,
            'size': self.size,
            'last_modified': self.last_modified.isoformat(),
            'hash': self.hash
        }

@dataclass
class CodeSnippet:
    """קטע קוד לניתוח"""
    content: str
    language: str
    start_line: int
    end_line: int
    file_path: Optional[str] = None
    context: Optional[str] = None
    
    def get_lines(self) -> List[str]:
        """קבלת שורות הקוד"""
        return self.content.splitlines()
    
    def get_line_count(self) -> int:
        """ספירת שורות"""
        return len(self.get_lines())

@dataclass
class AnalysisSession:
    """סשן ניתוח קוד"""
    session_id: str
    user_id: str
    started_at: datetime
    files_analyzed: List[CodeFile] = field(default_factory=list)
    total_lines: int = 0
    issues_found: int = 0
    recommendations_made: int = 0
    
    def add_file(self, file: CodeFile):
        """הוספת קובץ לסשן"""
        self.files_analyzed.append(file)
        self.total_lines += len(file.content.splitlines())
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat(),
            'files_analyzed': len(self.files_analyzed),
            'total_lines': self.total_lines,
            'issues_found': self.issues_found,
            'recommendations_made': self.recommendations_made
        }

@dataclass
class CodeMetrics:
    """מטריקות קוד"""
    lines_of_code: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    complexity: int = 0
    functions: int = 0
    classes: int = 0
    imports: int = 0
    
    def calculate_ratios(self) -> Dict[str, float]:
        """חישוב יחסים"""
        total = self.lines_of_code + self.blank_lines + self.comment_lines
        if total == 0:
            return {}
        
        return {
            'code_ratio': self.lines_of_code / total,
            'comment_ratio': self.comment_lines / total,
            'blank_ratio': self.blank_lines / total,
            'comment_to_code': self.comment_lines / self.lines_of_code if self.lines_of_code > 0 else 0
        }

@dataclass
class RefactoringProposal:
    """הצעת refactoring"""
    type: str
    description: str
    original_code: str
    proposed_code: str
    benefits: List[str]
    risks: List[str]
    estimated_impact: str  # 'low', 'medium', 'high'
    auto_applicable: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון"""
        return {
            'type': self.type,
            'description': self.description,
            'benefits': self.benefits,
            'risks': self.risks,
            'estimated_impact': self.estimated_impact,
            'auto_applicable': self.auto_applicable
        }

class CodeRepository:
    """מאגר קוד לניתוח"""
    
    def __init__(self, path: str):
        self.path = path
        self.files: List[CodeFile] = []
        self.metrics: Dict[str, CodeMetrics] = {}
        self.last_scan: Optional[datetime] = None
    
    def scan(self):
        """סריקת המאגר"""
        import os
        
        for root, dirs, files in os.walk(self.path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if self._is_code_file(file):
                    file_path = os.path.join(root, file)
                    self._add_file(file_path)
        
        self.last_scan = datetime.now()
    
    def _is_code_file(self, filename: str) -> bool:
        """בדיקה האם זה קובץ קוד"""
        extensions = ['.py', '.js', '.java', '.cpp', '.cs', '.rb', '.go', '.rs']
        return any(filename.endswith(ext) for ext in extensions)
    
    def _add_file(self, file_path: str):
        """הוספת קובץ למאגר"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            language = self._detect_language(file_path)
            size = len(content)
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            code_file = CodeFile(
                path=file_path,
                content=content,
                language=language,
                size=size,
                last_modified=last_modified
            )
            
            self.files.append(code_file)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    
    def _detect_language(self, file_path: str) -> str:
        """זיהוי שפת התכנות לפי סיומת"""
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust'
        }
        
        for ext, lang in ext_to_lang.items():
            if file_path.endswith(ext):
                return lang
        return 'unknown'
    
    def get_statistics(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות על המאגר"""
        stats = {
            'total_files': len(self.files),
            'total_lines': sum(len(f.content.splitlines()) for f in self.files),
            'languages': {},
            'largest_files': [],
            'last_scan': self.last_scan.isoformat() if self.last_scan else None
        }
        
        # Count by language
        for file in self.files:
            stats['languages'][file.language] = stats['languages'].get(file.language, 0) + 1
        
        # Find largest files
        sorted_files = sorted(self.files, key=lambda f: f.size, reverse=True)
        stats['largest_files'] = [
            {'path': f.path, 'size': f.size}
            for f in sorted_files[:5]
        ]
        
        return stats
