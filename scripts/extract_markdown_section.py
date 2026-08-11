#!/usr/bin/env python3
"""Print one Markdown H2 section while ignoring headings inside fenced code."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


WORKFLOW_REVISION = "ai-team-2026-08-12-r12"


def normalize_heading(value: str) -> str:
    normalized = re.sub(r"[^\w]+", " ", value.casefold(), flags=re.UNICODE)
    return re.sub(r"\s+", " ", normalized).strip()


def visible_markdown(text: str) -> str:
    """Blank fenced code and HTML comments while preserving line boundaries."""
    comment_free = re.sub(
        r"<!--[\s\S]*?(?:-->|$)",
        lambda match: "".join("\n" if char == "\n" else " " for char in match.group(0)),
        text,
    )
    output: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in comment_free.splitlines(keepends=True):
        if fence_character is not None:
            if re.match(
                rf"^\s*{re.escape(fence_character)}{{{fence_length},}}\s*$", line
            ):
                fence_character = None
                fence_length = 0
            output.append("\n" if line.endswith("\n") else "")
            continue
        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            output.append("\n" if line.endswith("\n") else "")
            continue
        output.append(line)
    return "".join(output)


def h2_heading_counts(text: str) -> dict[str, int]:
    """Return normalized visible H2 heading counts."""
    counts: dict[str, int] = {}
    for line in visible_markdown(text).splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            normalized = normalize_heading(heading.group(1))
            counts[normalized] = counts.get(normalized, 0) + 1
    return counts


def extract_h2_section(
    text: str, requested_heading: str, *, allow_suffix: bool = False
) -> str | None:
    expected = normalize_heading(requested_heading.lstrip("# "))
    lines = text.splitlines(keepends=True)
    visible_lines = visible_markdown(text).splitlines(keepends=True)
    start: int | None = None

    for index, line in enumerate(visible_lines):
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if not heading:
            continue
        if start is not None:
            return "".join(lines[start:index]).rstrip() + "\n"
        actual = normalize_heading(heading.group(1))
        if actual == expected or (allow_suffix and actual.startswith(expected + " ")):
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
