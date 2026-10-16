# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-16

### Added

- Claude and Codex plugin manifests, a Claude-compatible marketplace, and one canonical `skills/research-mentor/` package.
- Dependency-free Python project initialization, checkpoints, integrity validation, blocked states, and downstream reopening.
- Source/experiment/claim evidence ledger, direct evidence snapshots, and bounded submission-readiness gates.
- Optional host capability adapters, a portable standalone installer, deterministic release packaging, CI, and regression tests.
- Real isolated research-loop validation with actual synthetic experiments, negative results, drafts, review, and revision.

### Changed

- Preserve root `SKILL.md` as a compatibility entry; move canonical references and examples into the skill.
- Apply explicit mode priority, ignore mode words in quotes/history, and distinguish literature review from peer review.
- Require real deliverables and evidence-aware handoffs; clarify structural validation versus scientific correctness.
- Replace personal Windows installation paths with portable commands and document host limitations.

### Migration

- Back up an old installation and install the canonical skill or plugin, not both. Version 0.1.0 had no persisted project schema.

## [0.1.0] - 2026-05-16

### Added

- Initial Anthropic-style `research-mentor` Skill with root `SKILL.md`.
- Nine research lifecycle reference files under `references/`.
- Chinese and English example invocations under `examples/`.
- Bilingual `README.md` and `USAGE.md`.
- MIT license, contributing guide, code of conduct, and general `.gitignore`.
