import unittest

from research_workflow.core import WorkflowError
from research_workflow.review import profiles, template, validate_review


class ReviewTests(unittest.TestCase):
    def test_no_venue_still_has_method_appropriate_criteria(self):
        report = template(["interpretive"])
        self.assertIn("method:interpretive/rival_readings", report["criteria"])
        self.assertNotIn("method:quantitative/uncertainty_and_sensitivity", report["criteria"])
        self.assertIn("core/evidence_and_argument", report["criteria"])
        self.assertIsNone(report["numeric_total"])

    def test_reporting_guidance_is_not_an_acceptance_score(self):
        self.assertEqual(profiles()["medical-reporting"]["kind"], "reporting_guidance")
        report = template(["qualitative"], ["apa-jars"])
        report.update(
            id="review-1",
            summary="Bounded assessment",
            coverage={"reviewed": 2, "total": 5, "selection": "Only supplied sections"},
            confidence={"level": "low", "reason": "Methods section unavailable"},
        )
        for criterion in report["criteria"].values():
            criterion["reason"] = "Not enough supplied material to assess"
        validate_review(report)
        report["numeric_total"] = 8
        with self.assertRaises(WorkflowError):
            validate_review(report)

    def test_judgments_require_locations_and_missing_is_not_defect(self):
        report = template()
        report.update(
            summary="Review",
            coverage={"reviewed": 1, "total": 1, "selection": "Whole supplied excerpt"},
            confidence={"level": "low", "reason": "Excerpt only"},
        )
        for criterion in report["criteria"].values():
            criterion.update(verdict="needs_work", reason="A demonstrable inconsistency")
        with self.assertRaises(WorkflowError):
            validate_review(report)
        for criterion in report["criteria"].values():
            criterion["locators"] = ["artifacts/draft.md, paragraph 2"]
        validate_review(report)
