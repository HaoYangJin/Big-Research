#!/usr/bin/env python3
"""Local research checkpoints. Standard library only; never executes commands or fetches URLs."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlparse

VERSION = "1.0.0"
PHASES = {
    1: ("scope", ("question", "scope", "literature", "constraints")),
    2: ("hypothesis", ("hypotheses", "falsification", "contribution_boundary")),
    3: ("design", ("baselines", "metrics", "controls", "analysis_plan", "budget")),
    4: ("reproducibility", ("data_provenance", "split", "preprocessing", "reproduce", "environment")),
    5: ("results", ("observations", "uncertainty", "negative_results", "claim_limits")),
    6: ("draft", ("argument", "citation_audit", "limitations")),
    7: ("review", ("major_concerns", "fixes", "verdict")),
    8: ("revision", ("responses", "changes", "remaining_limits")),
    9: ("submission", ("fit", "venue_checks", "blockers", "next_action")),
}
STATES = {"pending", "done", "blocked", "skipped", "not_requested"}


class WorkflowError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise WorkflowError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and all(nonempty(x) for x in value)


def read_json(path):
    def pairs(items):
        obj = {}
        for key, value in items:
            require(key not in obj, f"Duplicate JSON key: {key}")
            obj[key] = value
        return obj
    def invalid_constant(value):
        raise WorkflowError(f"Non-finite JSON value: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=invalid_constant)


def inside(root, relative):
    require(nonempty(relative), "Artifact path must be a relative string")
    p = Path(relative)
    require(not p.is_absolute() and ".." not in p.parts, f"Unsafe artifact path: {relative}")
    result = (root / p).resolve()
    require(result.is_relative_to(root), f"Artifact escapes project: {relative}")
    return result


def digest(path):
    require(path.is_file() and path.stat().st_size > 0, f"Missing or empty artifact: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path, obj):
    require(not path.is_symlink(), f"Refuse symlink state file: {path}")
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(root):
    lock = root / ".workflow.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise WorkflowError("Project is locked; finish the other writer before retrying") from exc
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def load(root):
    state = read_json(inside(root, "project.json"))
    require(isinstance(state, dict) and state.get("schema_version") == 1, "Unsupported project schema")
    require(state.get("workflow_version") == VERSION, "Project version differs; migrate explicitly before writing")
    require(nonempty(state.get("title")), "Missing project title")
    require(state.get("mode") in {"mentor", "reviewer", "mixed"}, "Invalid mode")
    require(state.get("kind") in {"empirical", "theoretical", "review"}, "Invalid research kind")
    stages = state.get("stages")
    require(isinstance(stages, dict) and set(stages) == {str(n) for n in PHASES}, "Expected nine stages")
    require(isinstance(state.get("history"), list), "Invalid history")
    for n, stage in stages.items():
        require(isinstance(stage, dict) and stage.get("status") in STATES, f"Invalid stage {n}")
        if stage["status"] in {"skipped", "blocked", "not_requested"}:
            require(nonempty(stage.get("reason")), f"Stage {n} requires a reason")
    expected = next((n for n in PHASES if stages[str(n)]["status"] in {"pending", "blocked"}), None)
    require(state.get("current_phase") == expected, "Current phase is inconsistent with stage statuses")
    return state


def evidence(root):
    ledger = read_json(inside(root, "evidence.json"))
    require(isinstance(ledger, dict) and set(ledger) == {"sources", "experiments", "claims"}, "Invalid evidence ledger")
    index = {}
    for kind in ledger:
        require(isinstance(ledger[kind], list), f"{kind} must be a list")
        for item in ledger[kind]:
            require(isinstance(item, dict) and nonempty(item.get("id")), f"Invalid {kind} record")
            key = item["id"]
            require(key not in index, f"Duplicate evidence ID: {key}")
            index[key] = (kind, item)
    for key, (kind, item) in index.items():
        if kind == "sources":
            require(nonempty(item.get("title")), f"{key}: missing source title")
            require(item.get("status") in {"verified", "unverified"}, f"{key}: invalid source status")
            if "path" in item:
                require("url" not in item, f"{key}: choose a local path or URL, not both")
                require(digest(inside(root, item["path"])) == item.get("sha256"), f"{key}: local source hash mismatch")
            else:
                require(urlparse(item.get("url", "")).scheme in {"http", "https"} and urlparse(item["url"]).netloc, f"{key}: invalid source URL")
            if item["status"] == "verified":
                require(nonempty(item.get("accessed")) and nonempty(item.get("locator")), f"{key}: verified source needs accessed date and locator")
                try:
                    datetime.fromisoformat(item["accessed"])
                except ValueError as exc:
                    raise WorkflowError(f"{key}: invalid accessed ISO date") from exc
        elif kind == "experiments":
            require(item.get("status") in {"planned", "executed", "failed"}, f"{key}: invalid experiment status")
            require(nonempty(item.get("command")), f"{key}: missing command")
            if item["status"] == "executed":
                require(nonempty(item.get("environment")) and "seed" in item, f"{key}: record environment and seed (null for deterministic)")
                files = item.get("artifacts")
                require(isinstance(files, list) and files, f"{key}: executed experiment needs artifacts")
                for f in files:
                    require(isinstance(f, dict), f"{key}: invalid artifact")
                    require(digest(inside(root, f.get("path"))) == f.get("sha256"), f"{key}: artifact hash mismatch")
        else:
            require(nonempty(item.get("text")), f"{key}: missing claim text")
            require(item.get("status") in {"supported", "hypothesis", "unsupported"}, f"{key}: invalid claim status")
            refs = item.get("evidence", [])
            require(strings(refs), f"{key}: evidence must be ID strings")
            if item["status"] == "supported":
                require(refs, f"{key}: supported claim needs evidence")
            for ref in refs:
                require(ref in index and index[ref][0] != "claims", f"{key}: unknown or circular evidence {ref}")
                k, r = index[ref]
                if item["status"] == "supported":
                    require((k == "sources" and r["status"] == "verified") or (k == "experiments" and r["status"] == "executed"), f"{key}: evidence {ref} is not verified/executed")
    return index


def check_artifact(root, state, phase, obj, index):
    require(isinstance(obj, dict) and obj.get("phase") == phase, f"Stage artifact must have phase={phase}")
    require(nonempty(obj.get("summary")), "Stage artifact needs a summary")
    criteria = obj.get("criteria")
    require(isinstance(criteria, dict), "Missing criteria object")
    for key in PHASES[phase][1]:
        value = criteria.get(key)
        require(nonempty(value) and not re.match(r"^(TODO|TBD|待填写|<.*>)", value.strip(), re.I), f"Stage {phase}: fill criterion {key}")
    refs = obj.get("evidence", [])
    require(strings(refs) and all(r in index for r in refs), "Stage references unknown evidence IDs")
    outputs = obj.get("outputs", [])
    require(strings(outputs), "Outputs must be relative path strings")
    hashes = {p: digest(inside(root, p)) for p in outputs}
    if phase == 5:
        if state["kind"] == "empirical":
            require(any(index[r][0] == "experiments" and index[r][1]["status"] == "executed" for r in refs), "Empirical results require an executed experiment")
        elif state["kind"] == "review":
            require(any(index[r][0] == "sources" and index[r][1]["status"] == "verified" for r in refs), "Review results require verified sources")
        else:
            require(outputs, "Theoretical results require a proof/derivation artifact")
    if phase == 6:
        require(outputs, "Draft phase requires an actual draft file")
        require(any(index[r][0] == "claims" and index[r][1]["status"] == "supported" for r in refs), "Draft requires an evidence-backed claim; otherwise mark blocked")
    if phase in {7, 8}:
        field = "blocking_concerns" if phase == 7 else "resolved_concerns"
        require(strings(obj.get(field)), f"Stage {phase} requires a {field} list (may be empty)")
    if phase == 9:
        require(obj.get("decision") in {"ready", "not_ready"}, "Submission decision must be ready or not_ready")
        if obj["decision"] == "ready":
            require(all(state["stages"][str(n)]["status"] == "done" for n in range(1, 9)), "Ready requires stages 1-8 done; skipped/unrequested stages do not qualify")
            review = read_json(inside(root, state["stages"]["7"]["artifact"]))
            revision = read_json(inside(root, state["stages"]["8"]["artifact"]))
            require(not set(review["blocking_concerns"]) - set(revision["resolved_concerns"]), "Unresolved blocking review concerns")
            require(not any(k == "claims" and i["status"] == "unsupported" for k, i in index.values()), "Unsupported claims remain")
    return hashes


def validate(root, state):
    index = evidence(root)
    for n in PHASES:
        stage = state["stages"][str(n)]
        if stage["status"] == "done":
            path = inside(root, stage.get("artifact"))
            require(digest(path) == stage.get("sha256"), f"Stage {n} artifact changed; reopen before updating")
            hashes = check_artifact(root, state, n, read_json(path), index)
            require(hashes == stage.get("output_hashes"), f"Stage {n} output changed; reopen before updating")
            require(evidence_hashes(read_json(path).get("evidence", []), index) == stage.get("evidence_hashes"), f"Stage {n} evidence changed; reopen before updating")
    return index


def evidence_hashes(refs, index):
    hashes = {}
    for ref in refs:
        kind, item = index[ref]
        encoded = json.dumps(item, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")
        hashes[ref] = hashlib.sha256(encoded).hexdigest()
        if kind == "claims":
            hashes.update(evidence_hashes(item.get("evidence", []), index))
    return hashes


def init(args):
    root = Path(args.project).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with locked(root):
        require(not any(p.name != ".workflow.lock" for p in root.iterdir()), "Init requires an empty project directory; existing files are never overwritten")
        (root / "artifacts").mkdir()
        stages = {str(n): ({"status": "not_requested", "reason": "Entry phase chosen by user"} if n < args.phase else {"status": "pending"}) for n in PHASES}
        state = {"schema_version": 1, "workflow_version": VERSION, "title": args.title, "kind": args.kind, "mode": args.mode, "current_phase": args.phase, "stages": stages, "history": [{"at": now(), "action": "init", "phase": args.phase}]}
        atomic_json(root / "evidence.json", {"sources": [], "experiments": [], "claims": []})
        atomic_json(root / "project.json", state)
    return state


def change(args):
    root = Path(args.project).resolve()
    with locked(root):
        state = load(root)
        if args.command == "reopen":
            require(nonempty(args.reason), "Reopen requires a reason")
            # Reopening is also the recovery path for edited or missing downstream artifacts.
            for n in range(args.phase, 10):
                state["stages"][str(n)] = {"status": "pending"}
            state["current_phase"] = next(n for n in PHASES if state["stages"][str(n)]["status"] in {"pending", "blocked"})
        else:
            validate(root, state)
            require(args.phase == state["current_phase"], "Checkpoint only the current phase; reopen to revisit earlier work")
            record = {"status": args.status}
            if args.status == "done":
                require(args.artifact, "Done requires --artifact")
                path = inside(root, args.artifact)
                obj, index = read_json(path), evidence(root)
                record.update(artifact=args.artifact, sha256=digest(path), output_hashes=check_artifact(root, state, args.phase, obj, index), evidence_hashes=evidence_hashes(obj.get("evidence", []), index))
            else:
                require(nonempty(args.reason), "Blocked/skipped requires --reason")
                record["reason"] = args.reason
            state["stages"][str(args.phase)] = record
            state["current_phase"] = next((n for n in PHASES if state["stages"][str(n)]["status"] in {"pending", "blocked"}), None)
        state["history"].append({"at": now(), "action": args.command, "phase": args.phase, "reason": args.reason})
        atomic_json(root / "project.json", state)
    return state


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init")
    p.add_argument("project")
    p.add_argument("--title", required=True)
    p.add_argument("--mode", choices=["mentor", "reviewer", "mixed"], default="mentor")
    p.add_argument("--kind", choices=["empirical", "theoretical", "review"], default="empirical")
    p.add_argument("--phase", type=int, choices=PHASES, default=1)
    p = sub.add_parser("template")
    p.add_argument("--phase", type=int, choices=PHASES, required=True)
    for command in ["status", "validate", "checkpoint", "reopen"]:
        p = sub.add_parser(command)
        p.add_argument("project")
        if command in {"checkpoint", "reopen"}:
            p.add_argument("--phase", type=int, choices=PHASES, required=True)
            p.add_argument("--reason", default="")
        if command == "checkpoint":
            p.add_argument("--status", choices=["done", "blocked", "skipped"], default="done")
            p.add_argument("--artifact")
    args = parser.parse_args(argv)
    try:
        if args.command == "template":
            out = {"phase": args.phase, "summary": "TODO", "criteria": {k: "TODO" for k in PHASES[args.phase][1]}, "evidence": [], "outputs": []}
            if args.phase == 7:
                out["blocking_concerns"] = []
            if args.phase == 8:
                out["resolved_concerns"] = []
            if args.phase == 9:
                out["decision"] = "not_ready"
        elif args.command == "init":
            require(nonempty(args.title), "Title cannot be blank")
            out = init(args)
        elif args.command in {"checkpoint", "reopen"}:
            out = change(args)
        else:
            root = Path(args.project).resolve()
            state = load(root)
            validate(root, state)
            final = state["stages"]["9"]
            decision = read_json(inside(root, final["artifact"]))["decision"] if final["status"] == "done" else None
            out = {"valid": True, "validation": "structural_only", "title": state["title"], "mode": state["mode"], "kind": state["kind"], "current_phase": state["current_phase"], "workflow_complete": state["current_phase"] is None, "submission_decision": decision, "stages": state["stages"]}
        print(json.dumps(out, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (WorkflowError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
