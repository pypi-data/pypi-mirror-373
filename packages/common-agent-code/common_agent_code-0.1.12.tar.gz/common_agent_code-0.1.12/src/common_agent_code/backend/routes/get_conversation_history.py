from flask import Flask, request, jsonify, Blueprint
from common_agent_code.backend.models import ChatHistory
import json
from flask import current_app as app
from common_agent_code.backend.utils import CustomJSONEncoder


get_conversation_history_bp = Blueprint("get_conversation_history", __name__, url_prefix="/api/conversations/<string:conversation_id>")
@get_conversation_history_bp.route('', methods=['GET'])
def get_conversation_history(conversation_id):
    """Get chat history for a specific conversation"""
    try:
        messages = ChatHistory.query.filter_by(
            conversation_id=conversation_id
        ).order_by(ChatHistory.timestamp).all()
        
        # Get the agent type
        agent_type = None
        if messages:
            agent_type = messages[0].agent_type
        
        # Format the result
        result = []
        for msg in messages:
            message_data = {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }

            has_objects = False
            if hasattr(msg, 'pickled_objects') and msg.pickled_objects:
                has_objects = True
                message_data["has_pickled_objects"] = True

            if msg.code:
                message_data["code"] = msg.code
            if msg.output:
                message_data["output"] = msg.output
            if msg.error:
                message_data["error"] = msg.error
            if msg.plot_path:
                message_data["plot_path"] = msg.plot_path
            if msg.plot_paths:
                message_data["plot_paths"] = json.loads(msg.plot_paths)
            # Add tool-related fields for knowledge extraction agent
            if msg.tool_used:
                message_data["tool_used"] = msg.tool_used
                message_data["tool_payload"] = msg.tool_payload
                message_data["tool_output"] = msg.tool_output
                message_data["step_number"] = msg.step_number
            
            # Add execution data for data analysis agent if available
            if agent_type == 'data_analysis' and msg.role == 'system' and msg.content.startswith('{') and msg.content.endswith('}'):
                try:
                    # Try to parse the content as JSON (for execution history)
                    execution_data = json.loads(msg.content)
                    if 'execution_history' in execution_data:
                        # Extract the execution history
                        message_data["execution_history"] = execution_data['execution_history']
                        
                        # Extract plot paths
                        plot_paths = []
                        for execution in execution_data['execution_history']:
                            if 'result' in execution and 'returned_objects' in execution['result']:
                                if 'plot_path' in execution['result']['returned_objects']:
                                    plot_paths.append(execution['result']['returned_objects']['plot_path'])
                        
                        if plot_paths:
                            message_data["plot_paths"] = plot_paths
                except json.JSONDecodeError:
                    # If content is not valid JSON, just keep as is
                    pass
                
            result.append(message_data)
            
        return json.dumps(result, cls = CustomJSONEncoder)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    