import os
from typing import List

from dotenv import load_dotenv
from langchain_community.document_loaders import BSHTMLLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import get_docs_path, get_index_path

load_dotenv()


class DocumentIngestion:
    """Handles document loading, chunking, and FAISS index creation."""

    def __init__(
            self,
            docs_path: str = None,
            index_path: str = None,
            chunk_size: int = 600,
            chunk_overlap: int = 100,
            embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize document ingestion pipeline.

        Args:
            docs_path: Path to HTML documents directory (defaults to config)
            index_path: Path where FAISS index will be saved (defaults to config)
            chunk_size: Token size for text chunks
            chunk_overlap: Token overlap between chunks
            embedding_model: OpenAI embedding model name
        """

        # Use config defaults if not provided
        self.docs_path = str(docs_path) if docs_path else str(get_docs_path())
        self.index_path = str(index_path) if index_path else str(get_index_path())
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model

        # Validate OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")

    def load_documents(self) -> List[Document]:
        """Load HTML documents from the docs directory."""
        print(f"Loading documents from {self.docs_path}...")

        loader = DirectoryLoader(
            self.docs_path,
            glob="*.html",
            loader_cls=BSHTMLLoader,
            loader_kwargs={"open_encoding": "utf-8"},
            recursive=True,
            show_progress=True,
        )
        docs = loader.load()
        print(f"Loaded {len(docs)} documents")
        return docs

    def chunk_documents(self, docs: List[Document]) -> List[Document]:
        """
        Split documents into chunks using tiktoken tokenizer.

        Uses RecursiveCharacterTextSplitter with cl100k_base encoding
        to ensure chunks respect token boundaries.
        """
        print("Chunking documents...")

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_documents(docs)
        print(f"Created {len(chunks)} chunks")
        return chunks

    def create_index(self, chunks: List[Document]) -> FAISS:
        """Create FAISS vector index from document chunks."""
        print("Creating FAISS index...")

        embeddings = OpenAIEmbeddings(model=self.embedding_model)
        vectorstore = FAISS.from_documents(chunks, embeddings)

        print(f"FAISS index created with {len(chunks)} vectors")
        return vectorstore

    def save_index(self, vectorstore: FAISS) -> None:
        """Save FAISS index to disk."""
        vectorstore.save_local(self.index_path)
        print(f"Index saved to {self.index_path}")

    def run_ingestion(self) -> None:
        """Run the complete ingestion pipeline."""
        print("=" * 60)
        print("Starting document ingestion pipeline")
        print("=" * 60)

        docs = self.load_documents()
        chunks = self.chunk_documents(docs)
        vectorstore = self.create_index(chunks)
        self.save_index(vectorstore)

        print("=" * 60)
        print("Ingestion complete!")
        print("=" * 60)


if __name__ == "__main__":
    ingestion = DocumentIngestion()
    ingestion.run_ingestion()
