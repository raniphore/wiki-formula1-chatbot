"""Standalone script to run document ingestion."""

import sys

from src.ingestion.ingest import DocumentIngestion

if __name__ == "__main__":
    print("=" * 60)
    print("F1 RAG Chatbot - Document Ingestion")
    print("=" * 60)

    try:
        # Run ingestion (config is loaded automatically)
        ingestion = DocumentIngestion()
        ingestion.run_ingestion()
    except Exception as e:
        print(f"Ingestion failed: {e}")
        sys.exit(1)
