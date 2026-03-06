"""
Pipeline-wide configuration — structures, templates, asset types.

All overridable constants are collected here.  Per-machine overrides
are loaded from config/local.py (gitignored; see local.py.example).

If DRIVE_ROOT is overridden in local.py, every path derived from it
(PROJECTS_DIR, RESOURCES_DIR, etc.) is re-computed automatically.
Individual path overrides still take precedence over re-derived values.

Usage:
    from config import PROJECT_STRUCTURE, ASSET_TYPES, PROJECTS_DIR
"""

import lightwarp.env as _env

from config.structures import (
    PROJECT_STRUCTURE,
    ASSET_STRUCTURE,
    SHOT_STRUCTURE,
    RENDER_STRUCTURE,
    ASSET_TYPES,
)
from config.templates import TEMPLATE_MAPPINGS

DRIVE_ROOT = _env.DRIVE_ROOT
PROJECTS_DIR = _env.PROJECTS_DIR
RESOURCES_DIR = _env.RESOURCES_DIR
SOFTWARE_DIR = _env.SOFTWARE_DIR
TEMPLATES_DIR = _env.TEMPLATES_DIR

try:
    from config import local as _local  # type: ignore[attr-defined]

    _drive_override = getattr(_local, "DRIVE_ROOT", None)
    if _drive_override is not None:
        DRIVE_ROOT = _drive_override
        PROJECTS_DIR = DRIVE_ROOT / "projects"
        RESOURCES_DIR = DRIVE_ROOT / "resources"
        SOFTWARE_DIR = DRIVE_ROOT / "software"
        TEMPLATES_DIR = RESOURCES_DIR / "templates"

    PROJECTS_DIR = getattr(_local, "PROJECTS_DIR", PROJECTS_DIR)
    RESOURCES_DIR = getattr(_local, "RESOURCES_DIR", RESOURCES_DIR)
    SOFTWARE_DIR = getattr(_local, "SOFTWARE_DIR", SOFTWARE_DIR)
    TEMPLATES_DIR = getattr(_local, "TEMPLATES_DIR", TEMPLATES_DIR)
    PROJECT_STRUCTURE = getattr(_local, "PROJECT_STRUCTURE", PROJECT_STRUCTURE)
    ASSET_STRUCTURE = getattr(_local, "ASSET_STRUCTURE", ASSET_STRUCTURE)
    SHOT_STRUCTURE = getattr(_local, "SHOT_STRUCTURE", SHOT_STRUCTURE)
    RENDER_STRUCTURE = getattr(_local, "RENDER_STRUCTURE", RENDER_STRUCTURE)
    TEMPLATE_MAPPINGS = getattr(_local, "TEMPLATE_MAPPINGS", TEMPLATE_MAPPINGS)
    ASSET_TYPES = getattr(_local, "ASSET_TYPES", ASSET_TYPES)
    del _local, _drive_override
except ImportError:
    pass
