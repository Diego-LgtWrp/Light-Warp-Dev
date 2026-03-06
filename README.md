# LightWarp Pipeline

Shared Python tools, DCC integrations, and utilities for the LightWarp animation pipeline.

## Drive Layout

This repository (`pipeline/`) lives on the LightWarp shared drive alongside production data and resources:

```
LightWarp_Test/
  projects/           Production data (project folders created by this tool)
  resources/          Shared non-code assets (templates, HDRIs, LUTs)
    templates/        .blend, .spp template files for asset creation
  software/           DCC installs, portable apps, plugin builds
  pipeline/           <-- THIS REPO (everything below is version-controlled)
```

Pipeline code is tracked in Git; production data and large binaries stay on the shared drive.

## Repository Structure

```
pipeline/
  lightwarp/          Shared Python package (env, folders engine, utilities + logging)
  config/             Pipeline-wide settings (folder structures, templates, asset types)
  tools/              End-user tools
    proj_folders/       Project/asset/shot folder creator (GUI + CLI)
    secure_transfer/    File copy & SHA-256 validation (GUI, requires customtkinter)
  hosts/              DCC-specific integrations (stubs for now)
    blender/            Blender operators, menus, startup hooks
    unreal/             Unreal Editor utilities and Python bindings
    houdini/            Shelf tools, HDAs, Python panels
    substance/          Substance Painter plugins and export presets
    nuke/               Gizmos, Python panels, render management
    adobe/              After Effects, Photoshop, and other Adobe bridges
  tests/              Unit and integration tests
  launchers/          .bat/.ps1 scripts for artists to double-click
  setup.py            Developer install (pip install -e .)
```

## Quick Start

### For Artists

Double-click one of the launcher scripts in `launchers/`:

- **proj_folders_gui.bat** — Opens the Project Folder Creator GUI
- **proj_folders_cli.bat** — CLI version (pass arguments after the script name)
- **secure_transfer.bat** — Opens the Secure Transfer GUI (requires `pip install customtkinter`)

### For Developers

1. Open a terminal in the `pipeline/` directory.

2. (Optional) Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install the package in editable mode:
   ```
   pip install -e .
   ```

4. Now you can run tools directly:
   ```
   python -m tools.proj_folders.gui
   python -m tools.proj_folders.cli project MyFilm
   python -m tools.proj_folders.cli asset MyFilm char_hero --blend
   python -m tools.proj_folders.cli shot MyFilm sh010 --dry-run
   ```

5. Run the tests:
   ```
   python -m pytest tests/
   ```
   or without pytest:
   ```
   python -m unittest discover tests/
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

Copy `config/local.py.example` to `config/local.py` and uncomment/edit the values you want to change. `local.py` is gitignored so each artist can have their own settings.

## Environment

`lightwarp/env.py` auto-detects the drive layout based on its own file path:

```python
from lightwarp.env import DRIVE_ROOT, PROJECTS_DIR, RESOURCES_DIR, TEMPLATES_DIR
```

These paths are the computed defaults. The `config/` package re-exports them and applies any overrides from `config/local.py`.

## Adding a New Tool

1. Create a directory under `tools/` (e.g. `tools/my_tool/`).
2. Add `__init__.py`, `core.py`, and optionally `gui.py` / `cli.py`.
3. Import shared utilities from `lightwarp` and settings from `config`.
4. Add a launcher script in `launchers/`.

## Adding a DCC Integration

1. Find the appropriate package under `hosts/` (or create one).
2. Read the README inside each host package for setup guidance.
3. Import from `lightwarp` and `config` as needed.
