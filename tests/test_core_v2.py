"""Behavioral acceptance tests for the current research workspace."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from big_research.core import Project, WorkflowError, methods


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "study"
        self.project = Project.create(
            self.root, "A question", field="history", paradigm="interpretive", method_ids=["interpretive"]
        )

    def tearDown(self):
        self.temp.cleanup()

    def artifact(self, name="note.md", text="A bounded interpretation with a rival reading."):
        path = self.root / "artifacts" / name
        path.write_text(text, encoding="utf-8")
        return f"artifacts/{name}"

    def source(self):
        self.project.record_evidence(
            {
                "id": "S1",
                "kind": "source",
                "title": "A local source",
                "path": self.artifact(),
                "status": "verified",
                "accessed": "2026-10-16",
                "locator": "paragraph 1",
            }
        )

    def test_cross_disciplinary_metadata_and_method_composition(self):
        for field, paradigm, module in [
            ("physics", "experimental", "quantitative"),
            ("engineering", "design science", "quantitative"),
            ("computer science", "formal", "formal"),
            ("medicine", "evidence synthesis", "synthesis"),
            ("sociology", "qualitative", "qualitative"),
            ("history", "hermeneutics", "interpretive"),
        ]:
            p = Project.create(
                Path(self.temp.name) / field.replace(" ", "-"),
                "Question",
                field=field,
                paradigm=paradigm,
                method_ids=[module],
            )
            self.assertEqual(p.read()["paradigm"], paradigm)
        self.assertNotIn("statistical_power", methods()["interpretive"]["checks"])
        self.assertIn("mixed", methods())

    def test_no_overwrite_and_unknown_method(self):
        with self.assertRaises(WorkflowError):
            Project.create(self.root, "Overwrite")
        with self.assertRaises(WorkflowError):
            self.project.configure(method_ids=["invented"])

    def test_task_graph_allows_parallel_and_detects_cycles(self):
        self.project.update_task("frame", {"depends_on": []})
        self.project.add_task({"id": "archive", "title": "Read archive", "depends_on": []})
        self.assertIn("archive", [t["id"] for t in self.project.status()["next_tasks"]])
        with self.assertRaises(WorkflowError):
            self.project.update_task("frame", {"depends_on": ["communicate"]})

    def test_completion_needs_outputs_and_dependencies(self):
        with self.assertRaises(WorkflowError):
            self.project.update_task("frame", {"status": "complete"})
        with self.assertRaises(WorkflowError):
            self.project.update_task(
                "design", {"status": "complete", "outputs": [self.artifact()], "summary": "Design"}
            )

    def test_invalid_updates_preserve_a_readable_project(self):
        before = (self.root / "project.json").read_bytes()
        for outputs in ([None], [""]):
            with self.assertRaises(WorkflowError):
                self.project.update_task("frame", {"outputs": outputs})
            self.assertEqual((self.root / "project.json").read_bytes(), before)
            self.assertEqual(self.project.read()["revision"], 0)
        self.project.update_task("frame", {"title": "Still editable"})
        self.assertEqual(self.project.read()["revision"], 1)

    def test_changes_invalidate_only_dependent_tasks(self):
        self.source()
        path = self.artifact("scope.md")
        self.project.update_task(
            "frame", {"status": "complete", "summary": "Question scoped", "outputs": [path], "evidence": ["S1"]}
        )
        self.project.update_task("map", {"status": "complete", "summary": "Sources mapped", "outputs": [path]})
        self.project.add_task({"id": "independent", "title": "Independent", "depends_on": []})
        self.project.update_task("frame", {"title": "A revised question"})
        state = self.project.read()
        self.assertEqual(state["tasks"]["map"]["status"], "stale")
        self.assertEqual(state["tasks"]["independent"]["status"], "planned")
        self.assertTrue(state["history"][-1]["before"])

    def test_evidence_integrity_and_stale_claims(self):
        self.source()
        self.project.record_claim(
            {"id": "C1", "text": "An interpretation of this source", "status": "supported", "supports": ["S1"]}
        )
        self.project.update_task(
            "frame", {"status": "complete", "summary": "Question", "outputs": ["artifacts/note.md"], "evidence": ["C1"]}
        )
        (self.root / "artifacts/note.md").write_text("Changed", encoding="utf-8")
        self.assertFalse(self.project.validate()["structural_valid"])
        self.project.record_evidence(
            {"id": "S1", "kind": "source", "title": "Updated", "path": "artifacts/note.md", "status": "unverified"}
        )
        self.assertEqual(self.project.read()["claims"]["C1"]["status"], "needs_review")

    def test_plans_and_failed_runs_cannot_support_findings(self):
        for status in ("planned", "failed"):
            self.project.record_evidence({"id": status, "kind": "run", "title": "A run", "status": status})
            with self.assertRaises(WorkflowError):
                self.project.record_claim({"id": "C1", "text": "A result", "status": "supported", "supports": [status]})
        with self.assertRaises(WorkflowError):
            self.project.record_evidence({"id": "run", "kind": "run", "title": "Run", "status": "executed"})

    def test_file_confinement_and_revision_conflict(self):
        for path in ("../outside", "C:/Windows/win.ini", "/etc/passwd"):
            with self.assertRaises(WorkflowError):
                self.project.record_evidence(
                    {"id": "S", "kind": "source", "title": "Bad", "path": path, "status": "unverified"}
                )
        revision = self.project.read()["revision"]
        self.project.configure(field="philosophy")
        with self.assertRaises(WorkflowError):
            self.project.update_task("frame", {"title": "Stale write"}, expected_revision=revision)

    def test_concurrent_writer_fails_and_process_exit_releases_lock(self):
        code = (
            "import os,sys; from pathlib import Path; from big_research.core import locked; "
            "lock=locked(Path(sys.argv[1])); lock.__enter__(); print('locked',flush=True); "
            "sys.stdin.readline(); os._exit(0)"
        )
        child = subprocess.Popen(
            [sys.executable, "-c", code, str(self.root)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )
        try:
            self.assertEqual(child.stdout.readline().strip(), "locked")
            with self.assertRaisesRegex(WorkflowError, "locked"):
                self.project.configure(title="Concurrent change")
        finally:
            # Exit the actual interpreter abruptly: on Windows sys.executable may be a venv launcher.
            child.communicate(input="exit\n", timeout=10)
        self.project.configure(title="Recovered after process exit")
        self.assertEqual(self.project.read()["revision"], 1)

    def test_decisions_concerns_and_budget_are_explicit(self):
        self.project.record_decision(
            {"id": "D1", "question": "Which interpretation?", "options": ["A", "B"], "status": "pending"}
        )
        self.assertEqual(len(self.project.status()["pending_decisions"]), 1)
        with self.assertRaises(WorkflowError):
            self.project.record_decision({"id": "D1", "question": "Which?", "status": "confirmed", "choice": "A"})
        self.project.record_decision(
            {
                "id": "D1",
                "question": "Which?",
                "status": "confirmed",
                "choice": "A",
                "researcher_statement": "I choose A because of its evidence.",
            }
        )
        self.project.record_concern({"id": "R1", "text": "Missing context", "status": "open"})
        self.project.configure(budget={"limit": 5, "spent": 5, "unit": "hours"})
        result = self.project.assess()
        self.assertTrue(result["budget_exhausted"])
        self.assertFalse(result["researcher_confirmed"])
        self.assertFalse(result["scientific_validity_certified"])

    def test_export_cannot_execute_untrusted_markup(self):
        self.project.configure(field="</script><script>alert(1)</script>")
        target = self.project.export("artifacts/workspace.html")
        html = Path(target).read_text(encoding="utf-8")
        self.assertNotIn("</script><script>alert", html)
        self.assertIn("Big-Research", html)

    def test_review_and_confirmation_follow_the_reviewed_material(self):
        self.project.record_method_review(
            {
                "id": "interpretive",
                "checks": {
                    key: {"verdict": "adequate", "reason": "Inspected supplied material"}
                    for key in methods()["interpretive"]["checks"]
                },
            }
        )
        self.project.record_decision(
            {
                "id": "research-conclusion",
                "question": "Adopt the conclusion?",
                "status": "confirmed",
                "choice": "Yes",
                "researcher_statement": "I adopt this bounded conclusion.",
            }
        )
        self.assertTrue(self.project.assess()["method_checks_complete"])
        self.assertTrue(self.project.assess()["researcher_confirmed"])
        self.project.update_task("frame", {"title": "A substantially changed question"})
        self.assertFalse(self.project.assess()["method_checks_complete"])
        self.assertFalse(self.project.assess()["researcher_confirmed"])

    def test_corrupted_saved_semantics_and_malformed_shapes_fail_cleanly(self):
        original = self.project.read()
        corruptions = [
            {**original, "tasks": {**original["tasks"], "frame": None}},
            {
                **original,
                "claims": {
                    "C1": {
                        "id": "C1",
                        "text": "Unsupported",
                        "status": "supported",
                        "supports": ["missing"],
                        "contradicts": [],
                    }
                },
            },
            {**original, "evidence": {"E1": {"id": "E1", "title": "Run", "kind": "run", "status": "executed"}}},
        ]
        for state in corruptions:
            (self.root / "project.json").write_text(json.dumps(state), encoding="utf-8")
            with self.assertRaises(WorkflowError):
                self.project.validate()
        (self.root / "project.json").write_text(json.dumps(original), encoding="utf-8")
        with self.assertRaises(WorkflowError):
            self.project.record_evidence(
                {
                    "id": "E1",
                    "title": "Run",
                    "kind": "run",
                    "status": "executed",
                    "command": "test",
                    "environment": "test",
                    "artifacts": [None],
                }
            )


if __name__ == "__main__":
    unittest.main()
