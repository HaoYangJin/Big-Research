# Maintainer guide

Big Research is an independent third-party plugin. Client-compatible manifests and `agents/openai.yaml` metadata enable installation and skill discovery; they do not imply platform ownership, endorsement or directory approval.

## Local checks

```shell
uv sync --frozen
npm ci
npm run build
uv run ruff check src tests scripts
uv run coverage run -m unittest discover -s tests -v
uv run coverage report
uv run python scripts/check_ui.py
uv run python scripts/validate_repo.py
uv run python scripts/build_release.py --output dist
```

Use existing dependencies when available. Browser checks require Playwright Chromium. The CI matrix verifies Windows, Linux and macOS; isolated client installation checks run on disposable runners.

## Runtime boundaries

The shared Python package provides storage, task dependencies, evidence, migration, review profiles and views. CLI and MCP use the same logic. Project data uses schema version 2. Project writes are locked and atomic; dependent tasks and assessments must be revisited when their inputs change.

MCP project names are confined to `BIG_RESEARCH_HOME`, defaulting to `~/Big-Research`. CLI paths are explicit. Research records are not execution permissions or scientific certification.

## Distribution

Keep versions consistent, pass CI for the exact commit, and build the allowlisted archive with its checksums. Publish a new version rather than replacing an existing tag or release. Maintainer notes, test fixtures and research data do not belong in the installation package.

[Source history](history.md) · [Changes](CHANGELOG.md)
