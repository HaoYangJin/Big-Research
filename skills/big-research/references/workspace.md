# Current workspace operations

Resolve PLUGIN_ROOT from the installed plugin. Prefix every CLI command with `uv run --isolated --frozen --no-dev --project PLUGIN_ROOT big-research`.

| Goal | Command |
| --- | --- |
| Diagnose / methods | `doctor` / `methods` |
| Review profiles / scaffold | `review-profiles` / `review-template --method interpretive` |
| Start | `start PROJECT --title "Question" --field "History" --paradigm "Interpretive" --method interpretive` |
| Resume / check / assess | `status PROJECT` / `check PROJECT` / `assess PROJECT` |
| Configure | `configure PROJECT --file settings.json` |
| Add / update task | `task-add PROJECT --file task.json` / `task-update PROJECT --id frame --file update.json --revision N` |
| Record | `record PROJECT --kind evidence --file record.json` |
| Snapshot | `export PROJECT --output artifacts/workspace.html` |
| Import data | `migrate OLD_PROJECT NEW_DESTINATION` |

Write JSON inputs through file tools rather than shell interpolation. stdout is JSON; errors use stderr/nonzero status. All artifact paths are relative to the project. The workspace never executes a recorded command.

The default review has no venue overlay. Add `--profile public-humanities` only when that specific journal's guidance is relevant to the researcher's goal; it is not a default for humanities research.

Task input: `{"id":"archive","title":"Read materials","depends_on":[]}`. Update: `{"status":"complete","summary":"Bounded outcome","outputs":["artifacts/note.md"],"evidence":["S1"]}`. Completion needs actual files and completed dependencies; blocked/out_of_scope needs reason.

Source: `{"id":"S1","kind":"source","title":"Primary material","path":"artifacts/source.txt","status":"verified","accessed":"2026-10-17","locator":"paragraph 2"}`. Remote sources use url instead of path. Mark verified only after inspecting contents. Local file hashes are computed automatically.

Run: `{"id":"E1","kind":"run","title":"Pilot","status":"executed","command":"python experiment.py","environment":"Actual Python/OS/dependencies","seed":7,"artifacts":[{"path":"artifacts/results.json"},{"path":"artifacts/experiment.py"}]}`. Keep planned, failed and executed distinct. Other evidence kinds proof/corpus/analysis/interpretation use status documented and path/artifacts, or planned.

Claim: `{"id":"C1","text":"A bounded conclusion","status":"supported","supports":["S1"],"contradicts":[],"limits":"Supplied material only"}`. Direct evidence references only; eligibility does not certify semantic support.

Decision: `{"id":"D1","question":"Which approach?","status":"pending","options":["A","B"]}`. Confirm only the actual choice using choice and researcher_statement. Final conclusion decision uses id research-conclusion; records do not authenticate authorship or grant ethics approval.

Other record kinds: claim, decision, concern, candidate, method_review, review. Candidates need id/title/value/evidence/cost/feasibility. Concerns need id/text/status open or resolved plus resolution when resolved. Method reviews use an active module id and checks mapping every criterion to verdict adequate/needs_work/not_applicable plus reason. Layered reviews come from review-template; fill a unique id, reasons/locators, coverage and confidence.

Changed evidence or completed tasks invalidate linked work. Revisit affected tasks and re-record corrected evidence instead of editing hashes. Exports never overwrite existing files.
