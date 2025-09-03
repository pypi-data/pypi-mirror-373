from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import pickle
from common_agent_code.backend import db

class AgentDefinition(db.Model):
    __tablename__ = 'agent_definitions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_type = db.Column(db.String(40), nullable=False)  # GPT-4o, Claude Sonet, etc.
    name = db.Column(db.String(100), nullable=False)
    system_prompt = db.Column(db.Text, nullable=False)
    tools = db.Column(db.Text, nullable=True)  # JSON string of tool configs
    memory_enabled = db.Column(db.Boolean, default=False)
    tasks = db.Column(db.Text, nullable=True)  # Optional default tasks
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AgentDefinition {self.name} ({self.model_type})>'

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(36), nullable=False)
    agent_type = db.Column(db.String(40), nullable=False)  # 'data_analysis', 'knowledge_extraction', or 'custom'
    model_type = db.Column(db.String(40), nullable=False)  # 'gpt-4o', 'claude-sonnet', etc.
    agent_definition_id = db.Column(db.String(36), db.ForeignKey('agent_definitions.id'), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'system', 'user', or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Fields for data analysis agent
    code = db.Column(db.Text, nullable=True)
    output = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    plot_path = db.Column(db.String(255), nullable=True)
    plot_paths = db.Column(db.Text, nullable=True)  # JSON string of plot paths
    pickled_objects = db.Column(db.LargeBinary, nullable=True)
    execution_history = db.Column(db.Text, nullable=True)
    
    # Fields for knowledge extraction agent
    tool_used = db.Column(db.String(100), nullable=True)
    tool_payload = db.Column(db.Text, nullable=True)
    tool_output = db.Column(db.Text, nullable=True)
    step_number = db.Column(db.Integer, nullable=True)
    
    # Relationship to agent definition
    agent_definition = db.relationship('AgentDefinition', backref='conversations', foreign_keys=[agent_definition_id])
    
    def save_objects(self, objects_dict):
        """Pickle and save Python objects"""
        try:
            # Filter out non-picklable objects (e.g., modules, functions)
            # This is a critical step to prevent pickling errors
            filtered_objects = {}
            for key, obj in objects_dict.items():
                try:
                    # Attempt to pickle a dummy object to check picklability
                    # This is a more robust check than type checking
                    pickle.dumps(obj)
                    filtered_objects[key] = obj
                except TypeError as e:
                    print(f"⚠️ Warning: Object '{key}' of type {type(obj)} is not picklable. Skipping. Error: {e}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not check picklability of object '{key}': {e}")


            if filtered_objects:
                print(f"📦 Pickling filtered objects: {filtered_objects.keys()}")
                self.pickled_objects = pickle.dumps(filtered_objects)
            else:
                self.pickled_objects = None
                print("No picklable objects to save.")

        except Exception as e:
            print(f"Error pickling objects: {e}")

    def load_objects(self):
        """Load pickled Python objects"""
        if not self.pickled_objects:
            return {}
        try:
            return pickle.loads(self.pickled_objects)
        except Exception as e:
            print(f"Error unpickling objects: {e}")
            return {}