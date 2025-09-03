import json
from flask import request, jsonify, Blueprint
from common_agent_code.backend.models import AgentDefinition
from common_agent_code.backend import db
from flask import current_app as app

update_agent_definitions_bp = Blueprint('update_agent_definitions', __name__, url_prefix='/api/agent-definitions/<definition_id>')
@update_agent_definitions_bp.route('', methods=['PUT'])
def update_agent_definition(definition_id):
    """Update an agent definition"""
    try:
        # Can't update built-in agents
        if definition_id in ['data_analysis', 'knowledge_extraction']:
            return jsonify({"error": "Cannot update built-in agents"}), 400
            
        definition = AgentDefinition.query.get(definition_id)
        if not definition:
            return jsonify({"error": "Agent definition not found"}), 404
            
        data = request.json
        
        # Update fields if provided
        if 'model_type' in data:
            definition.model_type = data['model_type']
        if 'name' in data:
            definition.name = data['name']
        if 'system_prompt' in data:
            definition.system_prompt = data['system_prompt']
        if 'tools' in data:
            definition.tools = json.dumps(data['tools'])
        if 'memory_enabled' in data:
            definition.memory_enabled = data['memory_enabled']
        if 'tasks' in data:
            definition.tasks = json.dumps(data['tasks'])
            
        db.session.commit()
        
        return jsonify({"message": "Agent definition updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
