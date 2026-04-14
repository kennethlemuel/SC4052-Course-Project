from __future__ import annotations

import base64
import hashlib
import os
import secrets
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Dict, Optional

from chief_of_staff.storage import JsonStore


SEEDED_USER = {
    "id": "user-kennethlemuel",
    "username": "kennethlemuel",
    "email": "kennethlemuel05@gmail.com",
    "password_hash": "pbkdf2_sha256$120000$c3R1ZHlidWRkeS1rZW5uZXRobGVtdWVsLXYx$yfqktecMnvaRaKG_AQPozNyrIJSq36xdX4lAtIi1GkA",
}


class AuthService:
    def __init__(self, store: JsonStore) -> None:
        self.store = store
        self._ensure_seed_user()

    def status(self, token: str = "") -> Dict[str, object]:
        user = self.user_for_token(token)
        return {"authenticated": bool(user), "user": self._public_user(user) if user else None}

    def login(self, identifier: str, password: str) -> Dict[str, object]:
        user = self._find_user(identifier)
        if not user or not self._verify_password(password, str(user.get("password_hash", ""))):
            raise ValueError("Username or password is incorrect.")
        token = self._create_session(str(user["id"]))
        return {"session_token": token, "user": self._public_user(user)}

    def register(self, email: str, username: str, password: str, password_confirm: str) -> Dict[str, object]:
        email = email.strip().lower()
        username = username.strip()
        if not email or "@" not in email:
            raise ValueError("Enter a valid email address.")
        if not username:
            raise ValueError("Username is required.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if password != password_confirm:
            raise ValueError("Passwords do not match.")

        state = self._state()
        users = state.setdefault("users", [])
        lowered_username = username.lower()
        for user in users:
            if str(user.get("username", "")).lower() == lowered_username:
                raise ValueError("That username is already registered.")
            if str(user.get("email", "")).lower() == email:
                raise ValueError("That email is already registered.")

        user = {
            "id": f"user-{secrets.token_urlsafe(10)}",
            "username": username,
            "email": email,
            "password_hash": self._hash_password(password),
            "created_at": self._now(),
        }
        users.append(user)
        self._save_state(state)
        token = self._create_session(str(user["id"]))
        return {"session_token": token, "user": self._public_user(user)}

    def logout(self, token: str) -> Dict[str, object]:
        if not token:
            return {"authenticated": False}
        state = self._state()
        sessions = state.setdefault("sessions", {})
        sessions.pop(token, None)
        self._save_state(state)
        return {"authenticated": False}

    def forgot_password(self, email: str, base_url: str = "") -> Dict[str, object]:
        email = email.strip().lower()
        state = self._state()
        reset_requests = state.setdefault("reset_requests", [])
        user = self._find_user(email)
        if user:
            token = secrets.token_urlsafe(24)
            reset_url = f"{base_url.rstrip('/')}/?reset={token}" if base_url else f"?reset={token}"
            email_sent = self._send_reset_email(email, reset_url)
            reset_requests.append(
                {
                    "email": email,
                    "user_id": user.get("id"),
                    "token": token,
                    "created_at": self._now(),
                    "status": "email_sent" if email_sent else "pending_email_configuration",
                }
            )
            self._save_state(state)
            if email_sent:
                return {"message": "A reset link was sent to your email.", "email_sent": True}
            return {
                "message": "Reset link created, but email delivery is not configured yet.",
                "email_sent": False,
                "reset_url": reset_url,
            }
        return {"message": "If that email is registered, a reset link will be sent to it.", "email_sent": False}

    def reset_password(self, token: str, password: str, password_confirm: str) -> Dict[str, object]:
        token = token.strip()
        if not token:
            raise ValueError("Reset token is missing.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if password != password_confirm:
            raise ValueError("Passwords do not match.")

        state = self._state()
        reset_requests = state.setdefault("reset_requests", [])
        request = next(
            (
                item
                for item in reset_requests
                if item.get("token") == token and item.get("status") not in {"used", "expired"}
            ),
            None,
        )
        if not request:
            raise ValueError("That reset link is invalid or already used.")
        user_id = request.get("user_id")
        user = next((item for item in state.get("users", []) if item.get("id") == user_id), None)
        if not user:
            raise ValueError("That reset link no longer matches a user.")
        user["password_hash"] = self._hash_password(password)
        request["status"] = "used"
        request["used_at"] = self._now()
        self._save_state(state)
        token = self._create_session(str(user["id"]))
        return {"session_token": token, "user": self._public_user(user)}

    def user_for_token(self, token: str) -> Optional[Dict[str, object]]:
        if not token:
            return None
        state = self._state()
        session = state.get("sessions", {}).get(token)
        if not session:
            return None
        user_id = session.get("user_id")
        for user in state.get("users", []):
            if user.get("id") == user_id:
                return user
        return None

    def _ensure_seed_user(self) -> None:
        state = self._state()
        users = state.setdefault("users", [])
        if not any(str(user.get("username", "")).lower() == SEEDED_USER["username"] for user in users):
            seeded = dict(SEEDED_USER)
            seeded["created_at"] = self._now()
            users.append(seeded)
            self._save_state(state)

    def _find_user(self, identifier: str) -> Optional[Dict[str, object]]:
        identifier = identifier.strip().lower()
        if not identifier:
            return None
        for user in self._state().get("users", []):
            if str(user.get("username", "")).lower() == identifier or str(user.get("email", "")).lower() == identifier:
                return user
        return None

    def _create_session(self, user_id: str) -> str:
        state = self._state()
        token = secrets.token_urlsafe(32)
        state.setdefault("sessions", {})[token] = {"user_id": user_id, "created_at": self._now()}
        self._save_state(state)
        return token

    def _hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(24)
        iterations = 120000
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return f"pbkdf2_sha256${iterations}${self._b64(salt)}${self._b64(digest)}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            method, iterations, salt, expected = stored_hash.split("$", 3)
            if method != "pbkdf2_sha256":
                return False
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                self._unb64(salt),
                int(iterations),
            )
        except (ValueError, TypeError):
            return False
        return secrets.compare_digest(self._b64(digest), expected)

    def _public_user(self, user: Optional[Dict[str, object]]) -> Optional[Dict[str, object]]:
        if not user:
            return None
        return {"id": user.get("id"), "username": user.get("username"), "email": user.get("email")}

    def _state(self) -> Dict[str, object]:
        state = self.store.load_auth_state()
        state.setdefault("users", [])
        state.setdefault("sessions", {})
        state.setdefault("reset_requests", [])
        return state

    def _save_state(self, state: Dict[str, object]) -> None:
        self.store.save_auth_state(state)

    def _send_reset_email(self, email: str, reset_url: str) -> bool:
        host = os.environ.get("STUDY_BUDDY_SMTP_HOST", "").strip()
        username = os.environ.get("STUDY_BUDDY_SMTP_USER", "").strip()
        password = os.environ.get("STUDY_BUDDY_SMTP_PASSWORD", "").strip()
        sender = os.environ.get("STUDY_BUDDY_SMTP_FROM", username).strip()
        if not host or not username or not password or not sender:
            return False
        try:
            port = int(os.environ.get("STUDY_BUDDY_SMTP_PORT", "587"))
        except ValueError:
            return False
        message = EmailMessage()
        message["Subject"] = "StudyBuddy password reset"
        message["From"] = sender
        message["To"] = email
        message.set_content(
            "Use this link to reset your StudyBuddy password:\n\n"
            f"{reset_url}\n\n"
            "If you did not request this, you can ignore this email."
        )
        try:
            if port == 465:
                with smtplib.SMTP_SSL(host, port, timeout=12) as smtp:
                    smtp.login(username, password)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(host, port, timeout=12) as smtp:
                    smtp.starttls()
                    smtp.login(username, password)
                    smtp.send_message(message)
        except (OSError, smtplib.SMTPException):
            return False
        return True

    @staticmethod
    def _b64(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    @staticmethod
    def _unb64(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
