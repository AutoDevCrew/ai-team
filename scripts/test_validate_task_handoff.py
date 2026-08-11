#!/usr/bin/env python3
"""Regression tests for the AI-team handoff validator and canonical examples."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import validate_task_handoff as validator


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "assets/project-template/.ai-team/governance/templates.md"


class HandoffValidatorTests(unittest.TestCase):
    def test_iso_8601_snapshot_timestamp_is_valid(self) -> None:
        for timestamp in (
            "2026-08-11T10:00+08:00",
            "2026-08-11T10:00:00Z",
            "2026-08-11 10:00",
            "2026-08-11",
        ):
            with self.subTest(timestamp=timestamp):
                snapshot = "\n".join(
                    (
                        f"- Snapshot ID and updated at: SNAP-001-01 / {timestamp}",
                        "- Source and decision references: REQ-001",
                        "- Required reads: `.ai-team/specs/acceptance.md`",
                        "- Next action and exit condition: run TEST-001; exit on PASS",
                    )
                )
                errors = validator.snapshot_semantic_errors(snapshot)
                self.assertFalse(
                    any("updated-at" in error for error in errors), errors
                )

    def test_minimal_fast_card_and_project_layout_pass_strict_validation(self) -> None:
        template_text = TEMPLATES.read_text(encoding="utf-8")
        match = re.search(
            r"## Minimal Fast-path task card.*?```md\n(.*?)\n```",
            template_text,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        card_text = match.group(1)

        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            ai_team = project / ".ai-team"
            governance = ai_team / "governance"
            tasks = ai_team / "tasks"
            governance.mkdir(parents=True)
            tasks.mkdir()
            (ai_team / "manifest.md").write_text(
                "\n".join(
                    (
                        "- Task root: `.ai-team/tasks`",
                        "- Project rules: `.ai-team/project-rules.md`",
                        "- Delivery policy: `.ai-team/governance/workflow.md`",
                        "- Role protocol: `.ai-team/governance/roles.md`",
                        "- Artifact templates: `.ai-team/governance/templates.md`",
                        "- Handoff validator: `.ai-team/scripts/validate_task_handoff.py`",
                        "- Markdown section extractor: `.ai-team/scripts/extract_markdown_section.py`",
                    )
                ),
                encoding="utf-8",
            )
            (ai_team / "project-rules.md").write_text("rules\n", encoding="utf-8")
            for name in ("workflow.md", "roles.md", "templates.md"):
                (governance / name).write_text(f"{name}\n", encoding="utf-8")
            scripts = ai_team / "scripts"
            scripts.mkdir()
            for name in ("validate_task_handoff.py", "extract_markdown_section.py"):
                (scripts / name).write_text(f"{name}\n", encoding="utf-8")
            card = tasks / "TASK-EXAMPLE-001.md"
            card.write_text(card_text, encoding="utf-8")

            errors = validator.validate(card_text, strict=True)
            errors.extend(validator.project_authority_errors(card))
            self.assertEqual([], errors)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts/validate_task_handoff.py"),
                    str(card),
                    "--strict",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_missing_runtime_authority_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            tasks = project / ".ai-team/tasks"
            tasks.mkdir(parents=True)
            (project / ".ai-team/manifest.md").write_text(
                "\n".join(
                    (
                        "- Task root: `.ai-team/tasks`",
                        "- Project rules: `.ai-team/project-rules.md`",
                        "- Delivery policy: `.ai-team/governance/workflow.md`",
                        "- Role protocol: `.ai-team/governance/roles.md`",
                        "- Artifact templates: `.ai-team/governance/templates.md`",
                        "- Handoff validator: `.ai-team/scripts/validate_task_handoff.py`",
                        "- Markdown section extractor: `.ai-team/scripts/extract_markdown_section.py`",
                    )
                ),
                encoding="utf-8",
            )
            card = tasks / "TASK-001.md"
            card.write_text("# TASK-001\n", encoding="utf-8")

            errors = validator.project_authority_errors(card)
            self.assertTrue(any("workflow.md" in error for error in errors), errors)

    def test_conditional_standard_readiness_guardrails(self) -> None:
        valid = """\
## Handoff Snapshot
- Current state and technical outcome: task-design-ready / not-complete

## Delivery planning
- Execution lane: standard

## Implementation-readiness review
- Verdict: conditional-pass
- Conditional activation (Standard only): dependency TASK-002 completes; command evidence is recorded; any source/design/manifest change invalidates; coordinator activation pending
"""
        self.assertEqual([], validator.conditional_readiness_errors(valid))

        invalid_lane = valid.replace("Execution lane: standard", "Execution lane: high-risk")
        self.assertTrue(
            any(
                "only for Standard" in error
                for error in validator.conditional_readiness_errors(invalid_lane)
            )
        )

        activated_too_early = valid.replace("task-design-ready", "implementation-ready")
        self.assertTrue(
            any(
                "must remain task-design-ready" in error
                for error in validator.conditional_readiness_errors(activated_too_early)
            )
        )

        missing_conditions = valid.replace(
            "dependency TASK-002 completes; command evidence is recorded; any source/design/manifest change invalidates; coordinator activation pending",
            "TBD",
        )
        self.assertTrue(
            any(
                "must record mechanical conditions" in error
                for error in validator.conditional_readiness_errors(missing_conditions)
            )
        )

    def test_non_fast_lane_requires_readiness_section_and_verdict(self) -> None:
        standard_without_section = """\
## Delivery planning
- Execution lane: standard
"""
        errors = validator.strict_readiness_section_errors(standard_without_section)
        self.assertTrue(any("missing Implementation-readiness" in error for error in errors))

        high_risk_without_section = standard_without_section.replace(
            "standard", "high-risk"
        )
        self.assertTrue(
            validator.strict_readiness_section_errors(high_risk_without_section)
        )

        missing_verdict = standard_without_section + """\
## Implementation-readiness review
- Reviewer: verifier
"""
        self.assertTrue(
            any(
                "missing field: Verdict:" in error
                for error in validator.strict_readiness_section_errors(missing_verdict)
            )
        )

        valid_not_reviewed = standard_without_section + """\
## Implementation-readiness review
- Verdict: not reviewed
"""
        self.assertEqual(
            [], validator.strict_readiness_section_errors(valid_not_reviewed)
        )

        fast_without_section = standard_without_section.replace("standard", "fast")
        self.assertEqual(
            [], validator.strict_readiness_section_errors(fast_without_section)
        )

        template_text = TEMPLATES.read_text(encoding="utf-8")
        match = re.search(
            r"## Task card.*?```md\n(.*?)\n```",
            template_text,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        standard_card = match.group(1).replace(
            "- Execution lane: fast / standard / high-risk",
            "- Execution lane: standard",
        )
        standard_card = re.sub(
            r"\n## Implementation-readiness review\n.*?(?=\n## |\Z)",
            "",
            standard_card,
            flags=re.DOTALL,
        )
        errors = validator.validate(standard_card, strict=True)
        self.assertTrue(
            any("missing Implementation-readiness" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
