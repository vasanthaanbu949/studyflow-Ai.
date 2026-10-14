import os
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage import TaskStore, MAX_TASKS_PER_USER


def make_task(name="Revise", subject="Math", completed=False):
    return {"subject": subject, "task": name, "deadline": date(2026, 10, 20), "hours": 1.5,
            "difficulty": "Hard", "importance": "High", "completed": completed}


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = TaskStore(os.path.join(self.tmp.name, "test.db"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_and_list_roundtrip(self):
        self.store.add_task("Student@Gmail.com", make_task())
        tasks = self.store.list_tasks("student@gmail.com")  # e-mail is case-insensitive
        self.assertEqual(len(tasks), 1)
        t = tasks[0]
        self.assertEqual((t["subject"], t["task"], t["hours"]), ("Math", "Revise", 1.5))
        self.assertEqual(t["deadline"], date(2026, 10, 20))
        self.assertIs(t["completed"], False)
        self.assertIsInstance(t["id"], int)

    def test_data_survives_reopening_the_database(self):
        path = os.path.join(self.tmp.name, "persist.db")
        TaskStore(path).add_task("a@gmail.com", make_task("Persistent"))
        again = TaskStore(path)
        self.assertEqual([t["task"] for t in again.list_tasks("a@gmail.com")], ["Persistent"])

    def test_users_are_isolated(self):
        self.store.add_task("a@gmail.com", make_task("A's task"))
        self.store.add_task("b@gmail.com", make_task("B's task"))
        self.assertEqual([t["task"] for t in self.store.list_tasks("a@gmail.com")], ["A's task"])
        # B cannot change or delete A's task by guessing its id.
        a_id = self.store.list_tasks("a@gmail.com")[0]["id"]
        self.store.set_completed("b@gmail.com", a_id, True)
        self.store.delete_task("b@gmail.com", a_id)
        a_task = self.store.list_tasks("a@gmail.com")[0]
        self.assertFalse(a_task["completed"])

    def test_set_completed_and_delete(self):
        self.store.add_task("a@gmail.com", make_task())
        task_id = self.store.list_tasks("a@gmail.com")[0]["id"]
        self.store.set_completed("a@gmail.com", task_id, True)
        self.assertTrue(self.store.list_tasks("a@gmail.com")[0]["completed"])
        self.store.delete_task("a@gmail.com", task_id)
        self.assertEqual(self.store.list_tasks("a@gmail.com"), [])

    def test_replace_all(self):
        self.store.add_task("a@gmail.com", make_task("old"))
        self.store.replace_all("a@gmail.com", [make_task("new1"), make_task("new2")])
        self.assertEqual([t["task"] for t in self.store.list_tasks("a@gmail.com")], ["new1", "new2"])

    def test_sql_injection_text_is_stored_as_plain_text(self):
        nasty = "x'); DROP TABLE tasks; --"
        self.store.add_task("a@gmail.com", make_task(nasty))
        self.assertEqual(self.store.list_tasks("a@gmail.com")[0]["task"], nasty)
        self.assertEqual(self.store.count_tasks("a@gmail.com"), 1)

    def test_task_limit(self):
        self.store.replace_all("a@gmail.com", [make_task(str(i)) for i in range(MAX_TASKS_PER_USER)])
        with self.assertRaises(ValueError):
            self.store.add_task("a@gmail.com", make_task("one too many"))

    def test_record_login_and_delete_user_data(self):
        self.store.record_login("a@gmail.com", "Asha")
        self.store.record_login("a@gmail.com", "Asha K")  # second login updates, not duplicates
        self.store.add_task("a@gmail.com", make_task())
        self.store.add_task("b@gmail.com", make_task("keep me"))
        self.store.delete_user_data("a@gmail.com")
        self.assertEqual(self.store.list_tasks("a@gmail.com"), [])
        self.assertEqual(len(self.store.list_tasks("b@gmail.com")), 1)

    def test_owner_required(self):
        with self.assertRaises(ValueError):
            self.store.add_task("  ", make_task())


if __name__ == "__main__":
    unittest.main()
