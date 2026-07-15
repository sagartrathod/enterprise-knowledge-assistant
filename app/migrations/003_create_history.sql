-- 1. Main Conversation History Table (Stores the unique Q&A interactions)
CREATE TABLE IF NOT EXISTS conversation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    total_chunks_used INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. History Citations Table (Stores the exact chunks referenced for that specific answer)
CREATE TABLE IF NOT EXISTS conversation_history_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    history_id UUID NOT NULL,
    document_id UUID NOT NULL,
    chunk_number INT NOT NULL,
    page_number INT NOT NULL,
    line_start INT NOT NULL,
    line_end INT NOT NULL,
    chunk_text TEXT NOT NULL,
    
    -- Ensure everything cascades cleanly on deletes
    CONSTRAINT fk_citation_history 
        FOREIGN KEY (history_id) 
        REFERENCES conversation_history(id) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_citation_document 
        FOREIGN KEY (document_id) 
        REFERENCES documents(document_id) 
        ON DELETE CASCADE
);

-- Crucial Performance Indexes
CREATE INDEX IF NOT EXISTS idx_history_session_id ON conversation_history(session_id);
CREATE INDEX IF NOT EXISTS idx_citations_history_id ON conversation_history_citations(history_id);