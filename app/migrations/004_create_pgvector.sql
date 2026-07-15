-- Migration: Enable pgvector and Add Vector Columns
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding vector column to your existing chunks table
-- Set to 768 dimensions for Gemini Embeddings. Swap to 1536 if using OpenAI.
ALTER TABLE document_chunks 
ADD COLUMN IF NOT EXISTS embedding vector(768) NOT NULL;

-- Create an HNSW index using Cosine Distance operator for ultra-fast RAG operations
CREATE INDEX IF NOT EXISTS chunk_hnsw_vector_idx 
ON document_chunks USING hnsw (embedding vector_cosine_ops);