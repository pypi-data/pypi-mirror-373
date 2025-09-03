from flask import current_app as app
from common_agent_code.backend.models import AgentDefinition, db
from flask import Blueprint, request, jsonify

home_bp = Blueprint("home", __name__, url_prefix="/")
@home_bp.route('/')
def home():
    return "Chat API is running"
