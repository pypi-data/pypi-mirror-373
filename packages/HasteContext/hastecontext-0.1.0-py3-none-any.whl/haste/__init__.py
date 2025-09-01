"""haste: lightweight entry point."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("haste")
except PackageNotFoundError:
    __version__ = "0.0.0"

# Public API facade (re-export)
from .api import select_from_file, build_payload_from_repo  # noqa: F401

__all__ = [
    "__version__",
    "select_from_file",
    "build_payload_from_repo",
]


