import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from big_research.core import WorkflowError
from big_research.migration import migrate


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.source = self.base / "old"
        self.source.mkdir()
        (self.source / "artifacts").mkdir()
        proof = self.source / "artifacts/proof.md"
        proof.write_text("A proof with explicitly stated assumptions.", encoding="utf-8")
        self.state = {
            "schema_version": 1,
            "workflow_version": "1.1.0",
            "title": "Original",
            "stages": {str(i): {"status": "pending"} for i in range(1, 10)},
        }
        self.ledger = {
            "sources": [
                {
                    "id": "S1",
                    "title": "Proof",
                    "path": "artifacts/proof.md",
                    "sha256": hashlib.sha256(proof.read_bytes()).hexdigest(),
                    "status": "verified",
                    "accessed": "2026-10-16",
                    "locator": "entire proof",
                }
            ],
            "experiments": [],
            "claims": [{"id": "C1", "text": "Claim", "status": "supported", "evidence": ["S1"]}],
        }
        self.save()

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        (self.source / "project.json").write_text(json.dumps(self.state), encoding="utf-8")
        (self.source / "evidence.json").write_text(json.dumps(self.ledger), encoding="utf-8")

    def test_preserves_source_and_imports_data_without_completion(self):
        before = {p.relative_to(self.source): p.read_bytes() for p in self.source.rglob("*") if p.is_file()}
        project = migrate(self.source, self.base / "current")
        self.assertEqual(
            before, {p.relative_to(self.source): p.read_bytes() for p in self.source.rglob("*") if p.is_file()}
        )
        self.assertEqual(project.read()["claims"]["C1"]["status"], "needs_review")
        self.assertTrue(all(t["status"] == "planned" for t in project.read()["tasks"].values()))
        self.assertTrue(project.validate()["structural_valid"])

    def test_corrupt_unknown_and_existing_destinations_fail_safely(self):
        for version in ("unknown", "1.1.0"):
            self.state["workflow_version"] = version
            self.ledger["sources"][0]["sha256"] = "bad"
            self.save()
            with self.assertRaises(WorkflowError):
                migrate(self.source, self.base / "target")
            self.assertFalse((self.base / "target").exists())
        with self.assertRaises(WorkflowError):
            migrate(self.source, self.source)

    def test_symlink_import_stops_before_creating_destination(self):
        outside = self.base / "outside.md"
        outside.write_text("Not part of the selected research project", encoding="utf-8")
        try:
            (self.source / "linked.md").symlink_to(outside)
        except OSError:
            self.skipTest("Creating symlinks requires permission on this system")
        with self.assertRaisesRegex(WorkflowError, "symlinks"):
            migrate(self.source, self.base / "target")
        self.assertFalse((self.base / "target").exists())

    def test_unreadable_material_aborts_instead_of_silently_omitting_it(self):
        def broken_walk(root, *, followlinks, onerror):
            onerror(PermissionError("A research material directory cannot be read"))
            return iter(())

        with patch("big_research.migration.os.walk", side_effect=broken_walk):
            with self.assertRaises(PermissionError):
                migrate(self.source, self.base / "target")
        self.assertFalse((self.base / "target").exists())
