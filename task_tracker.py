import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

# =========================================================
# COLORS
# =========================================================

BG = "#F4F6FB"
WHITE = "#FFFFFF"
TEXT = "#252A3D"
MUTED = "#7A8198"

PRIMARY = "#6C63FF"
PRIMARY_DARK = "#574FE0"

GREEN = "#20C879"
RED = "#EF476F"
ORANGE = "#F4A51C"
BLUE = "#3B82F6"

LIGHT_GREEN = "#EAF9F0"
LIGHT_RED = "#FFF0F2"
LIGHT_ORANGE = "#FFF7E3"
LIGHT_BLUE = "#EEF5FF"
LIGHT_PURPLE = "#F0EEFF"

# =========================================================
# FILES
# =========================================================

TASK_FILE = "tasks.json"
USER_FILE = "user.json"


# =========================================================
# GLOBAL DATA
# =========================================================

tasks = []
username = "User"

row_task_map = {}
reminded_tasks = set()


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()

window.title("My Task Tracker")
window.geometry("1150x800")
window.resizable(False, False)
window.configure(bg=BG)


# =========================================================
# DATE FUNCTIONS
# =========================================================

def parse_due_date(date_text):

    if not date_text or date_text == "No deadline":
        return None

    try:
        return datetime.strptime(
            date_text,
            "%d-%m-%Y %I:%M %p"
        )
    except ValueError:
        return None


def is_overdue(task):

    if task["status"] == "Completed":
        return False

    due = parse_due_date(task["due_date"])

    if due is None:
        return False

    return due < datetime.now()


def is_today(task):

    due = parse_due_date(task["due_date"])

    if due is None:
        return False

    return due.date() == datetime.now().date()


def is_upcoming(task):

    if task["status"] == "Completed":
        return False

    due = parse_due_date(task["due_date"])

    if due is None:
        return False

    return due > datetime.now()


# =========================================================
# USER
# =========================================================

def load_user():

    global username

    if os.path.exists(USER_FILE):

        try:
            with open(
                USER_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            username = data.get(
                "username",
                "User"
            )

        except:
            username = "User"


def save_user(name):

    global username

    username = name

    with open(
        USER_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "username": username
            },
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# TASK SAVE
# =========================================================

def save_tasks():

    try:

        with open(
            TASK_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                tasks,
                file,
                ensure_ascii=False,
                indent=4
            )

    except Exception as error:

        messagebox.showerror(
            "Save Error",
            f"Could not save tasks.\n\n{error}"
        )


# =========================================================
# TASK LOAD
# =========================================================

def load_tasks():

    global tasks

    if not os.path.exists(TASK_FILE):

        tasks = []

        return

    try:

        with open(
            TASK_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            saved_data = json.load(file)

        tasks = []

        for item in saved_data:

            # New dictionary format
            if isinstance(item, dict):

                item.setdefault(
                    "title",
                    "Untitled Task"
                )

                item.setdefault(
                    "category",
                    "General"
                )

                item.setdefault(
                    "priority",
                    "Medium"
                )

                item.setdefault(
                    "due_date",
                    "No deadline"
                )

                item.setdefault(
                    "date",
                    "Old Task"
                )

                item.setdefault(
                    "status",
                    "Pending"
                )

                item.setdefault(
                    "notes",
                    ""
                )

                tasks.append(item)

            # Old text format
            else:

                old_text = str(item)

                completed = old_text.startswith(
                    "✅ "
                )

                if completed:
                    old_text = old_text[2:]

                priority = "Medium"

                if old_text.startswith("[High]"):

                    priority = "High"

                    old_text = old_text.replace(
                        "[High]",
                        "",
                        1
                    ).strip()

                elif old_text.startswith("[Medium]"):

                    priority = "Medium"

                    old_text = old_text.replace(
                        "[Medium]",
                        "",
                        1
                    ).strip()

                elif old_text.startswith("[Low]"):

                    priority = "Low"

                    old_text = old_text.replace(
                        "[Low]",
                        "",
                        1
                    ).strip()

                if "|" in old_text:

                    title, date = old_text.split(
                        "|",
                        1
                    )

                    title = title.strip()
                    date = date.strip()

                else:

                    title = old_text
                    date = "Old Task"

                tasks.append(
                    {
                        "title": title,
                        "category": "General",
                        "priority": priority,
                        "due_date": "No deadline",
                        "date": date,
                        "status": (
                            "Completed"
                            if completed
                            else "Pending"
                        ),
                        "notes": ""
                    }
                )

        save_tasks()

    except Exception as error:

        messagebox.showerror(
            "Load Error",
            f"Could not load tasks.\n\n{error}"
        )

        tasks = []


# =========================================================
# LOGIN SCREEN
# =========================================================

def show_login():

    for widget in window.winfo_children():
        widget.destroy()

    window.geometry(
        "650x650"
    )

    window.configure(
        bg=BG
    )

    card = tk.Frame(
        window,
        bg=WHITE,
        width=500,
        height=520
    )

    card.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    card.pack_propagate(False)

    # Logo
    tk.Label(
        card,
        text="✓",
        font=("Segoe UI", 32, "bold"),
        bg=PRIMARY,
        fg=WHITE,
        width=2
    ).pack(
        pady=(40, 15)
    )

    # Title
    tk.Label(
        card,
        text="My Task Tracker",
        font=("Segoe UI", 27, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack()

    tk.Label(
        card,
        text="Your personal productivity space",
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=MUTED
    ).pack(
        pady=(5, 30)
    )

    tk.Label(
        card,
        text="Welcome 👋",
        font=("Segoe UI", 19, "bold"),
        bg=WHITE,
        fg=PRIMARY
    ).pack()

    tk.Label(
        card,
        text="What should we call you?",
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=MUTED
    ).pack(
        pady=(5, 15)
    )

    name_entry = tk.Entry(
        card,
        font=("Segoe UI", 12),
        bg="#F4F5FA",
        fg=TEXT,
        relief="flat",
        justify="center"
    )

    name_entry.pack(
        padx=70,
        fill="x",
        ipady=10
    )

    if username != "User":

        name_entry.insert(
            0,
            username
        )

    def continue_app():

        name = name_entry.get().strip()

        if name == "":

            messagebox.showwarning(
                "Name Required",
                "Please enter your name."
            )

            return

        save_user(name)

        show_dashboard()

    tk.Button(
        card,
        text="Continue  →",
        font=("Segoe UI", 12, "bold"),
        bg=PRIMARY,
        fg=WHITE,
        activebackground=PRIMARY_DARK,
        relief="flat",
        cursor="hand2",
        command=continue_app
    ).pack(
        fill="x",
        padx=70,
        pady=25,
        ipady=9
    )

    tk.Label(
        card,
        text="Your tasks are saved automatically.",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=MUTED
    ).pack()

    name_entry.focus()


# =========================================================
# DASHBOARD
# =========================================================

def show_dashboard():

    for widget in window.winfo_children():
        widget.destroy()

    window.geometry(
        "1150x800"
    )

    window.configure(
        bg=BG
    )

    row_task_map.clear()

    # =====================================================
    # TASK FUNCTIONS
    # =====================================================

    def update_stats():

        total = len(tasks)

        completed = sum(
            1
            for task in tasks
            if task["status"] == "Completed"
        )

        pending = total - completed

        total_value.config(
            text=str(total)
        )

        pending_value.config(
            text=str(pending)
        )

        completed_value.config(
            text=str(completed)
        )

        if total > 0:

            percent = (
                completed /
                total
            ) * 100

        else:

            percent = 0

        progress_bar["value"] = percent

        progress_label.config(
            text=f"{int(percent)}% Completed"
        )

    def refresh_table(data=None):

        row_task_map.clear()

        if data is None:
            data = tasks

        for item in task_table.get_children():
            task_table.delete(item)

        for task in data:

            if task["status"] == "Completed":

                status = "✓ Completed"

            elif is_overdue(task):

                status = "⚠ Overdue"

            else:

                status = "○ Pending"

            values = (
                task["title"],
                task["category"],
                task["priority"],
                task["due_date"],
                status
            )

            item_id = task_table.insert(
                "",
                tk.END,
                values=values
            )

            row_task_map[item_id] = tasks.index(
                task
            )

            if task["status"] == "Completed":

                task_table.item(
                    item_id,
                    tags=("completed",)
                )

            elif is_overdue(task):

                task_table.item(
                    item_id,
                    tags=("overdue",)
                )

            elif task["priority"] == "High":

                task_table.item(
                    item_id,
                    tags=("high",)
                )

            elif task["priority"] == "Medium":

                task_table.item(
                    item_id,
                    tags=("medium",)
                )

            else:

                task_table.item(
                    item_id,
                    tags=("low",)
                )

        update_stats()

    def add_task():

        title = task_entry.get().strip()

        notes = notes_text.get(
            "1.0",
            tk.END
        ).strip()

        category = category_combo.get()

        priority = priority_combo.get()

        due_date = due_entry.get().strip()

        if title == "":

            messagebox.showwarning(
                "Missing Task",
                "Please enter a task first."
            )

            task_entry.focus()

            return

        if due_date == "":
            due_date = "No deadline"

        if due_date != "No deadline":

            try:

                datetime.strptime(
                    due_date,
                    "%d-%m-%Y %I:%M %p"
                )

            except ValueError:

                messagebox.showwarning(
                    "Invalid Date",
                    "Use:\n\n"
                    "DD-MM-YYYY HH:MM AM/PM\n\n"
                    "Example:\n"
                    "10-10-2026 06:00 PM"
                )

                return

        now = datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        )

        tasks.append(
            {
                "title": title,
                "category": category,
                "priority": priority,
                "due_date": due_date,
                "date": now,
                "status": "Pending",
                "notes": notes
            }
        )

        save_tasks()

        refresh_table()

        task_entry.delete(
            0,
            tk.END
        )

        notes_text.delete(
            "1.0",
            tk.END
        )

        due_entry.delete(
            0,
            tk.END
        )

        task_entry.focus()

    def get_selected_index():

        selected = task_table.selection()

        if not selected:
            return None

        return row_task_map.get(
            selected[0]
        )

    def complete_task():

        index = get_selected_index()

        if index is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a task first."
            )

            return

        if tasks[index]["status"] == "Completed":

            messagebox.showinfo(
                "Already Completed",
                "This task is already completed."
            )

            return

        task_name = tasks[index]["title"]

        tasks[index]["status"] = "Completed"

        save_tasks()

        refresh_table()

        messagebox.showinfo(
            "✅ Task Completed",
            f"Great job, {username}! 🎉\n\n"
            f'"{task_name}"\n\n'
            f"has been completed successfully."
        )

    def delete_task():

        index = get_selected_index()

        if index is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a task first."
            )

            return

        task_name = tasks[index]["title"]

        answer = messagebox.askyesno(
            "Delete Task",
            f'Delete this task?\n\n"{task_name}"'
        )

        if answer:

            tasks.pop(index)

            save_tasks()

            refresh_table()

    def clear_all():

        if len(tasks) == 0:

            messagebox.showinfo(
                "No Tasks",
                "There are no tasks to clear."
            )

            return

        answer = messagebox.askyesno(
            "Clear All Tasks",
            "Are you sure you want to delete ALL tasks?"
        )

        if answer:

            tasks.clear()

            save_tasks()

            refresh_table()

    def search_task():

        text = (
            search_entry
            .get()
            .strip()
            .lower()
        )

        if text == "":

            refresh_table()

            return

        filtered = []

        for task in tasks:

            if (
                text in task["title"].lower()
                or text in task["category"].lower()
                or text in task["priority"].lower()
                or text in task["status"].lower()
                or text in task["notes"].lower()
            ):

                filtered.append(task)

        refresh_table(
            filtered
        )

    def show_all():

        search_entry.delete(
            0,
            tk.END
        )

        refresh_table()

    def show_pending():

        refresh_table(
            [
                task
                for task in tasks
                if task["status"] == "Pending"
            ]
        )

    def show_completed():

        refresh_table(
            [
                task
                for task in tasks
                if task["status"] == "Completed"
            ]
        )

    def show_high():

        refresh_table(
            [
                task
                for task in tasks
                if task["priority"] == "High"
            ]
        )

    def show_today():

        refresh_table(
            [
                task
                for task in tasks
                if is_today(task)
            ]
        )

    def show_upcoming():

        filtered = [
            task
            for task in tasks
            if is_upcoming(task)
        ]

        filtered.sort(
            key=lambda task:
            parse_due_date(
                task["due_date"]
            ) or datetime.max
        )

        refresh_table(
            filtered
        )

    def show_overdue():

        refresh_table(
            [
                task
                for task in tasks
                if is_overdue(task)
            ]
        )

    def sort_due_date():

        sorted_tasks = sorted(
            tasks,
            key=lambda task:
            parse_due_date(
                task["due_date"]
            ) or datetime.max
        )

        refresh_table(
            sorted_tasks
        )

    # =====================================================
    # VIEW DETAILS
    # =====================================================

    def view_details():

        index = get_selected_index()

        if index is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a task first."
            )

            return

        task = tasks[index]

        detail = tk.Toplevel(
            window
        )

        detail.title(
            "Task Details"
        )

        detail.geometry(
            "500x600"
        )

        detail.resizable(
            False,
            False
        )

        detail.configure(
            bg=BG
        )

        # Header
        tk.Label(
            detail,
            text="Task Details",
            font=("Segoe UI", 22, "bold"),
            bg=BG,
            fg=TEXT
        ).pack(
            pady=(25, 5)
        )

        tk.Label(
            detail,
            text="Complete information about your task",
            font=("Segoe UI", 9),
            bg=BG,
            fg=MUTED
        ).pack(
            pady=(0, 20)
        )

        # Task title
        tk.Label(
            detail,
            text=task["title"],
            font=("Segoe UI", 18, "bold"),
            bg=WHITE,
            fg=TEXT,
            wraplength=420,
            justify="center"
        ).pack(
            fill="x",
            padx=30,
            pady=15,
            ipady=15
        )

        # Information card
        info = tk.Frame(
            detail,
            bg=WHITE
        )

        info.pack(
            fill="x",
            padx=30,
            pady=5
        )

        def info_row(
            label,
            value
        ):

            row = tk.Frame(
                info,
                bg=WHITE
            )

            row.pack(
                fill="x",
                padx=15,
                pady=7
            )

            tk.Label(
                row,
                text=label,
                font=("Segoe UI", 9, "bold"),
                bg=WHITE,
                fg=MUTED,
                width=15,
                anchor="w"
            ).pack(
                side="left"
            )

            tk.Label(
                row,
                text=value,
                font=("Segoe UI", 10, "bold"),
                bg=WHITE,
                fg=TEXT,
                wraplength=280,
                anchor="w"
            ).pack(
                side="left"
            )

        info_row(
            "Category",
            task["category"]
        )

        info_row(
            "Priority",
            task["priority"]
        )

        info_row(
            "Due Date",
            task["due_date"]
        )

        info_row(
            "Status",
            task["status"]
        )

        info_row(
            "Created",
            task["date"]
        )

        # Notes
        tk.Label(
            detail,
            text="NOTES",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=30,
            pady=(18, 5)
        )

        notes_box = tk.Text(
            detail,
            height=7,
            font=("Segoe UI", 10),
            bg=WHITE,
            fg=TEXT,
            relief="flat",
            wrap="word"
        )

        notes_box.pack(
            fill="both",
            padx=30,
            pady=(0, 20)
        )

        notes_box.insert(
            "1.0",
            task["notes"]
            if task["notes"]
            else "No notes added."
        )

        notes_box.config(
            state="disabled"
        )

        tk.Button(
            detail,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=PRIMARY,
            fg=WHITE,
            activebackground=PRIMARY_DARK,
            relief="flat",
            cursor="hand2",
            command=detail.destroy
        ).pack(
            fill="x",
            padx=30,
            ipady=8
        )

    # =====================================================
    # EDIT TASK
    # =====================================================

    def edit_task():

        index = get_selected_index()

        if index is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a task first."
            )

            return

        task = tasks[index]

        edit = tk.Toplevel(
            window
        )

        edit.title(
            "Edit Task"
        )

        edit.geometry(
            "480x700"
        )

        edit.resizable(
            False,
            False
        )

        edit.configure(
            bg=BG
        )

        tk.Label(
            edit,
            text="Edit Your Task",
            font=("Segoe UI", 21, "bold"),
            bg=BG,
            fg=TEXT
        ).pack(
            pady=(22, 4)
        )

        tk.Label(
            edit,
            text="Update your task information",
            font=("Segoe UI", 9),
            bg=BG,
            fg=MUTED
        ).pack(
            pady=(0, 18)
        )

        # Title
        tk.Label(
            edit,
            text="TASK",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=35
        )

        edit_title = tk.Entry(
            edit,
            font=("Segoe UI", 11),
            bg=WHITE,
            fg=TEXT,
            relief="flat"
        )

        edit_title.pack(
            fill="x",
            padx=35,
            pady=(5, 15),
            ipady=9
        )

        edit_title.insert(
            0,
            task["title"]
        )

        # Category
        tk.Label(
            edit,
            text="CATEGORY",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=35
        )

        edit_category = ttk.Combobox(
            edit,
            values=[
                "Study",
                "Work",
                "Personal",
                "College",
                "Health",
                "Shopping",
                "General"
            ],
            state="readonly"
        )

        edit_category.set(
            task["category"]
        )

        edit_category.pack(
            fill="x",
            padx=35,
            pady=(5, 15)
        )

        # Priority
        tk.Label(
            edit,
            text="PRIORITY",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=35
        )

        edit_priority = ttk.Combobox(
            edit,
            values=[
                "High",
                "Medium",
                "Low"
            ],
            state="readonly"
        )

        edit_priority.set(
            task["priority"]
        )

        edit_priority.pack(
            fill="x",
            padx=35,
            pady=(5, 15)
        )

        # Due date
        tk.Label(
            edit,
            text="DUE DATE & TIME",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=35
        )

        edit_due = tk.Entry(
            edit,
            font=("Segoe UI", 10),
            bg=WHITE,
            fg=TEXT,
            relief="flat"
        )

        edit_due.pack(
            fill="x",
            padx=35,
            pady=(5, 3),
            ipady=8
        )

        edit_due.insert(
            0,
            task["due_date"]
        )

        tk.Label(
            edit,
            text="Example: 10-10-2026 06:00 PM",
            font=("Segoe UI", 8),
            bg=BG,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=35
        )

        # Notes
        tk.Label(
            edit,
            text="NOTES",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=35,
            pady=(18, 4)
        )

        edit_notes = tk.Text(
            edit,
            height=7,
            font=("Segoe UI", 10),
            bg=WHITE,
            fg=TEXT,
            relief="flat",
            wrap="word"
        )

        edit_notes.pack(
            fill="both",
            padx=35
        )

        edit_notes.insert(
            "1.0",
            task.get(
                "notes",
                ""
            )
        )

        def save_edit():

            new_title = (
                edit_title
                .get()
                .strip()
            )

            new_category = (
                edit_category
                .get()
            )

            new_priority = (
                edit_priority
                .get()
            )

            new_due = (
                edit_due
                .get()
                .strip()
            )

            new_notes = (
                edit_notes
                .get(
                    "1.0",
                    tk.END
                )
                .strip()
            )

            if new_title == "":

                messagebox.showwarning(
                    "Missing Task",
                    "Task name cannot be empty."
                )

                return

            if new_due == "":
                new_due = "No deadline"

            if new_due != "No deadline":

                try:

                    datetime.strptime(
                        new_due,
                        "%d-%m-%Y %I:%M %p"
                    )

                except ValueError:

                    messagebox.showwarning(
                        "Invalid Date",
                        "Use:\n"
                        "DD-MM-YYYY HH:MM AM/PM"
                    )

                    return

            tasks[index]["title"] = new_title

            tasks[index]["category"] = new_category

            tasks[index]["priority"] = new_priority

            tasks[index]["due_date"] = new_due

            tasks[index]["notes"] = new_notes

            save_tasks()

            refresh_table()

            edit.destroy()

        tk.Button(
            edit,
            text="✓  Save Changes",
            font=("Segoe UI", 11, "bold"),
            bg=PRIMARY,
            fg=WHITE,
            activebackground=PRIMARY_DARK,
            relief="flat",
            cursor="hand2",
            command=save_edit
        ).pack(
            fill="x",
            padx=35,
            pady=20,
            ipady=9
        )

    # =====================================================
    # REMINDER
    # =====================================================

    def check_reminders():

        now = datetime.now()

        for index, task in enumerate(tasks):

            if task["status"] == "Completed":
                continue

            if task["due_date"] == "No deadline":
                continue

            due = parse_due_date(
                task["due_date"]
            )

            if due is None:
                continue

            difference = (
                due - now
            ).total_seconds()

            reminder_key = (
                f"{index}|"
                f"{task['title']}|"
                f"{task['due_date']}"
            )

            if (
                0 <= difference <= 30
                and reminder_key not in reminded_tasks
            ):

                reminded_tasks.add(
                    reminder_key
                )

                messagebox.showinfo(
                    "🔔 Task Reminder",
                    f"Your task is due now!\n\n"
                    f"{task['title']}"
                )

        window.after(
            30000,
            check_reminders
        )

    # =====================================================
    # STYLE
    # =====================================================

    style = ttk.Style()

    try:
        style.theme_use("clam")
    except:
        pass

    style.configure(
        "Treeview",
        background=WHITE,
        foreground=TEXT,
        rowheight=40,
        fieldbackground=WHITE,
        font=("Segoe UI", 10),
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background="#EEF0F7",
        foreground=TEXT,
        font=("Segoe UI", 9, "bold"),
        padding=9
    )

    style.map(
        "Treeview",
        background=[
            ("selected", "#E7E4FF")
        ],
        foreground=[
            ("selected", TEXT)
        ]
    )

    style.configure(
        "TCombobox",
        padding=7,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#E7E8F0",
        background=PRIMARY,
        thickness=10
    )

    # =====================================================
    # HEADER
    # =====================================================

    header = tk.Frame(
        window,
        bg=PRIMARY,
        height=105
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(
        False
    )

    brand = tk.Frame(
        header,
        bg=PRIMARY
    )

    brand.pack(
        side="left",
        padx=30
    )

    logo = tk.Label(
        brand,
        text="✓",
        font=("Segoe UI", 25, "bold"),
        bg=WHITE,
        fg=PRIMARY,
        width=2
    )

    logo.pack(
        side="left",
        padx=(0, 12)
    )

    brand_text = tk.Frame(
        brand,
        bg=PRIMARY
    )

    brand_text.pack(
        side="left"
    )

    tk.Label(
        brand_text,
        text="My Task Tracker",
        font=("Segoe UI", 23, "bold"),
        bg=PRIMARY,
        fg=WHITE
    ).pack(
        anchor="w"
    )

    greeting_label = tk.Label(
        brand_text,
        text=f"Welcome, {username} 👋",
        font=("Segoe UI", 10),
        bg=PRIMARY,
        fg="#E8E7FF"
    )

    greeting_label.pack(
        anchor="w"
    )

    tk.Label(
        header,
        text=datetime.now().strftime(
            "%A, %d %B %Y"
        ),
        font=("Segoe UI", 9),
        bg=PRIMARY,
        fg=WHITE
    ).pack(
        side="right",
        padx=30
    )

    # =====================================================
    # MAIN
    # =====================================================

    main = tk.Frame(
        window,
        bg=BG
    )

    main.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=18
    )

    # =====================================================
    # STAT CARDS
    # =====================================================

    stats = tk.Frame(
        main,
        bg=BG
    )

    stats.pack(
        fill="x"
    )

    def create_card(
        parent,
        title,
        value,
        accent
    ):

        card = tk.Frame(
            parent,
            bg=WHITE,
            height=72
        )

        card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        card.pack_propagate(
            False
        )

        bar = tk.Frame(
            card,
            bg=accent,
            width=6
        )

        bar.pack(
            side="left",
            fill="y"
        )

        content = tk.Frame(
            card,
            bg=WHITE
        )

        content.pack(
            side="left",
            padx=14
        )

        value_label = tk.Label(
            content,
            text=value,
            font=("Segoe UI", 20, "bold"),
            bg=WHITE,
            fg=TEXT
        )

        value_label.pack(
            anchor="w"
        )

        tk.Label(
            content,
            text=title,
            font=("Segoe UI", 8),
            bg=WHITE,
            fg=MUTED
        ).pack(
            anchor="w"
        )

        return value_label

    total_value = create_card(
        stats,
        "TOTAL TASKS",
        "0",
        PRIMARY
    )

    pending_value = create_card(
        stats,
        "PENDING",
        "0",
        ORANGE
    )

    completed_value = create_card(
        stats,
        "COMPLETED",
        "0",
        GREEN
    )

    # =====================================================
    # PROGRESS
    # =====================================================

    progress_top = tk.Frame(
        main,
        bg=BG
    )

    progress_top.pack(
        fill="x",
        pady=(9, 2)
    )

    tk.Label(
        progress_top,
        text="Your Progress",
        font=("Segoe UI", 9, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(
        side="left"
    )

    progress_label = tk.Label(
        progress_top,
        text="0% Completed",
        font=("Segoe UI", 9, "bold"),
        bg=BG,
        fg=PRIMARY
    )

    progress_label.pack(
        side="right"
    )

    progress_bar = ttk.Progressbar(
        main,
        orient="horizontal",
        mode="determinate",
        maximum=100
    )

    progress_bar.pack(
        fill="x",
        pady=(0, 10)
    )

    # =====================================================
    # CONTENT
    # =====================================================

    content = tk.Frame(
        main,
        bg=BG
    )

    content.pack(
        fill="both",
        expand=True
    )

    # =====================================================
    # LEFT CREATE PANEL
    # =====================================================

    left = tk.Frame(
        content,
        bg=WHITE,
        width=300
    )

    left.pack(
        side="left",
        fill="y",
        padx=(0, 10)
    )

    left.pack_propagate(
        False
    )

    tk.Label(
        left,
        text="Create Task",
        font=("Segoe UI", 16, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 2)
    )

    tk.Label(
        left,
        text="Add details to your task.",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 10)
    )

    # Task
    tk.Label(
        left,
        text="TASK",
        font=("Segoe UI", 8, "bold"),
        bg=WHITE,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=20
    )

    task_entry = tk.Entry(
        left,
        font=("Segoe UI", 10),
        bg="#F4F5FA",
        fg=TEXT,
        relief="flat"
    )

    task_entry.pack(
        fill="x",
        padx=20,
        pady=(4, 10),
        ipady=8
    )

    # Category
    tk.Label(
        left,
        text="CATEGORY",
        font=("Segoe UI", 8, "bold"),
        bg=WHITE,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=20
    )

    category_combo = ttk.Combobox(
        left,
        values=[
            "Study",
            "Work",
            "Personal",
            "College",
            "Health",
            "Shopping",
            "General"
        ],
        state="readonly"
    )

    category_combo.set(
        "Study"
    )

    category_combo.pack(
        fill="x",
        padx=20,
        pady=(4, 10)
    )

    # Priority
    tk.Label(
        left,
        text="PRIORITY",
        font=("Segoe UI", 8, "bold"),
        bg=WHITE,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=20
    )

    priority_combo = ttk.Combobox(
        left,
        values=[
            "High",
            "Medium",
            "Low"
        ],
        state="readonly"
    )

    priority_combo.set(
        "Medium"
    )

    priority_combo.pack(
        fill="x",
        padx=20,
        pady=(4, 10)
    )

    # Due Date
    tk.Label(
        left,
        text="DUE DATE & TIME",
        font=("Segoe UI", 8, "bold"),
        bg=WHITE,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=20
    )

    due_entry = tk.Entry(
        left,
        font=("Segoe UI", 9),
        bg="#F4F5FA",
        fg=TEXT,
        relief="flat"
    )

    due_entry.pack(
        fill="x",
        padx=20,
        pady=(4, 2),
        ipady=8
    )

    tk.Label(
        left,
        text="Example: 10-10-2026 06:00 PM",
        font=("Segoe UI", 7),
        bg=WHITE,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=20
    )

    # Notes
    tk.Label(
        left,
        text="NOTES",
        font=("Segoe UI", 8, "bold"),
        bg=WHITE,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=20,
        pady=(9, 3)
    )

    notes_text = tk.Text(
        left,
        height=4,
        font=("Segoe UI", 9),
        bg="#F4F5FA",
        fg=TEXT,
        relief="flat",
        wrap="word"
    )

    notes_text.pack(
        fill="x",
        padx=20
    )

    # Add button
    tk.Button(
        left,
        text="＋  Add Task",
        font=("Segoe UI", 10, "bold"),
        bg=PRIMARY,
        fg=WHITE,
        activebackground=PRIMARY_DARK,
        relief="flat",
        cursor="hand2",
        command=add_task
    ).pack(
        fill="x",
        padx=20,
        pady=12,
        ipady=8
    )

    # =====================================================
    # RIGHT PANEL
    # =====================================================

    right = tk.Frame(
        content,
        bg=WHITE
    )

    right.pack(
        side="left",
        fill="both",
        expand=True
    )

    tk.Label(
        right,
        text="Your Tasks",
        font=("Segoe UI", 16, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=20,
        pady=(14, 2)
    )

    tk.Label(
        right,
        text="Search, filter and manage your tasks.",
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 6)
    )

    # =====================================================
    # SEARCH
    # =====================================================

    search_frame = tk.Frame(
        right,
        bg=WHITE
    )

    search_frame.pack(
        fill="x",
        padx=20,
        pady=(0, 6)
    )

    search_entry = tk.Entry(
        search_frame,
        font=("Segoe UI", 10),
        bg="#F4F5FA",
        fg=TEXT,
        relief="flat"
    )

    search_entry.pack(
        side="left",
        fill="x",
        expand=True,
        ipady=7
    )

    tk.Button(
        search_frame,
        text="🔍 Search",
        font=("Segoe UI", 9, "bold"),
        bg=PRIMARY,
        fg=WHITE,
        activebackground=PRIMARY_DARK,
        relief="flat",
        cursor="hand2",
        command=search_task
    ).pack(
        side="left",
        padx=6,
        ipadx=7,
        ipady=4
    )

    tk.Button(
        search_frame,
        text="All",
        font=("Segoe UI", 9, "bold"),
        bg="#EEF0F7",
        fg=TEXT,
        relief="flat",
        cursor="hand2",
        command=show_all
    ).pack(
        side="left",
        ipadx=7,
        ipady=4
    )

    # =====================================================
    # FILTERS
    # =====================================================

    filter_one = tk.Frame(
        right,
        bg=WHITE
    )

    filter_one.pack(
        fill="x",
        padx=20,
        pady=(0, 4)
    )

    def make_filter(
        parent,
        text,
        color,
        command
    ):

        tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 8, "bold"),
            bg=color,
            fg=TEXT,
            relief="flat",
            cursor="hand2",
            command=command
        ).pack(
            side="left",
            padx=(0, 5),
            ipadx=6,
            ipady=4
        )

    make_filter(
        filter_one,
        "All",
        "#EEF0F7",
        show_all
    )

    make_filter(
        filter_one,
        "📅 Today",
        LIGHT_BLUE,
        show_today
    )

    make_filter(
        filter_one,
        "🔮 Upcoming",
        LIGHT_PURPLE,
        show_upcoming
    )

    make_filter(
        filter_one,
        "⚠ Overdue",
        LIGHT_RED,
        show_overdue
    )

    filter_two = tk.Frame(
        right,
        bg=WHITE
    )

    filter_two.pack(
        fill="x",
        padx=20,
        pady=(0, 5)
    )

    make_filter(
        filter_two,
        "Pending",
        LIGHT_ORANGE,
        show_pending
    )

    make_filter(
        filter_two,
        "Completed",
        LIGHT_GREEN,
        show_completed
    )

    make_filter(
        filter_two,
        "🔥 High",
        LIGHT_RED,
        show_high
    )

    make_filter(
        filter_two,
        "↕ Due Date",
        "#EEF0F7",
        sort_due_date
    )

    # =====================================================
    # ACTION BUTTONS
    # =====================================================

    actions = tk.Frame(
        right,
        bg=WHITE
    )

    actions.pack(
        fill="x",
        padx=20,
        pady=(0, 7)
    )

    tk.Button(
        actions,
        text="✅ Complete",
        font=("Segoe UI", 9, "bold"),
        bg=GREEN,
        fg=WHITE,
        activebackground="#16A34A",
        relief="flat",
        cursor="hand2",
        command=complete_task
    ).pack(
        side="left",
        padx=(0, 4),
        ipadx=7,
        ipady=5
    )

    tk.Button(
        actions,
        text="👁 Details",
        font=("Segoe UI", 9, "bold"),
        bg=PRIMARY,
        fg=WHITE,
        activebackground=PRIMARY_DARK,
        relief="flat",
        cursor="hand2",
        command=view_details
    ).pack(
        side="left",
        padx=4,
        ipadx=7,
        ipady=5
    )

    tk.Button(
        actions,
        text="✏ Edit",
        font=("Segoe UI", 9, "bold"),
        bg=BLUE,
        fg=WHITE,
        activebackground="#2563EB",
        relief="flat",
        cursor="hand2",
        command=edit_task
    ).pack(
        side="left",
        padx=4,
        ipadx=7,
        ipady=5
    )

    tk.Button(
        actions,
        text="🗑 Delete",
        font=("Segoe UI", 9, "bold"),
        bg=RED,
        fg=WHITE,
        activebackground="#DC2626",
        relief="flat",
        cursor="hand2",
        command=delete_task
    ).pack(
        side="left",
        padx=4,
        ipadx=7,
        ipady=5
    )

    tk.Button(
        actions,
        text="❌ Clear All",
        font=("Segoe UI", 9, "bold"),
        bg=ORANGE,
        fg=TEXT,
        activebackground="#FBBF24",
        relief="flat",
        cursor="hand2",
        command=clear_all
    ).pack(
        side="right",
        ipadx=7,
        ipady=5
    )

    # =====================================================
    # TASK TABLE
    # =====================================================

    table_frame = tk.Frame(
        right,
        bg=WHITE
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 12)
    )

    columns = (
        "Task",
        "Category",
        "Priority",
        "Due Date",
        "Status"
    )

    task_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse",
        height=8
    )

    task_table.heading(
        "Task",
        text="TASK"
    )

    task_table.heading(
        "Category",
        text="CATEGORY"
    )

    task_table.heading(
        "Priority",
        text="PRIORITY"
    )

    task_table.heading(
        "Due Date",
        text="DUE DATE"
    )

    task_table.heading(
        "Status",
        text="STATUS"
    )

    task_table.column(
        "Task",
        width=200
    )

    task_table.column(
        "Category",
        width=85,
        anchor="center"
    )

    task_table.column(
        "Priority",
        width=75,
        anchor="center"
    )

    task_table.column(
        "Due Date",
        width=150,
        anchor="center"
    )

    task_table.column(
        "Status",
        width=100,
        anchor="center"
    )

    # Colors
    task_table.tag_configure(
        "high",
        background="#FFF0F0",
        foreground=TEXT
    )

    task_table.tag_configure(
        "medium",
        background="#FFF8E5",
        foreground=TEXT
    )

    task_table.tag_configure(
        "low",
        background="#EEF9F2",
        foreground=TEXT
    )

    task_table.tag_configure(
        "completed",
        background="#EAF9F0",
        foreground="#167C3A"
    )

    task_table.tag_configure(
        "overdue",
        background="#FFE7EB",
        foreground="#C6284A"
    )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=task_table.yview
    )

    task_table.configure(
        yscrollcommand=scrollbar.set
    )

    task_table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # =====================================================
    # DOUBLE CLICK = DETAILS
    # =====================================================

    task_table.bind(
        "<Double-1>",
        lambda event: view_details()
    )

    # =====================================================
    # ENTER = ADD
    # =====================================================

    window.bind(
        "<Return>",
        lambda event: add_task()
    )

    # =====================================================
    # LOAD
    # =====================================================

    refresh_table()

    task_entry.focus()

    window.after(
        2000,
        check_reminders
    )


# =========================================================
# START
# =========================================================

load_user()

load_tasks()

show_login()

window.mainloop()