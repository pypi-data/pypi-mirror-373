from flask import request, jsonify, Blueprint
from common_agent_code.backend.models import ChatHistory, AgentDefinition
from common_agent_code.backend import db
import uuid 
from common_agent_code.backend.utils import CustomJSONEncoder
from flask import current_app as app

start_conversation_bp = Blueprint('start_conversation', __name__, url_prefix='/api/conversation/start')
@start_conversation_bp.route('', methods=['POST'])
def start_conversation():
    """Starts a new conversation with the selected agent"""
    data = request.json
    agent_id = data.get('agent_id')
    print(agent_id)
    if not agent_id:
        return jsonify({"error": "Agent ID is required"}), 400

    conversation_id = str(uuid.uuid4())

    # Define tool access messages based on the agent type
    agent_tool_info = {
        "knowledge_extraction": (
            "Welcome to the Knowledge Extraction Agent! You have access to the following tools:\n\n"
            "🔹 **FAISS KNN** - Retrieve similar knowledge based on embeddings.\n"
            "🔹 **Knowledge Graph** - Explore relationships between concepts.\n"
            "🔹 **Web Search using FAISS KNN** - Find relevant information from indexed sources.\n\n"
            "How can I assist you?"
        ),
        "data_analysis": (
            "Welcome to the Data Analysis Agent! You have access to the **Code Executor**, which allows "
            "you to run Python code for data processing and analysis.\n\n"
            "How can I assist you?"
        )
    }

    # Get the appropriate welcome message, defaulting to a generic one
    welcome_message_text = agent_tool_info.get(agent_id, f"Welcome to the {agent_id} agent! How can I assist you?")
    definition = AgentDefinition.query.get(agent_id)

    if definition:
        agent_type = "custom"
        agent_definition_id = agent_id
    else:
        agent_type = agent_id  # 'data_analysis' or 'knowledge_extraction'
        agent_definition_id = None

    # Save the welcome message with correct agent type and definition
    welcome_message = ChatHistory(
        conversation_id=conversation_id,
        agent_type=agent_type,
        agent_definition_id=agent_definition_id,
        model_type=definition.model_type if definition else "gpt-4o",
        role="system",
        content=welcome_message_text
    )
    
    db.session.add(welcome_message)
    db.session.commit()

    return json.dumps({
        "conversation_id": conversation_id,
        "agent_id": agent_id,
        "message": welcome_message_text  # Include the message in the response
    }, cls=CustomJSONEncoder)

