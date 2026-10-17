"""Local MCP adapter. All project names are confined to one configured research home."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .core import Project, inside, methods, require
from .migration import migrate
from .review import profiles, template
from .views import render

UI_URI = "ui://research-workflow/workspace.html"
READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False)


def make_server(home: Path | None = None) -> FastMCP:
    base = (
        (home or Path(os.environ.get("RESEARCH_WORKFLOW_HOME", Path.home() / "Research-Workflow")))
        .expanduser()
        .resolve()
    )
    mcp = FastMCP(
        "Big Research",
        instructions="Human-led research. Records and integrity checks do not certify scientific truth. Project arguments are names relative to the explicitly configured research home. No tool executes commands or uploads research.",
    )

    def project_path(name: str) -> Path:
        path = inside(base, name)
        require(not any(part.startswith(".") for part in Path(name).parts), "Use a visible research project name")
        return path

    def snapshot(name: str) -> dict[str, Any]:
        return {**Project(project_path(name)).status(), "workspace": name}

    @mcp.resource(
        UI_URI,
        mime_type="text/html;profile=mcp-app",
        meta={"ui": {"csp": {"connectDomains": [], "resourceDomains": []}}},
    )
    def workspace_view() -> str:
        """Research map, evidence browser, candidate comparison and decisions."""
        return render(interactive=True)

    @mcp.tool(structured_output=True, annotations=READ)
    def method_catalog() -> dict[str, Any]:
        """Read available method guidance; choose by paradigm, never infer a method from discipline alone."""
        return methods()

    @mcp.tool(structured_output=True, annotations=READ)
    def review_catalog() -> dict[str, Any]:
        """Read source-backed review/reporting profiles and their applicability limits."""
        return profiles()

    @mcp.tool(structured_output=True, annotations=READ)
    def review_template(method_ids: list[str] | None = None, profile_ids: list[str] | None = None) -> dict[str, Any]:
        """Build a layered qualitative review scaffold; not an official checklist or calibrated score."""
        return template(method_ids, profile_ids)

    @mcp.tool(structured_output=True, annotations=WRITE, meta={"ui": {"resourceUri": UI_URI}})
    def workspace_create(
        project: str, title: str, field: str = "", paradigm: str = "", method_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """Create a named project in an empty directory under the configured research home. Never overwrites."""
        Project.create(project_path(project), title, field=field, paradigm=paradigm, method_ids=method_ids)
        return snapshot(project)

    @mcp.tool(structured_output=True, annotations=READ, meta={"ui": {"resourceUri": UI_URI}})
    def workspace_open(project: str) -> dict[str, Any]:
        """Open an existing current-format research project and its optional interactive workspace."""
        return snapshot(project)

    @mcp.tool(structured_output=True, annotations=READ, meta={"ui": {"resourceUri": UI_URI}})
    def workspace_status(project: str) -> dict[str, Any]:
        """Read current records, available next tasks, pending decisions and file integrity."""
        return snapshot(project)

    @mcp.tool(structured_output=True, annotations=WRITE)
    def workspace_update(
        project: str, action: str, payload: dict, task_id: str = "", expected_revision: int | None = None
    ) -> dict[str, Any]:
        """Configure project metadata, add_task, or update_task. Updates invalidate affected dependent work."""
        selected = Project(project_path(project))
        if action == "configure":
            selected.configure(**payload)
        elif action == "add_task":
            selected.add_task(payload)
        else:
            require(action == "update_task", "Choose configure, add_task or update_task")
            selected.update_task(task_id, payload, expected_revision)
        return snapshot(project)

    @mcp.tool(structured_output=True, annotations=WRITE)
    def workspace_record(project: str, kind: str, record: dict) -> dict[str, Any]:
        """Record evidence, claim, decision, concern, candidate or method_review. Confirmed decisions must quote the researcher's actual choice; do not self-approve."""
        require(
            kind in {"evidence", "claim", "decision", "concern", "candidate", "method_review", "review"},
            "Unknown record kind",
        )
        getattr(Project(project_path(project)), "record_" + kind)(record)
        return snapshot(project)

    @mcp.tool(structured_output=True, annotations=READ)
    def workspace_assess(project: str) -> dict[str, Any]:
        """Separate record integrity, method-review coverage, researcher statements, unresolved concerns and budget."""
        return Project(project_path(project)).assess()

    @mcp.tool(structured_output=True, annotations=WRITE)
    def workspace_export(project: str, output: str = "artifacts/workspace.html") -> dict[str, Any]:
        """Export a read-only HTML workspace or JSON snapshot inside the project, without overwriting."""
        return {"path": Project(project_path(project)).export(output)}

    @mcp.tool(structured_output=True, annotations=WRITE)
    def workspace_migrate(source: str, destination: str) -> dict[str, Any]:
        """Import known v1 project data into a new named project. Both names are confined to the research home; source is preserved."""
        migrate(project_path(source), project_path(destination))
        return snapshot(destination)

    return mcp


def main() -> None:
    make_server().run(transport="stdio")


if __name__ == "__main__":
    main()
