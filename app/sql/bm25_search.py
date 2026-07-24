BM25_SEARCH = """
WITH ranked AS (

SELECT

    dc.id AS chunk_id,

    dc.document_id,

    dc.chunk_number,

    dc.page_start,

    dc.page_end,

    dc.line_start,

    dc.line_end,

    dc.chunk_text,

    d.pdf_name,

    ts_rank_cd(
        to_tsvector(
            'english',
            coalesce(dc.chunk_text, '')
        ),
        websearch_to_tsquery(
            'english',
            $1
        )
    ) AS bm25_score

FROM document_chunks dc

JOIN documents d
ON d.document_id = dc.document_id

WHERE
(
    $3::uuid IS NULL
    OR dc.document_id = $3::uuid
)

AND
to_tsvector(
    'english',
    coalesce(dc.chunk_text, '')
)
@@
websearch_to_tsquery(
    'english',
    $1
)

)

SELECT *

FROM ranked

ORDER BY

    bm25_score DESC,

    page_start ASC,

    chunk_number ASC

LIMIT $2;
"""