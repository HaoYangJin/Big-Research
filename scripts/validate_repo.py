#!/usr/bin/env python3
"""Dependency-free source/package consistency checks; host validation is separate."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    version = (root / "VERSION").read_text().strip()
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), "Invalid release version"
    skill = root / "skills/research-mentor"
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: research-mentor\ndescription: "), "Invalid skill metadata"
    assert len(text.splitlines()) < 500, "Skill entry is too long"
    assert f'VERSION = "{version}"' in (skill / "scripts/workflow.py").read_text(encoding="utf-8"), "CLI version drift"
    claude = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    codex = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    for item in (claude, codex, marketplace["plugins"][0]):
        assert item["version"] == version and item["name"] == "research-workflow", "Manifest identity/version drift"
    assert marketplace["plugins"][0]["source"] == "./", "Marketplace source must resolve to this repository"
    assert codex["skills"] == "./skills/", "Missing canonical skill directory"
    interface = codex["interface"]
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "composerIcon", "logo"):
        assert field in interface and interface[field], f"Codex interface missing {field}"
    for field in ("displayName", "shortDescription"):
        assert len(interface[field]) <= 30, f"Codex {field} too long"
    for field in ("composerIcon", "logo"):
        assert (root / interface[field]).is_file(), f"Missing icon {field}"
    assert "$research-mentor" in (skill / "agents/openai.yaml").read_text(encoding="utf-8"), "Stale UI prompt"
    for doc in root.rglob("*.md"):
        if any(p in {".git", "dist", "node_modules"} for p in doc.parts):
            continue
        for target in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            path = target.split("#")[0]
            if not path or re.match(r"[a-z]+:", path):
                continue
            assert (doc.parent / path).exists(), f"Broken link: {doc.relative_to(root)} -> {target}"
    print(f"Repository checks passed: v{version} (structural; not a host import test)")
    return version


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
