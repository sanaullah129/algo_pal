"""
Core configuration for DSA Chatbot API.
Handles Azure OpenAI client initialization and environment configuration.
"""
from typing import Any, Dict
from openai import AzureOpenAI

from core.env import get_env_config
from prompts.dsa_system_prompt import get_dsa_system_prompt

class AzureConfig:
    """Handles Azure OpenAI configuration."""

    def __init__(self, env: Dict[str, Any]):
        self.api_key = env["AZURE_OPENAI_API_KEY"]
        self.endpoint = env["AZURE_OPENAI_ENDPOINT"]
        self.deployment_name = env["AZURE_OPENAI_DEPLOYMENT_NAME"]
        self.api_version = env["AZURE_OPENAI_API_VERSION"]
        self.model_name = env.get("AZURE_OPENAI_MODEL", self.deployment_name)
        self.embedding_deployment = env.get(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", self.deployment_name
        )
        self._validate_config()

    def _validate_config(self):
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not set")
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not set")
        if not self.deployment_name:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME is not set")

class LLMClient:
    """Manages Azure OpenAI client connections."""

    def __init__(self, config: AzureConfig):
        self.config = config
        self.client = self._create_client()

    def _create_client(self) -> AzureOpenAI:
        return AzureOpenAI(
            api_key=self.config.api_key,
            azure_endpoint=self.config.endpoint,
            api_version=self.config.api_version,
        )

    @property
    def chat_client(self) -> AzureOpenAI:
        return self.client

env_config = get_env_config()
azure_config = AzureConfig(env_config)
llm_client = LLMClient(azure_config)
system_prompt = get_dsa_system_prompt()


def create_app():
    """Create the FastAPI application instance."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(
        title="DSA Chatbot API",
        description="Backend service for DSA and competitive programming mentoring",
        version="1.0.0",
        contact={"name": "DSA Mentorship Team"},
        openapi_url="/api/docs/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app