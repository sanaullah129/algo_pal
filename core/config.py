"""
Core configuration for DSA Chatbot API.
Handles FastAPI setup and Azure OpenAI client initialization.
"""
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

# Import Azure OpenAI client
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

class AzureConfig:
    """Handles Azure OpenAI configuration."""
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_API_VERSION", "2023-05-15")

        # Validate required config
        self._validate_config()

    def _validate_config(self):
        """Validate Azure configuration."""
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
        self.chat_client = self._create_chat_client()

    def _create_client(self) -> AzureOpenAI:
        """Create Azure OpenAI client."""
        return AzureOpenAI(
            api_key=self.config.api_key,
            azure_endpoint=self.config.endpoint,
            api_version=self.config.api_version
        )

    def _create_chat_client(self) -> AzureOpenAI:
        """Create dedicated chat client."""
        return AzureOpenAI(
            api_key=self.config.api_key,
            azure_endpoint=self.config.endpoint,
            api_version=self.config.api_version
        )

# Global configuration
azure_config = AzureConfig()
llm_client = LLMClient(azure_config)

# System prompt for DSA mentoring
SYSTEM_PROMPT = """
You are a senior Data Structures and Algorithms mentor and competitive programming coach.

Your Role:
- Explain DSA concepts clearly with practical examples
- Provide step-by-step problem solving approaches
- Analyze time and space complexity thoroughly
- Compare brute force vs optimized solutions
- Provide code samples in Python and/or JavaScript
- Identify related problems and patterns
- Suggest follow-up problems for practice
- Maintain conversational context per session

Required Behavior:
- Always use proper algorithm terminology
- Draw connections between different concepts
- Suggest efficient data structures
- Highlight common mistakes and edge cases
- Include multiple examples and variations
- Recommend practice strategies
- Analyze complexity of proposed solutions
- Provide clear code implementations

Response Format:
- Start with conceptual explanation
- Provide step-by-step approach
- Include complexity analysis (Time & Space)
- Provide code samples when relevant
- Suggest related problems and practice strategies
"""

def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    app = FastAPI(
        title="DSA Chatbot API",
        description="Backend service for DSA and competitive programming mentoring",
        version="1.0.0",
        contact={"name": "DSA Mentorship Team"},
        openapi_url="/api/docs/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

# Initialize FastAPI app
app = create_app()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": "active",
        "dependencies": {
            "azure-openai": "configured",
            "fastapi": "running"
        }
    }