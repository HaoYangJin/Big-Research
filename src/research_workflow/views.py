"""Self-contained workspace export and optional MCP Apps resource."""

import json
from importlib.resources import files


def render(snapshot: dict | None = None, *, interactive: bool = False) -> str:
    template = files("research_workflow").joinpath("workspace.html").read_text(encoding="utf-8")
    data = (
        json.dumps(snapshot or {}, ensure_ascii=True, allow_nan=False).replace("<", "\\u003c").replace("&", "\\u0026")
    )
    bridge = files("research_workflow").joinpath("bridge.js").read_text(encoding="utf-8") if interactive else ""
    return template.replace("/*WORKSPACE_DATA*/{}", data).replace("/*MCP_BRIDGE*/", bridge)
