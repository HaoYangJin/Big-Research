"""Layered, source-backed review scaffolds. No uncalibrated cross-field total scores."""

import json
from importlib.resources import files

from .core import methods, nonempty, require

VERDICTS = {"adequate", "needs_work", "not_assessable", "not_applicable"}
BASE = [
    "question_and_value",
    "prior_work_and_context",
    "method_fit",
    "evidence_and_argument",
    "limitations_and_alternatives",
    "clarity_and_traceability",
    "ethics_and_disclosure",
]


def profiles() -> dict:
    return json.loads(files("big_research").joinpath("review_profiles.json").read_text(encoding="utf-8"))


def template(method_ids: list[str] | None = None, profile_ids: list[str] | None = None) -> dict:
    selected_methods, selected_profiles = method_ids or [], profile_ids or []
    require(all(m in methods() for m in selected_methods), "Unknown method")
    require(all(p in profiles() for p in selected_profiles), "Unknown review profile")
    criteria = {"core/" + key: {"verdict": "not_assessable", "reason": "", "locators": []} for key in BASE}
    for mid in selected_methods:
        for key in methods()[mid]["checks"]:
            criteria[f"method:{mid}/{key}"] = {"verdict": "not_assessable", "reason": "", "locators": []}
    for pid in selected_profiles:
        for key in profiles()[pid]["checks"]:
            criteria[f"profile:{pid}/{key}"] = {"verdict": "not_assessable", "reason": "", "locators": []}
    return {
        "methods": selected_methods,
        "profiles": selected_profiles,
        "summary": "",
        "strengths": [],
        "concerns": [],
        "coverage": {"reviewed": 0, "total": 0, "selection": ""},
        "confidence": {"level": "low", "reason": ""},
        "criteria": criteria,
        "calibration": "not_calibrated",
        "numeric_total": None,
        "note": "A working review scaffold, not an official form, complete reporting checklist, calibrated score or acceptance prediction.",
    }


def validate_review(record: dict) -> None:
    require(nonempty(record.get("summary")), "Review summary is required")
    expected = template(record.get("methods"), record.get("profiles"))
    require(
        set(record.get("criteria", {})) == set(expected["criteria"]),
        "Review must cover every selected criterion, with justified not_applicable where needed",
    )
    for criterion in record["criteria"].values():
        require(
            isinstance(criterion, dict) and criterion.get("verdict") in VERDICTS and nonempty(criterion.get("reason")),
            "Each criterion needs an explicit verdict and reason",
        )
        require(
            isinstance(criterion.get("locators"), list) and all(nonempty(v) for v in criterion["locators"]),
            "Locators must be a list of source/artifact positions",
        )
        if criterion["verdict"] in {"adequate", "needs_work"}:
            require(
                criterion["locators"],
                "Substantive judgments need evidence locations; missing materials are not a confirmed defect",
            )
    coverage = record.get("coverage", {})
    require(
        type(coverage.get("reviewed")) is int
        and type(coverage.get("total")) is int
        and 0 < coverage["total"]
        and 0 <= coverage["reviewed"] <= coverage["total"]
        and nonempty(coverage.get("selection")),
        "Declare reviewed/total coverage and selection limits",
    )
    confidence = record.get("confidence", {})
    require(
        confidence.get("level") in {"low", "medium", "high"} and nonempty(confidence.get("reason")),
        "Confidence needs a reason",
    )
    require(
        record.get("numeric_total") is None and record.get("calibration") == "not_calibrated",
        "This implementation has no validated scoring calibration; use reasoned criterion-level judgments",
    )
