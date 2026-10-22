import streamlit as st
import json
import os
import html
from datetime import datetime

st.set_page_config(
    page_title="My Task Tracker",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------- THEME --------------------
BG = "#F4F6FB"
PRIMARY = "#6C63FF"
PRIMARY_DARK = "#574FE0"
TEXT = "#252A3D"
MUTED = "#7A8198"
GREEN = "#20C879"
RED = "#EF476F"
ORANGE = "#F4A51C"
BLUE = "#3B82F6"
LIGHT_GREEN = "#EAF9F0"
LIGHT_RED = "#FFF0F2"
LIGHT_ORANGE = "#FFF7E3"
LIGHT_BLUE = "#EEF5FF"
LIGHT_PURPLE = "#F0EEFF"

TASK_FILE = "tasks.json"
USER_FILE = "user.json"
CATEGORIES = ["Study", "Work", "Personal", "College", "Health", "Shopping", "General"]
PRIORITIES = ["High", "Medium", "Low"]
FILTERS = ["All", "Today", "Upcoming", "Overdue", "Pending", "Completed", "High"]
DATE_FORMAT = "%d-%m-%Y %I:%M %p"


# -------------------- STORAGE --------------------
def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
    except (OSError, json.JSONDecodeError):
        pass
    return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except OSError:
        st.error(f"Could not save {path}. Check storage permissions.")
        return False


def normalize_tasks(data):
    result = []
    for item in data if isinstance(data, list) else []:
        if isinstance(item, dict):
            task = {
                "title": str(item.get("title", "Untitled Task")),
                "category": str(item.get("category", "General")),
                "priority": str(item.get("priority", "Medium")),
                "due_date": str(item.get("due_date", "No deadline") or "No deadline"),
                "date": str(item.get("date", "Old Task")),
                "status": str(item.get("status", "Pending")),
                "notes": str(item.get("notes", "")),
            }
        else:
            title = str(item)
            completed = title.startswith("✅ ")
            if completed:
                title = title[2:]
            priority = "Medium"
            for label in ("High", "Medium", "Low"):
                prefix = f"[{label}]"
                if title.startswith(prefix):
                    priority = label
                    title = title[len(prefix):].strip()
                    break
            if "|" in title:
                title, created = title.split("|", 1)
                created = created.strip()
            else:
                created = "Old Task"
            task = {
                "title": title.strip(),
                "category": "General",
                "priority": priority,
                "due_date": "No deadline",
                "date": created,
                "status": "Completed" if completed else "Pending",
                "notes": "",
            }
        if task["priority"] not in PRIORITIES:
            task["priority"] = "Medium"
        if task["category"] not in CATEGORIES:
            task["category"] = "General"
        if task["status"] not in ("Pending", "Completed"):
            task["status"] = "Pending"
        result.append(task)
    return result


if "tasks" not in st.session_state:
    st.session_state.tasks = normalize_tasks(load_json(TASK_FILE, []))
if "username" not in st.session_state:
    user_data = load_json(USER_FILE, {"username": "User"})
    st.session_state.username = (
        str(user_data.get("username", "User") or "User")
        if isinstance(user_data, dict) else "User"
    )
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None


def save_tasks():
    return save_json(TASK_FILE, st.session_state.tasks)


def save_user(name):
    st.session_state.username = name
    return save_json(USER_FILE, {"username": name})


# -------------------- DATE / STATUS HELPERS --------------------
def parse_due(task):
    value = task.get("due_date", "No deadline")
    if not value or value == "No deadline":
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (ValueError, TypeError):
        return None


def is_overdue(task):
    due = parse_due(task)
    return task.get("status", "Pending") != "Completed" and due is not None and due < datetime.now()


def is_today(task):
    due = parse_due(task)
    return due is not None and due.date() == datetime.now().date()


def is_upcoming(task):
    due = parse_due(task)
    return task.get("status", "Pending") != "Completed" and due is not None and due > datetime.now()


def status_text(task):
    if task.get("status") == "Completed":
        return "✓ Completed"
    if is_overdue(task):
        return "⚠ Overdue"
    return "○ Pending"


def safe(value):
    return html.escape(str(value))


def priority_color(priority):
    return {"High": RED, "Medium": ORANGE, "Low": GREEN}.get(priority, MUTED)


def status_color(task):
    if task.get("status") == "Completed":
        return GREEN
    if is_overdue(task):
        return RED
    return ORANGE


# -------------------- ORIGINAL-INSPIRED CSS --------------------
st.markdown(
    f"""
    <style>
    :root {{
        --primary: {PRIMARY};
        --background: {BG};
        --text: {TEXT};
        --muted: {MUTED};
    }}
    .stApp {{ background: var(--background); color: var(--text); }}
    .block-container {{ max-width: 1500px; padding-top: 1rem; padding-bottom: 2rem; }}
    h1, h2, h3 {{ color: var(--text); letter-spacing: -0.4px; }}
    p, label, .stMarkdown {{ color: var(--text); }}
    .topbar {{
        background: linear-gradient(120deg, #6C63FF, #8179FF);
        color: white; padding: 24px 28px; border-radius: 0;
        margin: -1rem -1rem 18px -1rem;
        box-shadow: 0 5px 18px rgba(108, 99, 255, 0.12);
    }}
    .topbar h1 {{ color: white !important; font-size: 30px; margin: 0 0 6px 0; }}
    .topbar p {{ color: #F0EEFF !important; margin: 0; }}
    .stat-card {{
        background: white; border-left: 6px solid var(--accent);
        border-radius: 0; padding: 16px 20px; min-height: 88px;
        box-shadow: none; border-top: 1px solid #E8EAF3;
        border-right: 1px solid #E8EAF3; border-bottom: 1px solid #E8EAF3;
    }}
    .stat-number {{ font-size: 30px; font-weight: 750; color: var(--text); line-height: 1.25; }}
    .stat-label {{ font-size: 11px; font-weight: 700; color: var(--muted); margin-top: 5px; }}
    .panel-title {{ font-size: 23px; font-weight: 750; margin: 0 0 2px 0; color: {TEXT}; }}
    .section-caption {{ color: {MUTED}; font-size: 13px; margin: 0 0 14px 0; }}
    .panel {{
        background: white; border: 1px solid #E8EAF3;
        padding: 16px 18px; min-height: 100%;
    }}
    .pill {{
        display: inline-block; padding: 4px 9px; margin: 4px 4px 0 0;
        border-radius: 3px; font-size: 11px; font-weight: 700;
    }}
    .stButton > button, .stFormSubmitButton > button {{
        border-radius: 3px; font-weight: 650; min-height: 39px;
        transition: all 0.15s ease;
    }}
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
        background: {PRIMARY}; border-color: {PRIMARY}; color: white;
    }}
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
        background: {PRIMARY_DARK}; border-color: {PRIMARY_DARK}; color: white;
    }}
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {{ border-radius: 3px; }}
    div[data-testid="stProgressBar"] > div > div {{ background-color: {PRIMARY}; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: white; border: 1px solid #E8EAF3; border-radius: 2px;
    }}
    div[data-testid="stDataFrame"] {{ border: 1px solid #B9B9B9; }}
    hr {{ border-color: #E3E6F0; }}
    @media (max-width: 800px) {{
        .block-container {{ padding: 0.7rem 0.6rem 1.5rem 0.6rem; }}
        .topbar {{ padding: 18px; margin: -0.7rem -0.6rem 14px -0.6rem; }}
        .topbar h1 {{ font-size: 24px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- HEADER --------------------
header_left, header_right = st.columns([4, 1])
with header_left:
    st.markdown(
        f"""
        <div class="topbar">
            <h1>✓ My Task Tracker</h1>
            <p>Welcome, {safe(st.session_state.username)} 👋</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown(
        f"<div style='text-align:right;padding:20px 3px;color:{MUTED};font-size:13px'>"
        f"{datetime.now().strftime('%A, %d %B %Y')}</div>",
        unsafe_allow_html=True,
    )

with st.expander("⚙ Change username"):
    with st.form("username_form"):
        new_username = st.text_input("Your name", value=st.session_state.username)
        if st.form_submit_button("Save username", type="primary"):
            if new_username.strip():
                save_user(new_username.strip())
                st.rerun()
            else:
                st.warning("Please enter a name.")


# -------------------- STATISTICS --------------------
tasks = st.session_state.tasks
total = len(tasks)
completed = sum(task.get("status") == "Completed" for task in tasks)
pending = total - completed
percent = round(completed / total * 100) if total else 0

st.markdown("###")
stats = [
    ("TOTAL TASKS", total, PRIMARY),
    ("PENDING", pending, ORANGE),
    ("COMPLETED", completed, GREEN),
]
stat_cols = st.columns(3, gap="small")
for col, (label, value, color) in zip(stat_cols, stats):
    with col:
        st.markdown(
            f"""
            <div class="stat-card" style="--accent:{color}">
                <div class="stat-number">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")
progress_left, progress_right = st.columns([3, 1])
with progress_left:
    st.markdown("**Your Progress**")
with progress_right:
    st.markdown(
        f"<div style='text-align:right;color:{PRIMARY};font-weight:750'>{percent}% Completed</div>",
        unsafe_allow_html=True,
    )
st.progress(percent / 100)
st.write("")


# -------------------- CREATE TASK + TASK LIST --------------------
form_col, list_col = st.columns([0.95, 2.3], gap="small")

with form_col:
    st.markdown('<div class="panel-title">Create Task</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Add details to your task.</div>', unsafe_allow_html=True)
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("TASK", placeholder="What do you need to do?")
        category = st.selectbox("CATEGORY", CATEGORIES)
        priority = st.selectbox("PRIORITY", PRIORITIES, index=1)
        due_date = st.text_input("DUE DATE & TIME", placeholder="10-10-2026 06:00 PM")
        st.caption("Example: 10-10-2026 06:00 PM. Leave blank for no deadline.")
        notes = st.text_area("NOTES", height=100)
        add = st.form_submit_button("＋ Add Task", use_container_width=True, type="primary")

    if add:
        if not title.strip():
            st.warning("Please enter a task first.")
        else:
            due_text = due_date.strip() or "No deadline"
            if due_text != "No deadline":
                try:
                    datetime.strptime(due_text, DATE_FORMAT)
                except ValueError:
                    st.error("Invalid date. Use DD-MM-YYYY HH:MM AM/PM, e.g. 10-10-2026 06:00 PM.")
                    st.stop()
            st.session_state.tasks.append({
                "title": title.strip(),
                "category": category,
                "priority": priority,
                "due_date": due_text,
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "status": "Pending",
                "notes": notes.strip(),
            })
            save_tasks()
            st.rerun()


with list_col:
    st.markdown('<div class="panel-title">Your Tasks</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Search, filter and manage your tasks.</div>', unsafe_allow_html=True)

    search_col, search_button_col, all_col = st.columns([5, 1, 0.7], gap="small")
    with search_col:
        search = st.text_input(" ", placeholder="Search title, notes, category...", label_visibility="collapsed", key="task_search")
    with search_button_col:
        st.markdown("<div style='height:1px'></div>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
    with all_col:
        st.markdown("<div style='height:1px'></div>", unsafe_allow_html=True)
        show_all_clicked = st.button("All", use_container_width=True)

    filter_row_1 = st.columns(4, gap="small")
    filter_row_2 = st.columns(4, gap="small")
    filter_buttons = [
        ("All", filter_row_1[0]), ("📅 Today", filter_row_1[1]),
        ("🔮 Upcoming", filter_row_1[2]), ("⚠ Overdue", filter_row_1[3]),
        ("Pending", filter_row_2[0]), ("Completed", filter_row_2[1]),
        ("🔥 High", filter_row_2[2]), ("↕ Due Date", filter_row_2[3]),
    ]
    if "filter_choice" not in st.session_state:
        st.session_state.filter_choice = "All"
    for label, col in filter_buttons:
        with col:
            key = "filter_" + label.replace(" ", "_").replace("📅", "today").replace("🔮", "upcoming").replace("⚠", "overdue").replace("🔥", "high").replace("↕", "due")
            if st.button(label, key=key, use_container_width=True):
                if label == "📅 Today":
                    st.session_state.filter_choice = "Today"
                elif label == "🔮 Upcoming":
                    st.session_state.filter_choice = "Upcoming"
                elif label == "⚠ Overdue":
                    st.session_state.filter_choice = "Overdue"
                elif label == "🔥 High":
                    st.session_state.filter_choice = "High"
                elif label == "↕ Due Date":
                    st.session_state.filter_choice = "Due Date"
                else:
                    st.session_state.filter_choice = label
                st.rerun()

    if show_all_clicked:
        st.session_state.filter_choice = "All"
        st.session_state.task_search = ""
        st.rerun()
    if search_clicked:
        st.session_state.filter_choice = st.session_state.filter_choice or "All"

    query = search.strip().lower()
    visible = []
    for idx, task in enumerate(st.session_state.tasks):
        searchable = " ".join([
            str(task.get("title", "")), str(task.get("category", "")),
            str(task.get("priority", "")), str(task.get("status", "")),
            str(task.get("notes", "")),
        ]).lower()
        if query and query not in searchable:
            continue
        choice = st.session_state.filter_choice
        if choice == "Today" and not is_today(task):
            continue
        if choice == "Upcoming" and not is_upcoming(task):
            continue
        if choice == "Overdue" and not is_overdue(task):
            continue
        if choice == "Pending" and task.get("status") != "Pending":
            continue
        if choice == "Completed" and task.get("status") != "Completed":
            continue
        if choice == "High" and task.get("priority") != "High":
            continue
        visible.append((idx, task))

    if st.session_state.filter_choice == "Due Date":
        visible.sort(key=lambda pair: parse_due(pair[1]) or datetime.max)
    st.caption(f"Showing {len(visible)} of {len(st.session_state.tasks)} tasks")

    # Table-like view matching the original Treeview
    if visible:
        table_rows = []
        for idx, task in visible:
            table_rows.append({
                "TASK": task.get("title", "Untitled Task"),
                "CATEGORY": task.get("category", "General"),
                "PRIORITY": task.get("priority", "Medium"),
                "DUE DATE": task.get("due_date", "No deadline"),
                "STATUS": status_text(task),
            })
        st.dataframe(table_rows, hide_index=True, use_container_width=True, height=250)

        selected_options = [idx for idx, _ in visible]
        selected_labels = {
            idx: f"{st.session_state.tasks[idx].get('title', 'Untitled Task')}  ·  "
                 f"{st.session_state.tasks[idx].get('category', 'General')}  ·  "
                 f"{st.session_state.tasks[idx].get('status', 'Pending')}  (#{idx + 1})"
            for idx in selected_options
        }
        selected_idx = st.selectbox(
            "Select a task for actions",
            options=selected_options,
            format_func=lambda idx: selected_labels[idx],
            key="selected_task_idx",
        )

        action_cols = st.columns([1, 1, 1, 1, 1.2], gap="small")
        with action_cols[0]:
            if st.button("✓ Complete", key="complete_selected", use_container_width=True, type="primary"):
                if st.session_state.tasks[selected_idx].get("status") != "Completed":
                    st.session_state.tasks[selected_idx]["status"] = "Completed"
                    save_tasks()
                    st.rerun()
                else:
                    st.info("This task is already completed.")
        with action_cols[1]:
            details_clicked = st.button("👁 Details", key="details_selected", use_container_width=True)
        with action_cols[2]:
            if st.button("✎ Edit", key="edit_selected", use_container_width=True):
                st.session_state.edit_index = selected_idx
                st.rerun()
        with action_cols[3]:
            if st.button("▣ Delete", key="delete_selected", use_container_width=True):
                st.session_state.confirm_delete = selected_idx
                st.rerun()
        with action_cols[4]:
            if st.button("✕ Clear All", key="clear_all", use_container_width=True):
                st.session_state.confirm_clear = True
                st.rerun()

        if details_clicked:
            st.session_state.details_index = selected_idx
        if st.session_state.get("details_index") == selected_idx:
            task = st.session_state.tasks[selected_idx]
            with st.expander("Task Details", expanded=True):
                st.markdown(f"**{safe(task.get('title', 'Untitled Task'))}**")
                detail_cols = st.columns(2)
                with detail_cols[0]:
                    st.write("**Category:**", task.get("category", "General"))
                    st.write("**Priority:**", task.get("priority", "Medium"))
                    st.write("**Due date:**", task.get("due_date", "No deadline"))
                with detail_cols[1]:
                    st.write("**Status:**", task.get("status", "Pending"))
                    st.write("**Created:**", task.get("date", "Unknown"))
                st.write("**Notes:**", task.get("notes", "") or "No notes added.")

        if st.session_state.edit_index is not None:
            edit_idx = st.session_state.edit_index
            if 0 <= edit_idx < len(st.session_state.tasks):
                task = st.session_state.tasks[edit_idx]
                st.markdown("#### Edit selected task")
                with st.form(f"edit_form_{edit_idx}"):
                    edit_title = st.text_input("TASK", value=task.get("title", ""))
                    cat = task.get("category", "General")
                    pri = task.get("priority", "Medium")
                    edit_category = st.selectbox("CATEGORY", CATEGORIES, index=CATEGORIES.index(cat) if cat in CATEGORIES else 6)
                    edit_priority = st.selectbox("PRIORITY", PRIORITIES, index=PRIORITIES.index(pri) if pri in PRIORITIES else 1)
                    edit_due = st.text_input("DUE DATE & TIME", value=task.get("due_date", "No deadline"))
                    edit_notes = st.text_area("NOTES", value=task.get("notes", ""), height=90)
                    save_edit = st.form_submit_button("✓ Save Changes", type="primary")
                cancel_col, _ = st.columns([1, 4])
                with cancel_col:
                    cancel_edit = st.button("Cancel edit", key="cancel_edit")
                if cancel_edit:
                    st.session_state.edit_index = None
                    st.rerun()
                if save_edit:
                    if not edit_title.strip():
                        st.error("Task name cannot be empty.")
                    else:
                        due_text = edit_due.strip() or "No deadline"
                        valid = due_text == "No deadline"
                        if not valid:
                            try:
                                datetime.strptime(due_text, DATE_FORMAT)
                                valid = True
                            except ValueError:
                                st.error("Use DD-MM-YYYY HH:MM AM/PM or No deadline.")
                        if valid:
                            st.session_state.tasks[edit_idx].update({
                                "title": edit_title.strip(),
                                "category": edit_category,
                                "priority": edit_priority,
                                "due_date": due_text,
                                "notes": edit_notes.strip(),
                            })
                            save_tasks()
                            st.session_state.edit_index = None
                            st.success("Task updated!")
                            st.rerun()
    else:
        st.info("No tasks found. Add a task or change the filter.")
        if st.button("✕ Clear All", key="clear_all_empty"):
            st.session_state.confirm_clear = True
            st.rerun()


# -------------------- CONFIRMATIONS --------------------
delete_value = st.session_state.confirm_delete
if delete_value is not False and delete_value is not None:
    if isinstance(delete_value, int) and 0 <= delete_value < len(st.session_state.tasks):
        st.warning(f"Delete '{st.session_state.tasks[delete_value].get('title', 'this task')}'?")
        yes_col, no_col = st.columns(2)
        with yes_col:
            if st.button("Yes, delete task", type="primary", key="confirm_delete_yes"):
                st.session_state.tasks.pop(delete_value)
                save_tasks()
                st.session_state.confirm_delete = False
                st.session_state.edit_index = None
                st.rerun()
        with no_col:
            if st.button("Cancel delete", key="confirm_delete_no"):
                st.session_state.confirm_delete = False
                st.rerun()

if st.session_state.confirm_clear:
    st.warning("Are you sure you want to delete ALL tasks?")
    yes_col, no_col = st.columns(2)
    with yes_col:
        if st.button("Yes, clear all tasks", type="primary", key="confirm_clear_yes"):
            st.session_state.tasks.clear()
            save_tasks()
            st.session_state.confirm_clear = False
            st.session_state.confirm_delete = False
            st.session_state.edit_index = None
            st.rerun()
    with no_col:
        if st.button("Cancel clear", key="confirm_clear_no"):
            st.session_state.confirm_clear = False
            st.rerun()


# -------------------- FOOTER --------------------
st.divider()
st.markdown(
    f"<div style='text-align:center;color:{MUTED};font-size:12px;padding:10px'>"
    "✓ My Task Tracker • Stay organized, one task at a time.</div>",
    unsafe_allow_html=True,
)
