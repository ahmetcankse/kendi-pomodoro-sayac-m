import tkinter as tk
from tkinter import ttk
import json
import os
import ctypes

SETTINGS_FILE = "focus_settings.json"
DURATIONS = [25, 45, 60, 120, 135]


class FocusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus")
        self.root.geometry("900x600")
        self.root.minsize(600, 400)

        self.running = False
        self.is_stopwatch = False
        self.time_left = 25 * 60
        self.dark_mode = True
        self.fullscreen = False
        self.zen_mode = False

        self.pomodoro_count = 0
        self.total_minutes = 0

        self.load_settings()
        self.create_ui()
        self.apply_theme()
        self.make_titlebar_dark()
        self.update_display()
        self.show_credit(startup=True)

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<space>", self.toggle_start_stop)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- UI ----------------
    def create_ui(self):

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.stats_label = ttk.Label(
            self.root,
            text="",
            font=("Segoe UI", 11)
        )
        self.stats_label.pack(pady=10)

        self.center_frame = ttk.Frame(self.root)
        self.center_frame.pack(expand=True)

        self.time_label = ttk.Label(
            self.center_frame,
            text="00:00",
            font=("Segoe UI", 120, "bold")
        )
        self.time_label.pack(expand=True)

        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(pady=20)

        self.duration_var = tk.IntVar(value=25)

        self.duration_menu = ttk.Combobox(
            self.bottom_frame,
            values=DURATIONS,
            textvariable=self.duration_var,
            state="readonly",
            width=6
        )
        self.duration_menu.grid(row=0, column=0, padx=5)

        ttk.Button(self.bottom_frame, text="Pomodoro", command=self.set_pomodoro).grid(row=0, column=1, padx=5)
        ttk.Button(self.bottom_frame, text="Kronometre", command=self.set_stopwatch).grid(row=0, column=2, padx=5)

        ttk.Button(self.bottom_frame, text="Başlat", command=self.start).grid(row=0, column=3, padx=5)
        ttk.Button(self.bottom_frame, text="Durdur", command=self.stop).grid(row=0, column=4, padx=5)
        ttk.Button(self.bottom_frame, text="Sıfırla", command=self.reset).grid(row=0, column=5, padx=5)

        ttk.Button(self.bottom_frame, text="Dark/Light", command=self.toggle_theme).grid(row=0, column=6, padx=5)
        ttk.Button(self.bottom_frame, text="Zen Mode", command=self.toggle_zen).grid(row=0, column=7, padx=5)

        self.update_stats()

    # ---------------- Theme ----------------
    def apply_theme(self):
        bg = "#111111" if self.dark_mode else "#ffffff"
        fg = "#ffffff" if self.dark_mode else "#000000"

        self.root.configure(bg=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", padding=6)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.save_settings()

    # ---------------- Titlebar Dark ----------------
    def make_titlebar_dark(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
            )
        except:
            pass

    # ---------------- Modes ----------------
    def toggle_zen(self):
        self.zen_mode = not self.zen_mode

        if self.zen_mode:
            self.bottom_frame.pack_forget()
            self.stats_label.pack_forget()
        else:
            self.stats_label.pack(pady=10)
            self.bottom_frame.pack(pady=20)

    def set_pomodoro(self):
        self.is_stopwatch = False
        self.reset()

    def set_stopwatch(self):
        self.is_stopwatch = True
        self.time_left = 0
        self.update_display()

    # ---------------- Timer ----------------
    def toggle_start_stop(self, event=None):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        if not self.running:
            self.running = True
            self.run_timer()

    def stop(self):
        self.running = False

    def reset(self):
        self.running = False
        self.time_left = 0 if self.is_stopwatch else self.duration_var.get() * 60
        self.update_display()

    def run_timer(self):
        if self.running:
            if self.is_stopwatch:
                self.time_left += 1
            else:
                if self.time_left > 0:
                    self.time_left -= 1
                else:
                    self.running = False
                    self.pomodoro_count += 1
                    self.total_minutes += self.duration_var.get()
                    self.update_stats()

            self.update_display()
            self.root.after(1000, self.run_timer)

    def update_display(self):
        m = self.time_left // 60
        s = self.time_left % 60
        self.time_label.config(text=f"{m:02}:{s:02}")

    def update_stats(self):
        self.stats_label.config(
            text=f"Pomodoro: {self.pomodoro_count}   |   Toplam Dakika: {self.total_minutes}"
        )
        self.save_settings()

    # ---------------- Fullscreen ----------------
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

    # ---------------- Credit ----------------
    def show_credit(self, startup=False):
        self.credit_label = tk.Label(
            self.root,
            text="Bu bir Ahmetcan Köse yazılımıdır",
            font=("Segoe UI", 9),
            fg="gray",
            bg=self.root["bg"]
        )
        self.credit_label.place(x=10, rely=1.0, anchor="sw")

        self.root.after(2000 if startup else 1000, self.credit_label.destroy)

    def on_close(self):
        self.show_credit(startup=False)
        self.root.after(1000, self.root.destroy)

    # ---------------- Settings ----------------
    def save_settings(self):
        data = {
            "dark_mode": self.dark_mode,
            "pomodoro_count": self.pomodoro_count,
            "total_minutes": self.total_minutes
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                self.dark_mode = data.get("dark_mode", True)
                self.pomodoro_count = data.get("pomodoro_count", 0)
                self.total_minutes = data.get("total_minutes", 0)


root = tk.Tk()
root.iconbitmap("focus.ico")
app = FocusApp(root)
root.mainloop()