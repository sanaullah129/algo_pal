import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv


def get_env_config() -> Dict[str, Any]:
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    return {
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "DEBUG": os.getenv("DEBUG", "False").lower() in ("1", "true", "yes"),
        "HOST": os.getenv("HOST", "0.0.0.0"),
        "PORT": int(os.getenv("PORT", "8000")),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "info").lower(),
        "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        "MONGODB_DB": os.getenv("MONGODB_DB", "algo_pal"),
        "MONGODB_COLLECTION": os.getenv("MONGODB_COLLECTION", "chat_sessions"),
        "QDRANT_URL": os.getenv("QDRANT_URL", "http://localhost:6333"),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY"),
        "QDRANT_COLLECTION": os.getenv("QDRANT_COLLECTION", "algo_pal_graph"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
        "AZURE_OPENAI_MODEL": os.getenv("AZURE_OPENAI_MODEL", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")),
    }
