from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Dict, List

from study_buddy.models import LocalLlmConfig


class MaterialAnalyzer:
    def __init__(self, config: LocalLlmConfig) -> None:
        self.config = config

    def analyze(self, title: str, text: str, academic_item: Dict[str, object]) -> Dict[str, object]:
        if self.config.is_configured() and self.config.provider == "ollama":
            started_at = time.perf_counter()
            print(
                f"[material-analyzer] ollama start model={self.config.model} "
                f"item={academic_item.get('title', 'Academic item')!r} material={title!r}",
                flush=True,
            )
            try:
                topics = self._analyze_with_ollama(title, text, academic_item)
                if topics:
                    elapsed = time.perf_counter() - started_at
                    print(
                        f"[material-analyzer] ollama ok model={self.config.model} "
                        f"topics={len(topics)} elapsed={elapsed:.1f}s",
                        flush=True,
                    )
                    return {"source": f"ollama:{self.config.model}", "topics": topics}
                print("[material-analyzer] ollama returned no topics; falling back to heuristic", flush=True)
            except (OSError, ValueError, urllib.error.URLError, TimeoutError) as exc:
                elapsed = time.perf_counter() - started_at
                print(
                    f"[material-analyzer] ollama failed elapsed={elapsed:.1f}s "
                    f"error={type(exc).__name__}: {exc}",
                    flush=True,
                )
            except Exception as exc:
                elapsed = time.perf_counter() - started_at
                print(
                    f"[material-analyzer] ollama unexpected failure elapsed={elapsed:.1f}s "
                    f"error={type(exc).__name__}: {exc}",
                    flush=True,
                )
        else:
            print("[material-analyzer] ollama not configured; using heuristic", flush=True)
        print(f"[material-analyzer] heuristic start material={title!r}", flush=True)
        return {"source": "heuristic", "topics": self._fallback_topics(title, text)}

    def _analyze_with_ollama(self, title: str, text: str, academic_item: Dict[str, object]) -> List[Dict[str, object]]:
        prompt = self._build_prompt(title, text, academic_item)
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "num_ctx": 8192,
            },
        }
        raw = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.config.base_url.rstrip("/") + "/api/generate",
            data=raw,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))

        content = data.get("response", "")
        parsed = self._parse_json_object(content)
        raw_topics = parsed.get("topics", [])
        if not isinstance(raw_topics, list):
            return []
        return self._normalize_topics(raw_topics)

    @staticmethod
    def _build_prompt(title: str, text: str, academic_item: Dict[str, object]) -> str:
        trimmed_text = text[:24000]
        item_label = (
            f"{academic_item.get('title', 'Academic item')} "
            f"({academic_item.get('kind', 'item')}, {academic_item.get('subject', 'subject')})"
        )
        return f"""
/no_think
You are analyzing study material for a student.

Academic item: {item_label}
Material title: {title}

Task:
Extract the real study topics a student should revise from the material. Ignore course codes, page headers, author names, table-of-contents noise, isolated words, and administrative metadata unless they are actual concepts.

Return JSON only with this schema:
{{
  "topics": [
    {{
      "name": "short concept name",
      "notes": ["2-4 concise study notes grounded in the material"],
      "importance": 1,
      "mastery": 0,
      "confidence": 0
    }}
  ]
}}

Rules:
- Return 3 to 8 topics.
- Names must be meaningful concepts, not fragments.
- Importance is 1-10 based on exam relevance inferred from the material.
- Mastery and confidence must be 0 because uploaded material has not been studied or quizzed yet.
- Use only information grounded in the material.

Material:
{trimmed_text}
""".strip()

    @staticmethod
    def _parse_json_object(content: str) -> Dict[str, object]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise ValueError("LLM response did not contain JSON.")
            parsed = json.loads(match.group(0))
        if not isinstance(parsed, dict):
            raise ValueError("LLM response JSON was not an object.")
        return parsed

    @staticmethod
    def _normalize_topics(raw_topics: List[object]) -> List[Dict[str, object]]:
        topics: List[Dict[str, object]] = []
        seen = set()
        for item in raw_topics:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            if not name or len(name.split()) > 10:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)

            notes = item.get("notes", [])
            if isinstance(notes, str):
                notes = [notes]
            if not isinstance(notes, list):
                notes = []
            normalized_notes = [str(note).strip() for note in notes if str(note).strip()][:4]

            topics.append(
                {
                    "name": name[:90],
                    "notes": normalized_notes,
                    "importance": MaterialAnalyzer._clamp_int(item.get("importance", 7), 1, 10),
                    "mastery": MaterialAnalyzer._clamp_int(item.get("mastery", 0), 0, 100),
                    "confidence": MaterialAnalyzer._clamp_int(item.get("confidence", 0), 0, 100),
                }
            )
            if len(topics) >= 8:
                break
        return topics

    @staticmethod
    def _fallback_topics(title: str, text: str) -> List[Dict[str, object]]:
        lines = [line.strip("-* \t") for line in text.splitlines() if line.strip()]
        extracted = []
        current_title = ""
        current_notes: List[str] = []
        for line in lines:
            clean = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
            if MaterialAnalyzer._looks_like_noise(clean):
                continue
            is_heading = len(clean.split()) <= 8 and not clean.endswith(".")
            if is_heading:
                if current_title:
                    extracted.append((current_title, current_notes[:4]))
                current_title = clean.title()
                current_notes = []
                continue
            if current_title:
                current_notes.append(clean)
        if current_title:
            extracted.append((current_title, current_notes[:4]))

        if not extracted:
            summary_lines = [line for line in lines if len(line.split()) >= 4][:4]
            extracted = [(f"{title} Topic {index + 1}", [line]) for index, line in enumerate(summary_lines)]
        if not extracted:
            extracted = [(title, ["Review imported material and create recall questions from it."])]

        return [
            {"name": name, "notes": notes, "importance": 7, "mastery": 0, "confidence": 0}
            for name, notes in extracted[:5]
        ]

    @staticmethod
    def _looks_like_noise(line: str) -> bool:
        if len(line) <= 2:
            return True
        if re.fullmatch(r"[A-Z]{2}\d{4}.*", line.replace(" ", "")):
            return True
        if re.fullmatch(r"[A-Za-z]{1,3}\s*/\s*[A-Za-z0-9]{1,8}", line):
            return True
        if line.lower() in {"why", "big", "management", "references", "contents"}:
            return True
        return False

    @staticmethod
    def _clamp_int(value: object, minimum: int, maximum: int) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = minimum
        return max(minimum, min(maximum, number))
