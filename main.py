"""
AI Personal Code Reviewer - Main Application
נקודת הכניסה הראשית למערכת
"""

import os
import sys
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes import api_blueprint
from core.analyzer import CodeAnalyzer
from models.user_profile import UserProfileManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            template_folder='ui/templates',
            static_folder='ui/static')

# Enable CORS
CORS(app)

# Register blueprints
app.register_blueprint(api_blueprint, url_prefix='/api')

# Initialize core components
analyzer = CodeAnalyzer()
profile_manager = UserProfileManager()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'components': {
            'analyzer': analyzer.is_ready(),
            'profile_manager': profile_manager.is_ready()
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

def initialize_app():
    """Initialize application components"""
    print("🚀 Initializing AI Personal Code Reviewer...")
    
    # Create necessary directories
    os.makedirs('ui/templates', exist_ok=True)
    os.makedirs('ui/static/css', exist_ok=True)
    os.makedirs('ui/static/js', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Initialize database
    from models.database import init_db
    init_db()
    
    print("✅ Initialization complete!")

if __name__ == '__main__':
    initialize_app()
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"🎯 AI Personal Code Reviewer is running on http://localhost:{port}")
    print("📝 Ready to analyze your code!")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
