from datetime import datetime, timezone

def generate_utc_timestamp() -> datetime:
    """
    Generates standard UTC timestamp objects for uniform database records.
    """
    return datetime.now(timezone.utc)

def sanitize_text_block(raw_text: str) -> str:
    """
    Strips dirty linebreaks, multi-spaces, and control signals out of chunks.
    """
    if not raw_text:
        return ""
    return " ".join(raw_text.strip().split())