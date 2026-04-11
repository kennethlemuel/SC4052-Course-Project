# Revision Control

Revision Control is a local study-strategy web app. It helps a student identify weak topics, generate adaptive revision sprints, run panic-mode triage, track confidence vs actual performance, and turn pasted materials into study targets.

## Project layout

- `app.py`
  Starts the local server.
- `chief_of_staff/`
  Backend code for the study engine, storage, and HTTP server.
- `static/`
  Frontend UI, styles, and browser-side interactions.
- `tests/`
  Unit tests for the study strategy service.
- `data/`
  Local runtime data and local-only config files. This folder is gitignored except for `.gitkeep`.

## Local setup

1. Clone the repository.
2. Go into the project folder.
3. Start the app:

```bash
python3 app.py
```

4. Open:

```text
http://127.0.0.1:8000
```

The app starts with seeded demo study data and writes local state to `data/study_state.json`.

## Optional local LLM setup

The current app works without an LLM. If you later want to connect a local model, keep that configuration in a local file such as:

`data/local_llm_config.json`

This file is gitignored and stays on your machine.

## Useful commands

Run tests:

```bash
python3 -m unittest discover -s tests
```
