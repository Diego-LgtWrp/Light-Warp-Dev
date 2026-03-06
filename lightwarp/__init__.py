"""
LightWarp pipeline — shared Python package for all pipeline tools and DCC hosts.

NOTE: The path constants re-exported below (DRIVE_ROOT, PROJECTS_DIR, etc.)
are the auto-detected defaults from ``lightwarp.env``.  For values that
respect per-machine overrides from ``config/local.py``, import from
``config`` instead::

    from config import PROJECTS_DIR  # uses local.py overrides
"""

__version__ = "0.1.0"

from lightwarp.env import DRIVE_ROOT, PROJECTS_DIR, RESOURCES_DIR, SOFTWARE_DIR, TEMPLATES_DIR
from lightwarp.folders import (
    FolderSpec,
    PipelineNoChangesError,
    PipelinePathExistsError,
    collect_missing_dirs,
    ensure_dirs_from_spec,
    ensure_existing_dir,
    raise_exists,
)
from lightwarp.util import log_to_project, open_folder
