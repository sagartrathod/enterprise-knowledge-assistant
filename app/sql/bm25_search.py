BM25_SEARCH = """
SELECT

    dc.id AS chunk_id,
    dc.document_id,
    dc.chunk_number,
    dc.page_number,
    dc.line_start,
    dc.line_end,
    dc.chunk_text,
    d.pdf_name,

    ts_rank_cd(
        to_tsvector('english', dc.chunk_text),
        plainto_tsquery('english', $1)
    ) AS bm25_score

FROM document_chunks dc

JOIN documents d
ON d.document_id = dc.document_id

WHERE

to_tsvector(
    'english',
    dc.chunk_text
)

@@

plainto_tsquery(
    'english',
    $1
)

AND
(
    $3::uuid IS NULL
    OR dc.document_id = $3::uuid
)

ORDER BY
bm25_score DESC

LIMIT $2;
"""