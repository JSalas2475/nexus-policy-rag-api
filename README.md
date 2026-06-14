# Nexus Policy RAG API

A Retrieval-Augmented Generation (RAG) application that answers employee questions about company policies and procedures using a local vector index and Groq LLM.

**Repository:** `nexus-policy-rag-api`

## Features

- Multi-format document ingestion (Markdown, TXT, HTML, PDF)
- Heading-aware chunking with token overlap
- FastEmbed (ONNX) embeddings + Chroma vector store
- Top-k retrieval with cross-encoder re-ranking
- Guardrails: out-of-corpus refusal, length limits, mandatory citations
- Flask web UI with `/`, `/chat`, and `/health` endpoints
- Evaluation suite with groundedness, citation accuracy, and latency metrics
- GitHub Actions CI/CD with optional Render deployment

## Prerequisites

- Python 3.11+
- [Groq API key](https://console.groq.com) (free tier)

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GROQ_API_KEY
```

## Build the Index

```bash
python scripts/ingest.py --seed 42 --rebuild
```

## Run Locally

```bash
flask --app app run --debug
```

Open http://127.0.0.1:5000

Production-style run:

```bash
gunicorn "app:create_app()" --bind 0.0.0.0:8000 --workers 1 --timeout 120
```

## API Endpoints

### GET /health

```json
{
  "status": "ok",
  "index_loaded": true,
  "model": "llama-3.3-70b-versatile",
  "embedding_model": "BAAI/bge-small-en-v1.5"
}
```

### POST /chat

Request:

```json
{"question": "How many PTO days do new employees receive?"}
```

Response:

```json
{
  "answer": "...",
  "citations": [{"doc_id": "...", "title": "...", "section": "...", "snippet": "...", "source_path": "..."}],
  "latency_ms": 1234.5,
  "refused": false
}
```

## Evaluation

```bash
python scripts/evaluate.py
```

Results are written to `evaluation/results.json`.

## Tests

```bash
pytest -q
```

## Deployment (Render)

1. Push this repo to GitHub
2. Create a Web Service on [Render](https://render.com) connected to the repo
3. Set environment variable `GROQ_API_KEY`
4. Render uses `render.yaml` for build/start commands
5. Add deploy hook URL as GitHub secret `RENDER_DEPLOY_HOOK_URL` for CI deploy job

See [deployed.md](deployed.md) for the live URL.

## Demo Video

Follow [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the step-by-step recording script. See [SUBMIT.md](SUBMIT.md) for final Quantic submission steps.

## Project Structure

```
app/           Flask application and RAG pipeline
data/policies/ Policy document corpus
scripts/       Ingestion and evaluation CLIs
evaluation/    Gold questions and results
tests/         Smoke and ingestion tests
.github/       CI/CD workflows
```

## Share with Grader

Add GitHub collaborator: **quantic-grader**

## License

Educational project for Quantic AI Engineering course.
