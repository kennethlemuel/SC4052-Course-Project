from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Dict, List

from study_buddy.models import CalendarEvent, Suggestion, TimeSlot, UserProfile
from study_buddy.utils import daterange, overlap_minutes, sort_events


class PlannerService:
    def analyze_week(self, events: List[CalendarEvent], profile: UserProfile, week_start: datetime, week_end: datetime) -> Dict[str, object]:
        ordered = sort_events(events)
        suggestions: List[Suggestion] = []
        overload_days = []
        conflicts = self.detect_conflicts(ordered)
        fragmented_days = self.detect_fragmented_days(ordered)

        for day_info in self._day_metrics(ordered, profile, week_start, week_end):
            if day_info["booked_hours"] >= 6:
                overload_days.append(day_info)
                suggestions.append(
                    Suggestion(
                        kind="overload",
                        title=f"{day_info['label']} looks overloaded",
                        detail=f"{day_info['label']} has {day_info['booked_hours']:.1f} booked hours across {day_info['event_count']} events.",
                        confidence=0.84,
                    )
                )
            if day_info["focus_blocks"] == 0 and day_info["event_count"] >= 3:
                suggestions.append(
                    Suggestion(
                        kind="focus",
                        title=f"No focus block protected on {day_info['label']}",
                        detail="Add a 2-hour deep-work block before more meetings fill the day.",
                        confidence=0.71,
                    )
                )

        for event_a, event_b in conflicts:
            suggestions.append(
                Suggestion(
                    kind="conflict",
                    title="Schedule conflict detected",
                    detail=f"{event_a.title} overlaps with {event_b.title}.",
                    confidence=0.95,
                    related_event_id=event_a.id,
                )
            )

        for label, event_count, gap_minutes in fragmented_days:
            suggestions.append(
                Suggestion(
                    kind="fragmentation",
                    title=f"{label} is highly fragmented",
                    detail=f"{event_count} events are split by {gap_minutes} total minutes of awkward gaps.",
                    confidence=0.66,
                )
            )

        return {
            "overload_days": overload_days,
            "conflicts": [{"left": a.to_dict(), "right": b.to_dict()} for a, b in conflicts],
            "suggestions": [suggestion.to_dict() for suggestion in suggestions],
        }

    def suggest_slots(
        self,
        events: List[CalendarEvent],
        profile: UserProfile,
        week_start: datetime,
        week_end: datetime,
        duration_minutes: int,
        title: str = "Focus session",
    ) -> List[TimeSlot]:
        ordered = sort_events(events)
        slots: List[TimeSlot] = []
        for day in daterange(week_start.date(), week_end.date()):
            if day.weekday() not in profile.working_days:
                continue
            day_start = datetime.combine(day, time(profile.day_start_hour, 0), tzinfo=week_start.tzinfo)
            day_end = datetime.combine(day, time(profile.day_end_hour, 0), tzinfo=week_start.tzinfo)
            day_events = [event for event in ordered if event.start.date() == day]
            cursor = day_start
            for event in day_events + [CalendarEvent(id="sentinel", title=title, start=day_end, end=day_end)]:
                if event.start > cursor:
                    gap = int((event.start - cursor).total_seconds() // 60)
                    if gap >= duration_minutes:
                        end = cursor + timedelta(minutes=duration_minutes)
                        slots.append(
                            TimeSlot(
                                start=cursor,
                                end=end,
                                score=self._slot_score(cursor, end, day_events, profile),
                                rationale=self._slot_rationale(cursor, end, day_events, profile),
                            )
                        )
                cursor = max(cursor, event.end)
        return sorted(slots, key=lambda slot: slot.score, reverse=True)[:5]

    def protect_focus_time(
        self,
        events: List[CalendarEvent],
        profile: UserProfile,
        week_start: datetime,
        week_end: datetime,
        duration_minutes: int,
    ) -> Dict[str, object]:
        suggestions = self.suggest_slots(events, profile, week_start, week_end, duration_minutes, title="Focus block")
        if not suggestions:
            return {"created": False, "reason": "No free focus slot found this week.", "slot": None}
        top = suggestions[0]
        return {
            "created": False,
            "reason": "Best focus block identified. Confirm it before writing to the calendar.",
            "slot": top.to_dict(),
        }

    @staticmethod
    def detect_conflicts(events: List[CalendarEvent]) -> List[tuple]:
        conflicts = []
        for left, right in zip(events, events[1:]):
            if right.start < left.end:
                conflicts.append((left, right))
        return conflicts

    @staticmethod
    def detect_fragmented_days(events: List[CalendarEvent]) -> List[tuple]:
        by_day = {}
        for event in events:
            by_day.setdefault(event.start.date(), []).append(event)
        fragmented = []
        for day, day_events in by_day.items():
            ordered = sort_events(day_events)
            gaps = 0
            for left, right in zip(ordered, ordered[1:]):
                gap = int((right.start - left.end).total_seconds() // 60)
                if 20 <= gap <= 90:
                    gaps += gap
            if len(day_events) >= 3 and gaps >= 90:
                fragmented.append((day.strftime("%A"), len(day_events), gaps))
        return fragmented

    def _day_metrics(self, events: List[CalendarEvent], profile: UserProfile, week_start: datetime, week_end: datetime) -> List[dict]:
        metrics = []
        for day in daterange(week_start.date(), week_end.date()):
            day_events = [event for event in events if event.start.date() == day]
            if not day_events:
                continue
            booked_minutes = sum(int((event.end - event.start).total_seconds() // 60) for event in day_events)
            focus_blocks = len(self.suggest_slots(day_events, profile, datetime.combine(day, time.min, tzinfo=week_start.tzinfo), datetime.combine(day + timedelta(days=1), time.min, tzinfo=week_start.tzinfo), profile.preferred_focus_hours * 60))
            metrics.append(
                {
                    "day": day.isoformat(),
                    "label": day.strftime("%A"),
                    "event_count": len(day_events),
                    "booked_hours": booked_minutes / 60,
                    "focus_blocks": focus_blocks,
                }
            )
        return metrics

    def _slot_score(self, start: datetime, end: datetime, day_events: List[CalendarEvent], profile: UserProfile) -> float:
        midday_bonus = 1.0 if 10 <= start.hour <= 15 else 0.5
        late_penalty = 0.6 if end.hour >= profile.no_meeting_after_hour else 1.0
        adjacency_penalty = 1.0
        for event in day_events:
            gap = min(
                abs(overlap_minutes(start, end, event.start - timedelta(minutes=15), event.start)),
                abs(overlap_minutes(start, end, event.end, event.end + timedelta(minutes=15))),
            )
            if gap:
                adjacency_penalty -= 0.1
        return round((midday_bonus + late_penalty + adjacency_penalty) * ((end - start).total_seconds() / 3600), 2)

    def _slot_rationale(self, start: datetime, end: datetime, day_events: List[CalendarEvent], profile: UserProfile) -> str:
        parts = []
        if 10 <= start.hour <= 15:
            parts.append("inside a high-energy daytime window")
        if end.hour < profile.no_meeting_after_hour:
            parts.append("ends before the user's no-meeting threshold")
        if not day_events:
            parts.append("keeps the day lightly scheduled")
        return ", ".join(parts) or "usable free slot"
