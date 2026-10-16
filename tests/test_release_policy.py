import unittest
from datetime import UTC, datetime

from research_workflow.release_policy import advance, release_action


class ReleasePolicyTests(unittest.TestCase):
    def test_daily_deferral_is_unlimited_and_fixed_pdt(self):
        state = {"target": "2026-10-17T07:00:00+00:00", "deferrals": 0, "published": False}
        for _ in range(40):
            state = advance(state, "Acceptance incomplete")
        self.assertEqual(state["deferrals"], 40)
        self.assertTrue(state["target"].endswith("07:00:00+00:00"))
        self.assertEqual(len(state["history"]), 40)

    def test_no_early_or_duplicate_release_and_late_readiness_waits(self):
        state = {"target": "2026-10-17T07:00:00+00:00", "published": False}
        before = datetime(2026, 10, 17, 6, 50, tzinfo=UTC)
        self.assertEqual(release_action(state, before, True, "2026-10-17T06:40:00+00:00"), "wait")
        after = datetime(2026, 10, 17, 7, 1, tzinfo=UTC)
        self.assertEqual(release_action(state, after, True, "2026-10-17T06:40:00+00:00"), "publish")
        self.assertEqual(release_action(state, after, True, "2026-10-17T07:00:01+00:00"), "defer")
        self.assertEqual(release_action(state, after, False, None), "defer")
        self.assertEqual(release_action({**state, "published": True}, after, True, None), "published")
