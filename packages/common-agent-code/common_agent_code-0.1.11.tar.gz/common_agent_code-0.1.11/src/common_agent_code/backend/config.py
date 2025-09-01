import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    DEBUG = True
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///chat_history.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API Keys (optional if needed globally)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

    # Optional: raise error at load time
    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")