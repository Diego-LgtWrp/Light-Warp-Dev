"""
Batch creation dialog — generate sequences with shots, or batch-create assets.

Opens as a modal window from the main Pipeline Manager GUI.
Requires ``customtkinter``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional, Tuple

import customtkinter as ctk

from lightwarp.config import (
    BATCH_INCREMENT,
    BATCH_PADDING,
    SEQUENCE_PREFIX,
    SHOT_PREFIX,
)
from .core import create_asset_structure, create_shot_structure


# ---------------------------------------------------------------------------
# Name generation (pure logic — no GUI)
# ---------------------------------------------------------------------------

def generate_sequence_shots(
    seq_count: int,
    shots_per_seq: int,
    start: int = 10,
    increment: int = BATCH_INCREMENT,
    seq_prefix: str = SEQUENCE_PREFIX,
    shot_prefix: str = SHOT_PREFIX,
    padding: int = BATCH_PADDING,
) -> List[Tuple[str, str]]:
    """Return ``(seq_dir, shot_dir)`` pairs for every shot across all sequences.

    Example with defaults (seq_count=2, shots_per_seq=3)::

        [("sq010", "s010"), ("sq010", "s020"), ("sq010", "s030"),
         ("sq020", "s010"), ("sq020", "s020"), ("sq020", "s030")]
    """
    pairs: List[Tuple[str, str]] = []
    for si in range(seq_count):
        seq_num = start + si * increment
        seq_name = f"{seq_prefix}{seq_num:0{padding}d}"
        for shi in range(shots_per_seq):
            shot_num = start + shi * increment
            shot_name = f"{shot_prefix}{shot_num:0{padding}d}"
            pairs.append((seq_name, shot_name))
    return pairs


def generate_flat_shots(
    count: int,
    start: int = 10,
    increment: int = BATCH_INCREMENT,
    prefix: str = SHOT_PREFIX,
    padding: int = BATCH_PADDING,
) -> List[str]:
    """Return flat shot names (no sequence grouping).

    Example (count=3)::

        ["s010", "s020", "s030"]
    """
    return [
        f"{prefix}{start + i * increment:0{padding}d}"
        for i in range(count)
    ]


# ---------------------------------------------------------------------------
# Batch creation dialog
# ---------------------------------------------------------------------------

class BatchCreationWindow(ctk.CTkToplevel):

    def __init__(
        self,
        parent: ctk.CTk,
        *,
        project_root: Optional[Path] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        mode: str = "shots",
    ):
        super().__init__(master=parent)

        self.project_root = project_root
        self._log = log_callback or (lambda m: None)
        self._mode = mode

        self.title("Batch Creation")
        self.geometry("560x620")
        self.resizable(False, False)
        self.grab_set()

        self._tabs = ctk.CTkTabview(self, anchor="nw")
        self._tabs.pack(fill="both", expand=True, padx=12, pady=12)

        self._build_sequence_tab()
        self._build_flat_shots_tab()
        self._build_assets_tab()

        if mode == "assets":
            self._tabs.set("Batch Assets")
        else:
            self._tabs.set("Sequences")

    # ------------------------------------------------------------------
    # Sequences tab
    # ------------------------------------------------------------------

    def _build_sequence_tab(self):
        tab = self._tabs.add("Sequences")

        info = ctk.CTkLabel(
            tab,
            text="Create numbered sequences, each containing numbered shots.",
            wraplength=500,
        )
        info.pack(anchor="w", pady=(0, 8))

        grid = ctk.CTkFrame(tab, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=1)

        self._seq_prefix = self._labeled_entry(grid, 0, "Sequence prefix", SEQUENCE_PREFIX)
        self._shot_prefix = self._labeled_entry(grid, 1, "Shot prefix", SHOT_PREFIX)
        self._seq_count = self._labeled_entry(grid, 2, "Number of sequences", "3")
        self._shots_per_seq = self._labeled_entry(grid, 3, "Shots per sequence", "5")
        self._seq_start = self._labeled_entry(grid, 4, "Start number", "10")
        self._seq_increment = self._labeled_entry(grid, 5, "Increment", str(BATCH_INCREMENT))
        self._seq_padding = self._labeled_entry(grid, 6, "Padding", str(BATCH_PADDING))

        btn_row = ctk.CTkFrame(tab, fg_color="transparent")
        btn_row.pack(fill="x", pady=8)
        ctk.CTkButton(btn_row, text="Preview", width=100, command=self._preview_sequences).pack(side="left")
        ctk.CTkButton(btn_row, text="Create", width=100, command=self._create_sequences).pack(side="left", padx=8)

        self._seq_preview = ctk.CTkTextbox(tab, height=160)
        self._seq_preview.pack(fill="both", expand=True, pady=(4, 0))

    # ------------------------------------------------------------------
    # Flat shots tab
    # ------------------------------------------------------------------

    def _build_flat_shots_tab(self):
        tab = self._tabs.add("Flat Shots")

        info = ctk.CTkLabel(
            tab,
            text="Create multiple shots directly under the project (no sequences).",
            wraplength=500,
        )
        info.pack(anchor="w", pady=(0, 8))

        grid = ctk.CTkFrame(tab, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=1)

        self._flat_prefix = self._labeled_entry(grid, 0, "Shot prefix", SHOT_PREFIX)
        self._flat_count = self._labeled_entry(grid, 1, "Number of shots", "5")
        self._flat_start = self._labeled_entry(grid, 2, "Start number", "10")
        self._flat_increment = self._labeled_entry(grid, 3, "Increment", str(BATCH_INCREMENT))
        self._flat_padding = self._labeled_entry(grid, 4, "Padding", str(BATCH_PADDING))

        btn_row = ctk.CTkFrame(tab, fg_color="transparent")
        btn_row.pack(fill="x", pady=8)
        ctk.CTkButton(btn_row, text="Preview", width=100, command=self._preview_flat_shots).pack(side="left")
        ctk.CTkButton(btn_row, text="Create", width=100, command=self._create_flat_shots).pack(side="left", padx=8)

        self._flat_preview = ctk.CTkTextbox(tab, height=180)
        self._flat_preview.pack(fill="both", expand=True, pady=(4, 0))

    # ------------------------------------------------------------------
    # Batch assets tab
    # ------------------------------------------------------------------

    def _build_assets_tab(self):
        tab = self._tabs.add("Batch Assets")

        info = ctk.CTkLabel(
            tab,
            text="Enter one asset name per line. Each will be created under the selected project.",
            wraplength=500,
        )
        info.pack(anchor="w", pady=(0, 8))

        type_row = ctk.CTkFrame(tab, fg_color="transparent")
        type_row.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(type_row, text="Asset type prefix").pack(side="left", padx=(0, 8))
        self._asset_type_var = ctk.StringVar(value="char")
        ctk.CTkComboBox(
            type_row, width=120, variable=self._asset_type_var,
            values=["env", "char", "prop"],
        ).pack(side="left")

        self._asset_names_box = ctk.CTkTextbox(tab, height=120)
        self._asset_names_box.pack(fill="x", pady=(0, 6))
        self._asset_names_box.insert("1.0", "char_hero\nchar_sidekick\nprop_sword")

        btn_row = ctk.CTkFrame(tab, fg_color="transparent")
        btn_row.pack(fill="x", pady=4)
        ctk.CTkButton(btn_row, text="Preview", width=100, command=self._preview_assets).pack(side="left")
        ctk.CTkButton(btn_row, text="Create", width=100, command=self._create_assets).pack(side="left", padx=8)

        self._asset_preview = ctk.CTkTextbox(tab, height=140)
        self._asset_preview.pack(fill="both", expand=True, pady=(4, 0))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _labeled_entry(parent, row: int, label: str, default: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=3)
        entry = ctk.CTkEntry(parent, width=140)
        entry.grid(row=row, column=1, sticky="w", pady=3)
        entry.insert(0, default)
        return entry

    def _set_preview(self, textbox: ctk.CTkTextbox, text: str):
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)

    def _int(self, entry: ctk.CTkEntry, fallback: int = 0) -> int:
        try:
            return int(entry.get().strip())
        except ValueError:
            return fallback

    def _require_project(self) -> Optional[Path]:
        if self.project_root and self.project_root.is_dir():
            return self.project_root
        from tkinter import messagebox
        messagebox.showerror("Error", "No valid project selected in the main window.")
        return None

    # ------------------------------------------------------------------
    # Sequence actions
    # ------------------------------------------------------------------

    def _read_seq_params(self):
        return dict(
            seq_count=self._int(self._seq_count, 1),
            shots_per_seq=self._int(self._shots_per_seq, 1),
            start=self._int(self._seq_start, 10),
            increment=self._int(self._seq_increment, BATCH_INCREMENT),
            seq_prefix=self._seq_prefix.get().strip() or SEQUENCE_PREFIX,
            shot_prefix=self._shot_prefix.get().strip() or SHOT_PREFIX,
            padding=self._int(self._seq_padding, BATCH_PADDING),
        )

    def _preview_sequences(self):
        pairs = generate_sequence_shots(**self._read_seq_params())
        lines = [f"{seq}/{shot}" for seq, shot in pairs]
        self._set_preview(self._seq_preview, "\n".join(lines) if lines else "(nothing to create)")

    def _create_sequences(self):
        pr = self._require_project()
        if not pr:
            return
        pairs = generate_sequence_shots(**self._read_seq_params())
        created, skipped = 0, 0
        for seq, shot in pairs:
            name = f"{seq}/{shot}"
            try:
                create_shot_structure(pr, name)
                created += 1
                self._log(f"[batch] Created shot {name}")
            except Exception as e:
                skipped += 1
                self._log(f"[batch] Skipped {name}: {e}")
        self._log(f"[batch] Done — {created} created, {skipped} skipped")
        self._set_preview(self._seq_preview, f"Created {created}, skipped {skipped}")

    # ------------------------------------------------------------------
    # Flat shot actions
    # ------------------------------------------------------------------

    def _preview_flat_shots(self):
        names = generate_flat_shots(
            count=self._int(self._flat_count, 1),
            start=self._int(self._flat_start, 10),
            increment=self._int(self._flat_increment, BATCH_INCREMENT),
            prefix=self._flat_prefix.get().strip() or SHOT_PREFIX,
            padding=self._int(self._flat_padding, BATCH_PADDING),
        )
        self._set_preview(self._flat_preview, "\n".join(names) if names else "(nothing to create)")

    def _create_flat_shots(self):
        pr = self._require_project()
        if not pr:
            return
        names = generate_flat_shots(
            count=self._int(self._flat_count, 1),
            start=self._int(self._flat_start, 10),
            increment=self._int(self._flat_increment, BATCH_INCREMENT),
            prefix=self._flat_prefix.get().strip() or SHOT_PREFIX,
            padding=self._int(self._flat_padding, BATCH_PADDING),
        )
        created, skipped = 0, 0
        for name in names:
            try:
                create_shot_structure(pr, name)
                created += 1
                self._log(f"[batch] Created shot {name}")
            except Exception as e:
                skipped += 1
                self._log(f"[batch] Skipped {name}: {e}")
        self._log(f"[batch] Done — {created} created, {skipped} skipped")
        self._set_preview(self._flat_preview, f"Created {created}, skipped {skipped}")

    # ------------------------------------------------------------------
    # Asset actions
    # ------------------------------------------------------------------

    def _parse_asset_names(self) -> List[str]:
        raw = self._asset_names_box.get("1.0", "end").strip()
        return [n.strip() for n in raw.splitlines() if n.strip()]

    def _preview_assets(self):
        names = self._parse_asset_names()
        self._set_preview(self._asset_preview, "\n".join(names) if names else "(no asset names entered)")

    def _create_assets(self):
        pr = self._require_project()
        if not pr:
            return
        names = self._parse_asset_names()
        created, skipped = 0, 0
        for name in names:
            try:
                create_asset_structure(pr, name)
                created += 1
                self._log(f"[batch] Created asset {name}")
            except Exception as e:
                skipped += 1
                self._log(f"[batch] Skipped {name}: {e}")
        self._log(f"[batch] Done — {created} created, {skipped} skipped")
        self._set_preview(self._asset_preview, f"Created {created}, skipped {skipped}")


# ---------------------------------------------------------------------------
# Entry point called by the main GUI
# ---------------------------------------------------------------------------

def open_bulk_shot(
    parent: ctk.CTk,
    *,
    project_root: Optional[Path] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    mode: str = "shots",
):
    BatchCreationWindow(
        parent,
        project_root=project_root,
        log_callback=log_callback,
        mode=mode,
    )
