def open_disk_gui(parent, disk_results):
    import customtkinter as ctk
    import threading
    import time
    from disk_scheduling.c_scan import cscan_schedule
    from disk_scheduling.c_look import clook_schedule

    # Global state for window
    seek_data = []
    seek_index = 0
    canvas_labels = []
    is_playing = False
    disk_max = 200
    points_xy = []

    # Setup window
    app = ctk.CTkToplevel(parent)
    app.title("Disk Scheduling Simulator")
    app.geometry("900x800")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    scrollable_frame = ctk.CTkScrollableFrame(app, width=850, height=750)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(scrollable_frame, text="C-SCAN Disk Scheduling", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    entry_disk = ctk.CTkEntry(scrollable_frame, placeholder_text="Total Cylinders (e.g. 200)", width=400)
    entry_disk.pack(pady=5)

    entry_requests = ctk.CTkEntry(scrollable_frame, placeholder_text="Request Queue (e.g. 98 183 37)", width=400)
    entry_requests.pack(pady=5)

    entry_head = ctk.CTkEntry(scrollable_frame, placeholder_text="Current Head Position (e.g. 53)", width=400)
    entry_head.pack(pady=5)

    algo_choice = ctk.StringVar(value="C-SCAN")
    ctk.CTkLabel(scrollable_frame, text="Choose Algorithm").pack(pady=3)
    ctk.CTkOptionMenu(scrollable_frame, variable=algo_choice, values=["C-SCAN", "C-LOOK"]).pack()

    output_box = ctk.CTkTextbox(scrollable_frame, height=150, width=800)
    output_box.pack(pady=10)

    canvas_frame = ctk.CTkFrame(scrollable_frame)
    canvas_frame.pack(pady=10)
    canvas = ctk.CTkCanvas(canvas_frame, width=850, height=600, bg="#1e1e1e", highlightthickness=0)
    canvas.pack()

    def reset_canvas():
        nonlocal canvas_labels
        for item in canvas_labels:
            canvas.delete(item)
        canvas_labels.clear()

    def get_scaled_x(value):
        margin = 50
        width = 750
        return int(margin + (value / disk_max) * width)

    def draw_points_only():
        nonlocal canvas_labels, points_xy
        reset_canvas()
        points_xy.clear()
        radius = 6
        margin_y = 40
        height_spacing = 40

        for i, cylinder in enumerate(seek_data):
            x = get_scaled_x(cylinder)
            y = margin_y + i * height_spacing
            circle = canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="red")
            label = canvas.create_text(x, y - 15, text=str(cylinder), fill="white", font=("Arial", 9))
            canvas_labels.extend([circle, label])
            points_xy.append((x, y))

    def draw_seek_step():
        nonlocal seek_index
        if seek_index >= len(points_xy) - 1:
            return
        x1, y1 = points_xy[seek_index]
        x2, y2 = points_xy[seek_index + 1]
        line = canvas.create_line(x1, y1, x2, y2, fill="deepskyblue", width=2)
        canvas_labels.append(line)
        seek_index += 1

    def previous_step():
        nonlocal seek_index
        if seek_index > 0:
            seek_index -= 1
            draw_points_only()
            for i in range(seek_index):
                x1, y1 = points_xy[i]
                x2, y2 = points_xy[i + 1]
                line = canvas.create_line(x1, y1, x2, y2, fill="deepskyblue", width=2)
                canvas_labels.append(line)

    def full_reset():
        nonlocal seek_data, seek_index, is_playing, points_xy
        seek_data = []
        seek_index = 0
        points_xy = []
        is_playing = False
        play_btn.configure(text="Play")
        reset_canvas()
        entry_disk.delete(0, "end")
        entry_requests.delete(0, "end")
        entry_head.delete(0, "end")
        output_box.delete("0.0", "end")

    def auto_play():
        nonlocal is_playing
        if not seek_data:
            return

        is_playing = not is_playing
        play_btn.configure(text="Pause" if is_playing else "Play")

        def loop():
            nonlocal seek_index, is_playing
            while is_playing and seek_index < len(points_xy) - 1:
                draw_seek_step()
                time.sleep(0.5)
            if seek_index >= len(points_xy) - 1:
                is_playing = False
                play_btn.configure(text="Play")

        threading.Thread(target=loop, daemon=True).start()

    def run_algorithm():
        nonlocal seek_data, seek_index, is_playing, disk_max
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
            if disk_max <= 0 or head < 0:
                output_box.insert("end", "❌ Disk size and head position must be positive.\n")
                return
            if head >= disk_max or any(r >= disk_max or r < 0 for r in requests):
                output_box.insert("end", "❌ Requests and head must be within disk size range.\n")
                return

            algo = algo_choice.get()
            if algo == "C-SCAN":
                seek_data, total_seek = cscan_schedule(requests, head, disk_max)
            elif algo == "C-LOOK":
                seek_data, total_seek = clook_schedule(requests, head)
            else:
                output_box.insert("end", "❌ Algorithm not implemented.\n")
                return

            draw_points_only()
            output_box.insert("end", f"✅ {algo} completed.\n")
            output_box.insert("end", f"🔢 Request Order: {seek_data}\n")
            output_box.insert("end", f"📏 Total Seek Distance: {total_seek}\n")

            disk_results.append({
                "algorithm": algo,
                "seek_distance": total_seek,
                "request_count": len(requests)
            })

        except ValueError:
            output_box.insert("end", "❌ Invalid input. Use numeric values.\n")
        except Exception as e:
            output_box.insert("end", f"❌ Error: {str(e)}\n")

    def show_summary():
        if not disk_results:
            output_box.insert("end", "⚠️ No disk scheduling results to summarize.\n")
            return

        summary_win = ctk.CTkToplevel(app)
        summary_win.title("Disk Scheduling Summary")
        headers = ["Algorithm", "Seek Distance", "# of Requests"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(summary_win, text=h, font=("Arial", 14, "bold")).grid(row=0, column=i)
        for idx, res in enumerate(disk_results, start=1):
            ctk.CTkLabel(summary_win, text=res["algorithm"]).grid(row=idx, column=0)
            ctk.CTkLabel(summary_win, text=res["seek_distance"]).grid(row=idx, column=1)
            ctk.CTkLabel(summary_win, text=res["request_count"]).grid(row=idx, column=2)

    # Buttons
    button_frame = ctk.CTkFrame(scrollable_frame)
    button_frame.pack(pady=5)
    ctk.CTkButton(button_frame, text="Run Algorithm", command=run_algorithm).pack(side="left", padx=10)
    ctk.CTkButton(button_frame, text="Show Summary", command=show_summary).pack(side="left", padx=10)

    nav_frame = ctk.CTkFrame(scrollable_frame)
    nav_frame.pack(pady=5)
    ctk.CTkButton(nav_frame, text="Previous Step", command=previous_step).pack(side="left", padx=5)
    ctk.CTkButton(nav_frame, text="Next Step", command=draw_seek_step).pack(side="left", padx=5)
    play_btn = ctk.CTkButton(nav_frame, text="Play", command=auto_play)
    play_btn.pack(side="left", padx=5)
    ctk.CTkButton(nav_frame, text="Reset", command=full_reset).pack(side="left", padx=5)
