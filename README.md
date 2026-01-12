# F1 Wikipedia RAG Chatbot

A production-oriented **Retrieval-Augmented Generation (RAG)** system that answers questions grounded in a curated collection of **Wikipedia Formula-1 documents**.

---

## 1. Problem Statement

Build a conversational AI assistant that can answer questions based on a document collection using a RAG approach, demonstrating:

* Grounded and source-backed answers
* Thoughtful design trade-offs
* Clean, maintainable code
* Production-friendly practices

---

## 2. Dataset

### Source

* Wikipedia Formula-1 pages (raw HTML files)

### Format

* Raw HTML files stored under `docs/`
* Parsed using an HTML-aware loader
* Metadata preserved (filename, source type)

---

## 3. Architecture Overview

```
docs/ (HTML files)
   ↓
HTML Loader (BSHTMLLoader)
   ↓
Token-aware Chunking
   ↓
OpenAI Embeddings
   ↓
FAISS Vector Index
   ↓
Retriever (Top-K similarity)
   ↓
Context Assembly with Sources
   ↓
LLM (Grounded Prompt)
   ↓
Flask API
```

---

## 4. RAG Design Decisions

### 4.1 Chunking Strategy

* **Approach**: Recursive, token-aware chunking
* **Chunk size**: ~600 tokens
* **Overlap**: 100 tokens

**Rationale**

* Preserves semantic coherence
* Prevents LLM context overflow
* Overlap reduces information loss at chunk boundaries

Token-based chunking ensures predictable behavior across LLMs.

---

### 4.2 Embedding Model

* **Model**: `text-embedding-3-small` (OpenAI)

**Why**

* Strong semantic performance
* Cost-effective and low latency
* Stable dimensionality

The same embedding model is used for both ingestion and retrieval to ensure deterministic similarity search.

---

### 4.3 Vector Store

* **Engine**: FAISS (Flat index)

**Why FAISS**

* Fast, local, deterministic
* No external infrastructure required
* Exact nearest-neighbor search

Approximate indexes were intentionally avoided due to the moderate dataset size.

---

### 4.4 Retrieval Strategy

* **Similarity metric**: Cosine similarity
* **Top-K**: 5
* **Re-ranking**: Not used

**Rationale**

* Top-K balances recall and prompt size
* Exact retrieval improves explainability
* Avoids unnecessary complexity

---

### 4.5 Prompt Engineering

A strict grounding contract is enforced:

* Answer **only** from retrieved context
* Explicit fallback when information is missing
* Mandatory `Sources` section in every response

This significantly reduces hallucinations and improves traceability.

---

### 4.6 Context Management

* Retrieved chunks are assembled with explicit identifiers:

  ```
  Sources:
   - doc1.html
   - doc2.html
  ```
* Context is bounded by top-K retrieval
* Least relevant chunks are implicitly excluded

---

### 4.7 Guardrails

Implemented safeguards include:

* Empty retrieval leads to deterministic fallback response
* Mandatory source citations
* `temperature=0` for factual consistency

---

## 5. API Interface

### Health Check

```
GET /api/health
```

Response:

```json
{
    "service": "f1-rag-chatbot",
    "status": "healthy"
}
```

---

### Chat Endpoint

```
POST /api/chat
```

Request:

```json
{
    "query": "Who built the Nurburgring?",
    "k": 3
}
```

Response:

```json
{
    "answer": "The Nürburgring was built following a proposal in the early 1920s, with construction beginning in September 1925. The track was designed by the Eichler Architekturbüro from Ravensburg, led by architect Gustav Eichler. It was completed in spring 1927.\n\nSources:\n- Nürburgring.html",
    "num_sources": 3,
    "query": "Who built the Nurburgring?"
}
```

---

## 6. Testing Philosophy

Tests focus on **determinism and contract enforcement**, not natural language quality.

### What is tested

* FAISS retrieval determinism
* Top-K correctness
* Prompt contract and source enforcement
* API request/response structure

### What is intentionally not tested

* LLM factual correctness
* Linguistic phrasing
* Latency benchmarks

LLM calls are mocked to keep tests fast, reliable, and reproducible.

---

## 7. Running the Project

### Prerequisites

* Docker
* Docker Compose
* OpenAI API key

---

### Setup Environment

```bash
cp .env.example .env
# Add your OPENAI_API_KEY
```

---

### Build FAISS Index (One-time)

```bash
# Build FAISS index if not present already in faiss_index directory
python run_ingestion.py
```

---

### Run with Docker

```bash
docker-compose up --build
```

---

### Verify API

```bash
curl http://localhost:5001/api/health

```

---

## 8. Containerization

* Single Dockerfile
* Docker Compose for orchestration
* FAISS index persisted locally
* No document ingestion at runtime

This ensures fast startup and deterministic behavior.

---

## 9. Key Trade-offs & Limitations

* No hybrid (keyword + vector) retrieval
* No re-ranking model
* No distributed vector database
* API-only interface (no UI)

These choices were intentional to keep the system **clear, explainable, and robust**.

---

## 10. Use of AI-Assisted Development

AI tools were used for:

* Prompt iteration and refinement
* Code review and refactoring suggestions
* Test strategy validation

All generated code was manually reviewed and adapted to fit the project’s design goals.

---

## 11. What I’d Improve With More Time

* Hybrid retrieval (BM25 + embeddings)
* Lightweight re-ranking
* Query clarification loop
* Evaluation harness with curated Q&A
* CI pipeline for automated testing
