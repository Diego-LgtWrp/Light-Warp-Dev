# LightWarp Pipeline

Shared Python tools, DCC integrations, and utilities for the LightWarp animation pipeline.

## Drive Layout

This repository (`pipeline/`) lives on the LightWarp shared drive alongside production data:

```
LightWarp_Test/                 (Google Drive shared root)
  projects/                     Production data (project folders created by pipeline tools)
  pipeline/                     <-- THIS REPO (version-controlled via GitHub)
  lib/                          Shared assets library (currently a marker directory)
  utils/                        Standalone dev utilities (not part of this repo)
    dev/
      projTools/                Pipeline folder tools (standalone version)
      SecureTransfer/           File transfer utility
```

Pipeline code is tracked in Git and hosted on GitHub.  Production data and large binaries stay on the shared drive and are never committed.

## Repository Structure

```
pipeline/
  lightwarp/              Core studio library  (import lightwarp as lw)
    env.py                  Auto-detected drive paths
    folders.py              Generic folder-spec engine
    setup.py                Project/asset/shot creation and updates
    navigate.py             Path resolution, listing, and open-in-browser
    naming.py               File versioning engine (v001, v002, ...)
    util.py                 Cross-platform helpers (logging, open_folder)
    config/                 Pipeline-wide settings
      structures.py           Folder structures + asset types
      templates.py            Template path mappings per DCC
      naming.py               Versioning format settings
      local.py                Per-machine overrides (gitignored)
  utils/
    dev/                    End-user tools — dev source (GUI + CLI)
      proj_folders/           Project/asset/shot folder creator
      secure_transfer/        File copy & SHA-256 validation (requires customtkinter)
    tools/                  Published tools (populated by publish.py)
    launchers/              .bat/.ps1 scripts for artists to double-click
  software/
    dev/
      plugins/              DCC integrations — dev source (stubs for now)
        blender/              Blender operators, menus, startup hooks
        houdini/              Shelf tools, HDAs, Python panels
        nuke/                 Gizmos, Python panels, render management
        substance/            Substance Painter plugins and export presets
        adobe/                After Effects, Photoshop, and Adobe bridges
        unreal/               Unreal Editor utilities and Python bindings
      templates/            software template files for asset creation reference
    plugins/                Published plugins (populated by publish.py)
    templates/              Published templates (populated by publish.py)
  tests/                  Unit and integration tests
  setup.py                Developer install (pip install -e .)
  setup_local.py          Auto-generates lightwarp/config/local.py for local clones
  deploy.py               Deploys the repo to the Google Drive (scoped: dev or full)
  publish.py              Promotes dev → production (dev/ → tools/, plugins/, templates/)
```

## Quick Start

### For Artists

Double-click one of the launcher scripts in `utils/launchers/`:

- **proj_folders_gui.bat** -- Opens the Project Folder Creator GUI
- **proj_folders_cli.bat** -- CLI version (pass arguments after the script name)
- **secure_transfer.bat** -- Opens the Secure Transfer GUI (requires `pip install customtkinter`)

### For Developers

Developers work from a **local clone** on their own machine (not directly on Google Drive).  See [CONTRIBUTING.md](CONTRIBUTING.md) for the full setup and Git workflow.

Quick version:

1. Clone the repo from GitHub to a local directory (e.g. `C:\dev\lightwarp-pipeline\`).

2. Point your clone at the shared drive so tools can find projects and templates:
   ```
   python setup_local.py
   ```

3. (Optional) Create a virtual environment and install in editable mode:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   ```

4. Run tools:
   ```
   python -m utils.dev.proj_folders.gui
   python -m utils.dev.proj_folders.cli project MyFilm
   ```

5. Run the tests:
   ```
   python -m pytest tests/
   ```

6. When your changes are ready, deploy to the shared drive:
   ```
   python deploy.py                # interactive (defaults to dev scope)
   python deploy.py --scope dev    # deploy only dev directories
   python deploy.py --scope full   # deploy all tracked files (core pipeline)
   ```

## CLI Usage

The Project Folder Creator CLI supports bare project names (resolved against PROJECTS_DIR) or full paths:

```
python -m utils.dev.proj_folders.cli project MyFilm
python -m utils.dev.proj_folders.cli project MyFilm --assets char_hero prop_sword --shots sh010 sh020
python -m utils.dev.proj_folders.cli asset MyFilm char_hero --blend --substance
python -m utils.dev.proj_folders.cli shot MyFilm sh010
python -m utils.dev.proj_folders.cli project-update MyFilm --dry-run
python -m utils.dev.proj_folders.cli asset-update MyFilm char_hero
python -m utils.dev.proj_folders.cli shot-update MyFilm sh010
```

## Configuration

Pipeline-wide settings live in `lightwarp/config/`:

| File               | Contents                                                       |
|--------------------|----------------------------------------------------------------|
| `structures.py`    | Folder structures (PROJECT, ASSET, SHOT, RENDER) + asset types |
| `templates.py`     | Template path mappings (subfolder + extension per DCC)         |
| `naming.py`        | Versioning format (prefix, separator, padding)                 |

### Per-Machine Overrides

Create `lightwarp/config/local.py` (gitignored) to set machine-specific values.  The easiest way is to run `python setup_local.py`, which auto-detects your Google Drive and writes the file for you.

You can also copy `lightwarp/config/local.py.example` and edit it manually.

**DRIVE_ROOT** -- If you are working from a local clone (not directly on the shared drive), set `DRIVE_ROOT` in `lightwarp/config/local.py` to point at the Google Drive root.  All derived paths (`PROJECTS_DIR`, `LIB_DIR`, etc.) will be re-computed automatically:

```python
from pathlib import Path
DRIVE_ROOT = Path("G:/Shared drives/LightWarp_Test")
```

Individual path overrides (`PROJECTS_DIR`, `TEMPLATES_DIR`, etc.) still take precedence if set.

## The `lightwarp` Module

`lightwarp` is the unified studio library.  A single import gives you environment paths, project setup, navigation, and versioning:

```python
import lightwarp as lw

# Environment paths (respects lightwarp/config/local.py overrides)
lw.DRIVE_ROOT
lw.PROJECTS_DIR
lw.LIB_DIR
lw.TEMPLATES_DIR

# Create project structures
lw.create_project_structure(root, "MyFilm")
lw.create_asset_structure(project, "char_hero", create_blend_file=True)
lw.create_shot_structure(project, "sh010")

# Navigate the pipeline
lw.project_path("MyFilm")          # -> Path to project root
lw.asset_path("MyFilm", "char_hero")
lw.shot_path("MyFilm", "sh010")
lw.render_path("MyFilm", "sh010")

# List contents
lw.list_projects()                  # -> ["MyFilm", "OtherProject"]
lw.list_assets("MyFilm")           # -> ["char_hero", "prop_sword"]
lw.list_shots("MyFilm")            # -> ["sh010", "sh020"]

# Open in file browser
lw.open_project("MyFilm")
lw.open_shot("MyFilm", "sh010")
lw.open_render("MyFilm", "sh010")

# File versioning
lw.format_version("char_hero", 3, ".blend")   # -> "char_hero_v003.blend"
lw.next_version_path(folder, "char_hero", ".blend")
lw.save_next_version(source_file, folder, "char_hero")
lw.list_versions(folder, "char_hero", ".blend")
lw.latest_version_path(folder, "char_hero", ".blend")

# Utilities
lw.open_folder(some_path)
lw.log_to_project(root, "tool", "message")
```

All path functions resolve correctly regardless of drive letter, whether you are working on the shared Google Drive or from a local clone with a `lightwarp/config/local.py` override.

## Deploying to the Shared Drive

`deploy.py` syncs your local clone to the Google Drive `pipeline/` directory.  It is a one-way push (repo to Drive), never the reverse.

### Deployment Scopes

Deploy supports two scopes to control what gets pushed:

| Scope  | What it deploys                                | Who it's for       |
|--------|------------------------------------------------|--------------------|
| `dev`  | `utils/dev/`, `software/dev/`, `tests/` only   | Any developer      |
| `full` | All git-tracked files (core pipeline included)  | Leads / admins     |

If no `--scope` flag is passed, the script prompts you to choose.  The default is `dev`.  Choosing `full` triggers an extra confirmation warning since it modifies core pipeline files shared by all users.

Certain directories on the Drive are **never** touched by deploy regardless of scope — these are managed by `publish.py` instead:

- `utils/tools/` (published from `utils/dev/`)
- `software/plugins/` (published from `software/dev/plugins/`)
- `software/templates/` (published from `software/dev/templates/`)

```
python deploy.py                                     # interactive scope selection
python deploy.py --scope dev                         # dev directories only
python deploy.py --scope full                        # all tracked files
python deploy.py --dry-run                           # preview changes
python deploy.py --dry-run --scope dev               # preview dev-only changes
python deploy.py "G:/Shared drives/LightWarp_Test"   # explicit Drive path
```

The script also:
- Pulls the latest from GitHub if you're behind
- Copies only git-tracked files (no `.git/`, no `__pycache__/`)
- Removes stale files from the Drive that are no longer tracked (within scope)
- Preserves runtime artifacts (`__pycache__/`, `lightwarp/config/local.py`, etc.)
- Shows a full summary and asks for confirmation before making changes

### Publishing Dev to Production

After deploying dev tools to the Drive, use `publish.py` to promote them to their production locations:

| Area        | Source (dev)               | Destination (production)    |
|-------------|----------------------------|-----------------------------|
| utils       | `pipeline/utils/dev`       | `pipeline/utils/tools`      |
| plugins     | `pipeline/software/dev/plugins`   | `pipeline/software/plugins`  |
| templates   | `pipeline/software/dev/templates` | `pipeline/software/templates`|

```
python publish.py                  # publish all areas
python publish.py utils            # publish only utils
python publish.py plugins          # publish only plugins
python publish.py --dry-run        # preview changes
```

`publish.py` runs on the Drive (not from your local clone).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete workflow.

## Adding a New Tool

1. Create a directory under `utils/dev/` (e.g. `utils/dev/my_tool/`).
2. Add `__init__.py`, `core.py`, and optionally `gui.py` / `cli.py`.
3. Import shared utilities from `lightwarp` and settings from `lightwarp.config`.
4. Add a launcher script in `utils/launchers/`.
5. Deploy with `python deploy.py --scope dev`, then promote to production with `python publish.py utils`.

## Adding a DCC Integration

1. Find the appropriate package under `software/dev/plugins/` (or create one).
2. Read the README inside each plugin package for setup guidance.
3. Import from `lightwarp` and `lightwarp.config` as needed.
4. Deploy with `python deploy.py --scope dev`, then promote with `python publish.py plugins`.
