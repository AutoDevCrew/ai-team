#!/usr/bin/env python3
"""Print one Markdown H2 section while ignoring headings inside fenced code."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


def normalize_heading(value: str) -> str:
    normalized = re.sub(r"[^\w]+", " ", value.casefold(), flags=re.UNICODE)
    return re.sub(r"\s+", " ", normalized).strip()


def extract_h2_section(text: str, requested_heading: str) -> str | None:
    expected = normalize_heading(requested_heading.lstrip("# "))
    lines = text.splitlines(keepends=True)
    start: int | None = None
    fence_character: str | None = None
    fence_length = 0

    for index, line in enumerate(lines):
        if fence_character is not None:
            if re.match(
                rf"^\s*{re.escape(fence_character)}{{{fence_length},}}\s*$", line
            ):
                fence_character = None
                fence_length = 0
            continue

        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            continue

        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if not heading:
            continue
        if start is not None:
            return "".join(lines[start:index]).rstrip() + "\n"
        if normalize_heading(heading.group(1)) == expected:
            start = index

    if start is None:
        return None
    return "".join(lines[start:]).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print one Markdown H2 section, ignoring fenced-code headings."
    )
    parser.add_argument("markdown_file", type=Path)
    parser.add_argument("heading", help="Exact H2 text, with or without the ## prefix")
    args = parser.parse_args()

    result = extract_h2_section(
        args.markdown_file.read_text(encoding="utf-8"), args.heading
    )
    if result is None:
        print(f"section not found: {args.heading}", file=sys.stderr)
        return 1
    print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
