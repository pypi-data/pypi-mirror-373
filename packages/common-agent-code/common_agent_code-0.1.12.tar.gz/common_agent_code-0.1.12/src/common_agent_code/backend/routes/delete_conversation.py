from flask import Blueprint, jsonify
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend import db
from flask import current_app as app

delete_conv_bp = Blueprint("delete_conversation", __name__, url_prefix="/api/conversations/<conversation_id>")
@delete_conv_bp.route("", methods=["DELETE", "OPTIONS"])
def delete_conversation(conversation_id):
    try:
        messages = ChatHistory.query.filter_by(conversation_id=conversation_id).all()
        if not messages:
            return jsonify({"error": "Conversation not found"}), 404
        ChatHistory.query.filter_by(conversation_id=conversation_id).delete()
        db.session.commit()
        return jsonify({"message": "Conversation deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    