"""Persistent per-user storage for StudyFlow AI.

Two backends share one interface:

* SQLite (default)  - a local file, great for running on your own computer.
  NOTE: on Streamlit Community Cloud the local disk is wiped when the app
  restarts or is redeployed, so SQLite is NOT permanent there.
* PostgreSQL        - any hosted Postgres (Supabase, Neon, ...). Data survives
  restarts. Selected automatically when the database URL starts with
  "postgres://" or "postgresql://".

Every query is filtered by the owner's e-mail address, so one signed-in user can
never read or change another user's tasks.
"""
from contextlib import contextmanager
from datetime import date, datetime, timezone
import os
import sqlite3
from typing import Any, Dict, List, Optional

MAX_TASKS_PER_USER = 500

_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS users (
        email      TEXT PRIMARY KEY,
        name       TEXT,
        first_seen TEXT NOT NULL,
        last_login TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id         {pk},
        owner      TEXT NOT NULL,
        subject    TEXT NOT NULL,
        task       TEXT NOT NULL,
        deadline   TEXT NOT NULL,
        hours      DOUBLE PRECISION NOT NULL,
        difficulty TEXT NOT NULL,
        importance TEXT NOT NULL,
        completed  INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks (owner)",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _norm(email: str) -> str:
    return (email or "").strip().lower()


class TaskStore:
    """Small storage layer. Create one with TaskStore(url_or_path)."""

    def __init__(self, url: Optional[str] = None):
        url = (url or "").strip()
        self.is_postgres = url.startswith(("postgres://", "postgresql://"))
        if self.is_postgres:
            try:
                import psycopg2  # noqa: F401  (imported lazily; only needed for Postgres)
            except ImportError as exc:  # pragma: no cover - depends on environment
                raise RuntimeError(
                    "A Postgres database URL was given but 'psycopg2-binary' is not installed."
                ) from exc
            self.url = url
            self.label = "Cloud database (PostgreSQL)"
            self.is_permanent = True
        else:
            if url.startswith("sqlite:///"):
                url = url[len("sqlite:///"):]
            self.url = url or os.path.join(os.path.dirname(os.path.abspath(__file__)), "studyflow.db")
            self.label = "Local file (SQLite)"
            # A local file is only permanent on your own computer; hosts such as
            # Streamlit Community Cloud may delete it on restart.
            self.is_permanent = False
        self._init_schema()

    # ---- connection helpers -------------------------------------------------
    @contextmanager
    def _cursor(self):
        if self.is_postgres:
            import psycopg2
            conn = psycopg2.connect(self.url, connect_timeout=10)
        else:
            conn = sqlite3.connect(self.url, timeout=10)
        try:
            cur = conn.cursor()
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _sql(self, query: str) -> str:
        """Write queries with '?' placeholders; convert for Postgres."""
        return query.replace("?", "%s") if self.is_postgres else query

    def _init_schema(self) -> None:
        pk = "BIGSERIAL PRIMARY KEY" if self.is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        with self._cursor() as cur:
            for statement in _SCHEMA:
                cur.execute(statement.format(pk=pk) if "{pk}" in statement else statement)

    # ---- users --------------------------------------------------------------
    def record_login(self, email: str, name: str = "") -> None:
        email = _norm(email)
        if not email:
            raise ValueError("email is required")
        now = _now()
        with self._cursor() as cur:
            cur.execute(self._sql("SELECT 1 FROM users WHERE email = ?"), (email,))
            if cur.fetchone():
                cur.execute(self._sql("UPDATE users SET last_login = ?, name = ? WHERE email = ?"),
                            (now, name or "", email))
            else:
                cur.execute(self._sql("INSERT INTO users (email, name, first_seen, last_login) VALUES (?, ?, ?, ?)"),
                            (email, name or "", now, now))

    # ---- tasks --------------------------------------------------------------
    @staticmethod
    def _row_to_task(row) -> Dict[str, Any]:
        return {
            "id": int(row[0]),
            "subject": row[1],
            "task": row[2],
            "deadline": date.fromisoformat(row[3]),
            "hours": float(row[4]),
            "difficulty": row[5],
            "importance": row[6],
            "completed": bool(row[7]),
        }

    def list_tasks(self, owner: str) -> List[Dict[str, Any]]:
        owner = _norm(owner)
        with self._cursor() as cur:
            cur.execute(
                self._sql("SELECT id, subject, task, deadline, hours, difficulty, importance, completed "
                          "FROM tasks WHERE owner = ? ORDER BY id"),
                (owner,),
            )
            return [self._row_to_task(r) for r in cur.fetchall()]

    def count_tasks(self, owner: str) -> int:
        with self._cursor() as cur:
            cur.execute(self._sql("SELECT COUNT(*) FROM tasks WHERE owner = ?"), (_norm(owner),))
            return int(cur.fetchone()[0])

    def _insert(self, cur, owner: str, task: Dict[str, Any]) -> None:
        cur.execute(
            self._sql("INSERT INTO tasks (owner, subject, task, deadline, hours, difficulty, importance, completed, created_at) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"),
            (owner, str(task["subject"]), str(task["task"]), task["deadline"].isoformat(),
             float(task["hours"]), str(task["difficulty"]), str(task["importance"]),
             1 if task.get("completed") else 0, _now()),
        )

    def add_task(self, owner: str, task: Dict[str, Any]) -> None:
        owner = _norm(owner)
        if not owner:
            raise ValueError("owner is required")
        if self.count_tasks(owner) >= MAX_TASKS_PER_USER:
            raise ValueError(f"You can store up to {MAX_TASKS_PER_USER} tasks. Please remove some first.")
        with self._cursor() as cur:
            self._insert(cur, owner, task)

    def set_completed(self, owner: str, task_id: int, completed: bool) -> None:
        with self._cursor() as cur:
            cur.execute(self._sql("UPDATE tasks SET completed = ? WHERE id = ? AND owner = ?"),
                        (1 if completed else 0, int(task_id), _norm(owner)))

    def delete_task(self, owner: str, task_id: int) -> None:
        with self._cursor() as cur:
            cur.execute(self._sql("DELETE FROM tasks WHERE id = ? AND owner = ?"), (int(task_id), _norm(owner)))

    def replace_all(self, owner: str, tasks: List[Dict[str, Any]]) -> None:
        """Replace the owner's whole task list in one transaction."""
        owner = _norm(owner)
        if len(tasks) > MAX_TASKS_PER_USER:
            raise ValueError(f"You can store up to {MAX_TASKS_PER_USER} tasks.")
        with self._cursor() as cur:
            cur.execute(self._sql("DELETE FROM tasks WHERE owner = ?"), (owner,))
            for task in tasks:
                self._insert(cur, owner, task)

    def delete_user_data(self, owner: str) -> None:
        """Erase everything stored for this user (tasks and profile row)."""
        owner = _norm(owner)
        with self._cursor() as cur:
            cur.execute(self._sql("DELETE FROM tasks WHERE owner = ?"), (owner,))
            cur.execute(self._sql("DELETE FROM users WHERE email = ?"), (owner,))
