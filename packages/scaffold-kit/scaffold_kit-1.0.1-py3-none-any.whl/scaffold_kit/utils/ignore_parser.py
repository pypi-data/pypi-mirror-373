"""Parses and applies .gitignore-style ignore rules to filesystem paths.

This module provides a robust, two-class system for handling file exclusion
patterns. The `IgnoreRule` class interprets a single pattern line, converting it
to a regular expression. The `IgnoreParser` class then reads and manages a
collection of these rules, using them to filter lists of files or to check
individual paths.

Demo:
    To run the module's demonstration code, use the following command:

    $ uv run python -m scaffold_kit.utils.ignore_parser
"""

from __future__ import annotations

import re

from pathlib import Path
from typing import Iterator

from scaffold_kit.utils.pattern_processor import PatternProcessor


class IgnoreRule:
    """Represents a single ignore pattern and its regex equivalent.

    This class handles the conversion of a .gitignore-style pattern string
    into a compiled regular expression, managing pattern nuances like
    negation and directory-only rules.
    """

    def __init__(
        self,
        pattern: str,
        regex: re.Pattern[str],
        negated: bool = False,
        dir_only: bool = False,
    ):
        """Initializes an IgnoreRule instance.

        Args:
            pattern: The original, raw pattern string.
            regex: The compiled regex pattern.
            negated: True if the rule is a negation (starts with '!').
            dir_only: True if the rule is for directories only (ends with '/').
        """
        self.pattern = pattern
        self.regex = regex
        self.negated = negated
        self.dir_only = dir_only

    @staticmethod
    def _pattern_to_regex(pattern: str) -> str:
        """Converts a glob pattern to a regex string.

        This method uses a `PatternProcessor` to handle the conversion
        logic, ensuring consistency with glob-to-regex standards.

        Args:
            pattern: The glob pattern string to convert.

        Returns:
            The regex equivalent of the pattern.
        """
        processor = PatternProcessor()
        return processor.pattern_to_regex(pattern)

    @classmethod
    def from_pattern(cls, pattern: str) -> "IgnoreRule":
        """Creates an IgnoreRule from a raw ignore pattern string.

        This factory method parses the input string to determine its properties
        (negation, directory-only) before converting it to a regex.

        Args:
            pattern: The raw ignore pattern (e.g., 'logs/', '!.gitkeep').

        Returns:
            A new `IgnoreRule` instance.
        """
        original_pattern = pattern

        # 1. Check for negation and strip '!' if present.
        negated = pattern.startswith("!")
        if negated:
            pattern = pattern[1:]

        # 2. Check for directory-only rule and strip '/' if present.
        dir_only = pattern.endswith("/")
        if dir_only:
            pattern = pattern[:-1]

        # 3. Convert the cleaned pattern to a regex string.
        regex_str = cls._pattern_to_regex(pattern)

        # 4. Modify the regex to handle directory-only patterns.
        if dir_only:
            # Replaces the final '$' anchor with a group that matches
            # either the directory name or its contents.
            regex_str = regex_str[:-1] + "(?:/.*)?$"

        return cls(
            pattern=original_pattern,
            regex=re.compile(regex_str),
            negated=negated,
            dir_only=dir_only,
        )

    def matches(self, path: str, is_dir: bool = False) -> bool:
        """Checks if the given path matches this ignore rule.

        This method uses the rule's compiled regex to check for a match and
        applies additional logic for directory-only rules.

        Args:
            path: The path string to check.
            is_dir: True if the path represents a directory.

        Returns:
            True if the path matches the rule, False otherwise.
        """
        match = self.regex.match(path)
        if not match:
            return False

        # If a path matches a dir-only rule, but is not a directory itself
        # (and isn't the directory's name), it's not a valid match.
        if self.dir_only and not is_dir and path == self.pattern.strip("/"):
            return False

        return True


class IgnoreParser:
    """Parses and applies ignore rules to filesystem paths.

    This class provides methods to load rules from files or strings,
    and to apply those rules to filter lists of paths or check
    individual paths for ignored status.
    """

    def __init__(self, base_path: str | Path | None = None) -> None:
        """Initializes the IgnoreParser.

        Args:
            base_path: The root path to which relative patterns are anchored.
                If not provided, the parser will handle paths as they are.
        """
        self.base_path = Path(base_path).resolve() if base_path else None
        self.rules: list[IgnoreRule] = []

    @staticmethod
    def _normalize_path(path: str | Path) -> str:
        """Normalizes a path to use forward slashes.

        This ensures that path patterns work consistently across different
        operating systems (e.g., Windows and Linux).

        Args:
            path: The path string or `Path` object to normalize.

        Returns:
            The normalized path string with forward slashes.
        """
        return str(Path(path).as_posix())

    def _rel_to_base(self, path: str | Path) -> str:
        """Returns a path relative to the base path if one is set.

        Args:
            path: The path string or `Path` object.

        Returns:
            A string representing the path relative to the `base_path`,
            or the original absolute path if a base path is not set.
        """
        p = Path(path)
        if self.base_path:
            try:
                # Get path relative to the base_path
                if p.is_absolute():
                    return str(p.relative_to(self.base_path))
                # For non-absolute paths, simply convert to string
                return str(p)
            except ValueError:
                # If the path is not a descendant of the base path
                return str(p.absolute())
        return str(p)

    @classmethod
    def from_file(
        cls, file_path: str | Path, base_path: str | Path | None = None
    ) -> IgnoreParser:
        """Loads ignore rules from a file.

        Args:
            file_path: The path to the ignore file (e.g., '.gitignore').
            base_path: The base path for relative rules. Defaults to the
                directory of the `file_path`.

        Returns:
            A new `IgnoreParser` instance with the loaded rules.
        """
        parser = cls(base_path=base_path or Path(file_path).parent)
        with open(file_path, encoding="utf-8") as f:
            parser.add_lines(f)
        return parser

    @classmethod
    def from_string(
        cls, rules: str, base_path: str | Path | None = None
    ) -> IgnoreParser:
        """Loads ignore rules from a string.

        Args:
            rules: A string containing newline-separated ignore patterns.
            base_path: The base path for relative rules.

        Returns:
            A new `IgnoreParser` instance with the loaded rules.
        """
        parser = cls(base_path=base_path)
        parser.add_lines(rules.splitlines())
        return parser

    def add_lines(self, lines: Iterator[str]) -> None:
        """Parses and adds ignore rules from an iterable of lines.

        Args:
            lines: An iterable of strings, such as from an open file or
                `str.splitlines()`.
        """
        for line in lines:
            line = line.strip()
            # Ignore empty lines and comments.
            if not line or line.startswith("#"):
                continue
            self.add_rule(line)

    def add_rule(self, pattern: str) -> None:
        """Adds a single ignore rule.

        Args:
            pattern: The pattern string to add.
        """
        self.rules.append(IgnoreRule.from_pattern(pattern))

    def matches(self, path: str | Path, is_dir: bool = False) -> bool:
        """Checks if a path is ignored by the rules.

        The method returns the result of the last matching rule, where a
        negated rule overrides a regular one.

        Args:
            path: The path string or `Path` object to check.
            is_dir: Optional flag to indicate if the path is a directory.

        Returns:
            True if the path is ignored, False otherwise.
        """
        # 1. Normalize the path relative to the base path.
        p = Path(path)
        norm = self._normalize_path(self._rel_to_base(p))

        matched = False
        # 2. Iterate through all rules, as the last matching rule wins.
        for rule in self.rules:
            # Check if the current rule matches the path.
            if rule.matches(norm, is_dir or p.is_dir()):
                # A match is an "ignored" decision unless the rule is negated.
                matched = not rule.negated
        return matched

    def filter(self, paths: list[str | Path]) -> list[str]:
        """Returns only the paths that are not ignored by the rules.

        Args:
            paths: A list of path strings or `Path` objects.

        Returns:
            A new list containing only the paths that are not ignored.
        """
        return [str(p) for p in paths if not self.matches(p)]

    def explain(self, path: str | Path, is_dir: bool = False) -> list[str]:
        """Returns a list of all rules that apply to a path.

        This method is useful for debugging as it shows every rule that
        matches the given path and its resulting decision.

        Args:
            path: The path string or `Path` object to explain.
            is_dir: Optional flag to indicate if the path is a directory.

        Returns:
            A list of strings, each explaining a matching rule and its
            outcome.
        """
        p = Path(path)
        norm = self._normalize_path(self._rel_to_base(p))
        explanations = []
        for rule in self.rules:
            if rule.matches(norm, is_dir or p.is_dir()):
                explanations.append(
                    f"Rule '{rule.pattern}' "
                    f"({'negated' if rule.negated else 'applied'}) -> "
                    f"Decision: {'ignored' if not rule.negated else 'kept'}"
                )
        return explanations


if __name__ == "__main__":
    import os
    import glob

    # IGNORE_FILE = ".gitignore"
    IGNORE_FILE = ".scaffoldignore"

    # Fallback for when the script is run in a directory without a .gitignore
    if not os.path.exists(IGNORE_FILE):
        print(
            f"'{IGNORE_FILE}' not found. Creating a sample one for "
            "demonstration."
        )
        with open(IGNORE_FILE, "w", encoding="utf-8") as f:
            f.write("*.log\n")
            f.write("build/\n")
            f.write(".venv/\n")
            f.write("!important.log\n")
        # Create dummy files for demonstration
        os.makedirs("build", exist_ok=True)
        # pylint: disable=consider-using-with
        open("app.log", "w", encoding="utf-8").close()
        open("important.log", "w", encoding="utf-8").close()
        open("main.py", "w", encoding="utf-8").close()

    parser = IgnoreParser.from_file(IGNORE_FILE)
    # pylint: disable=unexpected-keyword-arg
    files = glob.glob("**/*", recursive=True, include_hidden=True)

    print("\nIgnored files")
    print("=" * 60)

    ignored_files = []
    for f in files:
        if parser.matches(f):
            ignored_files.append(f)
            print(f" - {f:40} -> {parser.explain(f)}")

    print("-" * 60)
    print(f"Total ignored: {len(ignored_files)}\n")

    print("\nKept (filtered) files")
    print("=" * 60)

    filtered = parser.filter(files)
    for f in filtered:
        print(f" - {f}")

    print("-" * 60)
    print(f"Total kept: {len(filtered)}\n")
