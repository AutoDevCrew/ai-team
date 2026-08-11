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
                    )
                ),
                encoding="utf-8",
            )
            (ai_team / "project-rules.md").write_text("rules\n", encoding="utf-8")
            for name in ("workflow.md", "roles.md", "templates.md"):
                (governance / name).write_text(f"{name}\n", encoding="utf-8")
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
                    )
                ),
                encoding="utf-8",
            )
            card = tasks / "TASK-001.md"
            card.write_text("# TASK-001\n", encoding="utf-8")

            errors = validator.project_authority_errors(card)
            self.assertTrue(any("workflow.md" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
