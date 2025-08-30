"""Main CLI entry point for scaffold-kit.

This module provides a unified command-line interface for all scaffold-kit
subcommands: init, scaffold, checklist, and tree. It imports the core
functionality from each module and builds a proper CLI interface around them.

Usage:
    To run this script, navigate to your project's root directory or parent
    directory and execute it as a module:
    $ uv run python -m scaffold_kit.main init [options]
    $ uv run python -m scaffold_kit.main scaffold [options]
    $ uv run python -m scaffold_kit.main checklist
    $ uv run python -m scaffold_kit.main tree [options]
    $ uv run python -m scaffold_kit.main --help

    During development:
    $ uv run scaffold-kit init [options]
    $ uv run scaffold-kit scaffold [options]
    $ uv run scaffold-kit checklist
    $ uv run scaffold-kit tree [options]
    $ uv run scaffold-kit --help

    After installation:
    $ scaffold-kit init [options]
    $ scaffold-kit scaffold [options]
    $ scaffold-kit checklist
    $ scaffold-kit tree [options]
    $ scaffold-kit --help
"""

from __future__ import annotations

import sys
import argparse

from typing import NoReturn

from scaffold_kit import __description__, __title__, __url__, __version__
from scaffold_kit.checklist import generate_checklist
from scaffold_kit.config import (
    CHECKLIST_DIRECTORY,
    CHECKLIST_FILE,
    IGNORE_FILE,
    SCAFFOLD_FILE,
    TREE_DIRECTORY,
    TREE_FILE,
)
from scaffold_kit.init import init_project
from scaffold_kit.scaffold import scaffold_project
from scaffold_kit.tree import generate_tree


def create_parser() -> argparse.ArgumentParser:
    """Creates and configures the main argument parser with subcommands.

    Returns:
        Configured ArgumentParser with subcommands for scaffold, checklist, and
        tree.
    """
    parser = argparse.ArgumentParser(
        prog=__title__,
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{__title__} {__version__}",
    )

    # Create subparsers for each command
    subparsers = parser.add_subparsers(
        dest="command",
        title="available commands",
        description="Choose a command to run",
        help=f"Run '{__title__} <command> --help' for command-specific help",
        metavar="<command>",
    )

    # Init subcommand
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new project by copying example files",
        description="Initialize a new project by copying example files.",
    )
    # 2. Add the optional target argument.
    init_parser.add_argument(
        "target",
        type=str,
        nargs="?",
        choices=["ignore-file", "config-file", "scaffold-file"],
        help="Target file to copy (optional). "
        "If not provided, all files will be copied.",
    )

    # Scaffold subcommand
    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="Create project structure from a structured data file",
        description=(
            "Creates a project structure from a YAML or JSON file definition. "
            "Supports creating top-level root folders and nested structures."
        ),
    )
    scaffold_parser.add_argument(
        "-r",
        "--root",
        action="store_true",
        default=False,
        help="Create the root folder defined in the structured data file",
    )

    # Checklist subcommand
    _checklist_parser = subparsers.add_parser(
        "checklist",
        help="Generate a checklist of files in the current directory",
        description=(
            "Scans the current directory and creates a text-based checklist "
            "of all files, marking them as complete [x] or incomplete [ ] "
            "based on content."
        ),
    )

    # Tree subcommand
    tree_parser = subparsers.add_parser(
        "tree",
        help="Generate a hierarchical tree representation of a directory",
        description=(
            "Generates an ASCII tree diagram of directory structure, "
            "respecting ignore patterns and supporting partial trees."
        ),
    )
    tree_parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    tree_parser.add_argument(
        "--ignore-file",
        default=IGNORE_FILE,
        help=f"Ignore file to use (default: {IGNORE_FILE})",
    )

    return parser


def main() -> NoReturn:
    """Main entry point for the scaffold-kit CLI.

    Parses command-line arguments and dispatches to the appropriate subcommand.
    Exits with status code 0 on success, 1 on error, or 2 on invalid arguments.
    """
    parser = create_parser()
    args = parser.parse_args()

    # If no subcommand provided, show help and exit.
    if not args.command:
        parser.print_help()
        sys.exit(2)

    try:
        # Dispatch to appropriate subcommand using core functions.
        if args.command == "init":
            exit_code = init_project(args.target)
            sys.exit(exit_code)

        elif args.command == "scaffold":
            scaffold_project(root=args.root, scaffold_file=SCAFFOLD_FILE)

        elif args.command == "checklist":
            generate_checklist(
                ignore_file=IGNORE_FILE,
                output_file=CHECKLIST_FILE,
                output_dir=CHECKLIST_DIRECTORY,
            )

        elif args.command == "tree":
            generate_tree(
                root_dir=args.root_dir,
                ignore_file=args.ignore_file,
                output_file=TREE_FILE,
                output_dir=TREE_DIRECTORY,
            )

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
