from flask import Blueprint, request, jsonify
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend import db
from flask import current_app as app

get_agent_conversations_bp = Blueprint("get_agent_conversations", __name__, url_prefix="/api/conversations/agent/<agent_id>") 
@get_agent_conversations_bp.route('', methods=['GET'])
def get_agent_conversations(agent_id):
    """Get all conversations for a specific agent"""
    try:
        # For built-in agents
        if agent_id in ['data_analysis', 'knowledge_extraction']:
            # Query conversations by agent_type
            conversation_ids = db.session.query(ChatHistory.conversation_id).filter_by(
                agent_type=agent_id
            ).distinct().all()
        else:
            # For custom agents, query by agent_definition_id
            conversation_ids = db.session.query(ChatHistory.conversation_id).filter_by(
                agent_definition_id=agent_id
            ).distinct().all()
        conversations = []
        for conv_id in conversation_ids:
            # Get the first user message as preview
            first_msg = ChatHistory.query.filter_by(
                conversation_id=conv_id[0],
                role='user'
            ).order_by(ChatHistory.timestamp.asc()).first()
            
            # Get the timestamp of conversation start
            start_time = ChatHistory.query.filter_by(
                conversation_id=conv_id[0]
            ).order_by(ChatHistory.timestamp.asc()).first()
            
            if first_msg and start_time:
                conversations.append({
                    "id": conv_id[0],
                    "preview": first_msg.content[:50] + "..." if len(first_msg.content) > 50 else first_msg.content,
                    "timestamp": start_time.timestamp.isoformat() if hasattr(start_time, 'timestamp') else None
                })
        # Sort conversations by timestamp (newest first)
        conversations.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "", reverse=True)
        
        return jsonify(conversations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
