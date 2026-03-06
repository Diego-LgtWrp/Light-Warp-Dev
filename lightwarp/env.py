"""
LightWarp shared environment — single source of truth for drive layout.

Auto-detects the drive root from this file's position on the shared drive.
Any LightWarp tool can ``from lightwarp.env import PROJECTS_DIR`` instead of
hardcoding long paths.

File location:  <DRIVE_ROOT>/pipeline/lightwarp/env.py
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PIPELINE_ROOT = _HERE.parent

DRIVE_ROOT = _PIPELINE_ROOT.parent
PROJECTS_DIR = DRIVE_ROOT / "projects"
RESOURCES_DIR = DRIVE_ROOT / "resources"
SOFTWARE_DIR = DRIVE_ROOT / "software"
TEMPLATES_DIR = RESOURCES_DIR / "templates"
