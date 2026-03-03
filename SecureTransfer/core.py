from asyncio import log
import os
import shutil
import hashlib
import time

BUFFER_SIZE = 1024 * 1024  # 64KB chunks


# -------------------------
# HASH FILE
# -------------------------

def hash_file(filepath, progress_callback=None):

    total_size = os.path.getsize(filepath)
    read_bytes = 0

    sha = hashlib.sha256()

    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break

            sha.update(chunk)
            read_bytes += len(chunk)

            if progress_callback and total_size > 0:
                progress_callback(read_bytes / total_size)
                time.sleep(0.005)  # 5ms delay

    return sha.hexdigest()


# -------------------------
# COPY FILE (WITH PROGRESS)
# -------------------------

def copy_file(source, destination, progress_callback=None):

    total_size = os.path.getsize(source)
    copied_bytes = 0

    # Convert to absolute paths for safe comparison
    source = os.path.abspath(source)
    destination = os.path.abspath(destination)

    # 1️⃣ Prevent copying onto itself
    if source == destination:
        raise ValueError("Source and destination cannot be the same file.")

    # 2️⃣ Prevent overwriting existing file
    if os.path.exists(destination):
        raise FileExistsError(
            f"{os.path.basename(destination)} already exists in destination folder."
        )

    with open(source, "rb") as src, open(destination, "wb") as dst:
        while True:
            chunk = src.read(BUFFER_SIZE)
            if not chunk:
                break

            dst.write(chunk)
            copied_bytes += len(chunk)

            if progress_callback and total_size > 0:
                progress_callback(copied_bytes / total_size)
                time.sleep(0.01)  # 10ms delay
    return True


# -------------------------
# VALIDATE TWO FILES
# -------------------------

def validate_files(source, destination, progress_callback=None):

    if source == destination:
        log("Source and destination cannot be the same file.")
        return False
    
    if os.path.getsize(source) != os.path.getsize(destination):
        return False

    hash1 = hash_file(source, progress_callback)
    hash2 = hash_file(destination, progress_callback)

    return hash1 == hash2


