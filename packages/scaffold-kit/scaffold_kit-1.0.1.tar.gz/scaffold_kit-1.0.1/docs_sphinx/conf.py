"""Sphinx configuration for scaffold-kit."""

from __future__ import annotations

import os
import sys


# Add package to path
sys.path.insert(0, os.path.abspath("../src"))

# Get version from package
try:
    from scaffold_kit.__version__ import __version__

    version = __version__
    release = version
except ImportError:
    version = "unknown"
    release = "unknown"

# Project information
project = "Scaffold Kit"
author = "Dirk Sidney Jansen"
# pylint: disable=redefined-builtin
copyright = " 2025 Dirk Sidney Jansen. All Rights Reserved"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_favicon",
]

# Theme (using default alabaster)
html_theme = "alabaster"
html_theme_options = {
    "github_user": "sidisinsane",
    "github_repo": "scaffold-kit",
    "show_powered_by": False,
    "description": (
        "Command-line tools for project setup, structure creation, file "
        "tracking, and directory trees."
    ),
}

html_static_path = ["_static"]
html_logo = "_static/logo.svg"
exclude_patterns = []

# Favicons configuration
favicons = [
    {"rel": "shortcut icon", "sizes": "any", "href": "favicon.ico"},
]

# AutoDoc configuration
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
