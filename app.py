"""
Entry point for the construction project management chatbot.
"""
import os
from main import create_app

def main():
    """Run the application."""
    try:
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Create Flask app
        app = create_app()
        
        # Run the app
        print(f"Starting chatbot server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except Exception as e:
        print(f"Error starting application: {e}")
        raise

if __name__ == '__main__':
    main()