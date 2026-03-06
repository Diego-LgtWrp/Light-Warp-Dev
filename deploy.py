#!/usr/bin/env python3
"""
Deploy the pipeline from a local git clone to the Google Drive.

One-way sync: git repo -> Drive.  No git operations on the Drive.
Only git-tracked files are copied; stale files are cleaned up.

Usage:
    python deploy.py                                        # auto-detect
    python deploy.py "G:/Shared drives/LightWarp_Test"      # explicit path
    python deploy.py --dry-run                               # preview only
"""

from __future__ import annotations

import filecmp
import shutil
import string
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
MARKER_DIRS = ("projects", "pipeline", "resources")


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )


def _git_ok(*args: str) -> subprocess.CompletedProcess[str]:
    r = _git(*args)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r


def _get_tracked_files() -> set[str]:
    return set(_git_ok("ls-files").stdout.strip().splitlines())


def _is_gitignored(paths: list[str]) -> set[str]:
    """Return the subset of *paths* that the repo's .gitignore would match."""
    if not paths:
        return set()
    r = subprocess.run(
        ["git", "check-ignore", "--stdin"],
        cwd=REPO_DIR,
        input="\n".join(paths),
        capture_output=True,
        text=True,
    )
    return set(r.stdout.strip().splitlines()) if r.stdout.strip() else set()


# ---------------------------------------------------------------------------
# Drive detection  (same logic as setup_local.py)
# ---------------------------------------------------------------------------

def _is_lightwarp_root(path: Path) -> bool:
    return all((path / d).is_dir() for d in MARKER_DIRS)


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


# ---------------------------------------------------------------------------
# Deploy logic
# ---------------------------------------------------------------------------

def _walk_target(target: Path) -> set[str]:
    """Return relative posix paths for every file under *target*."""
    return {
        f.relative_to(target).as_posix()
        for f in target.rglob("*")
        if f.is_file()
    }


def _remove_empty_dirs(target: Path) -> None:
    for d in sorted(target.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()


def main() -> None:
    # ---- Parse args -------------------------------------------------------
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    # ---- Resolve Drive target ---------------------------------------------
    if args:
        drive_root = Path(args[0]).resolve()
    else:
        drive_root = _find_drive()

    if drive_root is None:
        print("ERROR: Could not find the LightWarp shared drive.")
        print("Provide the path explicitly:  python deploy.py <drive_root>")
        sys.exit(1)

    target = drive_root / "pipeline"
    if not target.is_dir():
        print(f"ERROR: Target directory does not exist: {target}")
        sys.exit(1)

    # ---- Git sanity checks ------------------------------------------------
    r = _git("rev-parse", "--is-inside-work-tree")
    if r.returncode != 0:
        print("ERROR: Not a git repository. Run this from your local clone.")
        sys.exit(1)

    branch = _git_ok("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    commit = _git_ok("log", "-1", "--format=%h %s").stdout.strip()

    status = _git("status", "--porcelain").stdout.strip()
    if status:
        print("WARNING: Uncommitted changes in your working tree:")
        for line in status.splitlines():
            print(f"  {line}")
        print()
        if input("Deploy anyway? [y/N] ").strip().lower() != "y":
            print("Aborted.  Commit or stash your changes first.")
            return

    fetch = _git("fetch", "--quiet")
    if fetch.returncode == 0:
        behind = _git("rev-list", "--count", "HEAD..@{u}").stdout.strip()
        if behind.isdigit() and int(behind) > 0:
            print(f"Local branch is {behind} commit(s) behind remote.")
            if input("Pull latest before deploying? [Y/n] ").strip().lower() != "n":
                pull = _git("pull", "--ff-only")
                if pull.returncode != 0:
                    print("Pull failed (merge conflict?). Resolve and retry.")
                    sys.exit(1)
                commit = _git_ok("log", "-1", "--format=%h %s").stdout.strip()
                print(f"Updated to: {commit}\n")

    # ---- Determine changes ------------------------------------------------
    tracked = _get_tracked_files()
    if not tracked:
        print("ERROR: git ls-files returned no tracked files.")
        print("Make sure you have at least one commit in the repo.")
        sys.exit(1)

    drive_files = _walk_target(target)

    to_add: list[str] = []
    to_update: list[str] = []
    unchanged: list[str] = []

    for f in sorted(tracked):
        src = REPO_DIR / f
        dst = target / f
        if not src.is_file():
            continue
        if not dst.exists():
            to_add.append(f)
        elif not filecmp.cmp(str(src), str(dst), shallow=False):
            to_update.append(f)
        else:
            unchanged.append(f)

    extra = sorted(drive_files - tracked)
    ignored = _is_gitignored(extra)
    to_remove = [f for f in extra if f not in ignored]

    # ---- Summary ----------------------------------------------------------
    print()
    print(f"  Branch : {branch}")
    print(f"  Commit : {commit}")
    print(f"  Target : {target}")
    if dry_run:
        print(f"  Mode   : DRY RUN (no changes will be made)")
    print()

    if not to_add and not to_update and not to_remove:
        print("Already up to date.  Nothing to deploy.")
        return

    if to_add:
        print(f"  Add ({len(to_add)}):")
        for f in to_add:
            print(f"    + {f}")
    if to_update:
        print(f"  Update ({len(to_update)}):")
        for f in to_update:
            print(f"    ~ {f}")
    if to_remove:
        print(f"  Remove ({len(to_remove)}):")
        for f in to_remove:
            print(f"    - {f}")
    print()
    print(f"  {len(to_add)} to add, {len(to_update)} to update, "
          f"{len(to_remove)} to remove  ({len(unchanged)} unchanged)")
    print()

    if dry_run:
        print("Dry run complete.  Re-run without --dry-run to apply.")
        return

    if input("Apply? [y/N] ").strip().lower() != "y":
        print("Aborted.")
        return

    # ---- Execute ----------------------------------------------------------
    errors: list[str] = []

    for f in to_add + to_update:
        src = REPO_DIR / f
        dst = target / f
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dst))
        except OSError as exc:
            errors.append(f"  COPY {f}: {exc}")

    for f in to_remove:
        try:
            (target / f).unlink()
        except OSError as exc:
            errors.append(f"  DEL  {f}: {exc}")

    _remove_empty_dirs(target)

    print()
    if errors:
        print(f"Deployed with {len(errors)} error(s):")
        for e in errors:
            print(e)
    else:
        print(f"Deploy complete.  {len(to_add)} added, {len(to_update)} updated, "
              f"{len(to_remove)} removed.")


if __name__ == "__main__":
    main()
