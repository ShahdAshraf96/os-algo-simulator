import customtkinter as ctk
from page_gui import open_page_gui
from disk_gui import open_disk_gui

# Shared results across modules
vm_results = []
disk_results = []


def show_master_dashboard():
    win = ctk.CTkToplevel(app)
    win.title("Master Comparative Dashboard")

    # --- Virtual Memory Summary ---
    ctk.CTkLabel(win, text="Virtual Memory", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
    headers_vm = ["Algorithm", "Page Faults", "Hits"]
    for i, h in enumerate(headers_vm):
        ctk.CTkLabel(win, text=h).grid(row=1, column=i)

    for idx, res in enumerate(vm_results, start=2):
        ctk.CTkLabel(win, text=res["algorithm"]).grid(row=idx, column=0)
        ctk.CTkLabel(win, text=str(res["faults"])).grid(row=idx, column=1)
        ctk.CTkLabel(win, text=str(res["hits"])).grid(row=idx, column=2)

    row_offset = len(vm_results) + 3
    ctk.CTkLabel(win, text="Disk Scheduling", font=("Arial", 16, "bold")).grid(row=row_offset, column=0, columnspan=3, pady=10)
    headers_disk = ["Algorithm", "Seek Distance", "# of Requests"]
    for i, h in enumerate(headers_disk):
        ctk.CTkLabel(win, text=h).grid(row=row_offset + 1, column=i)

    for idx, res in enumerate(disk_results, start=row_offset + 2):
        ctk.CTkLabel(win, text=res["algorithm"]).grid(row=idx, column=0)
        ctk.CTkLabel(win, text=str(res["seek_distance"])).grid(row=idx, column=1)
        ctk.CTkLabel(win, text=str(res["request_count"])).grid(row=idx, column=2)


# ---------------- MAIN HOME WINDOW ----------------
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("OS Simulator Home")
app.geometry("400x300")

ctk.CTkLabel(app, text="\U0001F9E0 OS Simulator", font=("Arial", 20, "bold")).pack(pady=20)
ctk.CTkButton(app, text="Run Page Replacement", command=lambda: open_page_gui(app, vm_results)).pack(pady=10)
ctk.CTkButton(app, text="Run Disk Scheduling", command=lambda: open_disk_gui(app, disk_results)).pack(pady=10)
ctk.CTkButton(app, text="Show Master Dashboard", command=show_master_dashboard).pack(pady=10)

app.mainloop()