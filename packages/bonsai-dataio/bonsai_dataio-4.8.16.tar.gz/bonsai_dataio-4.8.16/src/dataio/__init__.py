"""Initializes dataio Python package."""

# NOTE: Do not edit here
# Dependencies for __init__ file, d
import sys
from os import listdir
from os.path import dirname
from pathlib import Path

# NOTE: Edit here
# Functions and classes to export
from ._plot import plot

__all__ = ["describe", "validate", "plot", "load", "save", "create"]

STAGE = "util"
EXPORT_PATH = Path(dirname(__file__)).joinpath("_export")
# __all__ = ["datapackage"]

# NOTE: Do not edit from here downward
# Create package version number from git tag
if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import PackageNotFoundError, version
else:
    from importlib_metadata import PackageNotFoundError, version

# Change package version if project is renamed
try:
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError, dist_name, sys

# Remove files and folders starting with underscore from dir()
PATH = Path(dirname(__file__))
for f in listdir(PATH):
    if f[0] == "_":
        STEM = Path(f).stem
        exec(f"from . import {STEM}")
        exec(f"del {STEM}")

del (
    listdir,
    dirname,
    Path,
    PATH,
    STEM,
    f,
)
