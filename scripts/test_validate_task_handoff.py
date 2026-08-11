#!/usr/bin/env python3
"""Regression and adversarial tests for compact AI-team task validation."""

from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

try:
    from . import validate_task_handoff as validator
except ImportError:
    import validate_task_handoff as validator


SKILL_ROOT = Path(__file__).resolve().parent.parent
PROJECT_TEMPLATE = SKILL_ROOT / "assets/project-template"
TEMPLATES = PROJECT_TEMPLATE / ".ai-team/governance/templates.md"


def template_card(title: str) -> str:
    text = TEMPLATES.read_text(encoding="utf-8")
    match = re.search(rf"## {re.escape(title)}.*?```md\n(.*?)\n```", text, re.DOTALL)
    if match is None:
        raise AssertionError(f"template example not found: {title}")
    return match.group(1)


def review_record(
    phase: str,
    *,
    snapshot: str = "SNAP-EXAMPLE-STD-001-01",
    manifest: str = "TEM-EXAMPLE-STD-001-01",
    reviewer: str = "AGENT-IV-EXAMPLE",
    role: str = "independent verifier",
) -> str:
    return f"""# EVID-EXAMPLE: Review evidence

- Reviewer identity: {reviewer}
- Role: {role}
- Review phase: {phase}
- Snapshot and Manifest: {snapshot} / {manifest}
- Reviewed scope and inputs: current task scope, compact plan, and candidate
- Commands or inspection performed: declared task checks and independent diff inspection
- Evidence and findings: no blocking discrepancy found in the current scoped evidence
- Verdict: PASS
- Invalidated by: source, design, manifest, candidate, or environment change
- Recorded at: 2026-08-12T11:30+08:00
"""


def completed_standard_card() -> str:
    card = template_card("Complete Standard task card example")
    replacements = {
        "implementation-ready / not-complete": "complete / verified-complete",
        "- [ ] AC-EXAMPLE-STD-001 / TEST-EXAMPLE-STD-001": "- [x] AC-EXAMPLE-STD-001 / TEST-EXAMPLE-STD-001",
        "- [ ] AC-EXAMPLE-STD-001 / TEST-EXAMPLE-STD-002": "- [x] AC-EXAMPLE-STD-001 / TEST-EXAMPLE-STD-002",
        "- Build / generation / lint-typecheck results: pending implementation": "- Build / generation / lint-typecheck results: PASS — lint completed",
        "- Owner / affected / contract test results: pending implementation": "- Owner / affected / contract test results: PASS — owner and calculator regression groups passed",
        "- Omitted checks, residual risks, and evidence: none planned; Unicode normalization remains in independent verification": "- Omitted checks, residual risks, and evidence: none; `.ai-team/evidence/EXAMPLE-STD-001-verify.md`",
        "- Independent verifier verdict: readiness PASS; implementation verification pending": "- Independent verifier verdict: PASS — fresh scoped verification passed",
    }
    for old, new in replacements.items():
        card = card.replace(old, new)
    return card


def completed_fast_card() -> str:
    card = template_card("Minimal Fast-path task card")
    replacements = {
        "awaiting-verification / not-complete": "complete / verified-complete",
        "- Scope / acceptance / checks: REQ-EXAMPLE-001 → AC-EXAMPLE-001 → TEST-EXAMPLE-001; `markdownlint CONTRIBUTING.md`": "- Scope / acceptance / checks: PASS — REQ-EXAMPLE-001 → AC-EXAMPLE-001 → TEST-EXAMPLE-001; `markdownlint CONTRIBUTING.md`",
        "- Independent verifier / verdict / evidence: AGENT-IV-EXAMPLE / pending fresh TEST-EXAMPLE-001 / `.ai-team/evidence/EXAMPLE-001.md`": "- Independent verifier / verdict / evidence: AGENT-IV-EXAMPLE / PASS — fresh TEST-EXAMPLE-001 passed / `.ai-team/evidence/EXAMPLE-001.md`",
    }
    for old, new in replacements.items():
        card = card.replace(old, new)
    return card


class HandoffValidatorTests(unittest.TestCase):
    def materialize_project(self, project: Path, card_text: str) -> Path:
        shutil.copytree(PROJECT_TEMPLATE, project, dirs_exist_ok=True)
        ai_team = project / ".ai-team"
        governance = ai_team / "governance"
        scripts = ai_team / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        for source, target in (
            (SKILL_ROOT / "references/delivery-policy.md", governance / "workflow.md"),
            (SKILL_ROOT / "references/role-protocol.md", governance / "roles.md"),
            (SKILL_ROOT / "references/workflow-schema.json", governance / "workflow-schema.json"),
        ):
            shutil.copy2(source, target)
        for name in (
            "validate_task_handoff.py",
            "extract_markdown_section.py",
            "check_project_consistency.py",
            "render_fingerprint_ledger.py",
        ):
            shutil.copy2(SKILL_ROOT / "scripts" / name, scripts / name)
        (ai_team / "sources.md").write_text(
            """# Source Register

## Product requirement source
- Type: initial user request
- URL or verbatim request: Build a local calculator input validator.
- Authority: primary business-rule source
- Status: no-prd intake
- Version or updated at: N/A — initial request captured once
- Read at: 2026-08-12T10:00+08:00
""",
            encoding="utf-8",
        )
        specs = ai_team / "specs"
        specs.mkdir()
        (specs / "acceptance.md").write_text(
            """# Acceptance Specification: Calculator input

## Requirement source and intake state
- Source: initial request REQ-EXAMPLE-STD-001
- Verbatim initial request (when no PRD): Build calculator input validation.
- Status: frozen
- Product analyst: AGENT-PA-EXAMPLE
- Independent review: AGENT-IV-EXAMPLE / PASS / EVID-ACCEPTANCE-001 / `.ai-team/evidence/acceptance-review.md` / 2026-08-12T09:30+08:00
- Evidence-backed rules: REQ-EXAMPLE-STD-001
- Conventional low-risk MVP assumptions and rationale: N/A — no extra assumption
- Awaiting material human decision: none

## Scope
- In scope: calculator expression validation
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
        evidence = ai_team / "evidence"
        evidence.mkdir(exist_ok=True)
        (evidence / "acceptance-review.md").write_text("EVID-ACCEPTANCE-001 PASS\n", encoding="utf-8")
        (evidence / "EXAMPLE-STD-001-readiness.md").write_text(
            review_record("implementation-readiness"), encoding="utf-8"
        )
        (evidence / "EXAMPLE-STD-001-verify.md").write_text(
            review_record("verification"), encoding="utf-8"
        )
        (ai_team / "stage.md").write_text(
            "# Project Stage\n\n- Stage: implementation-authorized\n"
            "- Authority: explicit local build request for calculator validation\n"
            "- Scope: TASK-EXAMPLE-STD-001\n- Updated at: 2026-08-12T09:00+08:00\n",
            encoding="utf-8",
        )
        design = ai_team / "design"
        design.mkdir()
        (design / "calculator-input.md").write_text("existing calculator baseline\n", encoding="utf-8")
        source = project / "src/calculator/input.ts"
        test = project / "tests/calculator/input.test.ts"
        source.parent.mkdir(parents=True)
        test.parent.mkdir(parents=True)
        source.write_text("export const allowed = /[0-9+\\-*/]/;\n", encoding="utf-8")
        test.write_text("// calculator regression fixture\n", encoding="utf-8")
        card_text = card_text.replace(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            hashlib.sha256(source.read_bytes()).hexdigest(),
        ).replace(
            "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
            hashlib.sha256(test.read_bytes()).hexdigest(),
        )
        card = ai_team / "tasks/TASK-EXAMPLE-STD-001.md"
        card.write_text(card_text, encoding="utf-8")
        return card

    def test_schema_and_templates_are_aligned(self) -> None:
        standard = template_card("Task card")
        fast = template_card("Minimal Fast-path task card")
        for fields in (
            validator.SNAPSHOT_FIELDS,
            validator.PLANNING_FIELDS,
            validator.SELF_CHECK_FIELDS,
            validator.VERIFICATION_FIELDS,
        ):
            for field in fields:
                self.assertIn(field, standard)
        for field in validator.FAST_GATE_FIELDS:
            self.assertIn(field, fast)
        for field in validator.FAST_COMPLETION_FIELDS:
            self.assertIn(field, fast)
        self.assertNotIn("transitions", validator.WORKFLOW_SCHEMA)
        self.assertNotIn("reentry_targets", validator.WORKFLOW_SCHEMA)

    def test_compact_card_efficiency_budgets(self) -> None:
        def field_count(card: str) -> int:
            return sum(
                1 for line in card.splitlines() if line.startswith("- ") and ":" in line
            )

        self.assertLessEqual(field_count(template_card("Minimal Fast-path task card")), 22)
        self.assertLessEqual(field_count(template_card("Complete Standard task card example")), 35)

    def test_compact_examples_pass_expected_gates(self) -> None:
        fast = template_card("Minimal Fast-path task card")
        self.assertEqual([], validator.validate(fast, strict=True))
        ready_fast = fast.replace(
            "awaiting-verification / not-complete", "implementation-ready / not-complete"
        )
        self.assertEqual([], validator.validate(ready_fast, gate="implementation-ready"))
        self.assertEqual([], validator.validate(completed_fast_card(), gate="verified-complete"))
        standard = template_card("Complete Standard task card example")
        self.assertEqual([], validator.validate(standard, gate="implementation-ready"))
        self.assertEqual([], validator.validate(completed_standard_card(), gate="verified-complete"))

    def test_stage_scope_is_bound_to_current_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            card = self.materialize_project(Path(temp), template_card("Complete Standard task card example"))
            stage = Path(temp) / ".ai-team/stage.md"
            stage.write_text(
                "# Project Stage\n\n- Stage: implementation-authorized\n"
                "- Authority: explicit local build request for another task\n"
                "- Scope: TASK-OTHER\n- Updated at: 2026-08-12T09:00+08:00\n",
                encoding="utf-8",
            )
            errors = validator.project_stage_errors(card, "implementation-ready")
            self.assertTrue(any("does not authorize current task" in error for error in errors), errors)
            stage.write_text(
                "# Project Stage\n\n- Stage: implementation-authorized\n"
                "- Authority: explicit local build request for all tasks\n"
                "- Scope: all tasks\n- Updated at: 2026-08-12T09:00+08:00\n",
                encoding="utf-8",
            )
            self.assertEqual([], validator.project_stage_errors(card, "implementation-ready"))

    def test_cli_binds_layout_fingerprint_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            card = self.materialize_project(Path(temp), completed_standard_card())
            command = [sys.executable, str(SKILL_ROOT / "scripts/validate_task_handoff.py"), str(card), "--gate", "verified-complete"]
            passed = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(0, passed.returncode, passed.stdout + passed.stderr)
            (Path(temp) / ".ai-team/evidence/EXAMPLE-STD-001-verify.md").unlink()
            failed = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertNotEqual(0, failed.returncode)
            self.assertIn("independent verification", failed.stdout)

    def test_required_fingerprint_and_inventory_must_match(self) -> None:
        card = completed_standard_card().replace(
            "- Change-set file inventory: `src/calculator/input.ts`; `tests/calculator/input.test.ts`",
            "- Change-set file inventory: `src/calculator/input.ts`",
        )
        errors = validator.validate(card, gate="verified-complete")
        self.assertTrue(any("absent from inventory" in error for error in errors), errors)
        card = template_card("Complete Standard task card example").replace(
            "  - `tests/calculator/input.test.ts` = fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210\n",
            "",
        )
        self.assertTrue(any("missing inventory" in error for error in validator.inventory_ledger_errors(card)))

    def test_merged_standard_reviewer_is_allowed_but_triggered_review_is_required(self) -> None:
        self.assertEqual([], validator.validate(completed_standard_card(), gate="verified-complete"))
        triggered = completed_standard_card().replace(
            "standard / M / none — synchronous local validation using the existing module contract",
            "standard / M / security",
        ) + """

## Security impact
- Triggered: untrusted expression input crosses a validation boundary
- Review: authorization is unchanged; reject invalid control characters
- Required mitigations and negative tests: TEST-SEC-001 rejects control characters
"""
        errors = validator.validate(triggered, gate="verified-complete")
        self.assertTrue(any("separate code/security reviewer" in error for error in errors), errors)

    def test_security_trigger_requires_concrete_annex(self) -> None:
        card = template_card("Complete Standard task card example").replace(
            "standard / M / none — synchronous local validation using the existing module contract",
            "standard / M / security",
        )
        errors = validator.validate(card, gate="implementation-ready")
        self.assertTrue(any("Security impact" in error for error in errors), errors)
        card += """

## Security impact
- Triggered: N/A — nothing
- Review: N/A — nothing
- Required mitigations and negative tests: N/A — nothing
"""
        errors = validator.validate(card, gate="implementation-ready")
        self.assertTrue(any("may not be N/A" in error for error in errors), errors)

    def test_interface_trigger_requires_contract_reference_and_tests(self) -> None:
        card = template_card("Complete Standard task card example").replace(
            "standard / M / none — synchronous local validation using the existing module contract",
            "standard / M / interface",
        ).replace(
            "`.ai-team/sources.md`; no decision or contract change",
            "no frozen contract reference",
        ).replace(
            "- Risk and contract checks: invalid Unicode/control-character cases; no interface, security, or runtime-chain trigger",
            "- Risk and contract checks: no contract test",
        )
        errors = validator.validate(card, gate="implementation-ready")
        self.assertTrue(any("frozen contract reference" in error for error in errors), errors)
        self.assertTrue(any("contract TEST IDs" in error for error in errors), errors)

    def test_testsprite_trigger_requires_web_ui_and_annex(self) -> None:
        card = template_card("Complete Standard task card example").replace(
            "standard / M / none — synchronous local validation using the existing module contract",
            "standard / M / testsprite",
        )
        errors = validator.validate(card, gate="implementation-ready")
        self.assertTrue(any("requires the web-ui trigger" in error for error in errors), errors)
        self.assertTrue(any("TestSprite MCP" in error for error in errors), errors)

    def test_high_risk_requires_material_trigger(self) -> None:
        card = template_card("Complete Standard task card example").replace(
            "standard / M / none — synchronous local validation using the existing module contract",
            "high-risk / XL / experience",
        )
        errors = validator.validate(card, strict=True)
        self.assertTrue(any("material control trigger" in error for error in errors), errors)

    def test_standard_batch_regression_cannot_be_na(self) -> None:
        card = template_card("Complete Standard task card example").replace(
            "- Batch regression: `npm test` once at BATCH-EXAMPLE-01 exit",
            "- Batch regression: N/A — suite is expensive",
        )
        errors = validator.validate(card, strict=True)
        self.assertTrue(any("regression command" in error for error in errors), errors)

    def test_implementation_and_verification_evidence_must_be_final(self) -> None:
        card = completed_standard_card().replace(
            "- Build / generation / lint-typecheck results: PASS — lint completed",
            "- Build / generation / lint-typecheck results: FAIL — lint failed",
        )
        self.assertTrue(any("build/lint PASS" in error for error in validator.validate(card, gate="verified-complete")))
        card = completed_standard_card().replace(
            "- Independent verifier verdict: PASS — fresh scoped verification passed",
            "- Independent verifier verdict: NOT PASS — regression failed",
        )
        self.assertTrue(any("verifier PASS" in error for error in validator.validate(card, gate="verified-complete")))

    def test_implementer_cannot_self_verify(self) -> None:
        card = completed_standard_card().replace(
            "- Implementation engineer identity: AGENT-IE-EXAMPLE",
            "- Implementation engineer identity: AGENT-IV-EXAMPLE",
        )
        errors = validator.validate(card, gate="verified-complete")
        self.assertTrue(any("identities must differ" in error for error in errors), errors)

    def test_p0_p1_block_and_p2_requires_followup(self) -> None:
        p1 = completed_standard_card().replace(
            "- Findings / severity / affected REQ-AC-TEST: none / N/A — no finding / REQ-EXAMPLE-STD-001 AC-EXAMPLE-STD-001 TEST-EXAMPLE-STD-001 TEST-EXAMPLE-STD-002",
            "- Findings / severity / affected REQ-AC-TEST: FIND-P1-001 / P1 / REQ-EXAMPLE-STD-001 AC-EXAMPLE-STD-001 TEST-EXAMPLE-STD-001",
        ).replace("- Open P0/P1 / P2 follow-up: none", "- Open P0/P1 / P2 follow-up: FIND-P1-001")
        errors = validator.validate(p1, gate="verified-complete")
        self.assertTrue(any("unresolved P0/P1" in error for error in errors), errors)
        p2 = completed_standard_card().replace(
            "- Findings / severity / affected REQ-AC-TEST: none / N/A — no finding / REQ-EXAMPLE-STD-001 AC-EXAMPLE-STD-001 TEST-EXAMPLE-STD-001 TEST-EXAMPLE-STD-002",
            "- Findings / severity / affected REQ-AC-TEST: FIND-P2-001 / P2 / REQ-EXAMPLE-STD-001 AC-EXAMPLE-STD-001 TEST-EXAMPLE-STD-001",
        )
        errors = validator.validate(p2, gate="verified-complete")
        self.assertTrue(any("P2 findings require" in error for error in errors), errors)

    def test_conditional_readiness_activation_is_state_bound(self) -> None:
        card = template_card("Complete Standard task card example").replace(
            "- Design/readiness verdict and conditions: implementation-ready / direct PASS; no deferred condition",
            "- Design/readiness verdict and conditions: conditional-pass / pending / dependency TASK-002 completion evidence",
        ).replace("implementation-ready / not-complete", "task-design-ready / not-complete")
        self.assertEqual([], validator.validate(card, strict=True))
        self.assertTrue(validator.validate(card, gate="implementation-ready"))
        active = card.replace(
            "conditional-pass / pending / dependency TASK-002 completion evidence",
            "conditional-pass / activated / dependency TASK-002 complete in EVID-ACTIVATE-001 at 2026-08-12T12:00+08:00",
        ).replace("task-design-ready / not-complete", "implementation-ready / not-complete")
        self.assertEqual([], validator.validate(active, gate="implementation-ready"))

    def test_cancelled_state_requires_feedback_record(self) -> None:
        card = template_card("Complete Standard task card example").replace(
            "implementation-ready / not-complete", "cancelled/superseded / not-complete"
        )
        errors = validator.validate(card, strict=True)
        self.assertTrue(any("Human feedback and change record" in error for error in errors), errors)

    def test_invalid_state_and_missing_sections_are_rejected(self) -> None:
        card = template_card("Complete Standard task card example").replace(
            "implementation-ready / not-complete", "banana / verified-complete"
        )
        errors = validator.validate(card, strict=True)
        self.assertTrue(any("invalid task state" in error for error in errors), errors)
        no_plan = re.sub(r"\n## Plan and readiness\n.*?(?=\n## |\Z)", "", template_card("Complete Standard task card example"), flags=re.DOTALL)
        self.assertTrue(validator.validate(no_plan, gate="implementation-ready"))


if __name__ == "__main__":
    unittest.main()
