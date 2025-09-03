from flask import Blueprint, request, jsonify
from common_agent_code.backend.models import ChatHistory, AgentDefinition
from common_agent_code.backend import db
import os
from common_agent_code.backend.utils import load_file_by_type, handle_data_analysis, handle_knowledge_extraction, handle_custom_agent
from flask import current_app as app

send_message_bp = Blueprint('send_message', __name__, url_prefix='/api/conversations/<conversation_id>/messages')
@send_message_bp.route('', methods=['POST'])
def send_message(conversation_id):
    """Send a message to an agent"""
    try:
        print(f"📨 Received request for conversation: {conversation_id}")
        data = request.json or {}
        print(f"🧾 Request data: {data}")

        message = data.get('message', '').strip()
        file_paths = data.get('file_paths', [])
        
        preserved_objects = {}
        last_memory_state = ChatHistory.query.filter(
            ChatHistory.conversation_id == conversation_id,
            ChatHistory.pickled_objects.isnot(None)
        ).order_by(ChatHistory.timestamp.desc()).first()

        if last_memory_state:
            print("🧠 Found and loaded a previous state from the database.")
            preserved_objects = last_memory_state.load_objects()
        else:
            print("🧠 No previous state found. Starting fresh.")

        valid_paths = [p for p in file_paths if p and os.path.exists(p)]
        if valid_paths:
            print(f"📂 Loading new files for this turn: {valid_paths}")
            for file_path in valid_paths:
                try:
                    content, content_type = load_file_by_type(file_path)
                    # Create clean variable names without file extensions
                    file_name = os.path.basename(file_path)
                    clean_name = os.path.splitext(file_name)[0]  # Remove extension
                    
                    # Use a more user-friendly variable name
                    if content_type == 'df':
                        var_name = f"df_{clean_name}" if not clean_name.startswith('df') else clean_name
                    else:
                        var_name = f"{content_type}_{clean_name}"
                    
                    preserved_objects[var_name] = content
                    print(f"📊 Loaded {content_type} as variable: {var_name}")
                except Exception as e:
                    print(f"⚠️ Error loading file {file_path}: {e}")
        
        print(f"🔄 Current state includes objects: {list(preserved_objects.keys())}")

        # Fetch agent info
        agent_query = db.session.query(
            ChatHistory.agent_type,
            ChatHistory.model_type,
            ChatHistory.agent_definition_id
        ).filter_by(conversation_id=conversation_id).first()

        if not agent_query:
            return jsonify({"error": "Agent not found"}), 404

        agent_type, model_type, agent_definition_id = agent_query

        # Save user message
        user_message = ChatHistory(
            conversation_id=conversation_id,
            agent_type=agent_type,
            model_type=model_type,
            agent_definition_id=agent_definition_id,
            role="user",
            content=message
        )
        db.session.add(user_message)
        db.session.commit()

        # Handle based on agent type
        if agent_type == 'data_analysis':
            result = handle_data_analysis(conversation_id, message, valid_paths[0] if valid_paths else None)

        elif agent_type == 'knowledge_extraction':
            result = handle_knowledge_extraction(conversation_id, message)

        elif agent_type == 'custom' and agent_definition_id:
            definition = AgentDefinition.query.get(agent_definition_id)
            if not definition:
                return jsonify({"error": "Agent definition not found"}), 404

            # Forward only the first file for now (extendable later)
            result = handle_custom_agent(conversation_id, message, definition,
                                         preserved_objects=preserved_objects)
        else:
            return jsonify({"error": "Unsupported agent type"}), 400

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500
