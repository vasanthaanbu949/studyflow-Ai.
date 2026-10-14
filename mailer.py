"""Send a student's study plan to their own Gmail inbox.

How it works: the app owns ONE sender Gmail account and logs in to it with a
Google "App Password" (stored in Streamlit secrets, never in the code). The
plan is then e-mailed to the address the student signed in with. The app never
sees the student's Gmail password and never reads their inbox.
"""
from email.message import EmailMessage
from html import escape
import smtplib
from typing import Any, Dict, List

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def _clean_header(value: str) -> str:
    return " ".join(str(value).split())


def build_plan_email(sender: str, recipient: str, name: str, schedule: List[Dict[str, Any]],
                     open_task_count: int = 0) -> EmailMessage:
    """Build a plain-text + HTML e-mail containing the study timetable."""
    first_name = _clean_header(name).split(" ")[0] if name else "there"

    by_day: Dict[Any, List[Dict[str, Any]]] = {}
    for item in schedule:
        by_day.setdefault(item["date"], []).append(item)

    text_lines = [f"Hi {first_name},", "", "Here is your StudyFlow AI study plan.", ""]
    html_days = []
    for day, items in by_day.items():
        total = sum(int(i["minutes"]) for i in items)
        label = day.strftime("%A, %d %B %Y")
        text_lines.append(f"{label} ({total} min)")
        rows = []
        for i in items:
            text_lines.append(f"  - {i['task']} [{i['subject']}] - {i['minutes']} min")
            rows.append(
                f"<li><b>{escape(str(i['task']))}</b> "
                f"<span style='color:#52627a'>({escape(str(i['subject']))})</span> &ndash; {int(i['minutes'])} min</li>"
            )
        text_lines.append("")
        html_days.append(f"<h3 style='margin:16px 0 4px'>{escape(label)} &middot; {total} min</h3><ul>{''.join(rows)}</ul>")

    if not by_day:
        text_lines.append("There are no study sessions in your plan yet.")
        html_days.append("<p>There are no study sessions in your plan yet.</p>")

    text_lines += ["Plan realistically: leave room for breaks, meals and sleep.", "", "- StudyFlow AI"]

    msg = EmailMessage()
    msg["Subject"] = "Your StudyFlow AI study plan"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content("\n".join(text_lines))
    msg.add_alternative(
        "<div style='font-family:Arial,sans-serif;color:#17243a;max-width:560px'>"
        f"<h2 style='margin-bottom:4px'>Your study plan</h2><p>Hi {escape(first_name)}, here is your plan "
        f"({int(open_task_count)} open task(s)).</p>{''.join(html_days)}"
        "<p style='color:#52627a'>Plan realistically: leave room for breaks, meals and sleep.</p>"
        "<p>&mdash; StudyFlow AI</p></div>",
        subtype="html",
    )
    return msg


def send_message(msg: EmailMessage, sender: str, app_password: str, timeout: int = 20) -> None:
    """Send through Gmail SMTP. Raises on any failure so the caller can show a message."""
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=timeout) as server:
        server.login(sender, app_password.replace(" ", ""))
        server.send_message(msg)
