"""
LangGraph-based agent for DSA problem solving.
Implements stateful conversation management with memory and retrieval.
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import uuid
import re

from langgraph.graph import StateGraph, END

from services.mongo_store import MongoChatStore
from services.langchain_qdrant import LangchainQdrantService

# Type definitions for state management
class ChatState(TypedDict):
    """Graph state for conversation management."""
    session_id: str
    messages: List[Dict[str, Any]]
    current_problem: Optional[str]
    current_topic: Optional[str]
    difficulty_level: str
    problem_history: List[str]
    response: Optional[str]
    complexity_analysis: Optional[Dict[str, str]]
    code_samples: List[Dict[str, str]]
    follow_up_suggestions: List[str]
    metadata: Dict[str, Any]

class DSAConversationAgent:
    """Manages stateful DSA conversations using LangGraph."""

    def __init__(
        self,
        llm_client,
        system_prompt: str,
        chat_store: MongoChatStore,
        vector_service: LangchainQdrantService,
    ):
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.chat_store = chat_store
        self.vector_service = vector_service
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow for DSA conversations."""
        workflow = StateGraph(ChatState)
        workflow.add_node("initializer", self._initialize_conversation)
        workflow.add_node("analyzer", self._analyze_problem)
        workflow.add_node("responder", self._generate_response)
        workflow.add_node("updater", self._update_state)

        workflow.set_entry_point("initializer")
        workflow.add_edge("initializer", "analyzer")
        workflow.add_edge("analyzer", "responder")
        workflow.add_edge("responder", "updater")
        workflow.add_edge("updater", END)

        return workflow

    def _initialize_conversation(self, state: ChatState) -> ChatState:
        """Initialize or retrieve conversation state."""
        if not state.get("session_id"):
            state["session_id"] = str(uuid.uuid4())

        if not state.get("messages"):
            state["messages"] = []

        if not state["messages"] or state["messages"][0].get("role") != "system":
            state["messages"].insert(0, {"role": "system", "content": self.system_prompt})

        state["metadata"] = {
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "initialized",
        }

        if "problem_history" not in state or state["problem_history"] is None:
            state["problem_history"] = []

        return state

    def _analyze_problem(self, state: ChatState) -> ChatState:
        """Analyze current problem and determine appropriate strategy."""
        last_message = state["messages"][-1]
        if last_message["role"] != "user":
            return state

        content = last_message["content"].strip()
        state["current_problem"] = content
        state["difficulty_level"] = self._estimate_difficulty(content)
        state["current_topic"] = self._detect_topic(content)
        state["problem_history"].append(content)

        similar_documents = self.vector_service.semantic_search(content, top_k=3)
        if similar_documents:
            state["metadata"]["related_context"] = [
                {
                    "content": doc.page_content,
                    **doc.metadata,
                }
                for doc in similar_documents
            ]

        return state

    def _generate_response(self, state: ChatState) -> ChatState:
        """Generate response using LLM and retrieved graph context."""
        user_message = state["messages"][-1]
        if user_message["role"] != "user":
            return state

        messages = [
            {"role": message["role"], "content": message["content"]}
            for message in state["messages"]
        ]

        related_context = state["metadata"].get("related_context", [])
        if related_context:
            context_text = "\n\n".join(
                f"Previous {item.get('role', 'assistant')} memory: {item.get('content', '')}"
                for item in related_context
            )
            messages.insert(
                1,
                {
                    "role": "system",
                    "content": "Relevant historical context from previous sessions:\n" + context_text,
                },
            )

        response_text = self._call_llm(messages)
        response_data = self._parse_structured_response(response_text)

        state["response"] = response_data["text"]
        state["complexity_analysis"] = response_data.get("complexity")
        state["code_samples"] = response_data.get("code_samples", [])
        state["follow_up_suggestions"] = response_data.get("suggestions", [])

        state["messages"].append({"role": "assistant", "content": response_data["text"]})
        state["metadata"]["last_response_at"] = datetime.utcnow().isoformat()

        self.vector_service.add_message_embedding(
            state["session_id"], "user", user_message["content"]
        )
        self.vector_service.add_message_embedding(
            state["session_id"], "assistant", response_data["text"]
        )

        self.chat_store.update_graph_state(
            state["session_id"],
            {
                "current_problem": state["current_problem"],
                "current_topic": state["current_topic"],
                "difficulty_level": state["difficulty_level"],
                "metadata": state["metadata"],
            },
        )

        return state

    def _parse_structured_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        return {
            "text": response_text or "",
            "complexity": {
                "time_complexity": self._extract_complexity(response_text, "time"),
                "space_complexity": self._extract_complexity(response_text, "space"),
                "explanation": self._extract_analysis(response_text),
            }
            if "Time Complexity" in response_text or "Space Complexity" in response_text
            else None,
            "code_samples": self._extract_code_samples(response_text),
            "suggestions": self._extract_suggestions(response_text),
        }

    def _extract_complexity(self, text: str, complexity_type: str) -> str:
        pattern = r"Time Complexity: ([^\n]+)" if complexity_type == "time" else r"Space Complexity: ([^\n]+)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else "Not analyzed"

    def _extract_analysis(self, text: str) -> str:
        if "Analysis:" in text:
            parts = text.split("Analysis:")
            if len(parts) > 1:
                return parts[1].strip()
        return ""

    def _extract_code_samples(self, text: str) -> List[Dict[str, str]]:
        code_samples: List[Dict[str, str]] = []
        for language, code in re.findall(r'```(\w+)\n([\s\S]*?)```', text):
            code_samples.append({
                "language": language,
                "code": code.strip(),
                "description": "",
            })
        return code_samples

    def _extract_suggestions(self, text: str) -> List[str]:
        suggestions: List[str] = []
        for line in text.splitlines():
            if any(keyword in line.lower() for keyword in ["try", "practice", "suggest", "explore"]):
                cleaned = line.strip().lstrip("*- ")
                if cleaned:
                    suggestions.append(cleaned)
        return suggestions

    def _update_state(self, state: ChatState) -> ChatState:
        state["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        state["metadata"]["message_count"] = len(state["messages"])
        return state

    def _estimate_difficulty(self, text: str) -> str:
        normalized = text.lower()
        if any(keyword in normalized for keyword in ["hard", "challenging", "advanced"]):
            return "advanced"
        if any(keyword in normalized for keyword in ["easy", "beginner", "simple"]):
            return "beginner"
        return "intermediate"

    def _detect_topic(self, text: str) -> str:
        normalized = text.lower()
        if "graph" in normalized:
            return "graph"
        if "array" in normalized or "matrix" in normalized:
            return "array"
        if "tree" in normalized:
            return "tree"
        if "dynamic programming" in normalized or "dp" in normalized:
            return "dynamic programming"
        return "general"

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        try:
            completion = self.llm_client.chat_client.chat.completions.create(
                model=self.llm_client.config.model_name,
                deployment_id=self.llm_client.config.deployment_name,
                messages=messages,
                temperature=0.2,
                max_tokens=800,
            )

            choice = completion.choices[0]
            if hasattr(choice, "message"):
                content = choice.message.get("content") if isinstance(choice.message, dict) else getattr(choice.message, "content", "")
            else:
                content = getattr(choice, "text", "")

            return content.strip()
        except Exception as exc:
            return f"Error generating response: {exc}"

    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        session = self.chat_store.get_or_create_session(session_id)
        session_id = session["session_id"]
        self.chat_store.append_message(session_id, "user", message)

        updated_session = self.chat_store.get_or_create_session(session_id)
        state: ChatState = {
            "session_id": session_id,
            "messages": updated_session["history"],
            "current_problem": updated_session.get("current_problem"),
            "current_topic": updated_session.get("current_topic"),
            "difficulty_level": updated_session.get("difficulty_level", "intermediate"),
            "problem_history": updated_session.get("problem_history", []),
            "response": None,
            "complexity_analysis": None,
            "code_samples": [],
            "follow_up_suggestions": [],
            "metadata": updated_session.get("metadata", {}),
        }

        result = await self.app.ainvoke(state)
        self.chat_store.append_message(session_id, "assistant", result["response"])

        return {
            "session_id": session_id,
            "response": result["response"],
            "complexity": result.get("complexity_analysis"),
            "code_samples": result.get("code_samples", []),
            "suggestions": result.get("follow_up_suggestions", []),
            "metadata": result.get("metadata", {}),
        }
