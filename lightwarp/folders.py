"""
Generic folder-spec engine for creating and auditing directory trees.

A FolderSpec is a nested dict where keys are folder names and values are
child FolderSpecs (or empty dicts for leaf folders).  The two core functions
— ensure_dirs_from_spec and collect_missing_dirs — are used by any tool
that needs to build or validate folder hierarchies.
"""

from pathlib import Path
from typing import Any, Dict, List

FolderSpec = Dict[str, Any]


class PipelinePathExistsError(FileExistsError):
    """Raised when a target path already exists to prevent overwriting."""


class PipelineNoChangesError(Exception):
    """Raised when an update operation finds nothing to change."""


def raise_exists(kind: str, name: str, path: Path) -> None:
    raise PipelinePathExistsError(
        f"{kind} '{name}' already exists at {path.resolve()}. "
        "Use a different name or remove/rename the existing folder."
    )


def ensure_existing_dir(path: Path, label: str) -> None:
    if not path.is_dir():
        raise FileNotFoundError(f"{label} does not exist or is not a directory: {path}")


def ensure_dirs_from_spec(root: Path, spec: FolderSpec) -> List[Path]:
    """Recursively create directories from a nested dict; return newly created paths."""
    created: List[Path] = []
    for name, children in spec.items():
        folder = root / name
        is_new = not folder.exists()
        folder.mkdir(parents=True, exist_ok=True)
        if is_new:
            created.append(folder)
        if isinstance(children, dict) and children:
            created.extend(ensure_dirs_from_spec(folder, children))
    return created


def collect_missing_dirs(root: Path, spec: FolderSpec) -> List[Path]:
    """Return all directories from spec that do not yet exist, without creating anything."""
    missing: List[Path] = []
    for name, children in spec.items():
        folder = root / name
        if not folder.exists():
            missing.append(folder)
        if isinstance(children, dict) and children:
            missing.extend(collect_missing_dirs(folder, children))
    return missing
