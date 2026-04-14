from __future__ import annotations

import json
import random
import re
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from chief_of_staff.models import AcademicItem, StudyProfile, StudyTopic
from chief_of_staff.services.material_analyzer import MaterialAnalyzer
from chief_of_staff.services.resource_search import ResourceSearch
from chief_of_staff.storage import JsonStore


class StudyStrategyService:
    _ANSWER_STOPWORDS = {
        "about",
        "after",
        "against",
        "also",
        "answer",
        "because",
        "before",
        "being",
        "could",
        "detail",
        "does",
        "each",
        "exam",
        "explain",
        "from",
        "have",
        "into",
        "material",
        "only",
        "rather",
        "refers",
        "should",
        "such",
        "than",
        "that",
        "their",
        "then",
        "there",
        "these",
        "this",
        "through",
        "using",
        "which",
        "while",
        "with",
        "your",
    }
    _ANSWER_ALIASES = {
        "arrivals": "arrive",
        "arriving": "arrive",
        "collecting": "collect",
        "collected": "collect",
        "creates": "create",
        "created": "create",
        "creating": "create",
        "generated": "create",
        "generates": "create",
        "generating": "create",
        "handled": "process",
        "handling": "process",
        "processing": "process",
        "processed": "process",
        "quick": "speed",
        "quickly": "speed",
        "rapid": "speed",
        "rapidly": "speed",
        "real-time": "realtime",
        "realtime": "realtime",
        "timely": "speed",
        "updates": "update",
        "updating": "update",
    }

    def __init__(self, store: JsonStore, seed_demo: bool = True) -> None:
        self.store = store
        self.seed_demo = seed_demo
        self.llm_config = store.load_local_llm_config()
        self.material_analyzer = MaterialAnalyzer(self.llm_config)
        self.resource_search = ResourceSearch(self.llm_config)

    def get_dashboard(self) -> Dict[str, object]:
        state = self._ensure_state()
        focus_item = self._active_item(state)
        topics = self._topics_for_focus(state, focus_item)
        topics_by_risk = sorted(topics, key=self._risk_score, reverse=True)
        profile = StudyProfile(**state["profile"])
        metrics = self._build_metrics(profile, focus_item, topics_by_risk)
        readiness_cards = self._build_readiness_cards(topics_by_risk)
        last_plan_request = state.get("last_plan_request", {}) if isinstance(state.get("last_plan_request", {}), dict) else {}
        has_saved_plan = last_plan_request.get("focus_item_id") == state.get("active_item_id")
        try:
            plan_minutes = (
                int(float(last_plan_request.get("minutes", profile.default_study_minutes) or profile.default_study_minutes))
                if has_saved_plan
                else profile.default_study_minutes
            )
        except (TypeError, ValueError):
            plan_minutes = profile.default_study_minutes
        plan_material_ids = last_plan_request.get("material_ids", []) if has_saved_plan else []
        if not isinstance(plan_material_ids, list):
            plan_material_ids = []
        if has_saved_plan:
            plan_payload = self.build_plan(
                plan_minutes,
                [str(item) for item in plan_material_ids],
            )
        else:
            plan_payload = self.build_plan(plan_minutes)
        panic = self.build_panic_mode("tonight")
        recall = self._build_recall_deck(topics_by_risk[:4])
        academic_items = self._sorted_items(state["academic_items"])
        return {
            "profile": profile.to_dict(),
            "focus_item": focus_item,
            "academic_items": academic_items,
            "upcoming_items": [item for item in academic_items if item["id"] != state["active_item_id"]][:4],
            "metrics": metrics,
            "weakness_map": readiness_cards,
            "plan": plan_payload["plan"],
            "plan_meta": {
                "pace": plan_payload["pace"],
                "minutes": plan_minutes,
                "selected_material_ids": plan_payload["selected_material_ids"],
            },
            "panic_mode": panic,
            "recall_deck": recall,
            "topics": readiness_cards,
            "materials": state["materials"][::-1],
            "coach": self._coach_public_state(state),
        }

    def add_academic_item(self, title: str, subject: str, due_date: str, kind: str) -> Dict[str, object]:
        state = self._ensure_state()
        item = AcademicItem(
            id=f"item-{uuid.uuid4().hex[:8]}",
            kind=kind,
            title=title,
            subject=subject,
            due_date=due_date,
            target_readiness=0,
        )
        state["academic_items"].append(item.to_dict())
        if not state.get("active_item_id"):
            state["active_item_id"] = item.id
        self.store.save_study_state(state)
        return {
            "item": item.to_dict(),
            "dashboard": self.get_dashboard(),
        }

    def set_active_item(self, item_id: str) -> Dict[str, object]:
        state = self._ensure_state()
        for item in state["academic_items"]:
            if item["id"] == item_id:
                state["active_item_id"] = item_id
                self.store.save_study_state(state)
                return {"dashboard": self.get_dashboard()}
        raise ValueError("Academic item was not found.")

    def update_academic_item(
        self,
        item_id: str,
        title: str,
        subject: str,
        due_date: str,
        kind: str,
    ) -> Dict[str, object]:
        title = title.strip()
        subject = subject.strip()
        due_date = due_date.strip()
        kind = kind.strip().lower()
        if not title or not subject or not due_date:
            raise ValueError("Title, subject, and due date are required.")
        if kind not in {"exam", "assignment", "quiz"}:
            raise ValueError("Type must be exam, assignment, or quiz.")
        try:
            datetime.fromisoformat(due_date).date()
        except ValueError as exc:
            raise ValueError("Due date must use YYYY-MM-DD format.") from exc

        state = self._ensure_state()
        for item in state["academic_items"]:
            if item["id"] != item_id:
                continue
            item["title"] = title
            item["subject"] = subject
            item["due_date"] = due_date
            item["kind"] = kind
            self.store.save_study_state(state)
            return {
                "item": item,
                "dashboard": self.get_dashboard(),
            }
        raise ValueError("Academic item was not found.")

    def delete_academic_item(self, item_id: str) -> Dict[str, object]:
        state = self._ensure_state()
        deleted_item = next((item for item in state["academic_items"] if item["id"] == item_id), None)
        if deleted_item is None:
            raise ValueError("Academic item was not found.")

        state["academic_items"] = [item for item in state["academic_items"] if item["id"] != item_id]
        removed_topic_ids = {topic["id"] for topic in state["topics"] if topic.get("academic_item_id") == item_id}
        state["topics"] = [topic for topic in state["topics"] if topic["id"] not in removed_topic_ids]
        state["check_ins"] = [check_in for check_in in state["check_ins"] if check_in.get("topic_id") not in removed_topic_ids]
        if state.get("active_item_id") == item_id:
            remaining_items = self._sorted_items(state["academic_items"])
            state["active_item_id"] = remaining_items[0]["id"] if remaining_items else ""

        self.store.save_study_state(state)
        return {
            "deleted_item_title": deleted_item.get("title", "Academic item"),
            "dashboard": self.get_dashboard(),
        }

    def update_target_readiness(self, target_readiness: int) -> Dict[str, object]:
        state = self._ensure_state()
        focus_item = self._active_item(state)
        if not focus_item:
            raise ValueError("No current focus is selected.")
        target = self._clamp_int(target_readiness, 0, 100)
        for item in state["academic_items"]:
            if item["id"] == focus_item["id"]:
                item["target_readiness"] = target
                self.store.save_study_state(state)
                return {"dashboard": self.get_dashboard()}
        raise ValueError("Current focus was not found.")

    def build_plan(self, minutes: int, material_ids: List[str] | None = None, save_request: bool = False) -> Dict[str, object]:
        state = self._ensure_state()
        focus_item = self._active_item(state)
        focus_material_ids = {material.get("id", "") for material in self._materials_for_focus(state, focus_item)}
        selected_material_ids = {
            str(material_id).strip()
            for material_id in (material_ids or [])
            if str(material_id).strip() in focus_material_ids
        }
        topics = self._topics_for_focus(state, focus_item)
        if selected_material_ids:
            topics = [
                topic
                for topic in topics
                if topic.source_material_id in selected_material_ids
            ]
        topics = sorted(topics, key=lambda topic: (topic.confidence, topic.mastery, -topic.importance, topic.name.lower()))
        try:
            safe_minutes = max(15, int(float(minutes)))
        except (TypeError, ValueError):
            safe_minutes = 90
        remaining = safe_minutes
        plan = []
        cycle = [
            "Active recall sprint",
            "Closed-book concept summary",
            "Worked example repair",
            "Confidence calibration quiz",
        ]
        max_blocks = max(1, min(8, (remaining + 29) // 30))
        index = 0
        for topic in topics:
            if remaining <= 0 or len(plan) >= max_blocks:
                break
            block = min(45 if topic.importance >= 8 else 35, remaining)
            plan.append(
                {
                    "title": topic.name,
                    "module": topic.module,
                    "minutes": block,
                    "mode": cycle[index % len(cycle)],
                    "reason": self._focus_reason(topic),
                }
            )
            remaining -= block
            index += 1
        item_label = focus_item["title"] if focus_item else "your current focus"
        if save_request:
            state["last_plan_request"] = {
                "focus_item_id": focus_item.get("id", "") if focus_item else "",
                "minutes": safe_minutes,
                "material_ids": sorted(selected_material_ids),
            }
            self.store.save_study_state(state)
        return {
            "headline": f"{safe_minutes}-minute plan for {item_label}",
            "plan": plan,
            "pace": self._plan_pace(safe_minutes),
            "selected_material_ids": sorted(selected_material_ids),
        }

    def build_panic_mode(self, horizon: str) -> Dict[str, object]:
        state = self._ensure_state()
        focus_item = self._active_item(state)
        topics = sorted(self._topics_for_focus(state, focus_item), key=self._panic_score, reverse=True)
        minutes = {"three_hours": 180, "tonight": 240, "weekend": 480}.get(horizon, 240)
        must_cover = []
        remaining = minutes
        for topic in topics[:5]:
            block = 60 if topic.importance >= 8 else 40
            if remaining < 30:
                break
            block = min(block, remaining)
            must_cover.append(
                {
                    "title": topic.name,
                    "minutes": block,
                    "order": len(must_cover) + 1,
                    "reason": self._panic_reason(topic),
                }
            )
            remaining -= block
        skip = [topic.name for topic in topics[-2:]]
        item_label = focus_item["title"] if focus_item else "your current focus"
        return {
            "headline": f"{self._panic_headline(horizon)} for {item_label}",
            "must_cover": must_cover,
            "skip": skip,
            "triage_note": "Protect high-yield topics first. Skip polishing strong topics until weak, high-importance material is stabilized.",
        }

    def log_check_in(self, topic_id: str, confidence: int, quiz_score: int, minutes_studied: int) -> Dict[str, object]:
        state = self._ensure_state()
        timestamp = datetime.now().isoformat()
        updated_topic = None
        for topic in state["topics"]:
            if topic["id"] != topic_id:
                continue
            topic["confidence"] = round((topic["confidence"] * 0.55) + (confidence * 0.45))
            topic["quiz_average"] = round((topic["quiz_average"] * 0.4) + (quiz_score * 0.6)) if topic["quiz_average"] else quiz_score
            topic["mastery"] = round((topic["mastery"] * 0.55) + (quiz_score * 0.45))
            topic["last_reviewed"] = timestamp
            updated_topic = topic
            break
        if updated_topic is None:
            raise ValueError("Topic was not found.")
        state["check_ins"].append(
            {
                "topic_id": topic_id,
                "confidence": confidence,
                "quiz_score": quiz_score,
                "minutes_studied": minutes_studied,
                "recorded_at": timestamp,
            }
        )
        self.store.save_study_state(state)
        mastery_gap = max(0, updated_topic["confidence"] - updated_topic["mastery"])
        return {
            "topic": updated_topic,
            "insight": (
                f"Confidence gap is {mastery_gap} points. Re-test this topic tomorrow."
                if mastery_gap >= 15
                else "Confidence and performance are reasonably aligned."
            ),
            "dashboard": self.get_dashboard(),
        }

    def import_material(self, title: str, text: str, academic_item_id: str = "") -> Dict[str, object]:
        state = self._ensure_state()
        material_id = f"material-{uuid.uuid4().hex[:8]}"
        academic_item = self._academic_item_by_id(state, academic_item_id) if academic_item_id else self._active_item(state)
        if not academic_item:
            raise ValueError("Academic item was not found.")
        analysis = self.material_analyzer.analyze(title, text, academic_item)
        extracted_topics = analysis["topics"]
        created = []
        created_ids = []
        for topic_payload in extracted_topics:
            topic = StudyTopic(
                id=f"topic-{uuid.uuid4().hex[:8]}",
                name=topic_payload["name"],
                module=title,
                mastery=topic_payload["mastery"],
                confidence=topic_payload["confidence"],
                importance=topic_payload["importance"],
                last_reviewed="Not reviewed yet",
                notes=topic_payload["notes"][:5],
                quiz_average=0,
                source_material_id=material_id,
                academic_item_id=academic_item.get("id", ""),
            )
            state["topics"].append(topic.to_dict())
            created.append(topic.name)
            created_ids.append(topic.id)
        state["materials"].append(
            {
                "id": material_id,
                "title": title,
                "created_at": datetime.now().isoformat(),
                "topics": created,
                "topic_ids": created_ids,
                "academic_item_id": academic_item.get("id", ""),
                "analysis_source": analysis["source"],
                "text_excerpt": text[:12000],
            }
        )
        self.store.save_study_state(state)
        return {
            "created_topics": created,
            "analysis_source": analysis["source"],
            "dashboard": self.get_dashboard(),
        }

    def delete_material(self, material_id: str) -> Dict[str, object]:
        state = self._ensure_state()
        materials = state["materials"]
        material = next((item for item in materials if item.get("id") == material_id), None)
        if material is None:
            raise ValueError("Material was not found.")

        topic_ids = set(material.get("topic_ids", []))
        removed_topic_ids = {
            topic["id"]
            for topic in state["topics"]
            if topic.get("source_material_id") == material_id or topic["id"] in topic_ids
        }
        if not removed_topic_ids:
            topic_names = set(material.get("topics", []))
            title = str(material.get("title", "")).strip()
            removed_topic_ids = {
                topic["id"]
                for topic in state["topics"]
                if topic.get("module") == title and topic.get("name") in topic_names
            }

        state["materials"] = [item for item in materials if item.get("id") != material_id]
        state["topics"] = [topic for topic in state["topics"] if topic["id"] not in removed_topic_ids]
        state["check_ins"] = [check_in for check_in in state["check_ins"] if check_in.get("topic_id") not in removed_topic_ids]
        self.store.save_study_state(state)
        return {
            "deleted_material_title": material.get("title", "Material"),
            "removed_topics": len(removed_topic_ids),
            "dashboard": self.get_dashboard(),
        }

    def rename_material(self, material_id: str, title: str) -> Dict[str, object]:
        new_title = title.strip()
        if not new_title:
            raise ValueError("Material title is required.")

        state = self._ensure_state()
        materials = state["materials"]
        material = next((item for item in materials if item.get("id") == material_id), None)
        if material is None:
            raise ValueError("Material was not found.")

        old_title = str(material.get("title", "")).strip()
        material["title"] = new_title
        topic_ids = set(material.get("topic_ids", []))
        topic_names = set(material.get("topics", []))
        for topic in state["topics"]:
            belongs_to_material = (
                topic.get("source_material_id") == material_id
                or topic.get("id") in topic_ids
                or (topic.get("module") == old_title and topic.get("name") in topic_names)
            )
            if belongs_to_material:
                topic["module"] = new_title

        self.store.save_study_state(state)
        return {
            "material": material,
            "old_title": old_title,
            "dashboard": self.get_dashboard(),
        }

    def _legacy_coach_reply(self, text: str) -> Dict[str, object]:
        lowered = text.lower()
        dashboard = self.get_dashboard()
        topics = dashboard["topics"]
        focus_item = dashboard["focus_item"]
        focus_label = focus_item["title"] if focus_item else "your current focus"
        if "what can you do" in lowered or "help" in lowered:
            reply = (
                "I can show your weak topics, build a study plan, make a cram plan, "
                "track readiness, and turn your notes into study targets."
            )
        elif "panic" in lowered or "exam tomorrow" in lowered or "cram" in lowered:
            panic = self.build_panic_mode("tonight")
            reply = self._format_panic_reply(panic)
            return {"reply": reply, "panic_mode": panic}
        elif "weak" in lowered or "struggle" in lowered or "behind" in lowered:
            weakest = topics[:3]
            reply = "Current weak topics:\n" + "\n".join(
                f"• {topic['name']} ({topic['status_label']}): {topic['reason']}" for topic in weakest
            )
        elif "tonight" in lowered or "study next" in lowered or "what should i study" in lowered:
            minutes = self._extract_minutes(lowered)
            plan = self.build_plan(minutes)
            reply = self._format_plan_reply(plan)
            return {"reply": reply, "plan": plan}
        elif "confidence" in lowered or "overconfident" in lowered or "ready" in lowered:
            reply = (
                f"You are {dashboard['metrics']['readiness_score']}/100 ready for {focus_label}. "
                f"Your confidence gap is {dashboard['metrics']['confidence_gap']} points."
            )
        else:
            reply = (
                f"Your current focus is {focus_label}. "
                f"Best next move: {dashboard['metrics']['next_focus']}. "
                "Ask me for a study plan, cram plan, or weak topics."
            )
        return {"reply": reply}

    def coach_reply(self, text: str, tab_id: str = "") -> Dict[str, object]:
        state = self._ensure_state()
        lowered = text.lower().strip()
        tab = self._coach_tab(state, tab_id or str(state.get("active_coach_tab_id", "")), create=True)
        session = tab.setdefault("session", {})
        state["active_coach_tab_id"] = tab["id"]
        self._append_coach_message(tab, "user", text)

        if self._is_quiz_end(lowered):
            session.clear()
            result = {
                "reply": "Quiz ended. I updated the readiness view with the answers you completed.",
                "dashboard": self.get_dashboard(),
            }
            return self._finish_coach_reply(state, tab, result)

        if session.get("mode") == "quiz":
            if self._is_another_question(lowered):
                preferred_type = self._requested_question_type(lowered)
                if preferred_type:
                    session["preferred_question_type"] = preferred_type
                return self._finish_coach_reply(state, tab, self._coach_next_question(state, session))
            if session.get("current_question"):
                return self._finish_coach_reply(state, tab, self._coach_grade_answer(state, session, text))

        if self._wants_quiz(lowered):
            quiz_scope = self._resolve_quiz_scope(state, text, session)
            if quiz_scope["topic_ids"]:
                session["mode"] = "quiz"
                session["quiz_scope"] = quiz_scope
                session["topic_id"] = quiz_scope["topic_ids"][0]
                session.setdefault("asked_questions", [])
                preferred_type = self._requested_question_type(lowered)
                if preferred_type:
                    session["preferred_question_type"] = preferred_type
                session.pop("current_question", None)
                return self._finish_coach_reply(state, tab, self._coach_next_question(state, session))
            if quiz_scope.get("message"):
                return self._finish_coach_reply(state, tab, {"reply": str(quiz_scope["message"])})

        if "panic" in lowered or "exam tomorrow" in lowered or "cram" in lowered:
            panic = self.build_panic_mode("tonight")
            reply = self._format_panic_reply(panic)
            return self._finish_coach_reply(state, tab, {"reply": reply, "panic_mode": panic})

        if self._wants_lecture_overview(lowered):
            return self._finish_coach_reply(state, tab, self._coach_lecture_overview(state, text))

        if (
            "tonight" in lowered
            or "study next" in lowered
            or "what should i study" in lowered
            or "study" in lowered
            or "which lecture" in lowered
            or "most focus" in lowered
            or "most focusing" in lowered
        ):
            return self._finish_coach_reply(state, tab, self._coach_material_study_reply(state, text, session))

        if "weak" in lowered or "struggle" in lowered or "behind" in lowered:
            return self._finish_coach_reply(state, tab, self._coach_material_study_reply(state, text, session))

        if "confidence" in lowered or "overconfident" in lowered or "ready" in lowered:
            dashboard = self.get_dashboard()
            focus_item = dashboard["focus_item"]
            focus_label = focus_item["title"] if focus_item else "your current focus"
            return self._finish_coach_reply(state, tab, {
                "reply": (
                    f"You are {dashboard['metrics']['readiness_score']}/100 ready for {focus_label}. "
                    f"Your confidence gap is {dashboard['metrics']['confidence_gap']} points. "
                    "Ask for a topic quiz when you want me to update readiness from your answers."
                )
            })

        if "what can you do" in lowered or "help" in lowered:
            return self._finish_coach_reply(state, tab, {
                "reply": (
                    "I can rank what matters in the selected lecture, link outside resources, "
                    "quiz you on a chosen item, grade your answer, and update readiness. "
                    "Try: 'Study Lecture 1' or 'Quiz me on number 1'."
                )
            })

        return self._finish_coach_reply(state, tab, self._coach_material_study_reply(state, text, session))

    def get_coach_tabs(self) -> Dict[str, object]:
        state = self._ensure_state()
        return self._coach_public_state(state)

    def create_coach_tab(self, title: str = "") -> Dict[str, object]:
        state = self._ensure_state()
        tabs = state["coach_tabs"]
        tab = self._new_coach_tab(title.strip() or f"Chat {len(tabs) + 1}")
        tabs.append(tab)
        state["active_coach_tab_id"] = tab["id"]
        self.store.save_study_state(state)
        return self._coach_public_state(state)

    def rename_coach_tab(self, tab_id: str, title: str) -> Dict[str, object]:
        title = title.strip()
        if not title:
            raise ValueError("Tab title is required.")
        state = self._ensure_state()
        tab = self._coach_tab(state, tab_id)
        if not tab:
            raise ValueError("Coach tab was not found.")
        tab["title"] = title[:48]
        tab["updated_at"] = datetime.now().isoformat()
        self.store.save_study_state(state)
        return self._coach_public_state(state)

    def delete_coach_tab(self, tab_id: str) -> Dict[str, object]:
        state = self._ensure_state()
        tabs = state["coach_tabs"]
        if not any(tab.get("id") == tab_id for tab in tabs):
            raise ValueError("Coach tab was not found.")
        state["coach_tabs"] = [tab for tab in tabs if tab.get("id") != tab_id]
        if not state["coach_tabs"]:
            state["coach_tabs"] = [self._new_coach_tab("Chat 1")]
        if state.get("active_coach_tab_id") == tab_id:
            state["active_coach_tab_id"] = state["coach_tabs"][-1]["id"]
        self.store.save_study_state(state)
        return self._coach_public_state(state)

    def set_active_coach_tab(self, tab_id: str) -> Dict[str, object]:
        state = self._ensure_state()
        if not self._coach_tab(state, tab_id):
            raise ValueError("Coach tab was not found.")
        state["active_coach_tab_id"] = tab_id
        self.store.save_study_state(state)
        return self._coach_public_state(state)

    def _new_coach_tab(self, title: str) -> Dict[str, object]:
        now = datetime.now().isoformat()
        return {
            "id": f"coach-tab-{uuid.uuid4().hex[:8]}",
            "title": title[:48] or "Chat",
            "messages": [],
            "session": {},
            "created_at": now,
            "updated_at": now,
        }

    def _coach_tab(self, state: Dict[str, object], tab_id: str, create: bool = False) -> Dict[str, object]:
        for tab in state.get("coach_tabs", []):
            if tab.get("id") == tab_id:
                return tab
        if create:
            tab = self._new_coach_tab(f"Chat {len(state.get('coach_tabs', [])) + 1}")
            state.setdefault("coach_tabs", []).append(tab)
            return tab
        return {}

    def _append_coach_message(self, tab: Dict[str, object], role: str, text: str) -> None:
        tab.setdefault("messages", []).append(
            {
                "id": f"message-{uuid.uuid4().hex[:10]}",
                "role": role,
                "text": text,
                "created_at": datetime.now().isoformat(),
            }
        )
        tab["updated_at"] = datetime.now().isoformat()

    def _finish_coach_reply(self, state: Dict[str, object], tab: Dict[str, object], result: Dict[str, object]) -> Dict[str, object]:
        self._append_coach_message(tab, "assistant", str(result.get("reply", "")))
        self.store.save_study_state(state)
        result["coach"] = self._coach_public_state(state)
        if isinstance(result.get("dashboard"), dict):
            result["dashboard"]["coach"] = result["coach"]
        return result

    def _coach_public_state(self, state: Dict[str, object]) -> Dict[str, object]:
        self._normalize_coach_state(state)
        return {
            "active_tab_id": state["active_coach_tab_id"],
            "memory_count": len(state.get("coach_memory", {}).get("asked_questions", [])),
            "tabs": [
                {
                    "id": tab["id"],
                    "title": tab["title"],
                    "messages": tab.get("messages", []),
                    "updated_at": tab.get("updated_at", ""),
                    "has_open_quiz": bool(tab.get("session", {}).get("current_question")),
                }
                for tab in state.get("coach_tabs", [])
            ],
        }

    @staticmethod
    def _is_quiz_end(text: str) -> bool:
        return text in {"end", "stop", "stop quiz", "end quiz", "done", "finish", "finish quiz"}

    @staticmethod
    def _is_another_question(text: str) -> bool:
        return any(phrase in text for phrase in ["another question", "next question", "ask another", "quiz me again"])

    @staticmethod
    def _wants_quiz(text: str) -> bool:
        return any(
            phrase in text
            for phrase in [
                "quiz me",
                "give me a quiz",
                "give me an mcq",
                "give me a question",
                "start quiz",
                "test me",
                "multiple choice",
                "mcq",
                "short answer",
                "short form",
                "i studied",
            ]
        )

    @staticmethod
    def _wants_lecture_overview(text: str) -> bool:
        return (
            "what lectures" in text
            or "which lectures" in text
            or "lectures do i have" in text
            or "lectures should i study" in text
        )

    @staticmethod
    def _requested_question_type(text: str) -> str:
        if "short form" in text or "short answer" in text:
            return "Short answer"
        if "mcq" in text or "multiple choice" in text:
            return "MCQ"
        return ""

    def _focus_item_from_text(self, state: Dict[str, object], text: str, allow_kind_match: bool = True) -> Dict[str, object]:
        lowered = text.lower()
        active = self._active_item(state)
        scored = []
        query_terms = {term for term in re.findall(r"[a-z0-9]+", lowered) if len(term) >= 2}
        if not allow_kind_match:
            query_terms -= {
                "an",
                "answer",
                "answers",
                "entire",
                "form",
                "give",
                "lecture",
                "lectures",
                "mcq",
                "me",
                "multiple",
                "number",
                "on",
                "question",
                "questions",
                "quiz",
                "short",
                "start",
                "test",
                "the",
                "topic",
                "topics",
                "whole",
            }
        for item in self._sorted_items(state.get("academic_items", [])):
            title = str(item.get("title", "")).lower()
            subject = str(item.get("subject", "")).lower()
            kind = str(item.get("kind", "")).lower()
            score = 0
            if title and title in lowered:
                score += 12
            if subject and subject in lowered:
                score += 6
            if allow_kind_match and kind and kind in lowered:
                score += 3
            item_text = f"{title} {subject} {kind if allow_kind_match else ''}"
            item_terms = {term for term in re.findall(r"[a-z0-9]+", item_text) if len(term) >= 2}
            score += len(query_terms.intersection(item_terms))
            if score:
                scored.append((score, item))
        if scored:
            return max(scored, key=lambda pair: pair[0])[1]
        return active

    def _materials_for_focus(self, state: Dict[str, object], focus_item: Dict[str, object]) -> List[Dict[str, object]]:
        focus_id = focus_item.get("id", "") if focus_item else ""
        if not focus_id:
            return []
        return [
            material
            for material in state.get("materials", [])
            if material.get("academic_item_id") == focus_id
        ]

    def _topics_for_material(
        self,
        state: Dict[str, object],
        focus_item: Dict[str, object],
        material: Dict[str, object],
    ) -> List[StudyTopic]:
        topics = self._topics_for_focus(state, focus_item)
        if not material:
            return topics
        topic_ids = set(material.get("topic_ids", []))
        title = str(material.get("title", "")).strip()
        return [
            topic
            for topic in topics
            if topic.id in topic_ids or topic.source_material_id == material.get("id") or topic.module == title
        ]

    def _material_focus_score(
        self,
        state: Dict[str, object],
        focus_item: Dict[str, object],
        material: Dict[str, object],
    ) -> int:
        topics = self._topics_for_material(state, focus_item, material)
        if not topics:
            return 0
        average_risk = round(sum(self._risk_score(topic) for topic in topics) / len(topics))
        highest_risk = max(self._risk_score(topic) for topic in topics)
        average_confidence_gap = round(sum(100 - topic.confidence for topic in topics) / len(topics))
        untested_ratio = sum(1 for topic in topics if topic.quiz_average <= 0) / len(topics)
        evidence_risk = average_confidence_gap + round(untested_ratio * 22)
        return round((average_risk * 0.45) + (evidence_risk * 0.4) + (highest_risk * 0.15))

    def _material_from_text(
        self,
        state: Dict[str, object],
        text: str,
        focus_item: Dict[str, object],
        choose_highest_risk: bool = False,
    ) -> Dict[str, object]:
        materials = self._materials_for_focus(state, focus_item)
        if not materials:
            return {}
        lowered = text.lower()
        material = next(
            (item for item in materials if item.get("title", "").lower() in lowered),
            {},
        )
        if material:
            return material

        query_terms = [term for term in re.findall(r"[a-z0-9]+", lowered) if len(term) >= 2]
        scored = []
        lecture_match = re.search(r"\blecture\s+(\d+)\b", lowered)
        if choose_highest_risk and not lecture_match:
            return max(materials, key=lambda item: self._material_focus_score(state, focus_item, item))
        for item in materials:
            title = item.get("title", "").lower()
            if lecture_match:
                if re.search(rf"\blecture\s+{re.escape(lecture_match.group(1))}\b", title):
                    scored.append((10, item))
                continue
            score = sum(1 for term in query_terms if term in title)
            if score:
                scored.append((score, item))
        if scored:
            return max(scored, key=lambda pair: pair[0])[1]
        if lecture_match:
            return {}
        return materials[-1]

    def _coach_lecture_overview(self, state: Dict[str, object], text: str) -> Dict[str, object]:
        focus_item = self._focus_item_from_text(state, text)
        materials = self._materials_for_focus(state, focus_item)
        focus_label = focus_item.get("title", "this focus") if focus_item else "this focus"
        if not materials:
            return {"reply": f"I do not have lecture materials for {focus_label} yet. Upload notes in Materials first."}

        ranked = sorted(
            materials,
            key=lambda material: self._material_focus_score(state, focus_item, material),
            reverse=True,
        )
        lines = [f"Lectures to study for {focus_label}:"]
        for index, material in enumerate(ranked, start=1):
            topics = sorted(
                self._topics_for_material(state, focus_item, material),
                key=lambda topic: self._risk_score(topic),
                reverse=True,
            )
            topic_names = ", ".join(topic.name for topic in topics) if topics else "No extracted topics yet"
            score = self._material_focus_score(state, focus_item, material)
            lines.append(f"{index}. {material.get('title', 'Untitled lecture')} - focus score {score}. Topics: {topic_names}")
        lines.append("")
        lines.append("Ask 'Which lecture needs most focus?' for a ranked next step, or 'Quiz me on Lecture 2' when ready.")
        return {"reply": "\n".join(lines)}

    def _coach_material_study_reply(self, state: Dict[str, object], text: str, session: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        focus_item = self._focus_item_from_text(state, text)
        choose_highest_risk = "which lecture" in text.lower() or "most focus" in text.lower() or "most focusing" in text.lower()
        material, topics = self._resolve_material_and_topics(state, text, focus_item, choose_highest_risk=choose_highest_risk)
        if not topics:
            focus_label = focus_item.get("title", "this focus") if focus_item else "this focus"
            return {"reply": f"I do not have lecture topics for {focus_label} yet. Upload notes in Materials first."}

        items = self._llm_study_items(text, focus_item, material, topics)
        if not items:
            items = self._fallback_study_items(topics)

        if session is None:
            session = state.setdefault("coach_session", {})
        session.clear()
        session["mode"] = "study"
        session["last_study_topic_ids"] = [item["topic_id"] for item in items]
        session["last_lecture_topic_ids"] = [topic.id for topic in topics]
        session["last_focus_item_id"] = focus_item.get("id", "") if focus_item else ""
        session["last_material_id"] = material.get("id", "") if material else ""
        self.store.save_study_state(state)

        resources = self.resource_search.links_for_topics(
            [item["title"] for item in items],
            str(focus_item.get("subject", "")) if focus_item else "",
        )
        return {"reply": self._format_study_reply(focus_item, material, topics, items, resources)}

    def _resolve_material_and_topics(
        self,
        state: Dict[str, object],
        text: str,
        focus_item: Dict[str, object],
        choose_highest_risk: bool = False,
    ) -> Tuple[Dict[str, object], List[StudyTopic]]:
        material = self._material_from_text(state, text, focus_item, choose_highest_risk=choose_highest_risk)

        topics = self._topics_for_focus(state, focus_item)
        if material:
            filtered = self._topics_for_material(state, focus_item, material)
            if filtered:
                topics = filtered
        return material, sorted(topics, key=lambda topic: (topic.importance, self._risk_score(topic)), reverse=True)

    def _fallback_study_items(self, topics: List[StudyTopic]) -> List[Dict[str, object]]:
        items = []
        for topic in topics[:6]:
            note = topic.notes[0] if topic.notes else self._focus_reason(topic)
            items.append(
                {
                    "topic_id": topic.id,
                    "title": topic.name,
                    "why": self._focus_reason(topic),
                    "how": note,
                }
            )
        return items

    def _llm_study_items(
        self,
        user_text: str,
        focus_item: Dict[str, object],
        material: Dict[str, object],
        topics: List[StudyTopic],
    ) -> List[Dict[str, object]]:
        topic_payload = [
            {
                "id": topic.id,
                "name": topic.name,
                "mastery": topic.mastery,
                "confidence": topic.confidence,
                "importance": topic.importance,
                "notes": topic.notes,
            }
            for topic in topics[:10]
        ]
        prompt = f"""
/no_think
You are a course study coach. Use the uploaded material and topic records only.

Student request: {user_text}
Current focus: {focus_item.get('title', 'Current focus')} ({focus_item.get('subject', '')})
Material: {material.get('title', 'No specific material')}
Material excerpt:
{str(material.get('text_excerpt', ''))[:6000]}

Topics JSON:
{json.dumps(topic_payload)}

Return JSON only:
{{
  "items": [
    {{"topic_id": "existing id", "title": "topic title", "why": "why it matters", "how": "what to do first"}}
  ]
}}

Rules:
- Pick 3 to 6 important items.
- Use only topic_id values from Topics JSON.
- Prefer low confidence, missing quiz evidence, weak mastery, high importance, and concepts clearly supported by the material.
""".strip()
        parsed = self._ollama_json("coach-study-list", prompt, timeout=90)
        raw_items = parsed.get("items", [])
        if not isinstance(raw_items, list):
            return []

        by_id = {topic.id: topic for topic in topics}
        items = []
        seen = set()
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            topic_id = str(item.get("topic_id", "")).strip()
            if topic_id not in by_id or topic_id in seen:
                continue
            seen.add(topic_id)
            topic = by_id[topic_id]
            items.append(
                {
                    "topic_id": topic_id,
                    "title": str(item.get("title", topic.name)).strip()[:90] or topic.name,
                    "why": str(item.get("why", self._focus_reason(topic))).strip()[:260],
                    "how": str(item.get("how", topic.notes[0] if topic.notes else self._focus_reason(topic))).strip()[:260],
                }
            )
            if len(items) >= 6:
                break
        return items

    @staticmethod
    def _format_study_reply(
        focus_item: Dict[str, object],
        material: Dict[str, object],
        topics: List[StudyTopic],
        items: List[Dict[str, object]],
        resources: List[Dict[str, str]],
    ) -> str:
        focus_label = focus_item.get("title", "your focus") if focus_item else "your focus"
        material_label = material.get("title", "your uploaded material") if material else "your uploaded material"
        lines = [f"For {focus_label}, focus on {material_label} first."]
        if topics:
            lines.append("Lecture topics: " + ", ".join(topic.name for topic in topics))
        lines.append("")
        lines.append("Priority order:")
        for index, item in enumerate(items, start=1):
            lines.append(f"{index}. {item['title']} - {item['why']} Study move: {item['how']}")
        lines.append("")
        lines.append("Outside resources (non-NTU):")
        if resources:
            for resource in resources:
                label = resource["title"]
                if resource.get("source") == "generated":
                    label = f"{label} (fallback)"
                lines.append(f"- [{label}]({resource['url']})")
        else:
            lines.append("- No outside resources found right now. Use the lecture notes as the source of truth.")
        lines.append("")
        lines.append(
            "Quiz options: say 'Quiz me on the entire lecture', 'Quiz me on number 1', "
            "'Give me an MCQ on Lecture 2', or 'Give me a short form quiz on <topic name>'."
        )
        return "\n".join(lines)

    def _topic_from_text_or_session(self, state: Dict[str, object], text: str, session: Dict[str, object]) -> Optional[StudyTopic]:
        focus_item = self._active_item(state)
        topics = self._topics_for_focus(state, focus_item)
        match = re.search(r"\bnumber\s+(\d+)\b|\b#\s*(\d+)\b", text.lower())
        if match:
            index = int(next(group for group in match.groups() if group)) - 1
            topic_ids = session.get("last_study_topic_ids", [])
            if 0 <= index < len(topic_ids):
                target_id = topic_ids[index]
                for topic in topics:
                    if topic.id == target_id:
                        return topic

        lowered = text.lower()
        for topic in topics:
            if topic.name.lower() in lowered:
                return topic
        if session.get("topic_id"):
            for topic in topics:
                if topic.id == session["topic_id"]:
                    return topic
        return topics[0] if topics else None

    @staticmethod
    def _topic_index_from_text(text: str) -> Optional[int]:
        match = re.search(r"\btopic\s+(\d+)\b|\bnumber\s+(\d+)\b|\b#\s*(\d+)\b", text.lower())
        if not match:
            return None
        return int(next(group for group in match.groups() if group)) - 1

    @staticmethod
    def _wants_entire_lecture_quiz(text: str) -> bool:
        lowered = text.lower()
        return (
            "entire lecture" in lowered
            or "whole lecture" in lowered
            or ("lecture" in lowered and "topic" not in lowered and "number" not in lowered and "#" not in lowered)
        )

    def _resolve_quiz_scope(self, state: Dict[str, object], text: str, session: Dict[str, object]) -> Dict[str, object]:
        focus_item = self._focus_item_from_text(state, text, allow_kind_match=False)
        lowered = text.lower()
        named_focus = bool(
            focus_item
            and (
                str(focus_item.get("title", "")).lower() in lowered
                or str(focus_item.get("subject", "")).lower() in lowered
            )
        )
        if session.get("last_focus_item_id") and not named_focus:
            session_focus = self._academic_item_by_id(state, str(session["last_focus_item_id"]))
            if session_focus:
                focus_item = session_focus

        material = self._material_from_text(state, text, focus_item)
        named_material = bool(
            material
            and (
                str(material.get("title", "")).lower() in lowered
                or re.search(r"\blecture\s+\d+\b", lowered)
            )
        )
        requested_lecture = re.search(r"\blecture\s+\d+\b", lowered)
        if session.get("last_material_id") and not named_material and not requested_lecture:
            session_material = next(
                (item for item in self._materials_for_focus(state, focus_item) if item.get("id") == session.get("last_material_id")),
                {},
            )
            if session_material:
                material = session_material

        if requested_lecture and not material:
            focus_label = focus_item.get("title", "this focus") if focus_item else "this focus"
            return {
                "scope": "missing_material",
                "material_id": "",
                "topic_ids": [],
                "message": f"I do not have that lecture material for {focus_label} yet. Upload notes in Materials first.",
            }

        material_topics = sorted(
            self._topics_for_material(state, focus_item, material),
            key=lambda topic: self._risk_score(topic),
            reverse=True,
        ) if material else []
        focus_topics = sorted(self._topics_for_focus(state, focus_item), key=lambda topic: self._risk_score(topic), reverse=True)
        candidate_topics = material_topics or focus_topics

        topic_index = self._topic_index_from_text(text)
        if topic_index is not None:
            indexed_topic_ids = session.get("last_study_topic_ids", [])
            if material and "topic" in lowered:
                indexed_topics = material_topics
                if 0 <= topic_index < len(indexed_topics):
                    return {
                        "scope": "topic",
                        "material_id": material.get("id", ""),
                        "topic_ids": [indexed_topics[topic_index].id],
                    }
            if 0 <= topic_index < len(indexed_topic_ids):
                return {
                    "scope": "topic",
                    "material_id": material.get("id", session.get("last_material_id", "")),
                    "topic_ids": [indexed_topic_ids[topic_index]],
                }

        for topic in candidate_topics:
            if topic.name.lower() in lowered:
                return {
                    "scope": "topic",
                    "material_id": material.get("id", ""),
                    "topic_ids": [topic.id],
                }

        if self._wants_entire_lecture_quiz(text) and material_topics:
            return {
                "scope": "lecture",
                "material_id": material.get("id", ""),
                "topic_ids": [topic.id for topic in material_topics],
            }

        if session.get("topic_id"):
            return {
                "scope": "topic",
                "material_id": session.get("last_material_id", ""),
                "topic_ids": [str(session["topic_id"])],
            }

        return {
            "scope": "topic",
            "material_id": material.get("id", "") if material else "",
            "topic_ids": [candidate_topics[0].id] if candidate_topics else [],
        }

    def _coach_next_question(self, state: Dict[str, object], session: Dict[str, object]) -> Dict[str, object]:
        quiz_scope = session.get("quiz_scope", {})
        topic_ids = quiz_scope.get("topic_ids", []) if isinstance(quiz_scope, dict) else []
        if not topic_ids and session.get("topic_id"):
            topic_ids = [str(session["topic_id"])]
        selected_topic_id = random.choice(topic_ids) if len(topic_ids) > 1 else (topic_ids[0] if topic_ids else "")
        topic = self._topic_by_id(state, str(selected_topic_id))
        if topic is None:
            session.clear()
            self.store.save_study_state(state)
            return {"reply": "I could not find that topic anymore. Pick a topic from the latest study list."}

        memory = state.setdefault("coach_memory", {}).setdefault("asked_questions", [])
        tab_asked = session.setdefault("asked_questions", [])
        asked = list(dict.fromkeys([*memory, *tab_asked]))
        question_type = self._next_question_type(session)
        question = self._llm_question(topic, asked, question_type)
        if not question:
            question = self._fallback_question(topic, len(asked), question_type)
        if question["question"] not in asked:
            tab_asked.append(question["question"])
            memory.append(question["question"])
        asked_types = session.setdefault("asked_question_types", [])
        asked_types.append(question.get("type", question_type))
        session["current_question"] = question
        session["mode"] = "quiz"
        session["topic_id"] = topic.id
        session["current_question_topic_id"] = topic.id
        session.pop("preferred_question_type", None)
        self.store.save_study_state(state)
        return {"reply": self._format_question(topic, question)}

    @staticmethod
    def _next_question_type(session: Dict[str, object]) -> str:
        preferred = str(session.get("preferred_question_type", "")).strip()
        if preferred:
            return preferred
        return "MCQ" if random.random() < 0.55 else "Short answer"

    def _llm_question(self, topic: StudyTopic, asked_questions: List[str], question_type: str) -> Dict[str, object]:
        prompt = f"""
/no_think
Create one new study question for this topic. Avoid repeating previous questions.

Topic: {topic.name}
Material section: {topic.module}
Notes: {json.dumps(topic.notes)}
Previous questions: {json.dumps(asked_questions[-12:])}
Question type to create now: {question_type}
Random seed: {uuid.uuid4().hex}

Return JSON only:
{{"type": "MCQ|Short answer", "question": "...", "choices": ["A. ...", "B. ..."], "answer": "...", "rubric": ["..."]}}

Rules:
- Stay strictly inside the uploaded lecture note and this extracted topic.
- For MCQ, include 4 choices and mark the correct choice in answer.
- If Question type to create now is Short answer, do not return choices.
- Do not ask the same question as any previous question.
""".strip()
        parsed = self._ollama_json("coach-question", prompt, timeout=70)
        question = str(parsed.get("question", "")).strip()
        answer = str(parsed.get("answer", "")).strip()
        if not question or not answer:
            return {}
        choices = parsed.get("choices", [])
        rubric = parsed.get("rubric", [])
        return {
            "type": "MCQ" if "mcq" in str(parsed.get("type", question_type)).lower() else "Short answer",
            "question": question[:700],
            "choices": [str(choice).strip()[:180] for choice in choices if str(choice).strip()][:5] if isinstance(choices, list) else [],
            "answer": answer[:900],
            "rubric": [str(item).strip()[:180] for item in rubric if str(item).strip()][:5] if isinstance(rubric, list) else [],
        }

    @staticmethod
    def _fallback_question(topic: StudyTopic, asked_count: int, question_type: str = "") -> Dict[str, object]:
        notes = topic.notes or [f"Explain the core idea behind {topic.name}."]
        note = notes[asked_count % len(notes)]
        kind = "MCQ" if question_type == "MCQ" else "Short answer"
        if kind == "MCQ":
            return {
                "type": kind,
                "question": f"Which statement best explains {topic.name} in this material?",
                "choices": [
                    f"A. {note}",
                    "B. It is only administrative course metadata.",
                    "C. It is unrelated to the lecture's main concepts.",
                    "D. It should be skipped because it has no exam relevance.",
                ],
                "answer": "A",
                "rubric": [note],
            }
        return {
            "type": kind,
            "question": f"Explain {topic.name} using this material detail: {note}",
            "choices": [],
            "answer": note,
            "rubric": [note, "Uses the course concept accurately.", "Stays specific rather than generic."],
        }

    @staticmethod
    def _lecture_label(topic: StudyTopic) -> str:
        match = re.search(r"\blecture\s+(\d+)\b", topic.module, re.IGNORECASE)
        if match:
            return f"Lecture {match.group(1)}"
        return topic.module or "Lecture"

    def _format_question(self, topic: StudyTopic, question: Dict[str, object]) -> str:
        lines = [
            f"{question['type']} | {self._lecture_label(topic)} | {topic.name}",
            str(question["question"]),
        ]
        for choice in question.get("choices", []):
            lines.append(str(choice))
        lines.append("Reply with your answer. Say 'Another question' after I grade it, or 'End' to stop.")
        return "\n".join(lines)

    def _coach_grade_answer(self, state: Dict[str, object], session: Dict[str, object], student_answer: str) -> Dict[str, object]:
        topic = self._topic_by_id(state, str(session.get("current_question_topic_id") or session.get("topic_id", "")))
        question = session.get("current_question", {})
        if topic is None or not isinstance(question, dict):
            session.clear()
            self.store.save_study_state(state)
            return {"reply": "The quiz state was out of date. Ask me to quiz a topic again."}

        grade = self._grade_mcq_answer(question, student_answer)
        if not grade:
            grade = self._llm_grade(topic, question, student_answer)
        if not grade:
            grade = self._fallback_grade(question, student_answer)
        self._apply_quiz_score(state, topic.id, int(grade["score"]), str(question.get("type", "")))
        session.pop("current_question", None)
        self.store.save_study_state(state)
        dashboard = self.get_dashboard()
        reply = (
            f"Score: {grade['score']}/100\n"
            f"Feedback: {grade['feedback']}\n"
            f"Model answer: {question.get('answer', '')}\n\n"
            "Say 'Another question' to continue this topic, 'Quiz me on number 2' to switch, or 'End' to stop."
        )
        return {"reply": reply, "dashboard": dashboard}

    def _llm_grade(self, topic: StudyTopic, question: Dict[str, object], student_answer: str) -> Dict[str, object]:
        prompt = f"""
/no_think
Grade the student's answer for this course topic.

Topic: {topic.name}
Topic notes: {json.dumps(topic.notes)}
Question: {question.get('question', '')}
Expected answer: {question.get('answer', '')}
Rubric: {json.dumps(question.get('rubric', []))}
Student answer: {student_answer}

Return JSON only:
{{"score": 0, "feedback": "one concise sentence"}}

Rules:
- Score 0-100.
- Grade semantic correctness, not exact wording.
- Treat the expected answer as a reference answer, not the only valid answer.
- Award 90-100 when the student captures the core idea with equivalent terms, a valid example, or a longer correct explanation.
- Do not penalize length, extra correct detail, or lack of concision.
- Give partial credit for partially correct concepts.
- Penalize contradictions, unsupported claims, or unrelated answers.
""".strip()
        parsed = self._ollama_json("coach-grade", prompt, timeout=60)
        if "score" not in parsed:
            return {}
        grade = {
            "score": self._clamp_int(parsed.get("score", 0), 0, 100),
            "feedback": str(parsed.get("feedback", "Answer graded.")).strip()[:260],
        }
        if "mcq" not in str(question.get("type", "")).lower():
            return self._reconcile_short_answer_grade(grade, self._fallback_grade(question, student_answer))
        return grade

    @staticmethod
    def _grade_mcq_answer(question: Dict[str, object], student_answer: str) -> Dict[str, object]:
        question_type = str(question.get("type", "")).lower()
        choices = question.get("choices", [])
        if "mcq" not in question_type and not choices:
            return {}

        expected = str(question.get("answer", "")).strip()
        expected_match = re.match(r"^([A-Da-d])(?:[\.\)]|\s|$)", expected)
        if not expected_match:
            for choice in choices if isinstance(choices, list) else []:
                choice_text = str(choice).strip()
                if expected and expected.lower() in choice_text.lower():
                    choice_match = re.match(r"^([A-Da-d])(?:[\.\)]|\s)", choice_text)
                    if choice_match:
                        expected_match = choice_match
                        break
        if not expected_match:
            return {}

        expected_letter = expected_match.group(1).upper()
        submitted_match = re.match(r"^\s*([A-Da-d])(?:[\.\)]|\s|$)", student_answer)
        if not submitted_match:
            return {}

        submitted_letter = submitted_match.group(1).upper()
        if submitted_letter == expected_letter:
            return {
                "score": 100,
                "feedback": f"Correct. {expected_letter} is the best answer for this MCQ.",
            }
        return {
            "score": 0,
            "feedback": f"Not correct. The best answer is {expected_letter}.",
        }

    @staticmethod
    def _fallback_grade(question: Dict[str, object], student_answer: str) -> Dict[str, object]:
        expected_text = " ".join(
            [str(question.get("answer", ""))]
            + [str(item) for item in question.get("rubric", []) if str(item).strip()]
        )
        expected_terms = StudyStrategyService._semantic_answer_terms(expected_text)
        submitted_terms = StudyStrategyService._semantic_answer_terms(student_answer)
        matched = len(expected_terms.intersection(submitted_terms))
        if not expected_terms:
            score = 35
        else:
            coverage = matched / max(len(expected_terms), 1)
            if coverage >= 0.82:
                score = 100
            elif coverage >= 0.62:
                score = round(82 + 18 * (coverage - 0.62) / 0.2)
            elif coverage >= 0.38:
                score = round(58 + 24 * (coverage - 0.38) / 0.24)
            else:
                score = round(25 + 33 * coverage / 0.38)
        return {
            "score": max(0, min(100, score)),
            "feedback": "I used local semantic grading because the local model was unavailable.",
        }

    @staticmethod
    def _semantic_answer_terms(text: str) -> set:
        terms = set()
        for raw_token in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower()):
            token = StudyStrategyService._ANSWER_ALIASES.get(raw_token, raw_token)
            token = StudyStrategyService._stem_answer_term(token)
            token = StudyStrategyService._ANSWER_ALIASES.get(token, token)
            if token and token not in StudyStrategyService._ANSWER_STOPWORDS:
                terms.add(token)
        return terms

    @staticmethod
    def _stem_answer_term(token: str) -> str:
        for suffix in ("ing", "ed", "es", "s"):
            if len(token) > len(suffix) + 3 and token.endswith(suffix):
                return token[: -len(suffix)]
        return token

    @staticmethod
    def _reconcile_short_answer_grade(llm_grade: Dict[str, object], semantic_grade: Dict[str, object]) -> Dict[str, object]:
        llm_score = StudyStrategyService._clamp_int(llm_grade.get("score", 0), 0, 100)
        semantic_score = StudyStrategyService._clamp_int(semantic_grade.get("score", 0), 0, 100)
        feedback = str(llm_grade.get("feedback", "Answer graded.")).strip()
        style_penalty = any(
            phrase in feedback.lower()
            for phrase in ["concise", "too long", "length", "wordy", "brevity", "more direct"]
        )
        if style_penalty and llm_score >= 70:
            return {
                "score": max(llm_score, semantic_score, 90),
                "feedback": "Correct. I did not penalize answer length because the key idea was present.",
            }
        if semantic_score >= 88 and semantic_score > llm_score and llm_score >= 50:
            return {
                "score": semantic_score,
                "feedback": "Correct. Your wording differs from the model answer, but it covers the key idea.",
            }
        return {
            "score": llm_score,
            "feedback": feedback[:260] or "Answer graded.",
        }

    def _apply_quiz_score(self, state: Dict[str, object], topic_id: str, score: int, question_type: str = "") -> None:
        score = self._clamp_int(score, 0, 100)
        is_mcq = "mcq" in question_type.lower()
        delta = 3 if is_mcq else 5
        penalty = 1 if is_mcq else 2
        mastery_delta = delta if score >= 70 else -penalty
        for topic in state["topics"]:
            if topic["id"] != topic_id:
                continue
            old_mastery = int(topic.get("mastery", 0))
            old_confidence = int(topic.get("confidence", 0))
            old_quiz = int(topic.get("quiz_average", 0))
            topic["mastery"] = self._clamp_int(old_mastery + mastery_delta, 0, 100)
            topic["confidence"] = self._clamp_int(old_confidence + mastery_delta, 0, 100)
            topic["quiz_average"] = self._clamp_int(round(old_quiz * 0.5 + score * 0.5) if old_quiz else score, 0, 100)
            topic["last_reviewed"] = datetime.now().strftime("%Y-%m-%d")
            break

    def _topic_by_id(self, state: Dict[str, object], topic_id: str) -> Optional[StudyTopic]:
        for topic in self._topic_objects(state):
            if topic.id == topic_id:
                return topic
        return None

    def _ollama_json(self, purpose: str, prompt: str, timeout: int = 80) -> Dict[str, object]:
        if not self.llm_config.is_configured() or self.llm_config.provider != "ollama":
            return {}
        started_at = time.perf_counter()
        print(f"[coach] ollama start purpose={purpose} model={self.llm_config.model}", flush=True)
        payload = {
            "model": self.llm_config.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.35, "num_ctx": 8192},
        }
        request = urllib.request.Request(
            self.llm_config.base_url.rstrip("/") + "/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            parsed = MaterialAnalyzer._parse_json_object(str(data.get("response", "")))
            elapsed = time.perf_counter() - started_at
            print(f"[coach] ollama ok purpose={purpose} elapsed={elapsed:.1f}s", flush=True)
            return parsed
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
            elapsed = time.perf_counter() - started_at
            print(f"[coach] ollama failed purpose={purpose} elapsed={elapsed:.1f}s error={type(exc).__name__}: {exc}", flush=True)
            return {}

    @staticmethod
    def _clamp_int(value: object, minimum: int, maximum: int) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = minimum
        return max(minimum, min(maximum, number))

    def _ensure_state(self) -> Dict[str, object]:
        state = self.store.load_study_state()
        if not state:
            state = self._seed_state()
            self.store.save_study_state(state)
            return state
        state = self._normalize_state(state)
        self.store.save_study_state(state)
        return state

    def _normalize_state(self, state: Dict[str, object]) -> Dict[str, object]:
        state.setdefault("profile", StudyProfile().to_dict())
        state.setdefault("topics", [])
        state.setdefault("materials", [])
        state.setdefault("check_ins", [])
        active_item_id = state.get("active_item_id", "")
        default_target = self._clamp_int(state["profile"].get("target_readiness", 0), 0, 100)
        for item in state.get("academic_items", []):
            if "target_readiness" not in item:
                item["target_readiness"] = default_target if item.get("id") == active_item_id else 0
        for material in state["materials"]:
            material.setdefault("id", f"material-{uuid.uuid4().hex[:8]}")
            material.setdefault("topic_ids", [])
            material.setdefault("academic_item_id", "")
            material.setdefault("text_excerpt", "")
        for topic in state["topics"]:
            topic.setdefault("source_material_id", "")
            topic.setdefault("academic_item_id", self._resolve_topic_academic_item_id(state, topic))
        state.setdefault("coach_session", {})
        state.setdefault("last_plan_request", {})
        self._normalize_coach_state(state)
        self._backfill_material_topic_links(state)
        if "academic_items" not in state:
            legacy_profile = state["profile"]
            title = legacy_profile.pop("exam_title", "Main Exam")
            due_date = legacy_profile.pop("exam_date", datetime.now().date().isoformat())
            item = AcademicItem(
                id="item-primary",
                kind="exam",
                title=title,
                subject="General",
                due_date=due_date,
                target_readiness=self._clamp_int(legacy_profile.get("target_readiness", 0), 0, 100),
            )
            state["academic_items"] = [item.to_dict()]
            state["active_item_id"] = item.id
        elif not state.get("active_item_id") and state["academic_items"]:
            state["active_item_id"] = state["academic_items"][0]["id"]
        elif state.get("active_item_id") and not any(item["id"] == state["active_item_id"] for item in state["academic_items"]):
            state["active_item_id"] = state["academic_items"][0]["id"] if state["academic_items"] else ""
        return state

    def _normalize_coach_state(self, state: Dict[str, object]) -> None:
        memory = state.setdefault("coach_memory", {})
        asked_questions = memory.setdefault("asked_questions", [])
        if not isinstance(asked_questions, list):
            memory["asked_questions"] = []

        tabs = state.get("coach_tabs")
        if not isinstance(tabs, list) or not tabs:
            legacy_session = state.get("coach_session", {})
            if not isinstance(legacy_session, dict):
                legacy_session = {}
            state["coach_tabs"] = [
                {
                    **self._new_coach_tab("Chat 1"),
                    "id": "coach-tab-default",
                    "session": legacy_session,
                }
            ]
        for index, tab in enumerate(state["coach_tabs"], start=1):
            tab.setdefault("id", f"coach-tab-{uuid.uuid4().hex[:8]}")
            tab.setdefault("title", f"Chat {index}")
            tab.setdefault("messages", [])
            tab.setdefault("session", {})
            tab.setdefault("created_at", datetime.now().isoformat())
            tab.setdefault("updated_at", tab.get("created_at", datetime.now().isoformat()))
            if not isinstance(tab["messages"], list):
                tab["messages"] = []
            if not isinstance(tab["session"], dict):
                tab["session"] = {}

        active_tab_id = str(state.get("active_coach_tab_id", "")).strip()
        if not active_tab_id or not any(tab.get("id") == active_tab_id for tab in state["coach_tabs"]):
            state["active_coach_tab_id"] = state["coach_tabs"][0]["id"]

    def _seed_state(self) -> Dict[str, object]:
        if not self.seed_demo:
            return {
                "profile": StudyProfile(target_readiness=0, default_study_minutes=90).to_dict(),
                "academic_items": [],
                "active_item_id": "",
                "topics": [],
                "materials": [],
                "check_ins": [],
                "coach_session": {},
                "coach_memory": {"asked_questions": []},
                "coach_tabs": [
                    {
                        "id": "coach-tab-default",
                        "title": "Chat 1",
                        "messages": [],
                        "session": {},
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    }
                ],
                "active_coach_tab_id": "coach-tab-default",
            }
        exam_date = (datetime.now() + timedelta(days=12)).date().isoformat()
        assignment_date = (datetime.now() + timedelta(days=6)).date().isoformat()
        quiz_date = (datetime.now() + timedelta(days=19)).date().isoformat()
        academic_items = [
            AcademicItem("item-sc4052-final", "exam", "SC4052 Cloud Computing Final", "SC4052", exam_date, 82),
            AcademicItem("item-sc4052-assignment", "assignment", "SC4052 Assignment 3", "SC4052", assignment_date, 0),
            AcademicItem("item-sc4021-quiz", "quiz", "SC4021 Quiz 2", "SC4021", quiz_date, 0),
        ]
        topics = [
            StudyTopic("topic-virtualization", "Virtualization and Containers", "Cloud Foundations", 62, 78, 8, "2 days ago", ["Contrast hypervisors with containers.", "Know isolation tradeoffs."], 58, "", academic_items[0].id),
            StudyTopic("topic-scheduling", "Resource Scheduling", "Compute Orchestration", 41, 69, 10, "5 days ago", ["Review placement heuristics.", "Know fairness vs utilization tradeoff."], 44, "", academic_items[0].id),
            StudyTopic("topic-storage", "Distributed Storage", "Data Services", 55, 61, 8, "3 days ago", ["Compare replication and erasure coding."], 52, "", academic_items[0].id),
            StudyTopic("topic-security", "Cloud Security Models", "Security", 37, 74, 9, "6 days ago", ["Zero trust assumptions.", "Shared responsibility gaps."], 35, "", academic_items[0].id),
            StudyTopic("topic-consistency", "Consistency and Replication", "Data Services", 48, 58, 9, "4 days ago", ["Linearizability vs eventual consistency."], 46, "", academic_items[0].id),
            StudyTopic("topic-pricing", "Cloud Pricing and Autoscaling", "Operations", 71, 73, 6, "1 day ago", ["Cost-aware scaling examples."], 68, "", academic_items[0].id),
        ]
        return {
            "profile": StudyProfile(target_readiness=82, default_study_minutes=90).to_dict(),
            "academic_items": [item.to_dict() for item in academic_items],
            "active_item_id": academic_items[0].id,
            "topics": [topic.to_dict() for topic in topics],
            "materials": [],
            "check_ins": [],
            "coach_session": {},
            "coach_memory": {"asked_questions": []},
            "coach_tabs": [
                {
                    "id": "coach-tab-default",
                    "title": "Chat 1",
                    "messages": [],
                    "session": {},
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            ],
            "active_coach_tab_id": "coach-tab-default",
        }

    def _topic_objects(self, state: Dict[str, object]) -> List[StudyTopic]:
        return [StudyTopic(**topic) for topic in state["topics"]]

    def _topics_for_focus(self, state: Dict[str, object], focus_item: Dict[str, object]) -> List[StudyTopic]:
        focus_id = focus_item.get("id", "")
        if not focus_id:
            return []
        return [topic for topic in self._topic_objects(state) if topic.academic_item_id == focus_id]

    def _resolve_topic_academic_item_id(self, state: Dict[str, object], topic: Dict[str, object]) -> str:
        material_id = str(topic.get("source_material_id", "")).strip()
        for material in state["materials"]:
            if material.get("id") == material_id and material.get("academic_item_id"):
                return str(material["academic_item_id"])

        seeded_topic_ids = {
            "topic-virtualization",
            "topic-scheduling",
            "topic-storage",
            "topic-security",
            "topic-consistency",
            "topic-pricing",
        }
        if topic.get("id") in seeded_topic_ids:
            for item in state.get("academic_items", []):
                if item.get("id") == "item-sc4052-final":
                    return str(item["id"])

        return str(state.get("active_item_id") or "")

    def _sorted_items(self, raw_items: List[Dict[str, object]]) -> List[Dict[str, object]]:
        items = sorted(raw_items, key=lambda item: item["due_date"])
        today = datetime.now().date()
        normalized = []
        for item in items:
            due_date = datetime.fromisoformat(item["due_date"]).date()
            normalized.append(
                {
                    **item,
                    "days_left": max(0, (due_date - today).days),
                    "label": item["kind"].title(),
                }
            )
        return normalized

    def _active_item(self, state: Dict[str, object]) -> Dict[str, object]:
        active_id = state.get("active_item_id", "")
        for item in self._sorted_items(state["academic_items"]):
            if item["id"] == active_id:
                return item
        items = self._sorted_items(state["academic_items"])
        return items[0] if items else {}

    def _academic_item_by_id(self, state: Dict[str, object], item_id: str) -> Dict[str, object]:
        for item in self._sorted_items(state["academic_items"]):
            if item["id"] == item_id:
                return item
        return {}

    def _build_metrics(self, profile: StudyProfile, focus_item: Dict[str, object], topics: List[StudyTopic]) -> Dict[str, object]:
        target_readiness = self._clamp_int(focus_item.get("target_readiness", profile.target_readiness), 0, 100)
        if not topics:
            return {
                "focus_title": focus_item.get("title", "Current focus"),
                "focus_subject": focus_item.get("subject", ""),
                "focus_kind": focus_item.get("label", "Item"),
                "focus_date": focus_item.get("due_date", ""),
                "days_left": focus_item.get("days_left", 0),
                "readiness_score": 0,
                "target_readiness": target_readiness,
                "confidence_gap": 0,
                "confidence_risk_topic": "No topics for this focus yet",
                "next_focus": "Add notes for this focus",
            }
        weighted_total = sum(topic.mastery * topic.importance for topic in topics)
        total_weight = sum(topic.importance for topic in topics) or 1
        readiness = round(weighted_total / total_weight)
        confidence_gap = round(sum(max(0, topic.confidence - topic.mastery) for topic in topics) / max(len(topics), 1))
        confidence_risk_topic = max(topics, key=lambda item: item.confidence - item.mastery).name
        next_focus = topics[0].name if topics else "No topics yet"
        return {
            "focus_title": focus_item.get("title", "Current focus"),
            "focus_subject": focus_item.get("subject", ""),
            "focus_kind": focus_item.get("label", "Item"),
            "focus_date": focus_item.get("due_date", ""),
            "days_left": focus_item.get("days_left", 0),
            "readiness_score": readiness,
            "target_readiness": target_readiness,
            "confidence_gap": confidence_gap,
            "confidence_risk_topic": confidence_risk_topic,
            "next_focus": next_focus,
        }

    def _build_readiness_cards(self, topics: List[StudyTopic]) -> List[Dict[str, object]]:
        cards = []
        for topic in topics:
            risk = self._risk_score(topic)
            gap = topic.confidence - topic.mastery
            if risk >= 75:
                status = "Critical"
            elif risk >= 58:
                status = "Shaky"
            else:
                status = "Stable"
            cards.append(
                {
                    "id": topic.id,
                    "title": topic.name,
                    "module": topic.module,
                    "mastery": topic.mastery,
                    "confidence": topic.confidence,
                    "importance": topic.importance,
                    "risk_score": risk,
                    "status_label": status,
                    "reason": self._focus_reason(topic),
                    "confidence_gap": gap,
                    "last_reviewed": topic.last_reviewed,
                }
            )
        return cards

    def _build_recall_deck(self, topics: List[StudyTopic]) -> List[Dict[str, object]]:
        deck = []
        for topic in topics:
            note = topic.notes[0] if topic.notes else f"Explain the core mechanism behind {topic.name.lower()}."
            deck.append(
                {
                    "topic": topic.name,
                    "prompt": f"Without notes, explain: {note}",
                    "check": f"Then compare your answer against the key distinction in {topic.name}.",
                }
            )
            deck.append(
                {
                    "topic": topic.name,
                    "prompt": f"Write one exam-style question that tests {topic.name.lower()}, then answer it from memory.",
                    "check": "Mark anything you could not recall within 90 seconds.",
                }
            )
        return deck[:6]

    def _risk_score(self, topic: StudyTopic) -> int:
        gap = max(0, topic.confidence - topic.mastery)
        low_confidence = 100 - topic.confidence
        quiz_evidence_gap = 18 if topic.quiz_average <= 0 else max(0, 70 - topic.quiz_average) * 0.25
        score = (100 - topic.mastery) * 0.34 + low_confidence * 0.36 + gap * 0.16 + topic.importance * 2.1 + quiz_evidence_gap
        return round(score)

    def _panic_score(self, topic: StudyTopic) -> float:
        return (100 - topic.mastery) * 0.5 + topic.importance * 4.5

    def _focus_reason(self, topic: StudyTopic) -> str:
        gap = topic.confidence - topic.mastery
        if topic.quiz_average <= 0:
            return "No quiz evidence yet. Test this topic before treating the lecture as stable."
        if topic.confidence <= 55:
            return "Low confidence score. Prioritize this before polishing lectures you have tested more."
        if gap >= 18:
            return "You feel better about this topic than your recent performance suggests."
        if topic.mastery <= 45:
            return "Low mastery on a high-yield topic. Recover this before polishing stronger material."
        if topic.importance >= 9:
            return "Exam-relevant topic with meaningful upside if stabilized now."
        return "Worth revisiting, but not your main risk."

    def _panic_reason(self, topic: StudyTopic) -> str:
        if topic.mastery <= 40:
            return "Major gap. Learn the skeleton answer, not the perfect answer."
        if topic.importance >= 9:
            return "High-yield topic. Strong chance of showing up in some form."
        return "Good return on a short rescue pass."

    def _panic_headline(self, horizon: str) -> str:
        if horizon == "three_hours":
            return "3-hour rescue plan"
        if horizon == "weekend":
            return "Weekend recovery plan"
        return "Tonight-only triage plan"

    @staticmethod
    def _plan_pace(minutes: int) -> str:
        if minutes <= 90:
            return "Fast"
        if minutes <= 180:
            return "Balanced"
        return "Chill"

    def _format_plan_reply(self, plan_payload: Dict[str, object]) -> str:
        lines = [plan_payload["headline"] + ":"]
        for item in plan_payload["plan"]:
            lines.append(f"• {item['title']} for {item['minutes']} min: {item['mode']}. {item['reason']}")
        return "\n".join(lines)

    def _format_panic_reply(self, panic_payload: Dict[str, object]) -> str:
        lines = [panic_payload["headline"] + ":"]
        for item in panic_payload["must_cover"]:
            lines.append(f"• {item['order']}. {item['title']} for {item['minutes']} min. {item['reason']}")
        if panic_payload["skip"]:
            lines.append("Skip for now: " + ", ".join(panic_payload["skip"]))
        return "\n".join(lines)

    def _extract_minutes(self, text: str) -> int:
        match = re.search(r"(\d+)\s*(minute|minutes|min|mins)", text)
        if match:
            return int(match.group(1))
        match = re.search(r"(\d+)\s*(hour|hours|hr|hrs)", text)
        if match:
            return int(match.group(1)) * 60
        return 90

    def _extract_topics(self, title: str, text: str) -> List[Tuple[str, List[str]]]:
        lines = [line.strip("•-* \t") for line in text.splitlines() if line.strip()]
        extracted: List[Tuple[str, List[str]]] = []
        current_title = ""
        current_notes: List[str] = []
        for line in lines:
            clean = re.sub(r"^\d+[\.\)]\s*", "", line)
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
        if extracted:
            return extracted[:5]

        summary_lines = [line for line in lines if len(line.split()) >= 4][:4]
        if summary_lines:
            return [(f"{title} Topic {index + 1}", [line]) for index, line in enumerate(summary_lines)]
        return [(title, ["Review imported material and create recall questions from it."])]

    @staticmethod
    def _backfill_material_topic_links(state: Dict[str, object]) -> None:
        unclaimed_topics = {
            topic["id"]: topic
            for topic in state["topics"]
            if not str(topic.get("source_material_id", "")).strip()
        }
        for material in state["materials"]:
            if material.get("topic_ids"):
                continue
            title = str(material.get("title", "")).strip()
            topic_names = {str(name).strip() for name in material.get("topics", [])}
            matched_ids = []
            for topic_id, topic in list(unclaimed_topics.items()):
                if topic.get("module") != title or topic.get("name") not in topic_names:
                    continue
                topic["source_material_id"] = material["id"]
                matched_ids.append(topic_id)
                unclaimed_topics.pop(topic_id, None)
            material["topic_ids"] = matched_ids
