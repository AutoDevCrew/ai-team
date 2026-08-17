#!/usr/bin/env python3
"""Tests for deterministic delivery-package inventory handling."""

import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout

try:
    from . import intake_package_inventory as inventory
except ImportError:
    import intake_package_inventory as inventory


class IntakePackageInventoryTests(unittest.TestCase):
    def make_snapshot(self, root: Path, manifest_path: Path) -> dict:
        with redirect_stdout(io.StringIO()):
            inventory.snapshot_command(root, manifest_path)
        return inventory.load_manifest(manifest_path)

    def test_snapshot_classify_and_verify_closed_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            package = workspace / "delivery"
            package.mkdir()
            (package / "prd.md").write_text("requirements\n", encoding="utf-8")
            generated = package / "generated"
            generated.mkdir()
            (generated / "demo.js").write_text("compiled\n", encoding="utf-8")
            manifest_path = workspace / "intake.json"

            manifest = self.make_snapshot(package, manifest_path)
            self.assertEqual(2, len(manifest["items"]))
            self.assertTrue(
                any("still pending" in error for error in inventory.inventory_errors(manifest, rescan=True))
            )

            with redirect_stdout(io.StringIO()):
                inventory.mark_command(
                    manifest_path,
                    "reviewed",
                    ["prd.md"],
                    [],
                    ["EVID-INTAKE-001#prd"],
                    "",
                )
                inventory.mark_command(
                    manifest_path,
                    "excluded",
                    [],
                    ["generated"],
                    [],
                    "generated output derived from the reviewed demo source",
                )
            manifest = inventory.load_manifest(manifest_path)
            self.assertEqual(
                {"total": 2, "reviewed": 1, "excluded": 1, "gap": 0},
                inventory.manifest_counts(manifest),
            )
            self.assertEqual([], inventory.inventory_errors(manifest, rescan=True))

    def test_verify_detects_changed_and_unrecorded_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            package = workspace / "delivery"
            package.mkdir()
            source = package / "prd.md"
            source.write_text("v1\n", encoding="utf-8")
            manifest_path = workspace / "intake.json"
            self.make_snapshot(package, manifest_path)
            with redirect_stdout(io.StringIO()):
                inventory.mark_command(
                    manifest_path,
                    "reviewed",
                    ["prd.md"],
                    [],
                    ["EVID-INTAKE-001#prd"],
                    "",
                )

            source.write_text("v2\n", encoding="utf-8")
            (package / "new.png").write_bytes(b"image")
            errors = inventory.inventory_errors(
                inventory.load_manifest(manifest_path), rescan=True
            )
            self.assertTrue(any("changed after snapshot: prd.md" in error for error in errors), errors)
            self.assertTrue(any("unrecorded item: new.png" in error for error in errors), errors)

    def test_snapshot_rejects_output_inside_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            (package / "prd.md").write_text("requirements\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside the scanned package root"):
                inventory.snapshot_command(package, package / "intake.json")

    def test_verify_compacts_multiple_failures_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            package = workspace / "delivery"
            package.mkdir()
            (package / "one.md").write_text("one\n", encoding="utf-8")
            (package / "two.md").write_text("two\n", encoding="utf-8")
            manifest_path = workspace / "intake.json"
            self.make_snapshot(package, manifest_path)
            output = io.StringIO()
            with redirect_stdout(output):
                result = inventory.verify_command(manifest_path, no_rescan=False)
            self.assertEqual(1, result)
            self.assertEqual(1, output.getvalue().count("still pending"))
            self.assertIn("1 additional error(s) suppressed", output.getvalue())

    def test_manifest_json_is_deterministic_and_ascii_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            package = workspace / "delivery"
            package.mkdir()
            unicode_name = "requirements-\u9700\u6c42.md"
            unicode_text = "\u9700\u6c42\n"
            (package / unicode_name).write_text(unicode_text, encoding="utf-8")
            manifest_path = workspace / "intake.json"
            self.make_snapshot(package, manifest_path)
            raw = manifest_path.read_text(encoding="utf-8")
            json.loads(raw)
            self.assertTrue(raw.isascii())


if __name__ == "__main__":
    unittest.main()
