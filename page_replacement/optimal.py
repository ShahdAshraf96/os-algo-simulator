def optimal_page_replacement(pages, frames_count):
    memory = []             # Current pages in memory
    page_faults = 0         # Count of page faults
    hits = 0                # Total number of page hits
    simulation_steps = []  # Store history of frames at each step for visualization


    for i in range(len(pages)):
        page = pages[i]
        frame_snapshot = memory.copy()

        # ✅ If page is already in memory → no page fault (HIT)
        if page in memory:
            hits += 1
            print(f"[No Fault] Page {page} already in memory: {memory}")
            simulation_steps.append({
                "frame": memory.copy(),
                "page": page,
                "fault": False
            })
            continue

        # ✅ If there's still space → just add the page
        if len(memory) < frames_count:
            memory.append(page)
            page_faults += 1
            print(f"[Fault] Page {page} added → {memory}")
        else:
            # 🔁 Replace page using Optimal strategy
            future = pages[i+1:]  # Remaining pages
            index_to_replace = -1
            farthest_use = -1

            for mem_index in range(len(memory)):
                mem_page = memory[mem_index]
                if mem_page not in future:
                    index_to_replace = mem_index
                    break
                else:
                    next_use = future.index(mem_page)
                    if next_use > farthest_use:
                        farthest_use = next_use
                        index_to_replace = mem_index

            replaced = memory[index_to_replace]
            memory[index_to_replace] = page
            page_faults += 1
            print(f"[Replace] {replaced} → {page} → {memory}")
        
        # ✅ Add step to simulation log
        simulation_steps.append({
            "frame": memory.copy(),
            "page": page,
            "fault": True
        })
    print("\n✅ Total page faults:", page_faults)
    print(f"✅ Total hits: {hits}")
    
    return {
        "steps": simulation_steps,
        "page_faults": page_faults,
        "hits": hits
    }

# # 🔧 Example usage
# if __name__ == "__main__":
#     # You can change this input later
#     reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
#     frame_count = 3

#     optimal_page_replacement(reference_string, frame_count)

if __name__ == "__main__":
    # Get input from the user
    ref_str = input("Enter reference string (space-separated): ").strip()
    reference_string = list(map(int, ref_str.split()))
    frame_count = int(input("Enter number of frames: "))

    optimal_page_replacement(reference_string, frame_count)
