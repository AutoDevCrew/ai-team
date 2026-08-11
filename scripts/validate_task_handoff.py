#!/usr/bin/env python3
"""Validate the required handoff sections in a Markdown task card."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


SNAPSHOT_FIELDS = (
    "Snapshot ID and updated at:",
    "Current state and technical outcome:",
    "Source and decision references:",
    "Frozen inputs and contracts:",
    "Current change-set fingerprint:",
    "Test Execution Manifest revision:",
    "Required reads:",
    "On-demand evidence / Evidence index:",
    "Open findings / blockers:",
    "Next action and exit condition:",
    "Invalidated by:",
)

MANIFEST_FIELDS = (
    "Revision and frozen-at:",
    "Owner test group and command:",
    "Affected/regression test group and command:",
    "Approved full suite and runner:",
    "Independent risk/mutation group and runner:",
    "Expected evidence and invalidation conditions:",
)

EVIDENCE_INDEX_FIELDS = (
    "Current source/design/decision evidence:",
    "Current test and review evidence:",
    "Partial execution record (when stopped early):",
    "Raw logs or large outputs (on demand):",
    "Superseded snapshot, manifest, or verdict:",
)

STRICT_SNAPSHOT_FIELDS = (
    "Snapshot ID and updated at:",
    "Current state and technical outcome:",
    "Source and decision references:",
    "Frozen inputs and contracts:",
    "Current change-set fingerprint:",
    "Test Execution Manifest revision:",
    "Required reads:",
    "On-demand evidence / Evidence index:",
    "Next action and exit condition:",
    "Invalidated by:",
)

STRICT_MANIFEST_FIELDS = (
    "Revision and frozen-at:",
    "Owner test group and command:",
    "Affected/regression test group and command:",
    "Approved full suite and runner:",
    "Independent risk/mutation group and runner:",
    "Expected evidence and invalidation conditions:",
)

RUNTIME_TRIGGER = "Trigger:"
RUNTIME_FIELDS = (
    "Entry → authorization/precondition → scheduling or claim → state transition → side effect → recovery/compensation → observable result:",
    "REQ / AC / module / test mapping for each critical stage:",
)


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    tail = text[start + len(heading) :]
    end = tail.find("\n## ")
    return tail if end == -1 else tail[:end]


def missing_fields(content: str, fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if field not in content]


def field_value(content: str, field: str) -> str:
    match = re.search(
        rf"^[ \t]*-[ \t]*{re.escape(field)}[ \t]*(.*)$",
        content,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        not normalized
        or bool(re.fullmatch(r"<[^>]+>", normalized))
        or normalized in {"tbd", "todo", "tba", "not reviewed"}
    )


def has_reasoned_na(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized.startswith("n/a") and len(normalized.removeprefix("n/a").strip(" -:")) > 0


def strict_errors(snapshot: str, test_plan: str, runtime_chain: str) -> list[str]:
    errors: list[str] = []

    for field in STRICT_SNAPSHOT_FIELDS:
        if is_placeholder(field_value(snapshot, field)):
            errors.append(f"strict snapshot field is empty or placeholder: {field}")

    for field in STRICT_MANIFEST_FIELDS:
        value = field_value(test_plan, field)
        if is_placeholder(value) or (value.strip().lower() == "n/a"):
            errors.append(f"strict manifest field is empty or placeholder: {field}")
        elif value.strip().lower().startswith("n/a") and not has_reasoned_na(value):
            errors.append(f"strict manifest N/A lacks rationale: {field}")

    trigger = field_value(runtime_chain, RUNTIME_TRIGGER)
    if is_placeholder(trigger):
        errors.append("strict runtime-chain trigger is empty or placeholder")
    elif trigger.lower() != "n/a" and not has_reasoned_na(trigger):
        for field in RUNTIME_FIELDS:
            if is_placeholder(field_value(runtime_chain, field)):
                errors.append(f"strict runtime-chain field is empty or placeholder: {field}")

    return errors


def validate(text: str, strict: bool = False) -> list[str]:
    snapshot = section(text, "## Handoff Snapshot")
    test_plan = section(text, "## Test plan and environment")
    evidence_index = section(text, "## Evidence index")
    runtime_chain = section(text, "## Runtime-chain matrix")

    errors: list[str] = []
    if not snapshot:
        errors.append("missing Handoff Snapshot section")
    else:
        errors.extend(
            f"snapshot missing field: {field}"
            for field in missing_fields(snapshot, SNAPSHOT_FIELDS)
        )

    if not test_plan:
        errors.append("missing Test plan and environment section")
    else:
        errors.extend(
            f"test manifest missing field: {field}"
            for field in missing_fields(test_plan, MANIFEST_FIELDS)
        )

    if not evidence_index:
        errors.append("missing Evidence index section")
    else:
        errors.extend(
            f"evidence index missing field: {field}"
            for field in missing_fields(evidence_index, EVIDENCE_INDEX_FIELDS)
        )

    if strict and snapshot and test_plan:
        if not runtime_chain:
            errors.append("strict missing Runtime-chain matrix section")
        else:
            errors.extend(strict_errors(snapshot, test_plan, runtime_chain))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Handoff Snapshot and Test Execution Manifest fields."
    )
    parser.add_argument("task_card", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require non-placeholder handoff, manifest, and applicable runtime-chain values.",
    )
    args = parser.parse_args()

    text = args.task_card.read_text(encoding="utf-8")
    errors = validate(text, strict=args.strict)

    if errors:
        print(f"FAIL {args.task_card}")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS {args.task_card}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
