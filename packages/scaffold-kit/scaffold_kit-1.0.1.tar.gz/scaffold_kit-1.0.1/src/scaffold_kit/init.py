"""Project initialization module.

This module provides functionality to initialize new projects by copying
example configuration and scaffold files from the scaffold_kit package.
It supports copying individual example files or all example files at once
to help users quickly set up their project structure.

Usage:
    To run this script, navigate to your project's root directory or parent
    directory and execute it as a module:

    # Copy all example files:
    $ uv run python -m scaffold_kit.init

    # Copy a specific example file:
    $ uv run python -m scaffold_kit.scaffold config-file
"""

from __future__ import annotations

import sys
import shutil
import argparse
import importlib.resources

from pathlib import Path
from typing import Optional


def init_project(example_name: Optional[str] = None) -> int:
    """Initialize a new project by copying example files.

    This function initializes a new project by copying example files from
    the scaffold_kit package. It can copy either a specific example file
    or all example files to the current working directory.

    Args:
        example_name: The name of the example file to copy.
            If None, all example files will be copied. Valid options include
            'ignore-file', 'config-file', and 'scaffold-file'.

    Returns:
        Exit code: 0 for success, 1 if any errors occurred.

    Examples:
        Copy a specific example file:
        >>> init_project('config-file')
        Successfully copied '.scaffoldkitrc.yaml' to the current directory.
        0

        Copy all example files:
        >>> init_project()
        No example specified. Copying all example files...
        Successfully copied '.scaffoldignore' to the current directory.
        Successfully copied '.scaffoldkitrc.yaml' to the current directory.
        Successfully copied 'scaffold.yaml' to the current directory.
        0
    """

    try:
        # Access the examples directory bundled with the package
        examples_path = importlib.resources.files("scaffold_kit").joinpath(
            "examples"
        )

        # Define mapping of user-friendly names to actual file paths
        file_map = {
            "ignore-file": examples_path.joinpath(".scaffoldignore"),
            "config-file": examples_path.joinpath(  # pylint: disable=too-many-function-args
                "configs", ".scaffoldkitrc.yaml"
            ),
            "scaffold-file": examples_path.joinpath(  # pylint: disable=too-many-function-args
                "scaffold", "scaffold.yaml"
            ),
        }

        exit_code = 0

        if example_name:
            # Copy specific file
            if example_name not in file_map:
                print(
                    f"Error: Example file '{example_name}' not found.",
                    file=sys.stderr,
                )
                print("Available options:")
                for key in file_map:
                    print(f"  - {key}")
                return 1

            source_path = file_map[example_name]
            destination_name = Path(source_path).name
            exit_code = _copy_file(source_path, destination_name)

        else:
            # Copy all files
            print("No example specified. Copying all example files...")
            for _, source_path in file_map.items():
                destination_name = Path(source_path).name
                result = _copy_file(source_path, destination_name)
                if result != 0:
                    exit_code = 1

        return exit_code

    except Exception as e:  # pylint: disable=broad-except
        print(f"Unexpected error accessing example files: {e}", file=sys.stderr)
        return 1


def _copy_file(source_path: Path, destination_name: str) -> int:
    """Copy a single file and handle errors gracefully.

    Args:
        source_path: Path to the source file
        destination_name: Name for the destination file

    Returns:
        Exit code: 0 for success, 1 for failure
    """
    destination_path = Path.cwd() / destination_name

    try:
        # Check if destination already exists
        if destination_path.exists():
            print(
                f"Warning: '{destination_name}' already exists, skipping.",
                file=sys.stderr,
            )
            return 1

        # Copy the file
        with importlib.resources.as_file(source_path) as source_file:
            shutil.copy2(source_file, destination_path)

        print(
            f"Successfully copied '{destination_name}' to the current "
            "directory."
        )
        return 0

    except PermissionError:
        print(
            f"Warning: Permission denied when copying '{destination_name}'.",
            file=sys.stderr,
        )
        return 1
    except OSError as e:
        print(
            f"Warning: Failed to copy '{destination_name}': {e}",
            file=sys.stderr,
        )
        return 1
    except Exception as e:  # pylint: disable=broad-except
        print(
            f"Warning: Unexpected error copying '{destination_name}': {e}",
            file=sys.stderr,
        )
        return 1


def main():
    """Main entry point to run the init process.

    Parses command-line arguments and runs the init_project process.
    """
    # 1. Create the argument parser.
    parser = argparse.ArgumentParser(
        description="Initialize a new project by copying example files."
    )
    # 2. Add the optional target argument.
    parser.add_argument(
        "target",
        type=str,
        nargs="?",
        choices=["ignore-file", "config-file", "scaffold-file"],
        help="Target file to copy (optional). "
        "If not provided, all files will be copied.",
    )
    args = parser.parse_args()

    # 3. Call the main scaffolding function with parsed arguments.
    exit_code = init_project(args.target)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
