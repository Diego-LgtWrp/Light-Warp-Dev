"""
Pipeline-wide configuration — structures, templates, asset types, paths.

All overridable constants are collected here.  Per-machine overrides
are loaded from lightwarp/config/local.py (gitignored; see local.py.example).

If DRIVE_ROOT is overridden in local.py, every path derived from it
(PROJECTS_DIR, LIB_DIR, etc.) is re-computed automatically.
Individual path overrides still take precedence over re-derived values.

Usage:
    from lightwarp.config import PROJECT_STRUCTURE, ASSET_TYPES, PROJECTS_DIR
"""

from pathlib import Path

from lightwarp.config.defaults import (
    PROJECT_STRUCTURE,
    ASSET_STRUCTURE,
    SHOT_STRUCTURE,
    RENDER_STRUCTURE,
    ASSET_TYPES,
    TEMPLATE_MAPPINGS,
    VERSION_PADDING,
    VERSION_PREFIX,
    VERSION_SEPARATOR,
)

# Auto-detect drive layout from this file's position on disk.
# <DRIVE_ROOT>/pipeline/lightwarp/config/__init__.py
_PIPELINE_ROOT = Path(__file__).resolve().parents[2]

DRIVE_ROOT = _PIPELINE_ROOT.parent
PROJECTS_DIR = DRIVE_ROOT / "projects"
LIB_DIR = DRIVE_ROOT / "lib"
SOFTWARE_DIR = _PIPELINE_ROOT / "software"
TEMPLATES_DIR = SOFTWARE_DIR / "templates"

try:
    from lightwarp.config import local as _local  # type: ignore[attr-defined]

    _drive_override = getattr(_local, "DRIVE_ROOT", None)
    if _drive_override is not None:
        DRIVE_ROOT = _drive_override
        PROJECTS_DIR = DRIVE_ROOT / "projects"
        LIB_DIR = DRIVE_ROOT / "lib"
        _pipeline_root = DRIVE_ROOT / "pipeline"
        SOFTWARE_DIR = _pipeline_root / "software"
        TEMPLATES_DIR = SOFTWARE_DIR / "templates"

    PROJECTS_DIR = getattr(_local, "PROJECTS_DIR", PROJECTS_DIR)
    LIB_DIR = getattr(_local, "LIB_DIR", LIB_DIR)
    SOFTWARE_DIR = getattr(_local, "SOFTWARE_DIR", SOFTWARE_DIR)
    TEMPLATES_DIR = getattr(_local, "TEMPLATES_DIR", TEMPLATES_DIR)
    PROJECT_STRUCTURE = getattr(_local, "PROJECT_STRUCTURE", PROJECT_STRUCTURE)
    ASSET_STRUCTURE = getattr(_local, "ASSET_STRUCTURE", ASSET_STRUCTURE)
    SHOT_STRUCTURE = getattr(_local, "SHOT_STRUCTURE", SHOT_STRUCTURE)
    RENDER_STRUCTURE = getattr(_local, "RENDER_STRUCTURE", RENDER_STRUCTURE)
    TEMPLATE_MAPPINGS = getattr(_local, "TEMPLATE_MAPPINGS", TEMPLATE_MAPPINGS)
    ASSET_TYPES = getattr(_local, "ASSET_TYPES", ASSET_TYPES)
    VERSION_PREFIX = getattr(_local, "VERSION_PREFIX", VERSION_PREFIX)
    VERSION_SEPARATOR = getattr(_local, "VERSION_SEPARATOR", VERSION_SEPARATOR)
    VERSION_PADDING = getattr(_local, "VERSION_PADDING", VERSION_PADDING)
    del _local, _drive_override
except ImportError:
    pass
