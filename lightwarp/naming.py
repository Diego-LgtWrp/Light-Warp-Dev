"""
File naming and versioning engine.

Provides helpers to parse, format, discover, and create versioned
pipeline files.  All functions respect the naming settings in
``lightwarp/config/naming.py`` (overridable via ``lightwarp/config/local.py``).

Quick reference::

    import lightwarp as lw

    # Next version path (does not create the file)
    p = lw.next_version_path(blend_dir, "char_hero", ".blend")
    #  → .../char_hero_v003.blend

    # Latest existing version
    p = lw.latest_version_path(blend_dir, "char_hero", ".blend")
    #  → .../char_hero_v002.blend

    # Copy a file in as the next version
    p = lw.save_next_version(source, blend_dir, "char_hero")
    #  → copies source → char_hero_v003.blend, returns the Path

    # List every version on disk
    versions = lw.list_versions(blend_dir, "char_hero", ".blend")
    #  → [(1, Path(".../char_hero_v001.blend")), (2, ...)]
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple


def _cfg() -> Tuple[str, str, int]:
    """Return (prefix, separator, padding) from config, late-imported."""
    from lightwarp.config import VERSION_PREFIX, VERSION_SEPARATOR, VERSION_PADDING
    return VERSION_PREFIX, VERSION_SEPARATOR, VERSION_PADDING


def _version_pattern(name: str, ext: str) -> re.Pattern[str]:
    """Compile a regex that matches ``name_v001.ext`` style filenames."""
    prefix, sep, _ = _cfg()
    return re.compile(
        rf"^{re.escape(name)}{re.escape(sep)}{re.escape(prefix)}(\d+){re.escape(ext)}$",
        re.IGNORECASE,
    )


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_version(filename: str, name: str, ext: str) -> Optional[int]:
    """Extract the version number from *filename*, or ``None`` if it
    doesn't match the expected pattern.

    >>> parse_version("char_hero_v003.blend", "char_hero", ".blend")
    3
    """
    m = _version_pattern(name, ext).match(filename)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_version(name: str, version: int, ext: str) -> str:
    """Build a versioned filename string.

    >>> format_version("char_hero", 3, ".blend")
    'char_hero_v003.blend'
    """
    prefix, sep, padding = _cfg()
    return f"{name}{sep}{prefix}{version:0{padding}d}{ext}"


def version_path(directory: Path, name: str, version: int, ext: str) -> Path:
    """Return the full path for a specific version number."""
    return directory / format_version(name, version, ext)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def list_versions(
    directory: Path, name: str, ext: str,
) -> List[Tuple[int, Path]]:
    """Return every versioned file in *directory* as ``(version, path)``
    pairs, sorted ascending by version number.

    Non-existent directories return an empty list.
    """
    if not directory.is_dir():
        return []
    pat = _version_pattern(name, ext)
    hits: List[Tuple[int, Path]] = []
    for f in directory.iterdir():
        if not f.is_file():
            continue
        m = pat.match(f.name)
        if m:
            hits.append((int(m.group(1)), f))
    hits.sort(key=lambda t: t[0])
    return hits


def latest_version_path(
    directory: Path, name: str, ext: str,
) -> Optional[Path]:
    """Return the path of the highest-versioned file, or ``None``."""
    versions = list_versions(directory, name, ext)
    return versions[-1][1] if versions else None


def latest_version_number(
    directory: Path, name: str, ext: str,
) -> int:
    """Return the highest version number found, or ``0`` if none exist."""
    versions = list_versions(directory, name, ext)
    return versions[-1][0] if versions else 0


def next_version_path(directory: Path, name: str, ext: str) -> Path:
    """Return the path for the *next* version (current max + 1).

    If no versions exist yet, returns version 1.  Does **not** create
    the file — use :func:`save_next_version` for that.
    """
    nxt = latest_version_number(directory, name, ext) + 1
    return version_path(directory, name, nxt, ext)


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def save_next_version(
    source: Path,
    directory: Path,
    name: str,
    *,
    ext: Optional[str] = None,
) -> Path:
    """Copy *source* into *directory* as the next version and return the
    new path.

    *ext* defaults to the source file's suffix (e.g. ``".blend"``).

    Raises ``FileNotFoundError`` if *source* doesn't exist.
    """
    if not source.is_file():
        raise FileNotFoundError(f"Source file does not exist: {source}")
    extension = ext or source.suffix
    dest = next_version_path(directory, name, extension)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return dest
