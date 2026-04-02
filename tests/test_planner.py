import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from chief_of_staff.models import CalendarEvent, UserProfile
from chief_of_staff.services.planner_service import PlannerService


TZ = ZoneInfo("Asia/Singapore")


class PlannerServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = PlannerService()
        self.profile = UserProfile()
        self.week_start = datetime(2026, 3, 30, 0, 0, tzinfo=TZ)
        self.week_end = self.week_start + timedelta(days=7)

    def test_detects_conflicts(self):
        events = [
            CalendarEvent("1", "A", self.week_start.replace(hour=10), self.week_start.replace(hour=11)),
            CalendarEvent("2", "B", self.week_start.replace(hour=10, minute=30), self.week_start.replace(hour=12)),
        ]
        analysis = self.service.analyze_week(events, self.profile, self.week_start, self.week_end)
        self.assertEqual(len(analysis["conflicts"]), 1)

    def test_suggest_slots_returns_ranked_options(self):
        events = [
            CalendarEvent("1", "Lecture", self.week_start.replace(day=31, hour=10), self.week_start.replace(day=31, hour=12)),
            CalendarEvent("2", "Meeting", self.week_start.replace(day=31, hour=14), self.week_start.replace(day=31, hour=15)),
        ]
        slots = self.service.suggest_slots(events, self.profile, self.week_start, self.week_end, 120)
        self.assertGreaterEqual(len(slots), 1)
        self.assertGreaterEqual(slots[0].score, slots[-1].score)

    def test_protect_focus_time_returns_proposal(self):
        events = [
            CalendarEvent("1", "Class", self.week_start.replace(day=30, hour=10), self.week_start.replace(day=30, hour=12)),
        ]
        result = self.service.protect_focus_time(events, self.profile, self.week_start, self.week_end, 120)
        self.assertIn("reason", result)
        self.assertIsNotNone(result["slot"])


if __name__ == "__main__":
    unittest.main()
