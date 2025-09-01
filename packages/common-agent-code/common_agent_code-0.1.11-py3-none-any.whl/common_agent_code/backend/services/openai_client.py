from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY", "your-api-key-here"),
    api_version="2024-02-15-preview",
    azure_endpoint="https://radiusofself.openai.azure.com",
    azure_deployment="gpt-4o"
)