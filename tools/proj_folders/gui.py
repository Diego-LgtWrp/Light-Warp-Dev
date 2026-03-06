#!/usr/bin/env python3
"""
GUI to create and update pipeline folder structures (project, asset, shot).
Uses tkinter (built-in). Run via launcher or: python -m tools.proj_folders.gui
"""

import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List, Optional

from config import ASSET_TYPES
from lightwarp.util import open_folder
from tools.proj_folders.core import (
    create_asset_structure,
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


class PipelineFoldersGui:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Pipeline Folder Creator")
        self.root.geometry("820x560")
        self.root.minsize(640, 480)
        self.root.resizable(True, True)

        self.background = "#1e1e1e"
        self.panel_bg = "#252526"
        self.text_fg = "#f0f0f0"
        self.subtle_fg = "#c0c0c0"
        self.pad = dict(padx=10, pady=6)

        self._configure_style()
        self._build_scrollable_layout()
        self._build_header()
        self._build_project_section()
        self._build_asset_section()
        self._build_shot_section()
        self._build_event_log_section()

        self.refresh_project_lists()
        self.root.update_idletasks()
        self._on_frame_configure()
        self.canvas.yview_moveto(0)

    # ---- Style / layout ---------------------------------------------------

    def _configure_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        self.root.configure(bg=self.background)
        style.configure("Main.TFrame", background=self.background)
        style.configure("TLabel", background=self.background, foreground=self.text_fg)
        style.configure("Header.TLabel", background=self.background, foreground=self.text_fg,
                         font=("Segoe UI", 18, "bold"))
        style.configure("SubHeader.TLabel", background=self.background, foreground=self.subtle_fg,
                         font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=self.background, foreground=self.text_fg,
                         font=("", 11, "bold"))
        style.configure("TButton", padding=4)

    def _build_scrollable_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        container = ttk.Frame(self.root, style="Main.TFrame")
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(container, highlightthickness=0, bg=self.background)
        v_scroll = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")

        self.main = ttk.Frame(self.canvas, padding=15, style="Main.TFrame")
        self.frame_window = self.canvas.create_window((0, 0), window=self.main, anchor="nw")
        self.main.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_frame_configure(self, event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.frame_window, width=self.canvas.winfo_width())

    def _on_mousewheel(self, event) -> None:
        delta = -event.delta if sys.platform == "darwin" else -int(event.delta / 120)
        self.canvas.yview_scroll(delta, "units")

    # ---- Reusable widgets -------------------------------------------------

    def _section_title(self, text: str) -> None:
        ttk.Label(self.main, text=text, style="Section.TLabel").pack(anchor=tk.W, **self.pad)

    def _separator(self, top: int = 12) -> None:
        ttk.Separator(self.main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=top)

    def _labeled_entry(self, label: str, var: tk.StringVar, width: int = 45) -> ttk.Entry:
        ttk.Label(self.main, text=label).pack(anchor=tk.W, **self.pad)
        entry = ttk.Entry(self.main, textvariable=var, width=width)
        entry.pack(fill=tk.X, **self.pad)
        return entry

    def _labeled_combobox(
        self, label: str, var: tk.StringVar, values: List[str],
        width: int = 40, readonly: bool = True,
    ) -> ttk.Combobox:
        ttk.Label(self.main, text=label).pack(anchor=tk.W, **self.pad)
        combo = ttk.Combobox(self.main, textvariable=var, values=values, width=width,
                             state="readonly" if readonly else "normal")
        combo.pack(fill=tk.X, **self.pad)
        return combo

    # ---- Header / event log -----------------------------------------------

    def _build_header(self) -> None:
        header = ttk.Frame(self.main, style="Main.TFrame")
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Pipeline Folder Creator", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(header, text="Create and update project, asset, and shot folder structures on the shared pipeline drive.",
                  style="SubHeader.TLabel", wraplength=760, justify="left").pack(anchor=tk.W, pady=(2, 0))
        self._separator(top=10)

    def _build_event_log_section(self) -> None:
        self._separator(top=8)
        log_header = ttk.Frame(self.main)
        log_header.pack(fill=tk.X, **self.pad)
        ttk.Label(log_header, text="Event log", style="Section.TLabel").pack(side=tk.LEFT)
        ttk.Button(log_header, text="Clear", command=self._on_clear_log).pack(side=tk.RIGHT)

        log_frame = ttk.Frame(self.main)
        log_frame.pack(fill=tk.BOTH, expand=True, **self.pad)
        self.log_text = tk.Text(log_frame, height=6, wrap="word", state="disabled",
                                bg=self.panel_bg, fg=self.text_fg, insertbackground=self.text_fg, relief="flat")
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def append_log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{ts}] {message.rstrip()}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _on_clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    # ---- Common operation helpers -----------------------------------------

    def _show_preview(self, label: str, folders: List[Path], action: str = "created") -> None:
        if not folders:
            messagebox.showinfo("Preview", f"Nothing to do \u2014 {label.lower()} is already up to date.")
        else:
            messagebox.showinfo("Preview",
                f"{label} dry-run \u2014 folders that would be {action}:\n\n" + "\n".join(str(p) for p in folders))

    def _preview_and_log(self, tag: str, label: str,
                         fn: Callable[[], List[Path]], action: str = "created") -> None:
        """Run a single-list preview function and show result + log entry."""
        try:
            missing = fn()
            self._show_preview(label, missing, action=action)
            self.append_log(f"[preview][{tag}] {len(missing)} folder(s) would be {action}"
                            if missing else f"[preview][{tag}] already up to date")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.append_log(f"[error][{tag}] {e}")

    def _exec_and_report(self, tag: str, fn: Callable[[], str],
                         on_success: Optional[Callable[[], None]] = None) -> None:
        """Run an operation that returns a success message string, or handle errors."""
        try:
            msg = fn()
            messagebox.showinfo("Success", msg)
            self.append_log(f"[{tag}] {msg}")
            if on_success:
                on_success()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.append_log(f"[error][{tag}] {e}")

    # ---- Project list helpers ---------------------------------------------

    def _list_projects(self) -> List[str]:
        try:
            base = Path(self.root_var.get()).resolve()
        except Exception:
            return []
        if not base.is_dir():
            return []
        return sorted(p.name for p in base.iterdir() if p.is_dir())

    def refresh_project_lists(self) -> None:
        names = self._list_projects()
        self.asset_project_combo["values"] = names
        self.shot_project_combo["values"] = names

    # ---- Validation helpers -----------------------------------------------

    def _require(self, value: str, message: str) -> bool:
        if not value.strip():
            messagebox.showerror("Error", message)
            return False
        return True

    def _selected_project_root(self, project_name_var: tk.StringVar) -> Optional[Path]:
        if not self._require(self.root_var.get(), "Projects root is required."):
            return None
        project_name = project_name_var.get().strip()
        if not self._require(project_name, "Project selection is required."):
            return None
        return Path(self.root_var.get()).resolve() / project_name

    def _prefixed_asset_name(self) -> str:
        raw = self.asset_name_var.get().strip()
        prefix = self.asset_type_var.get() or ""
        if not raw:
            return ""
        return raw if raw.startswith(prefix) else prefix + raw

    # ---- Project section --------------------------------------------------

    def _build_project_section(self) -> None:
        self._section_title("Project")

        self.root_var = tk.StringVar(value=str(get_default_projects_root()))
        self.asset_project_var = tk.StringVar()
        self.project_dry_run_var = tk.BooleanVar(value=False)
        self.project_name_var = tk.StringVar()

        row = ttk.Frame(self.main)
        row.pack(fill=tk.X, **self.pad)
        ttk.Label(row, text="Projects root:", width=14, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(row, textvariable=self.root_var, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(row, text="Browse", command=self._on_browse_root).pack(side=tk.LEFT)

        ttk.Checkbutton(self.main, text="Preview only (no changes)",
                        variable=self.project_dry_run_var).pack(anchor=tk.W, **self.pad)
        self._labeled_entry("Project name:", self.project_name_var)

        ttk.Button(self.main, text="Create project", command=self._on_create_project).pack(anchor=tk.W, **self.pad)
        ttk.Button(self.main, text="Update existing project structure",
                   command=self._on_update_project).pack(anchor=tk.W, **self.pad)
        ttk.Button(self.main, text="Open projects root",
                   command=self._on_open_projects_root).pack(anchor=tk.W, **self.pad)
        self._separator()

    def _on_browse_root(self) -> None:
        d = filedialog.askdirectory(title="Select projects root", initialdir=self.root_var.get())
        if d:
            self.root_var.set(d)
            self.refresh_project_lists()

    def _on_create_project(self) -> None:
        if not self._require(self.root_var.get(), "Projects root is required."):
            return
        name = self.project_name_var.get().strip()
        if not self._require(name, "Project name is required."):
            return
        root = Path(self.root_var.get()).resolve()

        if self.project_dry_run_var.get():
            self._preview_and_log("project", "Project", lambda: preview_project_structure(root, name))
            return

        def _do() -> str:
            return f"Created project:\n{create_project_structure(root, name)}"

        def _after() -> None:
            self.refresh_project_lists()
            self.project_name_var.set("")

        self._exec_and_report("project", _do, on_success=_after)

    def _on_update_project(self) -> None:
        if not self._require(self.root_var.get(), "Projects root is required."):
            return
        name = self.project_name_var.get().strip()
        if not self._require(name, "Project name is required to update an existing project."):
            return
        pr = Path(self.root_var.get()).resolve() / name

        if self.project_dry_run_var.get():
            self._preview_and_log("project-update", "Project update",
                                  lambda: preview_update_project_structure(pr), action="added")
            return

        self._exec_and_report("project-update",
                              lambda: f"Updated project structure:\n{update_project_structure(pr)}")

    def _on_open_projects_root(self) -> None:
        if self.root_var.get().strip():
            try:
                open_folder(Path(self.root_var.get()))
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder:\n{e}")

    # ---- Asset section ----------------------------------------------------

    def _build_asset_section(self) -> None:
        self._section_title("Asset")

        self.asset_name_var = tk.StringVar()
        self.asset_type_var = tk.StringVar(value=ASSET_TYPES[0])
        self.asset_dry_run_var = tk.BooleanVar(value=False)
        self.blend_var = tk.BooleanVar(value=False)
        self.substance_var = tk.BooleanVar(value=False)

        self.asset_project_combo = self._labeled_combobox("Project:", self.asset_project_var, values=[], readonly=True)
        self._labeled_entry("Asset name:", self.asset_name_var)
        self._labeled_combobox("Asset type:", self.asset_type_var, values=ASSET_TYPES, width=10, readonly=True)

        opts = ttk.Frame(self.main)
        opts.pack(fill=tk.X, **self.pad)
        ttk.Checkbutton(opts, text="Create Blender file (from template)",
                        variable=self.blend_var).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(opts, text="Create Substance Painter file (from template)",
                        variable=self.substance_var).pack(side=tk.LEFT)

        ttk.Checkbutton(self.main, text="Preview only (no changes)",
                        variable=self.asset_dry_run_var).pack(anchor=tk.W, **self.pad)

        ttk.Button(self.main, text="Create asset", command=self._on_create_asset).pack(anchor=tk.W, **self.pad)
        ttk.Button(self.main, text="Update existing asset structure",
                   command=self._on_update_asset).pack(anchor=tk.W, **self.pad)
        ttk.Button(self.main, text="Open asset folder",
                   command=self._on_open_asset_folder).pack(anchor=tk.W, **self.pad)
        self._separator()

    def _on_create_asset(self) -> None:
        name = self._prefixed_asset_name()
        pr = self._selected_project_root(self.asset_project_var)
        if pr is None or not self._require(name, "Asset name is required."):
            return

        if self.asset_dry_run_var.get():
            self._preview_and_log("asset", "Asset", lambda: preview_asset_structure(pr, name))
            return

        self._exec_and_report("asset", lambda: f"Created asset:\n{create_asset_structure(pr, name, create_blend_file=self.blend_var.get(), create_substance_file=self.substance_var.get())}")

    def _on_update_asset(self) -> None:
        name = self._prefixed_asset_name()
        pr = self._selected_project_root(self.asset_project_var)
        if pr is None or not self._require(name, "Asset name is required to update an existing asset."):
            return

        if self.asset_dry_run_var.get():
            self._preview_and_log("asset-update", "Asset update",
                                  lambda: preview_update_asset_structure(pr, name), action="added")
            return

        self._exec_and_report("asset-update",
                              lambda: f"Updated asset structure:\n{update_asset_structure(pr, name)}")

    def _on_open_asset_folder(self) -> None:
        name = self._prefixed_asset_name()
        if not self._require(name, "Asset name is required to open the folder."):
            return
        pr = self._selected_project_root(self.asset_project_var)
        if pr is None:
            return
        path = pr / "asset" / name
        if not path.is_dir():
            messagebox.showerror("Error", f"Asset folder does not exist:\n{path}")
            return
        try:
            open_folder(path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

    # ---- Shot section -----------------------------------------------------

    def _build_shot_section(self) -> None:
        self._section_title("Shot")

        self.shot_project_var = tk.StringVar()
        self.shot_name_var = tk.StringVar()
        self.shot_dry_run_var = tk.BooleanVar(value=False)

        self.shot_project_combo = self._labeled_combobox("Project:", self.shot_project_var, values=[], readonly=True)
        self._labeled_entry("Shot name:", self.shot_name_var)

        ttk.Checkbutton(self.main, text="Preview only (no changes)",
                        variable=self.shot_dry_run_var).pack(anchor=tk.W, **self.pad)

        ttk.Button(self.main, text="Create shot", command=self._on_create_shot).pack(anchor=tk.W, **self.pad)
        ttk.Button(self.main, text="Update existing shot structure",
                   command=self._on_update_shot).pack(anchor=tk.W, **self.pad)
        ttk.Button(self.main, text="Open shot folder",
                   command=self._on_open_shot_folder).pack(anchor=tk.W, **self.pad)

    def _show_dual_preview(
        self, label_a: str, folders_a: List[Path], label_b: str, folders_b: List[Path],
        log_tag: str, action: str = "created",
    ) -> None:
        if not folders_a and not folders_b:
            messagebox.showinfo("Preview", f"Nothing to do \u2014 {label_a.lower()}/{label_b.lower()} already up to date.")
            self.append_log(f"[preview][{log_tag}] already up to date")
        else:
            text = (f"{label_a} dry-run \u2014 folders that would be {action}:\n\n"
                    + "\n".join(str(p) for p in folders_a)
                    + f"\n\n{label_b} dry-run \u2014 folders that would be {action}:\n\n"
                    + "\n".join(str(p) for p in folders_b))
            messagebox.showinfo("Preview", text)
            self.append_log(f"[preview][{log_tag}] {len(folders_a)} {label_a.lower()} + "
                            f"{len(folders_b)} {label_b.lower()} folder(s) would be {action}")

    def _on_create_shot(self) -> None:
        name = self.shot_name_var.get().strip()
        pr = self._selected_project_root(self.shot_project_var)
        if pr is None or not self._require(name, "Shot name is required."):
            return

        if self.shot_dry_run_var.get():
            try:
                ms, mr = preview_shot_structure(pr, name)
                self._show_dual_preview("Shot", ms, "Render", mr, "shot")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.append_log(f"[error][shot-preview] {e}")
            return

        def _do() -> str:
            s, r = create_shot_structure(pr, name)
            return f"Created shot:\n{s}\n\nCreated render:\n{r}"
        self._exec_and_report("shot", _do)

    def _on_update_shot(self) -> None:
        name = self.shot_name_var.get().strip()
        pr = self._selected_project_root(self.shot_project_var)
        if pr is None or not self._require(name, "Shot name is required to update an existing shot."):
            return

        if self.shot_dry_run_var.get():
            try:
                ms, mr = preview_update_shot_structure(pr, name)
                self._show_dual_preview("Shot", ms, "Render", mr, "shot-update", action="added")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.append_log(f"[error][shot-update-preview] {e}")
            return

        def _do() -> str:
            s, r = update_shot_structure(pr, name)
            return f"Updated shot structure:\n{s}\n\nUpdated render structure:\n{r}"
        self._exec_and_report("shot-update", _do)

    def _on_open_shot_folder(self) -> None:
        name = self.shot_name_var.get().strip()
        if not self._require(name, "Shot name is required to open the folder."):
            return
        pr = self._selected_project_root(self.shot_project_var)
        if pr is None:
            return
        path = pr / "shot" / name
        if not path.is_dir():
            messagebox.showerror("Error", f"Shot folder does not exist:\n{path}")
            return
        try:
            open_folder(path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = PipelineFoldersGui()
    app.run()


if __name__ == "__main__":
    main()
