#!/usr/bin/env python3
"""Regression tests for fence-aware Markdown section extraction."""

from pathlib import Path
import re
import subprocess
import sys
import unittest

try:
    from . import extract_markdown_section as extractor
except ImportError:
    import extract_markdown_section as extractor


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "assets/project-template/.ai-team/governance/templates.md"
ROLES = SKILL_ROOT / "references/role-protocol.md"
POLICY = SKILL_ROOT / "references/delivery-policy.md"


class MarkdownSectionTests(unittest.TestCase):
    def test_task_card_keeps_fenced_headings_and_stops_at_next_outer_h2(self) -> None:
        result = extractor.extract_h2_section(
            TEMPLATES.read_text(encoding="utf-8"), "Task card"
        )
        self.assertIsNotNone(result)
        self.assertIn("## Handoff Snapshot", result)
        self.assertIn("## Verification and findings", result)
        self.assertNotIn("## Discussion record", result)

    def test_role_section_stops_before_next_role(self) -> None:
        result = extractor.extract_h2_section(
            ROLES.read_text(encoding="utf-8"), "Independent verifier"
        )
        self.assertIsNotNone(result)
        self.assertIn("### Responsibilities", result)
        self.assertNotIn("## Code and security reviewer", result)

    def test_optional_suffix_match_supports_validator_headings(self) -> None:
        text = """\
## Handoff Snapshot (current authoritative view)
- Current state: analysis

## Delivery planning
- Execution lane: standard
"""
        self.assertIsNone(extractor.extract_h2_section(text, "Handoff Snapshot"))
        result = extractor.extract_h2_section(
            text, "Handoff Snapshot", allow_suffix=True
        )
        self.assertIsNotNone(result)
        self.assertIn("Current state: analysis", result)
        self.assertNotIn("Delivery planning", result)

    def test_visible_markdown_ignores_comments_and_reports_duplicate_h2(self) -> None:
        text = """\
<!-- ## Handoff Snapshot -->
## Handoff Snapshot
```md
## Handoff Snapshot
```
## Handoff Snapshot
"""
        counts = extractor.h2_heading_counts(text)
        self.assertEqual(2, counts[extractor.normalize_heading("Handoff Snapshot")])

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

    def test_every_catalog_navigation_heading_is_extractable(self) -> None:
        text = TEMPLATES.read_text(encoding="utf-8")
        navigation = extractor.extract_h2_section(text, "Catalog navigation")
        self.assertIsNotNone(navigation)
        headings = [
            heading
            for line in navigation.splitlines()
            if line.startswith("- ")
            for heading in re.findall(r"`([^`]+)`", line)
        ]
        self.assertTrue(headings)
        missing = [
            heading
            for heading in headings
            if extractor.extract_h2_section(text, heading) is None
        ]
        self.assertEqual([], missing)

    def test_role_assignment_envelope_is_referenced_by_role_protocol(self) -> None:
        templates = TEMPLATES.read_text(encoding="utf-8")
        roles = ROLES.read_text(encoding="utf-8")
        self.assertIsNotNone(
            extractor.extract_h2_section(templates, "Role assignment envelope")
        )
        self.assertIn("`Role assignment envelope`", roles)

    def test_run_delivery_policy_links_resolve_to_exact_h2_sections(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        run_delivery = extractor.extract_h2_section(skill, "Run delivery")
        self.assertIsNotNone(run_delivery)
        references = re.findall(
            r"\[([^\]]+)\]\(references/delivery-policy\.md#([^)]+)\)",
            run_delivery,
        )
        self.assertTrue(references)
        policy = POLICY.read_text(encoding="utf-8")
        for heading, anchor in references:
            expected_anchor = re.sub(r"[^a-z0-9 -]", "", heading.lower()).replace(" ", "-")
            self.assertEqual(expected_anchor, anchor, heading)
            self.assertIsNotNone(
                extractor.extract_h2_section(policy, heading),
                f"delivery-policy H2 not found: {heading}",
            )


if __name__ == "__main__":
    unittest.main()
