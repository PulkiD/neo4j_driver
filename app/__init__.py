"""
Main application module.

This module initializes the Flask application and registers all blueprints.
"""

import os
from flask import Flask
from dotenv import load_dotenv
from app.api.query_routes import query_bp
from app.utils.logger import get_logger

logger = get_logger()

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: The configured Flask application instance
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(query_bp)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return {'status': 'healthy'}, 200
    
    logger.info("Flask application initialized successfully")
    return app 