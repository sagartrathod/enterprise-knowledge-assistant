# Raw SQL statements for managing the primary metadata of uploaded PDFs

INSERT_DOCUMENT = """
    INSERT INTO documents (pdf_name) 
    VALUES ($1) 
    RETURNING document_id, pdf_name, created_at;
"""

GET_ALL_DOCUMENTS = """
    SELECT document_id, pdf_name, created_at 
    FROM documents 
    ORDER BY created_at DESC;
"""

DELETE_DOCUMENT_BY_ID = """
    DELETE FROM documents 
    WHERE document_id = $1;
"""