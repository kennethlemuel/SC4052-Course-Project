from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urlparse
from typing import Dict, List

from study_buddy.models import LocalLlmConfig


class ResourceSearch:
    EXCLUDED_DOMAINS = (
        "ntu.edu.sg",
        "ntu.edu",
        "coursehero.com",
        "studocu.com",
        "docsity.com",
        "chegg.com",
        "scribd.com",
    )

    def __init__(self, config: LocalLlmConfig) -> None:
        self.api_key = (config.tavily_api_key or os.environ.get("TAVILY_API_KEY", "")).strip()

    def links_for_topics(self, topics: List[str], course_hint: str = "") -> List[Dict[str, str]]:
        links = []
        for topic in topics[:4]:
            links.extend(self.search_topic(topic, course_hint, max_results=2))
            if len(links) >= 5:
                break
        return links[:5]

    def search_topic(self, topic: str, course_hint: str = "", max_results: int = 3) -> List[Dict[str, str]]:
        exclusions = " ".join(f"-site:{domain}" for domain in self.EXCLUDED_DOMAINS)
        query = f"{course_hint} {topic} tutorial explanation {exclusions} -NTU".strip()
        if self.api_key:
            results = self._tavily_search(query, max_results)
            if results:
                return results
        return [self._generated_link(topic, query)]

    @classmethod
    def _is_allowed_url(cls, url: str) -> bool:
        try:
            host = urlparse(url).netloc.lower()
        except ValueError:
            return False
        return bool(host) and not any(host == domain or host.endswith(f".{domain}") for domain in cls.EXCLUDED_DOMAINS)

    def _tavily_search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        payload = {
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
        }
        request = urllib.request.Request(
            "https://api.tavily.com/search",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
            print(f"[resource-search] tavily failed error={type(exc).__name__}: {exc}", flush=True)
            return []

        results = data.get("results", [])
        if not isinstance(results, list):
            return []

        normalized = []
        for item in results:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            url = str(item.get("url", "")).strip()
            snippet = str(item.get("content", "")).strip()
            if not title or not url or not self._is_allowed_url(url):
                continue
            if "ntu" in title.lower() or "ntu" in snippet.lower():
                continue
            normalized.append(
                {
                    "title": title[:120],
                    "url": url,
                    "snippet": snippet[:220],
                    "source": "tavily",
                }
            )
        return normalized

    @staticmethod
    def _generated_link(topic: str, query: str) -> Dict[str, str]:
        encoded = urllib.parse.quote_plus(query)
        return {
            "title": f"Search: {topic}",
            "url": f"https://www.google.com/search?q={encoded}",
            "snippet": "Generated fallback search link. Add a Tavily API key for verified resource results.",
            "source": "generated",
        }
