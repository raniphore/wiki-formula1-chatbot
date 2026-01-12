## Running with Docker

### Prerequisites
- Docker and Docker Compose installed
- FAISS index built (see Setup section)

### Quick Start
```bash
# 1. Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 2. Build FAISS index (one-time)
python run_ingestion.py

# 3. Start with Docker
docker-compose up --build

# 4. Test the API
curl http://localhost:5000/api/health
```

The API will be available at `http://localhost:5000`