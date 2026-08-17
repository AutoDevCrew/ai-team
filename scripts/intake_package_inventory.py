#!/usr/bin/env python3
"""Snapshot, classify, and verify a multi-file delivery package."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile


SCHEMA = "ai-team-intake-package-1"
STATUSES = {"pending", "reviewed", "excluded", "gap"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def item_state(path: Path) -> tuple[str, int, str]:
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode):
        target = os.readlink(path)
        return "symlink", metadata.st_size, hashlib.sha256(target.encode()).hexdigest()
    if stat.S_ISREG(metadata.st_mode):
        return "file", metadata.st_size, sha256_file(path)
    return "special", metadata.st_size, ""


def scan(root: Path) -> dict[str, tuple[str, int, str]]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"delivery package root is not a directory: {root}")
    result: dict[str, tuple[str, int, str]] = {}
    try:
        for path in sorted(root.rglob("*")):
            if path.is_dir() and not path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            result[relative] = item_state(path)
    except OSError as exc:
        detail = exc.strerror or exc.__class__.__name__
        raise ValueError(f"cannot inventory delivery package: {detail}") from exc
    if not result:
        raise ValueError(f"delivery package is empty: {root}")
    return result


def write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    temporary.replace(path)


def load_manifest(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read inventory manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("inventory manifest root must be an object")
    return value


def manifest_counts(manifest: dict) -> dict[str, int]:
    items = manifest.get("items")
    if not isinstance(items, list):
        return {"total": 0, "reviewed": 0, "excluded": 0, "gap": 0}
    reviewed = sum(item.get("status") == "reviewed" for item in items if isinstance(item, dict))
    excluded = sum(item.get("status") == "excluded" for item in items if isinstance(item, dict))
    return {
        "total": len(items),
        "reviewed": reviewed,
        "excluded": excluded,
        "gap": len(items) - reviewed - excluded,
    }


def normalize_selector(value: str) -> str:
    normalized = Path(value).as_posix()
    return normalized[2:] if normalized.startswith("./") else normalized


def inventory_errors(manifest: dict, *, rescan: bool) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != SCHEMA:
        errors.append(f"inventory schema must be {SCHEMA}")
    source_root = manifest.get("source_root")
    source_root_valid = isinstance(source_root, str) and bool(source_root.strip())
    if not source_root_valid:
        errors.append("inventory source_root is missing")
    items = manifest.get("items")
    if not isinstance(items, list) or not items:
        errors.append("inventory items must be a non-empty list")
        return errors

    indexed: dict[str, dict] = {}
    for index, item in enumerate(items):
        label = f"inventory item {index + 1}"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        relative = item.get("path")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append(f"{label} has an unsafe or missing relative path")
            continue
        if relative in indexed:
            errors.append(f"inventory contains duplicate path: {relative}")
        indexed[relative] = item
        if item.get("kind") not in {"file", "symlink", "special"}:
            errors.append(f"inventory item has invalid kind: {relative}")
        if not isinstance(item.get("size"), int) or item.get("size", -1) < 0:
            errors.append(f"inventory item has invalid size: {relative}")
        digest = item.get("sha256")
        if item.get("kind") in {"file", "symlink"} and (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            errors.append(f"inventory item has invalid SHA-256: {relative}")
        status_value = item.get("status")
        if status_value not in STATUSES:
            errors.append(f"inventory item has invalid status: {relative}")
        evidence = item.get("evidence")
        reason = item.get("reason")
        if status_value == "reviewed" and (
            not isinstance(evidence, list)
            or not evidence
            or any(
                not isinstance(value, str) or "EVID-" not in value.upper()
                for value in evidence
            )
        ):
            errors.append(f"reviewed inventory item requires an EVID-... reference: {relative}")
        if status_value in {"excluded", "gap"} and (
            not isinstance(reason, str) or len(reason.strip()) < 5
        ):
            errors.append(f"{status_value} inventory item requires a concrete reason: {relative}")
        if status_value == "pending":
            errors.append(f"inventory item is still pending: {relative}")
        elif status_value == "gap":
            errors.append(f"inventory item remains an unresolved gap: {relative}")

    if not rescan or not source_root_valid:
        return errors
    try:
        current = scan(Path(source_root))
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    recorded_paths = set(indexed)
    current_paths = set(current)
    for relative in sorted(recorded_paths - current_paths):
        errors.append(f"inventory source item is missing: {relative}")
    for relative in sorted(current_paths - recorded_paths):
        errors.append(f"inventory source has an unrecorded item: {relative}")
    for relative in sorted(recorded_paths & current_paths):
        item = indexed[relative]
        actual_kind, actual_size, actual_digest = current[relative]
        if (
            item.get("kind") != actual_kind
            or item.get("size") != actual_size
            or item.get("sha256") != actual_digest
        ):
            errors.append(f"inventory source item changed after snapshot: {relative}")
    return errors


def snapshot_command(root: Path, output: Path) -> int:
    root = root.resolve()
    output = output.resolve()
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("inventory output must be outside the scanned package root")
    items = []
    for relative, (kind, size, digest) in scan(root).items():
        items.append(
            {
                "path": relative,
                "kind": kind,
                "size": size,
                "sha256": digest,
                "status": "pending",
                "evidence": [],
                "reason": "",
            }
        )
    manifest = {
        "schema": SCHEMA,
        "source_root": str(root),
        "snapshot_at": now_iso(),
        "updated_at": now_iso(),
        "items": items,
    }
    write_manifest(output, manifest)
    print(f"SNAPSHOT {output} total={len(items)} pending={len(items)}")
    return 0


def mark_command(
    manifest_path: Path,
    status_value: str,
    paths: list[str],
    prefixes: list[str],
    evidence: list[str],
    reason: str,
) -> int:
    if not paths and not prefixes:
        raise ValueError("mark requires at least one --path or --prefix")
    if status_value == "reviewed" and (
        not evidence or any("EVID-" not in value.upper() for value in evidence)
    ):
        raise ValueError("mark --status reviewed requires an --evidence EVID-... reference")
    if status_value in {"excluded", "gap"} and len(reason.strip()) < 5:
        raise ValueError(f"mark --status {status_value} requires --reason")
    normalized_paths = {normalize_selector(value) for value in paths}
    normalized_prefixes = [normalize_selector(value).rstrip("/") for value in prefixes]
    if "" in normalized_paths or "" in normalized_prefixes:
        raise ValueError("mark path and prefix selectors must not be empty")
    manifest = load_manifest(manifest_path)
    matches = 0
    for item in manifest.get("items", []):
        relative = item.get("path", "")
        if relative in normalized_paths or any(
            relative == prefix or relative.startswith(prefix + "/")
            for prefix in normalized_prefixes
        ):
            item["status"] = status_value
            item["evidence"] = evidence if status_value == "reviewed" else []
            item["reason"] = reason if status_value in {"excluded", "gap"} else ""
            matches += 1
    if not matches:
        raise ValueError("mark matched no inventory items")
    manifest["updated_at"] = now_iso()
    write_manifest(manifest_path, manifest)
    counts = manifest_counts(manifest)
    print(
        f"MARKED {matches} status={status_value} "
        f"total={counts['total']} reviewed={counts['reviewed']} "
        f"excluded={counts['excluded']} gap={counts['gap']}"
    )
    return 0


def verify_command(manifest_path: Path, *, no_rescan: bool, verbose: bool = False) -> int:
    manifest = load_manifest(manifest_path)
    errors = inventory_errors(manifest, rescan=not no_rescan)
    counts = manifest_counts(manifest)
    if errors:
        print(f"FAIL {manifest_path.resolve()}")
        for error in errors if verbose else errors[:1]:
            print(f"- {error}")
        if not verbose and len(errors) > 1:
            print(f"- {len(errors) - 1} additional error(s) suppressed; rerun with --verbose")
        return 1
    print(
        f"PASS {manifest_path.resolve()} "
        f"total={counts['total']} reviewed={counts['reviewed']} "
        f"excluded={counts['excluded']} gap={counts['gap']}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot", help="Create a pending inventory snapshot.")
    snapshot_parser.add_argument("package_root", type=Path)
    snapshot_parser.add_argument("--output", type=Path, required=True)

    mark_parser = subparsers.add_parser("mark", help="Classify matching inventory items.")
    mark_parser.add_argument("manifest", type=Path)
    mark_parser.add_argument("--status", choices=sorted(STATUSES - {"pending"}), required=True)
    mark_parser.add_argument("--path", action="append", default=[])
    mark_parser.add_argument("--prefix", action="append", default=[])
    mark_parser.add_argument("--evidence", action="append", default=[])
    mark_parser.add_argument("--reason", default="")

    verify_parser = subparsers.add_parser("verify", help="Validate closure and source freshness.")
    verify_parser.add_argument("manifest", type=Path)
    verify_parser.add_argument(
        "--no-rescan",
        action="store_true",
        help="Validate manifest structure and closure without rescanning the package root.",
    )
    verify_parser.add_argument(
        "--verbose", action="store_true", help="Print every validation error."
    )

    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            return snapshot_command(args.package_root, args.output)
        if args.command == "mark":
            return mark_command(
                args.manifest,
                args.status,
                args.path,
                args.prefix,
                args.evidence,
                args.reason,
            )
        return verify_command(
            args.manifest, no_rescan=args.no_rescan, verbose=args.verbose
        )
    except ValueError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
