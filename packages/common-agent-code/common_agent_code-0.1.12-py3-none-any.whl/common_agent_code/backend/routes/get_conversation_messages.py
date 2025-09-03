from flask import Blueprint, request, jsonify
from common_agent_code.backend.models import ChatHistory
from flask import current_app as app

get_conversation_messages_bp = Blueprint('get_conversation_messages', __name__, url_prefix='/api/conversations/<conversation_id>/messages')
@get_conversation_messages_bp.route('', methods=['GET'])
def get_conversation_messages(conversation_id):
    try:
        messages = ChatHistory.query.filter_by(conversation_id=conversation_id).order_by(ChatHistory.timestamp.asc()).all()
        message_data = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for msg in messages
        ]
        return jsonify(message_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
