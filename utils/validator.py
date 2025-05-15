def validate_reference_string(ref_str):
    if not ref_str.strip():
        return False, "Reference string is empty."

    try:
        pages = list(map(int, ref_str.strip().split()))
        # ✅ Reject negative page numbers
        if any(p < 0 for p in pages):
            return False, "Page numbers must be non-negative integers."
        return True, pages
    except ValueError:
        return False, "Reference string must contain only integers."

def validate_frame_count(frame_input):
    try:
        frames = int(frame_input)
        if frames <= 0:
            return False, "Number of frames must be greater than 0."
        return True, frames
    except ValueError:
        return False, "Number of frames must be a valid integer."
