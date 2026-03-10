"""
Re-export shim — all logic lives in ``lightwarp.project``.

The CLI and GUI import from this module so they don't need to know
the full lightwarp path.
"""

from lightwarp.project import (  # noqa: F401 — re-export
    TOOL_NAME,
    create_asset_structure,
    create_project,
    create_project_structure,
    create_shot_structure,
    get_default_projects_root,
    preview_asset_structure,
    preview_project_structure,
    preview_shot_structure,
    preview_update_asset_structure,
    preview_update_project_structure,
    preview_update_shot_structure,
    update_asset_structure,
    update_project_structure,
    update_shot_structure,
)
