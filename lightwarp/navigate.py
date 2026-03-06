"""
Pipeline navigation — resolve paths, list contents, and open folders.

All path functions use the overridden PROJECTS_DIR from ``config``, so they
resolve correctly regardless of drive letter or local-clone setup.

Usage::

    import lightwarp as lw

    lw.project_path("MyFilm")
    lw.list_assets("MyFilm")
    lw.open_shot("MyFilm", "sh010")
"""

from pathlib import Path
from typing import List, Optional, Tuple

from lightwarp.util import open_folder


def _projects_dir() -> Path:
    """Late import to avoid circular dependency at module load time."""
    from config import PROJECTS_DIR
    return PROJECTS_DIR


# ---------------------------------------------------------------------------
# Path resolvers
# ---------------------------------------------------------------------------

def project_path(project_name: str, *, projects_root: Optional[Path] = None) -> Path:
    """Return the root directory for a project."""
    root = projects_root or _projects_dir()
    return root / project_name


def asset_path(
    project_name: str, asset_name: str, *, projects_root: Optional[Path] = None,
) -> Path:
    """Return the directory for an asset within a project."""
    return project_path(project_name, projects_root=projects_root) / "asset" / asset_name


def shot_path(
    project_name: str, shot_name: str, *, projects_root: Optional[Path] = None,
) -> Path:
    """Return the directory for a shot within a project."""
    return project_path(project_name, projects_root=projects_root) / "shot" / shot_name


def render_path(
    project_name: str, shot_name: str, *, projects_root: Optional[Path] = None,
) -> Path:
    """Return the render directory for a shot within a project."""
    return project_path(project_name, projects_root=projects_root) / "render" / shot_name


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

def _list_subdirs(parent: Path) -> List[str]:
    """Return sorted names of immediate subdirectories under *parent*."""
    if not parent.is_dir():
        return []
    return sorted(d.name for d in parent.iterdir() if d.is_dir())


def list_projects(*, projects_root: Optional[Path] = None) -> List[str]:
    """Return sorted project names under the projects directory."""
    return _list_subdirs(projects_root or _projects_dir())


def list_assets(project_name: str, *, projects_root: Optional[Path] = None) -> List[str]:
    """Return sorted asset names within a project."""
    return _list_subdirs(
        project_path(project_name, projects_root=projects_root) / "asset",
    )


def list_shots(project_name: str, *, projects_root: Optional[Path] = None) -> List[str]:
    """Return sorted shot names within a project."""
    return _list_subdirs(
        project_path(project_name, projects_root=projects_root) / "shot",
    )


# ---------------------------------------------------------------------------
# Open in file browser
# ---------------------------------------------------------------------------

def open_project(project_name: str, *, projects_root: Optional[Path] = None) -> None:
    """Open a project's root folder in the OS file browser."""
    open_folder(project_path(project_name, projects_root=projects_root))


def open_asset(
    project_name: str, asset_name: str, *, projects_root: Optional[Path] = None,
) -> None:
    """Open an asset folder in the OS file browser."""
    open_folder(asset_path(project_name, asset_name, projects_root=projects_root))


def open_shot(
    project_name: str, shot_name: str, *, projects_root: Optional[Path] = None,
) -> None:
    """Open a shot folder in the OS file browser."""
    open_folder(shot_path(project_name, shot_name, projects_root=projects_root))


def open_render(
    project_name: str, shot_name: str, *, projects_root: Optional[Path] = None,
) -> None:
    """Open a render folder in the OS file browser."""
    open_folder(render_path(project_name, shot_name, projects_root=projects_root))
