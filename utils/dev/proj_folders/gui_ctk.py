#!/usr/bin/env python3
"""
Pipeline Manager GUI — CustomTkinter version.

Provides project, asset, and shot folder creation with a modern dark UI.
Requires ``customtkinter``:  pip install customtkinter
"""

import sys
from pathlib import Path

import os
import customtkinter as ctk
from datetime import datetime
from tkinter import filedialog, messagebox

from lightwarp.config import ASSET_TYPES
from lightwarp.util import open_folder as _open_folder
from .bulk_shot import open_bulk_shot
from .core import (
    create_asset_structure,
    create_project_structure,
    create_shot_structure,
    get_default_projects_root,
    preview_asset_structure,
    preview_project_structure,
    preview_shot_structure,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class PipelineFoldersGui:

    def __init__(self):

        self.root = ctk.CTk()
        self.root.title("Pipeline Manager")
        self.root.geometry("900x600")

        self.main = ctk.CTkScrollableFrame(self.root)
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        self._build_header()
        self._build_main_section()

        self.refresh_project_lists()
        self.root.update_idletasks()


    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    def _build_header(self):

        ctk.CTkLabel(
            self.main,
            text="Pipeline Manager",
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(anchor="w")

        hrow = ctk.CTkFrame(self.main)
        hrow.pack(fill="x", pady=15)

        ctk.CTkLabel(
            hrow,
            text="Create and update project, asset, and shot folder structures",
        ).pack(anchor="w", side="left")

    # --------------------------------------------------
    # PREVIEW MODE
    # --------------------------------------------------

        self.preview_mode = ctk.BooleanVar()
        ctk.CTkCheckBox(hrow,text="Preview Mode (For Testing - No Files Created)",
                        command=self.check_preview_mode,
                        variable=self.preview_mode,
                        ).pack(side="right", anchor ="w", padx=10)

    def check_preview_mode(self):
        if self.preview_mode.get() == True:
            self.append_log("[info] Preview mode is ON. No files will be created.")
            return True
        else:
            self.append_log("[info] Preview mode is OFF. Files will be created.")
            return False

    # --------------------------------------------------
    # PROJECT
    # --------------------------------------------------

    def _build_main_section(self):

        self.root_var = ctk.StringVar(value=str(get_default_projects_root()))
        self.project_name_var = ctk.StringVar()

    # -----------------------------
    # PROJECT ROOT (FULL WIDTH)
    # -----------------------------

        root_row = ctk.CTkFrame(self.main, fg_color="transparent")
        root_row.pack(fill="x", pady=5)

        ctk.CTkLabel(root_row, text="Projects root").pack(side="left", padx=(0,5))
        ctk.CTkEntry(root_row, textvariable=self.root_var).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(root_row, text="Set Root Folder", command=self._browse_root).pack(side="left", padx=5)
        ctk.CTkButton(root_row, text="Open Root Folder", command=self._open_projects_root).pack(side="left", padx=5)

        self.separator()

        # -----------------------------
        # LOWER SECTION (SIDE BY SIDE)
        # -----------------------------

        mid_section = ctk.CTkFrame(self.main,fg_color="transparent")
        mid_section.pack(fill="both", expand=True, pady=(0,20))

        lower_section = ctk.CTkFrame(self.main,fg_color="transparent")
        lower_section.pack(fill="both", expand=True, pady=5)

        # LEFT SIDE (PROJECT CONTROLS)
        project_frame = ctk.CTkFrame(mid_section, fg_color="transparent")
        project_frame.pack(side="left", fill="both", expand=True,padx=5)

        # RIGHT SIDE (EVENT LOG)
        console_frame = ctk.CTkFrame(mid_section, width=600, height=100, fg_color="transparent")
        console_frame.pack(side="left", fill="both", expand=True)
        console_frame.pack_propagate(False)

        asset_frame = ctk.CTkFrame(lower_section, width=300, fg_color="transparent")
        asset_frame.pack(side="left", fill="both",padx=5)

        shot_frame = ctk.CTkFrame(lower_section, width=300, fg_color="transparent")
        shot_frame.pack(side="right", fill="both",padx=10)

    # -----------------------------
    # PROJECT SECTION
    # -----------------------------

        ctk.CTkLabel(project_frame, text="Project", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        proj_row = ctk.CTkFrame(project_frame, fg_color="transparent")
        proj_row.pack(fill="x", pady=10)

        ctk.CTkLabel(proj_row, text="Project name").pack(side="left")
        ctk.CTkEntry(
            proj_row,
            textvariable=self.project_name_var,
            placeholder_text="Enter new project name",
            width=200
        ).pack(side="left", padx=10)
        ctk.CTkCheckBox(proj_row, text="Sequence Project").pack(side="left", anchor="w", padx=5)

        proj_button_row = ctk.CTkFrame(project_frame, fg_color="transparent")
        proj_button_row.pack(fill="x")

        ctk.CTkButton(proj_button_row, text="Create Project", command=self._create_project)\
            .grid(row=0, column=0, sticky="w")

        ctk.CTkButton(proj_button_row, text="Open Project Folder", command=self._open_project_folder)\
            .grid(row=0, column=1, sticky="w", padx=10)
        

    # -----------------------------
    # EVENT LOG
    # -----------------------------

        ctk.CTkLabel(console_frame, text="Event Log", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        self.log = ctk.CTkTextbox(console_frame, height=100)
        self.log.pack(fill="both",expand=True)

        self.separator()
    
    # --------------------------------------------------
    # ASSET
    # --------------------------------------------------

        ctk.CTkLabel(asset_frame, text="Asset", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        self.asset_project_var = ctk.StringVar()
        self.asset_type_var = ctk.StringVar(value="env")

        self.blend_var = ctk.BooleanVar()
        self.substance_var = ctk.BooleanVar()

        self.asset_project_frame = ctk.CTkFrame(asset_frame,fg_color="transparent")
        self.asset_project_frame.pack(fill="both", expand=True, pady=4)

        ctk.CTkLabel(self.asset_project_frame, text="Select Project").pack(side="left", padx=(0,5))
        self.asset_project_combo = ctk.CTkComboBox(self.asset_project_frame, width=300, variable=self.asset_project_var, values=[])
        self.asset_project_combo.pack(side="left", padx=4)

        self.asset_typeframe = ctk.CTkFrame(asset_frame,fg_color="transparent")
        self.asset_typeframe.pack(fill="both", expand=True, pady=4)

        self.asset_name_var = ctk.CTkEntry(self.asset_typeframe,width=280, placeholder_text="Asset name")
        self.asset_name_var.pack(side="left", fill="x")
        ctk.CTkComboBox(self.asset_typeframe,width=100, variable=self.asset_type_var, values=["env","char","prop"]).pack(side="left", padx=(5,0))

        ''' Deprecated .blend and .sbsar files checkbox, but keeping the code in case we need to re-enable it in the future
        self.button_frame = ctk.CTkFrame(asset_frame, fg_color="transparent")
        self.button_frame.pack(pady=5, fill="x", expand=True)

        ctk.CTkCheckBox(self.button_frame, text="Create Substance file", variable=self.substance_var).pack(side="right", padx=10)
        '''

        ctk.CTkButton(asset_frame, text="Create Asset", command=self._create_asset).pack(anchor="w", pady=5)
        ctk.CTkButton(asset_frame, text="Open Asset Folder", command=self._open_asset_folder).pack(anchor="w", pady=5)

        self.separator()

    # --------------------------------------------------
    # SHOT
    # --------------------------------------------------

        ctk.CTkLabel(shot_frame, text="Shot", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        self.shot_project_var = ctk.StringVar()

        self.shot_project_frame = ctk.CTkFrame(shot_frame,fg_color="transparent")
        self.shot_project_frame.pack(fill="both", expand=True, pady=2)

        ctk.CTkLabel(self.shot_project_frame, text="Select Project").pack(side="left", padx=(0,5))
        self.shot_project_combo = ctk.CTkComboBox(self.shot_project_frame, width=300,variable=self.shot_project_var, values=[])
        self.shot_project_combo.pack(side="left", padx=5)

        self.shot_name_var = ctk.CTkEntry(shot_frame, placeholder_text="Shot name")
        self.shot_name_var.pack(fill="x", pady=5)

        ctk.CTkButton(shot_frame, text="Create Shot", command=self._create_shot).pack(anchor="w", pady=5)
        ctk.CTkButton(shot_frame, text="Bulk Shot Setup", command=lambda: open_bulk_shot(self.root)).pack(anchor="w", pady=5)
        ctk.CTkButton(shot_frame, text="Open Shot Folder", command=self._open_shot_folder).pack(anchor="w", pady=5)

        self.separator()


    # --------------------------------------------------
    # HELPER FUNCTIONS
    # --------------------------------------------------

    #Project functions
    # --------------------------------------------------
    def _open_project_folder(self):
        name = self.project_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Project name is required to open the folder.")
            self.append_log("[error] Project name is required to open the folder.")
            return

        try:
            path = Path(self.root_var.get()) / name

            if not path.is_dir():
                messagebox.showerror("Error", f"Project folder does not exist:\n{path}")
                self.append_log(f"[error] Project folder does not exist: {path}")
                return

            self._open_in_browser(path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open project folder:\n{e}")
            self.append_log(f"[error] Failed to open project folder: {e}")


    def _open_projects_root(self):
        path = self.root_var.get()

        if not os.path.exists(path):
            messagebox.showerror("Error", f"Root folder does not exist:\n{path}")
            self.append_log(f"[error] Root folder does not exist: {path}")
            return

        self._open_in_browser(path)

    def _browse_root(self):
        d = filedialog.askdirectory()
        if d:
            self.root_var.set(d)
            self.refresh_project_lists()

    def _create_project(self):

        root = Path(self.root_var.get())
        name = self.project_name_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Project name required")
            self.append_log(f"[error] Project name required")
            return

        if self.check_preview_mode():
            folders = preview_project_structure(root, name)
            messagebox.showinfo("Preview", "\n".join(map(str, folders)))
            return

        p = create_project_structure(root, name)

        messagebox.showinfo("Success", f"Created project:\n{p}")
        self.append_log(f"[success] Created project: {p}")
        self.refresh_project_lists()

    #Asset functions
    # --------------------------------------------------
    def _create_asset(self):

        name = self.asset_name_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Asset name required.")
            self.append_log("[error] Asset name required.")
            return

        pr = Path(self.root_var.get()) / self.asset_project_var.get()

        if self.check_preview_mode():
            folders = preview_asset_structure(pr, name)
            messagebox.showinfo("Preview", "\n".join(map(str, folders)))
            return

        p = create_asset_structure(
            pr,
            name,
            create_blend_file=self.blend_var.get(),
            create_substance_file=self.substance_var.get(),
        )

        messagebox.showinfo("Success", str(p))
        self.append_log(f"[success] Created asset: {p}")

    
    def _open_asset_folder(self):

        name = self.asset_name_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Asset name is required to open the folder.")
            self.append_log("[error] Asset name is required to open the folder.")
            return

        project = self.asset_project_var.get()

        if not project:
            messagebox.showerror("Error", "Select a project first.")
            self.append_log("[error] No project selected.")
            return

        root = self.root_var.get()
        pr = os.path.join(root, project)

        path = os.path.join(pr, "asset", name)

        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Asset folder does not exist:\n{path}")
            self.append_log(f"[error] Asset folder does not exist: {path}")
            return

        self._open_in_browser(path)

    #Shot functions
    # --------------------------------------------------
    def _create_shot(self):

        name = self.shot_name_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Shot name required.")
            self.append_log("[error] Shot name required.")
            return

        pr = Path(self.root_var.get()) / self.shot_project_var.get()

        if self.check_preview_mode():
            s, r = preview_shot_structure(pr, name)
            messagebox.showinfo("Preview", "\n".join(map(str, s + r)))
            return

        s, r = create_shot_structure(pr, name)

        messagebox.showinfo("Success", f"{s}\n{r}")
        self.append_log(f"[success] Created shot: {name}")


    def _open_shot_folder(self) -> None:
        name = self.shot_name_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Shot name is required to open the folder.")
            self.append_log("[error] Shot name is required to open the folder.")
            return

        project = self.shot_project_var.get()

        if not project:
            messagebox.showerror("Error", "Select a project first.")
            self.append_log("[error] No project selected.")
            return

        root = self.root_var.get()
        pr = os.path.join(root, project)

        path = os.path.join(pr, "shot", name)

        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Shot folder does not exist:\n{path}")
            self.append_log(f"[error] Shot folder does not exist: {path}")
            return

        self._open_in_browser(path)

    #General functions
    # --------------------------------------------------
    def append_log(self, message: str):

        ts = datetime.now().strftime("%H:%M:%S")

        self.log.configure(state="normal")

        self.log.insert("end", f"[{ts}] {message.rstrip()}\n")

        self.log.see("end")

        self.log.configure(state="disabled")

    def _open_in_browser(self, path):
        try:
            _open_folder(Path(path))
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.append_log(f"[error] Failed to open folder: {path}. Error: {e}")

    def refresh_project_lists(self):

        base = Path(self.root_var.get())

        if not base.exists():
            return

        names = [p.name for p in base.iterdir() if p.is_dir()]

        if names:
            self.asset_project_combo.configure(values=names)
            self.shot_project_combo.configure(values=names) 
            self.asset_project_combo.set(names[0])
            self.shot_project_combo.set(names[0])
        else:
            self.asset_project_combo.set("")
            self.shot_project_combo.set("")

    def separator(self):
        ctk.CTkFrame(self.main, height=2).pack(fill="x", pady=10)

    # --------------------------------------------------

    def run(self):
        self.root.mainloop()


#--------------------------------------------------
# MAIN_EXECUTION
#-------------------------------------------------

def main():
    app = PipelineFoldersGui()
    app.run()


if __name__ == "__main__":
    main()