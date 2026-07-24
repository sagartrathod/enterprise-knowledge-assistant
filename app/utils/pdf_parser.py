import re
import unicodedata

import fitz  # PyMuPDF


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """

    if not text:
        return ""

    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Remove NULL bytes
    text = text.replace("\x00", "")

    # Remove control characters
    text = re.sub(
        r"[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]",
        "",
        text,
    )

    # Collapse whitespace
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def parse_pdf_layout(file_path: str) -> list[dict]:
    """
    Extract text and tables from a PDF.

    Output Example:

    [
        {
            "page_number": 1,
            "line_number": 1,
            "type": "text",
            "text": "Introduction..."
        },
        {
            "page_number": 1,
            "line_number": 2,
            "type": "table",
            "text": "Name | Age | City"
        }
    ]
    """

    parsed_lines = []

    try:

        doc = fitz.open(file_path)

        for page_idx, page in enumerate(doc):

            page_number = page_idx + 1
            line_counter = 1

            # =====================================================
            # NORMAL TEXT
            # =====================================================

            text_page = page.get_text(
                "dict",
                sort=True,
            )

            for block in text_page.get("blocks", []):

                # Ignore image blocks
                if block.get("type") != 0:
                    continue

                for line in block.get("lines", []):

                    raw_text = "".join(
                        span.get("text", "")
                        for span in line.get("spans", [])
                    )

                    cleaned = clean_text(raw_text)

                    if not cleaned:
                        continue

                    parsed_lines.append(
                        {
                            "page_number": page_number,
                            "line_number": line_counter,
                            "type": "text",
                            "text": cleaned,
                        }
                    )

                    line_counter += 1

            # =====================================================
            # TABLES
            # =====================================================

            try:

                tables = page.find_tables()

                for table in tables.tables:

                    rows = table.extract()

                    for row in rows:

                        if not row:
                            continue

                        cells = []

                        for cell in row:

                            if cell is None:
                                cells.append("")
                            else:
                                cells.append(
                                    clean_text(str(cell))
                                )

                        row_text = " | ".join(cells).strip()

                        if not row_text.replace("|", "").strip():
                            continue

                        parsed_lines.append(
                            {
                                "page_number": page_number,
                                "line_number": line_counter,
                                "type": "table",
                                "text": row_text,
                            }
                        )

                        line_counter += 1

            except Exception:
                # Continue even if table detection fails
                pass

        doc.close()

        return parsed_lines

    except Exception as exc:

        raise Exception(
            f"PDF parsing failed: {exc}"
        ) from exc