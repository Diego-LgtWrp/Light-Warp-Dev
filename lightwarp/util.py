"""Cross-platform utility helpers shared by all pipeline tools."""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def open_folder(path: Path) -> None:
    """Open a folder in the platform's file browser. Raises OSError on failure."""
    p = path.resolve()
    if sys.platform.startswith("win"):
        os.startfile(str(p))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(p)], check=False)
    else:
        subprocess.run(["xdg-open", str(p)], check=False)


def log_to_project(project_root: Path, tool_name: str, message: str) -> None:
    """Append a timestamped line to project_root/utils/logs/<tool_name>.log.

    Never raises — logging must not break the calling operation.
    """
    try:
        logs_dir = project_root / "utils" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / f"{tool_name}.log"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {message}\n")
    except Exception:
        pass
