import os
import sys
import datetime
import customtkinter as ctk
from tkinter import filedialog
from utils.dev.secure_transfer import core

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# -------------------------
# LOGGING FUNCTION
# -------------------------
log_buffer = []

def log(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    console.insert("end", f"{timestamp}  {message}\n")
    console.see("end")

# -------------------------
# FILE PICKERS
# -------------------------

def select_source():
    file = filedialog.askopenfilename(
        title="Select Source File"
    )
    if file:
        source_entry.delete(0, "end")
        source_entry.insert(0, file)
        log(f"Selected source: {file}")


def select_dest():
    mode = mode_var.get()

    # If validating, select a FILE
    if mode == "check":
        file = filedialog.askopenfilename(
            title="Select Destination File to Validate Against"
        )
        if file:
            dest_entry.delete(0, "end")
            dest_entry.insert(0, file)
            log(f"Selected destination file: {file}")

    # Otherwise select FOLDER
    else:
        folder = filedialog.askdirectory(
            title="Select Destination Folder"
        )
        if folder:
            dest_entry.delete(0, "end")
            dest_entry.insert(0, folder)
            log(f"Selected destination folder: {folder}")


# -------------------------
# MODE CHANGE HANDLER
# -------------------------

def on_mode_change():
    mode = mode_var.get()
    global previous_mode

    # Only clear if switching between validate and copy/move
    if (previous_mode in ["copy", "move"] and mode == "check") or \
       (previous_mode == "check" and mode in ["copy", "move"]):

        dest_entry.delete(0,"end")

    previous_mode = mode

    if mode == "check":
        dest_label.configure(text="Destination File:")
        log("Mode set to CHECK (validation only)")
    else:
        dest_label.configure(text="Destination Folder:")
        log(f"Mode set to {mode.upper()}")


# -------------------------
# PROGRESS UPDATE
# -------------------------

def update_progress(value):
    progressbar.set(value)
    app.update_idletasks()

# -------------------------
# LEAVE A NOTE_TXT AT SOURCE
# -------------------------

def create_note_file():
    source = source_entry.get()
    destination = dest_entry.get()

    filename = os.path.basename(source)
    name_only = filename.rsplit('.', 1)[0]  # Remove extension for note file name

    note_path = os.path.join(
        os.path.dirname(source),
        f"{name_only}.txt"
    )

    # Grab the entire GUI log directly
    full_log = console.get("1.0", "end").strip()

    message_header = (
        f"{filename} has been securely transferred to {destination}.\n"
        "The transfer is secure and SHA-256 checksum verified and the transaction "
        "has been documented by the following log from SecureTransfer.exe\n\n"
    )

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(message_header)
        f.write(full_log)

    log(f"Note file created: {note_path}")
    leave_note_button.grid_remove()


# -------------------------
# MAIN ACTION
# -------------------------

def run_transfer():

    try:
        source = source_entry.get()
        dest_input = dest_entry.get()
        mode = mode_var.get()
    except Exception as e:
        progressbar.set(1)
        progressbar.configure(progress_color="red")
        log(f"ERROR: {str(e)}")
        return

    if not source or not dest_input:
        status_label.configure(text="Select required fields")
        log("ERROR: Missing source or destination")
        return

    progressbar.set(0)
    progressbar.configure(progress_color="#15657f")  # Reset to default color
    log("Starting operation...")
    log(f"Mode: {mode}")

    try:

        success = False

        if mode == "check":

            status_label.configure(text="Validating...")

            log(f"Validating:\nSource: {source}\nDestination: {dest_input}")
            validation = core.validate_files(
                source,
                dest_input,
                update_progress
            )
            if validation == True:
                log("Validation successful! The files are identical.")
                success = True
            else:
                progressbar.set(1)
                progressbar.configure(progress_color="red")
                log("Validation failed! The files are not identical.")
                success = False

        else:
            filename = os.path.basename(source)
            destination = os.path.join(dest_input, filename)

            log(f"Source: {source}")
            log(f"Destination full path: {destination}")

            status_label.configure(text="Working...")
            
            safe_copy = core.copy_file(
                    source,
                    destination,
                    update_progress
                )
            if safe_copy == True:
                log("Transfer completed, Validating...")
                status_label.configure(text="Validating...")
                validation = core.validate_files(
                            source,
                            destination,
                            update_progress
                        )
                if validation == True:
                        if mode == "move":
                            os.remove(source)
                            log(f"Validation successful! Your file {filename} has been moved securely from {os.path.dirname(source)} to {dest_input}.")
                            success = True
                            if validation and mode == "move":
                                leave_note_button.grid()

                        elif mode == "copy":
                            log(f"Validation successful! Your file {filename} has been copied securely from {os.path.dirname(source)} to {dest_input}.")
                            success = True
                else:
                    progressbar.set(1)
                    progressbar.configure(progress_color="red")
                    os.remove(destination)
                    log("Validation failed! The files are not identical.")
                    success = False

        if success == True:
            progressbar.set(1)
            progressbar.configure(progress_color="green")
            app.update_idletasks()
            status_label.configure(text="SUCCESS")
        else:
            progressbar.configure(progress_color="red")
            status_label.configure(text="ERROR: Validation failed")
            log("ERROR: Validation failed! The files are not identical.")

    except Exception as e:
        status_label.configure(text="ERROR occurred")
        progressbar.set(1)
        progressbar.configure(progress_color="red")
        log(f"EXCEPTION: {str(e)}")
        
# -------------------------
# UI SETUP
# -------------------------

app = ctk.CTk()
app.title("Secure Transfer")
app.geometry("750x550")

app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(7, weight=1)

# ---- Header Section ----

header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.grid(row=0, column=0, columnspan=3, pady=(15, 5))

ctk.CTkLabel(
    header_frame,
    text="Secure Transfer",
    font=ctk.CTkFont(size=24, weight="bold")
).pack()

ctk.CTkLabel(
    header_frame,
    text="An app to securely copy, move, and validate files with SHA-256 verification + paper trail text file at source for moved files.",
    font=ctk.CTkFont(size=13),
    text_color="gray"
).pack()

# ---- Source Row ----

ctk.CTkLabel(app, text="Source File:").grid(
    row=1, column=0, padx=15, pady=15, sticky="w"
)

source_entry = ctk.CTkEntry(app)
source_entry.grid(
    row=1, column=1, padx=10, pady=15, sticky="ew"
)

ctk.CTkButton(
    app,
    text="Browse",
    width=100,
    command=select_source
).grid(
    row=1, column=2, padx=15, pady=15
)


# ---- Destination Row ----

dest_label = ctk.CTkLabel(app, text="Destination Folder:",
    anchor="w")
dest_label.grid(
    row=2, column=0, padx=15, pady=10, sticky="w"
)

dest_entry = ctk.CTkEntry(app)
dest_entry.grid(
    row=2, column=1, padx=10, pady=10, sticky="ew"
)

ctk.CTkButton(
    app,
    text="Browse",
    width=100,
    command=select_dest
).grid(
    row=2, column=2, padx=15, pady=10
)


# ---- Mode Selection ----

mode_var = ctk.StringVar(value="move")
previous_mode = "move"

mode_frame = ctk.CTkFrame(app, fg_color="transparent")
mode_frame.grid(row=3, columnspan=3, pady=10)

ctk.CTkRadioButton(
    mode_frame,
    text="Move",
    variable=mode_var,
    value="move",
    command=on_mode_change
).pack(side="left", padx=20)

ctk.CTkRadioButton(
    mode_frame,
    text="Copy",
    variable=mode_var,
    value="copy",
    command=on_mode_change
).pack(side="left", padx=20)

ctk.CTkRadioButton(
    mode_frame,
    text="Check",
    variable=mode_var,
    value="check",
    command=on_mode_change
).pack(side="left", padx=20)


# ---- Start Button ----

ctk.CTkButton(
    app,
    text="Start Secure Operation",
    height=40,
    command=run_transfer
).grid(
    row=4, column=0, columnspan=3, pady=15
)


# ---- Progress Bar ----

progressbar = ctk.CTkProgressBar(app)
progressbar.grid(
    row=5, column=0, columnspan=3,
    padx=40, pady=10, sticky="ew"
)
progressbar.set(0)


# ---- Status ----

status_label = ctk.CTkLabel(app, text="Ready")
status_label.grid(
    row=6, column=0, columnspan=3, pady=5
)


# ---- Console ----

ctk.CTkLabel(app, text="Console Log").grid(
    row=7, column=0, columnspan=3, sticky="w", padx=15
)

console = ctk.CTkTextbox(app, height=150)
console.grid(
    row=8, column=0, columnspan=3,
    padx=15, pady=5,
    sticky="nsew"
)

#---- Leave Note Button ----
leave_note_button = ctk.CTkButton(
    app,
    text="Leave a Note at Source",
    command=create_note_file
)

leave_note_button.grid(row=9, column=0, columnspan=3, pady=10)
leave_note_button.grid_remove()  # hide initially

# ---- Context Menu Support ----

if len(sys.argv) > 1:
    source_entry.insert(0, sys.argv[1])
    log(f"Loaded from context menu: {sys.argv[1]}")


app.mainloop()
