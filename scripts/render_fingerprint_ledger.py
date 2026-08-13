#!/usr/bin/env python3
"""Print an AI-team change-set inventory and SHA-256 ledger without editing files."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


WORKFLOW_REVISION = "ai-team-2026-08-13-r35"


def render(project_root: Path, paths: list[str]) -> str:
    root = project_root.resolve()
    normalized: list[tuple[str, Path]] = []
    for raw in paths:
        candidate = Path(raw)
        if candidate.is_absolute():
            raise ValueError(f"path must be project-relative: {raw}")
        resolved = (root / candidate).resolve()
        try:
            relative = resolved.relative_to(root).as_posix()
        except ValueError as error:
            raise ValueError(f"path escapes project root: {raw}") from error
        if not resolved.is_file():
            raise ValueError(f"file not found: {raw}")
        normalized.append((relative, resolved))
    if not normalized:
        raise ValueError("at least one project-relative file is required")
    if len({relative for relative, _ in normalized}) != len(normalized):
        raise ValueError("duplicate file path")
    inventory = "; ".join(f"`{relative}`" for relative, _ in normalized)
    lines = [f"- Change-set file inventory: {inventory}", "- Current change-set fingerprint:"]
    lines.extend(
        f"  - `{relative}` = {hashlib.sha256(path.read_bytes()).hexdigest()}"
        for relative, path in normalized
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print matching AI-team inventory and fingerprint Markdown."
    )
    parser.add_argument("project_root", type=Path)
    parser.add_argument("paths", nargs="+", help="Project-relative files in the change set")
    args = parser.parse_args()
    try:
        print(render(args.project_root, args.paths), end="")
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
