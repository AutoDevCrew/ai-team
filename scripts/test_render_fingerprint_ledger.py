#!/usr/bin/env python3
"""Regression tests for deterministic AI-team fingerprint ledger rendering."""

from pathlib import Path
import hashlib
import tempfile
import unittest

try:
    from . import render_fingerprint_ledger as renderer
except ImportError:
    import render_fingerprint_ledger as renderer


class FingerprintLedgerTests(unittest.TestCase):
    def test_render_emits_matching_inventory_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "src/example.txt"
            source.parent.mkdir()
            source.write_text("example\n", encoding="utf-8")
            output = renderer.render(root, ["src/example.txt"])
            self.assertIn("- Change-set file inventory: `src/example.txt`", output)
            self.assertIn(hashlib.sha256(source.read_bytes()).hexdigest(), output)

    def test_render_rejects_missing_or_escaping_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaises(ValueError):
                renderer.render(root, ["missing.txt"])
            with self.assertRaises(ValueError):
                renderer.render(root, ["../outside.txt"])


if __name__ == "__main__":
    unittest.main()
