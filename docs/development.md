# Development

The shared package contains project storage, task dependencies, evidence, migration, review profiles and views. CLI and MCP are adapters over that package. Skills explain when and how to combine these capabilities. There is no historical executor in the current source tree.

Install locked dependencies with `uv sync --frozen` and `npm ci`. Build the bundled UI with `npm run build`. Run `uv run coverage run -m unittest discover -s tests -v`, `uv run coverage report`, `uv run python scripts/validate_repo.py`, and the examples described in their README. Browser tests use the installed Playwright Chromium; install it with `uv run playwright install chromium`.

Project data is schema version 2. Fields and paradigms are free text; methods refer to the bundled registry. Task dependencies form a directed acyclic graph. Mutations lock and atomically replace one project.json. Files/evidence used by completed tasks are snapshotted. Task/evidence edits invalidate affected work; method checks and researcher conclusions do not follow automatically from hashes.

MCP names are confined to RESEARCH_WORKFLOW_HOME (default ~/Research-Workflow); CLI paths are explicit. The UI uses structured content and the SDK bridge, with user content rendered as text. HTML exports have no active bridge.

For a release, use the guarded workflow rather than pushing a version number. Publication is bound to an exact candidate commit, required CI and acceptance checks. A persistent draft-release state records its target midnight, readiness and every daily deferral. See the release workflow and its unit-tested fixed-PDT policy.

Local verification on 2026-10-17: 31 tests passed and one symlink-creation test was skipped because Windows permission was unavailable; measured core/CLI coverage was 93%. Seven retained experiment checks, three runnable examples, real stdio MCP calls and browser/SDK interactions passed. Independent reviews prompted fixes for stale assessments, invalid saved updates, migration preservation, release identity and ignored-file packaging. The three-platform CI matrix and clean client installations also passed; see the [verification snapshot](compatibility.md). Publication still requires CI for the exact final candidate and its bound acceptance record.
