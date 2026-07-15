import fitz  # PyMuPDF
import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Cleans extracted PDF text before storing in PostgreSQL.
    Removes invalid UTF-8/control characters.
    """

    if not text:
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Remove NULL bytes
    text = text.replace("\x00", "")

    # Remove other control characters except newline/tab
    text = re.sub(
        r"[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]",
        "",
        text
    )

    # Replace multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()



def parse_pdf_layout(file_path: str) -> list[dict]:
    """
    Extracts PDF text with page and line metadata.

    Output:
    [
        {
            "page_number": 1,
            "line_number": 1,
            "text": "clean text"
        }
    ]
    """

    parsed_lines = []

    try:
        doc = fitz.open(file_path)

        for page_idx, page in enumerate(doc):

            page_number = page_idx + 1

            text_page = page.get_text(
                "dict",
                sort=True
            )

            line_counter = 1


            for block in text_page.get("blocks", []):

                # Ignore images
                if block.get("type") != 0:
                    continue


                for line in block.get("lines", []):

                    spans = line.get(
                        "spans",
                        []
                    )


                    raw_text = "".join(
                        span.get("text", "")
                        for span in spans
                    )


                    cleaned = clean_text(
                        raw_text
                    )


                    if not cleaned:
                        continue


                    parsed_lines.append(
                        {
                            "page_number": page_number,
                            "line_number": line_counter,
                            "text": cleaned
                        }
                    )


                    line_counter += 1


        doc.close()

        return parsed_lines


    except Exception as e:

        raise Exception(
            f"PDF parsing failed: {str(e)}"
        )