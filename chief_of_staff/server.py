from __future__ import annotations

import json
import mimetypes
import os
import secrets
from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlencode, urlparse
from typing import Tuple

from chief_of_staff.models import CalendarSourceSettings, GoogleOAuthConfig
from chief_of_staff.services.assistant_service import AssistantService
from chief_of_staff.services.calendar_adapters import build_calendar_adapter
from chief_of_staff.services.calendar_service import CalendarService
from chief_of_staff.services.planner_service import PlannerService
from chief_of_staff.services.profile_service import ProfileService
from chief_of_staff.storage import JsonStore
from chief_of_staff.utils import end_of_week, form_request, get_tz, safe_json_loads, start_of_week, wrap_http_error


ROOT = Path(__file__).resolve().parent.parent
STATIC_ROOT = ROOT / "static"
DATA_ROOT = ROOT / "data"


class AppContext:
    def __init__(self) -> None:
        self.store = JsonStore(DATA_ROOT)
        self.profile_service = ProfileService(self.store)
        self.planner_service = PlannerService()
        self.oauth_config = self._load_oauth_config()
        self.sessions = {}

    def now(self) -> datetime:
        profile = self.profile_service.get_profile()
        return datetime.now(tz=get_tz(profile.timezone))

    def _load_oauth_config(self) -> GoogleOAuthConfig:
        file_config = self.store.load_google_oauth_config()
        return GoogleOAuthConfig(
            client_id=file_config.client_id or os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
            client_secret=file_config.client_secret or os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
            redirect_uri=file_config.redirect_uri or os.getenv("GOOGLE_OAUTH_REDIRECT_URI", ""),
        )

    def ensure_session(self, session_id: str) -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "calendar_source": CalendarSourceSettings(),
                "oauth_state": "",
            }
        return self.sessions[session_id]

    def clear_session_calendar(self, session_id: str) -> None:
        session = self.ensure_session(session_id)
        session["calendar_source"] = CalendarSourceSettings()

    def build_calendar_service(self, session_id: str) -> CalendarService:
        session = self.ensure_session(session_id)
        settings = session["calendar_source"]
        adapter = build_calendar_adapter(
            self.store,
            settings=settings,
            oauth_config=self.oauth_config,
            on_token_update=lambda updated: self._update_session_source(session_id, updated),
        )
        return CalendarService(adapter)

    def build_assistant_service(self, session_id: str) -> AssistantService:
        return AssistantService(self.build_calendar_service(session_id), self.planner_service)

    def calendar_source_info(self, session_id: str) -> dict:
        session = self.ensure_session(session_id)
        settings = session["calendar_source"]
        info = settings.to_public_dict()
        info["provider"] = self.build_calendar_service(session_id).adapter.__class__.__name__
        info["oauth_ready"] = self.oauth_config.is_configured()
        return info

    def start_google_auth(self, session_id: str) -> str:
        if not self.oauth_config.is_configured():
            raise ValueError("Google OAuth is not configured yet.")
        session = self.ensure_session(session_id)
        session["oauth_state"] = secrets.token_urlsafe(24)
        params = {
            "client_id": self.oauth_config.client_id,
            "redirect_uri": self.oauth_config.redirect_uri,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/calendar",
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
            "state": session["oauth_state"],
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    def complete_google_auth(self, session_id: str, state: str, code: str) -> None:
        session = self.ensure_session(session_id)
        if state != session.get("oauth_state"):
            raise ValueError("Google sign-in state did not match. Please try again.")
        payload = {
            "client_id": self.oauth_config.client_id,
            "client_secret": self.oauth_config.client_secret,
            "redirect_uri": self.oauth_config.redirect_uri,
            "grant_type": "authorization_code",
            "code": code,
        }
        try:
            tokens = form_request("https://oauth2.googleapis.com/token", payload)
        except Exception as exc:
            raise ValueError(f"Google sign-in failed: {wrap_http_error(exc)}")
        expires_in = int(tokens.get("expires_in", 3600))
        session["calendar_source"] = CalendarSourceSettings(
            mode="google",
            access_token=tokens.get("access_token", ""),
            refresh_token=tokens.get("refresh_token", ""),
            expires_at=(datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat(),
            calendar_id="primary",
        )
        session["oauth_state"] = ""
        service = self.build_calendar_service(session_id)
        start = start_of_week(self.now())
        end = end_of_week(self.now())
        try:
            service.list_events(start, end)
        except Exception as exc:
            session["calendar_source"] = CalendarSourceSettings()
            raise ValueError(f"Google Calendar connection failed: {exc}")

    def _update_session_source(self, session_id: str, settings: CalendarSourceSettings) -> None:
        session = self.ensure_session(session_id)
        session["calendar_source"] = settings


CONTEXT = AppContext()


class ChiefOfStaffHandler(BaseHTTPRequestHandler):
    server_version = "ChiefOfStaffHTTP/0.1"

    def setup(self) -> None:
        super().setup()
        self._pending_cookie = None
        self._session_id = None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "/index.html":
            self._serve_static("index.html")
            return
        if path.startswith("/static/"):
            self._serve_static(path.removeprefix("/static/"))
            return
        if path == "/calendar/week-summary":
            self._handle_week_summary()
            return
        if path == "/calendar/source":
            self._handle_calendar_source_get()
            return
        if path == "/auth/google/start":
            self._handle_google_auth_start()
            return
        if path == "/auth/google/callback":
            self._handle_google_auth_callback(parsed)
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/assistant/query":
            self._handle_assistant_query()
            return
        if path == "/calendar/events":
            self._handle_create_event()
            return
        if path == "/calendar/source":
            self._handle_calendar_source_post()
            return
        if path == "/planner/suggest-slots":
            self._handle_suggest_slots()
            return
        if path == "/planner/protect-focus-time":
            self._handle_protect_focus()
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def _handle_week_summary(self) -> None:
        session_id = self._ensure_session()
        profile = CONTEXT.profile_service.get_profile()
        now = CONTEXT.now()
        start = start_of_week(now)
        end = end_of_week(now)
        calendar_service = CONTEXT.build_calendar_service(session_id)
        events = calendar_service.weekly_summary(start, end)
        analysis = CONTEXT.planner_service.analyze_week(calendar_service.list_events(start, end), profile, start, end)
        self._send_json({"source": CONTEXT.calendar_source_info(session_id), "summary": events, "analysis": analysis})

    def _handle_calendar_source_get(self) -> None:
        session_id = self._ensure_session()
        self._send_json({"source": CONTEXT.calendar_source_info(session_id)})

    def _handle_calendar_source_post(self) -> None:
        session_id = self._ensure_session()
        payload = self._read_json()
        mode = payload.get("mode", "local")
        if mode != "local":
            self._send_json({"error": "Use the Google connect flow for Google Calendar."}, status=HTTPStatus.BAD_REQUEST)
            return
        CONTEXT.clear_session_calendar(session_id)
        self._send_json({"source": CONTEXT.calendar_source_info(session_id)})

    def _handle_assistant_query(self) -> None:
        session_id = self._ensure_session()
        profile = CONTEXT.profile_service.get_profile()
        payload = self._read_json()
        text = payload.get("text", "")
        if not text.strip():
            self._send_json({"error": "Missing text"}, status=HTTPStatus.BAD_REQUEST)
            return
        assistant_service = CONTEXT.build_assistant_service(session_id)
        result = assistant_service.handle_query(text, CONTEXT.now(), profile)
        self._send_json(result)

    def _handle_create_event(self) -> None:
        session_id = self._ensure_session()
        payload = self._read_json()
        missing = [field for field in ["title", "start", "end"] if field not in payload]
        if missing:
            self._send_json({"error": f"Missing fields: {', '.join(missing)}"}, status=HTTPStatus.BAD_REQUEST)
            return
        calendar_service = CONTEXT.build_calendar_service(session_id)
        event = calendar_service.create_event(
            payload["title"],
            datetime.fromisoformat(payload["start"]),
            datetime.fromisoformat(payload["end"]),
            payload.get("location", ""),
            payload.get("notes", ""),
        )
        self._send_json({"event": event.to_dict()})

    def _handle_suggest_slots(self) -> None:
        session_id = self._ensure_session()
        payload = self._read_json()
        duration = int(payload.get("duration_minutes", 120))
        profile = CONTEXT.profile_service.get_profile()
        now = CONTEXT.now()
        start = start_of_week(now)
        end = end_of_week(now)
        calendar_service = CONTEXT.build_calendar_service(session_id)
        events = calendar_service.list_events(start, end)
        slots = CONTEXT.planner_service.suggest_slots(events, profile, start, end, duration, payload.get("title", "Focus session"))
        self._send_json({"slots": [slot.to_dict() for slot in slots]})

    def _handle_protect_focus(self) -> None:
        session_id = self._ensure_session()
        payload = self._read_json()
        duration = int(payload.get("duration_minutes", 120))
        profile = CONTEXT.profile_service.get_profile()
        now = CONTEXT.now()
        start = start_of_week(now)
        end = end_of_week(now)
        calendar_service = CONTEXT.build_calendar_service(session_id)
        events = calendar_service.list_events(start, end)
        result = CONTEXT.planner_service.protect_focus_time(events, profile, start, end, duration)
        self._send_json(result)

    def _handle_google_auth_start(self) -> None:
        session_id = self._ensure_session()
        try:
            url = CONTEXT.start_google_auth(session_id)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._redirect(url)

    def _handle_google_auth_callback(self, parsed) -> None:
        session_id = self._ensure_session()
        params = parse_qs(parsed.query)
        code = params.get("code", [""])[0]
        state = params.get("state", [""])[0]
        error = params.get("error", [""])[0]
        if error:
            self._redirect(f"/?google_auth_error={error}")
            return
        try:
            CONTEXT.complete_google_auth(session_id, state=state, code=code)
        except ValueError as exc:
            self._redirect(f"/?google_auth_error={quote(str(exc))}")
            return
        self._redirect("/?google_auth=success")

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
        self._write_pending_cookie()
        self.send_header("Content-Type", content_type or "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(file_path.read_bytes())

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self._write_pending_cookie()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.FOUND)
        self._write_pending_cookie()
        self.send_header("Location", location)
        self.end_headers()

    def _ensure_session(self) -> str:
        if self._session_id:
            return self._session_id
        cookies = SimpleCookie(self.headers.get("Cookie"))
        session_cookie = cookies.get("chief_session")
        if session_cookie and session_cookie.value in CONTEXT.sessions:
            self._session_id = session_cookie.value
        else:
            self._session_id = secrets.token_urlsafe(24)
            self._pending_cookie = f"chief_session={self._session_id}; Path=/; HttpOnly; SameSite=Lax"
        CONTEXT.ensure_session(self._session_id)
        return self._session_id

    def _write_pending_cookie(self) -> None:
        if self._pending_cookie:
            self.send_header("Set-Cookie", self._pending_cookie)
            self._pending_cookie = None

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
