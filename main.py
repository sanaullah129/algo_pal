"""
Main application entry point for DSA Chatbot API.
FastAPI application with streaming responses and Azure OpenAI integration.
"""
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import json
import asyncio
import os
from datetime import datetime

# Core imports
from core.config import llm, system_prompt
from core.env import get_env_config
from core.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="DSA Chatbot API",
    description="Backend service for DSA and competitive programming mentoring",
    version="1.0.0",
    contact={"name": "DSA Mentorship Team", "email": "mentorship@dsa.org"},
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Global state management
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "current_problem": None,
                "difficulty_level": "beginner",
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat()
            }
        else:
            self.sessions[session_id]["last_accessed"] = datetime.utcnow().isoformat()
        return self.sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        if session_id in self.sessions:
            self.sessions[session_id]["history"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })

session_manager = SessionManager()

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message content")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation persistence")
    streaming: Optional[bool] = Field(True, description="Enable streaming response")

    @validator("session_id")
    def validate_session_id(cls, v):
        if v is None:
            return f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        return v

class CodeSample(BaseModel):
    language: str
    code: str
    description: Optional[str] = None

class ComplexityAnalysis(BaseModel):
    time_complexity: str
    space_complexity: str
    explanation: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    complexity: Optional[ComplexityAnalysis] = None
    code_samples: List[CodeSample] = []
    follow_up_suggestions: List[str] = []
    session_id: str
    timestamp: str
    streaming_complete: bool = False

class HealthCheckResponse(BaseModel):
    status: str
    version: str
    uptime: str
    dependencies: Dict[str, str]

# Environment Configuration
env_config = get_env_config()

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancing."""
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        uptime=datetime.utcnow().isoformat(),
        dependencies={
            "fastapi": "0.95.0",
            "langchain": "0.0.21",
            "langgraph": "0.150.16",
            "azure-openai": "1.0.0",
            "python-dotenv": "1.0.0"
        }
    )

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for DSA problem discussions."""
    try:
        # Get or create session
        session = session_manager.get_session(request.session_id)

        # Add user message to history
        session_manager.add_message(request.session_id, "user", request.message)

        # Generate response (with streaming support)
        response_content = await generate_dsa_response(
            request.message,
            session["history"],
            request.streaming
        )

        # Create response
        chat_response = ChatResponse(
            response=response_content["text"],
            complexity=response_content.get("complexity"),
            code_samples=response_content.get("code_samples", []),
            follow_up_suggestions=response_content.get("suggestions", []),
            session_id=request.session_id,
            timestamp=datetime.utcnow().isoformat(),
            streaming_complete=True
        )

        # Add assistant response to history
        session_manager.add_message(request.session_id, "assistant", response_content["text"])

        return chat_response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

async def generate_dsa_response(user_message: str, history: List[Dict], streaming: bool = True):
    """Generate DSA-focused response using Azure OpenAI with proper system prompt."""

    # Build conversation history
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_message}
    ]

    # Generate response using Azure OpenAI
    try:
        # This would use Azure OpenAI streaming or regular completion
        # Placeholder for actual LLM call
        response_text = "This is a placeholder response. Implement Azure OpenAI integration here."

        return {
            "text": response_text,
            "complexity": {
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "explanation": "Time and space complexity analysis"
            },
            "code_samples": [
                {
                    "language": "python",
                    "code": "# Code example would go here",
                    "description": "Implementation example"
                }
            ],
            "suggestions": [
                "Try implementing this with different data structures",
                "Consider edge cases for this problem",
                "Practice similar problems for reinforcement"
            ]
        }

    except Exception as e:
        return {
            "text": f"Error generating response: {str(e)}",
            "complexity": None,
            "code_samples": [],
            "suggestions": []
        }

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("DSA Chatbot API starting up...")
    print(f"Environment: {env_config.get('ENVIRONMENT', 'development')}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=env_config.get("HOST", "0.0.0.0"),
        port=int(env_config.get("PORT", 8000)),
        reload=env_config.get("DEBUG", False),
        log_level=env_config.get("LOG_LEVEL", "info")
    )