from flask import Blueprint, Flask, request, jsonify
from common_agent_code.backend.models import AgentDefinition, db
import json
from flask import current_app as app

agent_def_bp = Blueprint("agent_def", __name__, url_prefix="/api/agent-definitions")

@agent_def_bp.route("", methods=["POST"])
def create_agent_definition():
    """Create a new agent definition"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['model_type', 'name', 'system_prompt']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create new agent definition
        new_definition = AgentDefinition(
            model_type=data['model_type'],
            name=data['name'],
            system_prompt=data['system_prompt'],
            tools=json.dumps(data.get('tools', [])),
            memory_enabled=data.get('memory_enabled', False),
            tasks=json.dumps(data.get('tasks', []))
        )
        
        db.session.add(new_definition)
        db.session.commit()
        
        return jsonify({
            "id": new_definition.id,
            "message": "Agent definition created successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
