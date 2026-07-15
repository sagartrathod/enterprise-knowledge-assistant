def create_overlapping_chunks(
    parsed_lines: list[dict], 
    max_words: int = 200, 
    overlap_words: int = 30
) -> list[dict]:
    """
    Groups raw lines into larger semantic chunks, ensuring overlap constraints
    and mapping structural trackers back onto the document timeline[cite: 1].
    """
    chunks = []
    chunk_sequence = 1
    
    i = 0
    while i < len(parsed_lines):
        current_chunk_words = []
        chunk_lines_included = []
        
        # Build window until word size limit boundary is crossed
        j = i
        while j < len(parsed_lines) and len(current_chunk_words) < max_words:
            line_data = parsed_lines[j]
            line_words = line_data["text"].split()
            
            current_chunk_words.extend(line_words)
            chunk_lines_included.append(line_data)
            j += 1
            
        if not chunk_lines_included:
            break
            
        # Extract positional coordinates from tracking metrics
        page_number = chunk_lines_included[0]["page_number"]
        line_start = chunk_lines_included[0]["line_number"]
        line_end = chunk_lines_included[-1]["line_number"]
        combined_text = " ".join([l["text"] for l in chunk_lines_included])
        
        chunks.append({
            "chunk_number": chunk_sequence,
            "page_number": page_number,
            "line_start": line_start,
            "line_end": line_end,
            "chunk_text": combined_text
        })
        
        chunk_sequence += 1
        
        # Calculate overlap step index
        if j >= len(parsed_lines):
            break
            
        # Rewind loop sequence to preserve sliding window overlaps[cite: 1]
        accumulated_overlap = 0
        rewind_steps = 0
        for rev_line in reversed(chunk_lines_included):
            accumulated_overlap += len(rev_line["text"].split())
            if accumulated_overlap >= overlap_words:
                break
            rewind_steps += 1
            
        # Determine movement stride offset
        stride = len(chunk_lines_included) - rewind_steps
        if stride <= 0:
            stride = 1
        i += stride
        
    return chunks