import json
from flask import Blueprint, request, jsonify
from common_agent_code.backend.models import ChatHistory

get_conversation_bp = Blueprint("get_conversation", __name__, url_prefix="/api/conversations/<string:conversation_id>")
@get_conversation_bp.route('', methods=['GET'])
def get_conversation(conversation_id):
    history = ChatHistory.query.filter_by(conversation_id=conversation_id).order_by(ChatHistory.timestamp).all()
    
    if not history:
        return jsonify({"error": "Conversation not found"}), 404

    # Get agent type
    agent_type = history[0].agent_type if history else None
    
    messages = []
    for msg in history:
        if msg.role == 'user':
            messages.append({
                "role": "user",
                "content": msg.content
            })
        else:  # assistant messages
            message_data = {
                "role": "assistant",
                "content": msg.content
            }
            
            # For knowledge extraction agent
            if msg.tool_used:
                message_data["tool_used"] = msg.tool_used
                message_data["tool_payload"] = json.loads(msg.tool_payload) if msg.tool_payload else None
                message_data["tool_output"] = json.loads(msg.tool_output) if msg.tool_output else None
                message_data["step_number"] = msg.step_number
            
            # For data analysis agent
            if agent_type == 'data_analysis' and msg.content.startswith('{') and msg.content.endswith('}'):
                try:
                    # Try to parse the content as JSON (for execution history)
                    execution_data = json.loads(msg.content)
                    if 'execution_history' in execution_data:
                        # Process execution history into a more frontend-friendly format
                        reasoning_steps = []
                        plot_paths = []
                        
                        for i, execution in enumerate(execution_data['execution_history']):
                            step = {
                                "step_number": i + 1,
                                "reasoning": execution.get('reasoning', ''),
                                "next_step": execution.get('next_step', ''),
                                "code": execution.get('code_to_execute', ''),
                            }
                            
                            # Add execution results if available
                            if 'result' in execution:
                                step["output"] = execution['result'].get('output', '')
                                step["error"] = execution['result'].get('error', '')
                                
                                # Extract any plot paths
                                if 'returned_objects' in execution['result']:
                                    returned_objects = execution['result']['returned_objects']
                                    if 'plot_path' in returned_objects:
                                        plot_path = returned_objects['plot_path']
                                        step["plot_path"] = plot_path
                                        plot_paths.append(plot_path)
                            
                            reasoning_steps.append(step)
                        
                        message_data["reasoning_steps"] = reasoning_steps
                        if plot_paths:
                            message_data["plot_paths"] = plot_paths
                except json.JSONDecodeError:
                    # If content is not valid JSON, just keep as is
                    pass
                
            messages.append(message_data)
            
    return jsonify(messages), 200