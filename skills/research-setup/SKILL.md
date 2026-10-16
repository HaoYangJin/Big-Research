---
name: research-setup
description: Set up Research Workflow, diagnose local prerequisites, choose a research home, or guide a researcher through a first saved project.
---

# Start a research workspace

Explain the mission briefly, then help produce a first useful result. Identify the goal, available materials and desired project location only when not already known.

The full local plugin needs uv and Python 3.11+; uv can provision compatible Python. MCP Apps UI support is optional. Search and inference come from the user's client; no model API key or Connected App is required by this plugin.

Resolve PLUGIN_ROOT from this skill's installed location: two parents above its containing skill folder. Run `uv run --isolated --frozen --no-dev --project PLUGIN_ROOT research-workflow doctor` and inspect actual MCP tools. Never invent an installation path.

The MCP research home defaults to ~/Research-Workflow. Configure RESEARCH_WORKFLOW_HOME in the client's MCP environment for another directory. Project names are relative to this home. CLI operations accept explicit paths for projects elsewhere. Do not scan arbitrary directories.

Offer guided or concise explanation. Select methods by paradigm and question, not discipline alone. Create persistent work only in an empty destination. Show its research map and deliver an actual first artifact or bounded plan. Without MCP, use the identical current CLI; without execution/storage, disclose that persistence is unavailable.

Only Latest is installed. Migrate pre-v2 data into a new directory; never run old Skills or executors. If an independently installed old skill remains in the user's client, explain how to remove that exact duplicate after preserving their data; do not delete unrelated skills.
