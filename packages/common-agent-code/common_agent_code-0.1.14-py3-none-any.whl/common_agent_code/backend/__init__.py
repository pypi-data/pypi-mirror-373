# src/common_agent_code/backend/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from common_agent_code.backend.database.init_db import initialize_database

# Shared SQLAlchemy instance — do NOT re-declare elsewhere
db = SQLAlchemy()

def create_app():
    static_dir = os.getenv("FLASK_STATIC_DIR") or os.path.join(os.path.dirname(__file__), "static")
    app = Flask(__name__, static_folder=static_dir, static_url_path="/static")

    # Load configuration from config.py
    app.config.from_object('common_agent_code.backend.config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
    # Set up database and CORS
    db.init_app(app)
    CORS(app,
         origins=["http://localhost:8080", "http://127.0.0.1:8080"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         expose_headers=["Content-Type"],
         methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    )

    # Register all route blueprints
    from common_agent_code.backend.routes.create_agent_definitions import agent_def_bp
    from common_agent_code.backend.routes.create_conversation import create_conv
    from common_agent_code.backend.routes.home import home_bp
    from common_agent_code.backend.routes.delete_agent_definition import del_agent_def_bp
    from common_agent_code.backend.routes.delete_conversation import delete_conv_bp
    from common_agent_code.backend.routes.get_agent_conversations import get_agent_conversations_bp
    from common_agent_code.backend.routes.get_agent_definitions import get_agent_definitions_bp
    from common_agent_code.backend.routes.get_available_agents import available_agents_bp
    from common_agent_code.backend.routes.get_conversation_history import get_conversation_history_bp
    from common_agent_code.backend.routes.get_conversation_messages import get_conversation_messages_bp
    from common_agent_code.backend.routes.get_conversation import get_conversation_bp
    from common_agent_code.backend.routes.get_conversations import get_conversations_bp
    from common_agent_code.backend.routes.get_message_objects import get_message_objects_bp
    from common_agent_code.backend.routes.new_conversation import new_conversation_bp
    from common_agent_code.backend.routes.restore_state_from_message import restore_state_from_message_bp
    from common_agent_code.backend.routes.send_message import send_message_bp
    from common_agent_code.backend.routes.start_conversation import start_conversation_bp
    from common_agent_code.backend.routes.update_agent_definitions import update_agent_definitions_bp
    from common_agent_code.backend.routes.upload_file import upload_file_bp

    app.register_blueprint(agent_def_bp)
    app.register_blueprint(create_conv)
    app.register_blueprint(home_bp)
    app.register_blueprint(del_agent_def_bp)
    app.register_blueprint(delete_conv_bp)
    app.register_blueprint(get_agent_conversations_bp)
    app.register_blueprint(get_agent_definitions_bp)
    app.register_blueprint(available_agents_bp)
    app.register_blueprint(get_conversation_history_bp)
    app.register_blueprint(get_conversation_messages_bp)
    app.register_blueprint(get_conversation_bp)
    app.register_blueprint(get_conversations_bp)
    app.register_blueprint(get_message_objects_bp)
    app.register_blueprint(new_conversation_bp)
    app.register_blueprint(restore_state_from_message_bp)
    app.register_blueprint(send_message_bp)
    app.register_blueprint(start_conversation_bp)
    app.register_blueprint(update_agent_definitions_bp)
    app.register_blueprint(upload_file_bp)

    # Create upload folder if it doesn't exist
    UPLOAD_FOLDER = "uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Initialize additional SQLite tables if needed (non-SQLAlchemy)
    initialize_database()

    # Auto-create missing SQLAlchemy tables (like agent_definitions, chat_history, etc.)
    @app.before_request
    def create_all_tables():
        db.create_all()
    from flask import request
    def handle_preflight():
        if request.method == 'OPTIONS':
            return '', 200

    # Test route to verify static files
    @app.route('/test-static')
    def test_static():
        static_path = app.static_folder
        return f'<p>Static folder: {static_path}</p><a href="/static/test.txt">Test static file</a>'

    return app
