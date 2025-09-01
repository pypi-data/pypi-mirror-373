import uuid
from flask import jsonify, Blueprint
from flask import current_app as app

new_conversation_bp = Blueprint('new_conversation', __name__, url_prefix='/conversations/new')
@new_conversation_bp.route('', methods=['POST'])
def new_conversation():
    try:
        conversation_id = str(uuid.uuid4())
        return jsonify({"id": conversation_id, "preview": "New conversation"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

