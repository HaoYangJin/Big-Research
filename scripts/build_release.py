"""Create a deterministic, allowlisted current-plugin archive; no research data or old runtime."""

import argparse
import hashlib
import subprocess
import zipfile
from pathlib import Path

from validate_repo import ROOT, validate

FILES = [
    "plugin.json",
    "mcp.json",
    ".mcp.json",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "pyproject.toml",
    "uv.lock",
    "LICENSE",
    "VERSION",
    "README.md",
    "README.en.md",
]


def build(output, root=ROOT):
    root, output = Path(root), Path(output)
    version = validate(root)
    # A clean release checkout contains only tracked source plus ignored caches/data.
    # Never recursively package ignored research output or maintainer-only files.
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        check=True,
    ).stdout
    eligible = {name.decode("utf-8") for name in listing.split(b"\0") if name}
    entries = [(name, root / name) for name in FILES]
    for directory in ("skills", "src/big_research", "assets"):
        for path in (root / directory).rglob("*"):
            relative = path.relative_to(root)
            if (
                path.is_file()
                and not path.name.startswith("test_")
                and not any(part.startswith(".") or part == "__pycache__" for part in relative.parts)
                and path.suffix in {".py", ".md", ".yaml", ".json", ".html", ".js", ".txt", ".svg", ".png"}
            ):
                assert not path.is_symlink(), "Package symlinks are not permitted"
                entries.append((relative.as_posix(), path))
    for name in (
        "docs/quickstart.md",
        "docs/methods.md",
        "docs/compatibility.md",
        "docs/research-basis.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "NOTICE.md",
        "CITATION.cff",
    ):
        entries.append((name, root / name))
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"big-research-{version}.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(entries):
            if name not in eligible:
                continue
            assert path.resolve().is_relative_to(root.resolve()) and not path.is_symlink(), "Unsafe package path"
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    sums = output / "SHA256SUMS.txt"
    sums.write_text(f"{hashlib.sha256(target.read_bytes()).hexdigest()}  {target.name}\n", encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="dist")
    print(build(parser.parse_args().output))
