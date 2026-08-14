#!/usr/bin/env python3
"""Read-only authority, backlog, dependency, path, and active-task consistency checks."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from urllib.parse import unquote

try:
    from . import validate_task_handoff as validator
    from .extract_markdown_section import visible_markdown
except ImportError:
    import validate_task_handoff as validator
    from extract_markdown_section import visible_markdown


WORKFLOW_SCHEMA = validator.WORKFLOW_SCHEMA
WORKFLOW_REVISION = validator.WORKFLOW_REVISION
REVISION_PATTERN = re.compile(r"\bai-team-\d{4}-\d{2}-\d{2}-r\d+\b")
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
BACKTICK_PATH_PATTERN = re.compile(r"`([^`]+)`")
TASK_ID_PATTERN = re.compile(r"\bTASK-[A-Za-z0-9._-]+\b", re.IGNORECASE)
DECISION_ID_PATTERN = re.compile(r"\bDEC-[A-Za-z0-9._-]+\b", re.IGNORECASE)
FINDING_ID_PATTERN = re.compile(r"\bFIND-[A-Za-z0-9._-]+\b", re.IGNORECASE)
TERMINAL_STATES = {"complete", "cancelled", "cancelled/superseded", "superseded"}
OWNER_ROLES = set(WORKFLOW_SCHEMA["enums"]["owner_roles"])
NEXT_GATES = set(WORKFLOW_SCHEMA["enums"]["next_gates"])
CHECKPOINT_MODES = set(WORKFLOW_SCHEMA["enums"]["checkpoint_modes"])
CHECKPOINT_STATUSES = set(WORKFLOW_SCHEMA["enums"]["checkpoint_statuses"])
BACKLOG_COLUMNS = tuple(WORKFLOW_SCHEMA["tables"]["backlog_columns"])
BATCH_COLUMNS = tuple(WORKFLOW_SCHEMA["tables"]["batch_columns"])
REVISION_AUTHORITY_FIELDS = tuple(
    field for field in validator.LAYOUT_AUTHORITY_FIELDS if field != "Project stage:"
)
SCHEMA_DRIVEN_AUTHORITY_FIELDS = {
    "Handoff validator:",
    "Project consistency checker:",
}


def relative_display(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def located_error(card: Path, project_root: Path, error: str) -> str:
    if error.startswith(".ai-team/") or error.startswith(".ai-team\\"):
        return error
    return f"{relative_display(card, project_root)}: {error}"


def revision_tokens(text: str) -> set[str]:
    return set(REVISION_PATTERN.findall(text))


def local_link_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")] 
    else:
        target = target.split(maxsplit=1)[0]
    target = unquote(target).split("#", 1)[0]
    if not target or re.match(r"^(?:[a-z][a-z0-9+.-]*:|#)", target, re.IGNORECASE):
        return None
    return target


def manifest_path(project_root: Path, manifest_text: str, field: str) -> Path | None:
    value = validator.markdown_path_value(validator.field_value(manifest_text, field))
    if not value:
        return None
    configured = Path(value)
    if configured.is_absolute():
        return None
    return (project_root / configured).resolve()


def revision_errors(project_root: Path, manifest_text: str) -> list[str]:
    errors: list[str] = []
    for field in REVISION_AUTHORITY_FIELDS:
        artifact = manifest_path(project_root, manifest_text, field)
        if artifact is None or not artifact.is_file():
            continue
        artifact_text = artifact.read_text(encoding="utf-8")
        revisions = revision_tokens(artifact_text)
        if (
            not revisions
            and field in SCHEMA_DRIVEN_AUTHORITY_FIELDS
            and "WORKFLOW_REVISION" in artifact_text
        ):
            continue
        if revisions != {WORKFLOW_REVISION}:
            actual = ", ".join(sorted(revisions)) or "missing"
            errors.append(
                f"workflow revision drift in {relative_display(artifact, project_root)}: expected {WORKFLOW_REVISION}, got {actual}"
            )
    return errors


def link_errors(project_root: Path, ai_team_root: Path) -> list[str]:
    errors: list[str] = []
    for markdown_file in sorted(ai_team_root.rglob("*.md")):
        for line_number, line in enumerate(
            visible_markdown(markdown_file.read_text(encoding="utf-8")).splitlines(),
            start=1,
        ):
            for match in LINK_PATTERN.finditer(line):
                target = local_link_target(match.group(1))
                if target is None:
                    continue
                resolved = (markdown_file.parent / target).resolve()
                try:
                    resolved.relative_to(project_root)
                except ValueError:
                    errors.append(
                        f"local Markdown link escapes project root: {relative_display(markdown_file, project_root)}:{line_number} -> {target}"
                    )
                    continue
                if not resolved.exists():
                    errors.append(
                        f"local Markdown link target not found: {relative_display(markdown_file, project_root)}:{line_number} -> {target}"
                    )
    return errors


def parse_backlog(board: Path) -> tuple[list[dict[str, str]], list[str]]:
    lines = visible_markdown(board.read_text(encoding="utf-8")).splitlines()
    errors: list[str] = []
    header_index: int | None = None
    columns: list[str] = []
    for index, line in enumerate(lines):
        if line.strip().startswith("|"):
            candidate = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if candidate and candidate[0] == "ID":
                header_index = index
                columns = candidate
                break
    if header_index is None:
        return [], ["canonical backlog is missing its task table"]
    if tuple(columns) != BACKLOG_COLUMNS:
        errors.append(
            "canonical backlog columns must be: " + " | ".join(BACKLOG_COLUMNS)
        )
    rows: list[dict[str, str]] = []
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if len(cells) != len(columns):
            errors.append(f"backlog row has {len(cells)} cells instead of {len(columns)}: {cells[0]}")
            continue
        rows.append(dict(zip(columns, cells)))
    return rows, errors


def parse_batches(board: Path) -> tuple[list[dict[str, str]], list[str]]:
    lines = visible_markdown(board.read_text(encoding="utf-8")).splitlines()
    errors: list[str] = []
    header_index: int | None = None
    columns: list[str] = []
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        candidate = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if candidate and candidate[0] == "Batch":
            header_index = index
            columns = candidate
            break
    if header_index is None:
        return [], ["canonical backlog is missing its implementation-batch table"]
    if tuple(columns) != BATCH_COLUMNS:
        errors.append(
            "canonical implementation-batch columns must be: "
            + " | ".join(BATCH_COLUMNS)
        )
    rows: list[dict[str, str]] = []
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if len(cells) != len(columns):
            errors.append(f"batch row has {len(cells)} cells instead of {len(columns)}: {cells[0]}")
            continue
        rows.append(dict(zip(columns, cells)))
    return rows, errors


def card_identity(card: Path, text: str) -> tuple[str, str, str, str, str]:
    title = re.search(r"^#\s+(TASK-[^:\s]+)(?::|\s|$)", visible_markdown(text), re.MULTILINE)
    task_id = title.group(1) if title else ""
    snapshot = validator.section(text, "## Handoff Snapshot")
    state, _ = validator.state_and_outcome(snapshot)
    lane, complexity, _ = validator.delivery_descriptor(snapshot)
    batch_value = validator.field_value(snapshot, "Batch / dependencies / entry:")
    batch = batch_value.split("/", 1)[0].strip()
    complexity = complexity.upper()
    return task_id, state, lane, complexity, batch


def confirmed_decision_ids(project_root: Path) -> set[str]:
    decisions = project_root / ".ai-team/governance/decisions.md"
    if not decisions.is_file():
        return set()
    text = visible_markdown(decisions.read_text(encoding="utf-8"))
    headings = list(
        re.finditer(
            r"^##\s+(DEC-[A-Za-z0-9._-]+)(?::|\s|$)",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
    )
    confirmed: set[str] = set()
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        record = text[heading.end() : end]
        status = re.search(
            r"^\s*-\s*(?:\*\*)?Status:(?:\*\*)?\s*([^\n]+)$",
            record,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        if status and status.group(1).strip().casefold() == "confirmed":
            confirmed.add(heading.group(1).upper())
    return confirmed


def blocker_is_resolved(
    blocker: str, terminal_ids: set[str], confirmed_decisions: set[str]
) -> bool:
    task_refs = {match.group(0).upper() for match in TASK_ID_PATTERN.finditer(blocker)}
    decision_refs = {
        match.group(0).upper() for match in DECISION_ID_PATTERN.finditer(blocker)
    }
    finding_refs = {
        match.group(0).upper() for match in FINDING_ID_PATTERN.finditer(blocker)
    }
    if finding_refs:
        return False
    return bool(task_refs or decision_refs) and task_refs.issubset(
        terminal_ids
    ) and decision_refs.issubset(confirmed_decisions)


def has_batch_evidence(value: str) -> bool:
    return bool(
        validator.identifiers(value, "EVID")
        or re.search(r"`?\.ai-team/evidence/[^`\s]+", value, re.IGNORECASE)
    )


def resolve_card_link(board: Path, value: str) -> Path | None:
    match = LINK_PATTERN.search(value)
    if not match:
        return None
    target = local_link_target(match.group(1))
    return (board.parent / target).resolve() if target else None


def dependency_cycle(graph: dict[str, set[str]]) -> list[str]:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, path: list[str]) -> list[str]:
        if node in visiting:
            start = path.index(node)
            return path[start:] + [node]
        if node in visited:
            return []
        visiting.add(node)
        path.append(node)
        for dependency in graph.get(node, set()):
            cycle = visit(dependency, path)
            if cycle:
                return cycle
        path.pop()
        visiting.remove(node)
        visited.add(node)
        return []

    for task_id in graph:
        cycle = visit(task_id, [])
        if cycle:
            return cycle
    return []


def task_inventory_errors(project_root: Path, task_root: Path, board: Path) -> list[str]:
    rows, errors = parse_backlog(board)
    cards: dict[str, tuple[Path, str, str, str, str]] = {}
    card_paths: set[Path] = set()
    for card in sorted(task_root.rglob("TASK-*.md")):
        text = card.read_text(encoding="utf-8")
        task_id, state, lane, complexity, batch = card_identity(card, text)
        if not task_id:
            errors.append(f"task card lacks a TASK-... H1: {relative_display(card, project_root)}")
            continue
        if task_id in cards:
            errors.append(f"duplicate task ID across cards: {task_id}")
        cards[task_id] = (card.resolve(), state, lane, complexity, batch)
        card_paths.add(card.resolve())
    row_ids: set[str] = set()
    row_paths: set[Path] = set()
    graph: dict[str, set[str]] = {}
    blocker_references: list[tuple[str, set[str], set[str], set[str]]] = []
    for row in rows:
        task_id = row.get("ID", "")
        if task_id in row_ids:
            errors.append(f"duplicate backlog task ID: {task_id}")
        row_ids.add(task_id)
        owner = row.get("Owner role", "").strip().casefold()
        if owner not in OWNER_ROLES:
            errors.append(f"invalid backlog Owner role for {task_id}: {owner or 'missing'}")
        next_gate = row.get("Next gate", "").strip().casefold()
        if next_gate not in NEXT_GATES:
            errors.append(f"invalid backlog Next gate for {task_id}: {next_gate or 'missing'}")
        blocker = row.get("Blocker / decision", "").strip()
        if blocker and not validator.is_none(blocker):
            task_refs = {
                match.group(0).upper() for match in TASK_ID_PATTERN.finditer(blocker)
            }
            decision_refs = {
                match.group(0).upper()
                for match in DECISION_ID_PATTERN.finditer(blocker)
            }
            finding_refs = {
                match.group(0).upper()
                for match in FINDING_ID_PATTERN.finditer(blocker)
            }
            if not task_refs and not decision_refs and not finding_refs:
                errors.append(
                    f"backlog blocker must reference a TASK-..., DEC-..., or FIND-... ID: {task_id}"
                )
            blocker_references.append(
                (task_id, task_refs, decision_refs, finding_refs)
            )
        linked = resolve_card_link(board, row.get("Card", ""))
        if linked is None:
            errors.append(f"backlog task has no local task-card link: {task_id}")
            continue
        if linked in row_paths:
            errors.append(f"duplicate backlog task-card link: {relative_display(linked, project_root)}")
        row_paths.add(linked)
        if linked not in card_paths:
            errors.append(f"backlog task card not found or not unique: {task_id} -> {relative_display(linked, project_root)}")
            continue
        card_id = next((known for known, values in cards.items() if values[0] == linked), "")
        if card_id != task_id:
            errors.append(f"backlog/card ID mismatch: {task_id} -> {card_id or 'missing'}")
            continue
        _, state, lane, complexity, batch = cards[task_id]
        for column, expected in (("State", state), ("Lane", lane), ("Complexity", complexity), ("Batch", batch)):
            actual = row.get(column, "").strip()
            if expected and actual.casefold() != expected.casefold():
                errors.append(f"backlog/card {column} mismatch for {task_id}: {actual or 'missing'} != {expected}")
        dependencies = {match.group(0).upper() for match in TASK_ID_PATTERN.finditer(row.get("Dependencies", ""))}
        graph[task_id] = dependencies
        card_dependencies = validator.task_dependencies(linked.read_text(encoding="utf-8"))
        if dependencies != card_dependencies:
            errors.append(
                f"backlog/card Dependencies mismatch for {task_id}: backlog={sorted(dependencies)} card={sorted(card_dependencies)}"
            )
        finding_refs = {
            match.group(0).upper()
            for match in FINDING_ID_PATTERN.finditer(
                row.get("Blocker / decision", "")
            )
        }
        if finding_refs:
            card_text = linked.read_text(encoding="utf-8")
            card_findings = validator.identifiers(card_text, "FIND")
            missing_findings = sorted(finding_refs - card_findings)
            if missing_findings:
                errors.append(
                    f"backlog blocker finding is absent from its task card: {task_id} -> {', '.join(missing_findings)}"
                )
            severities, _ = validator.recorded_findings(card_text)
            if not severities.intersection({"P0", "P1"}):
                errors.append(
                    f"backlog FIND blocker requires recorded P0/P1 severity in its task card: {task_id}"
                )
    for task_id, (card, _, _, _, _) in cards.items():
        if task_id not in row_ids:
            errors.append(f"task card is missing from backlog: {relative_display(card, project_root)}")
        text = card.read_text(encoding="utf-8")
        state = card_identity(card, text)[1]
        if state == "complete":
            findings = validator.section(text, "## Verification and findings")
            for follow_up in validator.identifiers(
                validator.field_value(findings, "Open P0/P1 / P2 follow-up:"), "TASK"
            ):
                if follow_up not in row_ids:
                    errors.append(f"P2 follow-up task not found: {task_id} -> {follow_up}")
    for task_id, dependencies in graph.items():
        for dependency in dependencies:
            if dependency not in row_ids:
                errors.append(f"backlog dependency not found: {task_id} -> {dependency}")
        state = cards.get(task_id, (None, "", "", "", ""))[1]
        if state in {"implementation-ready", "implementing", "awaiting-verification", "complete"}:
            incomplete = sorted(dependencies - {
                known_id
                for known_id, values in cards.items()
                if values[1] == "complete"
            })
            if incomplete:
                errors.append(
                    f"promoted task has incomplete dependencies: {task_id} -> {', '.join(incomplete)}"
                )
    manifest = project_root / ".ai-team/manifest.md"
    if manifest.is_file():
        traceability = manifest_path(
            project_root,
            manifest.read_text(encoding="utf-8"),
            "Requirement traceability:",
        )
        if traceability and traceability.is_file():
            matrix_task_ids = validator.identifiers(
                visible_markdown(traceability.read_text(encoding="utf-8")), "TASK"
            )
            for reference in sorted(matrix_task_ids - row_ids):
                errors.append(f"Requirement traceability task not found in backlog: {reference}")
    decisions_path = project_root / ".ai-team/governance/decisions.md"
    decision_ids = (
        {
            match.group(0).upper()
            for match in DECISION_ID_PATTERN.finditer(
                visible_markdown(decisions_path.read_text(encoding="utf-8"))
            )
        }
        if decisions_path.is_file()
        else set()
    )
    for task_id, task_refs, decision_refs, _ in blocker_references:
        for reference in task_refs:
            if reference not in row_ids:
                errors.append(f"backlog blocker task not found: {task_id} -> {reference}")
        for reference in decision_refs:
            if reference not in decision_ids:
                errors.append(f"backlog blocker decision not found: {task_id} -> {reference}")
    cycle = dependency_cycle(graph)
    if cycle:
        errors.append("backlog dependency cycle: " + " -> ".join(cycle))
    batch_rows, batch_errors = parse_batches(board)
    errors.extend(batch_errors)
    batches: dict[str, dict[str, str]] = {}
    for batch_row in batch_rows:
        batch_id = batch_row.get("Batch", "").strip()
        if batch_id in batches:
            errors.append(f"duplicate implementation batch: {batch_id}")
        batches[batch_id] = batch_row
    assigned: dict[str, set[str]] = {}
    for task_id, (_, _, lane, _, batch) in cards.items():
        if lane == "fast" and batch.casefold().startswith("batch-not-applicable"):
            continue
        if not batch:
            continue
        assigned.setdefault(batch, set()).add(task_id.upper())
        if batch not in batches:
            errors.append(f"task references an undefined implementation batch: {task_id} -> {batch}")
    for batch_id, task_ids in assigned.items():
        batch_row = batches.get(batch_id)
        if batch_row is None:
            continue
        member_list = [
            match.group(0).upper()
            for match in TASK_ID_PATTERN.finditer(batch_row.get("Member tasks", ""))
        ]
        members = set(member_list)
        order_list = [
            match.group(0).upper()
            for match in TASK_ID_PATTERN.finditer(
                batch_row.get("Serial implementation order", "")
            )
        ]
        order = set(order_list)
        if members != task_ids:
            errors.append(
                f"batch member/card mismatch for {batch_id}: table={sorted(members)} cards={sorted(task_ids)}"
            )
        if len(member_list) != len(members):
            errors.append(f"batch member list contains duplicate task IDs for {batch_id}")
        if order != task_ids or len(order_list) != len(order):
            errors.append(
                validator.format_error(
                    f"batch serial order must list each member once for {batch_id}",
                    batch_row.get("Serial implementation order", ""),
                    "serial_task_order",
                )
            )
        for field in (
            "Objective",
            "Entry criteria",
            "Exit evidence",
            "Checkpoint mode",
            "Checkpoint status",
        ):
            if not batch_row.get(field, "").strip():
                errors.append(f"implementation batch {batch_id} is missing {field}")
        checkpoint = batch_row.get("Acceptance checkpoint", "").strip()
        mode = batch_row.get("Checkpoint mode", "").strip().casefold()
        status = batch_row.get("Checkpoint status", "").strip().casefold()
        if mode not in CHECKPOINT_MODES:
            errors.append(f"implementation batch {batch_id} has invalid Checkpoint mode")
        if status not in CHECKPOINT_STATUSES:
            errors.append(f"implementation batch {batch_id} has invalid Checkpoint status")
        if mode == "none" and (not validator.is_none(checkpoint) or status != "not-required"):
            errors.append(
                f"implementation batch {batch_id} checkpoint mode none requires checkpoint none / not-required"
            )
        if mode != "none" and (
            validator.is_none(checkpoint) or not checkpoint or status == "not-required"
        ):
            errors.append(
                f"implementation batch {batch_id} named checkpoint requires pending, accepted, or rejected status"
            )
        if task_ids and all(cards[task_id][1] == "complete" for task_id in task_ids):
            exit_evidence = batch_row.get("Exit evidence", "")
            if validator.is_pass(exit_evidence) and (
                not has_batch_evidence(exit_evidence)
                or not validator.iso_datetime(exit_evidence)
            ):
                errors.append(
                    f"completed batch {batch_id} regression PASS requires evidence reference and ISO time"
                )
            if re.match(r"^\s*FAIL(?:\s|[-—:]|$)", exit_evidence, re.IGNORECASE) and not (
                has_batch_evidence(exit_evidence)
                and (
                    validator.identifiers(exit_evidence, "TASK")
                    or validator.identifiers(exit_evidence, "TEST")
                    or validator.identifiers(exit_evidence, "FIND")
                )
            ):
                errors.append(
                    f"completed batch {batch_id} regression FAIL requires evidence and affected TASK/TEST/FIND scope"
                )
    return errors


def active_task_errors(project_root: Path, task_root: Path) -> list[str]:
    errors: list[str] = []
    implementing: list[str] = []
    for card in sorted(task_root.rglob("TASK-*.md")):
        text = card.read_text(encoding="utf-8")
        snapshot = validator.section(text, "## Handoff Snapshot")
        if not snapshot:
            errors.append(f"task card has no Handoff Snapshot: {relative_display(card, project_root)}")
            continue
        state, _ = validator.state_and_outcome(snapshot)
        if state == "implementing":
            implementing.append(card.name)
        revision = validator.field_value(snapshot, "Workflow revision:").strip(" `")
        if revision != WORKFLOW_REVISION:
            errors.append(
                f"active task workflow revision mismatch: {relative_display(card, project_root)} expected {WORKFLOW_REVISION}, got {revision or 'missing'}"
            )
        gate: str | None = None
        if state == "task-design-ready":
            gate = "task-design"
        elif state == "implementation-ready":
            gate = "implementation-ready"
        elif state == "complete":
            gate = "verified-complete"
        if gate:
            for error in validator.validate(text, gate=gate):
                errors.append(located_error(card, project_root, error))
            for error in validator.gate_reference_errors(card, text, gate):
                errors.append(located_error(card, project_root, error))
            for error in validator.project_stage_errors(card, gate):
                errors.append(located_error(card, project_root, error))
        elif state in {"implementing", "awaiting-verification"}:
            promoted_errors = validator.active_promotion_errors(text, state)
            promoted_errors.extend(
                validator.gate_reference_errors(card, text, "implementation-ready")
            )
            promoted_errors.extend(validator.project_spec_errors(card, text))
            promoted_errors.extend(
                validator.project_stage_errors(
                    card,
                    "implementation-ready"
                    if state == "implementing"
                    else "verified-complete",
                )
            )
            for error in dict.fromkeys(promoted_errors):
                errors.append(located_error(card, project_root, error))
        else:
            for error in validator.state_model_errors(snapshot):
                errors.append(f"{relative_display(card, project_root)}: {error}")
            if state == "cancelled/superseded":
                for error in validator.cancellation_errors(text):
                    errors.append(located_error(card, project_root, error))
        if validator.candidate_fingerprint_required(text):
            for error in validator.fingerprint_errors(card, text):
                errors.append(located_error(card, project_root, error))
    if len(implementing) > 1:
        errors.append(
            "more than one task is implementing; one serial implementation engineer may own only one active implementation: "
            + ", ".join(implementing)
        )
    return errors


def check_project(project_root: Path) -> list[str]:
    project_root = project_root.resolve()
    ai_team_root = project_root / ".ai-team"
    manifest = ai_team_root / "manifest.md"
    if not manifest.is_file():
        return ["project consistency requires .ai-team/manifest.md"]
    manifest_text = manifest.read_text(encoding="utf-8")
    errors: list[str] = []
    if revision_tokens(manifest_text) != {WORKFLOW_REVISION}:
        errors.append(f"manifest workflow revision must be {WORKFLOW_REVISION}")
    errors.extend(validator.project_authority_errors_from_root(project_root))
    errors.extend(revision_errors(project_root, manifest_text))
    source = manifest_path(project_root, manifest_text, "Source register:")
    if validator.repository_contains_code(project_root):
        if source is None or not source.is_file():
            errors.append("existing-code initialization requires the manifest-declared Source register")
        else:
            errors.extend(validator.code_baseline_errors(source))
    task_root = manifest_path(project_root, manifest_text, "Task root:")
    board = manifest_path(project_root, manifest_text, "Canonical task board:")
    if task_root is None or not task_root.is_dir():
        errors.append("manifest-declared Task root is missing")
    elif board is None or not board.is_file():
        errors.append("manifest-declared canonical task board is missing")
    else:
        task_readme = task_root / "README.md"
        if not task_readme.is_file() or revision_tokens(task_readme.read_text(encoding="utf-8")) != {WORKFLOW_REVISION}:
            errors.append(f"task management README must use workflow revision {WORKFLOW_REVISION}")
        errors.extend(task_inventory_errors(project_root, task_root, board))
        errors.extend(active_task_errors(project_root, task_root))
        task_cards = list(task_root.rglob("TASK-*.md"))
        if any(
            validator.section(card.read_text(encoding="utf-8"), "## Handoff Snapshot")
            for card in task_cards
        ):
            evidence_root = manifest_path(project_root, manifest_text, "Evidence root:")
            if source is None or not source.is_file():
                errors.append("active delivery requires the manifest-declared Source register")
            else:
                errors.extend(validator.source_register_errors(source))
            if evidence_root is None or not evidence_root.is_dir():
                errors.append("active delivery requires the manifest-declared Evidence root")
    errors.extend(link_errors(project_root, ai_team_root))
    return list(dict.fromkeys(errors))


def next_eligible_action(project_root: Path) -> str | None:
    project_root = project_root.resolve()
    manifest = project_root / ".ai-team/manifest.md"
    if not manifest.is_file():
        return None
    manifest_text = manifest.read_text(encoding="utf-8")
    board = manifest_path(project_root, manifest_text, "Canonical task board:")
    if board is None or not board.is_file():
        return None
    rows, errors = parse_backlog(board)
    if errors:
        return None
    if not rows:
        source = manifest_path(project_root, manifest_text, "Source register:")
        if source is None or not source.is_file():
            return "PROJECT: initialize the source register and intake boundary"
        if validator.source_register_errors(source):
            return "PROJECT: complete the source register and intake boundary"
        return "PROJECT: start product analysis and create the first traceable task"
    terminal_ids = {
        row.get("ID", "").upper()
        for row in rows
        if row.get("State", "").strip().casefold() == "complete"
    }
    batch_rows, batch_errors = parse_batches(board)
    if batch_errors:
        return None
    row_by_id = {row.get("ID", "").upper(): row for row in rows}
    confirmed_decisions = confirmed_decision_ids(project_root)
    batch_index = {
        batch.get("Batch", "").strip(): index for index, batch in enumerate(batch_rows)
    }
    deferred_checkpoints: list[tuple[str, str]] = []
    for batch in batch_rows:
        members = [
            match.group(0).upper()
            for match in TASK_ID_PATTERN.finditer(batch.get("Member tasks", ""))
        ]
        if not members or not all(
            row_by_id.get(member, {}).get("State", "").strip().casefold() == "complete"
            for member in members
        ):
            continue
        exit_evidence = batch.get("Exit evidence", "").strip()
        batch_id = batch.get("Batch", "").strip()
        if re.match(r"^\s*FAIL(?:\s|[-—:]|$)", exit_evidence, re.IGNORECASE):
            return f"{batch_id}: re-enter affected completed tasks from failed batch regression; evidence={exit_evidence}"
        if not validator.is_pass(exit_evidence):
            return f"{batch_id}: run the planned batch regression and record PASS or FAIL; plan={exit_evidence or 'missing'}"
        checkpoint_status = batch.get("Checkpoint status", "").strip().casefold()
        checkpoint = batch.get("Acceptance checkpoint", "").strip()
        if checkpoint_status == "rejected":
            return f"{checkpoint}: re-enter affected scope from rejected checkpoint {batch.get('Batch', '').strip()}"
        if checkpoint_status == "conditional":
            return f"{checkpoint}: re-enter affected scope for conditional acceptance of batch {batch.get('Batch', '').strip()}"
        if checkpoint_status == "pending":
            if batch.get("Checkpoint mode", "").strip().casefold() == "blocking":
                return f"{checkpoint}: human acceptance required for completed batch {batch.get('Batch', '').strip()}"
            deferred_checkpoints.append((checkpoint, batch.get("Batch", "").strip()))

    for row in rows:
        state = row.get("State", "").strip().casefold()
        if state not in {"implementing", "awaiting-verification"}:
            continue
        batch_id = row.get("Batch", "").strip()
        batch = next(
            (item for item in batch_rows if item.get("Batch", "").strip() == batch_id),
            None,
        )
        if batch is None:
            continue
        order = [
            match.group(0).upper()
            for match in TASK_ID_PATTERN.finditer(
                batch.get("Serial implementation order", "")
            )
        ]
        task_id = row.get("ID", "").upper()
        if task_id in order:
            earlier = order[: order.index(task_id)]
            incomplete = [item for item in earlier if item not in terminal_ids]
            if incomplete:
                return (
                    f"{task_id}: stop out-of-order active work and resume {incomplete[0]} "
                    "before continuing this task"
                )

    actions = {
        "analysis": "continue product/technical task design",
        "task-design-ready": "run or activate implementation-readiness",
        "implementation-ready": "start the one serial implementation engineer",
        "implementing": "continue the one serial implementation engineer",
        "awaiting-verification": "start independent verification",
    }
    state_priority = (
        "implementing",
        "awaiting-verification",
        "implementation-ready",
        "task-design-ready",
        "analysis",
    )
    for desired_state in state_priority:
        for row in rows:
            state = row.get("State", "").strip().casefold()
            if state != desired_state:
                continue
            action = actions.get(state)
            if action is None:
                continue
            card = resolve_card_link(board, row.get("Card", ""))
            if state == "awaiting-verification":
                if card and card.is_file():
                    card_text = card.read_text(encoding="utf-8")
                    severities, verifier_verdict = validator.recorded_findings(card_text)
                    if "P0" in severities:
                        return (
                            f"{row.get('ID', '').strip()}: block implementation and escalate the recorded P0 finding"
                        )
                    if "P1" in severities or re.search(
                        r"\bFAIL\b", verifier_verdict, re.IGNORECASE
                    ):
                        return (
                            f"{row.get('ID', '').strip()}: return to serial implementation remediation "
                            "with task-scoped design re-entry when required"
                        )
                    if validator.separate_review_required(card_text):
                        action += " and triggered code/security review"
            blocker = row.get("Blocker / decision", "").strip()
            if blocker and not validator.is_none(blocker):
                finding_refs = {
                    match.group(0).upper()
                    for match in FINDING_ID_PATTERN.finditer(blocker)
                }
                if finding_refs and card and card.is_file():
                    severities, _ = validator.recorded_findings(
                        card.read_text(encoding="utf-8")
                    )
                    if "P0" in severities:
                        return (
                            f"{row.get('ID', '').strip()}: block implementation and escalate "
                            f"the recorded P0 finding {sorted(finding_refs)[0]}"
                        )
                    if "P1" in severities:
                        return (
                            f"{row.get('ID', '').strip()}: return {sorted(finding_refs)[0]} "
                            "to serial implementation remediation"
                        )
                if blocker_is_resolved(blocker, terminal_ids, confirmed_decisions):
                    return (
                        f"{row.get('ID', '').strip()}: clear the resolved blocker and resume {action}"
                    )
                continue
            dependencies = {
                match.group(0).upper()
                for match in TASK_ID_PATTERN.finditer(row.get("Dependencies", ""))
            }
            if not dependencies.issubset(terminal_ids):
                continue
            if state == "implementation-ready":
                batch_id = row.get("Batch", "").strip()
                batch = next(
                    (
                        item
                        for item in batch_rows
                        if item.get("Batch", "").strip() == batch_id
                    ),
                    None,
                )
                if batch:
                    order = [
                        match.group(0).upper()
                        for match in TASK_ID_PATTERN.finditer(
                            batch.get("Serial implementation order", "")
                        )
                    ]
                    task_key = row.get("ID", "").upper()
                    if task_key in order:
                        earlier = order[: order.index(task_key)]
                        if not set(earlier).issubset(terminal_ids):
                            continue
                    current_index = batch_index.get(batch_id, 0)
                    blocked_by_prior_checkpoint = any(
                        prior.get("Checkpoint mode", "").strip().casefold()
                        == "blocking"
                        and prior.get("Checkpoint status", "").strip().casefold()
                        != "accepted"
                        for prior in batch_rows[:current_index]
                    )
                    if blocked_by_prior_checkpoint:
                        continue
            task_id = row.get("ID", "").strip()
            owner = row.get("Owner role", "").strip()
            next_gate = row.get("Next gate", "").strip()
            return f"{task_id}: {action}; owner={owner}; next-gate={next_gate}"
    for row in rows:
        state = row.get("State", "").strip().casefold()
        if state in TERMINAL_STATES:
            continue
        blocker = row.get("Blocker / decision", "").strip()
        decision = DECISION_ID_PATTERN.search(blocker)
        if blocker_is_resolved(blocker, terminal_ids, confirmed_decisions):
            return f"{row.get('ID', '').strip()}: clear the resolved blocker and resume local delivery"
        if state == "awaiting-human-decision" or decision:
            decision_id = decision.group(0).upper() if decision else "unrecorded-decision"
            return (
                f"{decision_id}: human decision required for {row.get('ID', '').strip()}; "
                f"next-gate={row.get('Next gate', '').strip()}"
            )
    if deferred_checkpoints:
        checkpoint, batch_id = deferred_checkpoints[0]
        return f"{checkpoint}: non-blocking human acceptance remains pending for completed batch {batch_id}"
    for row in rows:
        state = row.get("State", "").strip().casefold()
        if state in TERMINAL_STATES:
            continue
        blocker = row.get("Blocker / decision", "").strip() or "unmet dependency or gate"
        return f"{row.get('ID', '').strip()}: no eligible local action; blocked-by={blocker}"
    return None


def selected_task_gate_errors(project_root: Path, task_id: str, gate: str) -> list[str]:
    project_root = project_root.resolve()
    manifest = project_root / ".ai-team/manifest.md"
    if not manifest.is_file():
        return ["selected task validation requires .ai-team/manifest.md"]
    task_root = manifest_path(
        project_root, manifest.read_text(encoding="utf-8"), "Task root:"
    )
    if task_root is None or not task_root.is_dir():
        return ["selected task validation requires the manifest-declared Task root"]
    matches = [
        card
        for card in task_root.rglob("*.md")
        if card.name != "README.md"
        and card_identity(card, card.read_text(encoding="utf-8"))[0] == task_id.upper()
    ]
    if len(matches) != 1:
        return [f"selected task must resolve to one card: {task_id} -> {len(matches)} matches"]
    card = matches[0]
    text = card.read_text(encoding="utf-8")
    errors = validator.validate(text, gate=gate)
    errors.extend(validator.gate_reference_errors(card, text, gate))
    errors.extend(validator.project_stage_errors(card, gate))
    if validator.candidate_fingerprint_required(text):
        errors.extend(validator.fingerprint_errors(card, text))
    return [located_error(card, project_root, error) for error in dict.fromkeys(errors)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check an AI-team project without modifying it.")
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument(
        "--next-action",
        action="store_true",
        help="After a clean consistency check, print the first dependency-eligible continuation action.",
    )
    parser.add_argument("--task", help="Validate one TASK-... card in the same project check.")
    parser.add_argument(
        "--gate",
        choices=validator.GATES,
        help="Gate to validate for --task; combines task, project, fingerprint, and next-action checks.",
    )
    args = parser.parse_args()
    errors = check_project(args.project_root)
    if args.task or args.gate:
        if not args.task or not args.gate:
            errors.append("--task and --gate must be provided together")
        else:
            errors.extend(selected_task_gate_errors(args.project_root, args.task, args.gate))
    errors = list(dict.fromkeys(errors))
    if errors:
        print(f"FAIL {args.project_root.resolve()}")
        for error in errors:
            print(f"- {error}")
        if args.next_action:
            print(f"NEXT fix-consistency: {errors[0]}")
        return 1
    print(f"PASS {args.project_root.resolve()}")
    if args.next_action:
        action = next_eligible_action(args.project_root)
        print(f"NEXT {action or 'none — no dependency-eligible local action'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
