#!/usr/bin/env python3
"""
Generate lightwarp/config/local.py with the correct DRIVE_ROOT for this machine.

Run from the pipeline/ directory:
    python setup_local.py            # auto-detect or folder picker
    python setup_local.py <path>     # provide the drive root directly
"""

from __future__ import annotations

import string
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_CONFIG_DIR = _SCRIPT_DIR / "lightwarp" / "config"
_LOCAL_PY = _CONFIG_DIR / "local.py"

MARKER_DIRS = ("projects", "pipeline", "lib")


def _is_lightwarp_root(path: Path) -> bool:
    """Return True if *path* looks like the LightWarp drive root."""
    return all((path / d).is_dir() for d in MARKER_DIRS)


def _already_on_drive() -> bool:
    """True when this script itself lives inside the shared drive."""
    candidate = _SCRIPT_DIR.parent
    return _is_lightwarp_root(candidate)


def _find_candidates() -> list[Path]:
    """Search the filesystem for likely LightWarp drive mount points."""
    found: list[Path] = []

    if sys.platform == "win32":
        for letter in string.ascii_uppercase:
            root = Path(f"{letter}:/")
            if not root.is_dir():
                continue
            for name in ("Shared drives", "My Drive"):
                candidate = root / name / "LightWarp_Test"
                if _is_lightwarp_root(candidate):
                    found.append(candidate)
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
                candidate = child if child.name == "LightWarp_Test" else child / "LightWarp_Test"
                if _is_lightwarp_root(candidate):
                    found.append(candidate)

    return found


def _ask_user_for_path() -> Path | None:
    """Open a folder-picker dialog (tkinter) and return the chosen path."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        chosen = filedialog.askdirectory(
            title="Select the LightWarp shared drive root (e.g. LightWarp_Test)",
        )
        root.destroy()
        if chosen:
            return Path(chosen)
    except Exception:
        pass
    return None


def _write_local_py(drive_root: Path) -> None:
    """Write config/local.py with the given DRIVE_ROOT."""
    posix = drive_root.as_posix()
    _LOCAL_PY.write_text(
        f'from pathlib import Path\n'
        f'\n'
        f'DRIVE_ROOT = Path("{posix}")\n',
        encoding="utf-8",
    )


def main() -> None:
    if _LOCAL_PY.exists():
        print(f"lightwarp/config/local.py already exists:  {_LOCAL_PY}")
        answer = input("Overwrite? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    if _already_on_drive():
        print(
            "This script is running from the shared drive — no DRIVE_ROOT\n"
            "override is needed.  lightwarp/config/local.py was NOT created."
        )
        return

    drive_root: Path | None = None

    if len(sys.argv) > 1:
        drive_root = Path(sys.argv[1]).resolve()
    else:
        candidates = _find_candidates()

        if len(candidates) == 1:
            drive_root = candidates[0]
            print(f"Found shared drive at:  {drive_root}")
        elif len(candidates) > 1:
            print("Multiple LightWarp drives detected:")
            for i, c in enumerate(candidates, 1):
                print(f"  [{i}] {c}")
            choice = input(f"Choose [1-{len(candidates)}]: ").strip()
            try:
                drive_root = candidates[int(choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice. Aborted.")
                return
        else:
            print("Could not auto-detect the LightWarp shared drive.")
            print("Opening folder picker...")
            drive_root = _ask_user_for_path()

    if drive_root is None:
        print("No path selected. Aborted.")
        return

    if not _is_lightwarp_root(drive_root):
        print(f"Warning: {drive_root} does not look like a LightWarp drive root")
        print(f"  (expected subdirectories: {', '.join(MARKER_DIRS)})")
        answer = input("Continue anyway? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    _write_local_py(drive_root)
    print(f"\nCreated {_LOCAL_PY}")
    print(f"  DRIVE_ROOT = Path(\"{drive_root.as_posix()}\")")


if __name__ == "__main__":
    main()
