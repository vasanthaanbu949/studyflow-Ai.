"""Transparent rule-based scheduling logic for StudyFlow AI."""
from datetime import date, timedelta
from typing import List, Dict, Any


def score_task(task: Dict[str, Any], today: date) -> float:
    """Return an explainable priority score; higher scores schedule earlier."""
    days_left = (task["deadline"] - today).days
    if days_left < 0:
        urgency = 10.0
    elif days_left == 0:
        urgency = 9.0
    elif days_left <= 1:
        urgency = 8.0
    elif days_left <= 3:
        urgency = 6.5
    elif days_left <= 7:
        urgency = 4.5
    else:
        urgency = 2.5

    difficulty_points = {"Easy": 1.0, "Medium": 2.0, "Hard": 3.0}.get(task.get("difficulty"), 2.0)
    importance_points = {"Low": 1.0, "Normal": 2.0, "High": 3.0}.get(task.get("importance"), 2.0)
    effort_points = min(max(float(task.get("hours", 1)), 0), 4.0) * 0.35
    return round(urgency * 2.0 + difficulty_points * 1.5 + importance_points * 2.0 + effort_points, 2)


def build_schedule(
    tasks: List[Dict[str, Any]],
    today: date,
    days: int = 7,
    daily_minutes: int = 120,
    session_minutes: int = 30,
) -> List[Dict[str, Any]]:
    """Allocate focus sessions within daily capacity, prioritizing urgent tasks.

    Sessions never exceed session_minutes, and the sum scheduled on any day never
    exceeds daily_minutes. Any remaining workload can be measured with
    unplanned_minutes().
    """
    if days < 1:
        raise ValueError("days must be at least 1")
    if daily_minutes < 1 or session_minutes < 1:
        raise ValueError("Study time must be positive")

    dates = [today + timedelta(days=i) for i in range(days)]
    remaining_capacity = {d: daily_minutes for d in dates}
    schedule = []
    ranked = sorted(tasks, key=lambda t: (-score_task(t, today), t["deadline"], t.get("subject", "")))

    for task in ranked:
        remaining = max(1, round(float(task.get("hours", 1)) * 60))
        deadline = task["deadline"]
        eligible_dates = [d for d in dates if d <= deadline]
        if not eligible_dates:
            eligible_dates = [dates[0]]

        # Fill eligible dates first, then use spare capacity later in the window.
        allocation_dates = eligible_dates + [d for d in dates if d not in eligible_dates]
        for day in allocation_dates:
            while remaining > 0 and remaining_capacity[day] > 0:
                block = min(session_minutes, remaining, remaining_capacity[day])
                schedule.append({
                    "date": day,
                    "subject": task.get("subject", "General"),
                    "task": task.get("task", "Study task"),
                    "minutes": block,
                    "priority": score_task(task, today),
                    "reason": _reason(task, today) + (" (after deadline)" if day > deadline else ""),
                })
                remaining -= block
                remaining_capacity[day] -= block
            if remaining <= 0:
                break

    return sorted(schedule, key=lambda item: (item["date"], -item["priority"], item["subject"]))


def unplanned_minutes(tasks: List[Dict[str, Any]], schedule: List[Dict[str, Any]]) -> int:
    """Return task minutes not allocated in the generated schedule."""
    requested = sum(max(1, round(float(t.get("hours", 1)) * 60)) for t in tasks)
    allocated = sum(int(item["minutes"]) for item in schedule)
    return max(0, requested - allocated)


def _reason(task: Dict[str, Any], today: date) -> str:
    days_left = (task["deadline"] - today).days
    if days_left < 0:
        urgency_text = "Overdue task"
    elif days_left == 0:
        urgency_text = "Due today"
    elif days_left <= 3:
        urgency_text = "Deadline approaching"
    else:
        urgency_text = "Plan ahead"
    return f"{urgency_text}; {str(task.get('difficulty', 'Medium')).lower()} difficulty; {str(task.get('importance', 'Normal')).lower()} importance"


def summarize_schedule(schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = sum(int(item["minutes"]) for item in schedule)
    return {"sessions": len(schedule), "total_minutes": total, "total_hours": round(total / 60, 1)}
