"""
Database Module
ניהול בסיס הנתונים
"""

import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List, Dict, Any

Base = declarative_base()

class AnalysisRecord(Base):
    """רשומת ניתוח בבסיס הנתונים"""
    __tablename__ = 'analysis_records'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True)
    user_id = Column(String(50))
    file_path = Column(String(500))
    language = Column(String(50))
    timestamp = Column(DateTime, default=datetime.now)
    
    # Analysis results
    metrics = Column(JSON)
    issues = Column(JSON)
    suggestions = Column(JSON)
    patterns = Column(JSON)
    
    # Summary
    lines_analyzed = Column(Integer)
    issues_found = Column(Integer)
    complexity_score = Column(Float)
    quality_score = Column(Float)

class StyleProfile(Base):
    """פרופיל סגנון בבסיס הנתונים"""
    __tablename__ = 'style_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Style patterns
    naming_patterns = Column(JSON)
    formatting_patterns = Column(JSON)
    structure_patterns = Column(JSON)
    
    # Preferences
    preferences = Column(JSON)
    
    # Statistics
    total_analyses = Column(Integer, default=0)
    consistency_score = Column(Float, default=0.0)

class BugPattern(Base):
    """דפוס באג בבסיס הנתונים"""
    __tablename__ = 'bug_patterns'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    pattern_type = Column(String(100))
    pattern_description = Column(Text)
    occurrences = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, default=datetime.now)
    severity = Column(String(20))
    
    # Pattern details
    code_example = Column(Text)
    fix_suggestion = Column(Text)
    language = Column(String(50))

class DatabaseManager:
    """מנהל בסיס הנתונים"""
    
    def __init__(self, db_path: str = "data/code_reviewer.db"):
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """אתחול בסיס הנתונים"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create engine
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """קבלת סשן לבסיס הנתונים"""
        return self.SessionLocal()
    
    def save_analysis(self, session_id: str, user_id: str, file_path: str,
                     language: str, analysis_result: Dict[str, Any]) -> bool:
        """שמירת תוצאות ניתוח"""
        session = self.get_session()
        try:
            record = AnalysisRecord(
                session_id=session_id,
                user_id=user_id,
                file_path=file_path,
                language=language,
                metrics=analysis_result.get('metrics', {}),
                issues=analysis_result.get('issues', []),
                suggestions=analysis_result.get('suggestions', []),
                patterns=analysis_result.get('patterns', {}),
                lines_analyzed=analysis_result.get('metrics', {}).get('lines_of_code', 0),
                issues_found=len(analysis_result.get('issues', [])),
                complexity_score=analysis_result.get('metrics', {}).get('complexity', 0),
                quality_score=self._calculate_quality_score(analysis_result)
            )
            
            session.add(record)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error saving analysis: {e}")
            return False
        finally:
            session.close()
    
    def get_analysis_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """קבלת היסטוריית ניתוחים"""
        session = self.get_session()
        try:
            records = session.query(AnalysisRecord)\
                .filter(AnalysisRecord.user_id == user_id)\
                .order_by(AnalysisRecord.timestamp.desc())\
                .limit(limit)\
                .all()
            
            history = []
            for record in records:
                history.append({
                    'session_id': record.session_id,
                    'file_path': record.file_path,
                    'language': record.language,
                    'timestamp': record.timestamp.isoformat(),
                    'lines_analyzed': record.lines_analyzed,
                    'issues_found': record.issues_found,
                    'quality_score': record.quality_score
                })
            
            return history
            
        finally:
            session.close()
    
    def save_style_profile(self, user_id: str, style_data: Dict[str, Any]) -> bool:
        """שמירת פרופיל סגנון"""
        session = self.get_session()
        try:
            # Check if profile exists
            profile = session.query(StyleProfile)\
                .filter(StyleProfile.user_id == user_id)\
                .first()
            
            if profile:
                # Update existing
                profile.naming_patterns = style_data.get('naming_patterns', {})
                profile.formatting_patterns = style_data.get('formatting_patterns', {})
                profile.structure_patterns = style_data.get('structure_patterns', {})
                profile.preferences = style_data.get('preferences', {})
                profile.total_analyses += 1
                profile.consistency_score = style_data.get('consistency_score', 0.0)
                profile.updated_at = datetime.now()
            else:
                # Create new
                profile = StyleProfile(
                    user_id=user_id,
                    naming_patterns=style_data.get('naming_patterns', {}),
                    formatting_patterns=style_data.get('formatting_patterns', {}),
                    structure_patterns=style_data.get('structure_patterns', {}),
                    preferences=style_data.get('preferences', {}),
                    total_analyses=1,
                    consistency_score=style_data.get('consistency_score', 0.0)
                )
                session.add(profile)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error saving style profile: {e}")
            return False
        finally:
            session.close()
    
    def get_style_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """קבלת פרופיל סגנון"""
        session = self.get_session()
        try:
            profile = session.query(StyleProfile)\
                .filter(StyleProfile.user_id == user_id)\
                .first()
            
            if not profile:
                return None
            
            return {
                'user_id': profile.user_id,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat(),
                'naming_patterns': profile.naming_patterns,
                'formatting_patterns': profile.formatting_patterns,
                'structure_patterns': profile.structure_patterns,
                'preferences': profile.preferences,
                'total_analyses': profile.total_analyses,
                'consistency_score': profile.consistency_score
            }
            
        finally:
            session.close()
    
    def save_bug_pattern(self, user_id: str, pattern_data: Dict[str, Any]) -> bool:
        """שמירת דפוס באג"""
        session = self.get_session()
        try:
            # Check if pattern exists
            pattern = session.query(BugPattern)\
                .filter(BugPattern.user_id == user_id,
                       BugPattern.pattern_type == pattern_data['type'])\
                .first()
            
            if pattern:
                # Update existing
                pattern.occurrences += 1
                pattern.last_seen = datetime.now()
            else:
                # Create new
                pattern = BugPattern(
                    user_id=user_id,
                    pattern_type=pattern_data['type'],
                    pattern_description=pattern_data.get('description', ''),
                    severity=pattern_data.get('severity', 'medium'),
                    code_example=pattern_data.get('code_example', ''),
                    fix_suggestion=pattern_data.get('fix_suggestion', ''),
                    language=pattern_data.get('language', 'unknown')
                )
                session.add(pattern)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error saving bug pattern: {e}")
            return False
        finally:
            session.close()
    
    def get_common_bug_patterns(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """קבלת דפוסי באגים נפוצים"""
        session = self.get_session()
        try:
            patterns = session.query(BugPattern)\
                .filter(BugPattern.user_id == user_id)\
                .order_by(BugPattern.occurrences.desc())\
                .limit(limit)\
                .all()
            
            result = []
            for pattern in patterns:
                result.append({
                    'type': pattern.pattern_type,
                    'description': pattern.pattern_description,
                    'occurrences': pattern.occurrences,
                    'severity': pattern.severity,
                    'first_seen': pattern.first_seen.isoformat(),
                    'last_seen': pattern.last_seen.isoformat(),
                    'fix_suggestion': pattern.fix_suggestion
                })
            
            return result
            
        finally:
            session.close()
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """קבלת סטטיסטיקות כלליות"""
        session = self.get_session()
        try:
            # Count analyses
            total_analyses = session.query(AnalysisRecord)\
                .filter(AnalysisRecord.user_id == user_id)\
                .count()
            
            # Average quality score
            records = session.query(AnalysisRecord)\
                .filter(AnalysisRecord.user_id == user_id)\
                .all()
            
            if records:
                avg_quality = sum(r.quality_score for r in records) / len(records)
                total_lines = sum(r.lines_analyzed for r in records)
                total_issues = sum(r.issues_found for r in records)
            else:
                avg_quality = 0
                total_lines = 0
                total_issues = 0
            
            # Count bug patterns
            bug_patterns = session.query(BugPattern)\
                .filter(BugPattern.user_id == user_id)\
                .count()
            
            return {
                'total_analyses': total_analyses,
                'average_quality_score': avg_quality,
                'total_lines_analyzed': total_lines,
                'total_issues_found': total_issues,
                'unique_bug_patterns': bug_patterns
            }
            
        finally:
            session.close()
    
    def _calculate_quality_score(self, analysis_result: Dict[str, Any]) -> float:
        """חישוב ציון איכות"""
        score = 100.0
        
        # Deduct for issues
        issues = analysis_result.get('issues', [])
        for issue in issues:
            if issue.get('severity') == 'error':
                score -= 10
            elif issue.get('severity') == 'warning':
                score -= 5
            else:
                score -= 2
        
        # Deduct for complexity
        complexity = analysis_result.get('metrics', {}).get('complexity', 0)
        if complexity > 20:
            score -= 15
        elif complexity > 10:
            score -= 10
        elif complexity > 5:
            score -= 5
        
        # Deduct for missing documentation
        doc_coverage = analysis_result.get('metrics', {}).get('docstring_coverage', 100)
        if doc_coverage < 50:
            score -= 10
        elif doc_coverage < 80:
            score -= 5
        
        return max(0, min(100, score))

# Global database instance
_db_manager = None

def init_db():
    """אתחול בסיס הנתונים"""
    global _db_manager
    _db_manager = DatabaseManager()
    return _db_manager

def get_db() -> DatabaseManager:
    """קבלת מנהל בסיס הנתונים"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
