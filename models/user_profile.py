"""
User Profile Module
ניהול פרופילי משתמשים וההעדפות שלהם
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import hashlib

@dataclass
class UserPreferences:
    """העדפות משתמש"""
    naming_convention: str = 'snake_case'
    indentation: str = '4_spaces'
    max_line_length: int = 100
    quote_style: str = 'single'
    docstring_style: str = 'google'
    import_style: str = 'grouped'
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון"""
        return {
            'naming_convention': self.naming_convention,
            'indentation': self.indentation,
            'max_line_length': self.max_line_length,
            'quote_style': self.quote_style,
            'docstring_style': self.docstring_style,
            'import_style': self.import_style
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """יצירה ממילון"""
        return cls(**data)

@dataclass
class CodingHistory:
    """היסטוריית קידוד של המשתמש"""
    total_files_analyzed: int = 0
    total_lines_written: int = 0
    languages_used: Dict[str, int] = field(default_factory=dict)
    common_mistakes: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    last_analysis: Optional[datetime] = None
    
    def update(self, language: str, lines: int):
        """עדכון היסטוריה"""
        self.total_files_analyzed += 1
        self.total_lines_written += lines
        self.languages_used[language] = self.languages_used.get(language, 0) + 1
        self.last_analysis = datetime.now()

@dataclass
class UserProfile:
    """פרופיל משתמש מלא"""
    user_id: str
    username: str
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    preferences: UserPreferences = field(default_factory=UserPreferences)
    history: CodingHistory = field(default_factory=CodingHistory)
    skill_level: str = 'intermediate'  # 'beginner', 'intermediate', 'advanced', 'expert'
    focus_areas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'preferences': self.preferences.to_dict(),
            'history': {
                'total_files_analyzed': self.history.total_files_analyzed,
                'total_lines_written': self.history.total_lines_written,
                'languages_used': self.history.languages_used,
                'common_mistakes': self.history.common_mistakes,
                'improvement_areas': self.history.improvement_areas,
                'last_analysis': self.history.last_analysis.isoformat() if self.history.last_analysis else None
            },
            'skill_level': self.skill_level,
            'focus_areas': self.focus_areas
        }

class UserProfileManager:
    """מנהל פרופילי משתמשים"""
    
    def __init__(self, data_dir: str = "data/users"):
        self.data_dir = data_dir
        self.profiles: Dict[str, UserProfile] = {}
        self._ensure_data_dir()
        self._load_profiles()
    
    def _ensure_data_dir(self):
        """יצירת תיקיית נתונים אם לא קיימת"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_profiles(self):
        """טעינת פרופילים קיימים"""
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                user_id = filename[:-5]  # Remove .json
                profile = self.load_profile(user_id)
                if profile:
                    self.profiles[user_id] = profile
    
    def create_profile(self, username: str, email: Optional[str] = None) -> UserProfile:
        """יצירת פרופיל חדש"""
        user_id = self._generate_user_id(username)
        
        profile = UserProfile(
            user_id=user_id,
            username=username,
            email=email
        )
        
        self.profiles[user_id] = profile
        self.save_profile(profile)
        
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """קבלת פרופיל משתמש"""
        if user_id in self.profiles:
            return self.profiles[user_id]
        
        # Try to load from disk
        profile = self.load_profile(user_id)
        if profile:
            self.profiles[user_id] = profile
        
        return profile
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """עדכון פרופיל משתמש"""
        profile = self.get_profile(user_id)
        if not profile:
            return False
        
        # Update preferences
        if 'preferences' in updates:
            for key, value in updates['preferences'].items():
                if hasattr(profile.preferences, key):
                    setattr(profile.preferences, key, value)
        
        # Update skill level
        if 'skill_level' in updates:
            profile.skill_level = updates['skill_level']
        
        # Update focus areas
        if 'focus_areas' in updates:
            profile.focus_areas = updates['focus_areas']
        
        self.save_profile(profile)
        return True
    
    def save_profile(self, profile: UserProfile):
        """שמירת פרופיל לדיסק"""
        filepath = os.path.join(self.data_dir, f"{profile.user_id}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_profile(self, user_id: str) -> Optional[UserProfile]:
        """טעינת פרופיל מהדיסק"""
        filepath = os.path.join(self.data_dir, f"{user_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct profile
            profile = UserProfile(
                user_id=data['user_id'],
                username=data['username'],
                email=data.get('email'),
                created_at=datetime.fromisoformat(data['created_at']),
                preferences=UserPreferences.from_dict(data['preferences']),
                skill_level=data.get('skill_level', 'intermediate'),
                focus_areas=data.get('focus_areas', [])
            )
            
            # Reconstruct history
            history_data = data.get('history', {})
            profile.history.total_files_analyzed = history_data.get('total_files_analyzed', 0)
            profile.history.total_lines_written = history_data.get('total_lines_written', 0)
            profile.history.languages_used = history_data.get('languages_used', {})
            profile.history.common_mistakes = history_data.get('common_mistakes', [])
            profile.history.improvement_areas = history_data.get('improvement_areas', [])
            
            if history_data.get('last_analysis'):
                profile.history.last_analysis = datetime.fromisoformat(history_data['last_analysis'])
            
            return profile
            
        except Exception as e:
            print(f"Error loading profile {user_id}: {e}")
            return None
    
    def delete_profile(self, user_id: str) -> bool:
        """מחיקת פרופיל"""
        filepath = os.path.join(self.data_dir, f"{user_id}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            
        if user_id in self.profiles:
            del self.profiles[user_id]
            
        return True
    
    def _generate_user_id(self, username: str) -> str:
        """יצירת מזהה ייחודי למשתמש"""
        timestamp = datetime.now().isoformat()
        unique_string = f"{username}_{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def get_all_profiles(self) -> List[UserProfile]:
        """קבלת כל הפרופילים"""
        return list(self.profiles.values())
    
    def update_history(self, user_id: str, language: str, lines: int, 
                      mistakes: List[str] = None, improvements: List[str] = None):
        """עדכון היסטוריית המשתמש"""
        profile = self.get_profile(user_id)
        if not profile:
            return
        
        profile.history.update(language, lines)
        
        if mistakes:
            # Add unique mistakes
            for mistake in mistakes:
                if mistake not in profile.history.common_mistakes:
                    profile.history.common_mistakes.append(mistake)
            
            # Keep only last 20 mistakes
            profile.history.common_mistakes = profile.history.common_mistakes[-20:]
        
        if improvements:
            # Add unique improvement areas
            for improvement in improvements:
                if improvement not in profile.history.improvement_areas:
                    profile.history.improvement_areas.append(improvement)
            
            # Keep only last 10 improvement areas
            profile.history.improvement_areas = profile.history.improvement_areas[-10:]
        
        self.save_profile(profile)
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """קבלת סטטיסטיקות משתמש"""
        profile = self.get_profile(user_id)
        if not profile:
            return {}
        
        stats = {
            'user_id': user_id,
            'username': profile.username,
            'member_since': profile.created_at.isoformat(),
            'skill_level': profile.skill_level,
            'total_analyses': profile.history.total_files_analyzed,
            'total_lines': profile.history.total_lines_written,
            'favorite_language': max(profile.history.languages_used.items(), 
                                    key=lambda x: x[1])[0] if profile.history.languages_used else None,
            'languages': profile.history.languages_used,
            'recent_mistakes': profile.history.common_mistakes[-5:],
            'improvement_areas': profile.history.improvement_areas,
            'last_active': profile.history.last_analysis.isoformat() if profile.history.last_analysis else None
        }
        
        return stats
    
    def is_ready(self) -> bool:
        """בדיקת מוכנות המנהל"""
        return os.path.exists(self.data_dir)
