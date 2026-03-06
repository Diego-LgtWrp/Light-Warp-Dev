# LightWarp Pipeline

Shared Python tools, DCC integrations, and utilities for the LightWarp animation pipeline.

## Drive Layout

This repository (`pipeline/`) lives on the LightWarp shared drive alongside production data and resources:

```
LightWarp_Test/                 (Google Drive shared root)
  projects/                     Production data (project folders created by this tool)
  resources/                    Shared non-code assets (templates, HDRIs, LUTs)
    templates/                  .blend, .spp template files for asset creation
  software/                     DCC installs, portable apps, plugin builds
  pipeline/                     <-- THIS REPO (version-controlled via GitHub)
```

Pipeline code is tracked in Git and hosted on GitHub.  Production data and large binaries stay on the shared drive and are never committed.

## Repository Structure

```
pipeline/
  lightwarp/            Shared Python package (env, folders engine, utilities + logging)
  config/               Pipeline-wide settings (folder structures, templates, asset types)
  tools/                End-user tools
    proj_folders/         Project/asset/shot folder creator (GUI + CLI)
    secure_transfer/      File copy & SHA-256 validation (GUI, requires customtkinter)
  hosts/                DCC-specific integrations (stubs for now)
    blender/              Blender operators, menus, startup hooks
    unreal/               Unreal Editor utilities and Python bindings
    houdini/              Shelf tools, HDAs, Python panels
    substance/            Substance Painter plugins and export presets
    nuke/                 Gizmos, Python panels, render management
    adobe/                After Effects, Photoshop, and other Adobe bridges
  tests/                Unit and integration tests
  launchers/            .bat/.ps1 scripts for artists to double-click
  setup.py              Developer install (pip install -e .)
  setup_local.py        Auto-generates config/local.py for local clones
  deploy.py             Deploys the repo to the Google Drive pipeline/ directory
```

## Quick Start

### For Artists

Double-click one of the launcher scripts in `launchers/`:

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
   python -m tools.proj_folders.gui
   python -m tools.proj_folders.cli project MyFilm
   ```

5. Run the tests:
   ```
   python -m pytest tests/
   ```

6. When your changes are ready, deploy to the shared drive:
   ```
   python deploy.py
   ```

## CLI Usage

The Project Folder Creator CLI supports bare project names (resolved against PROJECTS_DIR) or full paths:

```
python -m tools.proj_folders.cli project MyFilm
python -m tools.proj_folders.cli project MyFilm --assets char_hero prop_sword --shots sh010 sh020
python -m tools.proj_folders.cli asset MyFilm char_hero --blend --substance
python -m tools.proj_folders.cli shot MyFilm sh010
python -m tools.proj_folders.cli project-update MyFilm --dry-run
python -m tools.proj_folders.cli asset-update MyFilm char_hero
python -m tools.proj_folders.cli shot-update MyFilm sh010
```

## Configuration

Pipeline-wide settings live in `config/`:

| File               | Contents                                                       |
|--------------------|----------------------------------------------------------------|
| `structures.py`    | Folder structures (PROJECT, ASSET, SHOT, RENDER) + asset types |
| `templates.py`     | Template path mappings (subfolder + extension per DCC)         |

### Per-Machine Overrides

Create `config/local.py` (gitignored) to set machine-specific values.  The easiest way is to run `python setup_local.py`, which auto-detects your Google Drive and writes the file for you.

You can also copy `config/local.py.example` and edit it manually.

**DRIVE_ROOT** -- If you are working from a local clone (not directly on the shared drive), set `DRIVE_ROOT` in `config/local.py` to point at the Google Drive root.  All derived paths (`PROJECTS_DIR`, `RESOURCES_DIR`, etc.) will be re-computed automatically:

```python
from pathlib import Path
DRIVE_ROOT = Path("G:/Shared drives/LightWarp_Test")
```

Individual path overrides (`PROJECTS_DIR`, `TEMPLATES_DIR`, etc.) still take precedence if set.

## Environment

`lightwarp/env.py` auto-detects the drive layout based on its own file path:

```python
from config import DRIVE_ROOT, PROJECTS_DIR, RESOURCES_DIR, TEMPLATES_DIR
```

Always import paths from `config` (not `lightwarp.env` directly) to get values that respect `config/local.py` overrides.

## Deploying to the Shared Drive

`deploy.py` syncs your local clone to the Google Drive `pipeline/` directory.  It is a one-way push (repo to Drive), never the reverse.

```
python deploy.py              # auto-detect Drive location
python deploy.py --dry-run    # preview changes without applying
python deploy.py "G:/Shared drives/LightWarp_Test"   # explicit path
```

The script:
- Pulls the latest from GitHub if you're behind
- Copies only git-tracked files (no `.git/`, no `__pycache__/`)
- Removes stale files from the Drive that are no longer in the repo
- Preserves runtime artifacts (`__pycache__/`, `config/local.py`, etc.)
- Shows a full summary and asks for confirmation before making changes

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete workflow.

## Adding a New Tool

1. Create a directory under `tools/` (e.g. `tools/my_tool/`).
2. Add `__init__.py`, `core.py`, and optionally `gui.py` / `cli.py`.
3. Import shared utilities from `lightwarp` and settings from `config`.
4. Add a launcher script in `launchers/`.

## Adding a DCC Integration

1. Find the appropriate package under `hosts/` (or create one).
2. Read the README inside each host package for setup guidance.
3. Import from `lightwarp` and `config` as needed.
