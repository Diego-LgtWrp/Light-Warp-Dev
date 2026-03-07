"""
LightWarp pipeline — one-stop import for studio environment, project setup,
and pipeline navigation.

Usage::

    import lightwarp as lw

    # Environment paths (respects config/local.py overrides)
    lw.DRIVE_ROOT
    lw.PROJECTS_DIR

    # Project setup
    lw.create_project_structure(root, "MyFilm")
    lw.create_asset_structure(project, "char_hero")

    # Navigation
    lw.project_path("MyFilm")
    lw.list_projects()
    lw.open_shot("MyFilm", "sh010")

    # Utilities
    lw.open_folder(some_path)
    lw.log_to_project(root, "tool", "message")
"""

__version__ = "0.1.0"

# ---------------------------------------------------------------------------
# Environment paths — imported from config so local.py overrides are applied.
# lightwarp/config/__init__.py imports from lightwarp.env (a submodule), so
# there is no circular dependency.
# ---------------------------------------------------------------------------
from lightwarp.config import (  # noqa: F401 — re-export
    DRIVE_ROOT,
    PROJECTS_DIR,
    LIB_DIR,
    SOFTWARE_DIR,
    TEMPLATES_DIR,
)

# ---------------------------------------------------------------------------
# Folder-spec engine
# ---------------------------------------------------------------------------
from lightwarp.folders import (  # noqa: F401 — re-export
    FolderSpec,
    PipelineNoChangesError,
    PipelinePathExistsError,
    collect_missing_dirs,
    ensure_dirs_from_spec,
    ensure_existing_dir,
    raise_exists,
)

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
from lightwarp.util import log_to_project, open_folder  # noqa: F401

# ---------------------------------------------------------------------------
# Project setup (create / update / preview)
# ---------------------------------------------------------------------------
from lightwarp.setup import (  # noqa: F401 — re-export
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

# ---------------------------------------------------------------------------
# Navigation (path resolvers, listing, open-in-browser)
# ---------------------------------------------------------------------------
from lightwarp.navigate import (  # noqa: F401 — re-export
    asset_path,
    list_assets,
    list_projects,
    list_shots,
    open_asset,
    open_project,
    open_render,
    open_shot,
    project_path,
    render_path,
    shot_path,
)

# ---------------------------------------------------------------------------
# Naming and versioning
# ---------------------------------------------------------------------------
from lightwarp.naming import (  # noqa: F401 — re-export
    format_version,
    latest_version_number,
    latest_version_path,
    list_versions,
    next_version_path,
    parse_version,
    save_next_version,
    version_path,
)
