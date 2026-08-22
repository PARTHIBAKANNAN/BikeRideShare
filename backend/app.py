#!/usr/bin/env python3
"""
Smart Ride Matcher - Flask Backend Application
"""

import os
import sys

# Set UTF-8 encoding support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_cors import CORS
from config.settings import Config
from models.models import db

def create_app(config_name='development'):
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    
    # Load configuration
    config = {
        'development': Config,
        'production': Config,
        'testing': Config
    }
    
    app.config.from_object(config[config_name])
    
    # Configure CORS properly for Hugging Face Spaces iframe & local dev
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # JWT Configuration
    jwt = JWTManager(app)
    
    # Create instance directory
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("[OK] Database tables verified / created successfully")
    
    # Initialize Flask-RESTX API
    api = Api(
        app,
        version='1.0',
        title='Smart Ride Matcher API',
        description='AI-Powered Bike Ride Sharing Platform for Chennai',
        doc='/docs/',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Add "Bearer " before your JWT token'
            }
        },
        security='Bearer'
    )
    
    # Import and register route namespaces
    from routes.auth_routes import auth_ns
    from routes.bike_routes import bike_ns
    from routes.ride_routes import ride_ns
    from routes.dashboard_routes import dashboard_ns
    from routes.admin_routes import admin_ns
    from routes.notification_routes import notification_ns
    
    # Register namespaces with API
    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(bike_ns, path='/api/bikes')
    api.add_namespace(ride_ns, path='/api/rides')
    api.add_namespace(dashboard_ns, path='/api/dashboard')
    api.add_namespace(admin_ns, path='/api/admin')
    api.add_namespace(notification_ns, path='/api')
    
    # Check for compiled frontend distribution folder
    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static_dist')
    if not os.path.exists(dist_dir):
        dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')
        
    if os.path.exists(dist_dir):
        from flask import send_from_directory
        
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            if path.startswith('api/') or path.startswith('docs') or path.startswith('swagger'):
                return jsonify({'error': 'Not found'}), 404
            if path != "" and os.path.exists(os.path.join(dist_dir, path)):
                return send_from_directory(dist_dir, path)
            return send_from_directory(dist_dir, 'index.html')
    else:
        # Basic health check endpoint when running API-only
        @app.route('/')
        def home():
            return jsonify({
                "message": "🚴‍♂️ Smart Ride Matcher API - Chennai Daily Commute",
                "status": "active",
                "version": "1.0.0",
                "swagger_ui": "/docs/",
                "features": [
                    "✅ User Authentication (JWT)",
                    "🏍️ Bike Registration & Management",
                    "🛣️ Ride Posting & Searching",
                    "🤝 Join Ride Requests",
                    "📊 User Dashboard & History",
                    "🤖 AI-Powered Route Matching",
                    "📍 Chennai Area Coverage",
                    "📱 Mobile-Friendly API"
                ]
            })
    
    # Configuration status endpoint
    @app.route('/api/status')
    def status():
        db_type = "Neon PostgreSQL" if Config.is_postgres() else "SQLite"
        return jsonify({
            "database": db_type,
            "authentication": "JWT",
            "api_docs": "Swagger/OpenAPI",
            "cors_enabled": True,
            "debug_mode": app.config.get('DEBUG', False),
            "gemini_ai_configured": Config.is_gemini_configured(),
            "gemini_model": Config.GEMINI_MODEL,
            "routing_engine": "OSRM + OpenStreetMap (Chennai Geo)",
            "status": "online"
        })
    
    return app

def run_app():
    """Run the Flask application"""
    # Get environment from environment variable or default to development
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create and run the app
    app = create_app(config_name)
    
    # Run with debug mode in development
    debug_mode = config_name == 'development'
    
    print("[INFO] Starting Smart Ride Matcher API...")
    print(f"   Environment: {config_name}")
    print(f"   Debug Mode: {debug_mode}")
    print(f"   URL: http://localhost:5000")
    print(f"   API Docs: http://localhost:5000/docs/")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        use_reloader=debug_mode
    )

if __name__ == '__main__':
    run_app() 