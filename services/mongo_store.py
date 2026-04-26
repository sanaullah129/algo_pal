from datetime import datetime
from typing import Any, Dict, List, Optional
import os

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoChatStore:
    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGODB_DB", "algo_pal")
        self.collection_name = collection_name or os.getenv("MONGODB_COLLECTION", "chat_sessions")
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.collection.create_index("session_id", unique=True)

    def _generate_session_id(self) -> str:
        return f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

    def get_or_create_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        if session_id:
            session = self.collection.find_one({"session_id": session_id})
        else:
            session = None

        if not session:
            session_id = session_id or self._generate_session_id()
            session = {
                "session_id": session_id,
                "history": [],
                "current_problem": None,
                "current_topic": None,
                "difficulty_level": "beginner",
                "problem_history": [],
                "metadata": {},
                "graph_state": {},
                "created_at": datetime.utcnow(),
                "last_accessed": datetime.utcnow(),
            }
            try:
                self.collection.insert_one(session)
            except DuplicateKeyError:
                session = self.collection.find_one({"session_id": session_id})

        session.pop("_id", None)
        return session

    def append_message(self, session_id: str, role: str, content: str) -> None:
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
        }
        self.collection.update_one(
            {"session_id": session_id},
            {
                "$push": {"history": message},
                "$set": {"last_accessed": datetime.utcnow()},
            },
            upsert=True,
        )

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        session = self.collection.find_one({"session_id": session_id})
        if not session:
            return []
        return session.get("history", [])

    def update_graph_state(self, session_id: str, graph_state: Dict[str, Any]) -> None:
        self.collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "graph_state": graph_state,
                    "last_accessed": datetime.utcnow(),
                }
            },
            upsert=True,
        )

    def get_graph_state(self, session_id: str) -> Dict[str, Any]:
        session = self.collection.find_one({"session_id": session_id})
        if not session:
            return {}
        return session.get("graph_state", {})
