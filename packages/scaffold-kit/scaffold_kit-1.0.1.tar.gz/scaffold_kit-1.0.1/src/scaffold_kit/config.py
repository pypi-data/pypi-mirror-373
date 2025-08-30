"""Provides utilities for locating and loading configuration files.

This module searches for a configuration file in the current directory,
supporting multiple names and formats (YAML and JSON). It then loads the
first file found and uses the values to set a series of module-level
constants, providing sensible defaults if the file or specific keys are
not found.

Demo:
    To run the module's demonstration code, use the following command:

    $ uv run python -m scaffold_kit.config
"""

from __future__ import annotations

import json

from pathlib import Path

import yaml


def find_config_file() -> str | None:
    """Searches for a configuration file in the current directory.

    The function checks for a predefined list of filenames in a specific
    order to locate a configuration file.

    Returns:
        The path to the first configuration file found, or None if no
        file is found.
    """
    candidates = [
        ".scaffoldkitrc.yaml",
        "scaffoldkitrc.yaml",
        ".scaffoldkitrc",
        ".scaffoldkitrc.json",
        "scaffoldkitrc.json",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def load_config(file_path: str) -> dict:
    """Loads configuration from a given file path.

    Args:
        file_path: The path to the configuration file.

    Returns:
        A dictionary containing the loaded configuration data.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        if file_path.endswith((".json")):
            return json.load(f)

        return yaml.safe_load(f) or {}
    return {}


# 1. Find and load the configuration file.
config_file = find_config_file()
config = {}
if config_file:
    config = load_config(config_file)

# 2. Define constants using loaded config values or fallbacks.
SCAFFOLD_FILE = config.get("scaffold_file", "scaffold.yaml")
"""Constant signifying scaffold file config."""  # pylint: disable=W0105

IGNORE_FILE = config.get("ignore_file", ".scaffoldignore")
"""Constant signifying ignore file config."""  # pylint: disable=W0105

CHECKLIST_DIRECTORY = config.get("checklist_directory", ".")
"""Constant signifying checklist directory config."""  # pylint: disable=W0105

CHECKLIST_FILE = config.get("checklist_file", "empty-files-checklist.txt")
"""Constant signifying checklist file config."""  # pylint: disable=W0105

TREE_DIRECTORY = config.get("tree_directory", ".")
"""Constant signifying tree directory config."""  # pylint: disable=W0105

TREE_FILE = config.get("tree_file", "tree.txt")
"""Constant signifying tree file config."""  # pylint: disable=W0105

if __name__ == "__main__":
    constant_nested_list = [
        ["SCAFFOLD_FILE", SCAFFOLD_FILE],
        ["IGNORE_FILE", IGNORE_FILE],
        ["CHECKLIST_DIRECTORY", CHECKLIST_DIRECTORY],
        ["CHECKLIST_FILE", CHECKLIST_FILE],
        ["TREE_DIRECTORY", TREE_DIRECTORY],
        ["TREE_FILE", TREE_FILE],
    ]
    config_list = [[key, value] for key, value in config.items()]
    for key, value in config_list:
        print(f"{key}: {value}")
