from flask import Blueprint, request, jsonify
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend import db
from flask import current_app as app

get_conversations_bp = Blueprint('get_conversations', __name__, url_prefix='/api/conversations')
@get_conversations_bp.route('', methods=['GET'])
def get_conversations():
    """Get all conversation IDs and their agent types"""
    try:
        # Query distinct conversation IDs and their agent types with aggregated timestamp
        conversations = db.session.query(
            ChatHistory.conversation_id,
            ChatHistory.agent_type,
            db.func.min(ChatHistory.timestamp).label('first_timestamp'),
            db.func.max(ChatHistory.timestamp).label('latest_timestamp')
        ).group_by(ChatHistory.conversation_id, ChatHistory.agent_type).order_by(
            db.func.max(ChatHistory.timestamp).desc()
        ).all()
        
        # Format the result
        result = []
        for convo_id, agent_type, first_timestamp, latest_timestamp in conversations:
            # Fetch first user message for preview
            first_user_msg = db.session.query(ChatHistory.content).filter_by(
                conversation_id=convo_id,
                role='user'
            ).order_by(ChatHistory.timestamp.asc()).first()

            preview = (first_user_msg[0][:20] + '...') if first_user_msg else "New Chat"
            label = f"Data_Agent - {preview}" if agent_type == "data_analysis" else f"{agent_type} - {preview}"

            result.append({
                "id": convo_id,
                "agent_type": agent_type,
                "label": label,
                "latest_timestamp": latest_timestamp.isoformat()
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

