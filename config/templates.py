"""Template file configuration for asset creation.

TEMPLATE_MAPPINGS maps each template type to its source filename,
the asset subfolder it copies into, and the output file extension.
Adding a new DCC template (e.g. Houdini .hip) is a single dict entry.
"""

from typing import Dict

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
