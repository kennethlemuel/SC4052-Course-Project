from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import date, datetime, time, timedelta
from typing import Iterable, List, Optional, Tuple
from zoneinfo import ZoneInfo

from chief_of_staff.models import CalendarEvent


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def get_tz(tz_name: str) -> ZoneInfo:
    return ZoneInfo(tz_name)


def start_of_week(anchor: datetime) -> datetime:
    return datetime.combine(
        (anchor - timedelta(days=anchor.weekday())).date(),
        time.min,
        tzinfo=anchor.tzinfo,
    )


def end_of_week(anchor: datetime) -> datetime:
    return start_of_week(anchor) + timedelta(days=7)


def daterange(start_day: date, end_day: date) -> Iterable[date]:
    cursor = start_day
    while cursor < end_day:
        yield cursor
        cursor += timedelta(days=1)


def overlap_minutes(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> int:
    start = max(a_start, b_start)
    end = min(a_end, b_end)
    if end <= start:
        return 0
    return int((end - start).total_seconds() // 60)


def sort_events(events: Iterable[CalendarEvent]) -> List[CalendarEvent]:
    return sorted(events, key=lambda event: event.start)


def json_request(method: str, url: str, headers: Optional[dict] = None, payload: Optional[dict] = None) -> dict:
    data = None
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=data, headers=req_headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def parse_duration_minutes(text: str, default: int = 60) -> int:
    lowered = text.lower()
    hour_match = re.search(r"(\d+)\s*(hour|hours|hr|hrs)", lowered)
    minute_match = re.search(r"(\d+)\s*(minute|minutes|min|mins)", lowered)
    total = 0
    if hour_match:
        total += int(hour_match.group(1)) * 60
    if minute_match:
        total += int(minute_match.group(1))
    return total or default


def parse_time_component(raw: str) -> Optional[Tuple[int, int]]:
    text = raw.strip().lower()
    match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    suffix = match.group(3)
    if suffix == "pm" and hour != 12:
        hour += 12
    if suffix == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return None
    return hour, minute


def next_weekday(base: datetime, weekday: int, include_today: bool = True) -> datetime:
    delta = weekday - base.weekday()
    if delta < 0 or (delta == 0 and not include_today):
        delta += 7
    target_day = base.date() + timedelta(days=delta)
    return datetime.combine(target_day, time.min, tzinfo=base.tzinfo)


def parse_relative_date(text: str, now: datetime) -> Optional[datetime]:
    lowered = text.lower()
    if "today" in lowered:
        return datetime.combine(now.date(), time.min, tzinfo=now.tzinfo)
    if "tomorrow" in lowered:
        return datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=now.tzinfo)
    for name, weekday in WEEKDAYS.items():
        if name in lowered:
            include_today = "next " not in lowered
            return next_weekday(now, weekday, include_today=include_today)
    return None


def describe_day(day: date) -> str:
    return day.strftime("%A %d %b")


def format_event_line(event: CalendarEvent) -> str:
    start = event.start.strftime("%a %I:%M %p").lstrip("0")
    end = event.end.strftime("%I:%M %p").lstrip("0")
    return f"{start}-{end}: {event.title}"


def safe_json_loads(raw: bytes) -> dict:
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


class HttpServiceError(RuntimeError):
    pass


def wrap_http_error(exc: Exception) -> HttpServiceError:
    if isinstance(exc, urllib.error.HTTPError):
        body = exc.read().decode("utf-8", errors="ignore")
        return HttpServiceError(f"{exc.code} {exc.reason}: {body}")
    return HttpServiceError(str(exc))
