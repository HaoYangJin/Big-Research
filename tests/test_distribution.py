import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_release import build


class DistributionTests(unittest.TestCase):
    def test_deterministic_packages_are_self_contained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = build(root / "one")
            second = build(root / "two")
            for a, b in zip(first, second):
                self.assertEqual(hashlib.sha256(a.read_bytes()).digest(), hashlib.sha256(b.read_bytes()).digest())
                with zipfile.ZipFile(a) as z:
                    names = z.namelist()
                    self.assertFalse(any(".." in Path(n).parts or n.startswith("/") for n in names))
                    self.assertFalse(any(x in n for n in names for x in [".git/", ".env", "__pycache__", "project.json", "evidence.json"]))
                    z.extractall(root / a.stem)
            skill_cli = root / first[0].stem / "research-mentor/scripts/workflow.py"
            proc = subprocess.run([sys.executable, str(skill_cli), "init", str(root / "new-study"), "--title", "Installed package trial"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["current_phase"], 1)
            with zipfile.ZipFile(first[1]) as z:
                manifest = json.loads(z.read(".codex-plugin/plugin.json"))
                self.assertIn("skills/research-mentor/SKILL.md", z.namelist())
                self.assertIn(manifest["interface"]["logo"].removeprefix("./"), z.namelist())

    def test_installer_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "research-mentor"
            cmd = [sys.executable, str(ROOT / "scripts/install_skill.py"), "--target", str(target)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            marker = target / "local-edits.txt"
            marker.write_text("Keep my edits")
            proc = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(marker.read_text(), "Keep my edits")


if __name__ == "__main__":
    unittest.main()
