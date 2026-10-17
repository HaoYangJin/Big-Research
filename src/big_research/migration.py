"""Import known v1 data without importing or executing any historical implementation."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from pathlib import Path

from .core import Project, atomic_json, digest, fingerprint, inside, read_json, require


def validate_legacy(root: Path) -> tuple[dict, dict]:
    state, ledger = read_json(inside(root, "project.json")), read_json(inside(root, "evidence.json"))
    require(
        state.get("schema_version") == 1 and state.get("workflow_version") in {"1.0.0", "1.1.0"},
        "Only known v1.0.0/v1.1.0 project data can be imported",
    )
    require(isinstance(state.get("title"), str) and state["title"].strip(), "Missing legacy title")
    require(set(ledger) == {"sources", "experiments", "claims"}, "Invalid legacy evidence ledger")
    require(
        isinstance(state.get("stages"), dict) and set(state["stages"]) == {str(n) for n in range(1, 10)},
        "Expected nine legacy stages",
    )
    index = {}
    for records in ledger.values():
        require(isinstance(records, list), "Legacy evidence must be lists")
        for item in records:
            require(
                isinstance(item, dict) and item.get("id") and item["id"] not in index,
                "Duplicate or invalid legacy evidence ID",
            )
            index[item["id"]] = item
    for item in ledger["sources"] + ledger["experiments"]:
        artifacts = ([item] if "path" in item else []) + item.get("artifacts", [])
        for artifact in artifacts:
            require(
                digest(inside(root, artifact.get("path"))) == artifact.get("sha256"), "Legacy evidence artifact changed"
            )
    for claim in ledger["claims"]:
        require(
            all(ref in index and ref not in {c["id"] for c in ledger["claims"]} for ref in claim.get("evidence", [])),
            "Invalid legacy claim references",
        )
        if claim.get("status") == "supported":
            require(
                claim.get("evidence")
                and all(index[ref].get("status") in {"verified", "executed"} for ref in claim["evidence"]),
                "Legacy supported claim has inadequate evidence records",
            )
    for stage in state["stages"].values():
        require(
            stage.get("status") in {"pending", "done", "blocked", "skipped", "not_requested"},
            "Invalid legacy stage status",
        )
        if stage["status"] != "done":
            continue
        artifact = read_json(inside(root, stage.get("artifact")))
        require(digest(inside(root, stage["artifact"])) == stage.get("sha256"), "Legacy checkpoint changed")
        for path, expected in stage.get("output_hashes", {}).items():
            require(digest(inside(root, path)) == expected, "Legacy output changed")
        for key, expected in stage.get("evidence_hashes", {}).items():
            require(key in index and fingerprint(index[key]) == expected, "Legacy checkpoint evidence changed")
        require(all(ref in index for ref in artifact.get("evidence", [])), "Unknown legacy checkpoint evidence")
    return state, ledger


def migrate(source: str | Path, destination: str | Path) -> Project:
    root, target = Path(source).resolve(), Path(destination).resolve()
    require(
        root != target and not target.is_relative_to(root) and not root.is_relative_to(target),
        "Source and destination must be separate directories",
    )
    require(not target.exists(), "Migration destination must not exist")
    source_files = []

    def traversal_error(error):
        raise error

    for folder, directories, filenames in os.walk(root, followlinks=False, onerror=traversal_error):
        for name in directories + filenames:
            path = Path(folder) / name
            require(
                not path.is_symlink() and not (getattr(path.lstat(), "st_file_attributes", 0) & 0x400),
                "Migration refuses symlinks and junctions; materialize and inspect the files first",
            )
        directories[:] = [name for name in directories if name not in {".git", ".venv", "__pycache__"}]
        source_files.extend(
            Path(folder) / name for name in filenames if name not in {".workflow.lock", ".research.lock"}
        )
    original, ledger = validate_legacy(root)
    hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".research-import-", dir=target.parent)).resolve()
    require(staging.is_relative_to(target.parent), "Unsafe migration staging directory")
    try:
        project = Project.create(staging, original["title"], paradigm="Imported project; select applicable methods")
        for source_file in source_files:
            relative = source_file.relative_to(root)
            if relative.as_posix() == "project.json":
                relative = Path("artifacts/imported-v1-project.json")
            dest = inside(staging, relative.as_posix())
            require(not dest.exists(), f"Migration path collision: {relative}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, dest)
            require(
                hashlib.sha256(dest.read_bytes()).hexdigest() == hashes[source_file.relative_to(root).as_posix()],
                "Source changed while copying",
            )
        for item in ledger["sources"]:
            project.record_evidence({**item, "kind": "source"})
        for item in ledger["experiments"]:
            project.record_evidence({**item, "title": item.get("title", item["id"]), "kind": "run"})
        for item in ledger["claims"]:
            imported = {k: v for k, v in item.items() if k != "evidence"}
            project.record_claim({**imported, "status": "needs_review", "supports": item.get("evidence", [])})
        state = project.read()
        state["legacy_import"] = {
            "workflow_version": original["workflow_version"],
            "metadata": "artifacts/imported-v1-project.json",
            "source_hashes": hashes,
            "completion_and_submission_verdicts_imported": False,
        }
        atomic_json(staging / "project.json", state)
        validate_legacy(root)
        require(
            all(hashlib.sha256(inside(root, path).read_bytes()).hexdigest() == sha for path, sha in hashes.items()),
            "Source changed during migration",
        )
        require(project.validate()["structural_valid"], "Imported project failed integrity checks")
        staging.rename(target)
        return Project(target)
    except (OSError, ValueError, KeyError, TypeError):
        # Only this freshly created, verified staging directory is removed.
        shutil.rmtree(staging)
        raise
