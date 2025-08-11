"""
API Routes Module
נתיבי API לשרת
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from typing import Dict, Any

# Import core modules
from core.analyzer import CodeAnalyzer
from core.style_learner import StyleLearner
from core.pattern_detector import PatternDetector
from core.recommendation import RecommendationEngine
from models.user_profile import UserProfileManager
from models.database import get_db

# Create blueprint
api_blueprint = Blueprint('api', __name__)

# Initialize components
analyzer = CodeAnalyzer()
recommendation_engine = RecommendationEngine()
profile_manager = UserProfileManager()
db = get_db()

# File upload configuration
UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'py', 'js', 'java', 'cpp', 'cs', 'rb', 'go', 'rs', 'txt'}

def allowed_file(filename):
    """בדיקה האם הקובץ מותר"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_blueprint.route('/analyze', methods=['POST'])
def analyze_code():
    """ניתוח קוד"""
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
        
        code = data['code']
        language = data.get('language', 'python')
        user_id = data.get('user_id', session.get('user_id', 'anonymous'))
        
        # Create session ID
        session_id = str(uuid.uuid4())
        
        # Analyze code
        analysis_result = analyzer.analyze_code(code, language)
        
        # Detect patterns
        pattern_detector = PatternDetector(user_id)
        patterns = pattern_detector.detect_patterns(code, language)
        
        # Learn style
        style_learner = StyleLearner(user_id)
        style_learning = style_learner.learn_from_code(code, language)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            analysis_result.__dict__,
            style_learner.style_profile,
            patterns
        )
        
        # Convert recommendations to dict
        recommendations_dict = [
            {
                'type': rec.type,
                'title': rec.title,
                'description': rec.description,
                'severity': rec.severity,
                'priority': rec.priority,
                'line_start': rec.line_start,
                'line_end': rec.line_end,
                'confidence': rec.confidence,
                'tags': rec.tags
            }
            for rec in recommendations
        ]
        
        # Prepare response
        response = {
            'session_id': session_id,
            'analysis': {
                'metrics': analysis_result.metrics,
                'issues': analysis_result.issues,
                'suggestions': analysis_result.suggestions,
                'style_patterns': analysis_result.style_patterns
            },
            'patterns': patterns,
            'recommendations': recommendations_dict,
            'summary': recommendation_engine.get_recommendation_summary(recommendations)
        }
        
        # Save to database
        db.save_analysis(
            session_id=session_id,
            user_id=user_id,
            file_path='inline_code',
            language=language,
            analysis_result=response['analysis']
        )
        
        # Update user history
        profile_manager.update_history(
            user_id=user_id,
            language=language,
            lines=len(code.splitlines()),
            mistakes=[issue['type'] for issue in analysis_result.issues],
            improvements=[rec.type for rec in recommendations[:5]]
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/analyze_file', methods=['POST'])
def analyze_file():
    """ניתוח קובץ"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file temporarily
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
        file.save(filepath)
        
        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Detect language from extension
        ext = filename.rsplit('.', 1)[1].lower()
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'java': 'java',
            'cpp': 'cpp',
            'cs': 'csharp',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust'
        }
        language = language_map.get(ext, 'unknown')
        
        # Get user ID
        user_id = request.form.get('user_id', session.get('user_id', 'anonymous'))
        
        # Analyze using the same logic as analyze_code
        data = {'code': code, 'language': language, 'user_id': user_id}
        request.get_json = lambda: data
        
        # Clean up temporary file
        os.remove(filepath)
        
        return analyze_code()
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """קבלת פרופיל משתמש"""
    try:
        profile = profile_manager.get_profile(user_id)
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify(profile.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/profile', methods=['POST'])
def create_profile():
    """יצירת פרופיל חדש"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data:
            return jsonify({'error': 'Username required'}), 400
        
        username = data['username']
        email = data.get('email')
        
        profile = profile_manager.create_profile(username, email)
        
        # Store user_id in session
        session['user_id'] = profile.user_id
        
        return jsonify(profile.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    """עדכון פרופיל משתמש"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = profile_manager.update_profile(user_id, data)
        
        if not success:
            return jsonify({'error': 'Failed to update profile'}), 400
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    """קבלת היסטוריית ניתוחים"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db.get_analysis_history(user_id, limit)
        
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/statistics/<user_id>', methods=['GET'])
def get_statistics(user_id):
    """קבלת סטטיסטיקות משתמש"""
    try:
        # Get user statistics
        user_stats = profile_manager.get_user_statistics(user_id)
        
        # Get database statistics
        db_stats = db.get_statistics(user_id)
        
        # Combine statistics
        combined_stats = {**user_stats, **db_stats}
        
        return jsonify(combined_stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/patterns/<user_id>', methods=['GET'])
def get_patterns(user_id):
    """קבלת דפוסים נפוצים"""
    try:
        # Get common bug patterns
        bug_patterns = db.get_common_bug_patterns(user_id)
        
        # Get pattern statistics
        pattern_detector = PatternDetector(user_id)
        pattern_stats = pattern_detector.get_pattern_statistics()
        
        response = {
            'bug_patterns': bug_patterns,
            'statistics': pattern_stats
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/refactor', methods=['POST'])
def refactor_code():
    """ביצוע refactoring אוטומטי"""
    try:
        data = request.get_json()
        
        if not data or 'code' not in data or 'recommendation_id' not in data:
            return jsonify({'error': 'Code and recommendation_id required'}), 400
        
        code = data['code']
        recommendation_id = data['recommendation_id']
        
        # In a real implementation, we would retrieve the recommendation
        # For now, return a simple response
        refactored_code = code  # Placeholder
        
        response = {
            'original_code': code,
            'refactored_code': refactored_code,
            'changes_made': []
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/learn_style', methods=['POST'])
def learn_style():
    """למידת סגנון מקוד"""
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'Code required'}), 400
        
        code = data['code']
        language = data.get('language', 'python')
        user_id = data.get('user_id', session.get('user_id', 'anonymous'))
        
        # Learn style
        style_learner = StyleLearner(user_id)
        result = style_learner.learn_from_code(code, language)
        
        # Get style recommendations
        recommendations = style_learner.get_style_recommendations(code)
        
        response = {
            'features_learned': result['features_learned'],
            'patterns_identified': result['patterns_identified'],
            'style_recommendations': recommendations
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/session', methods=['GET'])
def get_session_info():
    """קבלת מידע על הסשן הנוכחי"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        response = {
            'user_id': user_id,
            'logged_in': user_id != 'anonymous'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/logout', methods=['POST'])
def logout():
    """יציאה מהמערכת"""
    try:
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
