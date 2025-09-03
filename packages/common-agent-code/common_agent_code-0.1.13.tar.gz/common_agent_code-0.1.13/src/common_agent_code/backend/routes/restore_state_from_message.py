from flask import request, jsonify, Blueprint
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend import db
from flask import current_app as app

restore_state_from_message_bp = Blueprint('restore_state_from_message', __name__, url_prefix='/api/conversations/<string:conversation_id>/state/restore')
# Add a new endpoint to update the state with objects from a previous message
@restore_state_from_message_bp.route('', methods=['POST'])
def restore_state_from_message(conversation_id):
    """Restore state from pickled objects in a message"""
    try:
        data = request.json
        message_id = data.get('message_id')
        
        if not message_id:
            return jsonify({"error": "Message ID is required"}), 400
            
        message = ChatHistory.query.get(message_id)
        if not message:
            return jsonify({"error": "Message not found"}), 404
            
        if not hasattr(message, 'pickled_objects') or not message.pickled_objects:
            return jsonify({"error": "No pickled objects found in this message"}), 404
            
        # Create a state message to store the restored state
        state_message = ChatHistory(
            conversation_id=conversation_id,
            agent_type=message.agent_type,
            role="system",
            content=f"State restored from message ID: {message_id}"
        )
        
        # Copy the pickled objects from the source message
        state_message.pickled_objects = message.pickled_objects
        
        db.session.add(state_message)
        db.session.commit()
        
        # Return a summary of restored objects
        objects = message.load_objects()
        restored_keys = list(objects.keys())
        
        return jsonify({
            "success": True,
            "message": f"State restored with {len(restored_keys)} objects: {', '.join(restored_keys)}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
