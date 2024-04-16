from io import TextIOBase

from yaml import safe_dump
from yaml import safe_load

from .data import Manifest

__all__ = ["load_manifest", "save_manifest"]


def load_manifest(file: TextIOBase) -> Manifest:
    """Load a YAML manifest file from disk.

    Args:
        file (TextIOBase):
            The file handle to read the manifest from.
    """
    data = safe_load(file)

    return Manifest.from_json(data)


def save_manifest(file: TextIOBase, manifest: Manifest):
    """Saves the manifest to disk.

    Args:
        file (TextIOBase):
            The file handle to write the manifest to.
        manifest (Manifest):
            The manifest to save to disk.
    """
    safe_dump(manifest.to_json(), file, indent=2)
