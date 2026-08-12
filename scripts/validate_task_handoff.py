#!/usr/bin/env python3
"""Validate AI-team task structure, gate semantics, layout, and fingerprints."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

try:
    from .extract_markdown_section import (
        extract_h2_section,
        h2_heading_counts,
        normalize_heading,
        visible_markdown,
    )
except ImportError:
    from extract_markdown_section import (
        extract_h2_section,
        h2_heading_counts,
        normalize_heading,
        visible_markdown,
    )


def _load_workflow_schema() -> dict:
    script_dir = Path(__file__).resolve().parent
    candidates = (
        script_dir.parent / "governance/workflow-schema.json",
        script_dir.parent / "references/workflow-schema.json",
    )
    for candidate in candidates:
        if candidate.is_file():
            return json.loads(candidate.read_text(encoding="utf-8"))
    raise RuntimeError("workflow-schema.json was not found beside the project or global skill")


WORKFLOW_SCHEMA = _load_workflow_schema()
WORKFLOW_REVISION = WORKFLOW_SCHEMA["workflow_revision"]


def _values(group: str) -> tuple[str, ...]:
    return tuple(WORKFLOW_SCHEMA["fields"][group])


def _enum(group: str) -> set[str]:
    return set(WORKFLOW_SCHEMA["enums"][group])


GATES = tuple(WORKFLOW_SCHEMA["enums"]["gates"])
SNAPSHOT_FIELDS = _values("snapshot")
PLANNING_FIELDS = _values("planning")
SELF_CHECK_FIELDS = _values("self_check")
VERIFICATION_FIELDS = _values("verification")
FAST_GATE_FIELDS = _values("fast_gate")
FAST_COMPLETION_FIELDS = _values("fast_completion")
RUNTIME_FIELDS = _values("runtime")
SECURITY_FIELDS = _values("security")
TESTSPRITE_DESIGN_FIELDS = _values("testsprite_design")
TESTSPRITE_COMPLETION_FIELDS = TESTSPRITE_DESIGN_FIELDS + _values("testsprite_completion_extra")

TASK_STATES = _enum("task_states")
TECHNICAL_OUTCOMES = _enum("technical_outcomes")
LANES = _enum("lanes")
COMPLEXITIES = _enum("complexities")
CONTROL_TRIGGERS = _enum("control_triggers")
FINDING_SEVERITIES = _enum("finding_severities")

LANE_FIELD = "Delivery lane / complexity / control triggers:"
LANE_CONTRACTS = WORKFLOW_SCHEMA["lane_contracts"]
FINGERPRINT_POLICY_FIELD = "Fingerprint policy:"
TASK_ROOT_FIELD = "Task root:"
CHANGE_INVENTORY_FIELD = "Change-set file inventory:"
LAYOUT_AUTHORITY_FIELDS = _values("layout_authority")
SOURCE_REGISTER_FIELDS = _values("source_register")
ACCEPTANCE_INTAKE_FIELDS = _values("acceptance_intake")
ACCEPTANCE_SCOPE_FIELDS = _values("acceptance_scope")
TRACEABILITY_COLUMNS = tuple(WORKFLOW_SCHEMA["tables"]["traceability_columns"])
REVIEW_EVIDENCE_FIELDS = _values("review_evidence")
CANCELLATION_FIELDS = _values("cancellation")

REFERENCE_PATTERN = re.compile(
    r"(?:https?://\S+|`[^`]+`|\b(?:REQ|AC|DEC|TASK|TEST|EVID|FIND|DISC|SNAP|TEM)-[A-Za-z0-9._-]+\b)",
    flags=re.IGNORECASE,
)
PROJECT_PATH_PATTERN = re.compile(
    r"(?:`[^`]+`|(?:^|[\s;,(])(?:\.ai-team/|[A-Za-z0-9_.-]+/)[^\s;,)]*)",
    flags=re.IGNORECASE,
)


def section(text: str, heading: str) -> str:
    """Return one exact visible H2 section."""
    return extract_h2_section(text, heading, allow_suffix=False) or ""


def section_count(text: str, heading: str) -> int:
    return h2_heading_counts(text).get(normalize_heading(heading.lstrip("# ")), 0)


def field_values(content: str, field: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(
            rf"^[ \t]*-[ \t]*{re.escape(field)}[ \t]*(.*)$",
            visible_markdown(content),
            flags=re.MULTILINE,
        )
    ]


def field_value(content: str, field: str) -> str:
    values = field_values(content, field)
    return values[0] if values else ""


def missing_fields(content: str, fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if not field_values(content, field)]


def duplicate_field_errors(
    content: str, fields: tuple[str, ...], section_name: str
) -> list[str]:
    return [
        f"duplicate field in {section_name}: {field}"
        for field in fields
        if len(field_values(content, field)) > 1
    ]


def is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        not normalized
        or bool(re.fullmatch(r"<[^>]+>", normalized))
        or normalized
        in {
            "tbd",
            "todo",
            "tba",
            "not reviewed",
            "not-reviewed",
            "pending",
            "待定",
            "未填写",
            "确认中",
            "暂无",
            "稍后补",
        }
        or bool(re.fullmatch(r"[?._-]+", normalized))
    )


def has_reasoned_na(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized.startswith("n/a") and len(
        normalized.removeprefix("n/a").strip(" -:")
    ) >= 5


def is_none(value: str) -> bool:
    return value.strip().lower() in {"none", "no", "无"}


def is_pass(value: str) -> bool:
    """Accept an explicit leading PASS status, never a substring such as NOT PASS."""
    return bool(re.match(r"^\s*PASS(?:\s|[-—:]|$)", value, flags=re.IGNORECASE))


def has_reference(value: str) -> bool:
    return bool(REFERENCE_PATTERN.search(value) or PROJECT_PATH_PATTERN.search(value))


def first_identifier(value: str, prefix: str) -> str:
    match = re.search(
        rf"\b{re.escape(prefix)}-[A-Za-z0-9._-]+\b", value, flags=re.IGNORECASE
    )
    return match.group(0).upper() if match else ""


def identifiers(value: str, prefix: str) -> set[str]:
    return {
        match.group(0).upper()
        for match in re.finditer(
            rf"\b{re.escape(prefix)}-[A-Za-z0-9._-]+\b",
            value,
            flags=re.IGNORECASE,
        )
    }


def finding_identifiers(value: str) -> set[str]:
    return identifiers(value, "FIND") | identifiers(value, "EVID")


def identity_errors(authors: str, reviewer: str, section_name: str) -> list[str]:
    errors: list[str] = []
    author_ids = {
        match.group(0).upper()
        for match in re.finditer(r"\bAGENT-[A-Za-z0-9._-]+\b", authors, re.IGNORECASE)
    }
    reviewer_id = first_identifier(reviewer, "AGENT")
    if not author_ids:
        errors.append(f"{section_name} requires concrete AGENT-... artifact author identities")
    if not reviewer_id:
        errors.append(f"{section_name} requires a concrete AGENT-... reviewer identity")
    elif reviewer_id in author_ids:
        errors.append(f"{section_name} reviewer may not be an artifact author")
    return errors


def markdown_path_value(value: str) -> str:
    match = re.search(r"`([^`]+)`", value)
    if match:
        return match.group(1).strip()
    return value.strip().split()[0] if value.strip() else ""


def concrete_value_errors(
    content: str,
    fields: tuple[str, ...],
    section_name: str,
    *,
    allow_reasoned_na: set[str] | None = None,
) -> list[str]:
    allowed = allow_reasoned_na or set()
    errors: list[str] = []
    for field in fields:
        values = field_values(content, field)
        if not values:
            errors.append(f"{section_name} missing field: {field}")
            continue
        if len(values) > 1:
            errors.append(f"duplicate field in {section_name}: {field}")
            continue
        value = values[0]
        if is_placeholder(value):
            errors.append(f"{section_name} field is empty or placeholder: {field}")
        elif value.strip().lower().startswith("n/a"):
            if field not in allowed:
                errors.append(f"{section_name} field may not be N/A: {field}")
            elif not has_reasoned_na(value):
                errors.append(f"{section_name} N/A lacks a concrete rationale: {field}")
    return errors


def exact_section_errors(text: str, headings: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    for heading in headings:
        count = section_count(text, heading)
        if count == 0:
            errors.append(f"missing section: {heading}")
        elif count > 1:
            errors.append(f"duplicate authoritative section: {heading}")
    return errors


def cancellation_errors(text: str) -> list[str]:
    heading = "## Human feedback and change record"
    errors = exact_section_errors(text, (heading,))
    if errors:
        return errors
    record = section(text, heading)
    errors.extend(
        concrete_value_errors(record, CANCELLATION_FIELDS, "Cancellation record")
    )
    outcome = field_value(record, "Outcome:").strip().lower()
    classification = field_value(record, "Classification:").strip().lower()
    if outcome not in {"cancelled", "replaced", "cancelled or replaced"}:
        errors.append("cancelled/superseded task requires a cancelled or replaced outcome")
    if classification != "cancelled or replaced scope":
        errors.append("cancelled/superseded task requires cancelled or replaced scope classification")
    if not iso_datetime(field_value(record, "Date:")):
        errors.append("cancelled/superseded task requires an ISO-style date")
    evidence = field_value(record, "Feedback and evidence:")
    linked = field_value(record, "Linked requirements and tasks:")
    if not has_reference(evidence) and not has_reference(linked):
        errors.append("cancelled/superseded task requires source, decision, or task evidence")
    if len(field_value(record, "Next action:").strip()) < 8:
        errors.append("cancelled/superseded task requires a concrete next action or replacement")
    return errors


def state_and_outcome(snapshot: str) -> tuple[str, str]:
    value = field_value(snapshot, "Current state and technical outcome:")
    if "/" not in value:
        return value.strip().lower(), ""
    state, outcome = value.rsplit("/", 1)
    return state.strip().lower(), outcome.strip().lower()


def state_model_errors(snapshot: str) -> list[str]:
    state, outcome = state_and_outcome(snapshot)
    errors: list[str] = []
    if state not in TASK_STATES:
        errors.append(f"invalid task state: {state or 'missing'}")
    if outcome not in TECHNICAL_OUTCOMES:
        errors.append(f"invalid technical outcome: {outcome or 'missing'}")
    if state == "complete" and outcome != "verified-complete":
        errors.append("complete state requires verified-complete technical outcome")
    if outcome == "verified-complete" and state != "complete":
        errors.append("verified-complete technical outcome requires complete state")
    return errors


def delivery_descriptor(snapshot: str) -> tuple[str, str, set[str]]:
    value = field_value(snapshot, LANE_FIELD)
    parts = [part.strip() for part in value.split("/", 2)]
    lane = parts[0].lower() if parts else ""
    complexity = parts[1].lower() if len(parts) > 1 else ""
    trigger_text = parts[2].lower() if len(parts) > 2 else ""
    triggers = {
        trigger
        for trigger in CONTROL_TRIGGERS
        if re.search(rf"\b{re.escape(trigger)}\b", trigger_text)
    }
    return lane, complexity, triggers


def lane_section_heading(lane: str, kind: str) -> str:
    contract = LANE_CONTRACTS.get(lane, {})
    section_name = contract.get(f"{kind}_section", "")
    return f"## {section_name}" if section_name else ""


def manifest_revision(text: str) -> str:
    planning = section(text, "## Plan and readiness")
    return first_identifier(
        field_value(planning, "Test Manifest revision and frozen-at:"), "TEM"
    )


def actor_identities(snapshot: str) -> set[str]:
    return identifiers(field_value(snapshot, "Actor identities:"), "AGENT")


def snapshot_semantic_errors(snapshot: str) -> list[str]:
    errors: list[str] = []
    revision = field_value(snapshot, "Workflow revision:")
    if revision.strip(" `") != WORKFLOW_REVISION:
        errors.append(
            f"snapshot workflow revision must be {WORKFLOW_REVISION}, got {revision or 'missing'}"
        )
    snapshot_id = field_value(snapshot, "Snapshot ID and updated at:")
    if not re.search(r"\bSNAP-[A-Za-z0-9._-]+\b", snapshot_id, flags=re.IGNORECASE):
        errors.append("strict snapshot ID must contain a concrete SNAP-... identifier")
    if not re.search(r"\b\d{4}-\d{2}-\d{2}(?=[T\s]|$)", snapshot_id):
        errors.append("strict snapshot updated-at must contain an ISO-style date")
    references = field_value(
        snapshot, "Scope, source, decision, and contract references:"
    )
    if not REFERENCE_PATTERN.search(references):
        errors.append("strict scope/source/decision references need an ID, URL, or backticked path")
    lane, complexity, triggers = delivery_descriptor(snapshot)
    if lane not in LANES:
        errors.append(f"invalid delivery lane: {lane or 'missing'}")
    if complexity not in COMPLEXITIES:
        errors.append(f"invalid complexity: {complexity or 'missing'}")
    descriptor = field_value(snapshot, LANE_FIELD)
    if not triggers:
        errors.append("delivery descriptor requires a recognized control trigger")
    elif "none" in triggers:
        trigger_part = descriptor.split("/", 2)[-1].strip()
        rationale = re.sub(r"^none\s*(?:[-—:]\s*)?", "", trigger_part, flags=re.IGNORECASE)
        if len(triggers) != 1 or len(rationale.strip()) < 5:
            errors.append("control trigger none requires one concrete rationale and no other trigger")
    elif lane == "high-risk" and not triggers.intersection(
        {"interface", "security", "runtime-chain", "baseline-change"}
    ):
        errors.append("high-risk lane requires a material control trigger")
    batch = field_value(snapshot, "Batch / dependencies / entry:")
    if len(batch.strip()) < 12:
        errors.append("batch/dependencies/entry must record concrete entry evidence")
    actors = actor_identities(snapshot)
    if len(actors) < 4:
        errors.append("Actor identities require product, technical, implementer, and verifier AGENT IDs")
    next_action = field_value(snapshot, "Next action, exit condition, and invalidation:")
    if len(next_action.strip()) < 12:
        errors.append("strict next action/exit/invalidation is too short to be actionable")
    elif not re.search(r"\bexit\b|退出|完成条件|结束条件", next_action, flags=re.IGNORECASE):
        errors.append("strict next action must state an exit/completion condition")
    if not re.search(r"invalidate|失效|变化|变更", next_action, flags=re.IGNORECASE):
        errors.append("strict next action must state invalidation conditions")
    errors.extend(state_model_errors(snapshot))
    return errors


def resolve_project_layout(task_card: Path) -> tuple[Path | None, Path | None, str | None]:
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
        return None, None, "validation requires an ancestor .ai-team/manifest.md"
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
        card_path.relative_to(task_root)
    except ValueError:
        return None, None, "task card or Task root is outside the manifest-declared .ai-team scope"
    return project_root, task_root, None


def fingerprint_entries(text: str) -> list[tuple[str, str]]:
    snapshot = visible_markdown(section(text, "## Handoff Snapshot"))
    return re.findall(
        r"^[ \t]*-[ \t]*`([^`\n]+)`[ \t]*=[ \t]*([0-9a-fA-F]{64})[ \t]*$",
        snapshot,
        flags=re.MULTILINE,
    )


def inventory_paths(text: str) -> list[str]:
    snapshot = section(text, "## Handoff Snapshot")
    return re.findall(r"`([^`\n]+)`", field_value(snapshot, CHANGE_INVENTORY_FIELD))


def task_dependencies(text: str) -> set[str]:
    snapshot = section(text, "## Handoff Snapshot")
    value = field_value(snapshot, "Batch / dependencies / entry:")
    parts = value.split("/", 2)
    return identifiers(parts[1], "TASK") if len(parts) > 1 else set()


def fast_change_surface_errors(text: str) -> list[str]:
    """Keep Fast work on explicitly declared non-production-code surfaces."""
    inventory = inventory_paths(text)
    if not inventory:
        return ["Fast task requires concrete change-set inventory paths"]
    patterns = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in LANE_CONTRACTS["fast"]["allowed_inventory_patterns"]
    ]
    errors: list[str] = []
    for raw in inventory:
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"Fast inventory path must be project-relative: {raw}")
        elif not any(pattern.search(raw) for pattern in patterns):
            errors.append(
                f"Fast inventory path is outside the allowed non-behavior surfaces; use Standard: {raw}"
            )
    return errors


def inventory_ledger_errors(text: str) -> list[str]:
    inventory = inventory_paths(text)
    ledger = [path for path, _ in fingerprint_entries(text)]
    errors: list[str] = []
    if len(inventory) != len(set(inventory)):
        errors.append("Change-set file inventory contains duplicate paths")
    if len(ledger) != len(set(ledger)):
        errors.append("fingerprint ledger contains duplicate paths")
    missing = sorted(set(inventory) - set(ledger))
    extra = sorted(set(ledger) - set(inventory))
    if missing:
        errors.append(f"fingerprint ledger is missing inventory paths: {', '.join(missing)}")
    if extra:
        errors.append(f"fingerprint ledger has paths absent from inventory: {', '.join(extra)}")
    return errors


def project_authority_errors_from_root(project_root: Path) -> list[str]:
    project_root = project_root.resolve()
    ai_team_root = project_root / ".ai-team"
    manifest_path = ai_team_root / "manifest.md"
    if not manifest_path.is_file():
        return ["project consistency requires .ai-team/manifest.md"]
    manifest_text = manifest_path.read_text(encoding="utf-8")
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


def project_authority_errors(task_card: Path) -> list[str]:
    project_root, _, layout_error = resolve_project_layout(task_card)
    if layout_error:
        return [layout_error]
    assert project_root is not None
    return project_authority_errors_from_root(project_root)


def project_stage_errors(task_card: Path, gate: str) -> list[str]:
    project_root, _, layout_error = resolve_project_layout(task_card)
    if layout_error:
        return [layout_error]
    assert project_root is not None
    manifest_text = (project_root / ".ai-team/manifest.md").read_text(encoding="utf-8")
    stage_value = markdown_path_value(field_value(manifest_text, "Project stage:"))
    if not stage_value:
        return ["layout manifest is missing Project stage:"]
    stage_path = (project_root / stage_value).resolve()
    if not stage_path.is_file():
        return [f"project stage file not found: {stage_value}"]
    stage_text = visible_markdown(stage_path.read_text(encoding="utf-8"))
    stage = field_value(stage_text, "Stage:").strip().lower()
    authority = field_value(stage_text, "Authority:")
    scope = field_value(stage_text, "Scope:")
    updated = field_value(stage_text, "Updated at:")
    errors: list[str] = []
    if stage not in set(WORKFLOW_SCHEMA["enums"]["project_stages"]):
        errors.append(f"invalid project stage: {stage or 'missing'}")
    allowed = set(WORKFLOW_SCHEMA["stage_authority"].get(gate, ()))
    if allowed and stage not in allowed:
        errors.append(
            f"project stage {stage or 'missing'} does not authorize {gate}; allowed: {', '.join(sorted(allowed))}"
        )
    if is_placeholder(authority) or len(authority.strip()) < 12:
        errors.append("project stage requires concrete authority provenance")
    if is_placeholder(scope):
        errors.append("project stage requires a concrete scope")
    elif gate in {"implementation-ready", "verified-complete"}:
        task_id = first_identifier(task_card.stem, "TASK")
        scope_lower = scope.strip().lower()
        if scope_lower != "all tasks" and (
            not task_id or task_id not in identifiers(scope, "TASK")
        ):
            errors.append(
                f"project stage scope does not authorize current task: {task_id or task_card.name}"
            )
    if not iso_datetime(updated):
        errors.append("project stage Updated at needs an ISO-style date")
    return errors


def source_register_errors(source: Path) -> list[str]:
    text = source.read_text(encoding="utf-8")
    product = section(text, "## Product requirement source")
    if not product:
        return ["Source register is not initialized from the canonical schema"]
    errors = concrete_value_errors(
        product,
        SOURCE_REGISTER_FIELDS,
        "Source register product requirement source",
        allow_reasoned_na={"Version or updated at:"},
    )
    source_type = field_value(product, "Type:").strip().lower()
    if source_type not in {"prd", "initial user request"}:
        errors.append("Source register Type must be PRD or initial user request")
    status = field_value(product, "Status:").strip().lower()
    if status not in {"provided", "no-prd intake"}:
        errors.append("current Source register Status must be provided or no-prd intake")
    request = field_value(product, "URL or verbatim request:")
    if len(request.strip()) < 10:
        errors.append("Source register needs a concrete URL or verbatim initial request")
    read_at = field_value(product, "Read at:")
    if not re.search(r"\b\d{4}-\d{2}-\d{2}(?=[T\s]|$)", read_at):
        errors.append("Source register Read at needs an ISO-style date")
    return errors


def acceptance_spec_errors(path: Path) -> tuple[list[str], set[str], set[str]]:
    text = path.read_text(encoding="utf-8")
    required = (
        "## Requirement source and intake state",
        "## Scope",
        "## Requirements",
        "## User stories and acceptance criteria",
    )
    errors = exact_section_errors(text, required)
    if errors:
        return errors, set(), set()
    intake = section(text, required[0])
    scope = section(text, required[1])
    requirements = section(text, required[2])
    acceptance = section(text, required[3])
    errors.extend(
        concrete_value_errors(
            intake,
            ACCEPTANCE_INTAKE_FIELDS,
            "Acceptance specification intake",
            allow_reasoned_na={
                "Conventional low-risk MVP assumptions and rationale:",
            },
        )
    )
    errors.extend(
        concrete_value_errors(scope, ACCEPTANCE_SCOPE_FIELDS, "Acceptance specification scope")
    )
    if field_value(intake, "Status:").strip().lower() != "frozen":
        errors.append("Acceptance specification must be frozen before task promotion")
    product_analyst = first_identifier(field_value(intake, "Product analyst:"), "AGENT")
    review = field_value(intake, "Independent review:")
    independent_verifier = first_identifier(review, "AGENT")
    if not product_analyst:
        errors.append("Acceptance specification requires an AGENT-... product analyst")
    if not independent_verifier or independent_verifier == product_analyst:
        errors.append("Acceptance specification requires a distinct AGENT-... independent verifier")
    if "PASS" not in {part.strip().upper() for part in review.split("/")}:
        errors.append("Acceptance specification independent review requires PASS")
    if not first_identifier(review, "EVID"):
        errors.append("Acceptance specification independent review requires EVID-... evidence")
    if not re.search(r"\b\d{4}-\d{2}-\d{2}(?=[T\s]|$)", review):
        errors.append("Acceptance specification independent review requires an ISO-style date")
    if not is_none(field_value(intake, "Awaiting material human decision:")):
        errors.append("Acceptance specification has an unresolved material human decision")
    requirement_ids = identifiers(requirements, "REQ")
    acceptance_ids = identifiers(acceptance, "AC")
    mapped_requirements = identifiers(acceptance, "REQ")
    if not requirement_ids:
        errors.append("Acceptance specification requires a REQ-... catalog")
    if not acceptance_ids:
        errors.append("Acceptance specification requires AC-... criteria")
    missing_requirement_links = mapped_requirements - requirement_ids
    if missing_requirement_links:
        errors.append(
            "Acceptance criteria reference unknown requirements: "
            + ", ".join(sorted(missing_requirement_links))
        )
    return errors, requirement_ids, acceptance_ids


def traceability_matrix_errors(
    path: Path, expected_requirements: set[str], expected_acceptance: set[str]
) -> tuple[
    list[str],
    set[str],
    set[str],
    dict[str, tuple[set[str], set[str], set[str]]],
]:
    lines = visible_markdown(path.read_text(encoding="utf-8")).splitlines()
    errors: list[str] = []
    header_index: int | None = None
    columns: list[str] = []
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        candidate = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if candidate and candidate[0] == "Requirement":
            header_index = index
            columns = candidate
            break
    if header_index is None:
        return ["Requirement traceability matrix is missing its canonical table"], set(), set(), {}
    if tuple(columns) != TRACEABILITY_COLUMNS:
        errors.append(
            "Requirement traceability columns must be: " + " | ".join(TRACEABILITY_COLUMNS)
        )
    seen_requirements: set[str] = set()
    seen_acceptance: set[str] = set()
    mappings: dict[str, tuple[set[str], set[str], set[str]]] = {}
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != len(columns):
            errors.append("Requirement traceability row has the wrong number of cells")
            continue
        row = dict(zip(columns, cells))
        requirement = first_identifier(row.get("Requirement", ""), "REQ")
        if not requirement:
            errors.append("Requirement traceability row requires one REQ-... ID")
            continue
        if requirement in seen_requirements:
            errors.append(f"duplicate Requirement traceability row: {requirement}")
        seen_requirements.add(requirement)
        state = row.get("State", "").strip().lower()
        if state not in {"covered", "out of scope", "awaiting decision"}:
            errors.append(f"invalid traceability state for {requirement}: {state or 'missing'}")
        classification = row.get("Requirement source and classification", "").lower()
        if not any(
            marker in classification
            for marker in ("evidence-backed", "low-risk assumption", "awaiting decision")
        ):
            errors.append(f"traceability source classification is missing for {requirement}")
        row_acceptance = identifiers(row.get("Acceptance criteria", ""), "AC")
        row_tasks = identifiers(row.get("Design and task", ""), "TASK")
        row_tests = identifiers(row.get("Test case/method", ""), "TEST")
        mappings[requirement] = (row_acceptance, row_tasks, row_tests)
        seen_acceptance |= row_acceptance
        if state == "covered":
            if not row_acceptance:
                errors.append(f"covered requirement lacks AC mapping: {requirement}")
            if not row_tasks:
                errors.append(f"covered requirement lacks TASK mapping: {requirement}")
            if not row_tests:
                errors.append(f"covered requirement lacks TEST mapping: {requirement}")
        elif state == "awaiting decision" and not identifiers(
            row.get("Decision", ""), "DEC"
        ):
            errors.append(f"awaiting-decision requirement lacks DEC mapping: {requirement}")
    if seen_requirements != expected_requirements:
        errors.append(
            "Requirement catalog/traceability mismatch: acceptance="
            + ",".join(sorted(expected_requirements))
            + " matrix="
            + ",".join(sorted(seen_requirements))
        )
    unknown_acceptance = seen_acceptance - expected_acceptance
    if unknown_acceptance:
        errors.append(
            "Requirement traceability references unknown acceptance criteria: "
            + ", ".join(sorted(unknown_acceptance))
        )
    orphan_acceptance = expected_acceptance - seen_acceptance
    if orphan_acceptance:
        errors.append(
            "Acceptance criteria missing from Requirement traceability: "
            + ", ".join(sorted(orphan_acceptance))
        )
    return errors, seen_requirements, seen_acceptance, mappings


def project_spec_errors(task_card: Path, text: str) -> list[str]:
    project_root, _, layout_error = resolve_project_layout(task_card)
    if layout_error:
        return [layout_error]
    assert project_root is not None
    manifest = (project_root / ".ai-team/manifest.md").read_text(encoding="utf-8")
    paths: dict[str, Path] = {}
    errors: list[str] = []
    missing_files: list[str] = []
    for field in ("Acceptance specification:", "Requirement traceability:"):
        value = markdown_path_value(field_value(manifest, field))
        candidate = Path(value)
        if not value or candidate.is_absolute():
            errors.append(f"layout manifest is missing a project-relative {field}")
            continue
        resolved = (project_root / candidate).resolve()
        try:
            resolved.relative_to(project_root / ".ai-team")
        except ValueError:
            errors.append(f"layout manifest {field} must remain under .ai-team/")
            continue
        if not resolved.is_file():
            missing_files.append(field)
            continue
        paths[field] = resolved
    snapshot = section(text, "## Handoff Snapshot")
    lane, _, _ = delivery_descriptor(snapshot)
    if lane == "fast" and len(missing_files) == 2 and not errors:
        return []
    errors.extend(f"manifest-declared {field} file is missing" for field in missing_files)
    if errors:
        return errors
    acceptance_errors, requirement_ids, acceptance_ids = acceptance_spec_errors(
        paths["Acceptance specification:"]
    )
    acceptance_intake = section(
        paths["Acceptance specification:"].read_text(encoding="utf-8"),
        "## Requirement source and intake state",
    )
    if not first_existing_project_path(
        project_root, field_value(acceptance_intake, "Independent review:")
    ):
        acceptance_errors.append(
            "Acceptance specification independent review has no existing evidence file"
        )
    matrix_errors, _, _, mappings = traceability_matrix_errors(
        paths["Requirement traceability:"], requirement_ids, acceptance_ids
    )
    errors.extend(acceptance_errors)
    errors.extend(matrix_errors)
    mapping = field_value(
        snapshot, "Scope, source, decision, and contract references:"
    )
    task_requirements = identifiers(mapping, "REQ")
    task_acceptance = identifiers(mapping, "AC")
    task_tests = identifiers(mapping, "TEST")
    if task_requirements or task_acceptance:
        unknown_requirements = task_requirements - requirement_ids
        unknown_acceptance = task_acceptance - acceptance_ids
        if unknown_requirements:
            errors.append(
                "task references requirements absent from the frozen acceptance specification: "
                + ", ".join(sorted(unknown_requirements))
            )
        if unknown_acceptance:
            errors.append(
                "task references acceptance criteria absent from the frozen acceptance specification: "
                + ", ".join(sorted(unknown_acceptance))
            )
        mapped_acceptance = set().union(
            *(mappings.get(requirement, (set(), set(), set()))[0] for requirement in task_requirements)
        ) if task_requirements else set()
        if task_acceptance - mapped_acceptance:
            errors.append(
                "task REQ/AC mapping is inconsistent with Requirement traceability: "
                + ", ".join(sorted(task_acceptance - mapped_acceptance))
            )
        mapped_tests = set().union(
            *(mappings.get(requirement, (set(), set(), set()))[2] for requirement in task_requirements)
        ) if task_requirements else set()
        if task_tests - mapped_tests:
            errors.append(
                "task TEST mapping is inconsistent with Requirement traceability: "
                + ", ".join(sorted(task_tests - mapped_tests))
            )
        title = re.search(r"^#\s+[^\n]+", visible_markdown(text), flags=re.MULTILINE)
        task_id = first_identifier(title.group(0) if title else "", "TASK")
        for requirement in task_requirements:
            mapped_tasks = mappings.get(requirement, (set(), set(), set()))[1]
            if task_id and task_id not in mapped_tasks:
                errors.append(
                    f"Requirement traceability does not map {requirement} to {task_id}"
                )
    return errors


def project_source_errors(task_card: Path) -> list[str]:
    project_root, _, layout_error = resolve_project_layout(task_card)
    if layout_error:
        return [layout_error]
    assert project_root is not None
    manifest = (project_root / ".ai-team/manifest.md").read_text(encoding="utf-8")
    source_value = markdown_path_value(field_value(manifest, "Source register:"))
    if not source_value:
        return ["layout manifest is missing Source register:"]
    candidate = Path(source_value)
    if candidate.is_absolute():
        return ["layout manifest Source register must be project-relative"]
    source = (project_root / candidate).resolve()
    try:
        source.relative_to(project_root / ".ai-team")
    except ValueError:
        return ["layout manifest Source register must remain under .ai-team/"]
    if not source.is_file():
        return ["manifest-declared Source register is missing"]
    return source_register_errors(source)


def first_existing_project_path(project_root: Path, value: str) -> Path | None:
    for raw in re.findall(r"`([^`]+)`", value):
        candidate = Path(raw)
        if candidate.is_absolute():
            continue
        resolved = (project_root / candidate).resolve()
        try:
            resolved.relative_to(project_root)
        except ValueError:
            continue
        if resolved.is_file():
            return resolved
    return None


def iso_datetime(value: str) -> datetime | None:
    match = re.search(r"\d{4}-\d{2}-\d{2}(?:[T\s][0-9:.+-]+Z?)?", value)
    if not match:
        return None
    raw = match.group(0).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def engineering_baseline_errors(path: Path) -> list[str]:
    state = section(path.read_text(encoding="utf-8"), "## State")
    fields = (
        "Version:",
        "Mode:",
        "Status:",
        "Technical lead:",
        "Independent verifier:",
        "Reviewed scope and verdict:",
    )
    errors = concrete_value_errors(state, fields, "Engineering baseline State")
    if field_value(state, "Status:").strip().lower() != "engineering baseline pass":
        errors.append("linked engineering baseline has not recorded Engineering baseline PASS")
    errors.extend(
        identity_errors(
            field_value(state, "Technical lead:"),
            field_value(state, "Independent verifier:"),
            "Engineering baseline",
        )
    )
    return errors


def experience_brief_errors(path: Path) -> list[str]:
    state = section(path.read_text(encoding="utf-8"), "## State and scope")
    fields = (
        "Status:",
        "Product analyst:",
        "UX/UI designer:",
        "Linked requirements and acceptance criteria:",
        "Source basis:",
    )
    errors = concrete_value_errors(state, fields, "Experience design State and scope")
    if field_value(state, "Status:").strip().lower() != "frozen":
        errors.append("linked experience-design brief must be frozen before task design")
    for field in ("Product analyst:", "UX/UI designer:"):
        if not first_identifier(field_value(state, field), "AGENT"):
            errors.append(f"Experience design requires a concrete AGENT-... identity: {field}")
    return errors


def review_evidence_errors(
    path: Path,
    snapshot_id: str,
    manifest_id: str,
    expected_reviewer: str,
    *,
    require_pass: bool,
    expected_role: str | None = None,
    expected_phase: str | None = None,
    bind_current_snapshot: bool = True,
    bind_current_manifest: bool = True,
    allow_conditional_pass: bool = False,
) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = concrete_value_errors(text, REVIEW_EVIDENCE_FIELDS, "Review evidence record")
    reviewer = first_identifier(field_value(text, "Reviewer identity:"), "AGENT")
    if not reviewer:
        errors.append("Review evidence record requires an AGENT-... reviewer identity")
    expected = first_identifier(expected_reviewer, "AGENT")
    if expected and reviewer != expected:
        errors.append("Review evidence reviewer does not match the task-card reviewer identity")
    binding = field_value(text, "Snapshot and Manifest:").upper()
    if bind_current_snapshot and snapshot_id not in binding:
        errors.append("Review evidence record is not bound to the current Snapshot")
    if bind_current_manifest and (not manifest_id or manifest_id not in binding):
        errors.append("Review evidence record is not bound to the current Manifest")
    if not first_identifier(binding, "SNAP"):
        errors.append("Review evidence record requires a concrete Snapshot ID")
    if bind_current_manifest and not first_identifier(binding, "TEM"):
        errors.append("Review evidence record requires a concrete Manifest ID")
    role = field_value(text, "Role:").strip().lower()
    if role not in {"independent verifier", "code and security reviewer"}:
        errors.append("Review evidence record has an invalid reviewer Role")
    if expected_role and role != expected_role:
        errors.append(f"Review evidence record Role must be {expected_role}")
    phase = field_value(text, "Review phase:").strip().lower()
    if expected_phase and phase != expected_phase:
        errors.append(f"Review evidence record phase must be {expected_phase}")
    for field in (
        "Reviewed scope and inputs:",
        "Commands or inspection performed:",
        "Evidence and findings:",
    ):
        value = field_value(text, field)
        if is_none(value) or len(value.strip()) < 12:
            errors.append(f"Review evidence record lacks concrete content: {field}")
    verdict = field_value(text, "Verdict:").strip().lower()
    if require_pass and not (
        is_pass(verdict)
        or (allow_conditional_pass and verdict.startswith("conditional-pass"))
    ):
        errors.append("Review evidence record requires a PASS verdict")
    if not re.search(
        r"\b\d{4}-\d{2}-\d{2}(?=[T\s]|$)", field_value(text, "Recorded at:")
    ):
        errors.append("Review evidence record requires an ISO-style recorded-at date")
    return errors


# Compact current-revision task validation. Project-wide facts stay in project artifacts; task cards
# contain only the current task delta, gate summaries, and evidence links.


def actor_identity(snapshot: str, role: str) -> str:
    value = field_value(snapshot, "Actor identities:")
    match = re.search(
        rf"\b{re.escape(role)}\s*=\s*(AGENT-[A-Za-z0-9._-]+)", value, re.IGNORECASE
    )
    return match.group(1).upper() if match else ""


def separate_review_required(text: str) -> bool:
    lane, _, triggers = delivery_descriptor(section(text, "## Handoff Snapshot"))
    return lane == "high-risk" or bool(
        triggers.intersection({"interface", "security", "runtime-chain", "baseline-change"})
    )


def trigger_errors(text: str) -> list[str]:
    snapshot = section(text, "## Handoff Snapshot")
    lane, _, triggers = delivery_descriptor(snapshot)
    planning = section(text, "## Plan and readiness")
    errors: list[str] = []
    if lane == "fast" and triggers != {"none"}:
        errors.append("Fast lane may use only a reasoned none control trigger")
    if "testsprite" in triggers and "web-ui" not in triggers:
        errors.append("TestSprite trigger requires the web-ui trigger")
    if "experience" in triggers:
        refs = field_value(planning, "Baseline and design references:")
        if not PROJECT_PATH_PATTERN.search(refs):
            errors.append("experience trigger requires a linked experience-design reference")
    if triggers.intersection({"web-ui", "testsprite"}):
        combined = field_value(
            snapshot, "Scope, source, decision, and contract references:"
        ) + field_value(planning, "Independent task verification:")
        if not identifiers(combined, "TEST"):
            errors.append("Web UI control requires provider-neutral TEST IDs")
    if "interface" in triggers:
        refs = field_value(
            snapshot, "Scope, source, decision, and contract references:"
        )
        checks = field_value(planning, "Risk and contract checks:")
        if not PROJECT_PATH_PATTERN.search(refs):
            errors.append("interface trigger requires a frozen contract reference")
        if not identifiers(checks, "TEST"):
            errors.append("interface trigger requires contract TEST IDs")
    for trigger, heading, fields in (
        ("security", "## Security impact", SECURITY_FIELDS),
        ("runtime-chain", "## Runtime-chain matrix", RUNTIME_FIELDS),
    ):
        if trigger not in triggers:
            if section(text, heading):
                errors.append(f"{heading.lstrip('# ')} exists without its control trigger")
            continue
        errors.extend(exact_section_errors(text, (heading,)))
        annex = section(text, heading)
        if annex:
            errors.extend(concrete_value_errors(annex, fields, heading.lstrip("# ")))
            for field in fields:
                if has_reasoned_na(field_value(annex, field)):
                    errors.append(f"{heading.lstrip('# ')} field may not be N/A: {field}")
    if "testsprite" in triggers:
        heading = "## TestSprite MCP (authorized Web UI only)"
        errors.extend(exact_section_errors(text, (heading,)))
        annex = section(text, heading)
        if annex:
            errors.extend(
                concrete_value_errors(annex, TESTSPRITE_DESIGN_FIELDS, "TestSprite MCP")
            )
    return errors


def planning_errors(text: str) -> list[str]:
    errors = exact_section_errors(text, ("## Plan and readiness",))
    if errors:
        return errors
    planning = section(text, "## Plan and readiness")
    errors.extend(concrete_value_errors(planning, PLANNING_FIELDS, "Plan and readiness"))
    baseline = field_value(planning, "Baseline and design references:")
    if not PROJECT_PATH_PATTERN.search(baseline):
        errors.append("Plan and readiness requires project-relative baseline/design references")
    if not manifest_revision(text):
        errors.append("Plan and readiness requires a TEM-... Test Manifest revision")
    if not iso_datetime(field_value(planning, "Test Manifest revision and frozen-at:")):
        errors.append("Test Manifest requires an ISO-style frozen-at date")
    verifier_report = field_value(planning, "Planning verifier and report:")
    if not first_identifier(verifier_report, "AGENT") or not PROJECT_PATH_PATTERN.search(
        verifier_report
    ):
        errors.append("Planning verifier/report requires an AGENT ID and evidence path")
    lane, _, _ = delivery_descriptor(section(text, "## Handoff Snapshot"))
    batch_regression = field_value(planning, "Batch regression:")
    if lane in {"standard", "high-risk"} and has_reasoned_na(batch_regression):
        errors.append(f"{lane} planning requires a concrete batch or per-task regression command")
    errors.extend(trigger_errors(text))
    return errors


def planning_verdict(text: str) -> str:
    return field_value(
        section(text, "## Plan and readiness"),
        "Design/readiness verdict and conditions:",
    ).strip().lower()


def task_design_common_errors(text: str) -> list[str]:
    errors = planning_errors(text)
    errors.extend(exact_section_errors(text, ("## Acceptance criteria checklist",)))
    snapshot = section(text, "## Handoff Snapshot")
    refs = field_value(snapshot, "Scope, source, decision, and contract references:")
    for prefix in ("REQ", "AC", "TEST"):
        if not identifiers(refs, prefix):
            errors.append(f"task scope requires at least one {prefix}-... reference")
    verdict = planning_verdict(text)
    if not verdict.startswith(("task-design-ready", "implementation-ready", "conditional-pass")):
        errors.append("task design requires a task-design-ready, implementation-ready, or conditional-pass verdict")
    report = field_value(section(text, "## Plan and readiness"), "Planning verifier and report:")
    verifier = first_identifier(report, "AGENT")
    for role in ("product", "technical", "implementer"):
        if verifier and verifier == actor_identity(snapshot, role):
            errors.append(f"planning verifier may not be the {role} artifact author")
    return errors


def readiness_common_errors(text: str) -> list[str]:
    errors = task_design_common_errors(text)
    verdict = planning_verdict(text)
    if verdict.startswith("implementation-ready"):
        pass
    elif verdict.startswith("conditional-pass"):
        if "activated" not in verdict or len(verdict) < 45:
            errors.append("conditional readiness requires activated status and concrete activation evidence")
    else:
        errors.append("implementation-ready gate requires direct PASS or activated conditional-pass")
    snapshot = section(text, "## Handoff Snapshot")
    if not is_none(field_value(snapshot, "Open findings / blockers:")):
        errors.append("implementation-ready gate has open findings or blockers")
    batch = field_value(snapshot, "Batch / dependencies / entry:")
    if len(batch.strip()) < 12:
        errors.append("implementation-ready gate requires batch/dependency entry evidence")
    return errors


def conditional_readiness_errors(text: str) -> list[str]:
    if not section(text, "## Plan and readiness"):
        return []
    verdict = planning_verdict(text)
    if not verdict.startswith("conditional-pass"):
        return []
    state, _ = state_and_outcome(section(text, "## Handoff Snapshot"))
    errors: list[str] = []
    if "activated" in verdict and state not in {
        "implementation-ready", "implementing", "awaiting-verification", "complete"
    }:
        errors.append("activated conditional readiness requires implementation-ready or later state")
    if "pending" in verdict and state != "task-design-ready":
        errors.append("pending conditional readiness must remain task-design-ready")
    if "activated" not in verdict and "pending" not in verdict:
        errors.append("conditional readiness must record pending or activated status")
    return errors


def fast_gate_common_errors(text: str, gate: str) -> list[str]:
    heading = lane_section_heading("fast", "readiness")
    errors = exact_section_errors(text, (heading,))
    if errors:
        return errors
    fast = section(text, heading)
    errors.extend(concrete_value_errors(fast, FAST_GATE_FIELDS, "Fast merged design/readiness"))
    snapshot = section(text, "## Handoff Snapshot")
    refs = field_value(snapshot, "Scope, source, decision, and contract references:")
    for prefix in ("REQ", "AC", "TEST"):
        if not identifiers(refs + field_value(fast, "Scope / acceptance / checks:"), prefix):
            errors.append(f"Fast gate requires {prefix}-... traceability")
    verifier = first_identifier(field_value(fast, "Independent verifier identity:"), "AGENT")
    for role in ("product", "technical", "implementer"):
        if verifier and verifier == actor_identity(snapshot, role):
            errors.append(f"Fast verifier may not be the {role} artifact author")
    if not field_value(fast, "Verdict:").strip().lower().startswith("implementation-ready"):
        errors.append("Fast gate requires implementation-ready verdict")
    return errors


def implementation_self_check_errors(self_check: str) -> list[str]:
    errors = concrete_value_errors(self_check, SELF_CHECK_FIELDS, "Implementation self-check")
    if re.search(r"\bpending\b|待执行|未执行", visible_markdown(self_check), re.IGNORECASE):
        errors.append("implementation self-check has pending evidence")
    if not first_identifier(field_value(self_check, "Implementation engineer identity:"), "AGENT"):
        errors.append("implementation self-check requires an AGENT-... implementation engineer identity")
    build = field_value(self_check, "Build / generation / lint-typecheck results:")
    if not is_pass(build) and not has_reasoned_na(build):
        errors.append("implementation self-check requires build/lint PASS or reasoned N/A")
    if not is_pass(field_value(self_check, "Owner / affected / contract test results:")):
        errors.append("implementation self-check requires owner/affected/contract test PASS")
    return errors


def fast_implementation_self_check_errors(text: str) -> list[str]:
    heading = lane_section_heading("fast", "execution")
    errors = exact_section_errors(text, (heading,))
    if errors:
        return errors
    completion = section(text, heading)
    value = field_value(completion, "Implementer / self-check / evidence:")
    implementer = first_identifier(value, "AGENT")
    result = re.sub(r"^.*?AGENT-[A-Za-z0-9._-]+\s*/\s*", "", value)
    if not implementer or not is_pass(result):
        errors.append("Fast implementation requires an implementation AGENT and PASS self-check")
    return errors


def active_promotion_errors(text: str, state: str) -> list[str]:
    """Validate an already-promoted task without applying the wrong lane contract."""
    errors = strict_errors(text)
    snapshot = section(text, "## Handoff Snapshot")
    lane, _, _ = delivery_descriptor(snapshot)
    if lane != "fast":
        errors.extend(readiness_common_errors(text))
    if state == "awaiting-verification":
        if lane == "fast":
            errors.extend(fast_implementation_self_check_errors(text))
        else:
            heading = lane_section_heading(lane, "execution")
            errors.extend(implementation_self_check_errors(section(text, heading)))
    return list(dict.fromkeys(errors))


def recorded_findings(text: str) -> tuple[set[str], str]:
    """Return P0/P1/P2 markers and the recorded verifier verdict for routing."""
    snapshot = section(text, "## Handoff Snapshot")
    lane, _, _ = delivery_descriptor(snapshot)
    if lane == "fast":
        completion = section(text, lane_section_heading("fast", "execution"))
        findings = field_value(completion, "Findings / severity / affected / follow-up:")
        verdict = field_value(completion, "Independent verifier / verdict / evidence:")
    else:
        completion = section(text, "## Verification and findings")
        findings = " ".join(
            (
                field_value(completion, "Findings / severity / affected REQ-AC-TEST:"),
                field_value(completion, "Open P0/P1 / P2 follow-up:"),
            )
        )
        verdict = field_value(completion, "Independent verifier verdict:")
    severities = {
        severity for severity in FINDING_SEVERITIES if re.search(rf"\b{severity}\b", findings, re.IGNORECASE)
    }
    return severities, verdict


def completion_binding_errors(text: str, findings: str) -> list[str]:
    snapshot = section(text, "## Handoff Snapshot")
    current_snapshot = first_identifier(
        field_value(snapshot, "Snapshot ID and updated at:"), "SNAP"
    )
    current_manifest = manifest_revision(text)
    binding = field_value(findings, "Verified Snapshot / Manifest / at:")
    errors: list[str] = []
    if not current_snapshot or current_snapshot not in binding:
        errors.append("verified-complete evidence must bind the current SNAP")
    lane, _, _ = delivery_descriptor(snapshot)
    if lane != "fast" and (not current_manifest or current_manifest not in binding):
        errors.append("verified-complete evidence must bind the current TEM")
    if not iso_datetime(binding):
        errors.append("verified-complete evidence requires an ISO-style verification time")
    return errors


def completion_result_errors(self_check: str, findings: str) -> list[str]:
    value = field_value(findings, "Findings / severity / affected REQ-AC-TEST:")
    followup = field_value(findings, "Open P0/P1 / P2 follow-up:")
    errors: list[str] = []
    finding_ids = finding_identifiers(value)
    severities = {severity for severity in FINDING_SEVERITIES if severity in value.upper()}
    if value.strip().lower().startswith("none"):
        if "n/a" not in value.lower() or len(value.strip()) < 16:
            errors.append("no findings require a reasoned N/A severity")
    else:
        if not finding_ids or not severities:
            errors.append("findings require FIND/EVID ID and P0/P1/P2 severity")
        if severities.intersection({"P0", "P1"}) and is_none(followup):
            errors.append("P0/P1 findings must remain open and block completion")
        if "P2" in severities and not identifiers(followup, "TASK"):
            errors.append("P2 findings require a TASK follow-up")
    return errors


def completion_identity_errors(text: str, self_check: str, findings: str) -> list[str]:
    snapshot = section(text, "## Handoff Snapshot")
    implementer = first_identifier(
        field_value(self_check, "Implementation engineer identity:"), "AGENT"
    )
    verifier = first_identifier(field_value(findings, "Independent verifier identity:"), "AGENT")
    reviewer = first_identifier(
        field_value(findings, "Separate code/security reviewer identity:"), "AGENT"
    )
    errors: list[str] = []
    for role in ("product", "technical"):
        if implementer and implementer == actor_identity(snapshot, role):
            errors.append(f"implementation engineer may not be the {role} artifact author")
        if verifier and verifier == actor_identity(snapshot, role):
            errors.append(f"independent verifier may not be the {role} artifact author")
    if implementer and verifier == implementer:
        errors.append("implementation engineer and independent verifier identities must differ")
    if reviewer and reviewer in {implementer, verifier}:
        errors.append("separate code/security reviewer must differ from implementer and verifier")
    return errors


def fast_completion_errors(text: str) -> list[str]:
    heading = lane_section_heading("fast", "execution")
    errors = exact_section_errors(text, (heading,))
    if errors:
        return errors
    completion = section(text, heading)
    errors.extend(
        concrete_value_errors(completion, FAST_COMPLETION_FIELDS, "Fast execution and verification")
    )
    implementer_value = field_value(completion, "Implementer / self-check / evidence:")
    verifier_value = field_value(
        completion, "Independent verifier / verdict / evidence:"
    )
    implementer = first_identifier(implementer_value, "AGENT")
    verifier = first_identifier(verifier_value, "AGENT")
    implementer_result = re.sub(
        r"^.*?AGENT-[A-Za-z0-9._-]+\s*/\s*", "", implementer_value
    )
    if not implementer or not is_pass(implementer_result):
        errors.append("Fast completion requires an implementation AGENT and PASS self-check")
    if not verifier or not is_pass(re.sub(r"^.*?AGENT-[A-Za-z0-9._-]+\s*/\s*", "", verifier_value)):
        errors.append("Fast completion requires an independent verifier AGENT and PASS verdict")
    if implementer and verifier == implementer:
        errors.append("Fast implementer and verifier identities must differ")
    findings = field_value(completion, "Findings / severity / affected / follow-up:")
    if re.search(r"\b(?:P0|P1|FIND-P[01])\b", findings, re.IGNORECASE):
        errors.append("verified-complete Fast gate has unresolved P0/P1 findings")
    if "P2" in findings.upper() and not identifiers(findings, "TASK"):
        errors.append("Fast P2 finding requires a TASK follow-up")
    binding = field_value(completion, "Verified Snapshot / at:")
    snapshot_id = first_identifier(
        field_value(section(text, "## Handoff Snapshot"), "Snapshot ID and updated at:"),
        "SNAP",
    )
    if not snapshot_id or snapshot_id not in binding or not iso_datetime(binding):
        errors.append("Fast completion must bind current Snapshot and verification time")
    acceptance = field_value(
        section(text, lane_section_heading("fast", "readiness")), "Scope / acceptance / checks:"
    )
    if not is_pass(acceptance):
        errors.append("verified-complete Fast gate requires PASS acceptance/check evidence")
    return errors


def verification_errors(text: str) -> list[str]:
    lane, _, _ = delivery_descriptor(section(text, "## Handoff Snapshot"))
    if lane == "fast":
        return fast_completion_errors(text)
    errors = exact_section_errors(
        text, ("## Implementation self-check", "## Verification and findings")
    )
    if errors:
        return errors
    self_check = section(text, "## Implementation self-check")
    findings = section(text, "## Verification and findings")
    errors.extend(implementation_self_check_errors(self_check))
    errors.extend(
        concrete_value_errors(
            findings,
            VERIFICATION_FIELDS,
            "Verification and findings",
            allow_reasoned_na={
                "Separate code/security reviewer identity:",
                "Separate code/security reviewer verdict:",
                "Separate code/security review evidence:",
            },
        )
    )
    verifier = field_value(findings, "Independent verifier verdict:")
    if not is_pass(verifier):
        errors.append("verified-complete gate requires a fresh independent verifier PASS")
    if separate_review_required(text):
        if not first_identifier(
            field_value(findings, "Separate code/security reviewer identity:"), "AGENT"
        ):
            errors.append("triggered work requires a separate code/security reviewer identity")
        if not is_pass(field_value(findings, "Separate code/security reviewer verdict:")):
            errors.append("triggered work requires separate code/security reviewer PASS")
        if not PROJECT_PATH_PATTERN.search(
            field_value(findings, "Separate code/security review evidence:")
        ):
            errors.append("triggered work requires separate code/security review evidence")
    else:
        for field in (
            "Separate code/security reviewer identity:",
            "Separate code/security reviewer verdict:",
            "Separate code/security review evidence:",
        ):
            if not has_reasoned_na(field_value(findings, field)):
                errors.append(f"merged-verifier mode requires a reasoned N/A: {field}")
    if not is_none(field_value(findings, "Open P0/P1 / P2 follow-up:")):
        if re.search(r"\b(?:P0|P1|FIND-P[01])\b", field_value(findings, "Open P0/P1 / P2 follow-up:"), re.IGNORECASE):
            errors.append("verified-complete gate has unresolved P0/P1 findings")
    errors.extend(completion_binding_errors(text, findings))
    errors.extend(completion_result_errors(self_check, findings))
    errors.extend(completion_identity_errors(text, self_check, findings))
    snapshot = section(text, "## Handoff Snapshot")
    if field_value(snapshot, FINGERPRINT_POLICY_FIELD).strip().lower() == "required":
        errors.extend(inventory_ledger_errors(text))
    acceptance = visible_markdown(section(text, "## Acceptance criteria checklist"))
    if re.search(r"^- \[ \]", acceptance, flags=re.MULTILINE):
        errors.append("verified-complete gate has unchecked acceptance criteria")
    if not re.search(r"^- \[[xX]\]", acceptance, flags=re.MULTILINE):
        errors.append("verified-complete gate requires checked acceptance evidence")
    _, _, triggers = delivery_descriptor(snapshot)
    if "testsprite" in triggers:
        testsprite = section(text, "## TestSprite MCP (authorized Web UI only)")
        errors.extend(
            concrete_value_errors(
                testsprite, TESTSPRITE_COMPLETION_FIELDS, "TestSprite MCP completion"
            )
        )
        if not is_pass(field_value(testsprite, "Independent verifier evidence:")):
            errors.append("TestSprite completion requires independent verifier PASS evidence")
    return errors


def strict_errors(text: str) -> list[str]:
    errors = exact_section_errors(text, ("## Handoff Snapshot",))
    if errors:
        return errors
    snapshot = section(text, "## Handoff Snapshot")
    snapshot_errors = concrete_value_errors(
        snapshot,
        SNAPSHOT_FIELDS,
        "Handoff Snapshot",
        allow_reasoned_na={
            "Fingerprint policy:",
            "Current change-set fingerprint:",
        },
    )
    if fingerprint_entries(text):
        snapshot_errors = [
            error for error in snapshot_errors if "Current change-set fingerprint:" not in error
        ]
    errors.extend(snapshot_errors)
    errors.extend(snapshot_semantic_errors(snapshot))
    lane, _, _ = delivery_descriptor(snapshot)
    if lane == "fast":
        errors.extend(fast_gate_common_errors(text, "strict"))
        errors.extend(fast_change_surface_errors(text))
    else:
        errors.extend(planning_errors(text))
    policy = field_value(snapshot, FINGERPRINT_POLICY_FIELD).strip().lower()
    if policy == "required":
        if not fingerprint_entries(text):
            errors.append("required fingerprint policy needs a SHA-256 ledger")
    elif policy.startswith("n/a"):
        if lane != "fast" or not has_reasoned_na(policy):
            errors.append("fingerprint N/A is allowed only for an eligible Fast task")
    else:
        errors.append("Fingerprint policy must be required or a reasoned Fast N/A")
    for heading in (
        "## Handoff Snapshot", "## Plan and readiness", "## Fast merged design/readiness",
        "## Acceptance criteria checklist", "## Implementation self-check",
        "## Verification and findings", "## Fast execution and verification",
        "## Security impact", "## Runtime-chain matrix",
    ):
        if section_count(text, heading) > 1:
            errors.append(f"duplicate authoritative section: {heading}")
    state, _ = state_and_outcome(snapshot)
    if state == "cancelled/superseded":
        errors.extend(cancellation_errors(text))
    return errors


def gate_errors(text: str, gate: str) -> list[str]:
    snapshot = section(text, "## Handoff Snapshot")
    state, outcome = state_and_outcome(snapshot)
    lane, _, _ = delivery_descriptor(snapshot)
    errors = fast_gate_common_errors(text, gate) if lane == "fast" else task_design_common_errors(text)
    if gate == "task-design":
        if (state, outcome) != ("task-design-ready", "not-complete"):
            errors.append("task-design gate requires task-design-ready / not-complete")
        return errors
    if lane != "fast":
        errors.extend(readiness_common_errors(text))
    if gate == "implementation-ready":
        if (state, outcome) != ("implementation-ready", "not-complete"):
            errors.append("implementation-ready gate requires implementation-ready / not-complete")
        return list(dict.fromkeys(errors))
    if (state, outcome) != ("complete", "verified-complete"):
        errors.append("verified-complete gate requires complete / verified-complete")
    errors.extend(verification_errors(text))
    return list(dict.fromkeys(errors))


def gate_reference_errors(task_card: Path, text: str, gate: str) -> list[str]:
    project_root, _, layout_error = resolve_project_layout(task_card)
    if layout_error:
        return [layout_error]
    assert project_root is not None
    snapshot = section(text, "## Handoff Snapshot")
    lane, _, _ = delivery_descriptor(snapshot)
    snapshot_id = first_identifier(field_value(snapshot, "Snapshot ID and updated at:"), "SNAP")
    manifest_id = manifest_revision(text)
    errors: list[str] = []

    def evidence_errors(path: Path, findings: list[str]) -> list[str]:
        location = path.relative_to(project_root)
        return [f"{location}: {finding}" for finding in findings]

    if lane == "fast":
        planning_section = section(text, lane_section_heading("fast", "readiness"))
        planning_path_value = field_value(planning_section, "Report:")
        planning_reviewer = field_value(planning_section, "Independent verifier identity:")
        planning_phase = "fast-design-readiness"
    else:
        planning_section = section(text, "## Plan and readiness")
        planning_path_value = field_value(planning_section, "Planning verifier and report:")
        planning_reviewer = planning_path_value
        planning_phase = None
    planning_path = first_existing_project_path(project_root, planning_path_value)
    if not planning_path:
        errors.append("planning/readiness report has no existing evidence file")
    else:
        errors.extend(
            evidence_errors(
                planning_path,
                review_evidence_errors(
                    planning_path,
                    snapshot_id,
                    manifest_id,
                    planning_reviewer,
                    require_pass=True,
                    expected_role="independent verifier",
                    expected_phase=planning_phase,
                    bind_current_snapshot=gate != "verified-complete",
                    bind_current_manifest=lane != "fast",
                    allow_conditional_pass=True,
                ),
            )
        )

    if lane != "fast":
        baseline_refs = field_value(planning_section, "Baseline and design references:")
        paths = re.findall(r"`([^`]+)`", baseline_refs)
        if not paths:
            errors.append("baseline/design references require project-relative evidence paths")
        for raw in paths:
            path = (project_root / raw).resolve()
            try:
                path.relative_to(project_root)
            except ValueError:
                errors.append(f"baseline/design path escapes project: {raw}")
                continue
            if not path.is_file():
                errors.append(f"baseline/design evidence not found: {raw}")

    if gate == "verified-complete":
        if lane == "fast":
            findings = section(text, lane_section_heading("fast", "execution"))
            verify_value = field_value(
                findings, "Independent verifier / verdict / evidence:"
            )
            verifier = verify_value
        else:
            findings = section(text, "## Verification and findings")
            verify_value = field_value(findings, "Independent verification evidence:")
            verifier = field_value(findings, "Independent verifier identity:")
        verify_path = first_existing_project_path(project_root, verify_value)
        if not verify_path:
            errors.append("independent verification has no existing evidence file")
        else:
            errors.extend(
                evidence_errors(
                    verify_path,
                    review_evidence_errors(
                        verify_path,
                        snapshot_id,
                        manifest_id,
                        verifier,
                        require_pass=True,
                        expected_role="independent verifier",
                        expected_phase="verification",
                        bind_current_manifest=lane != "fast",
                    ),
                )
            )
        review_path: Path | None = None
        if lane != "fast" and separate_review_required(text):
            review_value = field_value(findings, "Separate code/security review evidence:")
            review_path = first_existing_project_path(project_root, review_value)
            reviewer = field_value(findings, "Separate code/security reviewer identity:")
            if not review_path:
                errors.append("separate code/security review has no existing evidence file")
            else:
                errors.extend(
                    evidence_errors(
                        review_path,
                        review_evidence_errors(
                            review_path,
                            snapshot_id,
                            manifest_id,
                            reviewer,
                            require_pass=True,
                            expected_role="code and security reviewer",
                            expected_phase="code-security",
                            bind_current_manifest=lane != "fast",
                        ),
                    )
                )
        if verify_path and review_path:
            verify_time = iso_datetime(
                field_value(verify_path.read_text(encoding="utf-8"), "Recorded at:")
            )
            review_time = iso_datetime(
                field_value(review_path.read_text(encoding="utf-8"), "Recorded at:")
            )
            if verify_time and review_time and review_time > verify_time:
                errors.append("separate code/security fast-gate evidence must precede verifier PASS")
    errors.extend(project_spec_errors(task_card, text))
    return list(dict.fromkeys(errors))


def validate(text: str, strict: bool = False, gate: str | None = None) -> list[str]:
    if gate and gate not in GATES:
        return [f"unknown gate: {gate}"]
    errors = strict_errors(text) if strict or gate else exact_section_errors(
        text, ("## Handoff Snapshot",)
    )
    errors.extend(conditional_readiness_errors(text))
    if gate:
        errors.extend(gate_errors(text, gate))
    return list(dict.fromkeys(errors))


def fingerprint_errors(task_card: Path, text: str) -> list[str]:
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
        description="Validate AI-team task structure and promotion/completion gates."
    )
    parser.add_argument("task_card", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Validate current structure, semantics, layout, and required fingerprints without asserting a promotion gate.",
    )
    parser.add_argument(
        "--gate",
        choices=GATES,
        help="Validate the named semantic gate; implies --strict.",
    )
    parser.add_argument(
        "--verify-fingerprint",
        action="store_true",
        help="Verify the explicit SHA-256 ledger without running project commands.",
    )
    args = parser.parse_args()
    text = args.task_card.read_text(encoding="utf-8")
    strict = args.strict or bool(args.gate)
    errors = validate(text, strict=strict, gate=args.gate)
    if strict:
        errors.extend(project_authority_errors(args.task_card))
        errors.extend(project_source_errors(args.task_card))
    if args.gate:
        errors.extend(gate_reference_errors(args.task_card, text, args.gate))
        errors.extend(project_stage_errors(args.task_card, args.gate))
    fingerprint_policy = field_value(
        section(text, "## Handoff Snapshot"), FINGERPRINT_POLICY_FIELD
    ).strip().lower()
    if args.verify_fingerprint or (strict and fingerprint_policy == "required"):
        errors.extend(fingerprint_errors(args.task_card, text))
    errors = list(dict.fromkeys(errors))
    if errors:
        print(f"FAIL {args.task_card}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS {args.task_card}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
