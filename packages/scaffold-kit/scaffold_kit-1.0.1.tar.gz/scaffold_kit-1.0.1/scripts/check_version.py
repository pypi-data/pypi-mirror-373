#!/usr/bin/env python3
"""Validate version consistency across the project."""

import sys

# pylint: disable=import-error
import tomllib
import subprocess  # nosec

from typing import Optional


def normalize_version(version: str) -> str:
    """Normalize version string by removing 'v' prefix if present."""
    if version and version.startswith("v"):
        return version[1:]
    return version


def get_git_tag_version() -> Optional[str]:
    """Get version from latest git tag."""
    try:
        result = subprocess.run(  # nosec
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return normalize_version(result.stdout.strip())
    except subprocess.CalledProcessError:
        return None


def get_package_version() -> Optional[str]:
    """Get version from installed package."""
    try:
        # Import your specific module
        result = subprocess.run(  # nosec
            [
                "python",
                "-c",
                "import scaffold_kit; print(scaffold_kit.__version__)",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_pyproject_version() -> Optional[str]:
    """Get version from pyproject.toml using tomllib."""
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version")
    except (FileNotFoundError, tomllib.TOMLDecodeError, KeyError):
        return None


def main() -> int:
    """Check version consistency."""
    git_version = get_git_tag_version()
    package_version = get_package_version()
    pyproject_version = get_pyproject_version()

    print(f"Git tag version: {git_version or 'Not found'}")
    print(f"Package version: {package_version or 'Not found'}")
    print(f"pyproject.toml version: {pyproject_version or 'Not found'}")

    # Collect available versions
    versions = [
        v for v in [git_version, package_version, pyproject_version] if v
    ]

    if not versions:
        print(
            "Could not determine any versions "
            "(this may be normal for new repos)"
        )
        return 0

    if len(set(versions)) == 1:
        print("SUCCESS: All versions are consistent")
        return 0

    print("ERROR: Version inconsistency detected!")
    print("All versions should match. Please update inconsistent versions.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
