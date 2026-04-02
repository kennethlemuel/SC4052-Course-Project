from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from chief_of_staff.models import CalendarEvent, CalendarSourceSettings, GoogleOAuthConfig, UserProfile


class JsonStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.events_path = self.root / "events.json"
        self.profile_path = self.root / "profile.json"
        self.calendar_source_path = self.root / "calendar_source.json"
        self.google_oauth_path = self.root / "google_oauth_client.json"

    def load_events(self) -> List[CalendarEvent]:
        if not self.events_path.exists():
            return []
        raw = json.loads(self.events_path.read_text())
        return [self._event_from_dict(item) for item in raw]

    def save_events(self, events: Iterable[CalendarEvent]) -> None:
        payload = [event.to_dict() for event in events]
        self.events_path.write_text(json.dumps(payload, indent=2))

    def load_profile(self) -> UserProfile:
        if not self.profile_path.exists():
            return UserProfile()
        raw = json.loads(self.profile_path.read_text())
        return UserProfile(**raw)

    def save_profile(self, profile: UserProfile) -> None:
        self.profile_path.write_text(json.dumps(profile.__dict__, indent=2))

    def load_calendar_source(self) -> CalendarSourceSettings:
        if not self.calendar_source_path.exists():
            return CalendarSourceSettings()
        raw = json.loads(self.calendar_source_path.read_text())
        return CalendarSourceSettings(**raw)

    def save_calendar_source(self, settings: CalendarSourceSettings) -> None:
        self.calendar_source_path.write_text(json.dumps(settings.__dict__, indent=2))

    def load_google_oauth_config(self) -> GoogleOAuthConfig:
        if not self.google_oauth_path.exists():
            return GoogleOAuthConfig()
        raw = json.loads(self.google_oauth_path.read_text())
        return GoogleOAuthConfig(**raw)

    @staticmethod
    def _event_from_dict(data: dict) -> CalendarEvent:
        return CalendarEvent(
            id=data["id"],
            title=data["title"],
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]),
            location=data.get("location", ""),
            notes=data.get("notes", ""),
            source=data.get("source", "local"),
            travel_buffer_minutes=data.get("travel_buffer_minutes", 0),
            prep_buffer_minutes=data.get("prep_buffer_minutes", 0),
        )
