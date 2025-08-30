"""Generates a hierarchical tree representation of a directory.

This module scans a specified directory, builds a hierarchical structure of its
contents, and renders a text-based tree diagram. It uses an `IgnoreParser` to
exclude files and directories based on patterns found in a specified ignore
file (e.g., '.gitignore'). The generated tree is written to a file and also
printed to the console.

Usage:
    To run this script, navigate to your project's root directory and execute it
    as a module:

    # Generate full project tree:
    $ uv run python -m scaffold_kit.tree

    # Generate partial tree from subdirectory:
    $ uv run python -m scaffold_kit.tree my_project/data
"""

from __future__ import annotations

import os
import sys
import glob
import argparse

from pathlib import Path
from typing import Callable, Optional

from scaffold_kit.config import (
    IGNORE_FILE,
    TREE_DIRECTORY,
    TREE_FILE,
)
from scaffold_kit.utils.ignore_parser import IgnoreParser
from scaffold_kit.utils.string_utils import slugify


def build_tree_structure(paths: list[str], ignore_matches: Callable) -> dict:
    """Builds a hierarchical tree structure from a list of file paths.

    Args:
        paths: A list of file/directory paths.
        ignore_matches: A function to check if a path should be ignored.

    Returns:
        A nested dictionary representing the directory structure.
    """
    tree = {}

    for path in paths:
        if ignore_matches(path):
            continue

        parts = Path(path).parts
        current = tree

        # Build the nested structure by iterating through path parts.
        for _, part in enumerate(parts):
            if part not in current:
                current[part] = {}
            current = current[part]

    return tree


def sort_tree_items(items: list, current_path: str = "") -> list:
    """Sorts items with directories first, then files, both alphabetically.

    Args:
        items: A list of `(name, subtree)` tuples.
        current_path: The current path for checking if items are directories.

    Returns:
        A sorted list of `(name, subtree)` tuples.
    """
    directories = []
    files = []

    # 1. Separate directories and files.
    for name, subtree in items:
        # Construct the full path to check if it's a directory.
        full_path = os.path.join(current_path, name) if current_path else name

        if os.path.isdir(full_path):
            directories.append((name, subtree))
        else:
            files.append((name, subtree))

    # 2. Sort each category alphabetically.
    directories.sort(key=lambda x: x[0].lower())
    files.sort(key=lambda x: x[0].lower())

    return directories + files


def render_tree(tree: dict, prefix: str = "", current_path: str = "") -> list:
    """Recursively renders the tree structure with proper tree characters.

    Args:
        tree: The nested dictionary representing the directory structure.
        prefix: The current line prefix for indentation.
        current_path: The full path to the current directory being processed.

    Returns:
        A list of formatted lines representing the tree structure.
    """
    lines = []
    items = list(tree.items())
    sorted_items = sort_tree_items(items, current_path)

    for i, (name, subtree) in enumerate(sorted_items):
        is_last_item = i == len(sorted_items) - 1

        # Choose the appropriate tree character based on position.
        if is_last_item:
            current_prefix = prefix + "└── "
            next_prefix = prefix + "    "
        else:
            current_prefix = prefix + "├── "
            next_prefix = prefix + "│   "

        # Construct the full path to check if it's a directory.
        full_path = os.path.join(current_path, name) if current_path else name

        # Add directory indicator for directories.
        display_name = name + "/" if os.path.isdir(full_path) else name
        lines.append(current_prefix + display_name)

        # Recursively render subdirectories.
        if subtree:
            lines.extend(render_tree(subtree, next_prefix, full_path))

    return lines


# pylint: disable=too-many-locals
def generate_tree(
    root_dir: str = ".",
    ignore_file: str = ".gitignore",
    output_file: str = "directory-tree.txt",
    output_dir: Optional[str] = None,
):
    """Generates a directory tree of files in the specified directory.

    The function scans a directory, applies ignore patterns, and creates
    a text-based tree representation that is saved to a file and printed
    to the console.

    Args:
        root_dir: The root directory to scan (default: current directory).
        ignore_file: The name of the file containing ignore patterns.
        output_file: The name of the output file for the tree.
        output_dir: The directory where the output file will be saved.
            (default: current directory).

    Raises:
        SystemExit: If the specified `root_dir` does not exist.
    """
    # 1. Validate that the root directory exists.
    if not os.path.isdir(root_dir):
        print(f"Error: Directory '{root_dir}' does not exist.")
        sys.exit(1)

    # 2. Generate the output filename, sanitizing for partial trees.
    if root_dir == ".":
        display_root = "."
    else:
        # Sanitize path for filename (replace slashes with dashes).
        sanitized_path = root_dir.replace("/", "-").replace("\\", "-")
        output_file_base = Path(output_file).stem
        output_file = f"{output_file_base}-{sanitized_path}.txt"
        # Use just the last directory name for display.
        display_root = Path(root_dir).name + "/"

    # 3. Always read ignore file from the original project root.
    parser = IgnoreParser.from_file(ignore_file)

    # 4. Change to the target directory for scanning.
    original_cwd = os.getcwd()
    os.chdir(root_dir)

    try:
        # 5. Get all paths using glob, and add directories explicitly.
        # pylint: disable=unexpected-keyword-arg
        all_paths = glob.glob("**/*", recursive=True, include_hidden=True)

        all_dirs = set()
        for path in all_paths:
            p = Path(path)
            # Add all parent directories.
            for parent in p.parents:
                if parent != Path("."):
                    all_dirs.add(str(parent))

        # Combine files and directories.
        all_items = list(set(all_paths + list(all_dirs)))

        # 6. Filter paths using the ignore rules.
        if root_dir != ".":
            # For partial trees, use full paths for ignore checking.
            full_paths_for_ignore = [
                os.path.join(original_cwd, root_dir, p) for p in all_items
            ]
            filtered_relative_paths = [
                rel_path
                for rel_path, full_path in zip(all_items, full_paths_for_ignore)
                if not parser.matches(full_path)
            ]
        else:
            # For full tree, paths are already correct for ignore checking.
            filtered_relative_paths = [
                p for p in all_items if not parser.matches(p)
            ]

        sorted_paths = sorted(filtered_relative_paths)

        # 7. Build and render the tree structure.
        tree = build_tree_structure(
            sorted_paths, lambda x: False
        )  # No additional filtering needed
        lines = [display_root]
        if tree:
            lines.extend(render_tree(tree))

        content = "\n".join(lines)

    finally:
        # 8. Always return to the original directory.
        os.chdir(original_cwd)

    # 9. Write the output file in the original or set directory.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directory '{output_dir}' created successfully!")

    # Sanitize and assemble the final output file path.
    output_filename = (
        f"{slugify(Path(output_file).stem)}{Path(output_file).suffix}"
    )
    output_path = Path(output_dir) / output_filename

    print(f"Writing {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(content)
    print(f"\nSuccessfully wrote directory tree to {output_path}")


def main():
    """Main entry point to run the directory tree generation process.

    Parses command-line arguments and runs the tree generation process.
    """
    # 1. Create the argument parser.
    parser = argparse.ArgumentParser(
        description="Generate a directory tree of the project structure"
    )
    # 2. Add the positional argument for the root directory.
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    # 3. Add the optional argument for the ignore file.
    parser.add_argument(
        "--ignore-file",
        default=IGNORE_FILE,
        help=f"Ignore file to use (default: {IGNORE_FILE})",
    )

    args = parser.parse_args()
    generate_tree(
        args.root_dir,
        args.ignore_file,
        output_file=TREE_FILE,
        output_dir=TREE_DIRECTORY,
    )


if __name__ == "__main__":
    main()
