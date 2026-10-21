"""JSON CLI for the same workspace operations exposed through MCP."""

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__
from .core import Project, WorkflowError, methods, read_json
from .migration import migrate
from .review import profiles, template


def main() -> int:
    parser = argparse.ArgumentParser(description="Big-Research: human-led inquiry with traceable records")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("methods")
    sub.add_parser("doctor")
    sub.add_parser("review-profiles")
    review = sub.add_parser("review-template")
    review.add_argument("--method", action="append", default=[])
    review.add_argument("--profile", action="append", default=[])
    start = sub.add_parser("start")
    start.add_argument("project")
    start.add_argument("--title", required=True)
    start.add_argument("--field", default="")
    start.add_argument("--paradigm", default="")
    start.add_argument("--method", action="append", default=[])
    for name in ("status", "check", "assess", "export", "configure", "task-add", "task-update", "record"):
        command = sub.add_parser(name)
        command.add_argument("project")
        if name in {"configure", "task-add", "task-update", "record"}:
            command.add_argument("--file", required=True, help="Explicit JSON input file")
        if name == "task-update":
            command.add_argument("--id", required=True)
            command.add_argument("--revision", type=int)
        if name == "record":
            command.add_argument(
                "--kind",
                required=True,
                choices=["evidence", "claim", "decision", "concern", "candidate", "method_review", "review"],
            )
        if name == "export":
            command.add_argument(
                "--output", default="artifacts/workspace.html", help="Relative project path, never overwritten"
            )
    imp = sub.add_parser("migrate")
    imp.add_argument("source")
    imp.add_argument("destination")
    args = parser.parse_args()
    try:
        if args.command == "methods":
            result = methods()
        elif args.command == "review-profiles":
            result = profiles()
        elif args.command == "review-template":
            result = template(args.method, args.profile)
        elif args.command == "doctor":
            result = {
                "version": __version__,
                "python": sys.version.split()[0],
                "uv_available": bool(shutil.which("uv")),
                "storage": "local files",
                "model_or_search_included": False,
            }
        elif args.command == "start":
            result = Project.create(
                args.project, args.title, field=args.field, paradigm=args.paradigm, method_ids=args.method
            ).status()
        elif args.command == "migrate":
            result = migrate(args.source, args.destination).status()
        else:
            project = Project(args.project)
            payload = read_json(Path(args.file)) if hasattr(args, "file") else None
            if args.command == "status":
                result = project.status()
            elif args.command == "check":
                result = project.validate()
            elif args.command == "assess":
                result = project.assess()
            elif args.command == "export":
                result = {"path": project.export(args.output)}
            elif args.command == "configure":
                result = project.configure(**payload)
            elif args.command == "task-add":
                result = project.add_task(payload)
            elif args.command == "task-update":
                result = project.update_task(args.id, payload, args.revision)
            else:
                result = getattr(project, "record_" + args.kind)(payload)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (WorkflowError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
