"""Run three small research loops with actual outputs and explicitly bounded interpretations."""

from __future__ import annotations

import argparse
import platform
import shutil
import statistics
from pathlib import Path

from research_workflow.core import NAVIGATION, Project, atomic_json
from research_workflow.review import template

CONSTITUTION_URL = "https://www.archives.gov/founding-docs/constitution-transcript"
PASSAGES = {
    "Article I, Section 1": "All legislative Powers herein granted shall be vested in a Congress of the United States, which shall consist of a Senate and House of Representatives.",
    "Article II, Section 1, opening sentence": "The executive Power shall be vested in a President of the United States of America.",
}


def write(project: Project, name: str, text: str) -> str:
    relative = "artifacts/" + name
    (project.root / relative).write_text(text, encoding="utf-8")
    return relative


def study(root: Path, kind: str) -> Project:
    module = {"computational": "quantitative", "interpretive": "interpretive", "formal": "formal"}[kind]
    question = {
        "computational": "Does adding a linear trend improve mean squared prediction error in two deterministic synthetic cases?",
        "interpretive": "How do two constitutional vesting clauses frame institutional authority?",
        "formal": "Why does the sum of the first n positive integers equal n(n+1)/2?",
    }[kind]
    project = Project.create(
        root / kind,
        question,
        field={"computational": "computing", "interpretive": "humanities", "formal": "mathematics"}[kind],
        paradigm=module,
        method_ids=[module],
    )
    source = write(
        project,
        "question.md",
        f"# Question\n\n{question}\n\nA teaching example with bounded material, not a novelty claim.\n",
    )
    write(
        project,
        "protocol.md",
        "# Protocol\n\nKeep all cases and outputs. Do not infer a population result from a synthetic construction, a historical intention from two excerpts, or a universal theorem from finite calculations.\n",
    )
    shutil.copyfile(Path(__file__), project.root / "artifacts/example_source.py")
    if kind == "computational":
        rows = []
        for scenario in ("constant", "linear"):
            values = [2.0 if scenario == "constant" else 2.0 + i for i in range(10)]
            training, actual = values[:5], values[5:]
            static = [statistics.fmean(training)] * 5
            slope = (training[-1] - training[0]) / 4
            trend = [training[-1] + slope * i for i in range(1, 6)]
            rows.append(
                {
                    "scenario": scenario,
                    "static_mse": statistics.fmean((a - b) ** 2 for a, b in zip(actual, static, strict=True)),
                    "trend_mse": statistics.fmean((a - b) ** 2 for a, b in zip(actual, trend, strict=True)),
                }
            )
        atomic_json(
            project.root / "artifacts/results.json",
            {
                "observations": rows,
                "uncertainty": "Deterministic construction; no population or statistical uncertainty estimated.",
            },
        )
        finding = "In the constructed constant case both predictors have zero MSE: the proposed trend adds no benefit. In the constructed linear case the trend predictor has zero MSE, while the static predictor does not. This is a construction, not evidence of general forecasting superiority."
        project.record_evidence(
            {
                "id": "E1",
                "kind": "run",
                "title": "Two actually computed synthetic cases",
                "status": "executed",
                "command": "uv run python examples/run_examples.py --out NEW_DIRECTORY",
                "environment": f"Python {platform.python_version()}, {platform.system()}, standard library",
                "seed": None,
                "artifacts": [{"path": "artifacts/results.json"}, {"path": "artifacts/example_source.py"}],
            }
        )
        evidence = "E1"
    elif kind == "interpretive":
        corpus = write(
            project,
            "corpus.md",
            "# Public-domain primary text\n\nSource: "
            + CONSTITUTION_URL
            + "\nInspected 2026-10-17. Original 1787 wording; selected excerpts, not a complete constitutional or legal analysis.\n\n"
            + "\n\n".join(f"## {locator}\n{text}" for locator, text in PASSAGES.items()),
        )
        project.record_evidence(
            {
                "id": "S1",
                "kind": "source",
                "title": "Two 1787 vesting-clause excerpts",
                "path": corpus,
                "status": "verified",
                "accessed": "2026-10-17",
                "locator": "Article I section 1 and Article II section 1 opening sentence",
                "original_url": CONSTITUTION_URL,
                "license": "Original 1787 public-domain text; no modern editorial commentary copied",
            }
        )
        finding = "Both excerpts use 'shall be vested' to assign authority to an institution. Article I explicitly divides Congress into two chambers; the quoted Article II sentence names a President. A rival reading stresses that these excerpts alone omit checks and distributions elsewhere. Wording supports a local textual contrast, not a claim about actual historical power, authors' intentions or modern constitutional doctrine."
        note = write(project, "analytic-memo.md", finding)
        project.record_evidence(
            {
                "id": "A1",
                "kind": "interpretation",
                "title": "Close-reading memo and rival interpretation",
                "status": "documented",
                "path": note,
                "source_ids": ["S1"],
            }
        )
        evidence = "S1"
    else:
        proof = write(
            project,
            "proof.md",
            "# Induction argument\n\nClaim: for integers n >= 1, S(n)=sum(k=1..n) k = n(n+1)/2.\nBase n=1: 1=1(2)/2.\nAssume S(n)=n(n+1)/2. Then S(n+1)=S(n)+(n+1)=n(n+1)/2+2(n+1)/2=(n+1)(n+2)/2.\nBy induction the identity holds for all positive integers. For n=0 the empty sum also agrees. Negative n is outside this definition.\nAudit: the inductive hypothesis is used only for n, the added term is n+1, and the conclusion is the formula at n+1.\n",
        )
        checks = {str(n): sum(range(1, n + 1)) == n * (n + 1) // 2 for n in (0, 1, 2, 10, 100)}
        atomic_json(
            project.root / "artifacts/illustrative-checks.json", {"checks": checks, "proves_universal_claim": False}
        )
        project.record_evidence(
            {"id": "P1", "kind": "proof", "title": "Explicit induction argument", "status": "documented", "path": proof}
        )
        finding = "The induction argument establishes the stated identity under its integer-domain assumptions. Finite numerical checks illustrate the result and are not its proof. This is a known mathematical identity, not a novel contribution."
        evidence = "P1"
    project.record_claim(
        {
            "id": "C1",
            "text": finding,
            "status": "supported",
            "supports": [evidence],
            "contradicts": [],
            "limits": "Teaching example only; no novelty or general empirical effect claimed",
        }
    )
    draft = write(
        project,
        "draft.md",
        "# Bounded findings\n\n" + finding + "\n\nInitial draft: the claim is limited to the documented materials.\n",
    )
    project.record_concern(
        {"id": "R1", "text": "Make the scope and alternative interpretation explicit in the abstract", "status": "open"}
    )
    revision = write(
        project,
        "revision.md",
        "# Revision and response\n\nR1: explicitly restrict the conclusion to the selected materials/assumptions.\n\n"
        + finding
        + "\n\nThis exercise does not claim expert validation, novelty or publication readiness.\n",
    )
    project.record_concern(
        {
            "id": "R1",
            "text": "Make the scope explicit",
            "status": "resolved",
            "resolution": "artifacts/revision.md explicitly states scope and remaining limitations",
        }
    )
    for task_id, _ in NAVIGATION:
        output = (
            source
            if task_id == "frame"
            else (
                "artifacts/protocol.md"
                if task_id in {"map", "design"}
                else draft
                if task_id == "investigate"
                else revision
            )
        )
        project.update_task(
            task_id,
            {
                "status": "complete",
                "summary": "Actual teaching artifact produced; see its explicitly bounded claim",
                "outputs": [output],
                "evidence": ["C1"],
            },
        )
    report = template([module])
    report.update(
        id="review-1",
        summary="Bounded teaching-example assessment; no independent expert or human approval implied",
        coverage={
            "reviewed": 1,
            "total": 1,
            "selection": "All generated teaching artifacts; no external full literature review",
        },
        confidence={"level": "low", "reason": "Scripted teaching assessment, not independent subject-matter review"},
    )
    for criterion in report["criteria"].values():
        criterion.update(
            verdict="not_assessable",
            reason="The generated teaching exercise does not establish this broader quality judgment",
            locators=[],
        )
    project.record_review(report)
    write(
        project,
        "review.md",
        "# Review\n\nScope concern R1 was addressed in revision.md. The layered review remains explicitly limited and uncalibrated; no script records a researcher confirmation.\n",
    )
    project.export()
    assert project.validate()["structural_valid"]
    assert not project.assess()["researcher_confirmed"]
    return project


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("Choose an unused output directory")
    for kind in ("computational", "interpretive", "formal"):
        project = study(args.out, kind)
        print(f"{kind}: {project.root} (record integrity passed; researcher confirmation absent)")


if __name__ == "__main__":
    main()
