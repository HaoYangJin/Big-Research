"""Fail-closed acceptance and tag checks without touching GitHub."""

import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from release import REQUIRED_CHECKS, check_tag, prepare, readiness, tick  # noqa: E402


class FakeGitHub:
    repo = "owner/repo"

    def __init__(self):
        self.tag = []
        self.runs = [
            {
                "id": 1,
                "name": "CI",
                "head_sha": "candidate",
                "status": "completed",
                "conclusion": "success",
                "updated_at": "2026-10-16T06:40:00Z",
            }
        ]

    def api(self, endpoint):
        if "matching-refs" in endpoint:
            return self.tag
        if "/git/tags/" in endpoint:
            return {"object": {"type": "commit", "sha": "candidate"}}
        return {"workflow_runs": self.runs}


class PersistentGitHub(FakeGitHub):
    def __init__(self):
        super().__init__()
        self.saved = None
        self.bytes = {}
        self.main = "previous"
        self.publications = 0

    def release(self, tag):
        return deepcopy(self.saved)

    def upload(self, tag, path):
        if self.saved["tag_name"] != tag:
            raise RuntimeError("Cannot upload to a draft that lost its version tag")
        self.bytes[path.name] = path.read_bytes()
        self.saved["assets"] = [{"name": name, "id": name} for name in self.bytes]

    def asset_bytes(self, asset):
        return self.bytes[asset["id"]]

    def api(self, endpoint, method="GET", payload=None):
        if method == "POST":
            self.saved = {**payload, "id": 1, "assets": []}
            return deepcopy(self.saved)
        if method == "PATCH" and "/releases/" in endpoint:
            self.saved.update(payload)
            # GitHub draft updates can reset an omitted tag_name to an untagged placeholder.
            if "tag_name" not in payload:
                self.saved["tag_name"] = "untagged-placeholder"
            if payload.get("draft") is False:
                self.publications += 1
                self.saved.update(published_at="2026-10-19T07:00:00Z", html_url="https://example.test/release")
            return deepcopy(self.saved)
        if method == "PATCH":
            self.main = payload["sha"]
            return {}
        if "/git/ref/heads/" in endpoint:
            return {"object": {"sha": self.main if endpoint.endswith("/main") else "candidate"}}
        if "/compare/" in endpoint:
            return {"status": "identical" if self.main == "candidate" else "ahead"}
        if endpoint == f"repos/{self.repo}":
            return {"default_branch": "main"}
        return super().api(endpoint)


class ControllerTests(unittest.TestCase):
    def test_persistent_deferrals_restart_then_publish_once_at_next_midnight(self):
        gh = PersistentGitHub()
        plan = {
            "version": "2.1.0",
            "initial_target": "2026-10-17T07:00:00Z",
            "candidate_ref": "candidate-branch",
            "required_workflow": "CI",
        }

        def package(directory):
            path = directory / "candidate.zip"
            path.write_bytes(b"tested immutable package")
            (directory / "SHA256SUMS.txt").write_text(hashlib.sha256(path.read_bytes()).hexdigest())
            return path

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch("release.ensure_clean_checkout"),
            patch("release.content_digest", return_value="digest"),
            patch("release.build", side_effect=package),
            patch("release.datetime") as clock,
        ):
            clock.now.return_value = datetime(2026, 10, 17, 7, tzinfo=UTC)
            first = tick(gh, plan, "candidate", {}, once=True)
            self.assertEqual(first["deferrals"], 1)
            self.assertEqual(gh.publications, 0)
            # A restarted preparation must preserve its saved target and history.
            _, restored = prepare(gh, plan, "candidate", Path(tmp))
            self.assertEqual(restored["target"], first["target"])
            self.assertEqual(len(restored["history"]), 1)
            late = self.accepted()
            late["verified_at"] = "2026-10-18T07:00:01Z"
            clock.now.return_value = datetime(2026, 10, 18, 7, 1, tzinfo=UTC)
            second = tick(gh, plan, "candidate", late, once=True)
            self.assertEqual(second["deferrals"], 2)
            clock.now.return_value = datetime(2026, 10, 19, 6, 59, tzinfo=UTC)
            tick(gh, plan, "candidate", late, once=True)
            self.assertEqual(gh.publications, 0)
            clock.now.return_value = datetime(2026, 10, 19, 7, tzinfo=UTC)
            published = tick(gh, plan, "candidate", late, once=True)
            self.assertTrue(published["published"])
            self.assertEqual(gh.saved["tag_name"], "v2.1.0")
            self.assertEqual(gh.main, "candidate")
            tick(gh, plan, "candidate", late, once=True)
            self.assertEqual(gh.publications, 1)
            saved = json.loads(gh.bytes["release-state.json"])
            self.assertEqual(len(saved["history"]), 2)
            self.assertTrue(saved["published"])
            self.assertEqual(gh.saved["name"], "Big Research v2.1.0")

    def test_dirty_checkout_never_mutates_github(self):
        github = Mock()
        with patch("release.subprocess.run", return_value=Mock(stdout=b" M README.md\0")):
            with self.assertRaisesRegex(RuntimeError, "clean"):
                prepare(github, {"version": "2.1.0"}, "candidate", Path("unused"))
            with self.assertRaisesRegex(RuntimeError, "clean"):
                tick(github, {"version": "2.1.0"}, "candidate", {})
        github.assert_not_called()
        self.assertEqual(github.mock_calls, [])

    def accepted(self):
        return {
            "verified_at": "2026-10-16T06:30:00Z",
            "content_sha256": "digest",
            "checks": dict.fromkeys(REQUIRED_CHECKS, True),
            "evidence": dict.fromkeys(REQUIRED_CHECKS, "A concrete verification record"),
        }

    def test_all_named_gates_evidence_and_exact_content_are_required(self):
        gh = FakeGitHub()
        record = self.accepted()
        self.assertTrue(readiness(gh, "candidate", record, "CI", "digest")[0])
        record["checks"] = {"anything": True}
        self.assertFalse(readiness(gh, "candidate", record, "CI", "digest")[0])
        record = self.accepted()
        self.assertFalse(readiness(gh, "candidate", record, "CI", "different-content")[0])
        record["evidence"] = {}
        self.assertFalse(readiness(gh, "candidate", record, "CI", "digest")[0])

    def test_latest_failed_ci_and_wrong_sha_cannot_reuse_success(self):
        gh = FakeGitHub()
        self.assertFalse(readiness(gh, "different-sha", self.accepted(), "CI", "digest")[0])
        gh.runs.append({**gh.runs[0], "id": 2, "conclusion": "failure"})
        self.assertFalse(readiness(gh, "candidate", self.accepted(), "CI", "digest")[0])

    def test_existing_tag_is_immutable_and_annotated_tags_are_checked(self):
        gh = FakeGitHub()
        check_tag(gh, "v2.1.0", "candidate")
        gh.tag = [{"ref": "refs/tags/v2.1.0", "object": {"type": "commit", "sha": "old-source"}}]
        with self.assertRaises(RuntimeError):
            check_tag(gh, "v2.1.0", "candidate")
        gh.tag[0]["object"] = {"type": "tag", "sha": "annotated"}
        check_tag(gh, "v2.1.0", "candidate")
