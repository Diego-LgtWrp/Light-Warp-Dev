"""
Project structure builders — create, update, and preview
project / asset / shot directory trees.

This module is the canonical home for pipeline structure operations.
``tools/proj_folders/core.py`` re-exports from here for backward
compatibility with the CLI and GUI entry points.

Usage::

    import lightwarp as lw

    lw.create_project_structure(root, "MyFilm")
    lw.create_asset_structure(project, "char_hero", create_blend_file=True)
"""

import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from config import (
    ASSET_STRUCTURE,
    PROJECT_STRUCTURE,
    PROJECTS_DIR,
    RENDER_STRUCTURE,
    SHOT_STRUCTURE,
    TEMPLATE_MAPPINGS,
    TEMPLATES_DIR,
)
from lightwarp.folders import (
    PipelineNoChangesError,
    PipelinePathExistsError,
    collect_missing_dirs,
    ensure_dirs_from_spec,
    ensure_existing_dir,
    raise_exists,
)
from lightwarp.util import log_to_project

TOOL_NAME = "proj_folders"


def get_default_projects_root() -> Path:
    """Return the resolved default projects directory."""
    return PROJECTS_DIR


def _project_root(projects_root: Path, project_name: str) -> Path:
    return projects_root / project_name


def _asset_root(project_root: Path, asset_name: str) -> Path:
    return project_root / "asset" / asset_name


def _shot_roots(project_root: Path, shot_name: str) -> Tuple[Path, Path]:
    return project_root / "shot" / shot_name, project_root / "render" / shot_name


def _copy_asset_template(
    asset_root: Path, asset_name: str, template_path: Path,
    subfolder: str, extension: str,
) -> Path:
    """Copy template to asset_root/subfolder/[asset_name].extension."""
    dest_dir = asset_root / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{asset_name}{extension}"
    if not template_path.is_file():
        raise FileNotFoundError(
            f"Template not found: {template_path}\n"
            f"Check TEMPLATES_DIR in config/ or override via config/local.py."
        )
    shutil.copy2(template_path, dest)
    return dest


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_project_structure(projects_root: Path, project_name: str) -> Path:
    """Create full project tree; raises PipelinePathExistsError if it already exists."""
    root = _project_root(projects_root, project_name)
    if root.exists():
        raise_exists("Project", project_name, root)
    created = ensure_dirs_from_spec(root, PROJECT_STRUCTURE)
    log_to_project(root, TOOL_NAME, f"create-project {project_name} ({len(created)} new dirs)")
    return root


def create_asset_structure(
    project_root: Path, asset_name: str, *,
    create_blend_file: bool = False, create_substance_file: bool = False,
) -> Path:
    """Create asset tree; optionally copy .blend/.spp templates. Raises on existing path."""
    asset = _asset_root(project_root, asset_name)
    if asset.exists():
        raise_exists("Asset", asset_name, asset)
    created = ensure_dirs_from_spec(asset, ASSET_STRUCTURE)
    templates_to_copy = []
    if create_blend_file:
        templates_to_copy.append("blend")
    if create_substance_file:
        templates_to_copy.append("substance")
    for key in templates_to_copy:
        m = TEMPLATE_MAPPINGS[key]
        _copy_asset_template(asset, asset_name, TEMPLATES_DIR / m["filename"], m["subfolder"], m["extension"])
    log_to_project(project_root, TOOL_NAME, f"create-asset {asset_name} ({len(created)} new dirs)")
    return asset


def create_shot_structure(project_root: Path, shot_name: str) -> Tuple[Path, Path]:
    """Create shot + render trees; raises on existing path. Returns (shot_root, render_root)."""
    shot, render = _shot_roots(project_root, shot_name)
    if shot.exists():
        raise_exists("Shot", shot_name, shot)
    if render.exists():
        raise_exists("Render folder for shot", shot_name, render)
    cs = ensure_dirs_from_spec(shot, SHOT_STRUCTURE)
    cr = ensure_dirs_from_spec(render, RENDER_STRUCTURE)
    log_to_project(project_root, TOOL_NAME, f"create-shot {shot_name} ({len(cs)} shot, {len(cr)} render dirs)")
    return shot, render


def create_project(
    projects_root: Path, project_name: str, *,
    assets: Optional[List[str]] = None, shots: Optional[List[str]] = None,
) -> Path:
    """Create project tree and optionally add initial assets and shots."""
    root = create_project_structure(projects_root, project_name)
    for name in (assets or []):
        create_asset_structure(root, name)
    for name in (shots or []):
        create_shot_structure(root, name)
    return root


# ---------------------------------------------------------------------------
# Preview (no filesystem changes)
# ---------------------------------------------------------------------------

def preview_project_structure(projects_root: Path, project_name: str) -> List[Path]:
    """Return folders that create_project_structure would make."""
    root = _project_root(projects_root, project_name)
    if root.exists():
        raise_exists("Project", project_name, root)
    return collect_missing_dirs(root, PROJECT_STRUCTURE)


def preview_asset_structure(project_root: Path, asset_name: str) -> List[Path]:
    """Return folders that create_asset_structure would make."""
    asset = _asset_root(project_root, asset_name)
    if asset.exists():
        raise_exists("Asset", asset_name, asset)
    return collect_missing_dirs(asset, ASSET_STRUCTURE)


def preview_shot_structure(project_root: Path, shot_name: str) -> Tuple[List[Path], List[Path]]:
    """Return (shot_folders, render_folders) that create_shot_structure would make."""
    shot, render = _shot_roots(project_root, shot_name)
    if shot.exists() or render.exists():
        raise PipelinePathExistsError(
            f"Shot or render folder already exists for '{shot_name}' at "
            f"{shot.resolve()} or {render.resolve()}."
        )
    return collect_missing_dirs(shot, SHOT_STRUCTURE), collect_missing_dirs(render, RENDER_STRUCTURE)


# ---------------------------------------------------------------------------
# Update (non-destructive, add missing dirs only)
# ---------------------------------------------------------------------------

def update_project_structure(project_root: Path) -> Path:
    """Add any missing PROJECT_STRUCTURE folders under an existing project root."""
    ensure_existing_dir(project_root, "Project root")
    created = ensure_dirs_from_spec(project_root, PROJECT_STRUCTURE)
    if not created:
        raise PipelineNoChangesError(f"Project structure already up to date at {project_root.resolve()}.")
    log_to_project(project_root, TOOL_NAME, f"update-project ({len(created)} new dirs)")
    return project_root


def update_asset_structure(project_root: Path, asset_name: str) -> Path:
    """Add any missing ASSET_STRUCTURE folders under an existing asset root."""
    asset = _asset_root(project_root, asset_name)
    ensure_existing_dir(asset, "Asset root")
    created = ensure_dirs_from_spec(asset, ASSET_STRUCTURE)
    if not created:
        raise PipelineNoChangesError(f"Asset structure already up to date at {asset.resolve()}.")
    log_to_project(project_root, TOOL_NAME, f"update-asset {asset_name} ({len(created)} new dirs)")
    return asset


def update_shot_structure(project_root: Path, shot_name: str) -> Tuple[Path, Path]:
    """Add any missing SHOT/RENDER_STRUCTURE folders under an existing shot/render root."""
    shot, render = _shot_roots(project_root, shot_name)
    ensure_existing_dir(shot, "Shot root")
    ensure_existing_dir(render, "Render root for shot")
    cs = ensure_dirs_from_spec(shot, SHOT_STRUCTURE)
    cr = ensure_dirs_from_spec(render, RENDER_STRUCTURE)
    if not cs and not cr:
        raise PipelineNoChangesError(
            f"Shot/render structure already up to date at {shot.resolve()} and {render.resolve()}."
        )
    log_to_project(project_root, TOOL_NAME, f"update-shot {shot_name} ({len(cs)} shot, {len(cr)} render dirs)")
    return shot, render


# ---------------------------------------------------------------------------
# Preview update (no filesystem changes)
# ---------------------------------------------------------------------------

def preview_update_project_structure(project_root: Path) -> List[Path]:
    """Return folders that update_project_structure would add."""
    ensure_existing_dir(project_root, "Project root")
    return collect_missing_dirs(project_root, PROJECT_STRUCTURE)


def preview_update_asset_structure(project_root: Path, asset_name: str) -> List[Path]:
    """Return folders that update_asset_structure would add."""
    asset = _asset_root(project_root, asset_name)
    ensure_existing_dir(asset, "Asset root")
    return collect_missing_dirs(asset, ASSET_STRUCTURE)


def preview_update_shot_structure(project_root: Path, shot_name: str) -> Tuple[List[Path], List[Path]]:
    """Return folders that update_shot_structure would add."""
    shot, render = _shot_roots(project_root, shot_name)
    ensure_existing_dir(shot, "Shot root")
    ensure_existing_dir(render, "Render root for shot")
    return collect_missing_dirs(shot, SHOT_STRUCTURE), collect_missing_dirs(render, RENDER_STRUCTURE)
