"""Generates a checklist of files in a directory.

This module scans the current directory and creates a text-based checklist of
all files, excluding those specified in an ignore file (e.g., `.gitignore`).
Each file in the checklist is marked with an '[x]' if it contains content or
'[ ]' if it is empty. The final checklist is saved to a file and printed to
the console.

Usage:
    To run this script, navigate to your project's root directory and execute it
    as a module:

    $ uv run python -m scaffold_kit.checklist
"""

from __future__ import annotations

import os
import sys

from pathlib import Path
from typing import Optional

from scaffold_kit.config import (
    CHECKLIST_DIRECTORY,
    CHECKLIST_FILE,
    IGNORE_FILE,
)
from scaffold_kit.utils.ignore_parser import IgnoreParser
from scaffold_kit.utils.string_utils import slugify


def file_is_empty(file_path: str) -> bool:
    """Checks if a file is empty by checking its size.

    Args:
        file_path: The path to the file.

    Returns:
        True if the file's size is 0 bytes, False otherwise.
    """
    try:
        # Use os.stat to get file size directly without opening the file.
        return os.stat(file_path).st_size == 0
    except OSError as e:
        print(f"Error getting file stats for {file_path}: {e}", file=sys.stderr)
        return False


def walk_sorted(base: Path, root: Path | None = None) -> list[str]:
    """Walks a directory tree and returns relative paths in hierarchical order.

    Directories appear before files within each directory, both sorted
    case-insensitively. Parent directories are listed before their children.

    Args:
        base: The base path to walk.
        root: The root used to compute relative paths. Defaults to the base.

    Returns:
        A list of relative paths as strings in stable, hierarchical order.
    """
    if root is None:
        root = base

    results: list[str] = []

    # Sort entries: directories first, then files, both alphabetically
    # (casefold).
    entries = sorted(
        base.iterdir(),
        key=lambda p: (p.is_file(), p.name.casefold()),
    )

    for entry in entries:
        rel = str(entry.relative_to(root))
        results.append(rel)
        if entry.is_dir():
            results.extend(walk_sorted(entry, root))
    return results


# pylint: disable=too-many-locals
def generate_checklist(
    ignore_file: str = ".gitignore",
    output_file: str = "checklist.txt",
    output_dir: Optional[str] = None,
):
    """Generates a checklist of files and directories in the current directory.

    The traversal is hierarchical. Within each directory, entries are sorted
    case-insensitively with directories first and then files. Directories are
    always marked "[x]". Files are marked "[ ]" if empty and "[x]" otherwise.
    Paths matching patterns from the ignore file are skipped. The checklist is
    written to the output location and printed to stdout.

    Args:
        ignore_file: Name of the ignore file with patterns (e.g., ".gitignore").
        output_file: Name of the output checklist file.
        output_dir: Directory for the output file. Created if it does not exist.

    Raises:
        OSError: If writing the checklist file fails due to I/O errors.
    """
    parser = IgnoreParser.from_file(ignore_file)

    # Walk from current directory, hierarchical & sorted
    all_paths = walk_sorted(Path.cwd())

    lines = []
    for path in all_paths:
        p = Path(path)

        if parser.matches(path):
            continue

        if p.is_dir():
            # Directories always non-empty
            lines.append(f"[x] {path}/")
        else:
            mark = " " if file_is_empty(str(p)) else "x"
            lines.append(f"[{mark}] {path}")

    content = "\n".join(lines)

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directory '{output_dir}' created successfully!")

    output_filename = (
        f"{slugify(Path(output_file).stem)}{Path(output_file).suffix}"
    )
    output_path = Path(output_dir) / output_filename

    print(f"Writing {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"{content}\n")
    print(f"\nSuccessfully wrote checklist to {output_path}")


def main():
    """Main entry point to run the checklist generation process."""
    generate_checklist(
        ignore_file=IGNORE_FILE,
        output_file=CHECKLIST_FILE,
        output_dir=CHECKLIST_DIRECTORY,
    )


if __name__ == "__main__":
    main()
