# Contributing

Keep changes practical, evidence-aware, and domain-agnostic. 保持简体中文优先的阶段参考；公开安装和使用说明保持中英双语。

## Source layout

- Edit the canonical skill under `skills/research-mentor/`; root `SKILL.md` is only a legacy entry.
- Keep the main skill concise; add phase details or provider contracts to its references.
- Change CLI behavior with meaningful lifecycle/evidence regression coverage.
- Keep all release versions consistent with `VERSION`, both plugin manifests, the marketplace entry, CLI, and release documentation.
- Never commit private drafts, unpublished reviewer comments, credentials, copyrighted paper bodies, or real research data without authorization. Synthetic public demonstrations must be labeled and reproducible.

## Required checks

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s examples/drift-study -p test_experiment.py -v
python scripts/validate_repo.py
python scripts/build_release.py --output dist
claude plugin validate .claude-plugin/plugin.json --strict
claude plugin validate .claude-plugin/marketplace.json --strict
```

Read changed Markdown in a rendered viewer. For substantial skill behavior changes, run a realistic isolated task and preserve a concise public validation summary; do not pass the intended answer to a forward-testing agent. Distinguish static checks, actual host installation, scientific assessment, and untested capabilities.

## Main-only maintenance

This repository is maintained directly on `main`. Do not create routine `feature/*` or `codex-*` maintenance branches. Keep maintenance logs, snapshots, temporary drafts, project state, and local sessions out of version control. The tagged release workflow builds allowlisted packages and publishes assets only after validation. Do not force-push over concurrent work or move an existing release tag.

## Change descriptions

Explain the concrete workflow problem, resulting behavior, and validation. Identify behavior/routing changes and include a realistic prompt when relevant. Report unresolved limitations rather than claiming a successful experiment, host import, or submission that was not performed.
