"""
API routes for the chatbot application.
"""
from flask import Blueprint, request, jsonify, current_app
import logging
from chatbot.chat_handler import ChatHandler
from config import Config

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize chat handler
chat_handler = ChatHandler(
    api_key=Config.GEMINI_API_KEY,
    db_config=Config.DB_CONFIG
)

# In-memory conversation store (use Redis for production)
conversations = {}

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        message = data.get('message')
        chat_id = data.get('chat_id', 'default')
        
        # Get conversation history
        conversation = conversations.get(chat_id, [])
        
        # Process message
        response = chat_handler.process_query(message, conversation)
        
        # Update conversation history
        conversation.append({'role': 'user', 'content': message})
        conversation.append({'role': 'assistant', 'content': response['message']})
        
        # Keep only last N messages
        conversations[chat_id] = conversation[-Config.MAX_CONVERSATION_LENGTH:]
        
        return jsonify({
            'message': response['message'],
            'success': response['success'],
            'chat_id': chat_id
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check"""
    try:
        # Test database connection
        chat_handler.db.execute_query("SELECT 1")
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'api': 'operational'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@api_bp.route('/tables', methods=['GET'])
def get_tables():
    """Get available database tables and schema"""
    try:
        schema = chat_handler.db.get_schema_summary()
        
        return jsonify({
            'tables': list(schema.keys()),
            'schema': schema,
            'count': len(schema)
        })
    except Exception as e:
        logger.error(f"Error getting tables: {e}")
        return jsonify({
            'error': 'Failed to get tables',
            'message': str(e)
        }), 500

@api_bp.route('/clear-chat/<chat_id>', methods=['POST'])
def clear_chat(chat_id):
    """Clear conversation history for a specific chat"""
    try:
        if chat_id in conversations:
            del conversations[chat_id]
        
        return jsonify({
            'success': True,
            'message': f'Chat {chat_id} cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing chat {chat_id}: {e}")
        return jsonify({
            'error': 'Failed to clear chat',
            'message': str(e)
        }), 500

# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500