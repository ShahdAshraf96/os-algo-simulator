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

# ✅ New validation for disk scheduling
def validate_integer(value, field_name):
    try:
        num = int(value)
        if num < 0:
            return False, f"❌ {field_name} must be a non-negative integer."
        return True, num
    except ValueError:
        return False, f"❌ {field_name} must be a valid integer."


def validate_request_queue(queue_str, disk_max):
    if not queue_str.strip():
        return False, "❌ Request queue is empty."

    try:
        requests = list(map(int, queue_str.strip().split()))
    except ValueError:
        return False, "❌ Request queue must contain only integers."

    if any(r < 0 or r >= disk_max for r in requests):
        return False, f"❌ Requests must be in range 0 to {disk_max - 1}."

    return True, requests