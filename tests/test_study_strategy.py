import shutil
import tempfile
import unittest
from pathlib import Path

from chief_of_staff.services.auth_service import AuthService
from chief_of_staff.services.spotify_service import SpotifyService
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

    def test_seeded_auth_account_can_login_and_logout(self):
        auth = AuthService(JsonStore(self.temp_dir))

        result = auth.login("kennethlemuel", "1234567890!")

        self.assertEqual(result["user"]["email"], "kennethlemuel05@gmail.com")
        self.assertTrue(auth.status(result["session_token"])["authenticated"])
        self.assertFalse(auth.logout(result["session_token"])["authenticated"])
        self.assertFalse(auth.status(result["session_token"])["authenticated"])

    def test_auth_can_register_and_record_reset_request(self):
        auth = AuthService(JsonStore(self.temp_dir))

        result = auth.register("new@example.com", "newstudent", "password123!", "password123!")
        reset = auth.forgot_password("new@example.com", "http://studybuddy.localhost:8000")

        self.assertEqual(result["user"]["username"], "newstudent")
        self.assertIn("Reset link", reset["message"])

        token = reset["reset_url"].split("reset=", 1)[1]
        updated = auth.reset_password(token, "newpassword123!", "newpassword123!")
        self.assertEqual(updated["user"]["username"], "newstudent")
        self.assertEqual(auth.login("newstudent", "newpassword123!")["user"]["email"], "new@example.com")

    def test_study_state_can_be_scoped_by_user(self):
        kenneth_service = StudyStrategyService(JsonStore(self.temp_dir).for_study_user("user-kennethlemuel"))
        other_service = StudyStrategyService(JsonStore(self.temp_dir).for_study_user("user-other"), seed_demo=False)

        kenneth_service.import_material(
            "Kenneth Notes",
            "Data Volume\nLarge datasets need careful storage",
        )

        self.assertGreater(len(kenneth_service.get_dashboard()["materials"]), 0)
        self.assertEqual(other_service.get_dashboard()["materials"], [])
        self.assertEqual(other_service.get_dashboard()["academic_items"], [])

    def test_build_plan_returns_ranked_actions(self):
        payload = self.service.build_plan(90)
        self.assertIn("90-minute plan", payload["headline"])
        self.assertGreaterEqual(len(payload["plan"]), 1)
        self.assertIn("minutes", payload["plan"][0])
        self.assertEqual(payload["pace"], "Fast")

    def test_build_plan_filters_to_selected_focus_materials(self):
        result = self.service.import_material(
            "Focused Plan Notes",
            "Indexing\nHash indexes and B trees\nTransactions\nConsistency and isolation",
        )
        dashboard = result["dashboard"]
        focus_id = dashboard["focus_item"]["id"]
        materials = [material for material in dashboard["materials"] if material["academic_item_id"] == focus_id]
        self.assertGreaterEqual(len(materials), 1)

        selected = materials[0]
        payload = self.service.build_plan(125, [selected["id"]], save_request=True)
        self.assertEqual(payload["pace"], "Balanced")
        self.assertEqual(payload["selected_material_ids"], [selected["id"]])
        self.assertTrue(all(item["module"] == selected["title"] for item in payload["plan"]))

        refreshed = self.service.get_dashboard()
        self.assertEqual(refreshed["plan_meta"]["minutes"], 125)
        self.assertEqual(refreshed["plan_meta"]["selected_material_ids"], [selected["id"]])

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
        target_id = next(item["id"] for item in dashboard["academic_items"] if item["id"] != dashboard["focus_item"]["id"])
        result = self.service.set_active_item(target_id)
        self.assertEqual(result["dashboard"]["focus_item"]["id"], target_id)
        self.assertEqual(result["dashboard"]["metrics"]["target_readiness"], 0)

    def test_can_update_current_focus_target_readiness(self):
        result = self.service.update_target_readiness(91)

        self.assertEqual(result["dashboard"]["metrics"]["target_readiness"], 91)
        self.assertEqual(result["dashboard"]["focus_item"]["target_readiness"], 91)

    def test_new_academic_items_default_to_zero_target(self):
        result = self.service.add_academic_item(
            title="SC2100 Quiz",
            subject="SC2100",
            due_date="2026-05-02",
            kind="quiz",
        )

        self.assertEqual(result["item"]["target_readiness"], 0)

    def test_delete_academic_item_removes_it_from_dashboard(self):
        dashboard = self.service.get_dashboard()
        target_id = dashboard["academic_items"][1]["id"]
        target_title = dashboard["academic_items"][1]["title"]

        result = self.service.delete_academic_item(target_id)

        self.assertEqual(result["deleted_item_title"], target_title)
        self.assertFalse(any(item["id"] == target_id for item in result["dashboard"]["academic_items"]))

    def test_delete_active_academic_item_reassigns_focus(self):
        dashboard = self.service.get_dashboard()
        active_id = dashboard["focus_item"]["id"]

        result = self.service.delete_academic_item(active_id)

        self.assertNotEqual(result["dashboard"]["focus_item"].get("id"), active_id)
        self.assertFalse(any(item["id"] == active_id for item in result["dashboard"]["academic_items"]))

    def test_focus_switch_scopes_topics_and_plans(self):
        dashboard = self.service.get_dashboard()
        target_id = next(item["id"] for item in dashboard["academic_items"] if item["id"] == "item-sc4021-quiz")

        result = self.service.set_active_item(target_id)

        self.assertEqual(result["dashboard"]["focus_item"]["id"], target_id)
        self.assertEqual(result["dashboard"]["topics"], [])
        self.assertEqual(result["dashboard"]["plan"], [])
        self.assertEqual(result["dashboard"]["panic_mode"]["must_cover"], [])

    def test_import_material_adds_topics_to_current_focus(self):
        dashboard = self.service.get_dashboard()
        target_id = next(item["id"] for item in dashboard["academic_items"] if item["id"] == "item-sc4021-quiz")
        self.service.set_active_item(target_id)

        result = self.service.import_material(
            "SC4021 Notes",
            "Queues\nLittle law examples\nLatency\nTail latency basics",
        )

        self.assertEqual(result["dashboard"]["focus_item"]["id"], target_id)
        self.assertGreaterEqual(len(result["dashboard"]["topics"]), 2)
        self.assertGreaterEqual(len(result["dashboard"]["plan"]), 1)

    def test_import_material_can_target_non_current_focus(self):
        dashboard = self.service.get_dashboard()
        active_id = dashboard["focus_item"]["id"]
        target_id = next(item["id"] for item in dashboard["academic_items"] if item["id"] == "item-sc4021-quiz")

        result = self.service.import_material(
            "SC4021 Notes",
            "Queues\nLittle law examples\nLatency\nTail latency basics",
            academic_item_id=target_id,
        )

        self.assertEqual(result["dashboard"]["focus_item"]["id"], active_id)
        self.assertEqual(result["dashboard"]["materials"][0]["academic_item_id"], target_id)
        self.assertFalse(any(topic["module"] == "SC4021 Notes" for topic in result["dashboard"]["topics"]))

        switched = self.service.set_active_item(target_id)["dashboard"]
        self.assertTrue(any(topic["module"] == "SC4021 Notes" for topic in switched["topics"]))

    def test_coach_can_make_material_study_list_and_quiz(self):
        self.service.import_material(
            "Lecture 1 Big Data",
            "Volume\nLarge datasets need distributed storage\nVelocity\nStreams arrive quickly",
        )

        study_reply = self.service.coach_reply("study Lecture 1")

        self.assertIn("Outside resources (non-NTU):", study_reply["reply"])
        self.assertIn("Quiz me on number 1", study_reply["reply"])

        quiz_reply = self.service.coach_reply("Give me a short form question on number 1")

        self.assertIn("Short answer | Lecture 1 |", quiz_reply["reply"])
        self.assertIn("Reply with your answer", quiz_reply["reply"])

        before = self.service.get_dashboard()["topics"][0]["mastery"]
        graded = self.service.coach_reply("Large datasets need distributed storage and careful processing.")
        after = graded["dashboard"]["topics"][0]["mastery"]

        self.assertIn("Score:", graded["reply"])
        self.assertGreaterEqual(after, before)

    def test_coach_grades_matching_mcq_letter_as_correct(self):
        question = {
            "type": "MCQ",
            "question": "Which answer is correct?",
            "choices": ["A. First", "B. Second", "C. Third", "D. Fourth"],
            "answer": "D",
        }

        grade = self.service._grade_mcq_answer(question, "D")

        self.assertEqual(grade["score"], 100)

    def test_coach_lists_lectures_for_named_quiz_without_starting_quiz(self):
        dashboard = self.service.get_dashboard()
        target_id = next(item["id"] for item in dashboard["academic_items"] if item["id"] == "item-sc4021-quiz")
        self.service.import_material(
            "Lecture 2 Data Models",
            "Relational Data Model\nTables and primary keys\nGraph Data Model\nNodes and edges",
            academic_item_id=target_id,
        )

        reply = self.service.coach_reply("What lectures do I have to study for SC4021 Quiz 2?")

        self.assertIn("Lectures to study for SC4021 Quiz 2:", reply["reply"])
        self.assertIn("Lecture 2 Data Models", reply["reply"])
        self.assertIn("Topics:", reply["reply"])
        self.assertNotIn("Reply with your answer", reply["reply"])

    def test_coach_recommends_weakest_lecture_with_topics_and_external_resources(self):
        self.service.import_material(
            "Lecture 1 Big Data",
            "Volume\nLarge datasets need distributed storage\nVelocity\nStreams arrive quickly",
        )
        self.service.import_material(
            "Lecture 2 Data Models",
            "Relational Data Model\nTables and primary keys\nGraph Data Model\nNodes and edges",
        )

        reply = self.service.coach_reply("Which lecture needs most focusing on?")

        self.assertIn("focus on Lecture", reply["reply"])
        self.assertIn("Lecture topics:", reply["reply"])
        self.assertIn("Outside resources (non-NTU):", reply["reply"])
        self.assertIn("Quiz options:", reply["reply"])

    def test_coach_prioritizes_low_confidence_untested_lecture(self):
        first = self.service.import_material(
            "Lecture 1 Big Data",
            "Data Volume\nLarge datasets need distributed storage\nData Velocity\nStreams arrive quickly",
        )
        second = self.service.import_material(
            "Lecture 2 Data Models",
            "Relational Data Model\nTables and primary keys\nGraph Data Model\nNodes and edges",
        )
        state = self.service._ensure_state()
        first_ids = set(first["dashboard"]["materials"][0]["topic_ids"])
        second_ids = set(second["dashboard"]["materials"][0]["topic_ids"])
        for topic in state["topics"]:
            if topic["id"] in first_ids:
                topic["mastery"] = 82
                topic["confidence"] = 88
                topic["quiz_average"] = 90
            if topic["id"] in second_ids:
                topic["mastery"] = 64
                topic["confidence"] = 38
                topic["quiz_average"] = 0
        self.service.store.save_study_state(state)

        reply = self.service.coach_reply("Which lecture needs most focusing on?")

        self.assertIn("focus on Lecture 2 Data Models first", reply["reply"])
        self.assertIn("No quiz evidence yet", reply["reply"])

    def test_coach_can_quiz_an_entire_lecture_scope(self):
        self.service.import_material(
            "Lecture 2 Data Models",
            "Relational Data Model\nTables and primary keys\nKey-Value Data Model\nPairs map keys to values\nGraph Data Model\nNodes and edges",
        )
        self.service.coach_reply("Study Lecture 2")

        reply = self.service.coach_reply("Quiz me on the entire Lecture 2")
        state = self.service._ensure_state()
        active_tab = next(tab for tab in state["coach_tabs"] if tab["id"] == state["active_coach_tab_id"])
        session = active_tab["session"]

        self.assertEqual(session["quiz_scope"]["scope"], "lecture")
        self.assertGreaterEqual(len(session["quiz_scope"]["topic_ids"]), 2)
        self.assertIn(" | Lecture 2 | ", reply["reply"])

    def test_quiz_missing_lecture_stays_on_current_focus(self):
        self.service.import_material(
            "Lecture 1 Big Data",
            "Volume\nLarge datasets need distributed storage\nVelocity\nStreams arrive quickly",
        )

        reply = self.service.coach_reply("Quiz me on Lecture 9")
        state = self.service._ensure_state()
        active_tab = next(tab for tab in state["coach_tabs"] if tab["id"] == state["active_coach_tab_id"])

        self.assertIn("I do not have that lecture material for SC4052 Cloud Computing Final yet.", reply["reply"])
        self.assertNotIn("SC4021 Quiz 2", reply["reply"])
        self.assertEqual(active_tab["session"], {})

    def test_coach_tabs_have_separate_transcripts_and_shared_question_memory(self):
        self.service.import_material(
            "Lecture 1 Big Data",
            "Volume\nLarge datasets need distributed storage\nVelocity\nStreams arrive quickly",
        )
        first_tab_id = self.service.get_dashboard()["coach"]["active_tab_id"]

        self.service.coach_reply("Give me an MCQ on Lecture 1", first_tab_id)
        first_state = self.service.get_coach_tabs()
        first_tab = next(tab for tab in first_state["tabs"] if tab["id"] == first_tab_id)
        self.assertTrue(first_tab["has_open_quiz"])
        self.assertEqual(first_state["memory_count"], 1)

        second_state = self.service.create_coach_tab("Clean chat")
        second_tab_id = second_state["active_tab_id"]
        second_tab = next(tab for tab in second_state["tabs"] if tab["id"] == second_tab_id)
        self.assertEqual(second_tab["messages"], [])
        self.assertEqual(second_state["memory_count"], 1)

        self.service.coach_reply("What can you do?", second_tab_id)
        state = self.service.get_coach_tabs()
        first_tab = next(tab for tab in state["tabs"] if tab["id"] == first_tab_id)
        second_tab = next(tab for tab in state["tabs"] if tab["id"] == second_tab_id)
        self.assertTrue(first_tab["has_open_quiz"])
        self.assertFalse(second_tab["has_open_quiz"])
        self.assertEqual([message["role"] for message in second_tab["messages"]], ["user", "assistant"])

    def test_coach_memory_survives_service_restart(self):
        self.service.import_material(
            "Lecture 1 Big Data",
            "Volume\nLarge datasets need distributed storage\nVelocity\nStreams arrive quickly",
        )
        tab_id = self.service.get_dashboard()["coach"]["active_tab_id"]
        self.service.coach_reply("Give me an MCQ on Lecture 1", tab_id)

        restarted = StudyStrategyService(JsonStore(self.temp_dir))
        state = restarted.get_coach_tabs()
        tab = next(tab for tab in state["tabs"] if tab["id"] == tab_id)

        self.assertEqual(state["memory_count"], 1)
        self.assertEqual([message["role"] for message in tab["messages"]], ["user", "assistant"])
        self.assertTrue(tab["has_open_quiz"])

    def test_coach_tabs_can_be_renamed_and_closed_without_clearing_memory(self):
        self.service.import_material(
            "Lecture 1 Big Data",
            "Volume\nLarge datasets need distributed storage\nVelocity\nStreams arrive quickly",
        )
        tab_id = self.service.get_dashboard()["coach"]["active_tab_id"]
        self.service.coach_reply("Give me an MCQ on Lecture 1", tab_id)

        renamed = self.service.rename_coach_tab(tab_id, "Lecture drill")
        self.assertEqual(next(tab["title"] for tab in renamed["tabs"] if tab["id"] == tab_id), "Lecture drill")

        closed = self.service.delete_coach_tab(tab_id)

        self.assertEqual(closed["memory_count"], 1)
        self.assertNotIn(tab_id, [tab["id"] for tab in closed["tabs"]])
        self.assertGreaterEqual(len(closed["tabs"]), 1)

    def test_coach_honors_short_answer_question_request(self):
        self.service.import_material(
            "Lecture 1 Big Data",
            "Volume\nLarge datasets need distributed storage\nVelocity\nStreams arrive quickly",
        )
        self.service.coach_reply("Study Lecture 1")
        self.service.coach_reply("Quiz me on number 1")
        self.service.coach_reply("Large datasets need distributed storage.")

        reply = self.service.coach_reply("Another question, give me a short form question rather than MCQ")

        self.assertIn("Short answer", reply["reply"])
        self.assertNotIn("A.", reply["reply"])

    def test_short_answer_grading_does_not_penalize_long_correct_answer(self):
        question = {
            "type": "Short answer",
            "question": "Explain Data Velocity using this material detail.",
            "answer": "Velocity refers to the speed at which data is generated and processed, such as taxi location updates every 5 seconds.",
            "rubric": ["Data velocity is about speed of data generation and processing.", "Taxi location updates are a valid example."],
        }
        student_answer = (
            "Data velocity is about how fast data is being created, collected, and processed. "
            "Using the taxi example, a taxi sends its location every 5 seconds, so new data keeps arriving quickly "
            "and the system needs to process it fast enough to react in real time."
        )

        grade = self.service._fallback_grade(question, student_answer)

        self.assertGreaterEqual(grade["score"], 90)

    def test_short_answer_grading_ignores_concision_penalty_when_correct(self):
        low_style_grade = {
            "score": 85,
            "feedback": "Correct, but the answer could have been more concise.",
        }
        semantic_grade = {
            "score": 100,
            "feedback": "Local semantic grading found the key idea.",
        }

        grade = self.service._reconcile_short_answer_grade(low_style_grade, semantic_grade)

        self.assertEqual(grade["score"], 100)
        self.assertIn("did not penalize answer length", grade["feedback"])

    def test_mcq_has_smaller_readiness_impact_than_written_answer(self):
        base_state = self.service._ensure_state()
        topic_id = base_state["topics"][0]["id"]

        mcq_state = self.service._ensure_state()
        for topic in mcq_state["topics"]:
            if topic["id"] == topic_id:
                topic["mastery"] = 40
                topic["confidence"] = 40
        self.service._apply_quiz_score(mcq_state, topic_id, 100, "MCQ")
        mcq_mastery = next(topic["mastery"] for topic in mcq_state["topics"] if topic["id"] == topic_id)

        written_state = self.service._ensure_state()
        for topic in written_state["topics"]:
            if topic["id"] == topic_id:
                topic["mastery"] = 40
                topic["confidence"] = 40
        self.service._apply_quiz_score(written_state, topic_id, 100, "Short answer")
        written_mastery = next(topic["mastery"] for topic in written_state["topics"] if topic["id"] == topic_id)

        wrong_state = self.service._ensure_state()
        for topic in wrong_state["topics"]:
            if topic["id"] == topic_id:
                topic["mastery"] = 40
                topic["confidence"] = 40
        self.service._apply_quiz_score(wrong_state, topic_id, 0, "Short answer")
        wrong_mastery = next(topic["mastery"] for topic in wrong_state["topics"] if topic["id"] == topic_id)

        self.assertEqual(mcq_mastery, 43)
        self.assertEqual(written_mastery, 45)
        self.assertEqual(wrong_mastery, 38)
        self.assertLess(mcq_mastery, written_mastery)

    def test_spotify_login_tracks_pending_auth_without_marking_connected(self):
        (self.temp_dir / "spotify_config.json").write_text(
            '{"client_id":"client","client_secret":"secret","redirect_uri":"http://127.0.0.1:8000/spotify/callback"}'
        )
        spotify = SpotifyService(self.temp_dir)

        first_url = spotify.login_url()
        second_url = spotify.login_url()
        status = spotify.status()

        self.assertIn("https://accounts.spotify.com/authorize?", first_url)
        self.assertIn("https://accounts.spotify.com/authorize?", second_url)
        self.assertTrue(status["configured"])
        self.assertTrue(status["auth_pending"])
        self.assertFalse(status["connected"])

    def test_spotify_service_bypasses_environment_proxy_settings(self):
        spotify = SpotifyService(self.temp_dir)

        proxy_handlers = [handler for handler in spotify.http.handlers if hasattr(handler, "proxies")]
        self.assertEqual(proxy_handlers, [])


if __name__ == "__main__":
    unittest.main()
