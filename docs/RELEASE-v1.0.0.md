# Research Workflow v1.0.0

从只给科研建议的 Skill 升级为带真实产物、证据关联和可恢复检查点的科研插件。保留九阶段和 mentor / reviewer / mixed 模式。

## Added

- Claude Code plugin + marketplace and Codex plugin manifests sharing one canonical skill.
- Dependency-free Python 3.10+ project lifecycle CLI: init, template, status, checkpoint, validate, reopen.
- Evidence ledger for verified/unverified sources, executed/planned/failed experiments, and bounded claims.
- Checkpoint/output SHA-256 integrity checks, downstream invalidation, blocking states, and submission-readiness gates.
- Capability adapters for host-provided search, papers, execution, files, Git, and export, with explicit unavailable-tool fallback.
- Portable installer, deterministic allowlisted release packages, CI, and regression tests.

## Fixed

- Explicit mode precedence and literature-review/quoted-reviewer ambiguity.
- Replaced author-specific Windows paths with portable installation.
- Separated missing information from confirmed scientific errors, simulated viewpoints from independent peer review, and structural checks from scientific validation.
- Added source verification, pre-experiment protocol, negative-result reporting, synthetic-study limits, and honest blocked/not-ready outcomes.

## Migration

Canonical skill files now live in `skills/research-mentor/`. Root `SKILL.md` is a compatibility entry. Back up old installations and install only the canonical skill or the plugin. There was no project-state schema in 0.1.0.

## Validation and limits

See [the validation report](https://github.com/HaoYangJin/Research-workflow-Skill/blob/main/docs/validation-v1.0.0.md) for actual runs and observed checks. No real manuscript was submitted. The release does not certify scientific correctness, publication acceptance, official directory approval, or every possible host configuration. Optional service adapters are contracts, not bundled authenticated integrations.
