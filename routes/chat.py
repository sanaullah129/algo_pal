from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from core.config import env_config, llm_client, system_prompt
from services.langchain_qdrant import LangchainQdrantService
from services.mongo_store import MongoChatStore
from agents.dsa_agent import DSAConversationAgent

router = APIRouter(tags=["Chat"])

chat_store = MongoChatStore(
    uri=env_config.get("MONGODB_URI"),
    db_name=env_config.get("MONGODB_DB"),
    collection_name=env_config.get("MONGODB_COLLECTION"),
)
vector_service = LangchainQdrantService(config=env_config)
conversation_agent = DSAConversationAgent(
    llm_client=llm_client,
    system_prompt=system_prompt,
    chat_store=chat_store,
    vector_service=vector_service,
)


class CodeSample(BaseModel):
    language: str
    code: str
    description: Optional[str] = None


class ComplexityAnalysis(BaseModel):
    time_complexity: str
    space_complexity: str
    explanation: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message content")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation persistence")
    streaming: Optional[bool] = Field(True, description="Enable streaming response")

    @validator("session_id")
    def validate_session_id(cls, v):
        if v is None:
            return f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        return v


class ChatResponse(BaseModel):
    response: str
    complexity: Optional[ComplexityAnalysis] = None
    code_samples: List[CodeSample] = []
    follow_up_suggestions: List[str] = []
    session_id: str
    timestamp: str
    streaming_complete: bool = False


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = await conversation_agent.process_message(request.message, request.session_id)
        return ChatResponse(
            response=result["response"],
            complexity=result.get("complexity"),
            code_samples=result.get("code_samples", []),
            follow_up_suggestions=result.get("suggestions", []),
            session_id=result["session_id"],
            timestamp=datetime.utcnow().isoformat(),
            streaming_complete=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {exc}")
