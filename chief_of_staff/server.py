from __future__ import annotations

import cgi
import json
import mimetypes
from io import BytesIO
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

from pypdf import PdfReader

from chief_of_staff.services.study_strategy_service import StudyStrategyService
from chief_of_staff.storage import JsonStore
from chief_of_staff.utils import safe_json_loads


ROOT = Path(__file__).resolve().parent.parent
STATIC_ROOT = ROOT / "static"
DATA_ROOT = ROOT / "data"


class AppContext:
    def __init__(self) -> None:
        self.store = JsonStore(DATA_ROOT)
        self.study_service = StudyStrategyService(self.store)


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
        if path == "/study/dashboard":
            self._send_json(CONTEXT.study_service.get_dashboard())
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/assistant/query":
            self._handle_coach_query()
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
        if path == "/study/academic-items":
            self._handle_academic_item()
            return
        if path == "/study/focus":
            self._handle_focus_item()
            return
        if path == "/study/materials/upload":
            self._handle_material_upload()
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def _handle_coach_query(self) -> None:
        payload = self._read_json()
        text = payload.get("text", "").strip()
        if not text:
            self._send_json({"error": "Missing text"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = CONTEXT.study_service.coach_reply(text)
        self._send_json(result)

    def _handle_plan(self) -> None:
        payload = self._read_json()
        minutes = int(payload.get("minutes", 90))
        self._send_json(CONTEXT.study_service.build_plan(minutes))

    def _handle_panic_mode(self) -> None:
        payload = self._read_json()
        horizon = payload.get("horizon", "tonight")
        self._send_json(CONTEXT.study_service.build_panic_mode(horizon))

    def _handle_check_in(self) -> None:
        payload = self._read_json()
        required = ["topic_id", "confidence", "quiz_score", "minutes_studied"]
        missing = [field for field in required if field not in payload]
        if missing:
            self._send_json({"error": f"Missing fields: {', '.join(missing)}"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = CONTEXT.study_service.log_check_in(
            payload["topic_id"],
            int(payload["confidence"]),
            int(payload["quiz_score"]),
            int(payload["minutes_studied"]),
        )
        self._send_json(result)

    def _handle_materials(self) -> None:
        payload = self._read_json()
        title = payload.get("title", "").strip()
        text = payload.get("text", "").strip()
        if not title or not text:
            self._send_json({"error": "Both title and text are required."}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(CONTEXT.study_service.import_material(title, text))

    def _handle_material_delete(self) -> None:
        payload = self._read_json()
        material_id = str(payload.get("material_id", "")).strip()
        if not material_id:
            self._send_json({"error": "Missing material_id"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = CONTEXT.study_service.delete_material(material_id)
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
        result = CONTEXT.study_service.add_academic_item(
            title=str(payload["title"]).strip(),
            subject=str(payload["subject"]).strip(),
            due_date=str(payload["due_date"]).strip(),
            kind=str(payload["kind"]).strip(),
        )
        self._send_json(result)

    def _handle_focus_item(self) -> None:
        payload = self._read_json()
        item_id = str(payload.get("item_id", "")).strip()
        if not item_id:
            self._send_json({"error": "Missing item_id"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            result = CONTEXT.study_service.set_active_item(item_id)
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
        result = CONTEXT.study_service.import_material(resolved_title, text)
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

    def _serve_static(self, relative_path: str) -> None:
        file_path = (STATIC_ROOT / relative_path).resolve()
        if not file_path.is_file() or (STATIC_ROOT not in file_path.parents and file_path != STATIC_ROOT / "index.html"):
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
    CONTEXT.study_service.get_dashboard()
    server = ThreadingHTTPServer((host, port), StudyStrategyHandler)
    print(f"Study Strategy Service running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()
