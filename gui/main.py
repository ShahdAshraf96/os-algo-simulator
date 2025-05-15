# gui/main.py

import customtkinter as ctk
import subprocess
import sys
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x300")
app.title("🧠 OS Simulator Home")

ctk.CTkLabel(app, text="Welcome to OS Simulator", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=30)

# Helper to launch another file
def run_gui(path):
    if getattr(sys, 'frozen', False):
        # PyInstaller executable mode
        os.system(f"{sys.executable} {path}")
    else:
        subprocess.Popen([sys.executable, path])

# Page Replacement
ctk.CTkButton(app, text="📄 Page Replacement", command=lambda: run_gui("gui/page_gui.py")).pack(pady=10)

# Disk Scheduling
ctk.CTkButton(app, text="💿 Disk Scheduling", command=lambda: run_gui("gui/disk_gui.py")).pack(pady=10)

app.mainloop()
