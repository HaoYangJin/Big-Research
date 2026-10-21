"""Validate current package identity, assets and documentation references."""

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    root = Path(root)
    version = (root / "VERSION").read_text().strip()
    assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version), "Invalid version"
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["version"] == version
    lockfile = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    locked = {package["name"]: package for package in lockfile["package"]}
    assert locked["big-research"]["version"] == version, "Lockfile drift"
    for relative in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        manifest = json.loads((root / relative).read_text(encoding="utf-8"))
        assert manifest["version"] == version and manifest["name"] == "big-research", "Manifest drift"
    marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    assert len(marketplace["plugins"]) == 1 and marketplace["plugins"][0]["version"] == version
    codex_marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    assert codex_marketplace["name"] == marketplace["name"]
    assert codex_marketplace["plugins"][0]["source"] == {"source": "local", "path": "./"}
    assert not (root / "skills/research-mentor").exists(), "Historical skill must not be shipped"
    assert not (root / "SKILL.md").exists(), "Duplicate root skill"
    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    assert len(skill_files) == 7, "Expected current composed skills"
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        assert text.startswith(f"---\nname: {path.parent.name}\ndescription: ")
        assert len(text.splitlines()) < 150, "Use progressive disclosure"
        assert (path.parent / "agents/openai.yaml").is_file()
    for required in (
        "src/big_research/methods.json",
        "src/big_research/review_profiles.json",
        "src/big_research/workspace.html",
        "src/big_research/bridge.js",
        "uv.lock",
        "package-lock.json",
        "mcp.json",
        ".mcp.json",
    ):
        assert (root / required).is_file(), f"Missing runtime asset: {required}"
    assert (root / "README.md").read_text(encoding="utf-8").startswith("> 本项目旨在利用 AI 工具辅助人类科学家")
    assert (root / "README.en.md").read_text(encoding="utf-8").startswith("> This project uses AI tools")
    markdown = (
        list((root / "docs").rglob("*.md"))
        + list((root / "skills").rglob("*.md"))
        + list((root / ".github/maintainers").rglob("*.md"))
        + list(root.glob("*.md"))
    )
    for path in markdown:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            relative = target.split("#")[0]
            if not relative or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", relative):
                continue
            assert (path.parent / relative).is_file() or (path.parent / relative).is_dir(), (
                f"Broken link: {path.relative_to(root)} -> {target}"
            )
    return version


if __name__ == "__main__":
    try:
        print(f"Current package checks passed: v{validate()}")
    except (OSError, ValueError, KeyError, AssertionError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
