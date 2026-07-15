-- Retrieve semantically similar chunks using pgvector.

SEMANTIC_SEARCH = """

SELECT

    dc.id AS chunk_id,

    dc.document_id,

    d.pdf_name,

    dc.chunk_number,

    dc.page_number,

    dc.line_start,

    dc.line_end,

    dc.chunk_text,

    (
        1 - (
            dc.embedding <=> $1::vector
        )
    ) AS semantic_score

FROM document_chunks dc

INNER JOIN documents d
ON d.document_id = dc.document_id

WHERE
(
    $3::uuid IS NULL
    OR dc.document_id = $3::uuid
)

ORDER BY
dc.embedding <=> $1::vector

LIMIT $2;

"""