import logging
import os
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

logger = logging.getLogger(__name__)


class LangchainQdrantService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.openai_api_key = self.config.get("AZURE_OPENAI_API_KEY", os.getenv("AZURE_OPENAI_API_KEY"))
        self.openai_api_base = self.config.get("AZURE_OPENAI_ENDPOINT", os.getenv("AZURE_OPENAI_ENDPOINT"))
        self.openai_api_version = self.config.get("AZURE_OPENAI_API_VERSION", os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"))
        self.embedding_deployment = self.config.get(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        )
        # Use the embedding deployment name as the model name — avoids wrong tokenizer from chat model
        self.embedding_model = self.embedding_deployment or "text-embedding-3-large"
        self.collection_name = self.config.get("QDRANT_COLLECTION", os.getenv("QDRANT_COLLECTION", "algo_pal_graph"))
        self.qdrant_url = self.config.get("QDRANT_URL", os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.qdrant_api_key = self.config.get("QDRANT_API_KEY", os.getenv("QDRANT_API_KEY"))
        self._qdrant_client: Optional[QdrantClient] = None

        self.embeddings = self._build_embeddings()
        self.vector_store = self._initialize_vector_store()

    def _build_embeddings(self) -> AzureOpenAIEmbeddings:
        return AzureOpenAIEmbeddings(
            model=self.embedding_model,
            api_key=self.openai_api_key,
            azure_endpoint=self.openai_api_base,
            api_version=self.openai_api_version,
            azure_deployment=self.embedding_deployment,
        )

    def _initialize_vector_store(self) -> Optional[Qdrant]:
        try:
            self._qdrant_client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key, prefer_grpc=False)
            existing = {c.name for c in self._qdrant_client.get_collections().collections}
            if self.collection_name in existing:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    return Qdrant(
                        client=self._qdrant_client,
                        collection_name=self.collection_name,
                        embeddings=self.embeddings,
                    )
            # Collection will be created on first document insertion
            return None
        except Exception as exc:
            logger.warning("Qdrant init failed (vector search disabled): %s", exc)
            return None

    def add_message_embedding(self, session_id: str, role: str, content: str) -> None:
        if not content or not content.strip():
            return

        document = Document(
            page_content=content.strip(),
            metadata={"session_id": session_id, "role": role, "created_at": datetime.utcnow().isoformat()},
        )
        try:
            if self.vector_store is None:
                # Create the collection directly via the client API (avoids langchain's
                # Qdrant.from_documents which passes unsupported 'init_from' to newer clients)
                if self._qdrant_client is None:
                    self._qdrant_client = QdrantClient(
                        url=self.qdrant_url, api_key=self.qdrant_api_key, prefer_grpc=False
                    )
                existing = {c.name for c in self._qdrant_client.get_collections().collections}
                if self.collection_name not in existing:
                    sample = self.embeddings.embed_query("ping")
                    self._qdrant_client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=len(sample), distance=Distance.COSINE),
                    )
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.vector_store = Qdrant(
                        client=self._qdrant_client,
                        collection_name=self.collection_name,
                        embeddings=self.embeddings,
                    )
            self.vector_store.add_documents([document])
        except Exception as exc:
            logger.warning("Failed to add embedding: %s", exc)

    def semantic_search(self, query: str, top_k: int = 3) -> List[Document]:
        if not query or not query.strip() or self.vector_store is None:
            return []
        try:
            return self.vector_store.similarity_search(query, k=top_k)
        except Exception as exc:
            logger.warning("Semantic search failed: %s", exc)
            return []
