import customtkinter as ctk
from page_replacement.optimal import optimal_page_replacement
from page_replacement.second_chance import second_chance_page_replacement
from utils.validator import validate_reference_string, validate_frame_count

def open_page_gui(parent, vm_results):
    # Create new window instead of root
    app = ctk.CTkToplevel(parent)
    app.geometry("700x600")
    app.title("Page Replacement Simulator")

    # Global references for simulation
    simulation_data = None
    current_step = 0
    grid_labels = []
    is_playing = False

    def run_algorithm():
        nonlocal simulation_data, current_step, is_playing
        output_box.delete("0.0", "end")
        reset_grid()

        ref_input = entry_ref.get().strip()
        valid_ref, result_ref = validate_reference_string(ref_input)
        if not valid_ref:
            output_box.insert("end", f"❌ {result_ref}\n")
            return
        pages = result_ref

        frame_input = entry_frames.get().strip()
        valid_frame, result_frame = validate_frame_count(frame_input)
        if not valid_frame:
            output_box.insert("end", f"❌ {result_frame}\n")
            return
        frames = result_frame

        output_box.insert("end", f"✅ Running {algo_option.get()}...\n")
        algo = algo_option.get()

        if algo == "Optimal":
            simulation_data = optimal_page_replacement(pages, frames)
        elif algo == "Second Chance":
            simulation_data = second_chance_page_replacement(pages, frames)
            compute_aging_registers()
        else:
            output_box.insert("end", "❌ Algorithm not implemented.\n")
            return

        # Save results
        faults = simulation_data["page_faults"]
        hits = simulation_data["hits"]

        vm_results.append({
            "algorithm": algo,
            "faults": faults,
            "hits": hits
        })

        current_step = 0
        draw_grid(current_step)
        output_box.insert("end", f"✅ {algo} done. Page Faults: {faults}, Hits: {hits}\n")

    def compute_aging_registers():
        aging_history = {}
        steps = simulation_data["steps"]

        for step in steps:
            current_aging = {}
            pages = step["frame"]
            ref_bits = step["ref_bits"]
            for i, page in enumerate(pages):
                if page == -1:
                    continue
                prev = aging_history.get(page, 0)
                shifted = prev >> 1
                if ref_bits[i] == 1:
                    shifted |= 0b10000000
                current_aging[page] = shifted
            step["aging_registers"] = current_aging.copy()
            aging_history = current_aging.copy()

    def reset_gui():
        entry_ref.delete(0, 'end')
        entry_frames.delete(0, 'end')
        output_box.delete("0.0", "end")
        reset_grid()

    def reset_grid():
        nonlocal grid_labels
        for label in grid_labels:
            label.destroy()
        grid_labels = []

    def draw_grid(step_index):
        nonlocal grid_labels
        for label in grid_labels:
            label.destroy()
        grid_labels = []

        if not simulation_data:
            return

        steps = simulation_data["steps"]
        num_frames = max(len(step["frame"]) for step in steps)

        for row in range(num_frames + 1):
            for col in range(step_index + 2):
                if row == 0 and col == 0:
                    text = "Frame"
                elif row == 0:
                    text = f"T{col}"
                elif col == 0:
                    text = f"F{row}"
                else:
                    try:
                        frame_val = steps[col - 1]["frame"][row - 1]
                        is_fault = steps[col - 1]["fault"]
                        text = str(frame_val) if frame_val != -1 else ""
                        if algo_option.get() == "Second Chance":
                            ref_bit = steps[col - 1]["ref_bits"][row - 1]
                            text = f"{frame_val}\n(R{ref_bit})" if frame_val != -1 else ""
                    except IndexError:
                        text = ""
                        is_fault = False

                label = ctk.CTkLabel(grid_frame, text=text, width=35, height=35)
                if row > 0 and col > 0:
                    if text != "":
                        label.configure(
                            fg_color="#e74c3c" if is_fault else "#2ecc71",
                            text_color="white",
                            font=ctk.CTkFont(weight="bold")
                        )
                    else:
                        label.configure(fg_color="#2c2c2c", text_color="white")
                label.grid(row=row, column=col, padx=2, pady=1)
                grid_labels.append(label)

        step = steps[step_index]
        page = step["page"]
        fault = step["fault"]
        feedback = "❌ Page Fault: Loaded" if fault else "✅ Page Hit: Page"
        feedback_var.set(f"{feedback} {page}")
        summary_var.set(f"📊 Total Page Faults: {simulation_data['page_faults']} | ✅ Hits: {simulation_data['hits']}")

    def next_step():
        nonlocal current_step
        if simulation_data and current_step < len(simulation_data["steps"]) - 1:
            current_step += 1
            draw_grid(current_step)

    def prev_step():
        nonlocal current_step
        if simulation_data and current_step > 0:
            current_step -= 1
            draw_grid(current_step)

    def auto_play():
        nonlocal is_playing, current_step
        is_playing = not is_playing
        play_btn.configure(text="Pause" if is_playing else "Play")

        def step():
            nonlocal current_step, is_playing
            if is_playing and current_step < len(simulation_data["steps"]) - 1:
                current_step += 1
                draw_grid(current_step)
                app.after(500, step)
            else:
                is_playing = False
                play_btn.configure(text="Play")
        step()

    def draw_aging_history():
        steps = simulation_data["steps"]
        if not steps or "aging_registers" not in steps[0]:
            output_box.insert("end", "⚠️ No aging data found.\n")
            return

        win = ctk.CTkToplevel(app)
        win.title("Aging Bit History")
        all_pages = sorted({p for step in steps for p in step["aging_registers"]})

        ctk.CTkLabel(win, text="Page", font=("Arial", 12, "bold")).grid(row=0, column=0)
        for t in range(len(steps)):
            ctk.CTkLabel(win, text=f"T{t+1}").grid(row=0, column=t+1)

        for r, page in enumerate(all_pages, start=1):
            ctk.CTkLabel(win, text=str(page)).grid(row=r, column=0)
            for c, step in enumerate(steps):
                reg = step["aging_registers"].get(page, 0)
                reg_str = format(reg, '08b')
                fg = "#555555" if reg_str == "00000000" else "#27ae60" if reg_str.startswith("1") else "#ffffff"
                label = ctk.CTkLabel(win, text=reg_str, text_color="black", fg_color=fg, corner_radius=4)
                label.grid(row=r, column=c+1, padx=5, pady=2)

    # -------------- GUI Layout ----------------
    ctk.CTkLabel(app, text="Reference String:").pack(pady=5)
    entry_ref = ctk.CTkEntry(app, width=500)
    entry_ref.pack()

    ctk.CTkLabel(app, text="Number of Frames:").pack(pady=5)
    entry_frames = ctk.CTkEntry(app, width=120)
    entry_frames.pack()

    algo_option = ctk.StringVar(value="Optimal")
    ctk.CTkOptionMenu(app, variable=algo_option, values=["Optimal", "Second Chance"]).pack(pady=10)

    button_frame = ctk.CTkFrame(app)
    button_frame.pack(pady=10)

    ctk.CTkButton(button_frame, text="Run Algorithm", command=run_algorithm).pack(side="left", padx=10)
    ctk.CTkButton(button_frame, text="Reset", command=reset_gui).pack(side="left", padx=10)
    ctk.CTkButton(app, text="Show Summary", command=lambda: show_summary(app, vm_results)).pack(pady=5)
    ctk.CTkButton(app, text="Show Aging Bit History", command=draw_aging_history).pack(pady=5)

    nav_frame = ctk.CTkFrame(app)
    nav_frame.pack(pady=5)

    ctk.CTkButton(nav_frame, text="Previous Step", command=prev_step).pack(side="left", padx=5)
    ctk.CTkButton(nav_frame, text="Next Step", command=next_step).pack(side="left", padx=5)
    play_btn = ctk.CTkButton(nav_frame, text="Play", command=auto_play)
    play_btn.pack(side="left", padx=5)

    output_box = ctk.CTkTextbox(app, height=120, width=550)
    output_box.pack(pady=10)

    grid_frame = ctk.CTkFrame(app)
    grid_frame.pack(pady=10)

    feedback_var = ctk.StringVar()
    ctk.CTkLabel(app, textvariable=feedback_var, font=ctk.CTkFont(size=14)).pack(pady=5)

    summary_var = ctk.StringVar()
    ctk.CTkLabel(app, textvariable=summary_var, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

def show_summary(parent, vm_results):
    win = ctk.CTkToplevel(parent)
    win.title("Virtual Memory Summary")
    
    headers = ["Algorithm", "Page Faults", "Hits"]
    for i, h in enumerate(headers):
        ctk.CTkLabel(win, text=h, font=("Arial", 14, "bold")).grid(row=0, column=i, padx=10)

    for r, res in enumerate(vm_results, start=1):
        ctk.CTkLabel(win, text=res["algorithm"]).grid(row=r, column=0)
        ctk.CTkLabel(win, text=str(res["faults"])).grid(row=r, column=1)
        ctk.CTkLabel(win, text=str(res["hits"])).grid(row=r, column=2)
