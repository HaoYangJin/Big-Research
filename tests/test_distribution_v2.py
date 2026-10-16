import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_release import build  # noqa: E402


class DistributionTests(unittest.TestCase):
    def test_ignored_research_material_never_enters_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = build(base / "initial")
            root = base / "candidate"
            with zipfile.ZipFile(archive) as package:
                package.extractall(root)
            shutil.copyfile(ROOT / "package-lock.json", root / "package-lock.json")
            (root / ".gitignore").write_text("results/\n", encoding="utf-8")
            subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
            (root / "examples/results").mkdir()
            (root / "examples/results/private.json").write_text('{"unpublished":"research"}', encoding="utf-8")
            with zipfile.ZipFile(build(base / "filtered", root=root)) as package:
                self.assertNotIn("examples/results/private.json", package.namelist())
                self.assertIn("examples/run_examples.py", package.namelist())

    def test_deterministic_current_package_and_relocated_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = build(base / "one")
            second = build(base / "two")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                names = archive.namelist()
                self.assertIn("plugin.json", names)
                self.assertIn("src/research_workflow/bridge.js", names)
                self.assertIn("skills/research-workflow/SKILL.md", names)
                self.assertFalse(
                    any("research-mentor" in name or "__pycache__" in name or "test_" in name for name in names)
                )
                self.assertFalse(any(name.endswith("project.json") or name.startswith("tests/") for name in names))
                archive.extractall(base / "unpacked")
            self.assertTrue((base / "unpacked/mcp.json").is_file())
