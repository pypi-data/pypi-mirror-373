from flask import Blueprint, jsonify
from common_agent_code.backend.models import AgentDefinition
from common_agent_code.backend.utils import CustomJSONEncoder
import json
from flask import current_app as app

get_agent_definitions_bp = Blueprint("get_agent_definitions", __name__, url_prefix="/api/agent-definitions")
@get_agent_definitions_bp.route('', methods=['GET'])
def get_agent_definitions():
    """Get all agent definitions"""
    try:
        # Get built-in agents (data_analysis and knowledge_extraction)
        built_in_agents = [
            {
                "id": "data_analysis",
                "name": "Data Analysis Agent",
                "description": "An agent specialized in analyzing data through code execution.",
                "model_type": "gpt-4o",  # Default model for built-in agents
                "system_prompt": "You are a data analysis agent specialized in trading analysis. You can execute Python code, analyze market data, and provide insights on trading opportunities. Always be precise and data-driven in your analysis.",
                "is_built_in": True
            },
            {
                "id": "knowledge_extraction",
                "name": "Knowledge Extraction Agent",
                "description": "An agent for extracting knowledge from documents and the web.",
                "model_type": "gpt-4o",  # Default model for built-in agents
                "system_prompt": "You are a knowledge extraction agent for market research. You can search the web, process documents, and build knowledge graphs to provide comprehensive market insights and trading recommendations.",
                "is_built_in": True
            }
        ]
        
        # Get custom agents from database
        custom_agents = []
        definitions = AgentDefinition.query.all()
        for definition in definitions:
            custom_agents.append({
                "id": definition.id,
                "name": definition.name,
                "description": f"Custom agent using {definition.model_type}",
                "model_type": definition.model_type,
                "system_prompt": getattr(definition, 'system_prompt', '') or '',
                "memory_enabled": definition.memory_enabled,
                "is_built_in": False
            })
        
        # Combine both types
        all_agents = built_in_agents + custom_agents
        return json.dumps(all_agents, cls=CustomJSONEncoder)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
