# Contributing to the LightWarp Pipeline

This guide covers everything you need to start developing on the pipeline.

## Prerequisites

- **Git** -- Install [Git for Windows](https://git-scm.com/) (includes Git Bash)
- **Python 3.8+** -- Any recent Python version
- **GitHub account** -- Sign up at [github.com](https://github.com) (free)
- **Google Drive for Desktop** -- So your machine can access the shared drive

## Initial Setup (One-Time)

### 1. Clone the repository

Clone to a local directory on your own machine -- **not** on Google Drive:

```bash
cd /c/dev
git clone https://github.com/YOUR_ORG/lightwarp-pipeline.git
cd lightwarp-pipeline
```

Replace the URL with the actual repository URL.  You can put the clone
anywhere you like (`C:\dev`, `C:\Users\you\projects`, etc.).

### 2. Point your clone at the shared drive

Because your code lives locally but project data lives on Google Drive,
you need to tell the pipeline where the drive is:

```bash
python setup_local.py
```

This auto-detects the LightWarp shared drive and creates
`lightwarp/config/local.py` with the correct `DRIVE_ROOT`.  If
auto-detection fails, you can provide the path directly:

```bash
python setup_local.py "G:/Shared drives/LightWarp_Test"
```

### 3. Install in editable mode (optional but recommended)

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS / Linux
pip install -e .
```

### 4. Verify everything works

```bash
python -m utils.dev.proj_folders.gui
python -m pytest tests/
```

## Day-to-Day Workflow

### Getting the latest code

Before starting any work, make sure you have the latest changes:

```bash
git checkout main
git pull
```

### Making changes

1. **Create a branch** for your work:

   ```bash
   git checkout -b feature/my-change
   ```

   Use a descriptive name like `feature/add-nuke-tools`, `fix/folder-naming`,
   or `update/asset-types`.

2. **Make your changes** in your editor.

3. **Test** that everything still works:

   ```bash
   python -m pytest tests/
   ```

4. **Stage and commit** your changes:

   ```bash
   git add .
   git commit -m "Brief description of what you changed and why"
   ```

   You can make multiple commits on a branch.  Each commit should be a
   logical chunk of work.

5. **Push your branch** to GitHub:

   ```bash
   git push -u origin feature/my-change
   ```

### Opening a Pull Request

After pushing your branch, open a Pull Request (PR) on GitHub:

1. Go to the repository page on GitHub.
2. You should see a banner offering to create a PR for your branch -- click it.
3. Add a title and brief description of your changes.
4. Submit the PR.

Other team members can review the changes and leave comments.  Once
approved, merge the PR into `main` using the GitHub web interface.

### After merging

Switch back to `main` and pull the merged changes:

```bash
git checkout main
git pull
```

You can delete your local branch if you're done with it:

```bash
git branch -d feature/my-change
```

## Deploying to the Shared Drive

When changes on `main` are ready for artists, deploy them to the Google
Drive `pipeline/` directory:

```bash
git checkout main
git pull
python deploy.py
```

The deploy script will:

1. Check that your local `main` is up to date with GitHub.
2. Offer to pull if you're behind.
3. Ask you to select a deployment scope (`dev` or `full`).
4. Show a summary of files to add, update, and remove.
5. Ask for confirmation before making any changes.

### Deployment scopes

| Scope  | What it deploys                                | Who it's for       |
|--------|------------------------------------------------|--------------------|
| `dev`  | `utils/dev/`, `software/dev/`, `tests/` only   | Any developer      |
| `full` | All git-tracked files (core pipeline included)  | Leads / admins     |

Most developers should use `dev` scope (the default).  The `full` scope
modifies core pipeline code (`lightwarp/`, launchers, top-level scripts)
and requires an extra confirmation.

```bash
python deploy.py --scope dev       # deploy dev directories only
python deploy.py --scope full      # deploy everything (extra confirmation)
python deploy.py --dry-run         # preview without applying
```

### Publishing dev to production

After deploying dev content, promote it to its production location on the
Drive using `publish.py`:

```bash
python publish.py                  # publish all areas (utils, plugins, templates)
python publish.py utils            # publish utils only
python publish.py --dry-run        # preview
```

This copies `utils/dev/` to `utils/tools/`, `software/dev/plugins/` to
`software/plugins/`, and `software/dev/templates/` to `software/templates/`.

**Important notes:**

- Only deploy from the `main` branch to keep the Drive copy stable.
- Anyone on the team can run a `dev` deploy -- it's safe and scoped.
- The script never touches `__pycache__/`, `lightwarp/config/local.py`, or
  other runtime artifacts on the Drive.
- Directories managed by `publish.py` (`utils/tools/`, `software/plugins/`,
  `software/templates/`) are never modified by `deploy.py`.
- The Drive copy has no `.git` directory.  Git operations only happen in
  your local clone.

## Using the `lightwarp` Module

The `lightwarp` package is the unified studio library.  Everything you
need is available through a single import:

```python
import lightwarp as lw
```

### Environment paths

```python
lw.DRIVE_ROOT       # root of the shared drive
lw.PROJECTS_DIR     # projects/ directory
lw.LIB_DIR          # lib/ directory
lw.TEMPLATES_DIR    # software/templates/
```

These respect `lightwarp/config/local.py` overrides, so they resolve
correctly on any machine regardless of drive letter.

### Project setup

```python
lw.create_project_structure(root, "MyFilm")
lw.create_asset_structure(project, "char_hero")
lw.create_shot_structure(project, "sh010")
```

### Navigation

```python
lw.project_path("MyFilm")
lw.list_projects()
lw.list_assets("MyFilm")
lw.list_shots("MyFilm")
lw.open_shot("MyFilm", "sh010")
```

### Where the code lives

| What | Module |
|------|--------|
| Path auto-detection | `lightwarp.env` |
| Folder-spec engine | `lightwarp.folders` |
| Project setup functions | `lightwarp.setup` |
| Navigation and listing | `lightwarp.navigate` |
| File versioning | `lightwarp.naming` |
| Utilities (logging, open) | `lightwarp.util` |
| Settings and overrides | `lightwarp.config` |

You can import from a specific submodule (e.g. `from lightwarp.navigate
import list_shots`), but `import lightwarp as lw` re-exports everything
for convenience.

## Quick Reference

| Task | Command |
|------|---------|
| Get latest | `git pull` |
| Create a branch | `git checkout -b feature/my-change` |
| See what changed | `git status` |
| Stage all changes | `git add .` |
| Commit | `git commit -m "description"` |
| Push a branch | `git push -u origin feature/my-change` |
| Switch to main | `git checkout main` |
| Run tests | `python -m pytest tests/` |
| Deploy (dev scope) | `python deploy.py --scope dev` |
| Deploy (full scope) | `python deploy.py --scope full` |
| Deploy dry run | `python deploy.py --dry-run` |
| Publish dev to production | `python publish.py` |
| Publish dry run | `python publish.py --dry-run` |
| Re-generate local config | `python setup_local.py` |
