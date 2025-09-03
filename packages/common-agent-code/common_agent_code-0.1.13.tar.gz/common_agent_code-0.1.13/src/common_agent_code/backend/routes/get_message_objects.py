import json
from flask import jsonify, Blueprint
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend.utils import CustomJSONEncoder
import pandas as pd
import numpy as np
from flask import current_app as app

get_message_objects_bp = Blueprint('get_message_objects', __name__, url_prefix='/api/messages/<int:message_id>/objects')
@get_message_objects_bp.route('', methods=['GET'])
def get_message_objects(message_id):
    """Get pickled objects for a specific message"""
    try:
        message = ChatHistory.query.get(message_id)
        if not message:
            return jsonify({"error": "Message not found"}), 404
            
        if not hasattr(message, 'pickled_objects') or not message.pickled_objects:
            return jsonify({"error": "No pickled objects found"}), 404
            
        # Load the objects
        objects = message.load_objects()
        
        # Convert objects to a summary format for API response
        objects_summary = {}
        for key, value in objects.items():
            if isinstance(value, pd.DataFrame):
                objects_summary[key] = {
                    "type": "DataFrame",
                    "shape": value.shape,
                    "columns": list(value.columns),
                    "head": value.head(3).to_dict('records')
                }
            elif isinstance(value, np.ndarray):
                objects_summary[key] = {
                    "type": "ndarray",
                    "shape": value.shape,
                    "sample": value.flatten()[:5].tolist() if value.size > 0 else []
                }
            else:
                objects_summary[key] = {
                    "type": type(value).__name__,
                    "summary": str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                }
        
        return json.dumps({"objects": objects_summary}, cls=CustomJSONEncoder)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

