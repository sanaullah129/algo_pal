import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient


class LangchainQdrantService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.openai_api_key = self.config.get("AZURE_OPENAI_API_KEY", os.getenv("AZURE_OPENAI_API_KEY"))
        self.openai_api_base = self.config.get("AZURE_OPENAI_ENDPOINT", os.getenv("AZURE_OPENAI_ENDPOINT"))
        self.openai_api_version = self.config.get("AZURE_OPENAI_API_VERSION", os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"))
        self.embedding_deployment = self.config.get(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        )
        self.embedding_model = self.config.get("AZURE_OPENAI_MODEL", "text-embedding-3-large")
        self.collection_name = self.config.get("QDRANT_COLLECTION", os.getenv("QDRANT_COLLECTION", "algo_pal_graph"))
        self.qdrant_url = self.config.get("QDRANT_URL", os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.qdrant_api_key = self.config.get("QDRANT_API_KEY", os.getenv("QDRANT_API_KEY"))

        self.embeddings = self._build_embeddings()
        self.vector_store = self._initialize_vector_store()

    def _build_embeddings(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=self.openai_api_key,
            openai_api_base=self.openai_api_base,
            openai_api_type="azure",
            openai_api_version=self.openai_api_version,
            deployment=self.embedding_deployment,
        )

    def _initialize_vector_store(self) -> Qdrant:
        qdrant_client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key, prefer_grpc=False)
        try:
            return Qdrant(
                client=qdrant_client,
                collection_name=self.collection_name,
                embeddings=self.embeddings,
            )
        except ValueError:
            return Qdrant.from_documents(
                [],
                self.embeddings,
                collection_name=self.collection_name,
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                prefer_grpc=False,
            )

    def add_message_embedding(self, session_id: str, role: str, content: str) -> None:
        if not content or not content.strip():
            return

        document = Document(
            page_content=content.strip(),
            metadata={"session_id": session_id, "role": role, "created_at": datetime.utcnow().isoformat()},
        )
        self.vector_store.add_documents([document])

    def semantic_search(self, query: str, top_k: int = 3) -> List[Document]:
        if not query or not query.strip():
            return []
        return self.vector_store.similarity_search(query, k=top_k)
