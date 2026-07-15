-- Migration: Create Chunks Table
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    chunk_number INT NOT NULL,
    page_number INT NOT NULL,
    line_start INT NOT NULL,
    line_end INT NOT NULL,
    chunk_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Cascades deletion automatically if the parent document is wiped
    CONSTRAINT fk_chunks_document_id 
        FOREIGN KEY (document_id) 
        REFERENCES documents(document_id) 
        ON DELETE CASCADE
);

-- Index for quick lookups by a given document
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);