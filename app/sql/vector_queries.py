UPDATE_CHUNK_EMBEDDING = """
UPDATE document_chunks
SET embedding = $1::vector
WHERE id = $2;
"""


SEMANTIC_TOP_K_RETRIEVAL = """
SELECT

    dc.id AS chunk_id,

    dc.document_id,

    dc.chunk_number,

    dc.page_number,

    dc.line_start,

    dc.line_end,

    dc.chunk_text,

    d.pdf_name,

    dc.embedding <=> $1::vector AS distance,

    (
        1 - (dc.embedding <=> $1::vector)
    ) AS similarity

FROM document_chunks dc

INNER JOIN documents d
ON d.document_id = dc.document_id

WHERE
(
    $3::uuid IS NULL
    OR dc.document_id = $3::uuid
)

ORDER BY
distance ASC

LIMIT $2;
"""