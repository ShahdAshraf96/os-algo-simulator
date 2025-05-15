def second_chance_page_replacement(pages, frame_count):
    # Initialize frames as an empty list of tuples: (page_number, reference_bit)
    frames = []
    pointer = 0            # This will rotate through frames like a circular queue
    page_faults = 0
    hits = 0
    simulation_steps = []

    # Create fixed-size frame slots
    for _ in range(frame_count):
        frames.append([-1, 0])  # [-1 means empty], reference bit = 0

    for page in pages:
        print(f"\n🔍 Requesting page: {page}")

        # Check if page is already in memory
        in_memory = False
        for frame in frames:
            if frame[0] == page:
                frame[1] = 1  # Set reference bit to 1
                in_memory = True
                hits += 1
                print(f"✅ Page {page} found → set R=1 → Frames: {frames}")
                break

        if not in_memory:
            # Need to replace a page
            while True:
                current_page, ref_bit = frames[pointer]

                if ref_bit == 0:
                    # Found the page to replace
                    print(f"🔁 Replacing page {current_page} with {page} at position {pointer}")
                    frames[pointer] = [page, 1]  # Insert new page with R=1
                    pointer = (pointer + 1) % frame_count
                    page_faults += 1
                    break
                else:
                    # Give second chance: reset R and move on
                    print(f"🔄 Giving second chance to page {current_page} at position {pointer}")
                    frames[pointer][1] = 0
                    pointer = (pointer + 1) % frame_count
        
        # 🧠 Save a snapshot of frame states and ref bits
        snapshot = {
            "frame": [slot[0] for slot in frames],
            "ref_bits": [slot[1] for slot in frames],
            "page": page,
            "fault": not in_memory
        }
        simulation_steps.append(snapshot)
        
        # Debug: show current frame state
        print(f"📦 Frame state: {frames}")

    print(f"\n✅ Total page faults: {page_faults}")
    print(f"✅ Total hits: {hits}")
    
    return {
        "steps": simulation_steps,
        "page_faults": page_faults,
        "hits": hits
    }


# # 🧪 Example usage
# if __name__ == "__main__":
#     reference_string = [1, 2, 3, 2, 4, 1, 5, 2]
#     frame_count = 3
#     second_chance_page_replacement(reference_string, frame_count)

if __name__ == "__main__":
    ref_str = input("Enter reference string (space-separated): ").strip()
    reference_string = list(map(int, ref_str.split()))
    frame_count = int(input("Enter number of frames: "))

    second_chance_page_replacement(reference_string, frame_count)
