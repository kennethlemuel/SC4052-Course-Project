from __future__ import annotations

import cgi
import json
import mimetypes
from io import BytesIO
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Tuple
from urllib.parse import parse_qs, urlparse

from pypdf import PdfReader

from chief_of_staff.services.auth_service import AuthService, SEEDED_USER
from chief_of_staff.services.spotify_service import SpotifyService
from chief_of_staff.services.study_strategy_service import StudyStrategyService
from chief_of_staff.storage import JsonStore
from chief_of_staff.utils import safe_json_loads

mimetypes.add_type("font/ttf", ".ttf")
mimetypes.add_type("font/otf", ".otf")
mimetypes.add_type("font/woff", ".woff")
mimetypes.add_type("font/woff2", ".woff2")

ROOT = Path(__file__).resolve().parent.parent
STATIC_ROOT = ROOT / "static"
DATA_ROOT = ROOT / "data"


class AppContext:
    def __init__(self) -> None:
        self.store = JsonStore(DATA_ROOT)
        self.auth_service = AuthService(self.store)
        self.study_services: dict[str, StudyStrategyService] = {}
        self._migrate_seeded_user_state()
        self.spotify_service = SpotifyService(DATA_ROOT)

    def study_service_for_user(self, user_id: str) -> StudyStrategyService:
        if user_id not in self.study_services:
            self.study_services[user_id] = StudyStrategyService(
                self.store.for_study_user(user_id),
                seed_demo=user_id == SEEDED_USER["id"],
            )
        return self.study_services[user_id]

    def _migrate_seeded_user_state(self) -> None:
        legacy_path = self.store.study_state_path
        seeded_store = self.store.for_study_user(SEEDED_USER["id"])
        if legacy_path.exists() and not seeded_store.study_state_path.exists():
            seeded_store.save_study_state(self.store.load_study_state())


CONTEXT = AppContext()


class StudyStrategyHandler(BaseHTTPRequestHandler):
    server_version = "StudyStrategyHTTP/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "/index.html":
            self._serve_static("index.html")
            return
        if path.startswith("/static/"):
            self._serve_static(path.removeprefix("/static/"))
            return
        if path == "/auth/session":
            self._send_json(CONTEXT.auth_service.status(self._auth_token()))
            return
        if self._requires_auth(path) and not self._is_authenticated():
            self._send_json({"error": "Authentication required."}, status=HTTPStatus.UNAUTHORIZED)
            return
        if path == "/study/dashboard":
            self._send_json(self._study_service().get_dashboard())
            return
        if path == "/assistant/tabs":
            self._send_json(self._study_service().get_coach_tabs())
            return
        if path == "/spotify/login":
            self._handle_spotify_login()
            return
        if path == "/spotify/callback":
            self._handle_spotify_callback(parsed.query)
            return
        if path == "/spotify/status":
            self._send_json(CONTEXT.spotify_service.status())
            return
        if path == "/spotify/access-token":
            self._handle_spotify_access_token()
            return
        if path == "/spotify/library":
            self._handle_spotify_library()
            return
        if path == "/spotify/search":
            self._handle_spotify_search(parsed.query)
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/auth/login":
            self._handle_auth_login()
            return
        if path == "/auth/register":
            self._handle_auth_register()
            return
        if path == "/auth/logout":
            self._handle_auth_logout()
            return
        if path == "/auth/forgot-password":
            self._handle_auth_forgot_password()
            return
        if path == "/auth/reset-password":
            self._handle_auth_reset_password()
            return
        if self._requires_auth(path) and not self._is_authenticated():
            self._send_json({"error": "Authentication required."}, status=HTTPStatus.UNAUTHORIZED)
            return
        if path == "/assistant/query":
            self._handle_coach_query()
            return
        if path == "/assistant/tabs":
            self._handle_coach_tabs()
            return
        if path == "/study/plan":
            self._handle_plan()
            return
        if path == "/study/panic-mode":
            self._handle_panic_mode()
            return
        if path == "/study/check-in":
            self._handle_check_in()
            return
        if path == "/study/materials":
            self._handle_materials()
            return
        if path == "/study/materials/delete":
            self._handle_material_delete()
            return
        if path == "/study/materials/rename":
            self._handle_material_rename()
            return
        if path == "/study/academic-items":
            self._handle_academic_item()
            return
        if path == "/study/academic-items/delete":
            self._handle_academic_item_delete()
            return
        if path == "/study/academic-items/update":
            self._handle_academic_item_update()
            return
        if path == "/study/target":
            self._handle_target_readiness()
            return
        if path == "/study/focus":
            self._handle_focus_item()
            return
        if path == "/study/materials/upload":
            self._handle_material_upload()
            return
        if path == "/spotify/disconnect":
            self._send_json(CONTEXT.spotify_service.disconnect())
            return
        if path == "/spotify/transfer-playback":
            self._handle_spotify_transfer_playback()
            return
        if path == "/spotify/play":
            self._handle_spotify_play()
            return
        if path == "/spotify/pause":
            self._handle_spotify_pause()
            return
        if path == "/spotify/shuffle":
            self._handle_spotify_shuffle()
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def _handle_auth_login(self) -> None:
        payload = self._read_json()
        try:
            result = CONTEXT.auth_service.login(
                str(payload.get("identifier", "")).strip(),
                str(payload.get("password", "")),
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_auth_register(self) -> None:
        payload = self._read_json()
        try:
            result = CONTEXT.auth_service.register(
                str(payload.get("email", "")).strip(),
                str(payload.get("username", "")).strip(),
                str(payload.get("password", "")),
                str(payload.get("password_confirm", "")),
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_auth_logout(self) -> None:
        self._send_json(CONTEXT.auth_service.logout(self._auth_token()))

    def _handle_auth_forgot_password(self) -> None:
        payload = self._read_json()
        self._send_json(CONTEXT.auth_service.forgot_password(str(payload.get("email", "")).strip(), self._base_url()))

    def _handle_auth_reset_password(self) -> None:
        payload = self._read_json()
        try:
            result = CONTEXT.auth_service.reset_password(
                str(payload.get("token", "")).strip(),
                str(payload.get("password", "")),
                str(payload.get("password_confirm", "")),
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_spotify_login(self) -> None:
        try:
            self._redirect(CONTEXT.spotify_service.login_url())
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_spotify_callback(self, raw_query: str) -> None:
        params = parse_qs(raw_query)
        error = str(params.get("error", [""])[0])
        if error:
            self._redirect("/?spotify=error")
            return
        code = str(params.get("code", [""])[0])
        state = str(params.get("state", [""])[0])
        if not code or not state:
            self._redirect("/?spotify=missing")
            return
        try:
            CONTEXT.spotify_service.handle_callback(code, state)
        except ValueError as exc:
            self._redirect(f"/?spotify=error&spotify_message={self._url_quote(str(exc))}")
            return
        self._redirect("/?spotify=connected")

    def _handle_spotify_access_token(self) -> None:
        try:
            self._send_json(CONTEXT.spotify_service.access_token())
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_spotify_transfer_playback(self) -> None:
        payload = self._read_json()
        try:
            result = CONTEXT.spotify_service.transfer_playback(
                str(payload.get("device_id", "")).strip(),
                bool(payload.get("play", False)),
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_spotify_library(self) -> None:
        try:
            self._send_json(CONTEXT.spotify_service.library())
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_spotify_search(self, raw_query: str) -> None:
        params = parse_qs(raw_query)
        query = str(params.get("q", [""])[0])
        try:
            self._send_json(CONTEXT.spotify_service.search(query))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_spotify_play(self) -> None:
        payload = self._read_json()
        try:
            result = CONTEXT.spotify_service.play(
                str(payload.get("device_id", "")).strip(),
                str(payload.get("uri", "")).strip(),
                str(payload.get("context_uri", "")).strip(),
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_spotify_pause(self) -> None:
        payload = self._read_json()
        try:
            result = CONTEXT.spotify_service.pause(str(payload.get("device_id", "")).strip())
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_spotify_shuffle(self) -> None:
        payload = self._read_json()
        try:
            result = CONTEXT.spotify_service.shuffle(
                str(payload.get("device_id", "")).strip(),
                bool(payload.get("state", False)),
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_coach_query(self) -> None:
        payload = self._read_json()
        text = payload.get("text", "").strip()
        if not text:
            self._send_json({"error": "Missing text"}, status=HTTPStatus.BAD_REQUEST)
            return
        tab_id = str(payload.get("tab_id", "")).strip()
        result = self._study_service().coach_reply(text, tab_id)
        self._send_json(result)

    def _handle_coach_tabs(self) -> None:
        payload = self._read_json()
        action = str(payload.get("action", "")).strip()
        try:
            if action == "create":
                result = self._study_service().create_coach_tab(str(payload.get("title", "")).strip())
            elif action == "rename":
                result = self._study_service().rename_coach_tab(
                    str(payload.get("tab_id", "")).strip(),
                    str(payload.get("title", "")).strip(),
                )
            elif action == "delete":
                result = self._study_service().delete_coach_tab(str(payload.get("tab_id", "")).strip())
            elif action == "activate":
                result = self._study_service().set_active_coach_tab(str(payload.get("tab_id", "")).strip())
            else:
                self._send_json({"error": "Unknown tab action."}, status=HTTPStatus.BAD_REQUEST)
                return
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_plan(self) -> None:
        payload = self._read_json()
        try:
            minutes = int(float(payload.get("minutes", 90) or 90))
        except (TypeError, ValueError):
            minutes = 90
        material_ids = payload.get("material_ids", [])
        if not isinstance(material_ids, list):
            material_ids = []
        self._send_json(self._study_service().build_plan(minutes, [str(item) for item in material_ids], save_request=True))

    def _handle_panic_mode(self) -> None:
        payload = self._read_json()
        horizon = payload.get("horizon", "tonight")
        self._send_json(self._study_service().build_panic_mode(horizon))

    def _handle_check_in(self) -> None:
        payload = self._read_json()
        required = ["topic_id", "confidence", "quiz_score", "minutes_studied"]
        missing = [field for field in required if field not in payload]
        if missing:
            self._send_json({"error": f"Missing fields: {', '.join(missing)}"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = self._study_service().log_check_in(
                payload["topic_id"],
                int(payload["confidence"]),
                int(payload["quiz_score"]),
                int(payload["minutes_studied"]),
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_materials(self) -> None:
        payload = self._read_json()
        title = payload.get("title", "").strip()
        text = payload.get("text", "").strip()
        academic_item_id = str(payload.get("academic_item_id", "")).strip()
        if not title or not text:
            self._send_json({"error": "Both title and text are required."}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = self._study_service().import_material(title, text, academic_item_id)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_material_delete(self) -> None:
        payload = self._read_json()
        material_id = str(payload.get("material_id", "")).strip()
        if not material_id:
            self._send_json({"error": "Missing material_id"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = self._study_service().delete_material(material_id)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_material_rename(self) -> None:
        payload = self._read_json()
        material_id = str(payload.get("material_id", "")).strip()
        title = str(payload.get("title", "")).strip()
        if not material_id:
            self._send_json({"error": "Missing material_id"}, status=HTTPStatus.BAD_REQUEST)
            return
        if not title:
            self._send_json({"error": "Missing title"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = self._study_service().rename_material(material_id, title)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_academic_item(self) -> None:
        payload = self._read_json()
        required = ["title", "subject", "due_date", "kind"]
        missing = [field for field in required if not str(payload.get(field, "")).strip()]
        if missing:
            self._send_json({"error": f"Missing fields: {', '.join(missing)}"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = self._study_service().add_academic_item(
            title=str(payload["title"]).strip(),
            subject=str(payload["subject"]).strip(),
            due_date=str(payload["due_date"]).strip(),
            kind=str(payload["kind"]).strip(),
        )
        self._send_json(result)

    def _handle_academic_item_delete(self) -> None:
        payload = self._read_json()
        item_id = str(payload.get("item_id", "")).strip()
        if not item_id:
            self._send_json({"error": "Missing item_id"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = self._study_service().delete_academic_item(item_id)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_academic_item_update(self) -> None:
        payload = self._read_json()
        required = ["item_id", "title", "subject", "due_date", "kind"]
        missing = [field for field in required if not str(payload.get(field, "")).strip()]
        if missing:
            self._send_json({"error": f"Missing fields: {', '.join(missing)}"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = self._study_service().update_academic_item(
                item_id=str(payload["item_id"]).strip(),
                title=str(payload["title"]).strip(),
                subject=str(payload["subject"]).strip(),
                due_date=str(payload["due_date"]).strip(),
                kind=str(payload["kind"]).strip(),
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_target_readiness(self) -> None:
        payload = self._read_json()
        try:
            target = int(float(payload.get("target_readiness", 0)))
            result = self._study_service().update_target_readiness(target)
        except (TypeError, ValueError) as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_focus_item(self) -> None:
        payload = self._read_json()
        item_id = str(payload.get("item_id", "")).strip()
        if not item_id:
            self._send_json({"error": "Missing item_id"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = self._study_service().set_active_item(item_id)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(result)

    def _handle_material_upload(self) -> None:
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
            },
        )
        uploaded = form["file"] if "file" in form else None
        title = form.getfirst("title", "").strip()
        academic_item_id = form.getfirst("academic_item_id", "").strip()
        if uploaded is None or not getattr(uploaded, "file", None):
            self._send_json({"error": "A file upload is required."}, status=HTTPStatus.BAD_REQUEST)
            return

        filename = Path(uploaded.filename or "material")
        suffix = filename.suffix.lower()
        raw_bytes = uploaded.file.read()
        if not raw_bytes:
            self._send_json({"error": "The uploaded file was empty."}, status=HTTPStatus.BAD_REQUEST)
            return

        if suffix == ".pdf":
            text = self._extract_pdf_text(raw_bytes)
            source_note = "Imported from PDF text. Images were not analysed."
        else:
            try:
                text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                self._send_json(
                    {"error": "This file type is not supported yet. Use a text file or a PDF."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            source_note = f"Imported from {filename.suffix or 'text'} file."

        text = text.strip()
        if not text:
            self._send_json(
                {"error": "No readable text was found in that file."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        resolved_title = title or filename.stem
        try:
            result = self._study_service().import_material(resolved_title, text, academic_item_id)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        result["import_note"] = source_note
        self._send_json(result)

    def _extract_pdf_text(self, raw_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(raw_bytes))
        chunks = []
        for page in reader.pages:
            chunks.append(page.extract_text() or "")
        return "\n".join(chunks)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        return safe_json_loads(raw)

    def _auth_token(self) -> str:
        header = self.headers.get("Authorization", "")
        prefix = "Bearer "
        if header.startswith(prefix):
            return header.removeprefix(prefix).strip()
        return ""

    def _base_url(self) -> str:
        host = self.headers.get("Host", "127.0.0.1:8000")
        return f"http://{host}"

    def _is_authenticated(self) -> bool:
        return bool(CONTEXT.auth_service.user_for_token(self._auth_token()))

    def _current_user(self) -> dict:
        return CONTEXT.auth_service.user_for_token(self._auth_token()) or {}

    def _study_service(self) -> StudyStrategyService:
        user_id = str(self._current_user().get("id", ""))
        if not user_id:
            raise ValueError("Authentication required.")
        return CONTEXT.study_service_for_user(user_id)

    @staticmethod
    def _requires_auth(path: str) -> bool:
        return path.startswith("/study/") or path.startswith("/assistant/")

    def _serve_static(self, relative_path: str) -> None:
        file_path = (STATIC_ROOT / relative_path).resolve()
        if not file_path.is_file() or (STATIC_ROOT not in file_path.parents and file_path != STATIC_ROOT / "index.html"):
            self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return
        content_type, _ = mimetypes.guess_type(str(file_path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "text/plain; charset=utf-8")
        self.end_headers()
        try:
            self.wfile.write(file_path.read_bytes())
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    def _redirect(self, location: str) -> None:
        try:
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", location)
            self.end_headers()
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    @staticmethod
    def _url_quote(value: str) -> str:
        from urllib.parse import quote

        return quote(value, safe="")

    def log_message(self, format: str, *args: Tuple[object, ...]) -> None:
        return


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    CONTEXT.study_service_for_user(SEEDED_USER["id"]).get_dashboard()
    server = ThreadingHTTPServer((host, port), StudyStrategyHandler)
    print(f"Study Strategy Service running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()
