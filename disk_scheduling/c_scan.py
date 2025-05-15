# disk_scheduling/cscan.py

def cscan_schedule(requests, head, disk_size):
    """
    Simulate C-SCAN Disk Scheduling.
    - requests: list of integers (requested cylinders)
    - head: current head position (int)
    - disk_size: total cylinders (int)
    -Includes end (disk_size - 1) and jump to 0

    Returns:
        - seek_order: list of cylinders in service order
        - total_seek: total distance moved by the head
    """
    requests = sorted(requests)
    left = [r for r in requests if r < head]
    right = [r for r in requests if r >= head]

    seek_order = [head]
    total_seek = 0
    current = head

    # Move toward the end
    for r in right:
        seek_order.append(r)
        total_seek += abs(current - r)
        current = r

    # Jump to start (C-SCAN behavior)
    
    if left:
        # Move to end of disk (visual)
        if current != disk_size - 1:
            seek_order.append(disk_size - 1)
            total_seek += abs(current - (disk_size - 1))
            current = disk_size - 1

        # Jump to 0 (wrap around)
        seek_order.append(0)
        total_seek += current  # jump from end to start
        current = 0

    # Move to left requests
    for r in left:
        seek_order.append(r)
        total_seek += abs(current - r)
        current = r

    return seek_order, total_seek
