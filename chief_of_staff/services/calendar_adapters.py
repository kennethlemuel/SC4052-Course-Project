from __future__ import annotations

import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from chief_of_staff.models import CalendarEvent, CalendarSourceSettings, GoogleOAuthConfig
from chief_of_staff.storage import JsonStore
from chief_of_staff.utils import form_request, json_request, wrap_http_error


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
    def __init__(
        self,
        access_token: str,
        calendar_id: str = "primary",
        refresh_token: str = "",
        expires_at: str = "",
        oauth_config: Optional[GoogleOAuthConfig] = None,
        on_token_update=None,
    ) -> None:
        self.access_token = access_token
        self.calendar_id = calendar_id
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.oauth_config = oauth_config or GoogleOAuthConfig()
        self.on_token_update = on_token_update
        self.base_url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}"

    def list_events(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        self._ensure_access_token()
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
        self._ensure_access_token()
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

    def _ensure_access_token(self) -> None:
        if not self.refresh_token or not self.oauth_config.is_configured():
            return
        if not self.expires_at:
            return
        expires_at = datetime.fromisoformat(self.expires_at)
        if expires_at - timedelta(seconds=60) > datetime.now(timezone.utc):
            return
        payload = {
            "client_id": self.oauth_config.client_id,
            "client_secret": self.oauth_config.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        try:
            refreshed = form_request("https://oauth2.googleapis.com/token", payload)
        except Exception as exc:
            raise wrap_http_error(exc)
        self.access_token = refreshed["access_token"]
        expires_in = int(refreshed.get("expires_in", 3600))
        self.expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
        if self.on_token_update:
            self.on_token_update(
                CalendarSourceSettings(
                    mode="google",
                    access_token=self.access_token,
                    refresh_token=self.refresh_token,
                    expires_at=self.expires_at,
                    calendar_id=self.calendar_id,
                )
            )


def build_calendar_adapter(
    store: JsonStore,
    settings: Optional[CalendarSourceSettings] = None,
    oauth_config: Optional[GoogleOAuthConfig] = None,
    on_token_update=None,
) -> CalendarAdapter:
    resolved = settings or store.load_calendar_source()
    access_token = resolved.access_token or os.getenv("GOOGLE_CALENDAR_ACCESS_TOKEN", "")
    calendar_id = resolved.calendar_id or os.getenv("GOOGLE_CALENDAR_ID", "primary")
    if not store.calendar_source_path.exists() and access_token:
        return GoogleCalendarAdapter(access_token=access_token, calendar_id=calendar_id, oauth_config=oauth_config)
    if resolved.mode == "google" and access_token:
        return GoogleCalendarAdapter(
            access_token=access_token,
            calendar_id=calendar_id,
            refresh_token=resolved.refresh_token,
            expires_at=resolved.expires_at,
            oauth_config=oauth_config,
            on_token_update=on_token_update,
        )
    return LocalCalendarAdapter(store)
