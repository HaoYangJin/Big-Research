#!/usr/bin/env python3
"""Build deterministic, allowlisted standalone-skill and cross-host-plugin ZIPs."""
import argparse
import hashlib
from pathlib import Path
import zipfile

from validate_repo import ROOT, validate


def archive(path, entries):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for target, source in sorted(entries):
            info = zipfile.ZipInfo(target, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, source.read_bytes())


def build(output, root=ROOT):
    version = validate(root)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    skill = root / "skills/research-mentor"
    allowed = {"references", "scripts", "agents", "examples", "assets"}
    files = []
    for p in skill.rglob("*"):
        rel = p.relative_to(skill)
        if not p.is_file() or any(part.startswith(".") or part == "__pycache__" for part in rel.parts):
            continue
        if p.suffix == ".pyc" or p.name in {"project.json", "evidence.json"}:
            continue
        if rel.as_posix() == "SKILL.md" or rel.parts[0] in allowed:
            files.append(p)
    standalone = [("research-mentor/" + p.relative_to(skill).as_posix(), p) for p in files]
    standalone.append(("research-mentor/LICENSE", root / "LICENSE"))
    plugin = [(p.relative_to(root).as_posix(), p) for p in files]
    plugin += [(p, root / p) for p in [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".codex-plugin/plugin.json", "assets/plugin-icon.svg", "LICENSE", "VERSION"]]
    docs = [p for p in (root / "docs").rglob("*") if p.is_file()]
    docs += [p for folder in ["examples", "scripts", "tests"] for p in (root / folder).rglob("*") if p.is_file() and p.suffix in {".py", ".md", ".json"}]
    docs += [root / "CODE_OF_CONDUCT.md"]
    docs += [root / name for name in ["README.md", "README.en.md", "USAGE.md", "CHANGELOG.md", "CONTRIBUTING.md"]]
    plugin += [(p.relative_to(root).as_posix(), p) for p in docs]
    plugin += [(p.relative_to(root).as_posix(), p) for p in (root / "assets").glob("*.svg") if p.name != "plugin-icon.svg"]
    paths = [output / f"research-mentor-{version}.zip", output / f"research-workflow-{version}.zip"]
    archive(paths[0], standalone)
    archive(paths[1], plugin)
    sums = output / "SHA256SUMS.txt"
    sums.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in paths), encoding="utf-8")
    print("\n".join(str(p) for p in paths + [sums]))
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="dist")
    build(parser.parse_args().output)

