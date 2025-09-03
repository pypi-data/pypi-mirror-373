"""
Acolytes for Claude Code
Multi-agent system with 60+ specialized AI assistants
Revolutionary orchestration platform for development
"""

from importlib.metadata import version, PackageNotFoundError

try:
    # Try to get version from package metadata
    __version__ = version("acolytes")
except PackageNotFoundError:
    # Package is not installed, use a fallback
    __version__ = "0.0.0+dev"

__author__ = "unmasSk"

from .cli import main

__all__ = ["main", "__version__"]