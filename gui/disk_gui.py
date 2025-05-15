import customtkinter as ctk
from disk_scheduling.c_scan import cscan_schedule
import threading
import time

# Global state
seek_data = []
seek_index = 0
canvas_labels = []
is_playing = False
disk_max = 200

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("C-SCAN Disk Scheduling")
app.geometry("900x800")

scrollable_frame = ctk.CTkScrollableFrame(app, width=850, height=750)
scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

ctk.CTkLabel(scrollable_frame, text="🌀 C-SCAN Disk Scheduling", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

entry_disk = ctk.CTkEntry(scrollable_frame, placeholder_text="Total Cylinders (e.g. 200)", width=400)
entry_disk.pack(pady=5)

entry_requests = ctk.CTkEntry(scrollable_frame, placeholder_text="Request Queue (e.g. 98 183 37)", width=400)
entry_requests.pack(pady=5)

entry_head = ctk.CTkEntry(scrollable_frame, placeholder_text="Current Head Position (e.g. 53)", width=400)
entry_head.pack(pady=5)

output_box = ctk.CTkTextbox(scrollable_frame, height=150, width=800)
output_box.pack(pady=10)

canvas_frame = ctk.CTkFrame(scrollable_frame)
canvas_frame.pack(pady=10)

canvas = ctk.CTkCanvas(canvas_frame, width=850, height=600, bg="#1e1e1e", highlightthickness=0)
canvas.pack()

def reset_canvas():
    global canvas_labels
    for item in canvas_labels:
        canvas.delete(item)
    canvas_labels.clear()

def get_scaled_x(value):
    margin = 50
    width = 750
    return int(margin + (value / disk_max) * width)

def draw_seek_step():
    global seek_index, seek_data

    if seek_index >= len(seek_data):
        return

    reset_canvas()
    radius = 6
    margin_y = 40
    height_spacing = 40

    for i, cylinder in enumerate(seek_data):
        x = get_scaled_x(cylinder)
        y = margin_y + i * height_spacing
        circle = canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="red")
        canvas_labels.append(circle)
        label = canvas.create_text(x, y - 15, text=str(cylinder), fill="white", font=("Arial", 9))
        canvas_labels.append(label)

    for i in range(seek_index):
        x1 = get_scaled_x(seek_data[i])
        y1 = margin_y + i * height_spacing
        x2 = get_scaled_x(seek_data[i + 1])
        y2 = margin_y + (i + 1) * height_spacing
        line = canvas.create_line(x1, y1, x2, y2, fill="deepskyblue", width=2)
        canvas_labels.append(line)

    seek_index += 1

def reset_seek():
    global seek_index, is_playing
    seek_index = 0
    is_playing = False
    play_btn.configure(text="Play")
    reset_canvas()

def auto_play():
    global is_playing

    if not seek_data:
        return

    is_playing = not is_playing
    play_btn.configure(text="Pause" if is_playing else "Play")

    def loop():
        global seek_index
        while is_playing and seek_index < len(seek_data):
            draw_seek_step()
            time.sleep(0.5)
        if seek_index >= len(seek_data):
            is_playing = False
            play_btn.configure(text="Play")

    threading.Thread(target=loop, daemon=True).start()

def run_cscan():
    global seek_data, seek_index, is_playing, disk_max
    output_box.delete("0.0", "end")
    reset_canvas()
    seek_index = 0
    is_playing = False
    play_btn.configure(text="Play")

    try:
        disk_max = int(entry_disk.get().strip())
        head = int(entry_head.get().strip())
        request_str = entry_requests.get().strip()

        if not request_str:
            output_box.insert("end", "❌ Please enter the request queue.\n")
            return

        requests = list(map(int, request_str.split()))

        if head >= disk_max or any(r >= disk_max for r in requests):
            output_box.insert("end", "❌ Requests and head must be less than disk size.\n")
            return

        seek_data, total_seek = cscan_schedule(requests, head, disk_max)

        output_box.insert("end", "✅ C-SCAN Simulation Complete\n")
        output_box.insert("end", "-" * 40 + "\n")
        output_box.insert("end", f"📥 Request Order: {seek_data}\n")
        output_box.insert("end", f"📏 Total Seek Distance: {total_seek} cylinders\n")

        draw_seek_step()

    except Exception as e:
        output_box.insert("end", f"❌ Error: {e}\n")

ctk.CTkButton(scrollable_frame, text="Run C-SCAN", command=run_cscan).pack(pady=10)

nav_frame = ctk.CTkFrame(scrollable_frame)
nav_frame.pack(pady=5)

ctk.CTkButton(nav_frame, text="Previous Step", command=lambda: [reset_seek(), draw_seek_step()]).pack(side="left", padx=5)
ctk.CTkButton(nav_frame, text="Next Step", command=draw_seek_step).pack(side="left", padx=5)

play_btn = ctk.CTkButton(nav_frame, text="Play", command=auto_play)
play_btn.pack(side="left", padx=5)

app.mainloop()