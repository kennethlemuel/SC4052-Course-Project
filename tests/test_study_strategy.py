import shutil
import tempfile
import unittest
from pathlib import Path

from chief_of_staff.services.study_strategy_service import StudyStrategyService
from chief_of_staff.storage import JsonStore


class StudyStrategyServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = StudyStrategyService(JsonStore(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_dashboard_exposes_readiness_and_topics(self):
        dashboard = self.service.get_dashboard()
        self.assertIn("metrics", dashboard)
        self.assertGreater(len(dashboard["weakness_map"]), 0)
        self.assertGreater(dashboard["metrics"]["readiness_score"], 0)
        self.assertIn("focus_item", dashboard)
        self.assertGreater(len(dashboard["academic_items"]), 0)

    def test_build_plan_returns_ranked_actions(self):
        payload = self.service.build_plan(90)
        self.assertIn("90-minute plan", payload["headline"])
        self.assertGreaterEqual(len(payload["plan"]), 1)
        self.assertIn("minutes", payload["plan"][0])

    def test_panic_mode_returns_triage(self):
        payload = self.service.build_panic_mode("tonight")
        self.assertIn("must_cover", payload)
        self.assertGreaterEqual(len(payload["must_cover"]), 1)
        self.assertIn("skip", payload)

    def test_material_import_creates_targets(self):
        result = self.service.import_material(
            "Week 9 Notes",
            "Virtualization\nHypervisor tradeoffs\nContainers\nNamespaces and cgroups",
        )
        self.assertGreaterEqual(len(result["created_topics"]), 2)
        self.assertEqual(len(result["dashboard"]["materials"]), 1)

    def test_delete_material_removes_derived_topics_and_material_entry(self):
        result = self.service.import_material(
            "Week 9 Notes",
            "Virtualization\nHypervisor tradeoffs\nContainers\nNamespaces and cgroups",
        )
        dashboard = result["dashboard"]
        material_id = dashboard["materials"][0]["id"]
        imported_topic_ids = {topic_id for topic_id in dashboard["materials"][0]["topic_ids"]}

        deleted = self.service.delete_material(material_id)

        self.assertEqual(deleted["deleted_material_title"], "Week 9 Notes")
        self.assertGreaterEqual(deleted["removed_topics"], 1)
        self.assertEqual(deleted["dashboard"]["materials"], [])
        remaining_topic_ids = {topic["id"] for topic in deleted["dashboard"]["topics"]}
        self.assertTrue(imported_topic_ids.isdisjoint(remaining_topic_ids))

    def test_check_in_updates_topic(self):
        dashboard = self.service.get_dashboard()
        topic_id = dashboard["topics"][0]["id"]
        result = self.service.log_check_in(topic_id, confidence=85, quiz_score=52, minutes_studied=45)
        self.assertIn("insight", result)
        self.assertEqual(result["topic"]["id"], topic_id)

    def test_can_add_academic_item(self):
        result = self.service.add_academic_item(
            title="SC2100 Midterm",
            subject="SC2100",
            due_date="2026-05-01",
            kind="exam",
        )
        self.assertEqual(result["item"]["title"], "SC2100 Midterm")
        self.assertIn("dashboard", result)
        self.assertTrue(any(item["title"] == "SC2100 Midterm" for item in result["dashboard"]["academic_items"]))

    def test_can_switch_focus_item(self):
        dashboard = self.service.get_dashboard()
        target_id = dashboard["academic_items"][1]["id"]
        result = self.service.set_active_item(target_id)
        self.assertEqual(result["dashboard"]["focus_item"]["id"], target_id)


if __name__ == "__main__":
    unittest.main()
