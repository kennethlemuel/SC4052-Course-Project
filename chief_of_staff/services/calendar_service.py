from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from chief_of_staff.models import CalendarEvent
from chief_of_staff.services.calendar_adapters import CalendarAdapter
from chief_of_staff.utils import describe_day, format_event_line, sort_events


class CalendarService:
    def __init__(self, adapter: CalendarAdapter) -> None:
        self.adapter = adapter

    def list_events(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        return sort_events(self.adapter.list_events(start, end))

    def create_event(self, title: str, start: datetime, end: datetime, location: str = "", notes: str = "") -> CalendarEvent:
        return self.adapter.create_event(title, start, end, location=location, notes=notes)

    def update_event(
        self,
        event_id: str,
        start: datetime,
        end: datetime,
        title: Optional[str] = None,
        location: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> CalendarEvent:
        return self.adapter.update_event(event_id, start, end, title=title, location=location, notes=notes)

    def delete_event(self, event_id: str) -> None:
        self.adapter.delete_event(event_id)

    def weekly_summary(self, start: datetime, end: datetime) -> Dict[str, object]:
        events = self.list_events(start, end)
        by_day = {}
        for event in events:
            key = event.start.date().isoformat()
            by_day.setdefault(key, []).append(event)
        days = []
        for day_key, day_events in sorted(by_day.items()):
            days.append(
                {
                    "day": day_key,
                    "label": describe_day(day_events[0].start.date()),
                    "count": len(day_events),
                    "events": [event.to_dict() for event in day_events],
                    "headline": "; ".join(format_event_line(event) for event in day_events[:3]),
                }
            )
        return {"total_events": len(events), "days": days, "events": [event.to_dict() for event in events]}
