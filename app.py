import html
import time
from datetime import date, timedelta
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from planner import build_schedule, score_task, summarize_schedule, unplanned_minutes
from storage import TaskStore
from mailer import build_plan_email, send_message

st.set_page_config(
    page_title="StudyFlow AI | Smart Study Planner",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#17243a; --muted:#68778d; --line:#e5ebf3; --blue:#315efb; --teal:#18a999; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:#f5f7fb; color:var(--ink); }
.block-container { padding-top:1.35rem; padding-bottom:2.5rem; max-width:1500px; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #e8edf5; }
.hero { background:linear-gradient(120deg,#152c55 0%,#294fc4 60%,#18a999 130%); padding:1.7rem 1.85rem; border-radius:22px; color:white; box-shadow:0 12px 32px rgba(39,75,170,.16); margin-bottom:1.1rem; }
.hero-kicker { font-size:.76rem; letter-spacing:.15em; text-transform:uppercase; color:#cddaff; font-weight:700; }
.hero h1 { font-family:'Manrope',sans-serif; color:white; font-size:2.15rem; line-height:1.2; margin:.45rem 0 .55rem; }
.hero p { color:#e9efff; margin:0; font-size:1rem; }
.pill { display:inline-block; border:1px solid rgba(255,255,255,.28); background:rgba(255,255,255,.12); padding:.35rem .7rem; border-radius:999px; font-size:.8rem; margin-top:1rem; }
.metric-card { background:white; border:1px solid #e7ecf4; border-radius:16px; padding:1rem 1.1rem; min-height:112px; box-shadow:0 4px 14px rgba(20,40,80,.025); }
.metric-label { color:#7b879a; font-size:.75rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase; }
.metric-value { font-family:'Manrope',sans-serif; color:#17243a; font-size:1.8rem; font-weight:800; margin:.3rem 0 .1rem; }
.metric-note { color:#8a95a7; font-size:.78rem; }
.panel { background:white; border:1px solid #e7ecf4; border-radius:18px; padding:1.1rem 1.2rem; }
.section-title { font-family:'Manrope',sans-serif; font-size:1.15rem; font-weight:800; color:#17243a; margin:.45rem 0 .25rem; }
.section-sub { color:#718096; font-size:.9rem; margin-bottom:.9rem; }
.task-chip { display:inline-block; padding:.25rem .55rem; background:#edf2ff; color:#315efb; border-radius:8px; font-size:.78rem; font-weight:700; }
.stButton > button, .stDownloadButton > button { border-radius:10px; font-weight:700; min-height:2.55rem; }
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] { border-radius:10px; }
[data-testid="stDataFrame"] { border:1px solid #e7ecf4; border-radius:12px; overflow:hidden; }
hr { border-color:#e5ebf3; }
footer {visibility:hidden;}
/* Accessibility and colour-contrast refinements */
:root { color-scheme: light; --ink:#17243a; --muted:#52627a; --line:#dbe4f0; --blue:#2453d4; --teal:#087f73; }
.stApp, [data-testid="stAppViewContainer"] { background:#f4f7fc; color:#17243a; }
[data-testid="stSidebar"] > div:first-child { background:#ffffff; }
[data-testid="stSidebar"] *, .stMarkdown, .stText, label,
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p { color:#24344d; }
.stCaption, [data-testid="stCaptionContainer"] { color:#53647c !important; }
/* Inputs remain white with dark text for reliable readability. */
.stTextInput input, .stNumberInput input, .stDateInput input,
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea,
[data-baseweb="select"] > div { background:#ffffff !important; color:#17243a !important; border-color:#cbd7e6 !important; }
.stTextInput input::placeholder, [data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder { color:#687991 !important; opacity:1; }
[data-baseweb="select"] *, [role="listbox"], [role="option"] { color:#17243a !important; }
[role="option"] { background:#ffffff !important; }
[role="option"]:hover, [aria-selected="true"][role="option"] { background:#eaf0ff !important; }
input:focus, textarea:focus, [data-baseweb="select"] > div:focus-within { outline:2px solid #315efb !important; outline-offset:1px; }
/* Clear, high-contrast buttons and visible keyboard focus. */
.stButton > button, .stDownloadButton > button { border:1px solid #c6d3e5; color:#1e355b; background:#ffffff; transition:all .15s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:#2453d4; color:#173b9a; background:#edf3ff; }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background:#2453d4 !important; color:#ffffff !important; border:1px solid #2453d4 !important; }
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover { background:#193fAD !important; color:#ffffff !important; }
button:focus-visible, a:focus-visible { outline:3px solid #f0a202 !important; outline-offset:2px !important; }
/* Use darker, readable text on cards and status messages. */
.metric-label { color:#52627a; }
.metric-note { color:#53647c; }
.section-sub { color:#52627a; }
.task-chip { background:#e7eeff; color:#234bb5; }
[data-testid="stAlert"] { border-radius:12px; }
[data-testid="stDataFrame"] { background:#ffffff; border:1px solid #dbe4f0; border-radius:12px; overflow:hidden; }
[data-testid="stProgressBar"] > div > div { background:#2453d4; }
hr { border-color:#dbe4f0; }
@media (max-width: 700px) {
  .block-container { padding-left:1rem; padding-right:1rem; }
  .hero { padding:1.25rem; border-radius:16px; }
  .hero h1 { font-size:1.65rem; }
  .metric-card { padding:.85rem; min-height:100px; }
  .metric-value { font-size:1.5rem; }
}

/* ---------- Mobile / touch support (Android + iOS) ---------- */
.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; }
.tcard, .daycard { background:#fff; border:1px solid #dbe4f0; border-radius:14px; padding:.8rem .95rem; margin-bottom:.6rem; }
.tcard.done { opacity:.7; }
.tcard-top, .day-head, .sess { display:flex; justify-content:space-between; align-items:center; gap:.6rem; }
.tcard-title { font-weight:700; color:#17243a; margin:.4rem 0 .15rem; overflow-wrap:anywhere; }
.tcard-meta { color:#52627a; font-size:.82rem; overflow-wrap:anywhere; }
.badge { font-size:.74rem; font-weight:700; padding:.2rem .5rem; border-radius:8px; background:#eef2f8; color:#33445f; white-space:nowrap; }
.badge.hot { background:#ffe9e6; color:#a3281b; }
.badge.ok { background:#e2f6ee; color:#0b6b4f; }
.day-head { border-bottom:1px solid #e5ebf3; padding-bottom:.4rem; margin-bottom:.4rem; color:#17243a; }
.sess { padding:.35rem 0; }
.sess + .sess { border-top:1px dashed #e5ebf3; }
[data-baseweb="tab-list"] { overflow-x:auto; -webkit-overflow-scrolling:touch; }
button[data-baseweb="tab"] { min-height:44px; padding:.5rem .85rem; }
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button { min-height:2.9rem; touch-action:manipulation; }
html { -webkit-text-size-adjust:100%; }
@media (max-width: 700px) {
  .block-container { padding-top:3.5rem; padding-left:max(.9rem, env(safe-area-inset-left)); padding-right:max(.9rem, env(safe-area-inset-right)); padding-bottom:max(2rem, env(safe-area-inset-bottom)); }
  .metric-grid { grid-template-columns:repeat(2,1fr); gap:.6rem; }
  .metric-card { min-height:92px; }
  .hero-kicker { font-size:.68rem; }
  .pill { font-size:.74rem; }
  /* 16px inputs stop iOS Safari from zooming in when a field is tapped */
  input, textarea, [data-baseweb="select"] * { font-size:16px !important; }
  button[data-baseweb="tab"] { font-size:.88rem; padding:.5rem .7rem; }
}
</style>
""", unsafe_allow_html=True)

# Phone-friendly page settings: notch-safe viewport, home-screen app meta tags.
components.html("""<script>
try {
  const d = window.parent.document;
  const vp = d.querySelector('meta[name="viewport"]');
  if (vp) vp.setAttribute('content', 'width=device-width, initial-scale=1, viewport-fit=cover');
  [['mobile-web-app-capable','yes'],['apple-mobile-web-app-capable','yes'],
   ['apple-mobile-web-app-status-bar-style','default'],['apple-mobile-web-app-title','StudyFlow'],
   ['theme-color','#152c55']].forEach(([n,c]) => {
    if (!d.querySelector('meta[name="'+n+'"]')) { const m = d.createElement('meta'); m.name = n; m.content = c; d.head.appendChild(m); }
  });
} catch (e) {}
</script>""", height=0)


def esc(value):
    return html.escape(str(value))

# ---------- Accounts (Google sign-in) and storage ----------
def secret_section(name):
    """Return a section of Streamlit secrets as a dict, or {} if secrets are not set up."""
    try:
        if name in st.secrets:
            return dict(st.secrets[name])
    except Exception:
        pass
    return {}


@st.cache_resource(show_spinner=False)
def get_store(url):
    return TaskStore(url)


# Authentication is mandatory. Never fall back to demo mode, because that
# would allow visitors to reach the planner without signing in.
auth_settings = secret_section("auth")
google_settings = dict(auth_settings.get("google", {})) if auth_settings else {}
AUTH_CONFIGURED = bool(
    auth_settings.get("redirect_uri")
    and auth_settings.get("cookie_secret")
    and google_settings.get("client_id")
    and google_settings.get("client_secret")
    and google_settings.get("server_metadata_url")
)
signed_in = bool(AUTH_CONFIGURED and getattr(st.user, "is_logged_in", False))

if not AUTH_CONFIGURED:
    st.markdown('''
    <div class="hero">
      <div class="hero-kicker">STUDENT PRODUCTIVITY • SMART PLANNING</div>
      <h1>Welcome to StudyFlow AI</h1>
      <p>Your personal space to plan smarter, stay focused, and make progress.</p>
      <div class="pill">🔐 Google sign-in required</div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown("""
    <div class="panel">
      <h3 style="margin-top:0;color:#17243a">Sign-in setup required</h3>
      <p>StudyFlow AI is locked until Google authentication is configured. Add the required values to
      <code>.streamlit/secrets.toml</code> on your computer, or to your app's Secrets settings on Streamlit Community Cloud.</p>
      <p style="margin-bottom:0;color:#52627a">For setup instructions, open the Google sign-in section in README.md. No planner data is shown before sign-in.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not signed_in:
    st.markdown('''
    <div class="hero">
      <div class="hero-kicker">STUDENT PRODUCTIVITY • SMART PLANNING</div>
      <h1>Welcome to StudyFlow AI</h1>
      <p>One calm place to organize your subjects, plan your study time, and track your progress.</p>
      <div class="pill">✨ Smart priorities &nbsp; · &nbsp; ⏱ Focus sessions &nbsp; · &nbsp; 📈 Progress tracking</div>
    </div>
    ''', unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.15, 1])
    with center:
        st.markdown('''
        <div class="panel" style="text-align:center;padding:1.6rem 1.4rem">
          <div style="font-size:2.5rem;line-height:1.4">📘</div>
          <h2 style="color:#17243a;margin:.4rem 0">Your study space starts here</h2>
          <p style="color:#52627a;margin-bottom:1rem">Sign in securely with your Google account to access your planner and saved tasks.</p>
          <p style="font-size:.82rem;color:#52627a;margin-bottom:0">🔒 We use your Google name and email for your account. We do not access your Gmail inbox or see your password.</p>
        </div>
        ''', unsafe_allow_html=True)
        st.write("")
        if st.button("Continue with Google  →", type="primary", use_container_width=True):
            st.login("google")
        st.caption("By continuing, you’ll return to StudyFlow AI after Google verifies your account.")
    st.stop()

# Clear a stale demo flag from older versions of the app.
st.session_state.pop("demo_mode", None)

# The application below this point is only rendered for authenticated users.
OWNER = None
USER_NAME = ""
store = None
if signed_in:
    OWNER = str(getattr(st.user, "email", "") or "").strip().lower()
    USER_NAME = str(getattr(st.user, "name", "") or "")
    if not OWNER or getattr(st.user, "email_verified", True) is False:
        st.error("Google did not give us a verified e-mail address for this account, so we cannot sign you in.")
        if st.button("Sign out"):
            st.logout()
        st.stop()
    try:
        store = get_store(secret_section("database").get("url", ""))
        if not st.session_state.get("login_recorded"):
            store.record_login(OWNER, USER_NAME)
            st.session_state.login_recorded = True
    except Exception:
        store = None
        st.error("Storage is not available right now, so your tasks will not be saved in this session. "
                 "If you run this app yourself, check the [database] settings in the README.")

PERSIST = bool(store and OWNER)
SAVE_ERROR = "We could not reach the storage right now, so that change was not saved. Please try again in a moment."


def reload_tasks():
    st.session_state.tasks = store.list_tasks(OWNER)


def add_task(task):
    """Add a task (saved to storage when signed in). Returns True on success."""
    if PERSIST:
        try:
            store.add_task(OWNER, task)
            reload_tasks()
        except ValueError as exc:
            st.warning(str(exc))
            return False
        except Exception:
            st.error(SAVE_ERROR)
            return False
    else:
        st.session_state.tasks.append(dict(task, completed=False))
    st.session_state.pop("schedule", None)
    return True


def set_task_status(index, completed):
    task = st.session_state.tasks[index]
    if PERSIST:
        try:
            store.set_completed(OWNER, task["id"], completed)
            reload_tasks()
        except Exception:
            st.error(SAVE_ERROR)
            return False
    else:
        task["completed"] = completed
    st.session_state.pop("schedule", None)
    return True


def remove_task(index):
    task = st.session_state.tasks[index]
    if PERSIST:
        try:
            store.delete_task(OWNER, task["id"])
            reload_tasks()
        except Exception:
            st.error(SAVE_ERROR)
            return False
    else:
        st.session_state.tasks.pop(index)
    st.session_state.pop("schedule", None)
    return True


def replace_tasks(new_tasks):
    st.session_state.tasks = [dict(t, completed=False) for t in new_tasks]
    st.session_state.pop("schedule", None)


# ---------- Initial state ----------
if PERSIST:
    if st.session_state.get("tasks_owner") != OWNER:
        try:
            reload_tasks()
            st.session_state.tasks_owner = OWNER
            st.session_state.pop("schedule", None)
        except Exception:
            st.session_state.tasks = []
            st.error(SAVE_ERROR)
elif "tasks" not in st.session_state:
    seed_day = date.today()
    st.session_state.tasks = [
        {"subject":"Mathematics", "task":"Practice algebra problems", "deadline":seed_day + timedelta(days=2), "hours":2.0, "difficulty":"Hard", "importance":"High", "completed":False},
        {"subject":"Science", "task":"Revise electricity chapter", "deadline":seed_day + timedelta(days=4), "hours":1.5, "difficulty":"Medium", "importance":"High", "completed":False},
        {"subject":"English", "task":"Prepare poem notes", "deadline":seed_day + timedelta(days=1), "hours":1.0, "difficulty":"Easy", "importance":"Normal", "completed":False},
    ]

# Keep older saved-in-session task shapes compatible.
for task in st.session_state.tasks:
    task.setdefault("completed", False)

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="hero-kicker">STUDENT PRODUCTIVITY • SMART PLANNING</div>
  <h1>Make every study session count.</h1>
  <p>Organize assignments, understand priorities, and build a manageable study routine.</p>
  <div class="pill">✨ Smart priorities &nbsp; · &nbsp; ⏱ Focus sessions &nbsp; · &nbsp; 📈 Progress tracking</div>
</div>
""", unsafe_allow_html=True)


# ---------- Account and storage status ----------
acct_info, acct_action = st.columns([4, 1])
with acct_info:
    if signed_in:
        st.markdown(f"👤 Signed in as `{OWNER}`")
        if PERSIST and store.is_permanent:
            st.caption(f"💾 Your tasks are saved automatically · {store.label}")
        elif PERSIST:
            st.caption(f"💾 Your tasks are saved automatically · {store.label}. "
                       "On free cloud hosting this file can be erased when the app restarts - see the README to add a cloud database.")
with acct_action:
    if signed_in:
        if st.button("Sign out", use_container_width=True):
            st.logout()

if PERSIST:
    with st.expander("🔐 Privacy & my data"):
        st.write("Stored for your account: your e-mail address, your name, and the tasks you add. "
                 "Your Gmail inbox is never read. Other users cannot see your tasks.")
        confirm_delete = st.checkbox("I understand this permanently deletes all my saved data")
        if st.button("Delete my saved data", disabled=not confirm_delete):
            try:
                store.delete_user_data(OWNER)
                st.session_state.login_recorded = False
                reload_tasks()
                st.session_state.pop("schedule", None)
                st.success("Your saved tasks and profile were deleted.")
            except Exception:
                st.error(SAVE_ERROR)

# ---------- Plan settings (in the main page so phones can reach them easily) ----------
with st.expander("⚙️ Plan settings", expanded=False):
    today = st.date_input("Planning start date", value=date.today(), help="The first day of your suggested timetable.")
    planning_days = st.slider("Plan length", min_value=3, max_value=14, value=7, format="%d days", help="How far ahead to create your study plan.")
    daily_minutes = st.slider("Study time available each day", min_value=30, max_value=300, value=120, step=15, format="%d minutes", help="Choose a realistic amount after school and other activities.")
    session_minutes = st.select_slider("Focus session length", options=[15,20,25,30,40,45,60], value=30, format_func=lambda x:f"{x} minutes", help="Short focus blocks can make it easier to begin a task.")
    st.caption("Tip: choose a study time you can realistically keep. This is a rule-based, AI-inspired prototype and does not use a paid AI service.")

all_tasks = st.session_state.tasks
open_tasks = [t for t in all_tasks if not t.get("completed", False)]
completed_tasks = [t for t in all_tasks if t.get("completed", False)]
urgent_count = sum(1 for task in open_tasks if (task["deadline"] - today).days <= 2)
total_effort = round(sum(float(task["hours"]) for task in open_tasks), 1)
subject_count = len(set(task["subject"] for task in all_tasks))
completion_pct = int(100 * len(completed_tasks) / len(all_tasks)) if all_tasks else 0

metric_values = [
    ("TOTAL TASKS", str(len(all_tasks)), "Everything you have added"),
    ("DUE SOON", str(urgent_count), "Open tasks due within 2 days"),
    ("TIME TO PLAN", f"{total_effort} h", "Estimated time remaining"),
    ("COMPLETED", f"{len(completed_tasks)} / {len(all_tasks)}", f"{completion_pct}% complete"),
]
cards_html = "".join(f'<div class="metric-card"><div class="metric-label">{l}</div><div class="metric-value">{v}</div><div class="metric-note">{n}</div></div>' for l, v, n in metric_values)
st.markdown(f'<div class="metric-grid">{cards_html}</div>', unsafe_allow_html=True)

st.write("")
tab_home, tab_tasks, tab_schedule, tab_progress = st.tabs(["🏠 Home", "📝 Tasks", "🗓️ Plan", "📈 Progress"])

with tab_home:
    st.markdown('<div class="section-title">Your next best steps</div><div class="section-sub">A quick view of what to focus on today.</div>', unsafe_allow_html=True)
    home_left, home_right = st.columns([1.2, 1], gap="large")
    with home_left:
        if not open_tasks:
            st.success("Great work! You have no open tasks. Add a new task whenever you receive an assignment.")
        else:
            ranked = sorted(open_tasks, key=lambda t:(-score_task(t, today), t["deadline"]))
            for rank, task in enumerate(ranked[:3], start=1):
                days_left = (task["deadline"] - today).days
                due = "Overdue" if days_left < 0 else ("Due today" if days_left == 0 else (f"Due in {days_left} day(s)"))
                st.markdown(f'<div class="panel" style="margin-bottom:.65rem"><span class="task-chip">PRIORITY {rank}</span><h3 style="margin:.55rem 0 .2rem;color:#17243a;overflow-wrap:anywhere">{esc(task["task"])}</h3><p style="margin:0;color:#52627a">{esc(task["subject"])} · {due} · {task["hours"]} hour(s)</p></div>', unsafe_allow_html=True)
    with home_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("#### 📌 Completion progress")
        st.progress(completion_pct / 100 if all_tasks else 0)
        st.write(f"**{completion_pct}%** of your tasks marked complete")
        st.caption("Mark a task complete in the Tasks & priorities tab to update your progress.")
        st.divider()
        st.markdown("#### ⏰ Your planning settings")
        st.write(f"- **Plan length:** {planning_days} days")
        st.write(f"- **Daily study time:** {daily_minutes} minutes")
        st.write(f"- **Focus block:** {session_minutes} minutes")
        st.markdown('</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### How to get started")
        st.markdown("1. Add your assignments.\n2. Set a realistic deadline and effort estimate.\n3. Generate a schedule.\n4. Mark tasks complete as you finish them.")
    with c2:
        st.markdown("#### Keep your plan realistic")
        st.markdown("- Leave room for breaks and unexpected work.\n- Break big assignments into smaller tasks.\n- Update estimates if your workload changes.\n- Use the plan as a guide, not a strict rule.")

with tab_tasks:
    left, right = st.columns([0.8, 1.5], gap="large")
    with left:
        st.markdown('<div class="section-title">Add a study task</div><div class="section-sub">Enter a task once; the planner will help organize it.</div>', unsafe_allow_html=True)
        with st.form("add_task", clear_on_submit=True, border=True):
            subject = st.text_input("Subject", placeholder="e.g. Computer Science", help="The school subject this task belongs to.", max_chars=60)
            task_name = st.text_input("Task or assignment", placeholder="e.g. Revise Python loops", max_chars=120)
            deadline = st.date_input("Deadline", value=today + timedelta(days=3), key="new_deadline")
            hours = st.number_input("Estimated time (hours)", min_value=0.25, max_value=30.0, value=1.0, step=0.25, help="Estimate the total time needed, not the time for one session.")
            f1, f2 = st.columns(2)
            with f1:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
            with f2:
                importance = st.selectbox("Importance", ["Low", "Normal", "High"], index=1)
            submitted = st.form_submit_button("＋ Add task", type="primary", use_container_width=True)
            if submitted:
                if not subject.strip() or not task_name.strip():
                    st.error("Please enter both a subject and a task name.")
                else:
                    if deadline < today:
                        st.toast("This deadline is before your planning start date, so it will be treated as urgent.", icon="⚠️")
                    new_task = {"subject":subject.strip(), "task":task_name.strip(), "deadline":deadline, "hours":float(hours), "difficulty":difficulty, "importance":importance, "completed":False}
                    if add_task(new_task):
                        st.rerun()
        with st.expander("What do the task settings mean?"):
            st.markdown("- **Deadline:** when the work should be finished.\n- **Estimated time:** your best estimate of the total work.\n- **Difficulty:** how challenging the task feels.\n- **Importance:** how much attention the task deserves.")
        sample_label = "✨ Add sample tasks" if PERSIST else "✨ Restore sample tasks"
        sample_help = ("Add four sample tasks to your saved list." if PERSIST
                       else "Replace the current task list with sample tasks for a school exhibition demonstration.")
        if st.button(sample_label, use_container_width=True, help=sample_help):
            samples = [
                {"subject":"Mathematics", "task":"Practice algebra problems", "deadline":today + timedelta(days=1), "hours":2.0, "difficulty":"Hard", "importance":"High", "completed":False},
                {"subject":"Science", "task":"Revise electricity chapter", "deadline":today + timedelta(days=3), "hours":1.5, "difficulty":"Medium", "importance":"High", "completed":False},
                {"subject":"English", "task":"Prepare poem notes", "deadline":today + timedelta(days=2), "hours":1.0, "difficulty":"Easy", "importance":"Normal", "completed":False},
                {"subject":"Computer Science", "task":"Practice Python conditions", "deadline":today + timedelta(days=5), "hours":2.0, "difficulty":"Medium", "importance":"High", "completed":False},
            ]
            if PERSIST:
                added_all = all(add_task(t) for t in samples)
            else:
                replace_tasks(samples)
                added_all = True
            if added_all:
                st.rerun()
    with right:
        st.markdown('<div class="section-title">Your task list</div><div class="section-sub">Search, filter, update completion, or remove a task.</div>', unsafe_allow_html=True)
        if all_tasks:
            search_text = st.text_input("🔎 Search tasks", placeholder="Search by subject or task name", key="task_search")
            status_filter = st.selectbox("Show tasks", ["All tasks", "Open only", "Completed only"])
            visible = []
            for i, task in enumerate(st.session_state.tasks):
                if search_text.lower() not in (task["subject"] + " " + task["task"]).lower():
                    continue
                if status_filter == "Open only" and task.get("completed", False):
                    continue
                if status_filter == "Completed only" and not task.get("completed", False):
                    continue
                visible.append((i, task))
            rows = []
            for i, task in visible:
                days_left = (task["deadline"] - today).days
                due_label = "Overdue" if days_left < 0 else ("Today" if days_left == 0 else f"In {days_left} day(s)")
                rows.append({"Subject":task["subject"], "Task":task["task"], "Deadline":task["deadline"].strftime("%d %b %Y"), "Due status":due_label, "Hours":task["hours"], "Difficulty":task["difficulty"], "Priority":score_task(task, today), "Status":"Completed" if task.get("completed", False) else "Open"})
            if rows:
                task_frame = pd.DataFrame(rows).sort_values(["Status", "Priority"], ascending=[True, False])
                card_html = ""
                for _, r in task_frame.iterrows():
                    done = r["Status"] == "Completed"
                    badge = "ok" if done else ("hot" if r["Due status"] in ("Overdue", "Today") else "")
                    badge_text = "✓ Completed" if done else r["Due status"]
                    card_html += (f'<div class="tcard{" done" if done else ""}"><div class="tcard-top"><span class="task-chip">{esc(r["Subject"])}</span>'
                                  f'<span class="badge {badge}">{esc(badge_text)}</span></div><div class="tcard-title">{esc(r["Task"])}</div>'
                                  f'<div class="tcard-meta">📅 {esc(r["Deadline"])} · ⏱ {r["Hours"]} h · {esc(r["Difficulty"])} · Priority {r["Priority"]}</div></div>')
                st.markdown(card_html, unsafe_allow_html=True)
                with st.expander("Table view"):
                    st.dataframe(task_frame, use_container_width=True, hide_index=True)
            else:
                st.info("No tasks match these filters. Try another search or choose All tasks.")
            labels = {f'{i+1}. {t["subject"]} — {t["task"]}': i for i, t in enumerate(st.session_state.tasks)}
            selected_label = st.selectbox("Choose a task to update", list(labels.keys()), key="status_task_select")
            selected_index = labels[selected_label]
            current_task = st.session_state.tasks[selected_index]
            status_choice = st.radio("Task status", ["Open", "Completed"], index=1 if current_task.get("completed", False) else 0, horizontal=True, key=f"status_radio_{selected_index}")
            act1, act2 = st.columns(2)
            with act1:
                if st.button("Save status", use_container_width=True):
                    if set_task_status(selected_index, status_choice == "Completed"):
                        st.rerun()
            with act2:
                if st.button("Remove selected", use_container_width=True):
                    if remove_task(selected_index):
                        st.rerun()
            csv_frame = pd.DataFrame([{ "Subject":t["subject"], "Task":t["task"], "Deadline":t["deadline"].isoformat(), "Estimated hours":t["hours"], "Difficulty":t["difficulty"], "Importance":t["importance"], "Status":"Completed" if t.get("completed", False) else "Open"} for t in st.session_state.tasks])
            st.download_button("⬇️ Download task list (CSV)", data=csv_frame.to_csv(index=False).encode("utf-8"), file_name="study_tasks.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("Your list is empty. Add your first task using the form.")

with tab_schedule:
    st.markdown('<div class="section-title">Your personalized study plan</div><div class="section-sub">The planner splits tasks into focus blocks and tries to schedule urgent work earlier.</div>', unsafe_allow_html=True)
    active_tasks = [t for t in st.session_state.tasks if not t.get("completed", False)]
    action1, action2 = st.columns([1, 2])
    with action1:
        generate = st.button("✨ Generate smart schedule", type="primary", use_container_width=True)
    with action2:
        st.caption(f"Planning {planning_days} days · {daily_minutes} minutes/day · {session_minutes}-minute focus blocks · {len(active_tasks)} open task(s)")
    if generate:
        st.session_state.schedule = build_schedule(active_tasks, today, planning_days, daily_minutes, session_minutes)
        st.session_state.schedule_start = today
    if "schedule" in st.session_state:
        schedule = st.session_state.schedule
        summary = summarize_schedule(schedule)
        remaining_minutes = unplanned_minutes(active_tasks, schedule)
        if remaining_minutes:
            st.warning(
                f"Your selected time window has insufficient capacity for all open tasks. "
                f"About {remaining_minutes} minute(s) remain unscheduled. Increase the plan length "
                "or daily study budget, or review your time estimates."
            )
        elif active_tasks:
            st.success("All open-task time estimates fit within the selected planning window.")
        sm1, sm2, sm3 = st.columns(3)
        sm1.metric("Focus sessions", summary["sessions"])
        sm2.metric("Planned study time", f'{summary["total_hours"]} hours')
        sm3.metric("Daily study budget", f"{daily_minutes} min")
        if not schedule:
            st.warning("No sessions to show. Add an open task, then generate your schedule again.")
        else:
            frame = pd.DataFrame([{"Date":item["date"].strftime("%a, %d %b"), "Subject":item["subject"], "Task":item["task"], "Session (min)":item["minutes"], "Why prioritized":item["reason"], "Priority score":item["priority"]} for item in schedule])
            day_html = ""
            for day_label, grp in frame.groupby("Date", sort=False):
                rows_html = "".join(
                    f'<div class="sess"><div><b>{esc(r["Task"])}</b><div class="tcard-meta">{esc(r["Subject"])} · {esc(r["Why prioritized"])}</div></div>'
                    f'<span class="task-chip">{r["Session (min)"]} min</span></div>' for _, r in grp.iterrows())
                day_html += f'<div class="daycard"><div class="day-head"><b>{esc(day_label)}</b><span class="badge">{int(grp["Session (min)"].sum())} min</span></div>{rows_html}</div>'
            st.markdown(day_html, unsafe_allow_html=True)
            with st.expander("Table view"):
                st.dataframe(frame, use_container_width=True, hide_index=True)
            chart_left, chart_right = st.columns([1.2, 1], gap="large")
            with chart_left:
                st.markdown("#### Study time by subject")
                subject_minutes = frame.groupby("Subject")["Session (min)"].sum().sort_values(ascending=False)
                st.bar_chart(subject_minutes)
            with chart_right:
                st.markdown("#### Planned workload by day")
                daily = frame.groupby("Date")["Session (min)"].sum()
                st.line_chart(daily)
            st.download_button("⬇️ Download study timetable (CSV)", data=frame.to_csv(index=False).encode("utf-8"), file_name="smart_study_plan.csv", mime="text/csv", use_container_width=True)
            mail_settings = secret_section("email")
            if signed_in and mail_settings.get("sender") and mail_settings.get("app_password"):
                if st.button("📧 Email this plan to my Gmail", use_container_width=True, key="email_plan"):
                    if time.time() - st.session_state.get("last_email_ts", 0) < 60:
                        st.warning("Please wait a minute before sending another e-mail.")
                    else:
                        try:
                            with st.spinner("Sending your plan..."):
                                plan_email = build_plan_email(mail_settings["sender"], OWNER, USER_NAME, schedule, len(active_tasks))
                                send_message(plan_email, mail_settings["sender"], mail_settings["app_password"])
                            st.session_state.last_email_ts = time.time()
                            st.success(f"Your plan was sent to {OWNER}. Check your inbox (and the spam folder).")
                        except Exception:
                            st.error("The e-mail could not be sent. Please try again later.")
            elif signed_in:
                st.caption("📧 E-mail delivery is not set up on this copy of the app (see the README, step 4).")
            else:
                st.caption("📧 Sign in with Google to receive your plan by e-mail.")
            st.caption("Reminder: this is a suggested timetable. Make room for meals, breaks, sleep, school hours, and family commitments.")
    else:
        st.markdown("""
        <div class="panel">
          <div style="font-size:2rem">🗓️</div>
          <h3 style="margin:.4rem 0;color:#17243a">Your schedule is one click away</h3>
          <p style="color:#718096;margin:0">Add tasks, then click <b>Generate smart schedule</b>. Your focus sessions, subject charts, and downloadable timetable will appear here.</p>
        </div>
        """, unsafe_allow_html=True)
    with st.expander("How should I use the timetable?"):
        st.markdown("1. Check the date and task for each session.\n2. Work for the suggested number of minutes, then take a break.\n3. If a day feels too full, increase the planning window or reduce task estimates after reviewing them.\n4. Mark work complete in the Tasks tab when you finish it.")

with tab_progress:
    st.markdown('<div class="section-title">Your progress and learning guide</div><div class="section-sub">Use these summaries to understand your workload and learn how the planner makes suggestions.</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    p1.metric("Tasks completed", len(completed_tasks))
    p2.metric("Tasks still open", len(open_tasks))
    p3.metric("Completion rate", f"{completion_pct}%")
    st.progress(completion_pct / 100 if all_tasks else 0)
    if all_tasks:
        status_data = pd.DataFrame({"Status":["Completed", "Open"], "Tasks":[len(completed_tasks), len(open_tasks)]}).set_index("Status")
        st.markdown("#### Task status overview")
        st.bar_chart(status_data)
        subject_data = pd.DataFrame([{"Subject":t["subject"], "Estimated hours":float(t["hours"]), "Status":"Completed" if t.get("completed", False) else "Open"} for t in all_tasks])
        st.markdown("#### Estimated work by subject")
        st.bar_chart(subject_data.groupby("Subject")["Estimated hours"].sum().sort_values(ascending=False))
    st.divider()
    st.markdown("#### 🧠 How the smart priority score works")
    st.write("Each open task receives a score. Higher scores are considered earlier when the schedule is created.")
    explainer = pd.DataFrame([
        {"Factor":"Deadline urgency", "What it means":"Tasks that are overdue or due soon get more points."},
        {"Factor":"Difficulty", "What it means":"Harder tasks get extra points so you can allow more time."},
        {"Factor":"Importance", "What it means":"Tasks marked High receive more points than routine tasks."},
        {"Factor":"Estimated effort", "What it means":"Longer tasks receive a small boost to help avoid leaving them until the last minute."},
    ])
    st.dataframe(explainer, use_container_width=True, hide_index=True)
    st.info("Exhibition transparency: this prototype uses a visible rule-based scoring algorithm. It is AI-inspired, not a trained machine-learning model, and it does not send your task list to an external AI service. Signed-in users\u0027 tasks are stored in the app\u0027s own database, linked to their e-mail address.", icon="🔒")
    with st.expander("Frequently asked questions"):
        st.markdown("**Does it save my work permanently?**\n\nWith Google sign-in and working storage configured, your tasks are saved to your account and are there when you come back. You can also download your task list as CSV for a copy.\n\n**Why is a task not in my schedule?**\n\nThe planner schedules open tasks within the selected time window and daily capacity. If the workload is too large, increase the plan length or daily study budget and generate again.\n\n**Can I use it for an exhibition without internet?**\n\nAfter Python and the required packages have been installed, the app runs locally. The first setup may need an internet connection to download packages.\n\n**Is this a real trained AI model?**\n\nNo. It uses a transparent scoring formula to demonstrate how an intelligent study-planning assistant can work.")

st.divider()
st.caption("StudyFlow AI · School exhibition prototype · Sign in with Google to save your tasks · No paid AI API required")
