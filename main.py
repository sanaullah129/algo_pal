"""
Main application entry point for DSA Chatbot API.
FastAPI application with modular chat routing and persistence.
"""
from datetime import datetime

from core.config import create_app, env_config
from core.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware
from routes.chat import router as chat_router

app = create_app()
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.include_router(chat_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancing."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": datetime.utcnow().isoformat(),
        "dependencies": {
            "fastapi": "0.95.0",
            "langchain": "0.0.21",
            "langgraph": "0.150.16",
            "azure-openai": "1.0.0",
            "python-dotenv": "1.0.0",
            "qdrant-client": "compatible",
            "pymongo": "compatible"
        }
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