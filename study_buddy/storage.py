from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from study_buddy.models import CalendarEvent, CalendarSourceSettings, GoogleOAuthConfig, LocalLlmConfig, UserProfile


class JsonStore:
    def __init__(self, root: Path, study_user_id: str = "") -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.events_path = self.root / "events.json"
        self.profile_path = self.root / "profile.json"
        self.calendar_source_path = self.root / "calendar_source.json"
        self.google_oauth_path = self.root / "google_oauth_client.json"
        self.local_llm_config_path = self.root / "local_llm_config.json"
        if study_user_id:
            safe_user_id = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in study_user_id)
            user_root = self.root / "users" / safe_user_id
            user_root.mkdir(parents=True, exist_ok=True)
            self.study_state_path = user_root / "study_state.json"
        else:
            self.study_state_path = self.root / "study_state.json"
        self.auth_state_path = self.root / "auth_state.json"

    def for_study_user(self, user_id: str) -> "JsonStore":
        return JsonStore(self.root, user_id)

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

    def load_local_llm_config(self) -> LocalLlmConfig:
        if self.local_llm_config_path.exists():
            raw = json.loads(self.local_llm_config_path.read_text())
            return LocalLlmConfig(**raw)

        legacy_path = self.root / "ollama_config.json"
        if legacy_path.exists():
            raw = json.loads(legacy_path.read_text())
            return LocalLlmConfig(provider="ollama", **raw)

        return LocalLlmConfig(provider="", base_url="", model="")

    def load_study_state(self) -> Dict[str, object]:
        if not self.study_state_path.exists():
            return {}
        return json.loads(self.study_state_path.read_text())

    def save_study_state(self, payload: Dict[str, object]) -> None:
        self.study_state_path.write_text(json.dumps(payload, indent=2))

    def load_auth_state(self) -> Dict[str, object]:
        if not self.auth_state_path.exists():
            return {}
        return json.loads(self.auth_state_path.read_text())

    def save_auth_state(self, payload: Dict[str, object]) -> None:
        self.auth_state_path.write_text(json.dumps(payload, indent=2))

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
