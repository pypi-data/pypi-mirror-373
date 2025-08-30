# pylint: disable=broad-except
from __future__ import annotations

import json


try:
    from importlib import metadata

    __version__ = metadata.version(__package__ or __name__)
except Exception:
    # Fallback to build-generated version file
    try:
        from scaffold_kit.__version__ import __version__
    except ImportError:
        __version__ = "unknown"


def get_version_info():
    """Get detailed version information."""
    return {
        "version": __version__,
        "is_development": __version__ == "unknown",
        "source": "metadata" if __version__ != "unknown" else "fallback",
    }


__version__ = "editable"
__author__ = "Dirk Sidney Jansen"
__email__ = "sidisinsane@users.noreply.github.com"
__title__ = "scaffold-kit"
__description__ = "A utility for scaffolding projects from structured data, with complementary tools for generating file checklists and rendering ASCII trees."  # noqa: E501
__url__ = "https://github.com/sidisinsane/scaffold-kit"
__all__ = [
    "__version__",
    "get_version_info",
    "__author__",
    "__email__",
    "__title__",
    "__description__",
    "__url__",
]


def main():
    print(json.dumps(get_version_info(), indent=2))


if __name__ == "__main__":
    main()
