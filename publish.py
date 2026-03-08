#!/usr/bin/env python3
"""
Promote dev tools/plugins/templates to their production folders on the Drive.

Runs on the Google Drive (or any directory with the LightWarp layout).
Compares source (dev/) and destination (production/) folders, shows a summary,
and copies only changed files after confirmation.

Usage:
    python publish.py                                        # publish all areas
    python publish.py utils                                  # publish only utils
    python publish.py plugins                                # publish only plugins
    python publish.py templates                              # publish only templates
    python publish.py --dry-run                              # preview only
    python publish.py utils --dry-run                        # preview utils only
"""

from __future__ import annotations

import filecmp
import shutil
import string
import sys
from pathlib import Path
from typing import Dict, List, Tuple

_SKIP_DIRS = frozenset({
    "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".git",
})
_SKIP_EXTENSIONS = frozenset({
    ".pyc", ".pyo", ".pyd", ".egg", ".swp", ".swo",
})
_SKIP_FILES = frozenset({
    ".DS_Store", "Thumbs.db", "desktop.ini",
})

PUBLISH_MAPPINGS: Dict[str, Tuple[str, str]] = {
    "utils":     ("pipeline/utils/dev",              "pipeline/utils/tools"),
    "plugins":   ("pipeline/software/dev/plugins",   "pipeline/software/plugins"),
    "templates": ("pipeline/software/dev/templates",  "pipeline/software/templates"),
}


def _should_skip(rel: Path) -> bool:
    if rel.name in _SKIP_FILES:
        return True
    if rel.suffix in _SKIP_EXTENSIONS:
        return True
    for part in rel.parts:
        if part in _SKIP_DIRS or part.endswith(".egg-info"):
            return True
    return False


def _collect_files(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    result: set[str] = set()
    for f in root.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(root)
        if not _should_skip(rel):
            result.add(rel.as_posix())
    return result


def _remove_empty_dirs(target: Path) -> None:
    if not target.is_dir():
        return
    for d in sorted(target.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()


def _diff_area(
    src_root: Path, dst_root: Path,
) -> Tuple[List[str], List[str], List[str], List[str]]:
    src_files = _collect_files(src_root)
    dst_files = _collect_files(dst_root)

    to_add: List[str] = []
    to_update: List[str] = []
    unchanged: List[str] = []

    for f in sorted(src_files):
        src = src_root / f
        dst = dst_root / f
        if not dst.exists():
            to_add.append(f)
        elif not filecmp.cmp(str(src), str(dst), shallow=False):
            to_update.append(f)
        else:
            unchanged.append(f)

    to_remove = sorted(dst_files - src_files)
    return to_add, to_update, to_remove, unchanged


def _is_lightwarp_root(path: Path) -> bool:
    return all((path / d).is_dir() for d in ("projects", "pipeline", "lib"))


def _find_drive() -> Path | None:
    if sys.platform == "win32":
        for letter in string.ascii_uppercase:
            root = Path(f"{letter}:/")
            if not root.is_dir():
                continue
            for name in ("Shared drives", "My Drive"):
                candidate = root / name / "LightWarp_Test"
                if _is_lightwarp_root(candidate):
                    return candidate
    else:
        home = Path.home()
        search_roots = [
            Path("/Volumes/GoogleDrive/Shared drives"),
            home / "Library" / "CloudStorage",
            home / "Google Drive" / "Shared drives",
        ]
        for search_root in search_roots:
            if not search_root.is_dir():
                continue
            for child in search_root.iterdir():
                if search_root.name == "CloudStorage":
                    if not child.name.startswith("GoogleDrive"):
                        continue
                    candidate = child / "Shared drives" / "LightWarp_Test"
                else:
                    candidate = (
                        child if child.name == "LightWarp_Test"
                        else child / "LightWarp_Test"
                    )
                if _is_lightwarp_root(candidate):
                    return candidate
    return None


def main() -> None:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    areas = list(PUBLISH_MAPPINGS.keys())
    drive_path: Path | None = None

    for a in args:
        if a in PUBLISH_MAPPINGS:
            areas = [a]
        else:
            drive_path = Path(a).resolve()

    if drive_path is None:
        drive_path = _find_drive()

    if drive_path is None:
        print("ERROR: Could not find the LightWarp shared drive.")
        print("Provide the path explicitly:  python publish.py <drive_root>")
        sys.exit(1)

    if not _is_lightwarp_root(drive_path):
        print(f"ERROR: Not a valid LightWarp root: {drive_path}")
        sys.exit(1)

    print()
    print(f"  Drive  : {drive_path}")
    if dry_run:
        print(f"  Mode   : DRY RUN (no changes will be made)")
    print()

    total_add = 0
    total_update = 0
    total_remove = 0
    total_unchanged = 0
    area_diffs: Dict[str, Tuple[Path, Path, List[str], List[str], List[str]]] = {}

    for area in areas:
        src_rel, dst_rel = PUBLISH_MAPPINGS[area]
        src_root = drive_path / src_rel
        dst_root = drive_path / dst_rel

        if not src_root.is_dir():
            print(f"  [{area}] Source not found: {src_root} — skipping")
            continue

        to_add, to_update, to_remove, unchanged = _diff_area(src_root, dst_root)
        if not to_add and not to_update and not to_remove:
            print(f"  [{area}] Already up to date.")
            continue

        area_diffs[area] = (src_root, dst_root, to_add, to_update, to_remove)
        total_add += len(to_add)
        total_update += len(to_update)
        total_remove += len(to_remove)
        total_unchanged += len(unchanged)

        print(f"  [{area}]  {src_rel}/  -->  {dst_rel}/")
        if to_add:
            print(f"    Add ({len(to_add)}):")
            for f in to_add:
                print(f"      + {f}")
        if to_update:
            print(f"    Update ({len(to_update)}):")
            for f in to_update:
                print(f"      ~ {f}")
        if to_remove:
            print(f"    Remove ({len(to_remove)}):")
            for f in to_remove:
                print(f"      - {f}")
        print()

    if not area_diffs:
        print("Nothing to publish.")
        return

    print(f"  Total: {total_add} to add, {total_update} to update, "
          f"{total_remove} to remove  ({total_unchanged} unchanged)")
    print()

    if dry_run:
        print("Dry run complete.  Re-run without --dry-run to apply.")
        return

    if input("Apply? [y/N] ").strip().lower() != "y":
        print("Aborted.")
        return

    errors: List[str] = []

    for area, (src_root, dst_root, to_add, to_update, to_remove) in area_diffs.items():
        for f in to_add + to_update:
            src = src_root / f
            dst = dst_root / f
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))
            except OSError as exc:
                errors.append(f"  [{area}] COPY {f}: {exc}")

        for f in to_remove:
            try:
                (dst_root / f).unlink()
            except OSError as exc:
                errors.append(f"  [{area}] DEL  {f}: {exc}")

        _remove_empty_dirs(dst_root)

    print()
    if errors:
        print(f"Published with {len(errors)} error(s):")
        for e in errors:
            print(e)
    else:
        print(f"Publish complete.  {total_add} added, {total_update} updated, "
              f"{total_remove} removed.")


if __name__ == "__main__":
    main()
