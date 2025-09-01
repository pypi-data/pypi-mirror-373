from flask import Blueprint, request, jsonify
from common_agent_code.backend.models import ChatHistory, AgentDefinition
from common_agent_code.backend import db
import uuid
from flask import current_app as app

create_conv = Blueprint("create_conv", __name__, url_prefix="/api/conversations")


@create_conv.route('', methods=['POST'])
def create_conversation():
    """Create a new conversation with the specified agent"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({"error": "Agent ID is required"}), 400
        
        # Generate a unique conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Check if this is a built-in agent or custom agent
        if agent_id in ['data_analysis', 'knowledge_extraction']:
            # Handle built-in agent
            agent_type = agent_id
            model_type = 'gpt-4o'  # Default model for built-in agents
            
            # Create a welcome message
            welcome_message = ChatHistory(
                conversation_id=conversation_id,
                agent_type=agent_type,
                model_type=model_type,
                role="system",
                content=f"Welcome to the {agent_type} agent! How can I help you today?"
            )
            
            db.session.add(welcome_message)
            db.session.commit()
            
            return jsonify({
                "conversation_id": conversation_id,
                "agent_id": agent_id,
                "agent_type": agent_type,
                "model_type": model_type,
                "is_built_in": True
            })
        else:
            # Handle custom agent
            definition = AgentDefinition.query.get(agent_id)
            if not definition:
                return jsonify({"error": "Agent definition not found"}), 404
                
            # Create a welcome message
            welcome_message = ChatHistory(
                conversation_id=conversation_id,
                agent_type="custom",
                model_type=definition.model_type,
                agent_definition_id=definition.id,
                role="system",
                content=f"Welcome to {definition.name}! How can I help you today?"
            )
            
            db.session.add(welcome_message)
            db.session.commit()
            
            return jsonify({
                "conversation_id": conversation_id,
                "agent_id": agent_id,
                "agent_type": "custom",
                "model_type": definition.model_type,
                "agent_name": definition.name,
                "is_built_in": False
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
