#!/usr/bin/env python3
"""Regression tests for fence-aware Markdown section extraction."""

from pathlib import Path
import subprocess
import sys
import unittest

import extract_markdown_section as extractor


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "assets/project-template/.ai-team/governance/templates.md"
ROLES = SKILL_ROOT / "references/role-protocol.md"


class MarkdownSectionTests(unittest.TestCase):
    def test_task_card_keeps_fenced_headings_and_stops_at_next_outer_h2(self) -> None:
        result = extractor.extract_h2_section(
            TEMPLATES.read_text(encoding="utf-8"), "Task card"
        )
        self.assertIsNotNone(result)
        self.assertIn("## Handoff Snapshot (current authoritative view)", result)
        self.assertIn("## Baseline and re-entry impact", result)
        self.assertNotIn("## Discussion record", result)

    def test_role_section_stops_before_next_role(self) -> None:
        result = extractor.extract_h2_section(
            ROLES.read_text(encoding="utf-8"), "Independent verifier"
        )
        self.assertIsNotNone(result)
        self.assertIn("### Responsibilities", result)
        self.assertNotIn("## Code and security reviewer", result)

    def test_cli_prints_requested_section(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SKILL_ROOT / "scripts/extract_markdown_section.py"),
                str(TEMPLATES),
                "Minimal Fast-path task card",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(result.stdout.startswith("## Minimal Fast-path task card"))
        self.assertNotIn("## Required fingerprint example", result.stdout)


if __name__ == "__main__":
    unittest.main()
