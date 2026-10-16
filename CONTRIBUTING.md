# Help make research assistance work for more people

Thank you for helping researchers pursue better questions and more defensible work. Useful contributions include a missing method, a carefully documented case, a clearer explanation, a translation or a reproducible bug report.

## Start with a research need

Explain who needs the change, the actual task, the current difficulty and an observable improvement. For methods, state the paradigm and applicability: a useful standard in one tradition may be inappropriate in another. Link primary guidance and disclose limitations. Do not use prestige, publication counts or unsupported AI performance claims as evidence of quality.

## Contribute a method or review profile

Method definitions live in the shared package's methods.json; review overlays live in review_profiles.json. Include applicability, inputs, outputs, checks, guidance, optional tools and primary references. Distinguish reporting guidance, venue review, artifact evaluation and system-reference evidence. Use independently written text and compatible licenses; include provenance for reused files.

Keep universal workflow instructions short. Add a specialist Skill only when it serves a distinct recurring task. New modules should not force unrelated work to load their references or dependencies.

## Contribute a case

Use public, licensed or synthetic materials. Include the question, process, commands where applicable, actual outputs, bounded conclusions, review and revision. Preserve negative results. Do not include private datasets, identifiable participants, API credentials or confidential manuscripts.

## Check a change

```text
uv sync --frozen
npm ci
npm run build
uv run coverage run -m unittest discover -s tests -v
uv run coverage report
uv run python scripts/validate_repo.py
uv run python scripts/build_release.py --output dist
```

Run relevant example and UI checks too; see [development guide](docs/development.md). Open a focused pull request explaining the research need, change, actual validation and remaining limits. Historical executors and old command aliases must not return to the current runtime.
