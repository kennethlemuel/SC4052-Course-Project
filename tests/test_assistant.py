import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from chief_of_staff.models import CalendarEvent, UserProfile
from chief_of_staff.services.assistant_service import AssistantService
from chief_of_staff.services.calendar_service import CalendarService
from chief_of_staff.services.planner_service import PlannerService


class FakeAdapter:
    def __init__(self, events):
        self.events = list(events)

    def list_events(self, start, end):
        return [event for event in self.events if event.end > start and event.start < end]

    def create_event(self, title, start, end, location="", notes=""):
        raise NotImplementedError


class AssistantServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile = UserProfile()
        self.service = AssistantService(CalendarService(FakeAdapter([])), PlannerService())
        self.now = datetime(2026, 4, 2, 9, 0, tzinfo=ZoneInfo("Asia/Singapore"))

    def test_detects_week_summary(self):
        result = self.service.handle_query("What matters this week?", self.now, self.profile)
        self.assertEqual(result["intent"], "week_summary")

    def test_detects_best_slot_request(self):
        result = self.service.handle_query("Find the best slot this week for study for 2 hours", self.now, self.profile)
        self.assertEqual(result["intent"], "suggest_slot")

    def test_parses_event_creation(self):
        intent = self.service._detect_intent("Add revision tomorrow at 3 pm for 2 hours", self.now)
        self.assertEqual(intent.name, "create_event")
        self.assertEqual(intent.title, "Revision")
        self.assertEqual(intent.start.hour, 15)
        self.assertEqual(intent.duration_minutes, 120)

    def test_week_summary_reply_uses_multiline_briefing(self):
        events = [
            CalendarEvent("1", "Lecture", self.now.replace(hour=10), self.now.replace(hour=11)),
            CalendarEvent("2", "Meeting", self.now.replace(day=3, hour=14), self.now.replace(day=3, hour=15)),
        ]
        self.service = AssistantService(CalendarService(FakeAdapter(events)), PlannerService())
        result = self.service.handle_query("What matters this week?", self.now, self.profile)
        self.assertIn("Coming up:", result["reply"])
        self.assertIn("•", result["reply"])


if __name__ == "__main__":
    unittest.main()
