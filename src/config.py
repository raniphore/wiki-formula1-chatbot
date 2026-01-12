import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Path configurations
DOCS_PATH = PROJECT_ROOT / os.getenv("DOCS_PATH", "docs")
INDEX_PATH = PROJECT_ROOT / os.getenv("INDEX_PATH", "faiss_index")


def get_project_root() -> Path:
    """Get the project root directory."""
    return PROJECT_ROOT


def get_docs_path() -> Path:
    """Get the documents directory path."""
    return DOCS_PATH


def get_index_path() -> Path:
    """Get the FAISS index directory path."""
    return INDEX_PATH
