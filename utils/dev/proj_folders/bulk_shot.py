"""
Bulk shot creation dialog — generate multiple numbered shots at once.

Opens as a modal window from the main Pipeline Manager GUI.
Requires ``customtkinter``.
"""

import customtkinter as ctk


# -------------------------
# BULK SHOT PROCESSING FUNCTIONS
# -------------------------

def bulk_shot_setup(range_text, shot_count):
    print(range_text, shot_count)


# -------------------------
# GUI WINDOW
# -------------------------

class BulkShotWindow(ctk.CTkToplevel):

    def __init__(self, parent):

        super().__init__(master=parent)

        self.title("Bulk Shot Processing")
        self.geometry("400x300")
        self.resizable(False, False)

        self.grab_set()

        self.build_ui()

    # -------------------------
    # UI
    # -------------------------

    def build_ui(self):

        # HEADER
        header_label = ctk.CTkLabel(
            self,
            text="Bulk Shot Mode",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=(15, 5))

        description_label = ctk.CTkLabel(
            self,
            text="Enter a number range (ex: 100-1000) and how many shots\n"
                 "you want (ex: 10) to generate incremented shot names\n"
                 "(s100, s200 ... s1000).",
            justify="center"
        )
        description_label.pack(pady=(0, 15), padx=20)

        # INPUT FRAME
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(padx=20, pady=10, fill="x")

        self.input_frame.grid_columnconfigure(1, weight=1)

        # RANGE
        range_label = ctk.CTkLabel(self.input_frame, text="Shot Range")
        range_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.range_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="100-1000"
        )
        self.range_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # SHOT COUNT
        count_label = ctk.CTkLabel(self.input_frame, text="Number of Shots")
        count_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.count_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="10"
        )
        self.count_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # BUTTON
        self.submit_button = ctk.CTkButton(
            self,
            text="Bulk Shot Setup",
            command=self.run_bulk_setup
        )
        self.submit_button.pack(pady=20)

    # -------------------------
    # BUTTON FUNCTION
    # -------------------------

    def run_bulk_setup(self):

        range_text = self.range_entry.get()
        shot_count = self.count_entry.get()

        bulk_shot_setup(range_text, shot_count)


# -------------------------
# FUNCTION CALLED BY MAIN GUI
# -------------------------

def open_bulk_shot(parent):
    BulkShotWindow(parent)