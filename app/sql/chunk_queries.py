INSERT_CHUNK_METADATA = """

INSERT INTO document_chunks
(
    document_id,
    chunk_number,
    page_number,
    line_start,
    line_end,
    chunk_text,
    embedding
)

VALUES
(
    $1,
    $2,
    $3,
    $4,
    $5,
    $6,
    $7::vector
)

RETURNING id;

"""



GET_CHUNKS_BY_DOCUMENT = """

SELECT
    id,
    document_id,
    chunk_number,
    page_number,
    line_start,
    line_end,
    chunk_text,
    embedding

FROM document_chunks

WHERE document_id = $1

ORDER BY chunk_number ASC;

"""