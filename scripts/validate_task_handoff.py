#!/usr/bin/env python3
"""Validate the required handoff sections in a Markdown task card."""

from __future__ import annotations

import argparse
import hashlib
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
    "Fast-gate group and command:",
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
    "Fast-gate group and command:",
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

LANE_FIELD = "Execution lane:"
FINGERPRINT_POLICY_FIELD = "Fingerprint policy:"
TASK_ROOT_FIELD = "Task root:"
LAYOUT_AUTHORITY_FIELDS = (
    "Project rules:",
    "Delivery policy:",
    "Role protocol:",
    "Artifact templates:",
)

REFERENCE_PATTERN = re.compile(
    r"(?:https?://\S+|`[^`]+`|\b(?:REQ|AC|DEC|TASK|TEST|EVID|DISC|SNAP|TEM)-[A-Za-z0-9._-]+\b)",
    flags=re.IGNORECASE,
)
PROJECT_PATH_PATTERN = re.compile(
    r"(?:`[^`]+`|(?:^|[\s;,(])(?:\.ai-team/|[A-Za-z0-9_.-]+/)[^\s;,)]*)",
    flags=re.IGNORECASE,
)


def normalize_heading(value: str) -> str:
    """Normalize human-readable Markdown headings for tolerant matching."""
    normalized = re.sub(r"[^\w]+", " ", value.casefold(), flags=re.UNICODE)
    return re.sub(r"\s+", " ", normalized).strip()


def section(text: str, heading: str) -> str:
    expected = normalize_heading(heading.lstrip("# "))
    match = None
    for candidate in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE):
        actual = normalize_heading(candidate.group(1))
        if actual == expected or actual.startswith(expected + " "):
            match = candidate
            break
    if match is None:
        return ""
    tail = text[match.end() :]
    end = re.search(r"^##\s+", tail, flags=re.MULTILINE)
    return tail if end is None else tail[: end.start()]


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
        or normalized in {
            "tbd",
            "todo",
            "tba",
            "not reviewed",
            "pending",
            "待定",
            "未填写",
        }
        or bool(re.fullmatch(r"[?._-]+", normalized))
    )


def has_reasoned_na(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized.startswith("n/a") and len(normalized.removeprefix("n/a").strip(" -:")) > 0


def snapshot_semantic_errors(snapshot: str) -> list[str]:
    errors: list[str] = []
    snapshot_id = field_value(snapshot, "Snapshot ID and updated at:")
    if not re.search(r"\bSNAP-[A-Za-z0-9._-]+\b", snapshot_id, flags=re.IGNORECASE):
        errors.append("strict snapshot ID must contain a concrete SNAP-... identifier")
    if not re.search(r"\b\d{4}-\d{2}-\d{2}(?=[T\s]|$)", snapshot_id):
        errors.append("strict snapshot updated-at must contain an ISO-style date")

    references = field_value(snapshot, "Source and decision references:")
    if not REFERENCE_PATTERN.search(references):
        errors.append("strict source/decision references need an ID, URL, or backticked path")

    required_reads = field_value(snapshot, "Required reads:")
    if not PROJECT_PATH_PATTERN.search(required_reads):
        errors.append("strict Required reads needs a concrete project-relative path")

    next_action = field_value(snapshot, "Next action and exit condition:")
    if len(next_action.strip()) < 12:
        errors.append("strict next action and exit condition is too short to be actionable")
    elif not re.search(r"\bexit\b|退出|完成条件|结束条件", next_action, flags=re.IGNORECASE):
        errors.append("strict next action must state an exit/completion condition")
    return errors


def markdown_path_value(value: str) -> str:
    match = re.search(r"`([^`]+)`", value)
    if match:
        return match.group(1).strip()
    return value.strip().split()[0] if value.strip() else ""


def resolve_project_layout(task_card: Path) -> tuple[Path | None, Path | None, str | None]:
    """Resolve project and declared task roots from the nearest ancestor manifest."""
    card_path = task_card.resolve()
    ai_team_root = next(
        (
            ancestor
            for ancestor in card_path.parents
            if ancestor.name == ".ai-team" and (ancestor / "manifest.md").is_file()
        ),
        None,
    )
    if ai_team_root is None:
        return None, None, "fingerprint verification requires an ancestor .ai-team/manifest.md"

    project_root = ai_team_root.parent.resolve()
    manifest_text = (ai_team_root / "manifest.md").read_text(encoding="utf-8")
    task_root_value = markdown_path_value(field_value(manifest_text, TASK_ROOT_FIELD))
    if not task_root_value:
        return None, None, "layout manifest is missing Task root:"

    configured = Path(task_root_value)
    if configured.is_absolute():
        return None, None, "layout manifest Task root must be project-relative"
    task_root = (project_root / configured).resolve()
    try:
        task_root.relative_to(ai_team_root)
    except ValueError:
        return None, None, "layout manifest Task root must remain under .ai-team/"
    try:
        card_path.relative_to(task_root)
    except ValueError:
        return None, None, "task card is outside the manifest-declared Task root"
    return project_root, task_root, None


def fingerprint_entries(text: str) -> list[tuple[str, str]]:
    snapshot = section(text, "## Handoff Snapshot")
    return re.findall(
        r"^[ \t]*-[ \t]*`([^`\n]+)`[ \t]*=[ \t]*([0-9a-fA-F]{64})[ \t]*$",
        snapshot,
        flags=re.MULTILINE,
    )


def project_authority_errors(task_card: Path) -> list[str]:
    """Verify that strict validation has a complete project-local authority set."""
    project_root, _, layout_error = resolve_project_layout(task_card)
    if layout_error:
        return [layout_error]
    assert project_root is not None

    ai_team_root = project_root / ".ai-team"
    manifest_text = (ai_team_root / "manifest.md").read_text(encoding="utf-8")
    errors: list[str] = []
    for field in LAYOUT_AUTHORITY_FIELDS:
        value = markdown_path_value(field_value(manifest_text, field))
        if not value:
            errors.append(f"layout manifest is missing {field}")
            continue
        configured = Path(value)
        if configured.is_absolute():
            errors.append(f"layout manifest {field} must be project-relative")
            continue
        resolved = (project_root / configured).resolve()
        try:
            resolved.relative_to(ai_team_root)
        except ValueError:
            errors.append(f"layout manifest {field} must remain under .ai-team/")
            continue
        if not resolved.is_file():
            errors.append(f"layout authority file not found for {field} {value}")
    return errors


def strict_errors(
    snapshot: str, test_plan: str, runtime_chain: str, full_text: str
) -> list[str]:
    errors: list[str] = []

    for field in STRICT_SNAPSHOT_FIELDS:
        value = field_value(snapshot, field)
        if field == "Current change-set fingerprint:" and fingerprint_entries(full_text):
            continue
        if is_placeholder(value):
            errors.append(f"strict snapshot field is empty or placeholder: {field}")
    errors.extend(snapshot_semantic_errors(snapshot))

    lane = field_value(full_text, LANE_FIELD).strip().lower()
    if lane not in {"fast", "standard", "high-risk"}:
        errors.append("strict task field is missing or invalid: Execution lane:")

    for field in STRICT_MANIFEST_FIELDS:
        value = field_value(test_plan, field)
        if field == "Fast-gate group and command:" and lane == "fast" and has_reasoned_na(value):
            continue
        if is_placeholder(value) or (value.strip().lower() == "n/a"):
            errors.append(f"strict manifest field is empty or placeholder: {field}")
        elif value.strip().lower().startswith("n/a") and not has_reasoned_na(value):
            errors.append(f"strict manifest N/A lacks rationale: {field}")

    fingerprint_policy = field_value(full_text, FINGERPRINT_POLICY_FIELD).strip().lower()
    if is_placeholder(fingerprint_policy):
        errors.append("strict task field is missing or placeholder: Fingerprint policy:")
    elif fingerprint_policy.startswith("n/a"):
        if not has_reasoned_na(fingerprint_policy):
            errors.append("strict fingerprint N/A lacks rationale")
        if lane != "fast":
            errors.append("strict fingerprint N/A is allowed only for Fast path tasks")
    elif fingerprint_policy != "required":
        errors.append("strict Fingerprint policy must be 'required' or reasoned 'N/A'")

    if fingerprint_policy == "required" and not fingerprint_entries(full_text):
        errors.append("strict required fingerprint policy needs a SHA-256 ledger in Handoff Snapshot")

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
            lane = field_value(text, LANE_FIELD).strip().lower()
            if lane == "fast":
                runtime_chain = "- Trigger: N/A — Fast path; no runtime-chain trigger."
            else:
                errors.append("strict missing Runtime-chain matrix section")
        if runtime_chain:
            errors.extend(strict_errors(snapshot, test_plan, runtime_chain, text))

    return errors


def fingerprint_errors(task_card: Path, text: str) -> list[str]:
    """Verify an explicit SHA-256 ledger without running project commands."""
    snapshot = section(text, "## Handoff Snapshot")
    entries = fingerprint_entries(text)
    if not entries:
        return ["fingerprint verification requested but no SHA-256 ledger was found in Handoff Snapshot"]

    project_root, _, layout_error = resolve_project_layout(task_card)
    if layout_error:
        return [layout_error]
    assert project_root is not None
    errors: list[str] = []
    for relative_path, expected in entries:
        candidate = Path(relative_path)
        if candidate.is_absolute():
            errors.append(f"fingerprint path must be project-relative: {relative_path}")
            continue
        resolved = (project_root / candidate).resolve()
        try:
            resolved.relative_to(project_root)
        except ValueError:
            errors.append(f"fingerprint path escapes project root: {relative_path}")
            continue
        if not resolved.is_file():
            errors.append(f"fingerprint file not found: {relative_path}")
            continue
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
        if digest.lower() != expected.lower():
            errors.append(
                f"fingerprint mismatch: {relative_path} expected {expected.lower()} got {digest}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Handoff Snapshot and Test Execution Manifest fields."
    )
    parser.add_argument("task_card", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require the project authority layout, non-placeholder handoff, lane/fingerprint policy, manifest, and applicable runtime-chain values; verify required ledgers.",
    )
    parser.add_argument(
        "--verify-fingerprint",
        action="store_true",
        help="Verify the explicit SHA-256 file ledger in the Handoff Snapshot without running project commands.",
    )
    args = parser.parse_args()

    text = args.task_card.read_text(encoding="utf-8")
    errors = validate(text, strict=args.strict)
    if args.strict:
        errors.extend(project_authority_errors(args.task_card))
    strict_requires_fingerprint = (
        args.strict
        and field_value(text, FINGERPRINT_POLICY_FIELD).strip().lower() == "required"
    )
    if args.verify_fingerprint or strict_requires_fingerprint:
        errors.extend(fingerprint_errors(args.task_card, text))

    if errors:
        print(f"FAIL {args.task_card}")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS {args.task_card}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
