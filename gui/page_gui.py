import customtkinter as ctk
from page_replacement.optimal import optimal_page_replacement
from page_replacement.second_chance import second_chance_page_replacement
from utils.validator import validate_reference_string, validate_frame_count

# Global simulation state
simulation_data = None
current_step = 0
grid_labels = []
is_playing = False


def run_algorithm():
    global simulation_data, current_step, is_playing
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

    try:
        output_box.insert("end", f"✅ Running {algo_option.get()}...\n")
        output_box.insert("end", "-" * 40 + "\n")

        simulation_data = (
            optimal_page_replacement(pages, frames)
            if algo_option.get() == "Optimal"
            else second_chance_page_replacement(pages, frames)
        )

        current_step = 0
        is_playing = False
        play_btn.configure(text="Play")
        draw_grid(current_step)


    except Exception as e:
        output_box.insert("end", f"❌ Error: {e}\n")


def reset_gui():
    entry_ref.delete(0, 'end')
    entry_frames.delete(0, 'end')
    output_box.delete("0.0", "end")
    reset_grid()


def reset_grid():
    global grid_labels
    for label in grid_labels:
        label.destroy()
    grid_labels = []


def draw_grid(step_index):
    global grid_labels

    # Clear previous grid
    for label in grid_labels:
        label.destroy()
    grid_labels = []

    if not simulation_data:
        return

    steps = simulation_data["steps"]
    num_frames = max(len(step["frame"]) for step in steps)

    for row in range(num_frames + 1):  # +1 for header
        for col in range(step_index + 2):  # +1 for frame label, +1 for T1..Ti
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

                    # Append reference bit for Second Chance
                    if algo_option.get() == "Second Chance":
                        ref_bit = steps[col - 1]["ref_bits"][row - 1]
                        text = f"{frame_val}\n(R{ref_bit})" if frame_val != -1 else ""
                except IndexError:
                    text = ""
                    is_fault = False

            label = ctk.CTkLabel(grid_frame, text=text, width=35, height=35)

            # Apply coloring to value cells
            if row > 0 and col > 0:
                if text != "":
                    if is_fault:
                        label.configure(
                            fg_color="#e74c3c",  # Red
                            text_color="white",
                            font=ctk.CTkFont(weight="bold")
                        )
                    else:
                        label.configure(
                            fg_color="#2ecc71",  # Green
                            text_color="white",
                            font=ctk.CTkFont(weight="bold")
                        )
                else:
                    label.configure(
                        fg_color="#2c2c2c",  # Dark gray filler
                        text_color="white"
                    )

            label.grid(row=row, column=col, padx=2, pady=1)
            grid_labels.append(label)

    # ✅ Feedback message
    step = steps[step_index]
    page = step["page"]
    fault = step["fault"]

    if fault:
        try:
            loaded_index = step["frame"].index(page) + 1
            feedback_var.set(f"❌ Page Fault: Loaded page {page} into Frame {loaded_index}")
        except:
            feedback_var.set(f"❌ Page Fault: Loaded page {page}")
    else:
        try:
            hit_index = step["frame"].index(page) + 1
            feedback_var.set(f"✅ Page Hit: Page {page} was already in Frame {hit_index}")
        except:
            feedback_var.set(f"✅ Page Hit: Page {page}")

    # ✅ Summary section
    summary_var.set(f"📊 Total Page Faults: {simulation_data['page_faults']} | ✅ Hits: {simulation_data['hits']}")



def next_step():
    global current_step
    if simulation_data and current_step < len(simulation_data["steps"]) - 1:
        current_step += 1
        draw_grid(current_step)


def prev_step():
    global current_step
    if simulation_data and current_step > 0:
        current_step -= 1
        draw_grid(current_step)


def auto_play():
    global is_playing
    is_playing = not is_playing
    play_btn.configure(text="Pause" if is_playing else "Play")

    def step():
        global current_step
        if is_playing and current_step < len(simulation_data["steps"]) - 1:
            current_step += 1
            draw_grid(current_step)
            app.after(500, step)
        else:
            stop_play()

    step()


def stop_play():
    global is_playing
    is_playing = False
    play_btn.configure(text="Play")


# ---------------------- GUI SETUP --------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("700x600")
app.title("Page Replacement Simulator")

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

# Feedback message for step-by-step status
feedback_var = ctk.StringVar()
feedback_label = ctk.CTkLabel(app, textvariable=feedback_var, font=ctk.CTkFont(size=14))
feedback_label.pack(pady=5)

# Summary (total faults and hits)
summary_var = ctk.StringVar()
summary_label = ctk.CTkLabel(app, textvariable=summary_var, font=ctk.CTkFont(size=14, weight="bold"))
summary_label.pack(pady=5)


app.mainloop()
