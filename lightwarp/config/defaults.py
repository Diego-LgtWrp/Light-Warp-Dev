"""
Default pipeline configuration — folder structures, templates, asset types,
and naming/versioning conventions.

Override any value in ``lightwarp/config/local.py`` (gitignored).
"""

from typing import Dict, List

from lightwarp.folders import FolderSpec

# ---------------------------------------------------------------------------
# Folder structures
# ---------------------------------------------------------------------------

PROJECT_STRUCTURE: FolderSpec = {
    "asset": {},
    "shot": {},
    "unreal": {},
    "utils": {"vdev": {}, "tools": {}},
    "render": {},
    "final": {"edit": {}, "mgfx": {}, "sound": {}},
}

ASSET_STRUCTURE: FolderSpec = {
    "blend": {},
    "substance": {},
    "geo": {},
    "mat": {"tex": {}},
    "cache": {},
}

SHOT_STRUCTURE: FolderSpec = {
    "layout": {},
    "anim": {},
    "cfx": {},
    "fx": {},
    "light": {},
    "publish": {"anim": {}, "cache": {}, "usd": {}},
}

RENDER_STRUCTURE: FolderSpec = {
    "beauty": {"exr": {}},
    "data": {"cryptomattes": {}, "exr": {}},
    "comp": {},
    "mov": {},
}

ASSET_TYPES: List[str] = ["char_", "prop_"]

# ---------------------------------------------------------------------------
# Template mappings
# ---------------------------------------------------------------------------

TEMPLATE_MAPPINGS: Dict[str, Dict[str, str]] = {
    "blend": {
        "filename": "template.blend",
        "subfolder": "blend",
        "extension": ".blend",
    },
    "substance": {
        "filename": "template.spp",
        "subfolder": "substance",
        "extension": ".spp",
    },
}

# ---------------------------------------------------------------------------
# Naming / versioning conventions
#
#   {name}{VERSION_SEPARATOR}{VERSION_PREFIX}{version}{ext}
#   char_hero_v001.blend
# ---------------------------------------------------------------------------

VERSION_PREFIX: str = "v"
VERSION_SEPARATOR: str = "_"
VERSION_PADDING: int = 3

# ---------------------------------------------------------------------------
# Batch / sequence naming
#
#   SEQUENCE_PREFIX + padded number  →  sq010, sq020
#   SHOT_PREFIX     + padded number  →  s010, s020
# ---------------------------------------------------------------------------

SEQUENCE_PREFIX: str = "sq"
SHOT_PREFIX: str = "s"
BATCH_PADDING: int = 3
BATCH_INCREMENT: int = 100
