"""Creates project structure from a structured data file.

This module provides the core logic for the scaffolding utility. It can read a
project structure definition from a YAML or JSON file and create the
corresponding folders and files in the current working directory. It handles
common use cases like root-level project folders, nested structures, and
skipping existing files.

Usage:
    To run this script, navigate to your project's root directory or parent
    directory and execute it as a module:

    # Generate from project's root directory:
    $ uv run python -m scaffold_kit.scaffold

    # Generate project's parent directory:
    $ uv run python -m scaffold_kit.scaffold --root
"""

from __future__ import annotations

import os
import json
import argparse

from typing import Any

import yaml

from scaffold_kit.config import (
    SCAFFOLD_FILE,
)


def read_structure_file(scaffold_file: str) -> dict[str, Any]:
    """Reads a project structure file and returns its content.

    This function attempts to load a project structure definition from either
    a YAML or JSON file. It prioritizes the file extension provided, but will
    raise an error if the file is not found.

    Args:
        scaffold_file: The name of the file to read (e.g., 'scaffold.yaml').

    Returns:
        The content of the file as a dictionary.

    Raises:
        ValueError: If a found file has invalid YAML or JSON syntax.
        FileNotFoundError: If the specified `scaffold_file` is not found
            in the current working directory.
    """
    is_yaml = False
    is_json = False

    # 1. Check file extension to determine format.
    if scaffold_file.endswith((".json")):
        is_json = True
    else:
        is_yaml = True

    # 2. Attempt to read and parse the YAML file.
    if is_yaml and os.path.exists(scaffold_file):
        print(f"Found '{scaffold_file}'. Reading file...")
        try:
            with open(scaffold_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(
                f"Error parsing YAML file '{scaffold_file}': {e}"
            ) from e

    # 3. Attempt to read and parse the JSON file.
    if is_json and os.path.exists(scaffold_file):
        print(f"Found '{scaffold_file}'. Reading file...")
        try:
            with open(scaffold_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error decoding JSON file '{scaffold_file}': {e}"
            ) from e

    # 4. Raise error if the file was not found.
    raise FileNotFoundError(
        f"Error: '{scaffold_file}' was not found in the current directory."
    )


def scaffold_project(
    root: bool = False, scaffold_file: str = "scaffold.yaml"
) -> dict[str, Any]:
    """Creates a project structure from a structured data file.

    This function reads a project structure definition from a YAML or JSON
    file and creates the corresponding folders and files. It supports
    creating a top-level root folder and recursively creating nested files
    and directories.

    Args:
        root: If True, creates the top-level folder defined in the structure
            file. If False, it scaffolds the contents directly in the current
            directory.
        scaffold_file: The path to the project structure definition file.

    Returns:
        The parsed data from the structure file as a dictionary.

    Raises:
        OSError: If a file or directory cannot be created due to permissions.
        ValueError: If a found file is not valid YAML or JSON.
        FileNotFoundError: If the specified file is not found.
    """
    data: dict[str, Any] = read_structure_file(scaffold_file)
    name = data.get("name")
    children = data.get("children", [])

    # 1. Handle the creation of the top-level root folder.
    if root and name:
        if not os.path.exists(name):
            try:
                os.makedirs(name)
                print(f"Created folder: {name}")
            except OSError as e:
                raise OSError(
                    f"Permission denied: Unable to create folder '{name}'."
                ) from e
        else:
            print(f"Folder '{name}' already exists. Skipping.")
        base_path = name
    else:
        base_path = ""

    def create_structure(items: list[dict], path: str):
        """Recursively creates folders and files based on the structure.

        Args:
            items: A list of dictionaries, where each dictionary represents
                a folder or file.
            path: The base path where the items should be created.
        """
        for item in items:
            item_name = item.get("name")
            item_type = item.get("type", "folder")

            # Skip malformed entries without a name.
            if item_name is None:
                continue

            item_path = os.path.join(path, item_name)

            # Check if the item already exists to avoid overwriting.
            if os.path.exists(item_path):
                print(f"Found existing {item_type}: {item_path}")
                # Recursively create children for existing folders.
                if item_type == "folder" and "children" in item:
                    create_structure(item["children"], item_path)
                continue

            # Create the folder or file.
            try:
                if item_type == "folder":
                    os.makedirs(item_path)
                    print(f"Created folder: {item_path}")
                    if "children" in item:
                        create_structure(item["children"], item_path)
                elif item_type == "file":
                    with open(item_path, "w", encoding="utf-8") as _:
                        pass
                    print(f"Created file: {item_path}")
            except OSError as e:
                raise OSError(
                    f"Permission denied: Unable to create '{item_path}'."
                ) from e

    # 2. Start the recursive creation process if children are defined.
    if children:
        create_structure(children, base_path)

    return data


def main():
    """Main entry point to run the scaffolding process.

    Parses command-line arguments and runs the scaffolding process.
    """
    # 1. Create the argument parser.
    parser = argparse.ArgumentParser(
        description="Scaffold a project from a structured data file."
    )
    # 2. Add the --root argument.
    parser.add_argument(
        "-r",
        "--root",
        action="store_true",
        default=False,
        help="Create the root folder defined in the structured data file.",
    )
    args = parser.parse_args()

    # 3. Call the main scaffolding function with parsed arguments.
    scaffold_project(root=args.root, scaffold_file=SCAFFOLD_FILE)


if __name__ == "__main__":
    main()
