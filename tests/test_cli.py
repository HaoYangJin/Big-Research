import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from big_research.cli import main


class CLITests(unittest.TestCase):
    def call(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with patch("sys.argv", ["big-research", *map(str, args)]), redirect_stdout(out), redirect_stderr(err):
            status = main()
        return status, json.loads(out.getvalue() or err.getvalue())

    def test_current_cli_workflow_and_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            self.assertEqual(self.call("start", root, "--title", "Question", "--method", "formal")[0], 0)
            for command in ("status", "check", "assess"):
                self.assertEqual(self.call(command, root)[0], 0)
            for command in ("methods", "doctor", "review-profiles", "review-template"):
                self.assertEqual(self.call(command)[0], 0)
            payload = Path(tmp) / "input.json"
            payload.write_text(json.dumps({"field": "mathematics"}), encoding="utf-8")
            self.assertEqual(self.call("configure", root, "--file", payload)[0], 0)
            payload.write_text(json.dumps({"id": "extra", "title": "Audit", "depends_on": []}), encoding="utf-8")
            self.assertEqual(self.call("task-add", root, "--file", payload)[0], 0)
            payload.write_text(json.dumps({"title": "Updated audit"}), encoding="utf-8")
            self.assertEqual(self.call("task-update", root, "--id", "extra", "--file", payload)[0], 0)
            payload.write_text(json.dumps({"id": "D", "question": "Which?", "status": "pending"}), encoding="utf-8")
            self.assertEqual(self.call("record", root, "--kind", "decision", "--file", payload)[0], 0)
            self.assertEqual(self.call("export", root, "--output", "artifacts/workspace.json")[0], 0)
            self.assertEqual(self.call("start", root, "--title", "Overwrite")[0], 1)
            self.assertEqual(self.call("migrate", root, Path(tmp) / "import")[0], 1)
