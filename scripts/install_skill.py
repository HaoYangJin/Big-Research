#!/usr/bin/env python3
"""Copy the standalone skill to an explicit destination without overwriting files."""
import argparse
from pathlib import Path
import shutil
import sys


def install(target):
    source = Path(__file__).resolve().parents[1] / "skills/research-mentor"
    target = Path(target).expanduser().absolute()
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Destination exists; review/back up the old skill first: {target}")
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"Installed standalone skill: {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Exact destination skill folder")
    try:
        install(parser.parse_args().target)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
