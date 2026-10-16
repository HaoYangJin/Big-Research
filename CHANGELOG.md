# Changelog

## 1.1.0 — 2026-10-16

- Fix crash-held locks using OS advisory locking.
- Add persisted manual/automatic mode routing and history.
- Add validated v1.0.0 migration with a preserved backup.
- Deliver compact action cards and evidence-based, direction-supporting guidance; strict audit on request.
- Remove duplicate root skill discovery; include guides in plugin archives.
- Add bilingual READMEs, visual onboarding and Star History.

See [release notes](docs/RELEASE-v1.1.0.md) and [validation](docs/validation-v1.1.0.md).


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation

- Document tested Codex CLI plugin installation, separate desktop and workspace-cloud Work routes, and multi-turn conversations for all three modes.
- Publish a v1.0.0 limitations assessment, including a reproduced orphan-lock defect, mode persistence gaps, scientific-validation boundaries, and remaining host acceptance work.
- Add a task-based README entry, a rendered Mermaid usage flow, and a step-by-step Chinese guide covering the local demo, host installation, research deliverables, and checkpoint recovery.
- Clarify the separate roles of the host agent, synthetic experiment, and state CLI, with copyable prompts and observable completion criteria.

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

