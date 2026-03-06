"""Folder structure and asset-type definitions for the LightWarp animation pipeline."""

from typing import List

from lightwarp.folders import FolderSpec

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
