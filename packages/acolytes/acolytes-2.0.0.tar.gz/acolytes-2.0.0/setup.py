from setuptools import setup, find_packages
import os
from importlib.metadata import version, PackageNotFoundError

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Try to get version from installed package, fallback to reading from __init__.py
try:
    pkg_version = version("acolytes")
except PackageNotFoundError:
    # If package is not installed, read from __init__.py
    import re
    with open("acolytes/__init__.py", "r") as f:
        version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', f.read(), re.M)
        if version_match:
            pkg_version = version_match.group(1)
        else:
            pkg_version = "0.0.0"  # fallback

setup(
    name="acolytes",
    version=pkg_version,
    author="unmasSk",
    author_email="",
    description="Acolytes for Claude Code - Multi-agent system with 57+ specialized AI assistants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unmasSk/acolytes",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "colorama>=0.4",
        "packaging>=21.0",
        "pathlib",
    ],
    entry_points={
        "console_scripts": [
            "acolytes=acolytes.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "acolytes": [
            "data/agents/*.md",
            "data/commands/*.md", 
            "data/scripts/*.py",
            "data/hooks/*.py",
            "data/resources/**/*",
        ],
    },
)