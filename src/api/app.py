import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from src.generation.generator import AnswerGenerator
from src.retrieval.retriever import DocumentRetriever

app = Flask(__name__)

# Load environment variables first
load_dotenv()

# Initialize components (singleton pattern ensures single load)
retriever = None
generator = None


def initialize_components():
    """Lazy initialization of retriever and generator."""
    global retriever, generator

    if retriever is None:
        print("Initializing DocumentRetriever...")
        retriever = DocumentRetriever()
        print("DocumentRetriever initialized")

    if generator is None:
        print("Initializing AnswerGenerator...")
        generator = AnswerGenerator()
        print("AnswerGenerator initialized")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "f1-rag-chatbot"
    }), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.

    Expected JSON body:
    {
        "query": "Who won the 2023 F1 championship?",
        "k": 5  // optional, number of docs to retrieve
    }

    Returns:
    {
        "query": "...",
        "answer": "...",
        "num_sources": 5
    }
    """
    try:
        # Initialize components if needed
        initialize_components()

        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        query = data.get("query")

        if not query or not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400

        # Optional: custom k value
        k = data.get("k", 5)

        # Retrieve relevant documents
        docs = retriever.retrieve(query, k=k)

        # Generate answer
        answer = generator.generate(query, docs)

        return jsonify({
            "query": query,
            "answer": answer,
            "num_sources": len(docs)
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Validate API key is set
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not set")

    print(f"Starting F1 RAG Chatbot API...")
    print(f"API Key configured")
    app.run(host="0.0.0.0", port=5001, debug=False)
