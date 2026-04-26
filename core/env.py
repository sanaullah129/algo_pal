import os

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = "your_api_key"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT_NAME = "your-deployment-name"
AZURE_API_VERSION = "2023-05-15"

# Local Development Override
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8000")

# Log Level Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()