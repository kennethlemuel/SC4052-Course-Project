from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CalendarEvent:
    id: str
    title: str
    start: datetime
    end: datetime
    location: str = ""
    notes: str = ""
    source: str = "local"
    travel_buffer_minutes: int = 0
    prep_buffer_minutes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["start"] = self.start.isoformat()
        payload["end"] = self.end.isoformat()
        return payload


@dataclass
class UserProfile:
    preferred_focus_hours: int = 2
    day_start_hour: int = 9
    day_end_hour: int = 19
    no_meeting_after_hour: int = 18
    timezone: str = "Asia/Singapore"
    working_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])


@dataclass
class CalendarSourceSettings:
    mode: str = "local"
    access_token: str = ""
    refresh_token: str = ""
    expires_at: str = ""
    calendar_id: str = "primary"

    def to_public_dict(self) -> Dict[str, Any]:
        is_google = self.mode == "google"
        return {
            "mode": self.mode,
            "label": "Google Calendar" if is_google else "Demo calendar",
            "calendar_id": self.calendar_id,
            "connected": bool(self.access_token) if is_google else True,
        }


@dataclass
class GoogleOAuthConfig:
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.redirect_uri)


@dataclass
class LocalLlmConfig:
    provider: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    model: str = "gemma3:4b"
    api_key: str = ""

    def is_configured(self) -> bool:
        return bool(self.provider.strip() and self.base_url.strip() and self.model.strip())


@dataclass
class Suggestion:
    kind: str
    title: str
    detail: str
    confidence: float = 0.5
    related_event_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TimeSlot:
    start: datetime
    end: datetime
    score: float
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "score": self.score,
            "rationale": self.rationale,
        }


@dataclass
class StudyTopic:
    id: str
    name: str
    module: str
    mastery: int
    confidence: int
    importance: int
    last_reviewed: str
    notes: List[str] = field(default_factory=list)
    quiz_average: int = 0
    source_material_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StudyProfile:
    target_readiness: int = 82
    default_study_minutes: int = 90

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AcademicItem:
    id: str
    kind: str
    title: str
    subject: str
    due_date: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
