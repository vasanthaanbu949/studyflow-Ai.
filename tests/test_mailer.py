import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mailer import build_plan_email


class MailerTests(unittest.TestCase):
    def schedule(self):
        return [
            {"date": date(2026, 10, 15), "subject": "Math", "task": "Algebra <b>set</b>", "minutes": 30, "priority": 9, "reason": ""},
            {"date": date(2026, 10, 15), "subject": "Science", "task": "Electricity", "minutes": 30, "priority": 8, "reason": ""},
            {"date": date(2026, 10, 16), "subject": "English", "task": "Poem notes", "minutes": 45, "priority": 5, "reason": ""},
        ]

    def test_message_headers_and_content(self):
        msg = build_plan_email("sender@gmail.com", "student@gmail.com", "Asha Kumar", self.schedule(), 3)
        self.assertEqual(msg["To"], "student@gmail.com")
        self.assertEqual(msg["From"], "sender@gmail.com")
        text = msg.get_body(preferencelist=("plain",)).get_content()
        self.assertIn("Hi Asha,", text)
        self.assertIn("Thursday, 15 October 2026 (60 min)", text)
        self.assertIn("Poem notes", text)

    def test_html_part_escapes_user_text(self):
        msg = build_plan_email("s@gmail.com", "t@gmail.com", "<script>x</script>", self.schedule(), 3)
        html_part = msg.get_body(preferencelist=("html",)).get_content()
        self.assertNotIn("<script>", html_part)
        self.assertNotIn("<b>set</b>", html_part)
        self.assertIn("&lt;b&gt;set&lt;/b&gt;", html_part)

    def test_empty_schedule(self):
        msg = build_plan_email("s@gmail.com", "t@gmail.com", "", [], 0)
        self.assertIn("no study sessions", msg.get_body(preferencelist=("plain",)).get_content())

    def test_header_injection_is_rejected(self):
        with self.assertRaises(ValueError):
            build_plan_email("s@gmail.com", "t@gmail.com\nBcc: evil@x.com", "A", self.schedule(), 1)


if __name__ == "__main__":
    unittest.main()
