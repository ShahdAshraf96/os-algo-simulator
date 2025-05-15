def clook_schedule(requests, head):
    """
    Simulate C-LOOK Disk Scheduling Algorithm.

    Parameters:
        requests: List[int] - requested cylinders
        head: int - starting position of the disk head

    Returns:
        seek_order: List[int] - order in which requests are served
        total_seek: int - total head movement
    """
    requests = sorted(requests)
    left = [r for r in requests if r < head]
    right = [r for r in requests if r >= head]

    seek_order = [head]
    total_seek = 0
    current = head

    # Serve right side (higher than head)
    for r in right:
        seek_order.append(r)
        total_seek += abs(current - r)
        current = r

    # Jump to lowest request (leftmost)
    if left:
        total_seek += abs(current - left[0])
        current = left[0]

        for r in left:
            seek_order.append(r)
            total_seek += abs(current - r)
            current = r

    return seek_order, total_seek
