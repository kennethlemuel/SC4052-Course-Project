from __future__ import annotations

import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from chief_of_staff.models import CalendarEvent, CalendarSourceSettings
from chief_of_staff.storage import JsonStore
from chief_of_staff.utils import json_request, wrap_http_error


class CalendarAdapter(ABC):
    @abstractmethod
    def list_events(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        raise NotImplementedError

    @abstractmethod
    def create_event(self, title: str, start: datetime, end: datetime, location: str = "", notes: str = "") -> CalendarEvent:
        raise NotImplementedError


class LocalCalendarAdapter(CalendarAdapter):
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def list_events(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        events = self.store.load_events()
        return [event for event in events if event.end > start and event.start < end]

    def create_event(self, title: str, start: datetime, end: datetime, location: str = "", notes: str = "") -> CalendarEvent:
        events = self.store.load_events()
        event = CalendarEvent(
            id=str(uuid.uuid4()),
            title=title,
            start=start,
            end=end,
            location=location,
            notes=notes,
            source="local",
        )
        events.append(event)
        self.store.save_events(events)
        return event


class GoogleCalendarAdapter(CalendarAdapter):
    def __init__(self, access_token: str, calendar_id: str = "primary") -> None:
        self.access_token = access_token
        self.calendar_id = calendar_id
        self.base_url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}"

    def list_events(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        url = (
            f"{self.base_url}/events"
            f"?singleEvents=true&orderBy=startTime"
            f"&timeMin={start.isoformat()}&timeMax={end.isoformat()}"
        )
        try:
            raw = json_request("GET", url, headers=self._headers())
        except Exception as exc:
            raise wrap_http_error(exc)
        items = raw.get("items", [])
        events = []
        for item in items:
            start_raw = item.get("start", {}).get("dateTime")
            end_raw = item.get("end", {}).get("dateTime")
            if not start_raw or not end_raw:
                continue
            events.append(
                CalendarEvent(
                    id=item["id"],
                    title=item.get("summary", "Untitled event"),
                    start=datetime.fromisoformat(start_raw.replace("Z", "+00:00")),
                    end=datetime.fromisoformat(end_raw.replace("Z", "+00:00")),
                    location=item.get("location", ""),
                    notes=item.get("description", ""),
                    source="google",
                )
            )
        return events

    def create_event(self, title: str, start: datetime, end: datetime, location: str = "", notes: str = "") -> CalendarEvent:
        payload = {
            "summary": title,
            "location": location,
            "description": notes,
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": end.isoformat()},
        }
        try:
            raw = json_request("POST", f"{self.base_url}/events", headers=self._headers(), payload=payload)
        except Exception as exc:
            raise wrap_http_error(exc)
        return CalendarEvent(
            id=raw["id"],
            title=raw.get("summary", title),
            start=datetime.fromisoformat(raw["start"]["dateTime"].replace("Z", "+00:00")),
            end=datetime.fromisoformat(raw["end"]["dateTime"].replace("Z", "+00:00")),
            location=raw.get("location", location),
            notes=raw.get("description", notes),
            source="google",
        )

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}


def build_calendar_adapter(store: JsonStore, settings: Optional[CalendarSourceSettings] = None) -> CalendarAdapter:
    resolved = settings or store.load_calendar_source()
    access_token = resolved.access_token or os.getenv("GOOGLE_CALENDAR_ACCESS_TOKEN", "")
    calendar_id = resolved.calendar_id or os.getenv("GOOGLE_CALENDAR_ID", "primary")
    if not store.calendar_source_path.exists() and access_token:
        return GoogleCalendarAdapter(access_token=access_token, calendar_id=calendar_id)
    if resolved.mode == "google" and access_token:
        return GoogleCalendarAdapter(access_token=access_token, calendar_id=calendar_id)
    return LocalCalendarAdapter(store)
