#!/usr/bin/env python3
"""Regression tests for the read-only AI-team project consistency checker."""

from pathlib import Path, PureWindowsPath
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

try:
    from . import check_project_consistency as checker
except ImportError:
    import check_project_consistency as checker


SKILL_ROOT = Path(__file__).resolve().parent.parent
PROJECT_TEMPLATE = SKILL_ROOT / "assets/project-template"
TEMPLATES = PROJECT_TEMPLATE / ".ai-team/governance/templates.md"


def standard_example() -> str:
    match = re.search(
        r"## Implementation-ready Standard task card example.*?```md\n(.*?)\n```",
        TEMPLATES.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("Standard task example not found")
    return match.group(1)


def fast_example() -> str:
    match = re.search(
        r"## Minimal Fast-path task card.*?```md\n(.*?)\n```",
        TEMPLATES.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("Fast task example not found")
    return match.group(1)


def review_record(phase: str) -> str:
    return f"""# EVID-EXAMPLE: Review evidence

- Reviewer identity: AGENT-IV-EXAMPLE
- Role: independent verifier
- Review phase: {phase}
- Snapshot and Manifest: SNAP-EXAMPLE-STD-001-01 / TEM-EXAMPLE-STD-001-01
- Stage binding: N/A — task-bound evidence is checked by the current task gate
- Reviewed scope and inputs: current task design, manifest, and candidate
- Commands or inspection performed: scoped review and command inspection
- Evidence and findings: no blocking discrepancy found
- Verdict: PASS
- Invalidated by: source, design, manifest, candidate, or environment change
- Recorded at: 2026-08-11T11:30+08:00
"""


class ProjectConsistencyTests(unittest.TestCase):
    def test_state_contracts_cover_schema_enums(self) -> None:
        self.assertEqual(
            set(checker.WORKFLOW_SCHEMA["enums"]["task_states"]),
            set(checker.STATE_CONTRACTS),
        )
        for contract in checker.STATE_CONTRACTS.values():
            self.assertTrue(contract["owner_roles"])
            self.assertTrue(contract["next_gates"])
            self.assertLessEqual(contract["owner_roles"], checker.OWNER_ROLES)
            self.assertLessEqual(contract["next_gates"], checker.NEXT_GATES)

    def materialize_project(self, root: Path) -> None:
        shutil.copytree(PROJECT_TEMPLATE, root, dirs_exist_ok=True)
        governance = root / ".ai-team/governance"
        scripts = root / ".ai-team/scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            SKILL_ROOT / "references/delivery-policy.md", governance / "workflow.md"
        )
        shutil.copy2(
            SKILL_ROOT / "references/role-protocol.md", governance / "roles.md"
        )
        shutil.copy2(
            SKILL_ROOT / "references/workflow-schema.json",
            governance / "workflow-schema.json",
        )
        for name in (
            "validate_task_handoff.py",
            "extract_markdown_section.py",
            "check_project_consistency.py",
            "render_fingerprint_ledger.py",
            "intake_package_inventory.py",
        ):
            shutil.copy2(SKILL_ROOT / "scripts" / name, scripts / name)

    def fill_source_register(self, project: Path) -> None:
        source = project / ".ai-team/sources.md"
        text = source.read_text(encoding="utf-8")
        replacements = {
            "- Type: PRD / initial user request": "- Type: initial user request",
            "- URL or verbatim request:": "- URL or verbatim request: Build a local calculator input validator.",
            "- Status: provided / no-PRD intake": "- Status: no-PRD intake",
            "- Version or updated at:": "- Version or updated at: N/A — initial request captured once",
            "- Read at:": "- Read at: 2026-08-11T10:00+08:00",
            "- Applicability: applicable / N/A — one registered URL or verbatim request and no multi-file package": "- Applicability: N/A — one verbatim request and no multi-file delivery package",
        }
        for old, new in replacements.items():
            text = text.replace(old, new, 1)
        code_replacements = {
            "- Repository / directory:": "- Repository / directory: `.`",
            "- Mode: existing-code / greenfield": "- Mode: existing-code",
            "- Repomix initialization: PASS — Repomix <version>; runner=<repomix or npx --yes repomix@latest>; command=<exact command>; scope=<packed scope>; exclusions=<secret/generated/dependency exclusions>; files=<count>; tokens=<count> / N/A — greenfield has no pre-existing business or test source": "- Repomix initialization: PASS — Repomix 1.9.0; runner=npx --yes repomix@latest; command=npx --yes repomix@latest --compress --output /tmp/project.xml; scope=.; exclusions=.ai-team,node_modules,.env*; files=2; tokens=100",
            "- Baseline description:": "- Baseline description: existing calculator source and regression tests",
            "- Modules and tests inspected:": "- Modules and tests inspected: `src/calculator/input.ts`; `tests/calculator/input.test.ts`",
        }
        for old, new in code_replacements.items():
            text = text.replace(old, new, 1)
        before, marker, after = text.rpartition("- Read at:")
        self.assertTrue(marker)
        text = before + "- Read at: 2026-08-11T10:01+08:00" + after
        source.write_text(text, encoding="utf-8")

    def fill_specs(self, project: Path) -> None:
        specs = project / ".ai-team/specs"
        specs.mkdir(parents=True, exist_ok=True)
        (specs / "acceptance.md").write_text(
            """# Acceptance Specification: Calculator input

## Requirement source and intake state
- Source: initial user request REQ-EXAMPLE-STD-001
- Verbatim initial request (when no PRD): Build calculator input validation.
- Status: frozen
- Product analyst: AGENT-PA-EXAMPLE
- Independent review: AGENT-IV-EXAMPLE / PASS / EVID-ACCEPTANCE-001 / `.ai-team/evidence/acceptance-review.md` / 2026-08-11T09:30+08:00
- Evidence-backed rules: REQ-EXAMPLE-STD-001
- Conventional low-risk MVP assumptions and rationale: N/A — no extra product assumption
- Awaiting material human decision: none

## Scope
- In scope: calculator expression input validation
- Out of scope: none

## Requirements
- REQ-EXAMPLE-STD-001: Reject unsupported input and preserve valid arithmetic.

## User stories and acceptance criteria
### AC-EXAMPLE-STD-001: Validate expression input
- Requirement: REQ-EXAMPLE-STD-001
- Preconditions: calculator is available
- Main flow: validate input
- Error/boundary behavior: unsupported characters are rejected
- Observable result: valid input remains unchanged

## Source differences and decisions
- none
""",
            encoding="utf-8",
        )
        (specs / "traceability.md").write_text(
            """# Requirement Traceability Matrix

| Requirement | Requirement source and classification | State | Acceptance criteria | Source/Demo evidence | Baseline impact | Quality treatment | Design and task | Test case/method | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-EXAMPLE-STD-001 | initial request; evidence-backed | covered | AC-EXAMPLE-STD-001 | initial request | preserve valid input | regression | calculator module; TASK-EXAMPLE-STD-001 | TEST-EXAMPLE-STD-001; TEST-EXAMPLE-STD-002 | none |
""",
            encoding="utf-8",
        )
        evidence = project / ".ai-team/evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "acceptance-review.md").write_text(
            "EVID-ACCEPTANCE-001 independent intake PASS\n", encoding="utf-8"
        )
        (project / ".ai-team/stage.md").write_text(
            "# Project Stage\n\n- Stage: implementation-authorized\n"
            "- Authority: REQ-EXAMPLE-STD-001 local build request\n"
            "- Scope: TASK-EXAMPLE-STD-001\n- Updated at: 2026-08-11T09:00+08:00\n",
            encoding="utf-8",
        )

    def prepare_standard_ready_project(self, project: Path) -> tuple[Path, Path]:
        self.fill_source_register(project)
        self.fill_specs(project)
        source = project / "src/calculator/input.ts"
        test = project / "tests/calculator/input.test.ts"
        source.parent.mkdir(parents=True)
        test.parent.mkdir(parents=True)
        source.write_text("export const allowed = /[0-9+\\-*/]/;\n", encoding="utf-8")
        test.write_text("// calculator input regression fixture\n", encoding="utf-8")
        for path in (
            project / ".ai-team/design/calculator-input.md",
            project / ".ai-team/evidence/EXAMPLE-STD-001.md",
            project / ".ai-team/evidence/EXAMPLE-STD-001-design-review.md",
            project / ".ai-team/evidence/EXAMPLE-STD-001-readiness.md",
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                review_record(
                    "task-design"
                    if path.name.endswith("design-review.md")
                    else "implementation-readiness"
                )
                if path.name.endswith(("design-review.md", "readiness.md"))
                else f"evidence: {path.name}\n",
                encoding="utf-8",
            )
        card_text = standard_example().replace(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            hashlib.sha256(source.read_bytes()).hexdigest(),
        ).replace(
            "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
            hashlib.sha256(test.read_bytes()).hexdigest(),
        )
        card = project / ".ai-team/tasks/TASK-EXAMPLE-STD-001.md"
        card.write_text(card_text, encoding="utf-8")
        backlog = project / ".ai-team/tasks/backlog.md"
        backlog.write_text(
            backlog.read_text(encoding="utf-8").replace(
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| TASK-EXAMPLE-STD-001 | Input validation | implementation-ready | standard | M | BATCH-EXAMPLE-01 | serial implementation engineer | none | none | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |",
            ).replace(
                "| B1 |  |  |  |  |  | none / checkpoint ID | none / blocking / non-blocking | not-required / pending / accepted / rejected / conditional |",
                "| BATCH-EXAMPLE-01 | Validate calculator input | TASK-EXAMPLE-STD-001 | TASK-EXAMPLE-STD-001 | task implementation-ready | `npm test` | none | none | not-required |",
            ),
            encoding="utf-8",
        )
        return card, backlog

    def with_candidate_ledger(self, project: Path, card_text: str) -> str:
        source = project / "src/calculator/input.ts"
        test = project / "tests/calculator/input.test.ts"
        return card_text.replace(
            "- Current change-set fingerprint: N/A — candidate files do not exist yet before implementation",
            "- Current change-set fingerprint:\n"
            f"  - `src/calculator/input.ts` = {hashlib.sha256(source.read_bytes()).hexdigest()}\n"
            f"  - `tests/calculator/input.test.ts` = {hashlib.sha256(test.read_bytes()).hexdigest()}",
        )

    def test_current_project_template_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            self.assertEqual([], checker.check_project(project))
            result = subprocess.run(
                [
                    sys.executable,
                    str(project / ".ai-team/scripts/check_project_consistency.py"),
                    str(project),
                    "--audit",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_existing_code_blocks_project_check_until_repomix_intake_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            source = project / "src/existing.py"
            source.parent.mkdir()
            source.write_text("VALUE = 1\n", encoding="utf-8")

            errors = checker.check_project(project)
            self.assertTrue(any("Repomix" in error for error in errors), errors)

            self.fill_source_register(project)
            self.assertEqual([], checker.check_project(project))

    def test_rendered_relative_paths_are_posix_on_windows(self) -> None:
        root = PureWindowsPath(r"C:\work\project")
        card = root / ".ai-team" / "tasks" / "TASK-001.md"
        self.assertEqual(
            ".ai-team/tasks/TASK-001.md",
            checker.relative_display(card, root),
        )

    def test_realistic_implementation_ready_project_passes_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            self.prepare_standard_ready_project(project)
            self.assertEqual([], checker.check_project(project))
            self.assertEqual(
                [],
                checker.selected_task_gate_errors(
                    project, "TASK-EXAMPLE-STD-001", "implementation-ready"
                ),
            )
            self.assertIn("TASK-EXAMPLE-STD-001", checker.next_eligible_action(project) or "")

    def test_selected_task_gate_resolves_a_slugged_card_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card, backlog = self.prepare_standard_ready_project(project)
            slugged_card = card.with_name("TASK-EXAMPLE-STD-001-input-validation.md")
            card.rename(slugged_card)
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "[card](TASK-EXAMPLE-STD-001.md)",
                    "[card](TASK-EXAMPLE-STD-001-input-validation.md)",
                ),
                encoding="utf-8",
            )
            self.assertEqual([], checker.check_project(project))
            self.assertEqual(
                [],
                checker.selected_task_gate_errors(
                    project, "TASK-EXAMPLE-STD-001", "implementation-ready"
                ),
            )

    def test_shared_spec_error_is_located_once_across_multiple_cards(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card, _ = self.prepare_standard_ready_project(project)
            second = card.with_name("TASK-EXAMPLE-STD-002.md")
            second.write_text(
                card.read_text(encoding="utf-8").replace(
                    "TASK-EXAMPLE-STD-001", "TASK-EXAMPLE-STD-002"
                ),
                encoding="utf-8",
            )
            matrix = project / ".ai-team/specs/traceability.md"
            matrix.write_text(
                matrix.read_text(encoding="utf-8").replace(
                    "initial request; evidence-backed", "initial request"
                ),
                encoding="utf-8",
            )
            errors = []
            for candidate in (card, second):
                errors.extend(
                    checker.located_error(candidate, project, error)
                    for error in checker.validator.project_spec_errors(
                        candidate, candidate.read_text(encoding="utf-8")
                    )
                )
            shared = [
                error
                for error in dict.fromkeys(errors)
                if "traceability source classification is missing" in error
            ]
            self.assertEqual(1, len(shared), shared)
            self.assertTrue(shared[0].startswith(".ai-team/specs/traceability.md:"), shared)

    def test_review_evidence_errors_name_the_evidence_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            self.prepare_standard_ready_project(project)
            evidence = project / ".ai-team/evidence/EXAMPLE-STD-001-readiness.md"
            evidence.write_text("# damaged readiness evidence\n", encoding="utf-8")
            errors = checker.check_project(project)
            review_errors = [
                error for error in errors if "Review evidence record" in error
            ]
            self.assertTrue(review_errors, errors)
            self.assertTrue(
                all(
                    error.startswith(
                        ".ai-team/evidence/EXAMPLE-STD-001-readiness.md:"
                    )
                    for error in review_errors
                ),
                review_errors,
            )
            self.assertFalse(
                any(
                    error.startswith(
                        ".ai-team/tasks/TASK-EXAMPLE-STD-001.md: Review evidence record"
                    )
                    for error in errors
                ),
                errors,
            )

    def test_combined_cli_deduplicates_errors_and_prints_repair_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            self.prepare_standard_ready_project(project)
            evidence = project / ".ai-team/evidence/EXAMPLE-STD-001-readiness.md"
            evidence.write_text("# damaged readiness evidence\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(project / ".ai-team/scripts/check_project_consistency.py"),
                    str(project),
                    "--task",
                    "TASK-EXAMPLE-STD-001",
                    "--gate",
                    "implementation-ready",
                    "--next-action",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            error_lines = [
                line for line in result.stdout.splitlines() if line.startswith("- ")
            ]
            self.assertEqual(len(error_lines), len(set(error_lines)), result.stdout)
            self.assertIn(
                "NEXT fix-consistency: .ai-team/evidence/EXAMPLE-STD-001-readiness.md:",
                result.stdout,
            )

    def test_scoped_gate_ignores_historical_fingerprint_drift_until_full_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card, backlog = self.prepare_standard_ready_project(project)
            historical = project / ".ai-team/tasks/TASK-EXAMPLE-HIST-002.md"
            historical_text = self.with_candidate_ledger(project, card.read_text(encoding="utf-8")).replace(
                "TASK-EXAMPLE-STD-001", "TASK-EXAMPLE-HIST-002"
            ).replace(
                "implementation-ready / not-complete", "complete / verified-complete"
            )
            historical_text = historical_text.replace(
                hashlib.sha256((project / "src/calculator/input.ts").read_bytes()).hexdigest(),
                "0" * 64,
            )
            historical.write_text(historical_text, encoding="utf-8")
            backlog.write_text(
                backlog.read_text(encoding="utf-8")
                .replace(
                    "| TASK-EXAMPLE-STD-001 | Input validation | implementation-ready | standard | M | BATCH-EXAMPLE-01 | serial implementation engineer | none | none | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |",
                    "| TASK-EXAMPLE-STD-001 | Input validation | implementation-ready | standard | M | BATCH-EXAMPLE-01 | serial implementation engineer | none | none | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |\n"
                    "| TASK-EXAMPLE-HIST-002 | Historical validation | complete | standard | M | BATCH-EXAMPLE-01 | delivery coordinator | none | none | none | [card](TASK-EXAMPLE-HIST-002.md) |",
                )
                .replace(
                    "| BATCH-EXAMPLE-01 | Validate calculator input | TASK-EXAMPLE-STD-001 | TASK-EXAMPLE-STD-001 |",
                    "| BATCH-EXAMPLE-01 | Validate calculator input | TASK-EXAMPLE-STD-001 TASK-EXAMPLE-HIST-002 | TASK-EXAMPLE-STD-001 TASK-EXAMPLE-HIST-002 |",
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                checker.selected_task_gate_errors(
                    project, "TASK-EXAMPLE-STD-001", "implementation-ready"
                ),
            )
            audit_errors = checker.check_project(project)
            self.assertTrue(
                any(
                    "TASK-EXAMPLE-HIST-002.md: fingerprint mismatch" in error
                    for error in audit_errors
                ),
                audit_errors,
            )

    def test_compact_cli_suppresses_secondary_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            self.prepare_standard_ready_project(project)
            evidence = project / ".ai-team/evidence/EXAMPLE-STD-001-readiness.md"
            evidence.write_text("# damaged readiness evidence\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(project / ".ai-team/scripts/check_project_consistency.py"),
                    str(project),
                    "--task",
                    "TASK-EXAMPLE-STD-001",
                    "--gate",
                    "implementation-ready",
                    "--compact",
                    "--next-action",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("additional error(s) suppressed", result.stdout)
            self.assertIn("NEXT fix-consistency:", result.stdout)
            detailed_errors = [
                line
                for line in result.stdout.splitlines()
                if line.startswith("- ") and "additional error(s) suppressed" not in line
            ]
            self.assertEqual(1, len(detailed_errors), result.stdout)

    def test_audit_cli_checks_historical_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card, _ = self.prepare_standard_ready_project(project)
            card.write_text(
                self.with_candidate_ledger(project, card.read_text(encoding="utf-8"))
                .replace("implementation-ready / not-complete", "complete / verified-complete")
                .replace(
                    hashlib.sha256((project / "src/calculator/input.ts").read_bytes()).hexdigest(),
                    "0" * 64,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(project / ".ai-team/scripts/check_project_consistency.py"),
                    str(project),
                    "--audit",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("fingerprint mismatch", result.stdout)

    def test_cli_requires_an_explicit_gate_or_audit_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            result = subprocess.run(
                [
                    sys.executable,
                    str(project / ".ai-team/scripts/check_project_consistency.py"),
                    str(project),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("select --task with --gate", result.stdout)

    def test_stage_template_prompts_initialization_timestamp(self) -> None:
        stage = (PROJECT_TEMPLATE / ".ai-team/stage.md").read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("current ISO timestamp during initialization", stage)
        self.assertIn("stage.md` updated-at placeholder", skill)

    def test_project_rules_cannot_restate_mutable_current_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            rules = project / ".ai-team/project-rules.md"
            rules.write_text(
                rules.read_text(encoding="utf-8")
                + "\n- Current authorization is limited to Stage 2 under `analysis-only`.\n",
                encoding="utf-8",
            )

            errors = checker.check_project(project)
            self.assertTrue(
                any("must not restate the mutable current stage" in error for error in errors),
                errors,
            )

    def test_audit_rejects_stale_stage_bound_pre_task_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            stage = project / ".ai-team/stage.md"
            stage.write_text(
                "# Project Stage\n\n- Stage: analysis-only\n"
                "- Authority: bounded product and experience analysis\n"
                "- Scope: product and experience analysis\n"
                "- Updated at: 2026-08-17T09:00:00+08:00\n",
                encoding="utf-8",
            )
            stage_hash = hashlib.sha256(stage.read_bytes()).hexdigest()
            evidence = project / ".ai-team/evidence/EVID-PHASE-001.md"
            evidence.parent.mkdir(parents=True, exist_ok=True)
            evidence.write_text(
                """# EVID-PHASE-001: Pre-task review

- Reviewer identity: AGENT-IV-PHASE-001
- Role: independent verifier
- Review phase: intake
- Snapshot and Manifest: N/A — pre-task product and experience scope
"""
                f"- Stage binding: 2026-08-17T09:00:00+08:00 / {stage_hash}\n"
                """- Reviewed scope and inputs: current stage, sources, acceptance, and experience design
- Commands or inspection performed: source and artifact consistency inspection
- Evidence and findings: no blocking discrepancy in the bounded pre-task scope
- Verdict: **PASS**
- Invalidated by: any project stage or reviewed source change
- Recorded at: 2026-08-17T09:30:00+08:00
""",
                encoding="utf-8",
            )
            spec = project / ".ai-team/specs/phase.md"
            spec.parent.mkdir(parents=True, exist_ok=True)
            spec.write_text(
                "# Current phase\n\n- Independent review: `.ai-team/evidence/EVID-PHASE-001.md`\n",
                encoding="utf-8",
            )

            current_evidence = evidence.read_text(encoding="utf-8")
            evidence.write_text(
                re.sub(r"^- Stage binding:.*\n", "", current_evidence, flags=re.MULTILINE),
                encoding="utf-8",
            )
            missing_errors = checker.check_project(project)
            self.assertTrue(
                any("pre-task PASS requires Stage binding" in error for error in missing_errors),
                missing_errors,
            )
            evidence.write_text(current_evidence, encoding="utf-8")
            self.assertEqual([], checker.check_project(project))

            stage.write_text(
                "# Project Stage\n\n- Stage: implementation-authorized\n"
                "- Authority: unrelated local article change request\n"
                "- Scope: all tasks\n"
                "- Updated at: 2026-08-17T13:10:00+08:00\n",
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(
                any("stale Stage binding" in error for error in errors),
                errors,
            )

    def test_standard_task_state_walk_reaches_batch_regression_and_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card, backlog = self.prepare_standard_ready_project(project)

            self.assertEqual([], checker.check_project(project))
            self.assertIn("start the one serial", checker.next_eligible_action(project) or "")

            card.write_text(
                card.read_text(encoding="utf-8").replace(
                    "implementation-ready / not-complete", "implementing / not-complete"
                ),
                encoding="utf-8",
            )
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| implementation-ready |", "| implementing |"
                ),
                encoding="utf-8",
            )
            self.assertEqual([], checker.check_project(project))
            self.assertIn("continue the one serial", checker.next_eligible_action(project) or "")

            card_text = card.read_text(encoding="utf-8").replace(
                "implementing / not-complete", "awaiting-verification / not-complete"
            ).replace(
                "- Build / generation / lint-typecheck results: pending implementation",
                "- Build / generation / lint-typecheck results: PASS — lint completed",
            ).replace(
                "- Owner / affected / contract test results: pending implementation",
                "- Owner / affected / contract test results: PASS — focused tests completed",
            )
            card_text = self.with_candidate_ledger(project, card_text)
            card.write_text(card_text, encoding="utf-8")
            backlog.write_text(
                backlog.read_text(encoding="utf-8")
                .replace("| implementing |", "| awaiting-verification |")
                .replace(
                    "| serial implementation engineer |",
                    "| independent verifier |",
                ),
                encoding="utf-8",
            )
            self.assertEqual([], checker.check_project(project))
            self.assertIn("start independent verification", checker.next_eligible_action(project) or "")

            verify = project / ".ai-team/evidence/EXAMPLE-STD-001-verify.md"
            verify.write_text(review_record("verification"), encoding="utf-8")
            card.write_text(
                card.read_text(encoding="utf-8").replace(
                    "awaiting-verification / not-complete", "complete / verified-complete"
                ).replace(
                    "- [ ] AC-EXAMPLE-STD-001", "- [x] AC-EXAMPLE-STD-001"
                ).replace(
                    "- Independent verifier verdict: readiness PASS; implementation verification pending",
                    "- Independent verifier verdict: PASS — fresh scoped verification passed",
                ),
                encoding="utf-8",
            )
            backlog.write_text(
                backlog.read_text(encoding="utf-8")
                .replace("| awaiting-verification |", "| complete |")
                .replace("| independent verifier |", "| delivery coordinator |")
                .replace(
                    "| none | none | verified-complete |",
                    "| none | none | none |",
                ),
                encoding="utf-8",
            )
            self.assertEqual([], checker.check_project(project))
            self.assertIn("run the planned batch regression", checker.next_eligible_action(project) or "")

            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "`npm test`",
                    "PASS — EVID-BATCH-EXAMPLE-01 / 2026-08-12T12:00+08:00",
                ),
                encoding="utf-8",
            )
            self.assertEqual([], checker.check_project(project))
            self.assertIsNone(checker.next_eligible_action(project))

    def test_official_fast_card_passes_full_consistency_check(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            self.fill_source_register(project)
            (project / "CONTRIBUTING.md").write_text("Local contribution notes.\n", encoding="utf-8")
            evidence = project / ".ai-team/evidence"
            evidence.mkdir(exist_ok=True)
            (evidence / "EXAMPLE-001-fast-gate.md").write_text(
                review_record("fast-design-readiness")
                .replace("SNAP-EXAMPLE-STD-001-01", "SNAP-EXAMPLE-001-01"),
                encoding="utf-8",
            )
            (evidence / "EXAMPLE-001.md").write_text("EVID-EXAMPLE-001 owner PASS\n", encoding="utf-8")
            (project / ".ai-team/stage.md").write_text(
                "# Project Stage\n\n- Stage: implementation-authorized\n"
                "- Authority: explicit local documentation update request\n"
                "- Scope: TASK-EXAMPLE-001\n- Updated at: 2026-08-12T09:00+08:00\n",
                encoding="utf-8",
            )
            card = project / ".ai-team/tasks/TASK-EXAMPLE-001.md"
            card.write_text(fast_example(), encoding="utf-8")
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-EXAMPLE-001 | Contributor docs | awaiting-verification | fast | S | batch-not-applicable | independent verifier | none | none | verified-complete | [card](TASK-EXAMPLE-001.md) |",
                ),
                encoding="utf-8",
            )
            self.assertEqual([], checker.check_project(project))

    def test_backlog_and_card_dependencies_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001.md"
            card.write_text(
                f"""# TASK-001: Dependency drift

## Handoff Snapshot
- Workflow revision: {checker.WORKFLOW_REVISION}
- Current state and technical outcome: analysis / not-complete
- Delivery lane / complexity / control triggers: standard / M / none — analysis only
- Batch / dependencies / entry: B1 / TASK-002 / analysis may proceed
""",
                encoding="utf-8",
            )
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-001 | Drift | analysis | standard | M | B1 | delivery coordinator | none | none | task-design | [card](TASK-001.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("Dependencies mismatch" in error for error in errors), errors)

    def test_revision_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            rules = project / ".ai-team/project-rules.md"
            rules.write_text(
                rules.read_text(encoding="utf-8").replace(
                    checker.WORKFLOW_REVISION, "ai-team-2026-08-11-r4"
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("revision drift" in error for error in errors), errors)

    def test_missing_local_link_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            note = project / ".ai-team/evidence/link-check.md"
            note.parent.mkdir(parents=True, exist_ok=True)
            note.write_text("[missing evidence](missing.txt)\n", encoding="utf-8")
            errors = checker.check_project(project)
            self.assertTrue(any("link target not found" in error for error in errors), errors)

    def test_task_root_outside_ai_team_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            manifest = project / ".ai-team/manifest.md"
            manifest.write_text(
                manifest.read_text(encoding="utf-8").replace(
                    "- Task root: `.ai-team/tasks`", "- Task root: `tasks`"
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(
                any("Task root" in error for error in errors),
                errors,
            )

    def test_active_task_revision_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001-example.md"
            card.write_text(
                """\
# TASK-001: Example

## Handoff Snapshot
- Workflow revision: ai-team-2026-08-11-r4
- Current state and technical outcome: analysis / not-complete
""",
                encoding="utf-8",
            )
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-001 | Example | analysis | standard | M | B1 | coordinator | none | none | task-design | [card](TASK-001-example.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(
                any("active task workflow revision mismatch" in error for error in errors),
                errors,
            )

    def test_runtime_authority_revision_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            for name in ("workflow.md", "roles.md"):
                artifact = project / ".ai-team/governance" / name
                artifact.write_text("stale authority without revision\n", encoding="utf-8")
            errors = checker.check_project(project)
            self.assertTrue(any("workflow.md" in error for error in errors), errors)
            self.assertTrue(any("roles.md" in error for error in errors), errors)

    def test_unlisted_task_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001-example.md"
            card.write_text(
                f"""\
# TASK-001: Example

## Handoff Snapshot
- Workflow revision: {checker.WORKFLOW_REVISION}
- Current state and technical outcome: analysis / not-complete
""",
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("missing from backlog" in error for error in errors), errors)

    def test_backlog_state_mismatch_and_dependency_cycle_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            task_root = project / ".ai-team/tasks"
            for number, dependency in (("001", "TASK-002"), ("002", "TASK-001")):
                (task_root / f"TASK-{number}-example.md").write_text(
                    f"""\
# TASK-{number}: Example

## Handoff Snapshot
- Workflow revision: {checker.WORKFLOW_REVISION}
- Current state and technical outcome: analysis / not-complete
- Delivery lane / complexity / control triggers: standard / M / none — analysis-only task
- Batch / dependencies / entry: B1 / none / analysis may proceed
""",
                    encoding="utf-8",
                )
            backlog = task_root / "backlog.md"
            rows = "\n".join(
                (
                    "| TASK-001 | One | implementation-ready | standard | M | B1 | coordinator | TASK-002 | none | task-design | [card](TASK-001-example.md) |",
                    "| TASK-002 | Two | analysis | standard | M | B1 | coordinator | TASK-001 | none | task-design | [card](TASK-002-example.md) |",
                )
            )
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" + rows,
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("State mismatch" in error for error in errors), errors)
            self.assertTrue(any("dependency cycle" in error for error in errors), errors)

    def test_completed_task_cannot_bypass_completion_gate_or_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001-broken.md"
            card.write_text(
                f"""\
# TASK-001: Broken completion

## Handoff Snapshot
- Workflow revision: {checker.WORKFLOW_REVISION}
- Current state and technical outcome: complete / verified-complete
- Required reads: `.ai-team/sources.md`

## Delivery planning
- Execution lane: standard
- Complexity: M
- Implementation batch: B1

## Evidence index
- Current source/design/decision evidence: `.ai-team/evidence/missing.md`
- Current test and review evidence: `.ai-team/evidence/missing-verify.md`
""",
                encoding="utf-8",
            )
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-001 | Broken completion | complete | standard | M | B1 | delivery coordinator | none | none | verified-complete | [card](TASK-001-broken.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("missing section" in error for error in errors), errors)

    def test_active_delivery_requires_filled_source_register(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001-analysis.md"
            card.write_text(
                f"""\
# TASK-001: Analysis

## Handoff Snapshot
- Workflow revision: {checker.WORKFLOW_REVISION}
- Current state and technical outcome: analysis / not-complete
- Delivery lane / complexity / control triggers: standard / M / none — analysis-only task
- Batch / dependencies / entry: B1 / none / analysis may proceed
""",
                encoding="utf-8",
            )
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-001 | Analysis | analysis | standard | M | B1 | delivery coordinator | none | none | task-design | [card](TASK-001-analysis.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("Source register" in error for error in errors), errors)

    def test_backlog_owner_and_next_gate_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001-analysis.md"
            card.write_text(
                f"""\
# TASK-001: Analysis

## Handoff Snapshot
- Workflow revision: {checker.WORKFLOW_REVISION}
- Current state and technical outcome: analysis / not-complete
- Required reads: `.ai-team/sources.md`

## Delivery planning
- Execution lane: standard
- Complexity: M
- Implementation batch: B1
""",
                encoding="utf-8",
            )
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-001 | Analysis | analysis | standard | M | B1 | mystery role | none | none | bananas | [card](TASK-001-analysis.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("Owner role" in error for error in errors), errors)
            self.assertTrue(any("Next gate" in error for error in errors), errors)

    def test_backlog_owner_and_next_gate_must_match_state_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            _, backlog = self.prepare_standard_ready_project(project)
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| TASK-EXAMPLE-STD-001 | Input validation | implementation-ready | standard | M | BATCH-EXAMPLE-01 | serial implementation engineer | none | none | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |",
                    "| TASK-EXAMPLE-STD-001 | Input validation | implementation-ready | standard | M | BATCH-EXAMPLE-01 | product analyst | none | none | none | [card](TASK-EXAMPLE-STD-001.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(
                any("Owner role conflicts with State" in error for error in errors),
                errors,
            )
            self.assertTrue(
                any("Next gate conflicts with State" in error for error in errors),
                errors,
            )

    def test_triggered_reviewer_is_a_valid_awaiting_verification_owner(self) -> None:
        contract = checker.STATE_CONTRACTS["awaiting-verification"]
        self.assertIn("independent verifier", contract["owner_roles"])
        self.assertIn("code and security reviewer", contract["owner_roles"])
        self.assertEqual({"verified-complete"}, contract["next_gates"])

    def test_human_decision_contract_preserves_resume_gate(self) -> None:
        contract = checker.STATE_CONTRACTS["awaiting-human-decision"]
        self.assertIn("task-design", contract["next_gates"])
        self.assertIn("implementation-ready", contract["next_gates"])
        self.assertIn("verified-complete", contract["next_gates"])

    def test_next_action_selects_first_unblocked_dependency_ready_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            backlog = project / ".ai-team/tasks/backlog.md"
            rows = "\n".join(
                (
                    "| TASK-001 | Done | complete | standard | M | B1 | delivery coordinator | none | none | none | [done](TASK-001-done.md) |",
                    "| TASK-002 | Ready | implementation-ready | standard | M | B1 | serial implementation engineer | TASK-001 | none | verified-complete | [ready](TASK-002-ready.md) |",
                )
            )
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    + rows,
                ),
                encoding="utf-8",
            )
            action = checker.next_eligible_action(project)
            self.assertIsNotNone(action)
            self.assertIn("TASK-002", action or "")
            self.assertIn("serial implementation engineer", action or "")

    def test_next_action_prioritizes_active_implementation_over_later_ready_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            backlog = project / ".ai-team/tasks/backlog.md"
            text = backlog.read_text(encoding="utf-8")
            text = text.replace(
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| TASK-001 | Ready | implementation-ready | standard | M | B1 | serial implementation engineer | none | none | verified-complete | [ready](TASK-001-ready.md) |\n"
                "| TASK-002 | Active | implementing | standard | M | B1 | serial implementation engineer | none | none | verified-complete | [active](TASK-002-active.md) |",
            ).replace(
                "| B1 |  |  |  |  |  | none / checkpoint ID | none / blocking / non-blocking | not-required / pending / accepted / rejected / conditional |",
                "| B1 | Delivery | TASK-001, TASK-002 | TASK-001, TASK-002 | ready | verified | none | none | not-required |",
            )
            backlog.write_text(text, encoding="utf-8")
            action = checker.next_eligible_action(project) or ""
            self.assertIn("stop out-of-order", action)
            self.assertIn("TASK-001", action)

    def test_empty_project_bootstraps_intake_then_product_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            self.assertIn("source register", checker.next_eligible_action(project) or "")
            self.fill_source_register(project)
            self.assertIn("product analysis", checker.next_eligible_action(project) or "")

    def test_completed_batch_runs_regression_before_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            backlog = project / ".ai-team/tasks/backlog.md"
            text = backlog.read_text(encoding="utf-8").replace(
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| TASK-001 | Done | complete | standard | M | B1 | delivery coordinator | none | none | none | [done](TASK-001.md) |",
            ).replace(
                "| B1 |  |  |  |  |  | none / checkpoint ID | none / blocking / non-blocking | not-required / pending / accepted / rejected / conditional |",
                "| B1 | Delivery | TASK-001 | TASK-001 | ready | `pytest -q` | ACP-001 | blocking | pending |",
            )
            backlog.write_text(text, encoding="utf-8")
            action = checker.next_eligible_action(project) or ""
            self.assertIn("run the planned batch regression", action)
            self.assertNotIn("human acceptance required", action)

    def test_web_ui_batch_exit_requires_final_testsprite_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            report = project / "testsprite_tests/TestSprite_MCP_Test_Report.md"
            visual = project / "testsprite_tests/tmp/test_results.json"
            report.parent.mkdir(parents=True)
            visual.parent.mkdir(parents=True)
            report.write_text("# TestSprite report\n", encoding="utf-8")
            visual.write_text("{}\n", encoding="utf-8")
            required_tests = {"TEST-UI-001", "TEST-UI-002"}
            required_snapshots = {"SNAP-UI-001-02"}

            generic_pass = "PASS — EVID-BATCH-001 / 2026-08-12T12:00+08:00"
            errors = checker.testsprite_batch_exit_errors(
                project, generic_pass, required_tests, required_snapshots
            )
            self.assertTrue(any("TestSprite-final=PASS" in error for error in errors), errors)

            final_pass = (
                "PASS — EVID-BATCH-001; prerequisite-at=2026-08-12T12:00+08:00; "
                "TestSprite-final=PASS; run=TS-RUN-001; candidate=SNAP-UI-001-02; "
                "tests=TEST-UI-001 TEST-UI-002; "
                "report=`testsprite_tests/TestSprite_MCP_Test_Report.md`; "
                "visual-evidence=`testsprite_tests/tmp/test_results.json`; "
                "testsprite-at=2026-08-12T12:20+08:00"
            )
            self.assertEqual(
                [],
                checker.testsprite_batch_exit_errors(
                    project, final_pass, required_tests, required_snapshots
                ),
            )

            wrong_order = final_pass.replace(
                "testsprite-at=2026-08-12T12:20+08:00",
                "testsprite-at=2026-08-12T11:50+08:00",
            )
            errors = checker.testsprite_batch_exit_errors(
                project, wrong_order, required_tests, required_snapshots
            )
            self.assertTrue(any("after prerequisite suites" in error for error in errors), errors)

    def test_failed_batch_regression_reenters_affected_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            backlog = project / ".ai-team/tasks/backlog.md"
            text = backlog.read_text(encoding="utf-8").replace(
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| TASK-001 | Done | complete | standard | M | B1 | delivery coordinator | none | none | none | [done](TASK-001.md) |",
            ).replace(
                "| B1 |  |  |  |  |  | none / checkpoint ID | none / blocking / non-blocking | not-required / pending / accepted / rejected / conditional |",
                "| B1 | Delivery | TASK-001 | TASK-001 | ready | FAIL — EVID-BATCH-001 / TEST-001 | none | none | not-required |",
            )
            backlog.write_text(text, encoding="utf-8")
            self.assertIn("re-enter affected", checker.next_eligible_action(project) or "")

    def test_p1_routes_back_to_remediation_instead_of_reverification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001.md"
            card.write_text(
                """# TASK-001: Candidate

## Handoff Snapshot
- Delivery lane / complexity / control triggers: standard / M / none — ordinary task

## Verification and findings
- Independent verifier verdict: FAIL — TEST-001
- Findings / severity / affected REQ-AC-TEST: FIND-001 / P1 / REQ-001 AC-001 TEST-001
- Open P0/P1 / P2 follow-up: FIND-001 P1
""",
                encoding="utf-8",
            )
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-001 | Candidate | awaiting-verification | standard | M | B1 | independent verifier | none | none | verified-complete | [card](TASK-001.md) |",
                ),
                encoding="utf-8",
            )
            action = checker.next_eligible_action(project) or ""
            self.assertIn("serial implementation remediation", action)
            self.assertNotIn("start independent verification", action)

    def test_negated_severity_followup_does_not_stop_verification(self) -> None:
        for followup in (
            "no P0/P1 open / TASK-010 recorded",
            "P0: none / P1: none / P2: none",
        ):
            with self.subTest(followup=followup), tempfile.TemporaryDirectory() as temp_dir:
                project = Path(temp_dir)
                self.materialize_project(project)
                card = project / ".ai-team/tasks/TASK-001.md"
                card.write_text(
                    f"""# TASK-001: Healthy candidate

## Handoff Snapshot
- Delivery lane / complexity / control triggers: standard / M / none — ordinary task

## Verification and findings
- Independent verifier verdict: pending fresh verification
- Findings / severity / affected REQ-AC-TEST: none / N/A — no finding / REQ-001 AC-001 TEST-001
- Open P0/P1 / P2 follow-up: {followup}
""",
                    encoding="utf-8",
                )
                backlog = project / ".ai-team/tasks/backlog.md"
                backlog.write_text(
                    backlog.read_text(encoding="utf-8").replace(
                        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                        "| TASK-001 | Healthy | awaiting-verification | standard | M | B1 | independent verifier | none | none | verified-complete | [card](TASK-001.md) |",
                    ),
                    encoding="utf-8",
                )
                action = checker.next_eligible_action(project) or ""
                self.assertIn("start independent verification", action)
                self.assertNotIn("P0 finding", action)

    def test_resolved_task_or_decision_blocker_is_cleared(self) -> None:
        for blocker, prefix_rows in (
            ("DEC-900", ""),
            (
                "TASK-001",
                "| TASK-001 | Done | complete | standard | M | B1 | delivery coordinator | none | none | none | [done](TASK-001.md) |\n",
            ),
        ):
            with self.subTest(blocker=blocker), tempfile.TemporaryDirectory() as temp_dir:
                project = Path(temp_dir)
                self.materialize_project(project)
                if blocker == "DEC-900":
                    decisions = project / ".ai-team/governance/decisions.md"
                    decisions.write_text(
                        decisions.read_text(encoding="utf-8")
                        + "\n## DEC-900: Confirmed choice\n\n- Status: confirmed\n",
                        encoding="utf-8",
                    )
                backlog = project / ".ai-team/tasks/backlog.md"
                task_id = "TASK-002" if prefix_rows else "TASK-001"
                rows = prefix_rows + (
                    f"| {task_id} | Resume | analysis | standard | M | B1 | delivery coordinator | none | {blocker} | task-design | [card]({task_id}.md) |"
                )
                backlog.write_text(
                    backlog.read_text(encoding="utf-8").replace(
                        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" + rows,
                    ),
                    encoding="utf-8",
                )
                self.assertIn("clear the resolved blocker", checker.next_eligible_action(project) or "")

    def test_next_action_starts_security_review_only_when_triggered(self) -> None:
        for trigger, expected in (("none — ordinary task", False), ("security", True)):
            with self.subTest(trigger=trigger), tempfile.TemporaryDirectory() as temp_dir:
                project = Path(temp_dir)
                self.materialize_project(project)
                card = project / ".ai-team/tasks/TASK-001.md"
                card.write_text(
                    f"""# TASK-001: Verify candidate

## Handoff Snapshot
- Delivery lane / complexity / control triggers: standard / M / {trigger}
""",
                    encoding="utf-8",
                )
                backlog = project / ".ai-team/tasks/backlog.md"
                backlog.write_text(
                    backlog.read_text(encoding="utf-8").replace(
                        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                        "| TASK-001 | Verify | awaiting-verification | standard | M | B1 | independent verifier | none | none | verified-complete | [card](TASK-001.md) |",
                    ),
                    encoding="utf-8",
                )
                action = checker.next_eligible_action(project) or ""
                self.assertIn("independent verification", action)
                self.assertEqual(expected, "code/security review" in action)

    def test_blocking_checkpoint_becomes_the_next_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            backlog = project / ".ai-team/tasks/backlog.md"
            text = backlog.read_text(encoding="utf-8")
            text = text.replace(
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| TASK-001 | Done | complete | standard | M | B1 | delivery coordinator | none | none | none | [done](TASK-001-done.md) |",
            ).replace(
                "| B1 |  |  |  |  |  | none / checkpoint ID | none / blocking / non-blocking | not-required / pending / accepted / rejected / conditional |",
                "| B1 | Delivery | TASK-001 | TASK-001 | ready | PASS — EVID-BATCH-001 / 2026-08-12T12:00+08:00 | ACP-001 | blocking | pending |",
            )
            backlog.write_text(text, encoding="utf-8")
            action = checker.next_eligible_action(project) or ""
            self.assertIn("ACP-001", action)
            self.assertIn("human acceptance required", action)

    def test_next_action_explains_a_genuine_human_decision_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            backlog = project / ".ai-team/tasks/backlog.md"
            text = backlog.read_text(encoding="utf-8").replace(
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| TASK-001 | Decision | awaiting-human-decision | standard | M | B1 | delivery coordinator | none | DEC-999 | task-design | [card](TASK-001.md) |",
            )
            backlog.write_text(text, encoding="utf-8")
            action = checker.next_eligible_action(project) or ""
            self.assertIn("DEC-999", action)
            self.assertIn("human decision required", action)

    def test_only_confirmed_decisions_clear_human_blockers(self) -> None:
        for status, clears in (
            ("open", False),
            ("pending", False),
            ("rejected", False),
            ("confirmed", True),
        ):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp_dir:
                project = Path(temp_dir)
                self.materialize_project(project)
                decisions = project / ".ai-team/governance/decisions.md"
                decisions.write_text(
                    f"""# Decision Log

## DEC-900: Material choice

- Status: {status}
- Decision: selected by the human only when confirmed
""",
                    encoding="utf-8",
                )
                backlog = project / ".ai-team/tasks/backlog.md"
                backlog.write_text(
                    backlog.read_text(encoding="utf-8").replace(
                        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                        "| TASK-001 | Decision | awaiting-human-decision | standard | M | B1 | delivery coordinator | none | DEC-900 | task-design | [card](TASK-001.md) |",
                    ),
                    encoding="utf-8",
                )
                action = checker.next_eligible_action(project) or ""
                self.assertEqual(clears, "clear the resolved blocker" in action, action)
                self.assertEqual(not clears, "human decision required" in action, action)

    def test_pending_decision_is_a_valid_blocker_and_template_policies_use_pol_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card, backlog = self.prepare_standard_ready_project(project)
            card.write_text(
                card.read_text(encoding="utf-8").replace(
                    "implementation-ready / not-complete",
                    "awaiting-human-decision / not-complete",
                ),
                encoding="utf-8",
            )
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| TASK-EXAMPLE-STD-001 | Input validation | implementation-ready | standard | M | BATCH-EXAMPLE-01 | serial implementation engineer | none | none | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |",
                    "| TASK-EXAMPLE-STD-001 | Input validation | awaiting-human-decision | standard | M | BATCH-EXAMPLE-01 | delivery coordinator | none | DEC-001 | task-design | [card](TASK-EXAMPLE-STD-001.md) |",
                ),
                encoding="utf-8",
            )
            decisions = project / ".ai-team/governance/decisions.md"
            decisions.write_text(
                decisions.read_text(encoding="utf-8")
                + "\n## DEC-001: Material choice\n\n- Status: pending\n- Decision: awaiting human confirmation\n",
                encoding="utf-8",
            )
            self.assertEqual([], checker.check_project(project))
            action = checker.next_eligible_action(project) or ""
            self.assertIn("DEC-001", action)
            self.assertIn("human decision required", action)
            template_log = (PROJECT_TEMPLATE / ".ai-team/governance/decisions.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## POL-001", template_log)
            self.assertNotIn("## DEC-001: Markdown task management", template_log)

    def test_find_blocker_is_valid_and_routes_p1_to_remediation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card, backlog = self.prepare_standard_ready_project(project)
            card_text = (
                card.read_text(encoding="utf-8")
                .replace(
                    "implementation-ready / not-complete",
                    "awaiting-verification / not-complete",
                )
                .replace(
                    "- Build / generation / lint-typecheck results: pending implementation",
                    "- Build / generation / lint-typecheck results: PASS — lint completed",
                )
                .replace(
                    "- Owner / affected / contract test results: pending implementation",
                    "- Owner / affected / contract test results: PASS — focused tests completed",
                )
                .replace(
                    "- Independent verifier verdict: readiness PASS; implementation verification pending",
                    "- Independent verifier verdict: FAIL — TEST-EXAMPLE-STD-001",
                )
                .replace(
                    "- Findings / severity / affected REQ-AC-TEST: none — no design finding after TEST-EXAMPLE-STD-001 and TEST-EXAMPLE-STD-002 planning review",
                    "- Findings / severity / affected REQ-AC-TEST: FIND-P1-001 / P1 / REQ-EXAMPLE-STD-001 AC-EXAMPLE-STD-001 TEST-EXAMPLE-STD-001",
                )
                .replace(
                    "- Open P0/P1 / P2 follow-up: none",
                    "- Open P0/P1 / P2 follow-up: FIND-P1-001",
                )
            )
            card.write_text(self.with_candidate_ledger(project, card_text), encoding="utf-8")
            backlog.write_text(
                backlog.read_text(encoding="utf-8")
                .replace(
                    "| implementation-ready |", "| awaiting-verification |"
                )
                .replace(
                    "| serial implementation engineer |",
                    "| independent verifier |",
                )
                .replace(
                    "| none | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |",
                    "| FIND-P1-001 | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |",
                ),
                encoding="utf-8",
            )
            self.assertEqual([], checker.check_project(project))
            action = checker.next_eligible_action(project) or ""
            self.assertIn("serial implementation remediation", action)
            self.assertNotIn("clear the resolved blocker", action)

    def test_find_blocker_cannot_be_cleared_by_a_confirmed_decision(self) -> None:
        self.assertFalse(
            checker.blocker_is_resolved(
                "DEC-001 / FIND-P0-001",
                set(),
                {"DEC-001"},
            )
        )

    def test_dangling_find_blocker_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card, backlog = self.prepare_standard_ready_project(project)
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| none | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |",
                    "| FIND-MISSING-001 | verified-complete | [card](TASK-EXAMPLE-STD-001.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(
                any("absent from its task card" in error for error in errors),
                errors,
            )

    def test_conditional_acceptance_reenters_only_affected_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            backlog = project / ".ai-team/tasks/backlog.md"
            text = backlog.read_text(encoding="utf-8")
            text = text.replace(
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| TASK-001 | Done | complete | standard | M | B1 | delivery coordinator | none | none | none | [done](TASK-001-done.md) |",
            ).replace(
                "| B1 |  |  |  |  |  | none / checkpoint ID | none / blocking / non-blocking | not-required / pending / accepted / rejected / conditional |",
                "| B1 | Delivery | TASK-001 | TASK-001 | ready | PASS — EVID-BATCH-001 / 2026-08-12T12:00+08:00 | ACP-001 | blocking | conditional |",
            )
            backlog.write_text(text, encoding="utf-8")
            action = checker.next_eligible_action(project) or ""
            self.assertIn("conditional acceptance", action)
            self.assertIn("re-enter affected scope", action)

    def test_non_blocking_checkpoint_waits_until_local_actions_are_exhausted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            backlog = project / ".ai-team/tasks/backlog.md"
            text = backlog.read_text(encoding="utf-8")
            text = text.replace(
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| TASK-001 | Done | complete | standard | M | B1 | delivery coordinator | none | none | none | [done](TASK-001-done.md) |",
            ).replace(
                "| B1 |  |  |  |  |  | none / checkpoint ID | none / blocking / non-blocking | not-required / pending / accepted / rejected / conditional |",
                "| B1 | Delivery | TASK-001 | TASK-001 | ready | PASS — EVID-BATCH-001 / 2026-08-12T12:00+08:00 | ACP-001 | non-blocking | pending |",
            )
            backlog.write_text(text, encoding="utf-8")
            action = checker.next_eligible_action(project) or ""
            self.assertIn("non-blocking human acceptance remains pending", action)

    def test_batch_membership_and_serial_order_are_cross_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001-analysis.md"
            card.write_text(
                f"""\
# TASK-001: Analysis

## Handoff Snapshot
- Workflow revision: {checker.WORKFLOW_REVISION}
- Current state and technical outcome: analysis / not-complete
- Delivery lane / complexity / control triggers: standard / M / none — analysis-only task
- Batch / dependencies / entry: B1 / none / analysis may proceed
""",
                encoding="utf-8",
            )
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-001 | Analysis | analysis | standard | M | B1 | delivery coordinator | none | none | task-design | [card](TASK-001-analysis.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("batch member/card mismatch" in error for error in errors), errors)
            self.assertTrue(any("batch serial order" in error for error in errors), errors)

    def test_blockers_must_link_existing_task_or_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.materialize_project(project)
            card = project / ".ai-team/tasks/TASK-001-analysis.md"
            card.write_text(
                f"""\
# TASK-001: Analysis

## Handoff Snapshot
- Workflow revision: {checker.WORKFLOW_REVISION}
- Current state and technical outcome: analysis / not-complete
- Required reads: `.ai-team/sources.md`

## Delivery planning
- Execution lane: fast
- Complexity: S
- Implementation batch: batch-not-applicable — isolated Fast task
""",
                encoding="utf-8",
            )
            backlog = project / ".ai-team/tasks/backlog.md"
            backlog.write_text(
                backlog.read_text(encoding="utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| TASK-001 | Analysis | analysis | fast | S | batch-not-applicable — isolated Fast task | delivery coordinator | none | DEC-999 | task-design | [card](TASK-001-analysis.md) |",
                ),
                encoding="utf-8",
            )
            errors = checker.check_project(project)
            self.assertTrue(any("blocker decision not found" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
