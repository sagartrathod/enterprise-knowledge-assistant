-- Migration: Create Documents Table
CREATE TABLE IF NOT EXISTS documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for speedy file-lookup by filename
CREATE INDEX IF NOT EXISTS idx_documents_pdf_name ON documents(pdf_name);