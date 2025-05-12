
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
import logging
import os

def create_app(config_class=Config):
    """Create Flask application instance."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Enable CORS with specific options
    CORS(app, 
         origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'OPTIONS']
    )
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Register blueprints
    from routes import api_bp
    app.register_blueprint(api_bp)
    
    # Add a simple test route
    @app.route('/test')
    def test():
        return {'message': 'Server is running!'}
    
    # Serve React app in production
    if not app.debug:
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_react(path):
            if path != "" and os.path.exists(os.path.join('frontend/build', path)):
                return send_from_directory('frontend/build', path)
            else:
                return send_from_directory('frontend/build', 'index.html')
    
    return app