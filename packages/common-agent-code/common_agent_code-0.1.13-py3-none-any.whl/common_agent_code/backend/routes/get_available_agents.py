import json 
from flask import current_app as app
from flask import Blueprint
from common_agent_code.backend.utils import CustomJSONEncoder

available_agents_bp = Blueprint("available_agents", __name__, url_prefix="/api/agents")
@available_agents_bp.route('', methods=['GET'])
def get_available_agents():
    """Returns a list of available agents"""
    agents = [
        {
            "id": "data_analysis",
            "name": "Data Analysis Agent",
            "description": "An agent specialized in analyzing data through code execution."
        },
        {
            "id": "knowledge_extraction",
            "name": "Knowledge Extraction Agent",
            "description": "An agent for extracting knowledge from documents and the web."
        }
    ]
    return json.dumps(agents, cls = CustomJSONEncoder)
