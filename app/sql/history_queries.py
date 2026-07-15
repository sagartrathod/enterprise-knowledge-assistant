# Handles transactional storage of conversations along with their cited context references

INSERT_HISTORY_LOG = """
INSERT INTO conversation_history
(
    session_id,
    question,
    answer,
    total_chunks_used
)
VALUES
(
    $1,
    $2,
    $3,
    $4
)
RETURNING id;
"""


INSERT_HISTORY_CITATION = """
INSERT INTO conversation_history_citations
(
    history_id,
    document_id,
    pdf_name,
    chunk_number,
    page_number,
    line_start,
    line_end,
    similarity,
    chunk_text
)
VALUES
(
    $1,
    $2,
    $3,
    $4,
    $5,
    $6,
    $7,
    $8,
    $9
);
"""


GET_HISTORY_WITH_CITATIONS = """
SELECT

    ch.id,
    ch.session_id,
    ch.question,
    ch.answer,
    ch.total_chunks_used,
    ch.created_at,

    COALESCE(

        JSONB_AGG(

            JSONB_BUILD_OBJECT(

                'document_id', chc.document_id,
                'pdf_name', chc.pdf_name,
                'chunk_number', chc.chunk_number,
                'page_number', chc.page_number,
                'line_start', chc.line_start,
                'line_end', chc.line_end,
                'similarity', ROUND(COALESCE(chc.similarity,0)::numeric,4),
                'chunk_text', chc.chunk_text

            )

            ORDER BY chc.chunk_number

        )

        FILTER (WHERE chc.id IS NOT NULL),

        '[]'::jsonb

    ) AS citations

FROM conversation_history ch

LEFT JOIN conversation_history_citations chc
ON ch.id = chc.history_id

WHERE ch.session_id = $1

GROUP BY
    ch.id,
    ch.session_id,
    ch.question,
    ch.answer,
    ch.total_chunks_used,
    ch.created_at

ORDER BY
    ch.created_at ASC;
"""