UPDATE_CHUNK_EMBEDDING = """
UPDATE document_chunks
SET embedding = $1::vector
WHERE id = $2;
"""


SEMANTIC_TOP_K_RETRIEVAL = """
SELECT

    dc.id AS chunk_id,

    dc.document_id,

    d.pdf_name,

    dc.chunk_number,

    dc.page_start,

    dc.page_end,

    dc.line_start,

    dc.line_end,

    dc.chunk_text,

    dc.embedding <=> $1::vector AS distance,

    ROUND(
        (
            1.0 - (dc.embedding <=> $1::vector)
        )::numeric,
        6
    ) AS similarity,

    ts_rank_cd(
        to_tsvector(
            'english',
            dc.chunk_text
        ),
        plainto_tsquery(
            'english',
            COALESCE($4, '')
        )
    ) AS keyword_score

FROM document_chunks dc

INNER JOIN documents d
ON d.document_id = dc.document_id

WHERE
(
    $3::uuid IS NULL
    OR dc.document_id = $3::uuid
)

ORDER BY

    similarity DESC,

    page_start ASC,

    chunk_number ASC

LIMIT $2;
"""