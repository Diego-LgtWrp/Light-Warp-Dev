"""Naming and versioning conventions for pipeline files.

These settings control how versioned filenames are generated and parsed
across the entire pipeline.  Override any value in config/local.py.

A versioned filename looks like:

    {name}{VERSION_SEPARATOR}{VERSION_PREFIX}{version}{ext}
    char_hero_v001.blend
    sh010_anim_v002.blend

The *name* portion is context-dependent — typically the asset name for
asset work files, or ``{shot}_{task}`` for shot work files.
"""

VERSION_PREFIX: str = "v"
"""Letter(s) before the version number.  ``"v"`` → ``v001``."""

VERSION_SEPARATOR: str = "_"
"""Character between the base name and the version tag.  ``"_"`` → ``char_hero_v001``."""

VERSION_PADDING: int = 3
"""Zero-pad width.  ``3`` → ``v001``  /  ``4`` → ``v0001``."""
