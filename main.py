import tkinter as tk
import time
import json
import os
from datetime import datetime

APP_WIDTH = 1080
APP_HEIGHT = 700
SIDEBAR_WIDTH = 260

DATA_FILE = "Pinora_focus_data.json"

BG = "#1F111A"
SIDEBAR = "#2A1724"
SIDEBAR_LIGHT = "#3A2233"
MAIN_BG = "#FFF5F0"
CARD = "#FFFFFF"
TEXT = "#2B1E26"
MUTED = "#8B6F7C"
ACCENT = "#F2B8C6"
ACCENT_DARK = "#C86B85"
GOLD = "#D6A94A"
SOFT_GRAY = "#EADDE0"
GREEN = "#8FB996"
RED = "#C97B7B"
ORANGE = "#D89A5B"

STICKY_COLORS = [
    "#FFF2A8", "#FFD6E0", "#D8B4FE", "#B8F2E6",
    "#CDE7FF", "#FFD6A5", "#E7F7C8", "#FBCFE8"
]

PRIORITIES = ["Low", "Medium", "High"]
CATEGORIES = ["Study", "Project", "Personal", "Exam", "Other"]

TIMER_MODES = {
    "25 min Focus": 25 * 60,
    "50 min Deep Work": 50 * 60,
    "5 min Break": 5 * 60,
    "Custom": 25 * 60
}


class PinoraFocusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pinora By Apoorva")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.current_page = "Dashboard"

        self.notes = []
        self.tasks = []
        self.reflection_text = ""
        self.sessions = []

        self.timer_mode = "25 min Focus"
        self.timer_seconds = TIMER_MODES[self.timer_mode]
        self.timer_running = False
        self.last_tick = time.time()
        self.focus_sessions_completed = 0

        self.selected_task_index = None

        self.load_data()
        self.build_layout()
        self.show_dashboard()
        self.update_loop()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- DATA ----------------

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.notes = data.get("notes", [])
            self.tasks = data.get("tasks", [])
            self.reflection_text = data.get("reflection_text", "")
            self.sessions = data.get("sessions", [])
            self.timer_mode = data.get("timer_mode", "25 min Focus")
            self.timer_seconds = data.get("timer_seconds", TIMER_MODES["25 min Focus"])
            self.focus_sessions_completed = data.get("focus_sessions_completed", 0)

        except Exception:
            self.notes = []
            self.tasks = []
            self.reflection_text = ""
            self.sessions = []

    def autosave_reflection_if_open(self):
        try:
            if hasattr(self, "reflection_box") and self.reflection_box.winfo_exists():
                self.reflection_text = self.reflection_box.get("1.0", tk.END).strip()
                self.save_data()
        except tk.TclError:
            pass

    def save_data(self):
        data = {
            "notes": self.notes,
            "tasks": self.tasks,
            "reflection_text": self.reflection_text,
            "sessions": self.sessions,
            "timer_mode": self.timer_mode,
            "timer_seconds": self.timer_seconds,
            "focus_sessions_completed": self.focus_sessions_completed
        }

        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except Exception:
            pass

    def on_close(self):
        self.autosave_reflection_if_open()
        self.save_data()
        self.root.destroy()

    # ---------------- LAYOUT ----------------

    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=SIDEBAR_WIDTH, height=APP_HEIGHT)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = tk.Frame(self.root, bg=MAIN_BG, width=APP_WIDTH - SIDEBAR_WIDTH, height=APP_HEIGHT)
        self.main.pack(side="right", fill="both", expand=True)
        self.main.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="Pinora",
            font=("Helvetica", 28, "bold"),
            fg="#FFF8E8",
            bg=SIDEBAR
        ).pack(anchor="w", padx=24, pady=(28, 0))

        tk.Label(
            self.sidebar,
            text="Focus Board",
            font=("Helvetica", 15, "bold"),
            fg=ACCENT,
            bg=SIDEBAR
        ).pack(anchor="w", padx=26, pady=(0, 18))

        self.time_label = tk.Label(
            self.sidebar,
            text="",
            font=("Helvetica", 11, "bold"),
            fg=GOLD,
            bg=SIDEBAR,
            justify="left"
        )
        self.time_label.pack(anchor="w", padx=26, pady=(0, 18))

        self.nav_buttons = {}

        self.make_nav_button("Dashboard", self.show_dashboard)
        self.make_nav_button("Pinboard", self.show_pinboard)
        self.make_nav_button("To-Do", self.show_todo)
        self.make_nav_button("Focus", self.show_focus)
        self.make_nav_button("Reflection", self.show_reflection)

        tk.Frame(self.sidebar, bg=SIDEBAR_LIGHT, height=1).pack(fill="x", padx=24, pady=22)

        self.sidebar_status = tk.Label(
            self.sidebar,
            text="A calm place to plan,\nfocus, and reflect.",
            font=("Helvetica", 11),
            fg="#D1D5DB",
            bg=SIDEBAR,
            justify="left",
            wraplength=205
        )
        self.sidebar_status.pack(anchor="w", padx=26, pady=(0, 16))

        self.stats_label = tk.Label(
            self.sidebar,
            text="",
            font=("Helvetica", 11),
            fg="#FFF8E8",
            bg=SIDEBAR,
            justify="left"
        )
        self.stats_label.pack(anchor="w", padx=26, pady=(8, 0))

        tk.Button(
            self.sidebar,
            text="View Summary",
            font=("Helvetica", 11, "bold"),
            bg=GOLD,
            fg=TEXT,
            relief="flat",
            pady=10,
            command=self.show_summary_popup
        ).pack(side="bottom", fill="x", padx=24, pady=(0, 22))

        tk.Button(
            self.sidebar,
            text="Save Study Session",
            font=("Helvetica", 11, "bold"),
            bg=ACCENT,
            fg=TEXT,
            relief="flat",
            pady=10,
            command=self.save_study_session
        ).pack(side="bottom", fill="x", padx=24, pady=(0, 8))

    def make_nav_button(self, name, command):
        button = tk.Button(
            self.sidebar,
            text=name,
            font=("Helvetica", 13, "bold"),
            fg=TEXT,
            bg=SOFT_GRAY,
            activebackground=ACCENT,
            activeforeground=TEXT,
            relief="flat",
            anchor="w",
            padx=22,
            pady=11,
            command=command
        )
        button.pack(fill="x", padx=16, pady=3)
        self.nav_buttons[name] = button

    def clear_main(self):
        self.autosave_reflection_if_open()

        for widget in self.main.winfo_children():
            widget.destroy()

    def set_active_page(self, page_name):
        self.current_page = page_name

        for name, button in self.nav_buttons.items():
            if name == page_name:
                button.config(bg=ACCENT, fg=TEXT)
            else:
                button.config(bg=SOFT_GRAY, fg=TEXT)

        self.update_stats()

    def make_header(self, title, subtitle):
        header = tk.Frame(self.main, bg=MAIN_BG)
        header.pack(fill="x", padx=42, pady=(30, 14))

        tk.Label(
            header,
            text=title,
            font=("Helvetica", 30, "bold"),
            fg=TEXT,
            bg=MAIN_BG
        ).pack(anchor="w")

        tk.Label(
            header,
            text=subtitle,
            font=("Helvetica", 12),
            fg=MUTED,
            bg=MAIN_BG
        ).pack(anchor="w", pady=(4, 0))

    def make_card(self, parent):
        return tk.Frame(
            parent,
            bg=CARD,
            highlightbackground=SOFT_GRAY,
            highlightthickness=1
        )

    def update_stats(self):
        total = len(self.tasks)
        done = self.count_done_tasks()
        today_sessions = len(self.get_today_sessions())

        self.stats_label.config(
            text=(
                f"Notes: {len(self.notes)}\n"
                f"Tasks: {total}\n"
                f"Done: {done}\n"
                f"Sessions today: {today_sessions}"
            )
        )

    # ---------------- DASHBOARD ----------------

    def show_dashboard(self):
        self.set_active_page("Dashboard")
        self.clear_main()

        self.make_header(
            "Dashboard",
            "Your calm overview: notes, tasks, focus, and reflection."
        )

        content = tk.Frame(self.main, bg=MAIN_BG)
        content.pack(fill="both", expand=True, padx=42, pady=(0, 34))

        top = tk.Frame(content, bg=MAIN_BG)
        top.pack(fill="x")

        self.dashboard_card(top, "Notes Pinned", str(len(self.notes)), ACCENT_DARK).pack(
            side="left", fill="both", expand=True, padx=(0, 8)
        )

        self.dashboard_card(top, "Tasks Done", f"{self.count_done_tasks()}/{len(self.tasks)}", GREEN).pack(
            side="left", fill="both", expand=True, padx=8
        )

        self.dashboard_card(top, "Sessions Today", str(len(self.get_today_sessions())), GOLD).pack(
            side="left", fill="both", expand=True, padx=8
        )

        self.dashboard_card(top, "Timer", self.format_time(self.timer_seconds), ACCENT_DARK).pack(
            side="left", fill="both", expand=True, padx=(8, 0)
        )

        bottom = tk.Frame(content, bg=MAIN_BG)
        bottom.pack(fill="both", expand=True, pady=(24, 0))

        left = self.make_card(bottom)
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        right = self.make_card(bottom)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.config(width=300)
        right.pack_propagate(False)

        tk.Label(
            left,
            text="Today at a glance",
            font=("Helvetica", 20, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=28, pady=(28, 12))

        progress = self.get_progress_percent()

        tk.Label(
            left,
            text=f"Overall task progress: {progress}%",
            font=("Helvetica", 14, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=28, pady=(4, 10))

        progress_canvas = tk.Canvas(left, width=600, height=18, bg=CARD, highlightthickness=0)
        progress_canvas.pack(anchor="w", padx=28, pady=(0, 24))
        progress_canvas.create_rectangle(0, 0, 600, 18, fill=SOFT_GRAY, outline="")
        progress_canvas.create_rectangle(0, 0, int(600 * progress / 100), 18, fill=ACCENT_DARK, outline="")

        preview = self.get_next_task_preview()

        tk.Label(
            left,
            text="Next task",
            font=("Helvetica", 14, "bold"),
            fg=MUTED,
            bg=CARD
        ).pack(anchor="w", padx=28)

        tk.Label(
            left,
            text=preview,
            font=("Helvetica", 16, "bold"),
            fg=TEXT,
            bg=CARD,
            wraplength=650,
            justify="left"
        ).pack(anchor="w", padx=28, pady=(6, 0))

        tk.Label(
            right,
            text="Quick Actions",
            font=("Helvetica", 18, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=24, pady=(28, 16))

        self.quick_button(right, "Open Pinboard", self.show_pinboard)
        self.quick_button(right, "Open To-Do", self.show_todo)
        self.quick_button(right, "Start Focus", self.show_focus)
        self.quick_button(right, "Save Study Session", self.save_study_session)
        self.quick_button(right, "View Summary", self.show_summary_popup)

    def dashboard_card(self, parent, title, value, color):
        card = self.make_card(parent)

        tk.Label(
            card,
            text=title,
            font=("Helvetica", 11, "bold"),
            fg=MUTED,
            bg=CARD
        ).pack(anchor="w", padx=18, pady=(18, 4))

        tk.Label(
            card,
            text=value,
            font=("Helvetica", 26, "bold"),
            fg=color,
            bg=CARD
        ).pack(anchor="w", padx=18, pady=(0, 18))

        return card

    def quick_button(self, parent, text, command):
        tk.Button(
            parent,
            text=text,
            font=("Helvetica", 12, "bold"),
            bg=SOFT_GRAY,
            fg=TEXT,
            relief="flat",
            pady=11,
            command=command
        ).pack(fill="x", padx=24, pady=6)

    # ---------------- PINBOARD ----------------

    def show_pinboard(self):
        self.set_active_page("Pinboard")
        self.clear_main()

        self.make_header(
            "Pinboard",
            "Add reminders, ideas, quotes, or tiny plans as clean sticky notes."
        )

        controls = tk.Frame(self.main, bg=MAIN_BG)
        controls.pack(fill="x", padx=42, pady=(0, 16))

        self.note_entry = tk.Entry(
            controls,
            font=("Helvetica", 13),
            bg="#FFFFFF",
            fg=TEXT,
            relief="flat",
            highlightbackground=SOFT_GRAY,
            highlightthickness=1
        )
        self.note_entry.pack(side="left", fill="x", expand=True, ipady=10)
        self.note_entry.bind("<Return>", lambda event: self.add_note())

        tk.Button(
            controls,
            text="Add Note",
            font=("Helvetica", 12, "bold"),
            bg=ACCENT_DARK,
            fg=TEXT,
            relief="flat",
            padx=22,
            pady=10,
            command=self.add_note
        ).pack(side="left", padx=(12, 0))

        tk.Button(
            controls,
            text="Clear All",
            font=("Helvetica", 12, "bold"),
            bg=SOFT_GRAY,
            fg=TEXT,
            relief="flat",
            padx=18,
            pady=10,
            command=self.clear_notes
        ).pack(side="left", padx=(8, 0))

        board = self.make_card(self.main)
        board.pack(fill="both", expand=True, padx=42, pady=(0, 34))

        tk.Label(
            board,
            text="Pinned Notes",
            font=("Helvetica", 18, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=26, pady=(20, 8))

        self.notes_grid = tk.Frame(board, bg=CARD)
        self.notes_grid.pack(fill="both", expand=True, padx=22, pady=14)

        self.render_notes()

    def add_note(self):
        text = self.note_entry.get().strip()

        if text == "":
            self.sidebar_status.config(text="Type a note first.")
            return

        if len(self.notes) >= 12:
            self.sidebar_status.config(text="Pinboard full: keep it clean with 12 notes.")
            return

        self.notes.append(text)
        self.note_entry.delete(0, tk.END)
        self.sidebar_status.config(text="Note added.")
        self.save_data()
        self.render_notes()
        self.update_stats()

    def delete_note(self, index):
        if 0 <= index < len(self.notes):
            self.notes.pop(index)
            self.sidebar_status.config(text="Note deleted.")
            self.save_data()
            self.render_notes()
            self.update_stats()

    def clear_notes(self):
        self.notes = []
        self.sidebar_status.config(text="All notes cleared.")
        self.save_data()
        self.render_notes()
        self.update_stats()

    def render_notes(self):
        if not hasattr(self, "notes_grid"):
            return

        for widget in self.notes_grid.winfo_children():
            widget.destroy()

        if len(self.notes) == 0:
            tk.Label(
                self.notes_grid,
                text="No notes yet. Add your first note above.",
                font=("Helvetica", 15),
                fg=MUTED,
                bg=CARD
            ).grid(row=0, column=0, sticky="w", padx=8, pady=12)
            return

        for i, note in enumerate(self.notes):
            row = i // 3
            col = i % 3
            color = STICKY_COLORS[i % len(STICKY_COLORS)]

            sticky = tk.Frame(
                self.notes_grid,
                bg=color,
                width=210,
                height=120,
                highlightbackground="#E5DDA8",
                highlightthickness=1
            )
            sticky.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            sticky.grid_propagate(False)

            top = tk.Frame(sticky, bg=color)
            top.pack(fill="x", padx=10, pady=(8, 0))

            tk.Label(
                top,
                text=f"Note {i + 1}",
                font=("Helvetica", 9, "bold"),
                fg="#4B5563",
                bg=color
            ).pack(side="left")

            tk.Button(
                top,
                text="×",
                font=("Helvetica", 11, "bold"),
                bg=color,
                fg="#7F1D1D",
                relief="flat",
                command=lambda idx=i: self.delete_note(idx)
            ).pack(side="right")

            short = note
            if len(short) > 90:
                short = short[:90] + "..."

            tk.Label(
                sticky,
                text=short,
                font=("Helvetica", 11, "bold"),
                fg="#1F2937",
                bg=color,
                justify="left",
                wraplength=175
            ).pack(anchor="nw", padx=14, pady=(6, 10))

        for c in range(3):
            self.notes_grid.columnconfigure(c, weight=1)

    # ---------------- TODO ----------------

    def show_todo(self):
        self.set_active_page("To-Do")
        self.clear_main()

        self.make_header(
            "To-Do Board",
            "Add tasks with priority and category, then track progress."
        )

        controls = tk.Frame(self.main, bg=MAIN_BG)
        controls.pack(fill="x", padx=42, pady=(0, 14))

        self.task_entry = tk.Entry(
            controls,
            font=("Helvetica", 13),
            bg="#FFFFFF",
            fg=TEXT,
            relief="flat",
            highlightbackground=SOFT_GRAY,
            highlightthickness=1
        )
        self.task_entry.pack(side="left", fill="x", expand=True, ipady=10)
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        self.priority_var = tk.StringVar(value="Medium")
        self.category_var = tk.StringVar(value="Study")

        self.priority_menu = tk.OptionMenu(controls, self.priority_var, *PRIORITIES)
        self.priority_menu.config(bg="#FFFFFF", fg=TEXT, relief="flat", font=("Helvetica", 11), highlightthickness=1)
        self.priority_menu.pack(side="left", padx=(10, 0), ipadx=4, ipady=5)

        self.category_menu = tk.OptionMenu(controls, self.category_var, *CATEGORIES)
        self.category_menu.config(bg="#FFFFFF", fg=TEXT, relief="flat", font=("Helvetica", 11), highlightthickness=1)
        self.category_menu.pack(side="left", padx=(8, 0), ipadx=4, ipady=5)

        tk.Button(
            controls,
            text="Add Task",
            font=("Helvetica", 12, "bold"),
            bg=ACCENT_DARK,
            fg=TEXT,
            relief="flat",
            padx=18,
            pady=10,
            command=self.add_task
        ).pack(side="left", padx=(10, 0))

        content = tk.Frame(self.main, bg=MAIN_BG)
        content.pack(fill="both", expand=True, padx=42, pady=(0, 34))

        left = self.make_card(content)
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        right = self.make_card(content)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.config(width=270)
        right.pack_propagate(False)

        tk.Label(
            left,
            text="Today’s Tasks",
            font=("Helvetica", 18, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=26, pady=(20, 8))

        self.task_frame = tk.Frame(left, bg=CARD)
        self.task_frame.pack(fill="both", expand=True, padx=22, pady=10)

        tk.Label(
            right,
            text="Progress",
            font=("Helvetica", 18, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=22, pady=(24, 10))

        self.progress_text = tk.Label(
            right,
            text="0%",
            font=("Helvetica", 38, "bold"),
            fg=ACCENT_DARK,
            bg=CARD
        )
        self.progress_text.pack(anchor="w", padx=22, pady=(6, 2))

        self.progress_canvas = tk.Canvas(right, width=220, height=18, bg=CARD, highlightthickness=0)
        self.progress_canvas.pack(anchor="w", padx=22, pady=(10, 18))

        tk.Button(
            right,
            text="Complete Selected",
            font=("Helvetica", 12, "bold"),
            bg=GREEN,
            fg=TEXT,
            relief="flat",
            pady=10,
            command=self.complete_selected_task
        ).pack(fill="x", padx=22, pady=6)

        tk.Button(
            right,
            text="Delete Selected",
            font=("Helvetica", 12, "bold"),
            bg=RED,
            fg=TEXT,
            relief="flat",
            pady=10,
            command=self.delete_selected_task
        ).pack(fill="x", padx=22, pady=6)

        tk.Button(
            right,
            text="Clear Completed",
            font=("Helvetica", 12, "bold"),
            bg=SOFT_GRAY,
            fg=TEXT,
            relief="flat",
            pady=10,
            command=self.clear_completed_tasks
        ).pack(fill="x", padx=22, pady=6)

        self.render_tasks()

    def add_task(self):
        text = self.task_entry.get().strip()

        if text == "":
            self.sidebar_status.config(text="Type a task first.")
            return

        if len(self.tasks) >= 14:
            self.sidebar_status.config(text="Task board full: complete or delete tasks.")
            return

        task = {
            "text": text,
            "done": False,
            "priority": self.priority_var.get(),
            "category": self.category_var.get(),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.tasks.append(task)
        self.task_entry.delete(0, tk.END)
        self.sidebar_status.config(text="Task added.")
        self.save_data()
        self.render_tasks()
        self.update_stats()

    def select_task(self, index):
        self.selected_task_index = index
        self.render_tasks()

    def complete_selected_task(self):
        if self.selected_task_index is None:
            self.sidebar_status.config(text="Select a task first.")
            return

        index = self.selected_task_index

        if 0 <= index < len(self.tasks):
            self.tasks[index]["done"] = True
            self.sidebar_status.config(text="Task completed.")
            self.save_data()
            self.render_tasks()
            self.update_stats()

    def delete_selected_task(self):
        if self.selected_task_index is None:
            self.sidebar_status.config(text="Select a task to delete.")
            return

        index = self.selected_task_index

        if 0 <= index < len(self.tasks):
            removed = self.tasks.pop(index)
            self.selected_task_index = None
            self.sidebar_status.config(text="Deleted: " + removed["text"])
            self.save_data()
            self.render_tasks()
            self.update_stats()

    def clear_completed_tasks(self):
        self.tasks = [task for task in self.tasks if not task.get("done", False)]
        self.selected_task_index = None
        self.sidebar_status.config(text="Completed tasks cleared.")
        self.save_data()
        self.render_tasks()
        self.update_stats()

    def render_tasks(self):
        if not hasattr(self, "task_frame"):
            return

        for widget in self.task_frame.winfo_children():
            widget.destroy()

        if len(self.tasks) == 0:
            tk.Label(
                self.task_frame,
                text="No tasks yet. Add your first task above.",
                font=("Helvetica", 15),
                fg=MUTED,
                bg=CARD
            ).pack(anchor="w", padx=8, pady=12)
            self.draw_progress()
            return

        for i, task in enumerate(self.tasks):
            selected = self.selected_task_index == i
            done = task.get("done", False)

            if done:
                bg = "#EEF7EF"
                fg = "#355E3B"
                mark = "✓"
            else:
                bg = "#FFFFFF"
                fg = TEXT
                mark = "○"

            border = ACCENT_DARK if selected else SOFT_GRAY

            row = tk.Frame(
                self.task_frame,
                bg=bg,
                highlightbackground=border,
                highlightthickness=2 if selected else 1
            )
            row.pack(fill="x", padx=8, pady=5)

            tk.Button(
                row,
                text=mark,
                font=("Helvetica", 13, "bold"),
                bg=bg,
                fg=fg,
                relief="flat",
                command=lambda idx=i: self.select_task(idx),
                width=3
            ).pack(side="left", padx=(10, 4), pady=7)

            text_area = tk.Frame(row, bg=bg)
            text_area.pack(side="left", fill="x", expand=True, padx=4, pady=6)

            task_text = task["text"]
            if len(task_text) > 62:
                task_text = task_text[:62] + "..."

            tk.Label(
                text_area,
                text=task_text,
                font=("Helvetica", 12, "bold"),
                fg=fg,
                bg=bg,
                anchor="w"
            ).pack(anchor="w")

            priority_color = self.get_priority_color(task.get("priority", "Medium"))
            meta = f"{task.get('priority', 'Medium')} priority • {task.get('category', 'Other')}"

            tk.Label(
                text_area,
                text=meta,
                font=("Helvetica", 9, "bold"),
                fg=priority_color,
                bg=bg,
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))

            tk.Button(
                row,
                text="Select",
                font=("Helvetica", 10, "bold"),
                bg=ACCENT if selected else SOFT_GRAY,
                fg=TEXT,
                relief="flat",
                command=lambda idx=i: self.select_task(idx)
            ).pack(side="right", padx=10, pady=8)

        self.draw_progress()

    def get_priority_color(self, priority):
        if priority == "High":
            return RED
        if priority == "Medium":
            return ORANGE
        return GREEN

    def draw_progress(self):
        if not hasattr(self, "progress_canvas"):
            return

        progress = self.get_progress_percent()

        self.progress_text.config(text=f"{progress}%")
        self.progress_canvas.delete("all")
        self.progress_canvas.create_rectangle(0, 0, 220, 18, fill=SOFT_GRAY, outline="")
        self.progress_canvas.create_rectangle(0, 0, int(220 * progress / 100), 18, fill=ACCENT_DARK, outline="")

    # ---------------- FOCUS ----------------

    def show_focus(self):
        self.set_active_page("Focus")
        self.clear_main()

        self.make_header(
            "Focus",
            "Choose your timer mode and start a focused session."
        )

        content = tk.Frame(self.main, bg=MAIN_BG)
        content.pack(fill="both", expand=True, padx=42, pady=(0, 34))

        timer_card = self.make_card(content)
        timer_card.pack(side="left", fill="both", expand=True, padx=(0, 14))

        stats_card = self.make_card(content)
        stats_card.pack(side="right", fill="y", padx=(14, 0))
        stats_card.config(width=300)
        stats_card.pack_propagate(False)

        tk.Label(
            timer_card,
            text="Focus Timer",
            font=("Helvetica", 22, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=30, pady=(30, 14))

        settings = tk.Frame(timer_card, bg=CARD)
        settings.pack(anchor="w", padx=30, pady=(0, 16))

        tk.Label(
            settings,
            text="Mode:",
            font=("Helvetica", 12, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(side="left")

        self.timer_mode_var = tk.StringVar(value=self.timer_mode)
        mode_menu = tk.OptionMenu(settings, self.timer_mode_var, *TIMER_MODES.keys(), command=self.set_timer_mode)
        mode_menu.config(bg=SOFT_GRAY, fg=TEXT, relief="flat", font=("Helvetica", 11), highlightthickness=0)
        mode_menu.pack(side="left", padx=(8, 16), ipadx=4, ipady=4)

        tk.Label(
            settings,
            text="Custom minutes:",
            font=("Helvetica", 12, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(side="left")

        self.custom_minutes_entry = tk.Entry(
            settings,
            font=("Helvetica", 12),
            bg="#FFFFFF",
            fg=TEXT,
            relief="flat",
            width=6,
            highlightbackground=SOFT_GRAY,
            highlightthickness=1
        )
        self.custom_minutes_entry.pack(side="left", padx=(8, 8), ipady=5)
        self.custom_minutes_entry.insert(0, "25")

        tk.Button(
            settings,
            text="Apply",
            font=("Helvetica", 11, "bold"),
            bg=ACCENT_DARK,
            fg=TEXT,
            relief="flat",
            padx=12,
            pady=6,
            command=self.apply_timer_mode
        ).pack(side="left")

        self.timer_label = tk.Label(
            timer_card,
            text=self.format_time(self.timer_seconds),
            font=("Helvetica", 72, "bold"),
            fg=TEXT,
            bg=CARD
        )
        self.timer_label.pack(pady=(22, 8))

        self.timer_state_label = tk.Label(
            timer_card,
            text="Paused",
            font=("Helvetica", 14, "bold"),
            fg=MUTED,
            bg=CARD
        )
        self.timer_state_label.pack()

        buttons = tk.Frame(timer_card, bg=CARD)
        buttons.pack(pady=36)

        tk.Button(
            buttons,
            text="Start",
            font=("Helvetica", 13, "bold"),
            bg=ACCENT_DARK,
            fg=TEXT,
            relief="flat",
            padx=28,
            pady=12,
            command=self.start_timer
        ).pack(side="left", padx=8)

        tk.Button(
            buttons,
            text="Pause",
            font=("Helvetica", 13, "bold"),
            bg=SOFT_GRAY,
            fg=TEXT,
            relief="flat",
            padx=28,
            pady=12,
            command=self.pause_timer
        ).pack(side="left", padx=8)

        tk.Button(
            buttons,
            text="Reset",
            font=("Helvetica", 13, "bold"),
            bg=GOLD,
            fg=TEXT,
            relief="flat",
            padx=28,
            pady=12,
            command=self.reset_timer
        ).pack(side="left", padx=8)

        tk.Label(
            stats_card,
            text="Session Summary",
            font=("Helvetica", 18, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=24, pady=(30, 20))

        self.focus_stats_label = tk.Label(
            stats_card,
            text="",
            font=("Helvetica", 14),
            fg=TEXT,
            bg=CARD,
            justify="left"
        )
        self.focus_stats_label.pack(anchor="w", padx=24, pady=6)

        tk.Label(
            stats_card,
            text=(
                "Active time updates using\n"
                "your computer’s local time,\n"
                "so it works wherever you are."
            ),
            font=("Helvetica", 12),
            fg=MUTED,
            bg=CARD,
            justify="left",
            wraplength=230
        ).pack(anchor="w", padx=24, pady=(32, 0))

        self.refresh_focus_page()

    def set_timer_mode(self, value):
        self.timer_mode = value

    def apply_timer_mode(self):
        mode = self.timer_mode_var.get()
        self.timer_mode = mode

        if mode == "Custom":
            try:
                minutes = int(self.custom_minutes_entry.get().strip())

                if minutes <= 0 or minutes > 180:
                    self.sidebar_status.config(text="Custom timer must be 1 to 180 minutes.")
                    return

                self.timer_seconds = minutes * 60
            except ValueError:
                self.sidebar_status.config(text="Enter a valid custom minute number.")
                return
        else:
            self.timer_seconds = TIMER_MODES[mode]

        self.timer_running = False
        self.sidebar_status.config(text=f"Timer set: {mode}.")
        self.save_data()
        self.refresh_focus_page()
        self.update_stats()

    def start_timer(self):
        self.timer_running = True
        self.last_tick = time.time()
        self.sidebar_status.config(text="Focus timer started.")
        self.refresh_focus_page()

    def pause_timer(self):
        self.timer_running = False
        self.sidebar_status.config(text="Focus timer paused.")
        self.refresh_focus_page()

    def reset_timer(self):
        self.timer_running = False

        if self.timer_mode == "Custom" and hasattr(self, "custom_minutes_entry"):
            try:
                minutes = int(self.custom_minutes_entry.get().strip())
                self.timer_seconds = minutes * 60
            except ValueError:
                self.timer_seconds = 25 * 60
        else:
            self.timer_seconds = TIMER_MODES.get(self.timer_mode, 25 * 60)

        self.sidebar_status.config(text="Focus timer reset.")
        self.save_data()
        self.refresh_focus_page()

    def refresh_focus_page(self):
        if hasattr(self, "timer_label"):
            self.timer_label.config(text=self.format_time(self.timer_seconds))

        if hasattr(self, "timer_state_label"):
            if self.timer_running:
                self.timer_state_label.config(text="Running", fg=ACCENT_DARK)
            else:
                self.timer_state_label.config(text="Paused", fg=MUTED)

        if hasattr(self, "focus_stats_label"):
            self.focus_stats_label.config(
                text=(
                    f"Notes pinned: {len(self.notes)}\n"
                    f"Tasks added: {len(self.tasks)}\n"
                    f"Tasks completed: {self.count_done_tasks()}\n"
                    f"Timer mode: {self.timer_mode}\n"
                    f"Focus sessions: {self.focus_sessions_completed}\n"
                    f"Saved today: {len(self.get_today_sessions())}"
                )
            )

    # ---------------- REFLECTION ----------------

    def show_reflection(self):
        self.set_active_page("Reflection")
        self.clear_main()

        self.make_header(
            "Reflection",
            "End your session by writing what you finished and what comes next."
        )

        content = tk.Frame(self.main, bg=MAIN_BG)
        content.pack(fill="both", expand=True, padx=42, pady=(0, 34))

        left = self.make_card(content)
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        right = self.make_card(content)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.config(width=290)
        right.pack_propagate(False)

        tk.Label(
            left,
            text="Daily Reflection",
            font=("Helvetica", 20, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=28, pady=(28, 8))

        prompts = (
            "1. What did I finish today?\n"
            "2. What felt hard but I still tried?\n"
            "3. What is tomorrow’s first task?"
        )

        tk.Label(
            left,
            text=prompts,
            font=("Helvetica", 12),
            fg=MUTED,
            bg=CARD,
            justify="left"
        ).pack(anchor="w", padx=28, pady=(0, 12))

        self.reflection_box = tk.Text(
            left,
            font=("Helvetica", 13),
            bg="#FFFDF8",
            fg=TEXT,
            relief="flat",
            wrap="word",
            height=16,
            highlightbackground=SOFT_GRAY,
            highlightthickness=1
        )
        self.reflection_box.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        self.reflection_box.insert("1.0", self.reflection_text)

        tk.Label(
            right,
            text="Actions",
            font=("Helvetica", 18, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=24, pady=(30, 20))

        tk.Button(
            right,
            text="Save Reflection",
            font=("Helvetica", 12, "bold"),
            bg=ACCENT_DARK,
            fg=TEXT,
            relief="flat",
            pady=12,
            command=self.save_reflection
        ).pack(fill="x", padx=24, pady=6)

        tk.Button(
            right,
            text="Save Study Session",
            font=("Helvetica", 12, "bold"),
            bg=ACCENT,
            fg=TEXT,
            relief="flat",
            pady=12,
            command=self.save_study_session
        ).pack(fill="x", padx=24, pady=6)

        tk.Button(
            right,
            text="Clear Reflection",
            font=("Helvetica", 12, "bold"),
            bg=SOFT_GRAY,
            fg=TEXT,
            relief="flat",
            pady=12,
            command=self.clear_reflection
        ).pack(fill="x", padx=24, pady=6)

        tk.Button(
            right,
            text="View Summary",
            font=("Helvetica", 12, "bold"),
            bg=GOLD,
            fg=TEXT,
            relief="flat",
            pady=12,
            command=self.show_summary_popup
        ).pack(fill="x", padx=24, pady=6)

    def save_reflection(self):
        self.reflection_text = self.reflection_box.get("1.0", tk.END).strip()
        self.sidebar_status.config(text="Reflection saved.")
        self.save_data()

    def clear_reflection(self):
        self.reflection_text = ""
        self.reflection_box.delete("1.0", tk.END)
        self.sidebar_status.config(text="Reflection cleared.")
        self.save_data()

    # ---------------- STUDY SESSIONS ----------------

    def save_study_session(self):
        self.autosave_reflection_if_open()

        now = datetime.now()

        session = {
            "date_key": now.strftime("%Y-%m-%d"),
            "date_display": now.strftime("%d %B %Y"),
            "time": now.strftime("%I:%M %p"),
            "notes_count": len(self.notes),
            "tasks_done": self.count_done_tasks(),
            "tasks_total": len(self.tasks),
            "progress": self.get_progress_percent(),
            "timer_mode": self.timer_mode,
            "remaining_timer": self.format_time(self.timer_seconds),
            "focus_sessions_completed": self.focus_sessions_completed,
            "next_task": self.get_next_task_preview(),
            "reflection": self.reflection_text if self.reflection_text else "No reflection saved."
        }

        self.sessions.append(session)
        self.save_data()
        self.sidebar_status.config(text="Study session saved.")
        self.update_stats()

        self.show_session_saved_popup(session)

    def show_session_saved_popup(self, session):
        popup = tk.Toplevel(self.root)
        popup.title("Session Saved")
        popup.geometry("430x285")
        popup.resizable(False, False)
        popup.configure(bg=MAIN_BG)

        popup.transient(self.root)
        popup.grab_set()

        card = tk.Frame(
            popup,
            bg=CARD,
            highlightbackground=SOFT_GRAY,
            highlightthickness=1
        )
        card.pack(fill="both", expand=True, padx=24, pady=24)

        tk.Label(
            card,
            text="Study Session Saved",
            font=("Helvetica", 22, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=24, pady=(24, 8))

        tk.Label(
            card,
            text=f"{session['date_display']} • {session['time']}",
            font=("Helvetica", 12, "bold"),
            fg=ACCENT_DARK,
            bg=CARD
        ).pack(anchor="w", padx=24)

        tk.Label(
            card,
            text=(
                f"Tasks completed: {session['tasks_done']}/{session['tasks_total']}\n"
                f"Progress: {session['progress']}%\n"
                f"Timer mode: {session['timer_mode']}"
            ),
            font=("Helvetica", 12),
            fg=TEXT,
            bg=CARD,
            justify="left"
        ).pack(anchor="w", padx=24, pady=(18, 14))

        tk.Button(
            card,
            text="Done",
            font=("Helvetica", 12, "bold"),
            bg=ACCENT,
            fg=TEXT,
            relief="flat",
            padx=20,
            pady=9,
            command=popup.destroy
        ).pack(anchor="e", padx=24, pady=(4, 18))

    def get_today_sessions(self):
        today_key = datetime.now().strftime("%Y-%m-%d")
        return [session for session in self.sessions if session.get("date_key") == today_key]

    # ---------------- SUMMARY POPUP ----------------

    def show_summary_popup(self):
        self.autosave_reflection_if_open()
        self.save_data()

        today_date = datetime.now().strftime("%d %B %Y")
        today_sessions = self.get_today_sessions()

        popup = tk.Toplevel(self.root)
        popup.title("Pinora Daily Summary")
        popup.geometry("610x650")
        popup.resizable(False, False)
        popup.configure(bg=MAIN_BG)

        popup.transient(self.root)
        popup.grab_set()

        header = tk.Frame(popup, bg=ACCENT_DARK, height=105)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Pinora Daily Summary",
            font=("Helvetica", 24, "bold"),
            fg=TEXT,
            bg=ACCENT_DARK
        ).pack(anchor="w", padx=28, pady=(24, 0))

        tk.Label(
            header,
            text=f"Daily summary for {today_date}.",
            font=("Helvetica", 12, "bold"),
            fg=TEXT,
            bg=ACCENT_DARK
        ).pack(anchor="w", padx=30, pady=(4, 0))

        body = tk.Frame(
            popup,
            bg=CARD,
            highlightbackground=SOFT_GRAY,
            highlightthickness=1
        )
        body.pack(fill="both", expand=True, padx=26, pady=24)

        done = self.count_done_tasks()
        total = len(self.tasks)
        progress = self.get_progress_percent()

        tk.Label(
            body,
            text="Today’s Overview",
            font=("Helvetica", 18, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w", padx=24, pady=(20, 8))

        overview = (
            f"Notes pinned: {len(self.notes)}\n"
            f"Current tasks completed: {done}/{total}\n"
            f"Current progress: {progress}%\n"
            f"Saved study sessions today: {len(today_sessions)}\n"
            f"Timer mode: {self.timer_mode}\n"
            f"Focus sessions completed: {self.focus_sessions_completed}"
        )

        tk.Label(
            body,
            text=overview,
            font=("Helvetica", 12),
            fg=TEXT,
            bg=CARD,
            justify="left"
        ).pack(anchor="w", padx=24, pady=(0, 14))

        tk.Label(
            body,
            text="Saved Study Sessions",
            font=("Helvetica", 15, "bold"),
            fg=MUTED,
            bg=CARD
        ).pack(anchor="w", padx=24, pady=(4, 6))

        sessions_box = tk.Text(
            body,
            font=("Helvetica", 11),
            bg="#FFFDF8",
            fg=TEXT,
            relief="flat",
            wrap="word",
            height=12,
            highlightbackground=SOFT_GRAY,
            highlightthickness=1
        )
        sessions_box.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        if len(today_sessions) == 0:
            sessions_text = "No study sessions saved yet today.\n\nClick 'Save Study Session' after each study block."
        else:
            session_lines = []

            for i, session in enumerate(today_sessions, start=1):
                reflection = session.get("reflection", "No reflection saved.")
                if len(reflection) > 120:
                    reflection = reflection[:120] + "..."

                session_lines.append(
                    f"Session {i} — {session.get('time', '')}\n"
                    f"Tasks: {session.get('tasks_done', 0)}/{session.get('tasks_total', 0)} "
                    f"({session.get('progress', 0)}%)\n"
                    f"Timer: {session.get('timer_mode', 'Focus')}\n"
                    f"Next task: {session.get('next_task', 'No task')}\n"
                    f"Reflection: {reflection}\n"
                )

            sessions_text = "\n".join(session_lines)

        sessions_box.insert("1.0", sessions_text)
        sessions_box.config(state="disabled")

        tk.Button(
            body,
            text="Close Summary",
            font=("Helvetica", 12, "bold"),
            bg=ACCENT,
            fg=TEXT,
            relief="flat",
            padx=20,
            pady=10,
            command=popup.destroy
        ).pack(anchor="e", padx=24, pady=(0, 18))

    # ---------------- HELPERS ----------------

    def count_done_tasks(self):
        return sum(1 for task in self.tasks if task.get("done", False))

    def get_progress_percent(self):
        if len(self.tasks) == 0:
            return 0
        return int((self.count_done_tasks() / len(self.tasks)) * 100)

    def get_next_task_preview(self):
        for task in self.tasks:
            if not task.get("done", False):
                return task.get("text", "No task")
        if self.tasks:
            return "All tasks are complete."
        return "No tasks yet."

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def update_loop(self):
        now = datetime.now()
        self.time_label.config(
            text="Active time\n" + now.strftime("%a, %d %b\n%I:%M:%S %p")
        )

        if self.timer_running:
            current = time.time()

            if current - self.last_tick >= 1:
                self.last_tick = current

                if self.timer_seconds > 0:
                    self.timer_seconds -= 1
                else:
                    self.timer_running = False
                    self.focus_sessions_completed += 1
                    self.sidebar_status.config(text="Focus session complete.")
                    self.save_data()

        if self.current_page == "Focus":
            self.refresh_focus_page()

        self.update_stats()
        self.root.after(500, self.update_loop)


def main():
    root = tk.Tk()
    app = PinoraFocusApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
