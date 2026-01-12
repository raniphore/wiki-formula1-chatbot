import os
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.config import get_index_path


class DocumentRetriever:
    """Handles retrieval of relevant document chunks using FAISS."""

    # Singleton pattern to avoid reloading index
    _instance: Optional['DocumentRetriever'] = None
    _vectorstore: Optional[FAISS] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
            index_path: str = None,
            embedding_model: str = "text-embedding-3-small",
            k: int = 5
    ):
        """
        Initialize document retriever.

        Args:
            index_path: Path to FAISS index
            embedding_model: OpenAI embedding model (must match ingestion)
            k: Number of documents to retrieve
        """
        # Only initialize once
        if self._vectorstore is not None:
            return

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # from src.config import get_index_path

        self.index_path = str(index_path) if index_path else str(get_index_path())
        self.embedding_model = embedding_model
        self.k = k

        # Load the vectorstore
        self._load_vectorstore()

    def _load_vectorstore(self) -> None:
        """Load FAISS index from disk."""
        print(f"Loading FAISS index from {self.index_path}...")

        embeddings = OpenAIEmbeddings(model=self.embedding_model)
        self._vectorstore = FAISS.load_local(
            self.index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        print("FAISS index loaded successfully")

    def retrieve(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Retrieve most relevant documents for a query.

        Args:
            query: User's question
            k: Number of documents to retrieve (overrides default)

        Returns:
            List of relevant Document objects
        """
        if self._vectorstore is None:
            raise RuntimeError("Vectorstore not initialized")

        k = k or self.k
        return self._vectorstore.similarity_search(query, k=k)


if __name__ == "__main__":
    retriever = DocumentRetriever()
    query = "Who built the nuerburgring"
    results = retriever.retrieve(query)
    print(results)
