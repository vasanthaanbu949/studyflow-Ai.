import unittest
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, timedelta
from planner import build_schedule, score_task, summarize_schedule, unplanned_minutes


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 10, 14)

    def task(self, name="Math revision", hours=1.0, days=2, difficulty="Medium", importance="Normal"):
        return {"subject": "Math", "task": name, "deadline": self.today + timedelta(days=days),
                "hours": hours, "difficulty": difficulty, "importance": importance}

    def test_urgent_task_scores_higher_than_later_task(self):
        urgent = self.task(days=0)
        later = self.task(days=8)
        self.assertGreater(score_task(urgent, self.today), score_task(later, self.today))

    def test_schedule_respects_daily_capacity(self):
        tasks = [self.task("A", 2), self.task("B", 2), self.task("C", 2)]
        schedule = build_schedule(tasks, self.today, days=3, daily_minutes=75, session_minutes=30)
        by_day = {}
        for item in schedule:
            by_day[item["date"]] = by_day.get(item["date"], 0) + item["minutes"]
            self.assertLessEqual(item["minutes"], 30)
        self.assertTrue(all(minutes <= 75 for minutes in by_day.values()))

    def test_small_daily_budget_is_not_exceeded(self):
        schedule = build_schedule([self.task(hours=1)], self.today, days=2, daily_minutes=20, session_minutes=45)
        self.assertTrue(all(item["minutes"] <= 20 for item in schedule))
        self.assertLessEqual(sum(item["minutes"] for item in schedule if item["date"] == self.today), 20)

    def test_unplanned_workload_is_reported(self):
        tasks = [self.task(hours=5)]
        schedule = build_schedule(tasks, self.today, days=1, daily_minutes=60, session_minutes=30)
        self.assertEqual(unplanned_minutes(tasks, schedule), 240)

    def test_summary(self):
        schedule = build_schedule([self.task(hours=1)], self.today, days=2, daily_minutes=60, session_minutes=30)
        summary = summarize_schedule(schedule)
        self.assertEqual(summary["total_minutes"], 60)
        self.assertEqual(summary["total_hours"], 1.0)

    def test_invalid_plan_length_raises(self):
        with self.assertRaises(ValueError):
            build_schedule([], self.today, days=0)

if __name__ == "__main__":
    unittest.main()
