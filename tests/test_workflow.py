import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills/research-mentor/scripts/workflow.py"
spec = importlib.util.spec_from_file_location("workflow", CLI)
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "project"
        self.run_cli("init", self.root, "--title", "A bounded research question")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args, ok=True):
        proc = subprocess.run([sys.executable, str(CLI), *map(str, args)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0 if ok else 1, proc.stdout + proc.stderr)
        return json.loads(proc.stdout if ok else proc.stderr)

    def write(self, path, obj):
        (self.root / path).write_text(json.dumps(obj), encoding="utf-8")

    def artifact(self, n, **extra):
        obj = {"phase": n, "summary": "An assessed stage", "criteria": {k: "Concrete evidence and bounded interpretation" for k in wf.PHASES[n][1]}, "evidence": [], "outputs": []}
        if n == 7:
            obj["blocking_concerns"] = ["R1"]
        if n == 8:
            obj["resolved_concerns"] = []
        if n == 9:
            obj["decision"] = "not_ready"
        obj.update(extra)
        path = f"artifacts/{n:02}.json"
        self.write(path, obj)
        return path

    def checkpoint(self, n, **extra):
        path = self.artifact(n, **extra)
        return self.run_cli("checkpoint", self.root, "--phase", n, "--artifact", path)

    def empirical_evidence(self, status="executed"):
        path = self.root / "artifacts/result.txt"
        path.write_text("Measured result: 1.2\n", encoding="utf-8")
        ledger = {"sources": [], "experiments": [{"id": "E1", "status": status, "command": "python experiment.py", "environment": "Python stdlib", "seed": 7, "artifacts": [{"path": "artifacts/result.txt", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}]}], "claims": [{"id": "C1", "text": "This fixture has a measured result", "status": "supported" if status == "executed" else "hypothesis", "evidence": ["E1"]}]}
        self.write("evidence.json", ledger)

    def test_resume_and_reopen_invalidates_downstream(self):
        self.checkpoint(1)
        self.checkpoint(2)
        self.assertEqual(self.run_cli("status", self.root)["current_phase"], 3)
        self.run_cli("reopen", self.root, "--phase", 1, "--reason", "Change question")
        state = self.run_cli("status", self.root)
        self.assertEqual(state["current_phase"], 1)
        self.assertEqual(state["stages"]["2"]["status"], "pending")

    def test_init_never_overwrites(self):
        before = (self.root / "project.json").read_bytes()
        self.run_cli("init", self.root, "--title", "Overwrite attempt", ok=False)
        self.assertEqual(before, (self.root / "project.json").read_bytes())

    def test_block_stays_and_skip_requires_reason(self):
        self.run_cli("checkpoint", self.root, "--phase", 1, "--status", "skipped", ok=False)
        self.run_cli("checkpoint", self.root, "--phase", 1, "--status", "blocked", "--reason", "Missing input")
        self.assertEqual(self.run_cli("status", self.root)["current_phase"], 1)

    def test_out_of_order_is_rejected(self):
        self.run_cli("checkpoint", self.root, "--phase", 2, "--artifact", self.artifact(2), ok=False)

    def test_placeholder_is_not_completion(self):
        path = self.artifact(1)
        obj = json.loads((self.root / path).read_text())
        obj["criteria"]["question"] = "TODO replace"
        self.write(path, obj)
        self.run_cli("checkpoint", self.root, "--phase", 1, "--artifact", path, ok=False)

    def test_stage_and_output_mutations_are_detected(self):
        self.empirical_evidence()
        self.checkpoint(1, outputs=["artifacts/result.txt"])
        (self.root / "artifacts/result.txt").write_text("Changed result", encoding="utf-8")
        self.run_cli("validate", self.root, ok=False)

    def test_checkpoint_mutation_can_be_recovered(self):
        self.checkpoint(1)
        (self.root / "artifacts/01.json").write_text("{}")
        self.run_cli("validate", self.root, ok=False)
        self.run_cli("reopen", self.root, "--phase", 1, "--reason", "Revise artifact")
        self.checkpoint(1)

    def test_evidence_changes_invalidate_linked_checkpoints(self):
        self.empirical_evidence()
        self.checkpoint(1, evidence=["C1"])
        ledger = json.loads((self.root / "evidence.json").read_text())
        ledger["experiments"][0]["seed"] = 99
        self.write("evidence.json", ledger)
        self.assertIn("evidence changed", self.run_cli("validate", self.root, ok=False)["error"])

    def test_local_proof_can_support_theoretical_draft(self):
        self.run_cli("reopen", self.root, "--phase", 1, "--reason", "Change to proof task")
        state = json.loads((self.root / "project.json").read_text())
        state["kind"] = "theoretical"
        self.write("project.json", state)
        proof = self.root / "artifacts/proof.md"
        proof.write_text("An inspected derivation with stated assumptions")
        self.write("evidence.json", {"sources": [{"id": "P1", "title": "Local proof", "path": "artifacts/proof.md", "sha256": hashlib.sha256(proof.read_bytes()).hexdigest(), "status": "verified", "accessed": "2026-10-16", "locator": "Full derivation"}], "experiments": [], "claims": [{"id": "C1", "text": "Bounded theorem", "status": "supported", "evidence": ["P1"]}]})
        for n in range(1, 6):
            self.checkpoint(n, outputs=["artifacts/proof.md"])
        self.checkpoint(6, evidence=["C1"], outputs=["artifacts/proof.md"])

    def test_planned_experiment_cannot_be_results(self):
        for n in range(1, 5):
            self.checkpoint(n)
        self.empirical_evidence("planned")
        self.run_cli("checkpoint", self.root, "--phase", 5, "--artifact", self.artifact(5, evidence=["E1"]), ok=False)

    def test_supported_claim_needs_verified_evidence(self):
        ledger = {"sources": [{"id": "S1", "title": "Unread source", "url": "https://example.org/paper", "status": "unverified"}], "experiments": [], "claims": [{"id": "C1", "text": "Unverified assertion", "status": "supported", "evidence": ["S1"]}]}
        self.write("evidence.json", ledger)
        self.run_cli("validate", self.root, ok=False)

    def test_full_loop_can_conclude_not_ready(self):
        self.empirical_evidence()
        for n in range(1, 10):
            extra = {}
            if n == 5:
                extra["evidence"] = ["E1"]
            if n == 6:
                extra.update(evidence=["C1"], outputs=["artifacts/result.txt"])
            self.checkpoint(n, **extra)
        state = self.run_cli("validate", self.root)
        self.assertTrue(state["workflow_complete"])
        self.assertEqual(state["submission_decision"], "not_ready")
        self.assertEqual(state["validation"], "structural_only")

    def test_resolved_concerns_allow_ready(self):
        self.empirical_evidence()
        for n in range(1, 9):
            extra = {"evidence": ["E1"]} if n == 5 else {"evidence": ["C1"], "outputs": ["artifacts/result.txt"]} if n == 6 else {"resolved_concerns": ["R1"]} if n == 8 else {}
            self.checkpoint(n, **extra)
        self.checkpoint(9, decision="ready")
        self.assertEqual(self.run_cli("status", self.root)["submission_decision"], "ready")

    def test_midway_entry_cannot_claim_full_readiness(self):
        self.root = Path(self.tmp.name) / "midway"
        self.run_cli("init", self.root, "--title", "Only submission assessment", "--phase", 9)
        self.run_cli("checkpoint", self.root, "--phase", 9, "--artifact", self.artifact(9, decision="ready"), ok=False)
        self.checkpoint(9)

    def test_unresolved_review_blocks_ready(self):
        self.empirical_evidence()
        for n in range(1, 9):
            self.checkpoint(n, **({"evidence": ["E1"]} if n == 5 else {"evidence": ["C1"], "outputs": ["artifacts/result.txt"]} if n == 6 else {}))
        self.run_cli("checkpoint", self.root, "--phase", 9, "--artifact", self.artifact(9, decision="ready"), ok=False)

    def test_path_traversal_and_escaping_symlink_rejected(self):
        self.run_cli("checkpoint", self.root, "--phase", 1, "--artifact", "../outside.json", ok=False)
        outside = Path(self.tmp.name) / "outside.json"
        outside.write_text("{}")
        link = self.root / "artifacts/link.json"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            return  # Windows may not grant symlink privileges.
        self.run_cli("checkpoint", self.root, "--phase", 1, "--artifact", "artifacts/link.json", ok=False)

    def test_malformed_state_and_duplicate_ids_fail_cleanly(self):
        self.write("evidence.json", {"sources": [], "experiments": [], "claims": [{"id": "C1"}, {"id": "C1"}]})
        self.run_cli("validate", self.root, ok=False)
        (self.root / "project.json").write_text('{"schema_version":1,"schema_version":2}')
        self.assertIn("Duplicate", self.run_cli("status", self.root, ok=False)["error"])

    def test_lock_prevents_concurrent_write_and_recovers_after_crash(self):
        code = "import importlib.util,os,sys; s=importlib.util.spec_from_file_location('w',sys.argv[1]); w=importlib.util.module_from_spec(s); s.loader.exec_module(w); ctx=w.locked(w.Path(sys.argv[2])); ctx.__enter__(); print('locked',flush=True); sys.stdin.readline(); os._exit(17)"
        child = subprocess.Popen([sys.executable, "-c", code, str(CLI), str(self.root)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), "locked")
            error = self.run_cli("mode", self.root, "--select", "reviewer", ok=False)
            self.assertIn("locked", error["error"])
            child.communicate("exit\n", timeout=10)
            self.assertEqual(child.returncode, 17)
            self.assertTrue((self.root / ".workflow.lock").exists())
            self.run_cli("mode", self.root, "--select", "reviewer")
            self.assertEqual(self.run_cli("status", self.root)["mode"], "reviewer")
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate()

    def test_mode_memory_and_auto_phase_progress(self):
        self.assertEqual(self.run_cli("status", self.root)["mode_policy"], "auto")
        self.run_cli("mode", self.root, "--select", "reviewer", "--reason", "User choice")
        self.checkpoint(1)
        self.assertEqual(self.run_cli("status", self.root)["mode"], "reviewer")
        selected = self.run_cli("mode", self.root, "--select", "auto", "--task", "revise")
        self.assertEqual(selected["mode"], "mixed")
        self.checkpoint(2)
        self.assertEqual(self.run_cli("status", self.root)["mode"], "mentor")
        for n in [3, 4]:
            self.checkpoint(n)
        self.assertEqual(self.run_cli("status", self.root)["mode"], "mixed")
        state = json.loads((self.root / "project.json").read_text())
        self.assertTrue(any(e.get("reason") == "User choice" for e in state["history"]))

    def test_explicit_migration_preserves_checkpoints_and_backup(self):
        self.checkpoint(1)
        state = json.loads((self.root / "project.json").read_text())
        state["workflow_version"] = "1.0.0"
        state.pop("mode_policy")
        self.write("project.json", state)
        self.run_cli("status", self.root, ok=False)
        self.run_cli("migrate", self.root)
        backup = json.loads((self.root / "project.v1.0.0.backup.json").read_text())
        self.assertEqual(backup, state)
        current = self.run_cli("status", self.root)
        self.assertEqual(current["current_phase"], 2)
        self.assertEqual(current["mode_policy"], "manual")
        before = (self.root / "project.json").read_bytes()
        self.run_cli("migrate", self.root)
        self.assertEqual(before, (self.root / "project.json").read_bytes())

    def test_migration_refuses_corrupt_or_unknown_projects(self):
        self.checkpoint(1)
        state = json.loads((self.root / "project.json").read_text())
        state["workflow_version"] = "1.0.0"
        self.write("project.json", state)
        (self.root / "artifacts/01.json").write_text("{}")
        self.run_cli("migrate", self.root, ok=False)
        self.assertFalse((self.root / "project.v1.0.0.backup.json").exists())
        state["workflow_version"] = "0.9.0"
        self.write("project.json", state)
        self.run_cli("migrate", self.root, ok=False)



if __name__ == "__main__":
    unittest.main()

