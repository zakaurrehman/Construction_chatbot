"""
Application configuration.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Gemini API settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
    
    # Database settings
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 5432)),
        'dbname': os.environ.get('DB_NAME', 'construction_db'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'sslmode': os.environ.get('DB_SSLMODE', 'prefer')  # Added sslmode for Neon
    }
    
    # Application settings
    MAX_CONVERSATION_LENGTH = int(os.environ.get('MAX_CONVERSATION_LENGTH', 20))
    RESPONSE_TIMEOUT = int(os.environ.get('RESPONSE_TIMEOUT', 30))
    
    @staticmethod
    def init_app(app):
        """Initialize app with config."""
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}