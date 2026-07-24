# Enterprise RAG Engine

An asynchronous Retrieval-Augmented Generation (RAG) platform using FastAPI, raw SQL via `asyncpg`, and PostgreSQL `pgvector`.

## Architecture Overview
* **API / Controllers**: Exposes data input/output hooks via structural Pydantic validation parameters.
* **Services**: Handles chunk fragmentation protocols and vector spatial configurations.
* **Repositories**: Manages data querying layers executing raw SQL operations.
* **LLM Engine**: Dynamic provider routing supporting both Google GenAI and OpenAI clients.

## Quickstart

### 1. Environment Configuration
Create a `.env` file in the root workspace following the reference blueprint:
```bash
cp .env.example .env
# Edit .env and supply your GOOGLE_API_KEY or OPENAI_API_KEY

i want 75 % output as answer from chunk 1 and remaining from chunk 2 and other