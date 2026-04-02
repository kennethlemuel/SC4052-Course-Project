from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from chief_of_staff.models import CalendarEvent, UserProfile
from chief_of_staff.services.calendar_service import CalendarService
from chief_of_staff.services.planner_service import PlannerService
from chief_of_staff.utils import (
    end_of_week,
    format_event_line,
    parse_duration_minutes,
    parse_relative_date,
    parse_time_component,
    start_of_week,
)


@dataclass
class AssistantIntent:
    name: str
    title: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    duration_minutes: int = 120


class AssistantService:
    def __init__(self, calendar_service: CalendarService, planner_service: PlannerService) -> None:
        self.calendar_service = calendar_service
        self.planner_service = planner_service

    def handle_query(self, text: str, now: datetime, profile: UserProfile) -> Dict[str, object]:
        intent = self._detect_intent(text, now)
        week_start = start_of_week(now)
        week_end = end_of_week(now)
        week_events = self.calendar_service.list_events(week_start, week_end)

        if intent.name == "week_summary":
            analysis = self.planner_service.analyze_week(week_events, profile, week_start, week_end)
            return {
                "intent": intent.name,
                "reply": self._build_week_reply(week_events, analysis),
                "analysis": analysis,
            }

        if intent.name == "suggest_slot":
            slots = self.planner_service.suggest_slots(
                week_events,
                profile,
                week_start,
                week_end,
                intent.duration_minutes,
                title=intent.title or "Focus session",
            )
            reply = self._build_slot_reply(slots, intent.duration_minutes, intent.title or "focus work")
            return {"intent": intent.name, "reply": reply, "slots": [slot.to_dict() for slot in slots]}

        if intent.name == "protect_focus":
            result = self.planner_service.protect_focus_time(
                week_events,
                profile,
                week_start,
                week_end,
                intent.duration_minutes,
            )
            reply = result["reason"]
            if result["slot"]:
                slot = result["slot"]
                reply += f" Suggested slot: {self._format_slot(slot['start'], slot['end'])}."
            return {"intent": intent.name, "reply": reply, "proposal": result}

        if intent.name == "create_event" and intent.start and intent.end and intent.title:
            event = self.calendar_service.create_event(intent.title, intent.start, intent.end)
            return {
                "intent": intent.name,
                "reply": f"Added {event.title} on {event.start.strftime('%A %d %b at %I:%M %p').lstrip('0')}.",
                "event": event.to_dict(),
            }

        return {
            "intent": "fallback",
            "reply": (
                "I can summarize your week, add an event, suggest the best slot for work, "
                "or protect focus time. Try: 'What does my week look like?' or "
                "'Add project sync tomorrow at 3 pm for 1 hour.'"
            ),
        }

    def _detect_intent(self, text: str, now: datetime) -> AssistantIntent:
        lowered = text.lower().strip()
        if "protect focus" in lowered or "block focus" in lowered:
            return AssistantIntent(name="protect_focus", duration_minutes=parse_duration_minutes(lowered, 120))
        if any(phrase in lowered for phrase in ["best slot", "fit", "when can i", "suggest slot"]):
            title = self._extract_title(lowered)
            return AssistantIntent(name="suggest_slot", duration_minutes=parse_duration_minutes(lowered, 120), title=title)
        if lowered.startswith("add ") or lowered.startswith("schedule ") or lowered.startswith("create event"):
            return self._parse_create_event(text, now)
        if any(phrase in lowered for phrase in ["what do i have", "my week", "this week", "weekly summary", "what matters"]):
            return AssistantIntent(name="week_summary")
        return AssistantIntent(name="fallback")

    def _parse_create_event(self, text: str, now: datetime) -> AssistantIntent:
        lowered = text.lower()
        day = parse_relative_date(lowered, now)
        time_match = re.search(r"(?:at|from)\s+([0-9: ]+(?:am|pm)?)", lowered)
        duration = parse_duration_minutes(lowered, 60)
        title = self._extract_event_title(text)
        if not day or not time_match or not title:
            return AssistantIntent(name="fallback")
        parsed_time = parse_time_component(time_match.group(1))
        if not parsed_time:
            return AssistantIntent(name="fallback")
        start = day.replace(hour=parsed_time[0], minute=parsed_time[1])
        end = start + timedelta(minutes=duration)
        return AssistantIntent(name="create_event", title=title, start=start, end=end, duration_minutes=duration)

    @staticmethod
    def _extract_event_title(text: str) -> Optional[str]:
        lowered = text.lower()
        cleaned = re.sub(r"^(add|schedule|create event)\s+", "", lowered)
        cleaned = re.split(r"\s+(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next monday|next tuesday|next wednesday|next thursday|next friday|next saturday|next sunday)\b", cleaned)[0]
        title = cleaned.strip(" .")
        return title.title() if title else None

    @staticmethod
    def _extract_title(text: str) -> str:
        match = re.search(r"for\s+(.+)", text)
        if not match:
            return "focus work"
        return match.group(1).strip(" .")

    def _build_week_reply(self, events: List[CalendarEvent], analysis: Dict[str, object]) -> str:
        if not events:
            return (
                "Your week is currently clear.\n\n"
                "Suggested next step:\n"
                "• Protect a focus block before meetings appear."
            )
        lines = [f"You have {len(events)} events this week.", "", "Coming up:"]
        for event in events[:3]:
            lines.append(f"• {format_event_line(event)}")
        suggestions = analysis["suggestions"][:2]
        lines.append("")
        lines.append("Planning signals:")
        if suggestions:
            for item in suggestions:
                lines.append(f"• {item['title']}")
        else:
            lines.append("• No major overload signals detected.")
        return "\n".join(lines)

    @staticmethod
    def _build_slot_reply(slots: List[object], duration_minutes: int, title: str) -> str:
        if not slots:
            return (
                f"I could not find a {duration_minutes}-minute slot for {title} this week.\n\n"
                "Try a shorter session or move one of the existing events."
            )
        top = slots[0]
        return (
            f"Best slot for {title}:\n"
            f"• {top.start.strftime('%A %d %b %I:%M %p').lstrip('0')} to {top.end.strftime('%I:%M %p').lstrip('0')}\n"
            f"• Why this works: {top.rationale}"
        )

    @staticmethod
    def _format_slot(start: str, end: str) -> str:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        return f"{start_dt.strftime('%A %d %b %I:%M %p').lstrip('0')} to {end_dt.strftime('%I:%M %p').lstrip('0')}"
