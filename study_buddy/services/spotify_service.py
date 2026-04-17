from __future__ import annotations

import base64
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict


class SpotifyService:
    DEFAULT_SCOPES = "streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-read-collaborative"

    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root
        self.config_path = data_root / "spotify_config.json"
        self.tokens_path = data_root / "spotify_tokens.json"
        self.http = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def status(self) -> Dict[str, object]:
        config = self._config()
        tokens = self._tokens()
        user = tokens.get("user", {}) if isinstance(tokens.get("user", {}), dict) else {}
        return {
            "configured": bool(config["client_id"] and config["client_secret"] and config["redirect_uri"]),
            "connected": bool(tokens.get("refresh_token")),
            "auth_pending": bool(tokens.get("pending_state") or tokens.get("pending_states")),
            "client_id": config["client_id"] if config["client_id"] else "",
            "display_name": user.get("display_name") or user.get("id") or "",
            "email": user.get("email") or "",
            "scopes": tokens.get("scope") or config["scopes"],
            "premium_required": True,
        }

    def login_url(self) -> str:
        config = self._require_config()
        state = secrets.token_urlsafe(24)
        tokens = self._tokens()
        pending_states = tokens.setdefault("pending_states", [])
        if not isinstance(pending_states, list):
            pending_states = []
        pending_states.append(state)
        tokens["pending_states"] = pending_states[-5:]
        tokens["pending_state"] = state
        self._save_tokens(tokens)
        params = {
            "client_id": config["client_id"],
            "response_type": "code",
            "redirect_uri": config["redirect_uri"],
            "scope": config["scopes"],
            "state": state,
        }
        return f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

    def handle_callback(self, code: str, state: str) -> None:
        tokens = self._tokens()
        expected_state = str(tokens.get("pending_state", ""))
        pending_states = tokens.get("pending_states", [])
        if not isinstance(pending_states, list):
            pending_states = []
        valid_states = [str(item) for item in pending_states]
        if expected_state:
            valid_states.append(expected_state)
        if not state or not any(secrets.compare_digest(state, candidate) for candidate in valid_states):
            raise ValueError("Spotify authorization state did not match. Try connecting again.")

        config = self._require_config()
        try:
            token_payload = self._token_request(
                {
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": config["redirect_uri"],
                },
                config,
            )
            token_payload["expires_at"] = time.time() + int(token_payload.get("expires_in", 3600))
            token_payload["user"] = self._fetch_profile(str(token_payload["access_token"]))
            self._save_tokens(token_payload)
        except ValueError:
            tokens.pop("pending_state", None)
            tokens["pending_states"] = [candidate for candidate in valid_states if candidate != state][-4:]
            self._save_tokens(tokens)
            raise

    def access_token(self) -> Dict[str, object]:
        token = self._valid_access_token()
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": max(0, int(self._tokens().get("expires_at", 0) - time.time())),
        }

    def disconnect(self) -> Dict[str, object]:
        if self.tokens_path.exists():
            self.tokens_path.write_text("{}")
        return self.status()

    def transfer_playback(self, device_id: str, play: bool = False) -> Dict[str, object]:
        if not device_id.strip():
            raise ValueError("Missing Spotify device_id.")
        return self._spotify_api("PUT", "me/player", {"device_ids": [device_id], "play": bool(play)})

    def library(self) -> Dict[str, object]:
        playlists = self._spotify_api("GET", "me/playlists", params={"limit": "12"})
        return {
            "playlists": [self._format_playlist(item) for item in playlists.get("items", []) if isinstance(item, dict)],
            "tracks": [],
        }

    def search(self, query: str) -> Dict[str, object]:
        cleaned_query = query.strip()
        if not cleaned_query:
            return self.library()
        result = self._spotify_api(
            "GET",
            "search",
            params={"q": cleaned_query, "type": "track,playlist", "limit": "8", "market": "from_token"},
        )
        tracks = result.get("tracks", {})
        playlists = result.get("playlists", {})
        return {
            "tracks": [
                self._format_track(item)
                for item in tracks.get("items", [])
                if isinstance(item, dict)
            ],
            "playlists": [
                self._format_playlist(item)
                for item in playlists.get("items", [])
                if isinstance(item, dict)
            ],
        }

    def play(self, device_id: str, uri: str = "", context_uri: str = "") -> Dict[str, object]:
        cleaned_device_id = device_id.strip()
        cleaned_uri = uri.strip()
        cleaned_context_uri = context_uri.strip()
        if not cleaned_device_id:
            raise ValueError("Missing Spotify device_id.")
        if not cleaned_uri and not cleaned_context_uri:
            raise ValueError("Choose a Spotify track or playlist first.")

        payload: Dict[str, object]
        if cleaned_context_uri:
            payload = {"context_uri": cleaned_context_uri}
        else:
            payload = {"uris": [cleaned_uri]}
        return self._spotify_api(
            "PUT",
            "me/player/play",
            payload,
            params={"device_id": cleaned_device_id},
        )

    def pause(self, device_id: str) -> Dict[str, object]:
        cleaned_device_id = device_id.strip()
        if not cleaned_device_id:
            raise ValueError("Missing Spotify device_id.")
        return self._spotify_api("PUT", "me/player/pause", params={"device_id": cleaned_device_id})

    def shuffle(self, device_id: str, state: bool) -> Dict[str, object]:
        cleaned_device_id = device_id.strip()
        if not cleaned_device_id:
            raise ValueError("Missing Spotify device_id.")
        return self._spotify_api(
            "PUT",
            "me/player/shuffle",
            params={"device_id": cleaned_device_id, "state": "true" if state else "false"},
        )

    def _spotify_api(
        self,
        method: str,
        endpoint: str,
        payload: Dict[str, object] | None = None,
        params: Dict[str, str] | None = None,
    ) -> Dict[str, object]:
        token = self._valid_access_token()
        query = f"?{urllib.parse.urlencode(params)}" if params else ""
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"https://api.spotify.com/v1/{endpoint.lstrip('/')}{query}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with self.http.open(request, timeout=20) as response:
                raw = response.read().decode("utf-8")
                body = json.loads(raw) if raw.strip() else {}
                body["ok"] = response.status in {200, 202, 204}
                body["status"] = response.status
                return body
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"Spotify request failed with {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise ValueError(f"Spotify request failed: {exc.reason}") from exc

    def _format_playlist(self, item: Dict[str, object]) -> Dict[str, object]:
        owner = item.get("owner", {}) if isinstance(item.get("owner"), dict) else {}
        tracks = item.get("tracks", {}) if isinstance(item.get("tracks"), dict) else {}
        return {
            "type": "playlist",
            "name": item.get("name") or "Untitled playlist",
            "uri": item.get("uri") or "",
            "owner": owner.get("display_name") or owner.get("id") or "",
            "tracks_total": tracks.get("total") or 0,
            "image_url": self._first_image_url(item.get("images")),
        }

    def _format_track(self, item: Dict[str, object]) -> Dict[str, object]:
        album = item.get("album", {}) if isinstance(item.get("album"), dict) else {}
        artists = item.get("artists", []) if isinstance(item.get("artists"), list) else []
        artist_names = [str(artist.get("name", "")) for artist in artists if isinstance(artist, dict) and artist.get("name")]
        return {
            "type": "track",
            "name": item.get("name") or "Untitled track",
            "uri": item.get("uri") or "",
            "artists": ", ".join(artist_names),
            "album": album.get("name") or "",
            "image_url": self._first_image_url(album.get("images")),
        }

    @staticmethod
    def _first_image_url(images: object) -> str:
        if not isinstance(images, list):
            return ""
        for image in images:
            if isinstance(image, dict) and image.get("url"):
                return str(image["url"])
        return ""

    def _valid_access_token(self) -> str:
        tokens = self._tokens()
        access_token = str(tokens.get("access_token", ""))
        expires_at = float(tokens.get("expires_at", 0) or 0)
        if access_token and expires_at - 60 > time.time():
            return access_token
        refresh_token = str(tokens.get("refresh_token", ""))
        if not refresh_token:
            raise ValueError("Spotify is not connected yet.")

        config = self._require_config()
        refreshed = self._token_request({"grant_type": "refresh_token", "refresh_token": refresh_token}, config)
        tokens["access_token"] = refreshed["access_token"]
        tokens["expires_at"] = time.time() + int(refreshed.get("expires_in", 3600))
        tokens["token_type"] = refreshed.get("token_type", tokens.get("token_type", "Bearer"))
        tokens["scope"] = refreshed.get("scope", tokens.get("scope", config["scopes"]))
        if refreshed.get("refresh_token"):
            tokens["refresh_token"] = refreshed["refresh_token"]
        self._save_tokens(tokens)
        return str(tokens["access_token"])

    def _fetch_profile(self, access_token: str) -> Dict[str, object]:
        request = urllib.request.Request(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        try:
            with self.http.open(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError):
            return {}

    def _token_request(self, payload: Dict[str, str], config: Dict[str, str]) -> Dict[str, object]:
        encoded_credentials = base64.b64encode(f"{config['client_id']}:{config['client_secret']}".encode("utf-8")).decode("ascii")
        request = urllib.request.Request(
            "https://accounts.spotify.com/api/token",
            data=urllib.parse.urlencode(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        try:
            with self.http.open(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"Spotify token request failed with {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise ValueError(f"Spotify token request failed: {exc.reason}") from exc

    def _require_config(self) -> Dict[str, str]:
        config = self._config()
        if not config["client_id"] or not config["client_secret"] or not config["redirect_uri"]:
            raise ValueError("Spotify is not configured yet.")
        return config

    def _config(self) -> Dict[str, str]:
        file_config: Dict[str, str] = {}
        if self.config_path.exists():
            try:
                file_config = json.loads(self.config_path.read_text())
            except json.JSONDecodeError:
                file_config = {}
        return {
            "client_id": os.getenv("SPOTIFY_CLIENT_ID") or str(file_config.get("client_id", "")),
            "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET") or str(file_config.get("client_secret", "")),
            "redirect_uri": os.getenv("SPOTIFY_REDIRECT_URI") or str(file_config.get("redirect_uri", "http://127.0.0.1:8000/spotify/callback")),
            "scopes": os.getenv("SPOTIFY_SCOPES") or str(file_config.get("scopes", self.DEFAULT_SCOPES)),
        }

    def _tokens(self) -> Dict[str, object]:
        if not self.tokens_path.exists():
            return {}
        try:
            return json.loads(self.tokens_path.read_text())
        except json.JSONDecodeError:
            return {}

    def _save_tokens(self, tokens: Dict[str, object]) -> None:
        self.tokens_path.write_text(json.dumps(tokens, indent=2))
