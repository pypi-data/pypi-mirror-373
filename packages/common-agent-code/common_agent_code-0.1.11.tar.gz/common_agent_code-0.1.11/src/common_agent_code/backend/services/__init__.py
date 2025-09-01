# __init__.py in services/
from .faiss_service import *
from .openai_client import *
from .llm_service import *
from .graph_service import *
from .nlp_service import *
from .pdf_service import *
from .web_service import *

from openai import AzureOpenAI
import os

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY", "your-api-key-here"),
    api_version="2024-02-15-preview",
    azure_endpoint="https://radiusofself.openai.azure.com",
    azure_deployment="gpt-4o"
)