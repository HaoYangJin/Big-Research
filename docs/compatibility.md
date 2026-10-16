# Compatibility and verification

The primary targets are local Codex and Claude Code. The full plugin needs uv and Python 3.11+. MCP uses the official Python SDK; the optional UI uses the official MCP Apps JavaScript SDK bundled into the resource. Node is needed for development builds, not by researchers running the packaged plugin.

| Capability | Verification |
| --- | --- |
| Shared Python core and CLI | Automated local tests; CI covers Windows, Linux and macOS |
| MCP tool schemas, stdio and resource | Real client/server integration tests |
| Read-only local HTML | Browser checks for navigation, filtering, provenance and escaped content |
| MCP Apps interaction | Protocol/browser checks; exact client support depends on its version |
| Claude manifest/import | Strict CLI validation and clean installation on a disposable CI runner |
| Codex manifest/import | Clean CLI installation on a disposable CI runner |
| Cloud-only execution | Not a complete local-MCP experience; use conversation-level skills only when supported |

This table describes the verification strategy, not an assertion that every client/account combination passed. The release acceptance record tracks completed checks; incomplete primary-client acceptance defers the formal release. Directory listing/approval is separate from the GitHub release.

Verification snapshot, 2026-10-17: [CI passed](https://github.com/HaoYangJin/Research-workflow-Skill/actions/runs/38936132580) on Windows, Linux and macOS with Python 3.11/3.14. Disposable Linux runners passed browser/SDK checks, Claude Code 2.1.301 strict manifest validation and clean installation, and Codex CLI 0.163.0 clean installation. These results cover the tested versions; native client UI support remains conditional.

Local state supports a single machine's filesystem with fail-fast writer locking. Shared/network filesystems and multi-machine coordination are not supported. Recorded commands are never executed by the workspace. Source inspection, scientific review and final research decisions remain with the researcher and available AI tools.
