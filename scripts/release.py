"""Guarded GitHub release controller; persistent draft state and unlimited daily PDT deferral."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from build_release import build  # noqa: E402

from research_workflow.release_policy import advance, parse, release_action  # noqa: E402

STATE_ASSET = "release-state.json"
REQUIRED_CHECKS = {
    "independent_code_review",
    "behavioral_skill_evaluation",
    "cross_disciplinary_examples",
    "interactive_ui",
    "claude_clean_install",
    "codex_clean_install",
}


def ensure_clean_checkout(root: Path = ROOT) -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=normal"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    if result.stdout:
        raise RuntimeError("Release requires a clean checkout with all candidate and acceptance files committed")


def content_digest(root: Path = ROOT) -> str:
    """Bind manual acceptance to source bytes, excluding only the acceptance record itself."""
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        check=True,
    ).stdout
    records = {}
    for raw in listing.split(b"\0"):
        if not raw:
            continue
        name = raw.decode("utf-8")
        if name == ".github/release-acceptance.json":
            continue
        path = root / name
        if path.is_file():
            records[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def check_tag(github: GitHub, tag: str, sha: str) -> None:
    """Never publish candidate bytes under a tag identifying different source."""
    refs = github.api(f"repos/{github.repo}/git/matching-refs/tags/{tag}")
    exact = next((ref for ref in refs if ref["ref"] == "refs/tags/" + tag), None)
    if exact is None:
        return
    obj = exact["object"]
    seen = set()
    while obj["type"] == "tag":
        if obj["sha"] in seen:
            raise RuntimeError("Cyclic annotated tag")
        seen.add(obj["sha"])
        obj = github.api(f"repos/{github.repo}/git/tags/{obj['sha']}")["object"]
    if obj["type"] != "commit" or obj["sha"] != sha:
        raise RuntimeError("Existing release tag identifies different source; preserving it and refusing publication")


class GitHub:
    def __init__(self, repo: str):
        self.repo = repo

    def run(self, *args, binary=False):
        result = subprocess.run(["gh", *args], capture_output=True, text=not binary, check=False)
        if result.returncode:
            raise RuntimeError(
                f"GitHub operation failed: {args[0]} (exit {result.returncode}); inspect the authenticated workflow logs"
            )
        return result.stdout

    def api(self, endpoint: str, method="GET", payload=None):
        args = ["gh", "api", endpoint, "--method", method]
        if payload is not None:
            args += ["--input", "-"]
        result = subprocess.run(
            args,
            input=json.dumps(payload) if payload is not None else None,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(f"GitHub API {method} failed for {endpoint.split('?')[0]}")
        return json.loads(result.stdout) if result.stdout.strip() else None

    def release(self, tag: str):
        releases = self.api(f"repos/{self.repo}/releases?per_page=100")
        return next((r for r in releases if r["tag_name"] == tag), None)

    def upload(self, tag: str, path: Path):
        self.run("release", "upload", tag, str(path), "--repo", self.repo, "--clobber")

    def asset_bytes(self, asset: dict) -> bytes:
        return self.run(
            "api",
            f"repos/{self.repo}/releases/assets/{asset['id']}",
            "-H",
            "Accept: application/octet-stream",
            binary=True,
        )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def readiness(github: GitHub, sha: str, acceptance: dict, workflow: str, digest: str) -> tuple[bool, str | None, str]:
    checks = acceptance.get("checks", {})
    if (
        not REQUIRED_CHECKS.issubset(checks)
        or not all(value is True for value in checks.values())
        or not acceptance.get("verified_at")
    ):
        return False, None, "Primary acceptance is incomplete"
    if acceptance.get("content_sha256") != digest or not all(
        acceptance.get("evidence", {}).get(key) for key in REQUIRED_CHECKS
    ):
        return False, None, "Acceptance evidence does not match the candidate content"
    runs = github.api(f"repos/{github.repo}/actions/runs?head_sha={sha}&per_page=100")["workflow_runs"]
    relevant = [run for run in runs if run["name"] == workflow and run["head_sha"] == sha]
    if not relevant:
        return False, None, "No required CI run for the exact candidate"
    latest = max(relevant, key=lambda run: run["id"])
    if latest["status"] != "completed" or latest["conclusion"] != "success":
        return False, None, "Required CI has not passed for the exact candidate"
    ready_at = max(parse(latest["updated_at"]), parse(acceptance["verified_at"])).isoformat()
    return True, ready_at, "All required checks passed"


def save_state(github: GitHub, tag: str, state: dict, directory: Path) -> None:
    path = directory / STATE_ASSET
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    github.upload(tag, path)


def prepare(github: GitHub, plan: dict, sha: str, directory: Path) -> tuple[dict, dict]:
    ensure_clean_checkout()
    tag = "v" + plan["version"]
    check_tag(github, tag, sha)
    release = github.release(tag)
    if release and not release["draft"]:
        return release, {"published": True, "candidate_sha": release["target_commitish"]}
    if release is None:
        release = github.api(
            f"repos/{github.repo}/releases",
            "POST",
            {
                "tag_name": tag,
                "target_commitish": sha,
                "name": f"Research Workflow {tag}",
                "body": (ROOT / "docs/release-notes.md").read_text(encoding="utf-8"),
                "draft": True,
                "prerelease": False,
            },
        )
    state_asset = next((a for a in release["assets"] if a["name"] == STATE_ASSET), None)
    state = (
        json.loads(github.asset_bytes(state_asset))
        if state_asset
        else {"target": plan["initial_target"], "deferrals": 0, "history": [], "published": False}
    )
    archive = build(directory)
    package_hash = sha256(archive)
    if state.get("candidate_sha") != sha or state.get("package_sha256") != package_hash:
        github.api(f"repos/{github.repo}/releases/{release['id']}", "PATCH", {"target_commitish": sha})
        github.upload(tag, archive)
        github.upload(tag, directory / "SHA256SUMS.txt")
        state.update(candidate_sha=sha, package_sha256=package_hash, package_name=archive.name, ready_at=None)
        save_state(github, tag, state, directory)
    return release, state


def promote_main(github: GitHub, sha: str) -> None:
    repo = github.api(f"repos/{github.repo}")
    branch = repo["default_branch"]
    current = github.api(f"repos/{github.repo}/git/ref/heads/{branch}")["object"]["sha"]
    if current == sha:
        return
    comparison = github.api(f"repos/{github.repo}/compare/{current}...{sha}")
    if comparison["status"] != "ahead":
        raise RuntimeError(
            "Default branch cannot be fast-forwarded to the release candidate; merge its changes into the candidate first"
        )
    github.api(f"repos/{github.repo}/git/refs/heads/{branch}", "PATCH", {"sha": sha, "force": False})


def tick(github: GitHub, plan: dict, sha: str, acceptance: dict, *, once=False) -> dict:
    ensure_clean_checkout()
    tag = "v" + plan["version"]
    with tempfile.TemporaryDirectory(prefix="research-release-") as tmp:
        directory = Path(tmp)
        release, state = prepare(github, plan, sha, directory)
        if state["published"]:
            # Recover only an interrupted final promotion, and never overwrite another release's target.
            if state["candidate_sha"] == sha:
                promote_main(github, sha)
            return state
        while True:
            current = datetime.now(UTC)
            target = parse(state["target"])
            if (target - current).total_seconds() > 25 * 60:
                return state
            ready, ready_at, reason = readiness(github, sha, acceptance, plan["required_workflow"], content_digest())
            state["ready_at"] = ready_at
            action = release_action(state, current, ready, ready_at)
            if action == "wait":
                if once:
                    save_state(github, tag, state, directory)
                    return state
                time.sleep(min(30, max(0.1, (target - current).total_seconds())))
                continue
            if action == "defer":
                while parse(state["target"]) <= current:
                    state = advance(
                        state,
                        reason
                        if not ready
                        else "Candidate was not accepted before this midnight, or delivery window was missed",
                    )
                save_state(github, tag, state, directory)
                print(f"Deferred to {state['target']} (deferrals={state['deferrals']}; no limit)")
                return state
            if action == "publish":
                ensure_clean_checkout()
                check_tag(github, tag, sha)
                # Recheck branch identity immediately before publishing; CI must cover these exact bytes.
                actual = github.api(f"repos/{github.repo}/git/ref/heads/{plan['candidate_ref']}")["object"]["sha"]
                if actual != sha:
                    state = advance(state, "Candidate branch changed after preparation")
                    save_state(github, tag, state, directory)
                    return state
                refreshed = github.release(tag)
                package = next(a for a in refreshed["assets"] if a["name"] == state["package_name"])
                if hashlib.sha256(github.asset_bytes(package)).hexdigest() != state["package_sha256"]:
                    raise RuntimeError("Uploaded package digest differs from the accepted package")
                # Confirm promotion is safe before any public release mutation.
                default = github.api(f"repos/{github.repo}")["default_branch"]
                comparison = github.api(f"repos/{github.repo}/compare/{default}...{sha}")
                if comparison["status"] not in {"ahead", "identical"}:
                    state = advance(state, "Default branch changed; candidate needs integration and new CI")
                    save_state(github, tag, state, directory)
                    return state
                save_state(github, tag, state, directory)
                published = github.api(
                    f"repos/{github.repo}/releases/{release['id']}",
                    "PATCH",
                    {"draft": False, "make_latest": "true", "target_commitish": sha},
                )
                promote_main(github, sha)
                state.update(published=True, published_at=published["published_at"], url=published["html_url"])
                print(json.dumps({"published": True, "at": state["published_at"], "url": state["url"]}))
                return state
            raise RuntimeError(f"Unexpected release action: {action}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "tick", "status"])
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "HaoYangJin/Research-workflow-Skill"))
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    github = GitHub(args.repo)
    plan = json.loads((ROOT / ".github/release-plan.json").read_text(encoding="utf-8"))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    if args.command == "status":
        release = github.release("v" + plan["version"])
        print(
            json.dumps(
                {
                    "draft_exists": bool(release),
                    "published": bool(release and not release["draft"]),
                    "url": release["html_url"] if release else None,
                }
            )
        )
    elif args.command == "prepare":
        with tempfile.TemporaryDirectory(prefix="research-release-") as tmp:
            release, state = prepare(github, plan, sha, Path(tmp))
            print(json.dumps({"draft": release["draft"], "state": state}))
    else:
        tick(
            github,
            plan,
            sha,
            json.loads((ROOT / ".github/release-acceptance.json").read_text(encoding="utf-8")),
            once=args.once,
        )


if __name__ == "__main__":
    main()
