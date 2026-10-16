# Research Workflow

[简体中文](README.md) · [English](README.en.md) · [Changelog](CHANGELOG.md)

![Version](https://img.shields.io/badge/version-1.1.0-blue)

**A research mentor and reviewer plugin that turns your current task into concrete actions, evidence and resumable progress.**

## Install and start

In Claude Code:

```text
/plugin marketplace add HaoYangJin/Research-workflow-Skill
/plugin install research-workflow@research-workflow-marketplace
/research-workflow:research-mentor
Help me design a low-cost experiment on time-series drift using synthetic data and Python's standard library. Start with three actions.
```

For Codex CLI:

```bash
codex plugin marketplace add HaoYangJin/Research-workflow-Skill --ref v1.1.0
codex plugin add research-workflow@research-workflow-marketplace
```

Start a new session and invoke `$research-mentor`. See [installation details](USAGE.md) and [platform verification scope](docs/openai-install.md). The previous Codex 0.163.0 installation check does not establish end-to-end validation of this release in desktop/cloud clients.

## Three modes, automatic by default

| Mentor | Mixed | Reviewer |
| --- | --- | --- |
| Plan and learn | Advance and inspect | Review supplied work |
| Goal, action, success check | Two short perspectives, shared actions | Evidence, repair, verification |

Say “mentor mode”, “mixed mode”, “reviewer mode” or “automatic” at any time. Current instructions override saved defaults; project preferences and phase guide routing when intent is unclear. Platforms with choice controls may show a selector; others use a text strip. Persistent projects store the selection and history. Without storage, memory is limited to the current conversation.

Responses use compact task cards. Guidance follows your feasible research direction and proposes small tests instead of rejecting uncertain ideas. Only evidenced principle or methodology errors block progress. Explicit strict-audit requests expand the review to the full pipeline and bounded reproduction; missing data, code or configuration is requested specifically. Reading code alone is never described as a reproduced result.

## Coverage

Scope/literature → hypotheses → design → reproducibility → results/ablations → drafting → review → revision → submission readiness. Short questions use only the relevant phase. Long projects track artifacts, evidence and checkpoints.

v1.1.0 fixes crash-held locks, adds persisted mode selection and automatic phase routing, migrates v1.0.0 projects with a backup, removes duplicate skill discovery, and includes guides in plugin archives. See [release notes](docs/RELEASE-v1.1.0.md) and [validation](docs/validation-v1.1.0.md).

## Local workflow

Python 3.10+, standard library only:

```bash
python skills/research-mentor/scripts/workflow.py init /tmp/my-study --title "My question"
python skills/research-mentor/scripts/workflow.py mode /tmp/my-study --select auto --task review
python skills/research-mentor/scripts/workflow.py status /tmp/my-study
python skills/research-mentor/scripts/workflow.py migrate /path/to/v1-project
```

Migration validates old checkpoints, saves `project.v1.0.0.backup.json`, and preserves the old mode as a manual preference. Stop all old writers before upgrading. OS locks recover automatically on process exit; do not delete lock files. Only a single machine and local filesystem are supported.

The plugin distributes the canonical `skills/research-mentor/` implementation. The repository URL and plugin name remain stable. Standalone skill installation remains available; avoid enabling both copies. [Repository structure and references](docs/repository-design.md).

Search and execution require tools in the AI client. The CLI validates structure and hashes, not scientific truth or publication acceptance. See the [reproducible example](examples/drift-study/README.md), [guided tutorial](docs/quickstart.md) and [contributing guide](CONTRIBUTING.md).

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=HaoYangJin/Research-workflow-Skill&type=Date)](https://www.star-history.com/#HaoYangJin/Research-workflow-Skill&Date)

This live third-party chart may be unavailable due to service or API limits. MIT; see [LICENSE](LICENSE).
