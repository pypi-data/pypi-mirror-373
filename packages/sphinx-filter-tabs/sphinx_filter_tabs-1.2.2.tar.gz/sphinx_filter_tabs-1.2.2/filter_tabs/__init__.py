"""A robust Sphinx extension for creating accessible, JS-free filterable content tabs."""
from importlib.metadata import version, PackageNotFoundError

try:
    # Read the version from the installed package's metadata
    __version__ = version("sphinx-filter-tabs")
except PackageNotFoundError:
    # Fallback for when the package is not installed (e.g., in development)
    __version__ = "0.0.0"
