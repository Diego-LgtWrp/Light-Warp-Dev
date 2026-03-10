"""
Directory lock/unlock tool — restrict or restore write access to pipeline folders.

Provides platform-specific locking (Windows icacls, Linux chmod, macOS chflags)
behind an authentication gate.  Requires ``customtkinter``.
"""

import os
import platform
import subprocess
import customtkinter as ctk
from .auth.password import authenticate


# -------------------------
# OS LOCK FUNCTIONS
# -------------------------

def lock_windows(path):
    result = subprocess.run(
        ["icacls", path, "/deny", "Users:(D,DC)", "/T"],
        capture_output=True
    )
    return result.returncode == 0


def unlock_windows(path):
    result = subprocess.run(
        ["icacls", path, "/remove:d", "Users", "/T"],
        capture_output=True
    )
    return result.returncode == 0


def lock_linux(path):
    try:
        for root, dirs, _ in os.walk(path):
            os.chmod(root, 0o555)
        os.chmod(path, 0o555)
        return True
    except PermissionError:
        return False


def unlock_linux(path):
    try:
        for root, dirs, _ in os.walk(path):
            os.chmod(root, 0o755)
        os.chmod(path, 0o755)
        return True
    except PermissionError:
        return False


def lock_mac(path):
    result = subprocess.run(["chflags", "-R", "uchg", path])
    return result.returncode == 0


def unlock_mac(path):
    result = subprocess.run(["chflags", "-R", "nouchg", path])
    return result.returncode == 0


def lock_directory(path):

    system = platform.system()

    if system == "Windows":
        return lock_windows(path)

    elif system == "Linux":
        return lock_linux(path)

    elif system == "Darwin":
        return lock_mac(path)

    return False


def unlock_directory(path):

    system = platform.system()

    if system == "Windows":
        return unlock_windows(path)

    elif system == "Linux":
        return unlock_linux(path)

    elif system == "Darwin":
        return unlock_mac(path)

    return False


# -------------------------
# GUI WINDOW
# -------------------------

class LockWindow(ctk.CTkToplevel):

    def __init__(self, parent, mode, target_path):

        super().__init__(master=parent)

        self.mode = mode
        self.target_path = target_path

        self.title("Directory Lock")
        self.geometry("350x260")
        self.resizable(False, False)

        self.grab_set()  # modal window

        self.username = None

        self.build_login_ui()

    # -------------------------
    # LOGIN UI
    # -------------------------

    def build_login_ui(self):

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10, padx=20)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10, padx=20)

        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(pady=5)

        self.submit_button = ctk.CTkButton(
            self,
            text="Authenticate",
            command=self.check_auth
        )
        self.submit_button.pack(pady=10)

    # -------------------------
    # AUTHENTICATION
    # -------------------------

    def check_auth(self):

        username = self.username_entry.get()
        password = self.password_entry.get()

        unlock, message = authenticate(username, password)  # Call the authenticate function from password.py

        if unlock:

            self.message_label.configure(message)

            self.username_entry.destroy()
            self.password_entry.destroy()
            self.submit_button.destroy()

            self.build_lock_ui()

        else:
            self.message_label.configure(message)

    # -------------------------
    # LOCK UI
    # -------------------------

    def build_lock_ui(self):

        self.state_label = ctk.CTkLabel(
            self,
            text="Ready"
        )
        self.state_label.pack(pady=10)

        self.lock_button = ctk.CTkButton(
            self,
            text="Lock Directory",
            command=self.lock_directory_action
        )
        self.lock_button.pack(pady=5)

        self.unlock_button = ctk.CTkButton(
            self,
            text="Unlock Directory",
            command=self.unlock_directory_action
        )
        self.unlock_button.pack(pady=5)

    # -------------------------
    # LOCK ACTION
    # -------------------------

    def lock_directory_action(self):

        success = lock_directory(self.target_path)

        if success:
            self.state_label.configure(
                text=f"{self.mode.capitalize()} folder LOCKED"
            )
        else:
            self.state_label.configure(
                text="Lock failed (permissions?)"
            )

    # -------------------------
    # UNLOCK ACTION
    # -------------------------

    def unlock_directory_action(self):

        success = unlock_directory(self.target_path)

        if success:
            self.state_label.configure(
                text=f"{self.mode.capitalize()} folder UNLOCKED"
            )
        else:
            self.state_label.configure(
                text="Unlock failed (permissions?)"
            )


# -------------------------
# FUNCTION CALLED BY MAIN GUI
# -------------------------

def open_lock_window(parent, mode, path):

    LockWindow(parent, mode, path)