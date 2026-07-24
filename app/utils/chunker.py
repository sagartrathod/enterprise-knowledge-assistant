from __future__ import annotations

from app.core.constants import (
    CHUNK_MAX_WORDS,
    CHUNK_OVERLAP_WORDS,
    MIN_CHUNK_WORDS,
)


def create_overlapping_chunks(
    parsed_lines: list[dict],
    max_words: int = CHUNK_MAX_WORDS,
    overlap_words: int = CHUNK_OVERLAP_WORDS,
) -> list[dict]:
    """
    Enterprise PDF Chunking

    Features
    --------
    - Cross-page chunking
    - Sliding overlap
    - Preserves metadata
    - Deterministic chunk numbering
    - Optimized for RAG retrieval
    """

    if not parsed_lines:
        return []

    # -----------------------------------------------------
    # Remove empty lines
    # -----------------------------------------------------

    lines = [
        line
        for line in parsed_lines
        if line.get("text", "").strip()
    ]

    if not lines:
        return []

    chunks: list[dict] = []

    chunk_number = 1
    start = 0

    while start < len(lines):

        chunk_lines = []
        total_words = 0

        end = start

        # =================================================
        # Build chunk
        # =================================================

        while end < len(lines):

            current_line = lines[end]

            word_count = len(
                current_line["text"].split()
            )

            if (
                chunk_lines
                and total_words + word_count
                > max_words
            ):
                break

            chunk_lines.append(current_line)

            total_words += word_count

            end += 1

        # =================================================
        # Save chunk
        # =================================================

        if (
            chunk_lines
            and total_words >= MIN_CHUNK_WORDS
        ):

            page_start = chunk_lines[0][
                "page_number"
            ]

            page_end = chunk_lines[-1][
                "page_number"
            ]

            chunks.append(
                {
                    "chunk_number": chunk_number,

                    # page range
                    "page_start": page_start,
                    "page_end": page_end,

                    # line range
                    "line_start": chunk_lines[0][
                        "line_number"
                    ],
                    "line_end": chunk_lines[-1][
                        "line_number"
                    ],

                    "chunk_text": " ".join(
                        line["text"].strip()
                        for line in chunk_lines
                    ),
                }
            )

            chunk_number += 1

        # =================================================
        # End reached
        # =================================================

        if end >= len(lines):
            break

        # =================================================
        # Calculate overlap
        # =================================================

        overlap_count = 0

        new_start = end

        while new_start > start:

            previous_line = lines[
                new_start - 1
            ]

            overlap_count += len(
                previous_line["text"].split()
            )

            new_start -= 1

            if overlap_count >= overlap_words:
                break

        # Safety check
        if new_start <= start:
            new_start = start + 1

        start = new_start

    return chunks