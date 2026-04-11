from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from chief_of_staff.models import AcademicItem, StudyProfile, StudyTopic
from chief_of_staff.storage import JsonStore


class StudyStrategyService:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def get_dashboard(self) -> Dict[str, object]:
        state = self._ensure_state()
        topics = self._topic_objects(state)
        topics_by_risk = sorted(topics, key=self._risk_score, reverse=True)
        profile = StudyProfile(**state["profile"])
        focus_item = self._active_item(state)
        metrics = self._build_metrics(profile, focus_item, topics_by_risk)
        readiness_cards = self._build_readiness_cards(topics_by_risk)
        plan = self.build_plan(profile.default_study_minutes)["plan"]
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
            "plan": plan,
            "panic_mode": panic,
            "recall_deck": recall,
            "topics": readiness_cards,
            "materials": state["materials"][-3:][::-1],
        }

    def add_academic_item(self, title: str, subject: str, due_date: str, kind: str) -> Dict[str, object]:
        state = self._ensure_state()
        item = AcademicItem(
            id=f"item-{uuid.uuid4().hex[:8]}",
            kind=kind,
            title=title,
            subject=subject,
            due_date=due_date,
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

    def build_plan(self, minutes: int) -> Dict[str, object]:
        state = self._ensure_state()
        focus_item = self._active_item(state)
        topics = sorted(self._topic_objects(state), key=self._risk_score, reverse=True)
        remaining = max(30, int(minutes))
        plan = []
        cycle = [
            "Active recall sprint",
            "Closed-book concept summary",
            "Worked example repair",
            "Confidence calibration quiz",
        ]
        index = 0
        for topic in topics:
            if remaining <= 0 or len(plan) >= 4:
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
        return {
            "headline": f"{minutes}-minute plan for {item_label}",
            "plan": plan,
        }

    def build_panic_mode(self, horizon: str) -> Dict[str, object]:
        state = self._ensure_state()
        topics = sorted(self._topic_objects(state), key=self._panic_score, reverse=True)
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
        return {
            "headline": self._panic_headline(horizon),
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

    def import_material(self, title: str, text: str) -> Dict[str, object]:
        state = self._ensure_state()
        material_id = f"material-{uuid.uuid4().hex[:8]}"
        extracted_topics = self._extract_topics(title, text)
        created = []
        created_ids = []
        for name, notes in extracted_topics:
            topic = StudyTopic(
                id=f"topic-{uuid.uuid4().hex[:8]}",
                name=name,
                module=title,
                mastery=38,
                confidence=52,
                importance=7,
                last_reviewed="Not reviewed yet",
                notes=notes[:5],
                quiz_average=0,
                source_material_id=material_id,
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
            }
        )
        self.store.save_study_state(state)
        return {
            "created_topics": created,
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

    def coach_reply(self, text: str) -> Dict[str, object]:
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
        for topic in state["topics"]:
            topic.setdefault("source_material_id", "")
        for material in state["materials"]:
            material.setdefault("id", f"material-{uuid.uuid4().hex[:8]}")
            material.setdefault("topic_ids", [])
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
            )
            state["academic_items"] = [item.to_dict()]
            state["active_item_id"] = item.id
        elif not state.get("active_item_id") and state["academic_items"]:
            state["active_item_id"] = state["academic_items"][0]["id"]
        return state

    def _seed_state(self) -> Dict[str, object]:
        exam_date = (datetime.now() + timedelta(days=12)).date().isoformat()
        assignment_date = (datetime.now() + timedelta(days=6)).date().isoformat()
        quiz_date = (datetime.now() + timedelta(days=19)).date().isoformat()
        topics = [
            StudyTopic("topic-virtualization", "Virtualization and Containers", "Cloud Foundations", 62, 78, 8, "2 days ago", ["Contrast hypervisors with containers.", "Know isolation tradeoffs."], 58),
            StudyTopic("topic-scheduling", "Resource Scheduling", "Compute Orchestration", 41, 69, 10, "5 days ago", ["Review placement heuristics.", "Know fairness vs utilization tradeoff."], 44),
            StudyTopic("topic-storage", "Distributed Storage", "Data Services", 55, 61, 8, "3 days ago", ["Compare replication and erasure coding."], 52),
            StudyTopic("topic-security", "Cloud Security Models", "Security", 37, 74, 9, "6 days ago", ["Zero trust assumptions.", "Shared responsibility gaps."], 35),
            StudyTopic("topic-consistency", "Consistency and Replication", "Data Services", 48, 58, 9, "4 days ago", ["Linearizability vs eventual consistency."], 46),
            StudyTopic("topic-pricing", "Cloud Pricing and Autoscaling", "Operations", 71, 73, 6, "1 day ago", ["Cost-aware scaling examples."], 68),
        ]
        academic_items = [
            AcademicItem("item-sc4052-final", "exam", "SC4052 Cloud Computing Final", "SC4052", exam_date),
            AcademicItem("item-sc4052-assignment", "assignment", "SC4052 Assignment 3", "SC4052", assignment_date),
            AcademicItem("item-sc4021-quiz", "quiz", "SC4021 Quiz 2", "SC4021", quiz_date),
        ]
        return {
            "profile": StudyProfile(target_readiness=82, default_study_minutes=90).to_dict(),
            "academic_items": [item.to_dict() for item in academic_items],
            "active_item_id": academic_items[0].id,
            "topics": [topic.to_dict() for topic in topics],
            "materials": [],
            "check_ins": [],
        }

    def _topic_objects(self, state: Dict[str, object]) -> List[StudyTopic]:
        return [StudyTopic(**topic) for topic in state["topics"]]

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

    def _build_metrics(self, profile: StudyProfile, focus_item: Dict[str, object], topics: List[StudyTopic]) -> Dict[str, object]:
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
            "target_readiness": profile.target_readiness,
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
        score = (100 - topic.mastery) * 0.58 + gap * 0.24 + topic.importance * 2.1
        return round(score)

    def _panic_score(self, topic: StudyTopic) -> float:
        return (100 - topic.mastery) * 0.5 + topic.importance * 4.5

    def _focus_reason(self, topic: StudyTopic) -> str:
        gap = topic.confidence - topic.mastery
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
