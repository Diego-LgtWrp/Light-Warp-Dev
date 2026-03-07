#!/usr/bin/env python3
"""
CLI to create 3D animation pipeline folder structures.

project_root arguments accept either a full path or a bare project name
(resolved against PROJECTS_DIR from config).

Examples:
  python -m utils.dev.proj_folders.cli project MyFilm
  python -m utils.dev.proj_folders.cli asset MyFilm char_hero --blend
  python -m utils.dev.proj_folders.cli shot MyFilm sh010
  python -m utils.dev.proj_folders.cli project-update MyFilm --dry-run
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Callable, List

from utils.dev.proj_folders.core import (
    create_asset_structure,
    create_project,
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


def _resolve_project(arg: str) -> Path:
    """Accept a full path or a bare project name (resolved via PROJECTS_DIR)."""
    p = Path(arg)
    if p.is_absolute() or "/" in arg or "\\" in arg:
        return p.resolve()
    return get_default_projects_root() / arg


def _require_dir(path: Path, label: str = "path") -> bool:
    if not path.is_dir():
        print(f"Error: {label} is not a directory: {path}", file=sys.stderr)
        return False
    return True


def _print_preview(title: str, folders: List[Path], action: str = "created") -> None:
    if not folders:
        print(f"Nothing to do \u2014 {title} is already up to date.")
    else:
        print(f"{title} dry-run \u2014 folders that would be {action}:")
        for p in folders:
            print(f"  {p}")


def _run_or_preview(
    dry_run: bool, preview_fn: Callable[[], List[Path]], op_fn: Callable[[], Any],
    success_fmt: str, title: str, action: str = "created",
) -> int:
    try:
        if dry_run:
            _print_preview(title, preview_fn(), action=action)
            return 0
        print(success_fmt.format(op_fn()))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_project(args: argparse.Namespace) -> int:
    root = get_default_projects_root() if args.root is None else Path(args.root).resolve()
    name = (args.name or "").strip()
    if not name:
        print("Error: project name is required.", file=sys.stderr)
        return 1
    assets = [a.strip() for a in (args.assets or []) if a.strip()]
    shots = [s.strip() for s in (args.shots or []) if s.strip()]
    return _run_or_preview(
        args.dry_run,
        lambda: preview_project_structure(root, name),
        lambda: create_project(root, name, assets=assets or None, shots=shots or None),
        "Created project: {}", "project",
    )


def cmd_asset(args: argparse.Namespace) -> int:
    pr = _resolve_project(args.project_root)
    name = (args.name or "").strip()
    if not name:
        print("Error: asset name is required.", file=sys.stderr)
        return 1
    if not _require_dir(pr, "project root"):
        return 1
    return _run_or_preview(
        args.dry_run,
        lambda: preview_asset_structure(pr, name),
        lambda: create_asset_structure(pr, name, create_blend_file=args.blend, create_substance_file=args.substance),
        "Created asset: {}", "asset",
    )


def cmd_shot(args: argparse.Namespace) -> int:
    pr = _resolve_project(args.project_root)
    name = (args.name or "").strip()
    if not name:
        print("Error: shot name is required.", file=sys.stderr)
        return 1
    if not _require_dir(pr, "project root"):
        return 1
    try:
        if args.dry_run:
            ms, mr = preview_shot_structure(pr, name)
            _print_preview("shot", ms)
            _print_preview("render", mr)
            return 0
        sp, rp = create_shot_structure(pr, name)
        print(f"Created shot: {sp}\nCreated render: {rp}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_update_project(args: argparse.Namespace) -> int:
    pr = _resolve_project(args.project_root)
    if not _require_dir(pr, "project root"):
        return 1
    return _run_or_preview(
        args.dry_run,
        lambda: preview_update_project_structure(pr),
        lambda: update_project_structure(pr),
        "Updated project structure: {}", "project update", action="added",
    )


def cmd_update_asset(args: argparse.Namespace) -> int:
    pr = _resolve_project(args.project_root)
    name = (args.name or "").strip()
    if not name:
        print("Error: asset name is required.", file=sys.stderr)
        return 1
    if not _require_dir(pr, "project root"):
        return 1
    return _run_or_preview(
        args.dry_run,
        lambda: preview_update_asset_structure(pr, name),
        lambda: update_asset_structure(pr, name),
        "Updated asset structure: {}", "asset update", action="added",
    )


def cmd_update_shot(args: argparse.Namespace) -> int:
    pr = _resolve_project(args.project_root)
    name = (args.name or "").strip()
    if not name:
        print("Error: shot name is required.", file=sys.stderr)
        return 1
    if not _require_dir(pr, "project root"):
        return 1
    try:
        if args.dry_run:
            ms, mr = preview_update_shot_structure(pr, name)
            _print_preview("shot update", ms, action="added")
            _print_preview("render update", mr, action="added")
            return 0
        sp, rp = update_shot_structure(pr, name)
        print(f"Updated shot structure: {sp}\nUpdated render structure: {rp}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Argparse
# ---------------------------------------------------------------------------

PROJECT_ROOT_HELP = "Project name (e.g. MyFilm) or full path. Bare names resolve against PROJECTS_DIR."


def _add_dry_run(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without making them.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create 3D animation pipeline folder structures (project, asset, shot)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("project", help="Create a new project folder structure")
    p.add_argument("name", help="Project name (e.g. MyFilm)")
    p.add_argument("--root", default=None, help="Root folder for projects (default: PROJECTS_DIR from config)")
    p.add_argument("--assets", nargs="*", help="Optional initial asset names to create")
    p.add_argument("--shots", nargs="*", help="Optional initial shot names to create")
    _add_dry_run(p)
    p.set_defaults(func=cmd_project)

    p = sub.add_parser("asset", help="Create an asset folder structure inside a project")
    p.add_argument("project_root", help=PROJECT_ROOT_HELP)
    p.add_argument("name", help="Asset name (e.g. char_hero)")
    p.add_argument("--blend", action="store_true", help="Copy Blender template as [name].blend")
    p.add_argument("--substance", action="store_true", help="Copy Substance Painter template as [name].spp")
    _add_dry_run(p)
    p.set_defaults(func=cmd_asset)

    p = sub.add_parser("shot", help="Create a shot folder structure inside a project")
    p.add_argument("project_root", help=PROJECT_ROOT_HELP)
    p.add_argument("name", help="Shot name (e.g. sh010)")
    _add_dry_run(p)
    p.set_defaults(func=cmd_shot)

    p = sub.add_parser("project-update", help="Update existing project (add missing folders)")
    p.add_argument("project_root", help=PROJECT_ROOT_HELP)
    _add_dry_run(p)
    p.set_defaults(func=cmd_update_project)

    p = sub.add_parser("asset-update", help="Update existing asset (add missing folders)")
    p.add_argument("project_root", help=PROJECT_ROOT_HELP)
    p.add_argument("name", help="Asset name (e.g. char_hero)")
    _add_dry_run(p)
    p.set_defaults(func=cmd_update_asset)

    p = sub.add_parser("shot-update", help="Update existing shot/render (add missing folders)")
    p.add_argument("project_root", help=PROJECT_ROOT_HELP)
    p.add_argument("name", help="Shot name (e.g. sh010)")
    _add_dry_run(p)
    p.set_defaults(func=cmd_update_shot)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
