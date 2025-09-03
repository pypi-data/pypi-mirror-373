from flask import Blueprint,jsonify
from common_agent_code.backend.models import AgentDefinition, db
from flask import current_app as app

del_agent_def_bp = Blueprint("delete_agent_def", __name__, url_prefix="/api/agent-definition/<definition_id>")
@del_agent_def_bp.route('', methods=['DELETE'])
def delete_agent_definition(definition_id):
    """Delete an agent definition"""
    print(definition_id)
    try:
        # Can't delete built-in agents
        if definition_id in ['data_analysis', 'knowledge_extraction']:
            return jsonify({"error": "Cannot delete built-in agents"}), 400
            
        definition = AgentDefinition.query.get(definition_id)
        if not definition:
            return jsonify({"error": "Agent definition not found"}), 404
            
        db.session.delete(definition)
        db.session.commit()

        response = jsonify({"message": "Agent definition deleted successfully"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
