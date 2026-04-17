# Study Buddy

Study Buddy is a local study-planning web app for managing exam, quiz, and assignment revision. It lets students upload lecture materials, extract study topics, track topic readiness, ask a study coach what to focus on, build quick plans, run cram-mode sessions, and use focus audio while studying.

The app is local-first. User data, uploaded material summaries, auth state, Spotify tokens, and local configuration are stored under `data/` and are ignored by Git.

## API And Service Disclaimer

The core app can run locally without external APIs, but some features need extra services:

- **Spotify Web API and Web Playback SDK**
  Required only for the Spotify tab in Cram Mode. You need a Spotify Developer app with a client ID, client secret, and redirect URI. Spotify browser playback normally requires a Spotify Premium account.

- **SMTP email account**
  Required only if password reset links should actually be sent by email. Without SMTP settings, the app can still generate a local reset link, but it will not deliver email.

- **Ollama local LLM API**
  Optional. If configured, uploaded materials and coach replies can use a local model. Without it, the app falls back to heuristic topic extraction and local rules.

- **Tavily Search API**
  Optional. Used to fetch external non-NTU learning resources. Without it, the app generates Google search fallback links instead of verified search results.

Do not commit real API keys, client secrets, reset tokens, Spotify tokens, or user data. The repository `.gitignore` is set up to ignore local JSON files under `data/`.

## Features

- Login, registration, logout, and password reset flow.
- Per-user study state, so different accounts do not share materials or plans.
- Materials page for uploading pasted notes, text files, or PDFs.
- Grouped material library by exam, assignment, or quiz focus.
- Topic extraction from uploaded lecture material.
- Readiness and topic confidence tracking.
- Study Room coach with persistent chat tabs and shared question memory.
- Coach quiz flow with MCQ and short-answer questions.
- Quiz answers update topic mastery and confidence.
- Quick Plan builder for the current focus.
- Overview page showing the current focus, plan, topics, and upcoming academic items.
- Cram Mode with timer, rescue plan, website focus sounds, and optional Spotify playback.

## Project Structure

```text
SC4052-Course-Project/
|-- app.py
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- chief_of_staff/
|   |-- __init__.py
|   |-- models.py
|   |-- server.py
|   |-- storage.py
|   |-- utils.py
|   `-- services/
|       |-- __init__.py
|       |-- auth_service.py
|       |-- material_analyzer.py
|       |-- resource_search.py
|       |-- spotify_service.py
|       `-- study_strategy_service.py
|-- static/
|   |-- index.html
|   |-- app.js
|   |-- styles.css
|   |-- study-buddy-icon.svg
|   `-- fonts/
|       `-- CabinetGrotesk-Variable.ttf
|-- tests/
|   `-- test_study_strategy.py
`-- data/
    `-- .gitkeep
```

Some older backend modules for calendar/planner experiments may still exist under `chief_of_staff/services/`, but the current Study Buddy app is centered on materials, study planning, coach chat, readiness tracking, authentication, and Spotify/focus audio.

## Requirements

- Python 3.10 or newer.
- A modern browser.
- Python package dependencies from `requirements.txt`.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Local Setup

1. Clone the repository.

```bash
git clone https://github.com/kennethlemuel/SC4052-Course-Project.git
cd SC4052-Course-Project
```

2. Install Python dependencies.

```bash
python -m pip install -r requirements.txt
```

3. Start the local server.

```bash
python app.py
```

4. Open the app.

```text
http://127.0.0.1:8000
```

If you configured your hosts file for the friendly local domain, you can also use:

```text
http://studybuddy.localhost:8000
```

5. Register a user account from the login screen.

There is no required seeded demo account. Each registered user gets separate study data under `data/users/<user-id>/study_state.json`.

## Optional Spotify Setup

Cram Mode can connect to Spotify so students can browse playlists/tracks and play audio from the web app.

Create `data/spotify_config.json`:

```json
{
  "client_id": "your-spotify-client-id",
  "client_secret": "your-spotify-client-secret",
  "redirect_uri": "http://127.0.0.1:8000/spotify/callback",
  "scopes": "streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-read-collaborative"
}
```

You can also use environment variables instead:

```powershell
$env:SPOTIFY_CLIENT_ID="your-spotify-client-id"
$env:SPOTIFY_CLIENT_SECRET="your-spotify-client-secret"
$env:SPOTIFY_REDIRECT_URI="http://127.0.0.1:8000/spotify/callback"
python app.py
```

Spotify Developer Dashboard requirements:

- Add the same redirect URI to your Spotify app settings.
- Add test users if the Spotify app is in development mode.
- Use the account that is allowed in the Spotify Developer Dashboard.

After connection, Spotify tokens are stored locally in `data/spotify_tokens.json`, which is ignored by Git.

## Optional Email Reset Setup

Password reset links can be emailed if SMTP is configured.

PowerShell example:

```powershell
$env:STUDY_BUDDY_SMTP_HOST="smtp.gmail.com"
$env:STUDY_BUDDY_SMTP_PORT="587"
$env:STUDY_BUDDY_SMTP_USER="your-email@gmail.com"
$env:STUDY_BUDDY_SMTP_PASSWORD="your-app-password"
$env:STUDY_BUDDY_SMTP_FROM="your-email@gmail.com"
python app.py
```

For Gmail, use a Google app password, not your normal account password.

If SMTP is not configured, the reset flow still creates a reset token locally, but the app cannot send it through email.

## Optional Local LLM Setup

The app works without an LLM. To use Ollama, create `data/local_llm_config.json`:

```json
{
  "provider": "ollama",
  "base_url": "http://127.0.0.1:11434",
  "model": "gemma3:4b",
  "tavily_api_key": ""
}
```

Then make sure Ollama is running and the model is available:

```bash
ollama pull gemma3:4b
ollama serve
```

If Ollama is missing or unavailable, Study Buddy falls back to local heuristic behavior.

## Optional Tavily Setup

Tavily is used only for external learning resource search. You can configure it in either place:

```powershell
$env:TAVILY_API_KEY="your-tavily-api-key"
python app.py
```

or inside `data/local_llm_config.json`:

```json
{
  "provider": "ollama",
  "base_url": "http://127.0.0.1:11434",
  "model": "gemma3:4b",
  "tavily_api_key": "your-tavily-api-key"
}
```

Without Tavily, the Coach returns generated Google search links for outside resources.

## Runtime Data

Local runtime files are stored in `data/`.

Common files:

```text
data/
|-- auth_state.json
|-- local_llm_config.json
|-- spotify_config.json
|-- spotify_tokens.json
`-- users/
    `-- <user-id>/
        `-- study_state.json
```

These files are ignored by Git because they can contain private user data, credentials, or tokens.

## Running Tests

```bash
python -m unittest discover -s tests
```

## Notes For Development

- The backend uses Python's built-in `ThreadingHTTPServer`; it is not a Flask or Django app.
- The frontend is plain HTML, CSS, and JavaScript under `static/`.
- PDF upload text extraction uses `pypdf`.
- The app is designed for local coursework/demo use, not production deployment.
- Keep secrets in environment variables or ignored `data/*.json` files.
