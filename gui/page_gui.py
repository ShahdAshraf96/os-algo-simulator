import customtkinter as ctk
from page_replacement.optimal import optimal_page_replacement
from page_replacement.second_chance import second_chance_page_replacement
from utils.validator import validate_reference_string, validate_frame_count


def run_algorithm():
    output_box.delete("0.0", "end")  # Clear previous output

    # ✅ Validate reference string
    ref_input = entry_ref.get().strip()
    valid_ref, result_ref = validate_reference_string(ref_input)
    if not valid_ref:
        output_box.insert("end", f"❌ {result_ref}\n")
        return
    pages = result_ref

    # ✅ Validate frame count
    frame_input = entry_frames.get().strip()
    valid_frame, result_frame = validate_frame_count(frame_input)
    if not valid_frame:
        output_box.insert("end", f"❌ {result_frame}\n")
        return
    frames = result_frame

    try:
        # ✅ Run the selected algorithm
        output_box.insert("end", f"✅ Running {algo_option.get()}...\n")
        output_box.insert("end", "-" * 40 + "\n")

        if algo_option.get() == "Optimal":
            optimal_page_replacement(pages, frames)
        else:
            second_chance_page_replacement(pages, frames)

    except Exception as e:
        output_box.insert("end", f"❌ Error during algorithm execution: {e}\n")

def reset_gui():
    entry_ref.delete(0, 'end')
    entry_frames.delete(0, 'end')
    output_box.delete("0.0", "end")
    canvas_frame.delete("all")  # Clear canvas if visuals exist


# ----------------- GUI SETUP ------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("500x450")
app.title("Page Replacement GUI")

ctk.CTkLabel(app, text="Reference String:").pack(pady=5)
entry_ref = ctk.CTkEntry(app, width=400)
entry_ref.pack()

ctk.CTkLabel(app, text="Number of Frames:").pack(pady=5)
entry_frames = ctk.CTkEntry(app, width=100)
entry_frames.pack()

algo_option = ctk.StringVar(value="Optimal")
ctk.CTkOptionMenu(app, variable=algo_option, values=["Optimal", "Second Chance"]).pack(pady=10)

button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=10)

ctk.CTkButton(button_frame, text="Run Algorithm", command=run_algorithm).pack(side="left", padx=10)
ctk.CTkButton(button_frame, text="Reset", command=reset_gui).pack(side="left", padx=10)

output_box = ctk.CTkTextbox(app, height=200, width=450)
output_box.pack(pady=10)

canvas_frame = ctk.CTkCanvas(app, width=450, height=180, bg="#1e1e1e", highlightthickness=0)
canvas_frame.pack(pady=5)

# Optional: Add a scrollbar to the output box
scrollbar = ctk.CTkScrollbar(app, command=output_box.yview)
scrollbar.pack(side="right", fill="y")
output_box.configure(yscrollcommand=scrollbar.set)
# Optional: Add a scrollbar to the canvas
canvas_scrollbar = ctk.CTkScrollbar(app, command=canvas_frame.yview)
canvas_scrollbar.pack(side="right", fill="y")
canvas_frame.configure(yscrollcommand=canvas_scrollbar.set)


app.mainloop()
