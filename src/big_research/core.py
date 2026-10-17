"""Local research records. No model calls, network access, or command execution."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from contextlib import contextmanager
from copy import deepcopy
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path, PureWindowsPath
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from . import __version__

STATES = {"planned", "active", "blocked", "complete", "stale", "out_of_scope"}
NAVIGATION = [
    ("frame", "明确问题 / Frame the question"),
    ("map", "理解已有工作 / Map existing knowledge"),
    ("design", "选择研究路径 / Design an approach"),
    ("investigate", "开展研究 / Investigate"),
    ("interpret", "解释与检验 / Interpret and examine"),
    ("communicate", "写作与修订 / Communicate and revise"),
]


class WorkflowError(ValueError):
    """A recoverable validation or workspace error."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise WorkflowError(message)


def now() -> str:
    return datetime.now(UTC).isoformat()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def read_json(path: Path) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise WorkflowError(f"Non-finite JSON value: {value}")

    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    require(isinstance(result, dict), "Expected a JSON object")
    return result


def atomic_json(path: Path, value: dict) -> None:
    require(not path.is_symlink(), "Refuse symlink state file")
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(root: Path):
    path = root / ".research.lock"
    require(not path.is_symlink(), "Refuse symlink lock")
    with path.open("a+b") as handle:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise WorkflowError("Project is locked by another writer; retry after it finishes") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def inside(root: Path, relative: str) -> Path:
    require(nonempty(relative), "Expected a relative project path")
    path = Path(relative)
    require(
        not path.is_absolute()
        and not PureWindowsPath(relative).drive
        and ".." not in relative.replace("\\", "/").split("/"),
        "Unsafe project path",
    )
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root), "Path escapes project")
    require(resolved != root, "Expected a file inside project")
    return resolved


def digest(path: Path) -> str:
    require(path.is_file() and path.stat().st_size > 0, f"Missing or empty artifact: {path.name}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def methods() -> dict:
    return json.loads(files("big_research").joinpath("methods.json").read_text(encoding="utf-8"))


def identifier(value: Any) -> None:
    require(nonempty(value) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", value), "Invalid record ID")


def graph_check(tasks: dict) -> None:
    visited, visiting = set(), set()

    def visit(key):
        require(key in tasks, f"Unknown task dependency: {key}")
        require(key not in visiting, "Task dependencies contain a cycle")
        if key in visited:
            return
        visiting.add(key)
        task = tasks[key]
        require(isinstance(task, dict), f"Task {key} must be an object")
        require(task.get("id") == key, "Task ID mismatch")
        require(task.get("status") in STATES, f"Invalid task status: {key}")
        require(nonempty(task.get("title")), "Task needs a title")
        require(isinstance(task.get("depends_on"), list), "Dependencies must be a list")
        for dependency in task["depends_on"]:
            require(nonempty(dependency), "Dependency IDs must be strings")
            visit(dependency)
        visiting.remove(key)
        visited.add(key)

    for key in tasks:
        identifier(key)
        visit(key)


class Project:
    """An explicitly selected local research directory."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()

    @classmethod
    def create(
        cls, root: str | Path, title: str, *, field: str = "", paradigm: str = "", method_ids: list[str] | None = None
    ) -> Project:
        require(nonempty(title), "Project title is required")
        project = cls(root)
        project.root.mkdir(parents=True, exist_ok=True)
        with locked(project.root):
            require(
                not any(p.name != ".research.lock" for p in project.root.iterdir()),
                "Choose an empty directory; existing files are never overwritten",
            )
            chosen = method_ids or []
            require(all(m in methods() for m in chosen), "Unknown method module")
            tasks = {}
            for index, (key, label) in enumerate(NAVIGATION):
                tasks[key] = {
                    "id": key,
                    "title": label,
                    "depends_on": [NAVIGATION[index - 1][0]] if index else [],
                    "status": "planned",
                    "summary": "",
                    "outputs": [],
                    "evidence": [],
                }
            state = {
                "schema_version": 2,
                "workflow_version": __version__,
                "id": str(uuid4()),
                "title": title,
                "field": field,
                "paradigm": paradigm,
                "methods": chosen,
                "guidance": "guided",
                "revision": 0,
                "budget": {},
                "tasks": tasks,
                "evidence": {},
                "claims": {},
                "decisions": {},
                "concerns": {},
                "candidates": {},
                "method_reviews": {},
                "reviews": {},
                "history": [{"at": now(), "action": "create"}],
            }
            (project.root / "artifacts").mkdir()
            atomic_json(project.root / "project.json", state)
        return project

    def read(self) -> dict:
        return self._check_state(read_json(inside(self.root, "project.json")))

    def _check_state(self, state: dict) -> dict:
        require(state.get("schema_version") == 2, "Unsupported data format; migrate old data into a new directory")
        require(state.get("workflow_version") == __version__, "Only the current runtime is supported")
        for key in ("tasks", "evidence", "claims", "decisions", "concerns", "candidates", "method_reviews", "reviews"):
            require(isinstance(state.get(key), dict), f"Invalid project collection: {key}")
        require(type(state.get("revision")) is int and state["revision"] >= 0, "Invalid revision")
        require(isinstance(state.get("history"), list), "Invalid history")
        require(
            isinstance(state.get("methods"), list) and all(nonempty(m) and m in methods() for m in state["methods"]),
            "Invalid method selection",
        )
        require(isinstance(state.get("budget"), dict), "Invalid budget")
        graph_check(state["tasks"])
        for key, item in state["evidence"].items():
            self._check_evidence(item)
            require(item["id"] == key and key not in state["claims"], "Evidence ID mismatch or collision")
        for key, claim in state["claims"].items():
            self._check_claim(state, claim)
            require(claim["id"] == key, "Claim ID mismatch")
        for task in state["tasks"].values():
            require(
                isinstance(task.get("outputs"), list) and all(nonempty(p) for p in task["outputs"]),
                "Invalid task outputs",
            )
            self._evidence_snapshot(state, task.get("evidence"))
        for collection in ("decisions", "concerns", "candidates", "method_reviews", "reviews"):
            for key, item in state[collection].items():
                require(isinstance(item, dict) and item.get("id") == key, f"Invalid {collection} record")
                identifier(key)
        return state

    @staticmethod
    def _check_evidence(item: dict) -> None:
        require(isinstance(item, dict), "Evidence must be an object")
        identifier(item.get("id"))
        require(nonempty(item.get("title")), "Evidence needs a title")
        kind, status = item.get("kind"), item.get("status")
        require(kind in {"source", "run", "proof", "corpus", "analysis", "interpretation"}, "Unknown evidence kind")
        if kind == "source":
            require(status in {"verified", "unverified"}, "Invalid source status")
            require(bool(item.get("path")) != bool(item.get("url")), "Choose one local path or source URL")
            if "url" in item:
                require(nonempty(item["url"]), "Source URL must be text")
                parsed = urlsplit(item["url"])
                require(parsed.scheme in {"http", "https"} and parsed.netloc, "Invalid source URL")
            if status == "verified":
                require(
                    nonempty(item.get("accessed")) and nonempty(item.get("locator")),
                    "Verified source needs inspection date and locator",
                )
                try:
                    datetime.fromisoformat(item["accessed"])
                except ValueError as exc:
                    raise WorkflowError("Invalid inspection date") from exc
        elif kind == "run":
            require(status in {"planned", "failed", "executed"}, "Invalid run status")
            if status == "executed":
                require(
                    nonempty(item.get("command")) and nonempty(item.get("environment")) and bool(item.get("artifacts")),
                    "Executed run needs command, environment and actual artifacts",
                )
        else:
            require(status in {"planned", "documented"}, "Invalid analysis status")
            if status == "documented":
                require(bool(item.get("path")) or bool(item.get("artifacts")), "Documented evidence needs artifacts")
        if "path" in item:
            require(nonempty(item["path"]), "Artifact path must be text")
        if "artifacts" in item:
            require(
                isinstance(item["artifacts"], list)
                and all(isinstance(a, dict) and nonempty(a.get("path")) for a in item["artifacts"]),
                "Artifacts must contain path objects",
            )

    @staticmethod
    def _check_claim(state: dict, item: dict) -> None:
        require(isinstance(item, dict), "Claim must be an object")
        identifier(item.get("id"))
        require(nonempty(item.get("text")), "Claim text is required")
        require(
            item.get("status") in {"hypothesis", "supported", "unsupported", "needs_review"}, "Invalid claim status"
        )
        for field in ("supports", "contradicts"):
            require(
                isinstance(item.get(field), list)
                and all(nonempty(ref) and ref in state["evidence"] for ref in item[field]),
                "Claim links must reference direct evidence",
            )
        if item["status"] == "supported":
            require(
                bool(item["supports"])
                and all(
                    state["evidence"][ref]["status"] in {"verified", "executed", "documented"}
                    for ref in item["supports"]
                ),
                "Supported claims need eligible direct evidence",
            )

    @staticmethod
    def _method_basis(state: dict) -> str:
        return fingerprint(
            {key: state[key] for key in ("title", "field", "paradigm", "methods", "tasks", "evidence", "claims")}
        )

    @staticmethod
    def _conclusion_basis(state: dict) -> str:
        return fingerprint(
            {
                "research": Project._method_basis(state),
                "method_reviews": state["method_reviews"],
                "reviews": state["reviews"],
                "concerns": state["concerns"],
            }
        )

    def _mutate(self, action: str, change, expected_revision: int | None = None) -> dict:
        with locked(self.root):
            state = self.read()
            require(
                expected_revision is None or state["revision"] == expected_revision,
                "Revision conflict; refresh before saving",
            )
            before = deepcopy(state)
            detail = change(state)
            graph_check(state["tasks"])
            state["revision"] += 1
            state["history"].append({"at": now(), "action": action, **detail})
            # Serializing before replacement also validates all values and preserves the old state on failure.
            json.dumps(state, allow_nan=False)
            require(state["id"] == before["id"], "Project identity changed")
            self._check_state(state)
            atomic_json(self.root / "project.json", state)
            return state

    @staticmethod
    def _invalidate(state: dict, task_ids: set[str]) -> None:
        affected = set(task_ids)
        while True:
            new = {key for key, task in state["tasks"].items() if affected.intersection(task["depends_on"])}
            if new.issubset(affected):
                break
            affected |= new
        for key in affected:
            task = state["tasks"][key]
            if task["status"] in {"complete", "active"}:
                task["status"] = "stale"

    def configure(self, **changes) -> dict:
        require(
            set(changes) <= {"title", "field", "paradigm", "method_ids", "guidance", "budget"},
            "Unknown project setting",
        )

        def change(state):
            before = {k: state.get("methods" if k == "method_ids" else k) for k in changes}
            for key, value in changes.items():
                if key == "method_ids":
                    require(isinstance(value, list) and all(m in methods() for m in value), "Unknown method module")
                    key = "methods"
                elif key == "budget":
                    require(isinstance(value, dict), "Budget must be an object")
                    require(
                        all(
                            type(value.get(k)) in {int, float} and math.isfinite(value[k]) and value[k] >= 0
                            for k in ("limit", "spent")
                        ),
                        "Budget needs nonnegative finite limit and spent",
                    )
                    require(nonempty(value.get("unit")), "Budget unit is required")
                elif key == "guidance":
                    require(value in {"guided", "concise"}, "Choose guided or concise")
                else:
                    require(isinstance(value, str), "Setting must be text")
                    if key == "title":
                        require(nonempty(value), "Title is required")
                state[key] = value
            if set(changes) & {"title", "field", "paradigm", "method_ids"}:
                self._invalidate(state, set(state["tasks"]))
                state["method_reviews"] = {}
            return {"before": before, "after": changes}

        return self._mutate("configure", change)

    def add_task(self, task: dict) -> dict:
        identifier(task.get("id"))

        def change(state):
            key = task["id"]
            require(key not in state["tasks"], "Task ID already exists")
            require(set(task) <= {"id", "title", "depends_on"}, "New tasks begin planned")
            state["tasks"][key] = {
                "id": key,
                "title": task.get("title"),
                "depends_on": task.get("depends_on", []),
                "status": "planned",
                "summary": "",
                "outputs": [],
                "evidence": [],
            }
            return {"task": key}

        return self._mutate("add_task", change)

    def _evidence_snapshot(self, state: dict, refs: list[str]) -> dict:
        result = {}
        require(isinstance(refs, list), "Evidence references must be a list")
        for ref in refs:
            if ref in state["claims"]:
                claim = state["claims"][ref]
                result[ref] = fingerprint(claim)
                result.update(self._evidence_snapshot(state, claim.get("supports", []) + claim.get("contradicts", [])))
            else:
                require(ref in state["evidence"], f"Unknown evidence: {ref}")
                result[ref] = fingerprint(state["evidence"][ref])
        return result

    def update_task(self, task_id: str, changes: dict, expected_revision: int | None = None) -> dict:
        require(
            set(changes) <= {"title", "depends_on", "status", "summary", "outputs", "evidence", "reason"},
            "Unknown task field",
        )

        def change(state):
            require(task_id in state["tasks"], "Unknown task")
            task = state["tasks"][task_id]
            before = deepcopy(task)
            if task["status"] == "complete":
                self._invalidate(state, {task_id})
            task.update(deepcopy(changes))
            require(isinstance(task.get("outputs"), list), "Outputs must be a list")
            snapshots = self._evidence_snapshot(state, task.get("evidence", []))
            if task["status"] == "complete":
                require(
                    all(state["tasks"][d]["status"] == "complete" for d in task["depends_on"]),
                    "Complete dependencies first, or explicitly redesign the task graph",
                )
                require(
                    nonempty(task.get("summary")) and task["outputs"],
                    "Completion needs a summary and actual output files",
                )
                task["output_hashes"] = {path: digest(inside(self.root, path)) for path in task["outputs"]}
                task["evidence_hashes"] = snapshots
            if task["status"] in {"blocked", "out_of_scope"}:
                require(nonempty(task.get("reason")), "A reason is required")
            return {"task": task_id, "before": before, "after": deepcopy(task)}

        return self._mutate("update_task", change, expected_revision)

    def record_evidence(self, record: dict) -> dict:
        item = deepcopy(record)
        self._check_evidence(item)
        identifier(item.get("id"))
        require(nonempty(item.get("title")), "Evidence needs a title")
        require(
            item.get("kind") in {"source", "run", "proof", "corpus", "analysis", "interpretation"},
            "Unknown evidence kind",
        )
        if item["kind"] == "source":
            require(item.get("status") in {"verified", "unverified"}, "Source needs verified/unverified status")
            require(bool(item.get("path")) != bool(item.get("url")), "Choose one local path or source URL")
            if "url" in item:
                parsed = urlsplit(item["url"])
                require(parsed.scheme in {"http", "https"} and bool(parsed.netloc), "Invalid source URL")
            if item["status"] == "verified":
                require(
                    nonempty(item.get("accessed")) and nonempty(item.get("locator")),
                    "Verified sources need inspection date and precise locator",
                )
                datetime.fromisoformat(item["accessed"])
        elif item["kind"] == "run":
            require(item.get("status") in {"planned", "executed", "failed"}, "Invalid run status")
            if item["status"] == "executed":
                require(
                    nonempty(item.get("command")) and nonempty(item.get("environment")) and item.get("artifacts"),
                    "Executed runs need command, environment and artifacts",
                )
        else:
            require(item.get("status") in {"planned", "documented"}, "Analysis records need planned/documented status")
            if item["status"] == "documented":
                require(item.get("path") or item.get("artifacts"), "Documented work needs actual artifacts")
        if "path" in item:
            item["sha256"] = digest(inside(self.root, item["path"]))
        if "artifacts" in item:
            require(isinstance(item["artifacts"], list), "Artifacts must be a list")
            for artifact in item["artifacts"]:
                artifact["sha256"] = digest(inside(self.root, artifact.get("path")))

        def change(state):
            key = item["id"]
            require(key not in state["claims"], "ID already used by a claim")
            before = state["evidence"].get(key)
            if before != item:
                linked = {key}
                for cid, claim in state["claims"].items():
                    if key in claim.get("supports", []) + claim.get("contradicts", []):
                        claim["status"] = "needs_review"
                        linked.add(cid)
                self._invalidate(
                    state, {tid for tid, task in state["tasks"].items() if linked.intersection(task["evidence"])}
                )
                state["method_reviews"] = {}
            state["evidence"][key] = item
            return {"id": key, "before": before, "after": item}

        return self._mutate("record_evidence", change)

    def record_claim(self, record: dict) -> dict:
        item = deepcopy(record)
        identifier(item.get("id"))
        require(nonempty(item.get("text")), "Claim text is required")
        require(
            item.get("status") in {"hypothesis", "supported", "unsupported", "needs_review"}, "Invalid claim status"
        )
        item.setdefault("supports", [])
        item.setdefault("contradicts", [])

        def change(state):
            self._check_claim(state, item)
            key = item["id"]
            require(key not in state["evidence"], "ID already used by evidence")
            for ref in item["supports"] + item["contradicts"]:
                require(ref in state["evidence"], "Claims must link directly to evidence")
            if item["status"] == "supported":
                require(item["supports"], "Supported claims need inspected evidence")
                require(
                    all(
                        state["evidence"][ref]["status"] in {"verified", "executed", "documented"}
                        for ref in item["supports"]
                    ),
                    "Planned, failed or unverified evidence cannot support findings",
                )
                require(self.validate()["structural_valid"], "Repair evidence integrity before supporting claims")
            before = state["claims"].get(key)
            if before != item:
                self._invalidate(state, {tid for tid, task in state["tasks"].items() if key in task["evidence"]})
                state["method_reviews"] = {}
            state["claims"][key] = item
            return {"id": key, "before": before, "after": item}

        return self._mutate("record_claim", change)

    def _record(self, collection: str, record: dict) -> dict:
        item = deepcopy(record)
        identifier(item.get("id"))

        def change(state):
            before = state[collection].get(item["id"])
            if collection in {"method_reviews", "reviews"}:
                item["basis"] = self._method_basis(state)
            if collection == "decisions" and item["id"] == "research-conclusion" and item.get("status") == "confirmed":
                item["basis"] = self._conclusion_basis(state)
            state[collection][item["id"]] = item
            return {"id": item["id"], "before": before, "after": item}

        return self._mutate(f"record_{collection}", change)

    def record_decision(self, record: dict) -> dict:
        require(nonempty(record.get("question")), "Decision needs a question")
        require(record.get("status") in {"pending", "confirmed"}, "Invalid decision status")
        if record["status"] == "confirmed":
            require(
                nonempty(record.get("choice")) and nonempty(record.get("researcher_statement")),
                "Record the researcher's actual choice and statement; the tool cannot authenticate authorship",
            )
        return self._record("decisions", record)

    def record_concern(self, record: dict) -> dict:
        require(nonempty(record.get("text")), "Concern needs text")
        require(record.get("status") in {"open", "resolved"}, "Invalid concern status")
        if record["status"] == "resolved":
            require(nonempty(record.get("resolution")), "Resolution needs an explanation")
        return self._record("concerns", record)

    def record_candidate(self, record: dict) -> dict:
        require(nonempty(record.get("title")), "Candidate needs a title")
        require(
            all(nonempty(record.get(k)) for k in ("value", "evidence", "cost", "feasibility")),
            "Compare value, evidence, cost and feasibility explicitly",
        )
        return self._record("candidates", record)

    def record_method_review(self, record: dict) -> dict:
        module = record.get("id")
        require(module in self.read()["methods"], "Choose an active method module")
        require(
            set(record.get("checks", {})) == set(methods()[module]["checks"]), "Review every applicable method check"
        )
        require(
            all(
                isinstance(v, dict)
                and v.get("verdict") in {"adequate", "needs_work", "not_applicable"}
                and nonempty(v.get("reason"))
                for v in record["checks"].values()
            ),
            "Checks need a verdict and evidence-based reason",
        )
        return self._record("method_reviews", record)

    def record_review(self, record: dict) -> dict:
        from .review import validate_review

        validate_review(record)
        return self._record("reviews", record)

    def validate(self) -> dict:
        state, errors = self.read(), []
        for key, evidence in state["evidence"].items():
            artifacts = ([evidence] if "path" in evidence else []) + evidence.get("artifacts", [])
            for artifact in artifacts:
                try:
                    require(
                        digest(inside(self.root, artifact["path"])) == artifact.get("sha256"), f"Evidence {key} changed"
                    )
                except (WorkflowError, OSError, KeyError) as exc:
                    errors.append(str(exc))
        for key, task in state["tasks"].items():
            if task["status"] == "complete":
                try:
                    require(
                        all(state["tasks"][dep]["status"] == "complete" for dep in task["depends_on"]),
                        f"Task {key} has incomplete dependencies",
                    )
                    require(bool(task.get("output_hashes")), f"Task {key} has no output snapshots")
                    for path, sha in task.get("output_hashes", {}).items():
                        require(digest(inside(self.root, path)) == sha, f"Task {key} output changed")
                    require(
                        self._evidence_snapshot(state, task["evidence"]) == task.get("evidence_hashes"),
                        f"Task {key} evidence changed",
                    )
                except (WorkflowError, OSError, KeyError) as exc:
                    errors.append(str(exc))
        return {"structural_valid": not errors, "errors": errors, "scientific_validity_certified": False}

    def status(self) -> dict:
        state = self.read()
        next_tasks = [
            task
            for task in state["tasks"].values()
            if task["status"] in {"planned", "active", "stale"}
            and all(state["tasks"][d]["status"] == "complete" for d in task["depends_on"])
        ]
        return {
            "project": state,
            "stale_reviews": [
                r["id"] for r in state["reviews"].values() if r.get("basis") != self._method_basis(state)
            ],
            "next_tasks": next_tasks,
            "pending_decisions": [d for d in state["decisions"].values() if d["status"] == "pending"],
            "integrity": self.validate(),
        }

    def assess(self) -> dict:
        state = self.read()
        checks = self.validate()
        reviews = state["method_reviews"]
        method_complete = bool(state["methods"]) and all(
            m in reviews
            and reviews[m].get("basis") == self._method_basis(state)
            and all(c["verdict"] != "needs_work" for c in reviews[m]["checks"].values())
            for m in state["methods"]
        )
        decision = state["decisions"].get("research-conclusion", {})
        budget = state["budget"]
        return {
            **checks,
            "method_checks_complete": method_complete,
            "researcher_confirmed": decision.get("status") == "confirmed"
            and decision.get("basis") == self._conclusion_basis(state),
            "stale_reviews": [
                r["id"] for r in state["reviews"].values() if r.get("basis") != self._method_basis(state)
            ],
            "open_concerns": [r for r in state["concerns"].values() if r["status"] == "open"],
            "claims_needing_review": [c for c in state["claims"].values() if c["status"] != "supported"],
            "budget_exhausted": bool(budget) and budget["spent"] >= budget["limit"],
            "note": "Recorded checks and decisions are not certification of truth, ethics approval, or publication readiness.",
        }

    def export(self, relative: str = "artifacts/workspace.html") -> str:
        from .views import render

        target = inside(self.root, relative)
        require(not target.exists(), "Export destination exists; choose a new filename")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as handle:
            if target.suffix == ".json":
                json.dump(self.status(), handle, indent=2, ensure_ascii=False, allow_nan=False)
            else:
                handle.write(render(self.status()))
        return str(target)
