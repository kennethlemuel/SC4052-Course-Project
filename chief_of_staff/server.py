from __future__ import annotations

import json
import mimetypes
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Tuple

from chief_of_staff.models import CalendarSourceSettings
from chief_of_staff.services.assistant_service import AssistantService
from chief_of_staff.services.calendar_adapters import build_calendar_adapter
from chief_of_staff.services.calendar_service import CalendarService
from chief_of_staff.services.planner_service import PlannerService
from chief_of_staff.services.profile_service import ProfileService
from chief_of_staff.storage import JsonStore
from chief_of_staff.utils import end_of_week, get_tz, safe_json_loads, start_of_week


ROOT = Path(__file__).resolve().parent.parent
STATIC_ROOT = ROOT / "static"
DATA_ROOT = ROOT / "data"


class AppContext:
    def __init__(self) -> None:
        self.store = JsonStore(DATA_ROOT)
        self.profile_service = ProfileService(self.store)
        self.planner_service = PlannerService()
        self.calendar_settings = self.store.load_calendar_source()
        self.refresh_calendar_service()

    def now(self) -> datetime:
        profile = self.profile_service.get_profile()
        return datetime.now(tz=get_tz(profile.timezone))

    def refresh_calendar_service(self) -> None:
        self.calendar_service = CalendarService(build_calendar_adapter(self.store, self.calendar_settings))
        self.assistant_service = AssistantService(self.calendar_service, self.planner_service)

    def calendar_source_info(self) -> dict:
        info = self.calendar_settings.to_public_dict()
        info["provider"] = self.calendar_service.adapter.__class__.__name__
        return info

    def set_calendar_source(self, settings: CalendarSourceSettings) -> dict:
        if settings.mode not in {"local", "google"}:
            raise ValueError("Unsupported calendar mode.")
        if settings.mode == "google" and not settings.access_token.strip():
            raise ValueError("Google Calendar requires an access token.")
        previous = self.calendar_settings
        self.calendar_settings = settings
        self.refresh_calendar_service()
        if settings.mode == "google":
            start = start_of_week(self.now())
            end = end_of_week(self.now())
            try:
                self.calendar_service.list_events(start, end)
            except Exception as exc:
                self.calendar_settings = previous
                self.refresh_calendar_service()
                raise ValueError(f"Google Calendar connection failed: {exc}")
        self.store.save_calendar_source(settings)
        return self.calendar_source_info()


CONTEXT = AppContext()


class ChiefOfStaffHandler(BaseHTTPRequestHandler):
    server_version = "ChiefOfStaffHTTP/0.1"

    def do_GET(self) -> None:
        if self.path == "/" or self.path == "/index.html":
            self._serve_static("index.html")
            return
        if self.path.startswith("/static/"):
            self._serve_static(self.path.removeprefix("/static/"))
            return
        if self.path == "/calendar/week-summary":
            self._handle_week_summary()
            return
        if self.path == "/calendar/source":
            self._handle_calendar_source_get()
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path == "/assistant/query":
            self._handle_assistant_query()
            return
        if self.path == "/calendar/events":
            self._handle_create_event()
            return
        if self.path == "/calendar/source":
            self._handle_calendar_source_post()
            return
        if self.path == "/planner/suggest-slots":
            self._handle_suggest_slots()
            return
        if self.path == "/planner/protect-focus-time":
            self._handle_protect_focus()
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def _handle_week_summary(self) -> None:
        profile = CONTEXT.profile_service.get_profile()
        now = CONTEXT.now()
        start = start_of_week(now)
        end = end_of_week(now)
        events = CONTEXT.calendar_service.weekly_summary(start, end)
        analysis = CONTEXT.planner_service.analyze_week(
            CONTEXT.calendar_service.list_events(start, end), profile, start, end
        )
        self._send_json({"source": CONTEXT.calendar_source_info(), "summary": events, "analysis": analysis})

    def _handle_calendar_source_get(self) -> None:
        self._send_json({"source": CONTEXT.calendar_source_info()})

    def _handle_calendar_source_post(self) -> None:
        payload = self._read_json()
        settings = CalendarSourceSettings(
            mode=payload.get("mode", "local"),
            access_token=payload.get("access_token", "").strip(),
            calendar_id=payload.get("calendar_id", "primary").strip() or "primary",
        )
        try:
            source = CONTEXT.set_calendar_source(settings)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json({"source": source})

    def _handle_assistant_query(self) -> None:
        profile = CONTEXT.profile_service.get_profile()
        payload = self._read_json()
        text = payload.get("text", "")
        if not text.strip():
            self._send_json({"error": "Missing text"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = CONTEXT.assistant_service.handle_query(text, CONTEXT.now(), profile)
        self._send_json(result)

    def _handle_create_event(self) -> None:
        payload = self._read_json()
        missing = [field for field in ["title", "start", "end"] if field not in payload]
        if missing:
            self._send_json({"error": f"Missing fields: {', '.join(missing)}"}, status=HTTPStatus.BAD_REQUEST)
            return
        event = CONTEXT.calendar_service.create_event(
            payload["title"],
            datetime.fromisoformat(payload["start"]),
            datetime.fromisoformat(payload["end"]),
            payload.get("location", ""),
            payload.get("notes", ""),
        )
        self._send_json({"event": event.to_dict()})

    def _handle_suggest_slots(self) -> None:
        payload = self._read_json()
        duration = int(payload.get("duration_minutes", 120))
        profile = CONTEXT.profile_service.get_profile()
        now = CONTEXT.now()
        start = start_of_week(now)
        end = end_of_week(now)
        events = CONTEXT.calendar_service.list_events(start, end)
        slots = CONTEXT.planner_service.suggest_slots(events, profile, start, end, duration, payload.get("title", "Focus session"))
        self._send_json({"slots": [slot.to_dict() for slot in slots]})

    def _handle_protect_focus(self) -> None:
        payload = self._read_json()
        duration = int(payload.get("duration_minutes", 120))
        profile = CONTEXT.profile_service.get_profile()
        now = CONTEXT.now()
        start = start_of_week(now)
        end = end_of_week(now)
        events = CONTEXT.calendar_service.list_events(start, end)
        result = CONTEXT.planner_service.protect_focus_time(events, profile, start, end, duration)
        self._send_json(result)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        return safe_json_loads(raw)

    def _serve_static(self, relative_path: str) -> None:
        file_path = (STATIC_ROOT / relative_path).resolve()
        if not file_path.is_file() or STATIC_ROOT not in file_path.parents and file_path != STATIC_ROOT / "index.html":
            self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return
        content_type, _ = mimetypes.guess_type(str(file_path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(file_path.read_bytes())

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args: Tuple[object, ...]) -> None:
        return


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    _seed_demo_data()
    server = ThreadingHTTPServer((host, port), ChiefOfStaffHandler)
    print(f"Voice Calendar Chief-of-Staff running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()


def _seed_demo_data() -> None:
    if CONTEXT.store.events_path.exists():
        return
    now = CONTEXT.now()
    monday = start_of_week(now)
    demo_events = [
        {
            "id": "demo-1",
            "title": "Cloud Computing Lecture",
            "start": (monday + timedelta(days=1, hours=10)).isoformat(),
            "end": (monday + timedelta(days=1, hours=12)).isoformat(),
            "location": "LT1A",
            "notes": "Project brainstorming with notes afterward.",
            "source": "local",
            "travel_buffer_minutes": 20,
            "prep_buffer_minutes": 15,
        },
        {
            "id": "demo-2",
            "title": "Project Sync",
            "start": (monday + timedelta(days=2, hours=13)).isoformat(),
            "end": (monday + timedelta(days=2, hours=14)).isoformat(),
            "location": "Zoom",
            "notes": "Discuss assistant architecture.",
            "source": "local",
            "travel_buffer_minutes": 0,
            "prep_buffer_minutes": 10,
        },
        {
            "id": "demo-3",
            "title": "Gym",
            "start": (monday + timedelta(days=2, hours=18)).isoformat(),
            "end": (monday + timedelta(days=2, hours=19)).isoformat(),
            "location": "Hall Gym",
            "notes": "",
            "source": "local",
            "travel_buffer_minutes": 10,
            "prep_buffer_minutes": 0,
        },
        {
            "id": "demo-4",
            "title": "TA Consultation",
            "start": (monday + timedelta(days=3, hours=11)).isoformat(),
            "end": (monday + timedelta(days=3, hours=12)).isoformat(),
            "location": "TR+15",
            "notes": "Ask about report expectations.",
            "source": "local",
            "travel_buffer_minutes": 15,
            "prep_buffer_minutes": 15,
        },
        {
            "id": "demo-5",
            "title": "Dinner with Friends",
            "start": (monday + timedelta(days=4, hours=19)).isoformat(),
            "end": (monday + timedelta(days=4, hours=21)).isoformat(),
            "location": "North Spine",
            "notes": "",
            "source": "local",
            "travel_buffer_minutes": 20,
            "prep_buffer_minutes": 0,
        },
    ]
    CONTEXT.store.events_path.parent.mkdir(parents=True, exist_ok=True)
    CONTEXT.store.events_path.write_text(json.dumps(demo_events, indent=2))
    if not CONTEXT.store.profile_path.exists():
        CONTEXT.store.save_profile(CONTEXT.profile_service.get_profile())
