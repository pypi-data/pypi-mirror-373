"""Converts glob-like patterns to regular expressions.

This module provides classes for processing .gitignore-style glob patterns
and converting them into equivalent regular expressions. It uses a
handler-based, "strategy" pattern to process different types of characters
(e.g., wildcards, character classes, literals) and handles complex rules
like recursive wildcards and root-anchored patterns.

Demo:
    To run the module's demonstration code, use the following command:

    $ uv run python -m scaffold_kit.utils.pattern_processor
"""

from __future__ import annotations

import re

from abc import ABC, abstractmethod
from typing import Tuple


class CharacterHandler(ABC):
    """Abstract base class for character handlers.

    Character handlers define the logic for converting a specific type of
    pattern character into its regex equivalent.
    """

    @abstractmethod
    def can_handle(self, char: str) -> bool:
        """Checks if this handler can process the given character.

        Args:
            char: The single character to check.

        Returns:
            True if the handler can process the character, False otherwise.
        """
        pass

    @abstractmethod
    def handle(self, text: str, position: int) -> Tuple[str, int]:
        """Handles the character at the given position.

        Args:
            text: The full text being processed.
            position: Current position in the text.

        Returns:
            A tuple containing:
                - The replacement string for the character(s).
                - The new position in the text after processing.
        """
        pass


class WildcardHandler(CharacterHandler):
    """Handles '*' wildcard characters.

    Converts a single '*' glob character into its regex equivalent.
    """

    def can_handle(self, char: str) -> bool:
        """Checks if the character is a '*'.

        Args:
            char: The single character to check.

        Returns:
            True if the character is a wildcard, False otherwise.
        """
        return char == "*"

    def handle(self, text: str, position: int) -> Tuple[str, int]:
        """Converts '*' to '[^/]*'.

        Args:
            text: The full text being processed.
            position: Current position in the text.

        Returns:
            A tuple of the replacement regex and the new position.
        """
        return "[^/]*", position + 1


class SingleCharHandler(CharacterHandler):
    """Handles '?' single character wildcards.

    Converts a single '?' glob character into its regex equivalent.
    """

    def can_handle(self, char: str) -> bool:
        """Checks if the character is a '?'.

        Args:
            char: The single character to check.

        Returns:
            True if the character is a single-char wildcard, False otherwise.
        """
        return char == "?"

    def handle(self, text: str, position: int) -> Tuple[str, int]:
        """Converts '?' to '[^/]'.

        Args:
            text: The full text being processed.
            position: Current position in the text.

        Returns:
            A tuple of the replacement regex and the new position.
        """
        return "[^/]", position + 1


class CharacterClassHandler(CharacterHandler):
    """Handles '[...]' character classes.

    Captures the entire character class including its content and closing
    bracket.
    """

    def can_handle(self, char: str) -> bool:
        """Checks if the character is a '['.

        Args:
            char: The single character to check.

        Returns:
            True if the character is a character class, False otherwise.
        """
        return char == "["

    def handle(self, text: str, position: int) -> Tuple[str, int]:
        """Extracts the entire character class from the text.

        Args:
            text: The full text being processed.
            position: Current position in the text.

        Returns:
            A tuple containing:
                - The regex string for the character class.
                - The new position in the text after processing.
        """
        start = position
        i = position + 1  # Skip opening '['.

        # Handle negation characters.
        if i < len(text) and text[i] in ("!", "^"):
            i += 1

        # Handle immediate closing bracket.
        if i < len(text) and text[i] == "]":
            i += 1

        # Find the closing bracket.
        while i < len(text) and text[i] != "]":
            i += 1

        if i < len(text):  # Found closing bracket.
            return text[start : i + 1], i + 1
        # No closing bracket found, treat as literal.
        return re.escape("["), position + 1


class LiteralCharHandler(CharacterHandler):
    """Handles literal characters (default handler).

    Converts a literal character to a regex-escaped string.
    """

    def can_handle(self, char: str) -> bool:
        """Checks if this is the fallback handler.

        This is the fallback handler, so it can handle any character.

        Args:
            char: The single character to check.

        Returns:
            True.
        """
        return True

    def handle(self, text: str, position: int) -> Tuple[str, int]:
        """Escapes a single literal character for regex.

        Args:
            text: The full text being processed.
            position: Current position in the text.

        Returns:
            A tuple of the escaped character and the new position.
        """
        return re.escape(text[position]), position + 1


class GlobProcessor:
    """Processes glob patterns using the strategy pattern.

    This class iterates through a glob string, applying the appropriate
    CharacterHandler to each character to build a regex string part.
    """

    def __init__(self):
        """Initializes the GlobProcessor with a list of handlers.

        Note that the order of the handlers is crucial. More specific handlers
        (e.g., wildcards, character classes) must come before the generic
        fallback handler (LiteralCharHandler).
        """
        # Order matters! More specific handlers should come first.
        self.handlers = [
            WildcardHandler(),
            SingleCharHandler(),
            CharacterClassHandler(),
            LiteralCharHandler(),  # Fallback handler - must be last.
        ]

    def convert_glob_part(self, part: str) -> str:
        """Converts a single glob part to regex using character handlers.

        Args:
            part: A single string part of a glob pattern
                (e.g., 'path', '*', '**').

        Returns:
            The regex equivalent of the glob part.
        """
        # 1. Handle recursive wildcard special case.
        if part == "**":
            return ".*"

        result = ""
        position = 0

        while position < len(part):
            char = part[position]

            # 2. Find the first handler that can process this character.
            handler = self._find_handler(char)
            replacement, new_position = handler.handle(part, position)

            result += replacement
            position = new_position

        return result

    def _find_handler(self, char: str) -> CharacterHandler:
        """Finds the appropriate handler for the given character.

        Args:
            char: The single character to find a handler for.

        Returns:
            The first matching `CharacterHandler` instance.

        Raises:
            RuntimeError: If no handler is found for the given character.
                This should not happen if LiteralCharHandler is present.
        """
        for handler in self.handlers:
            if handler.can_handle(char):
                return handler

        # This should never happen since LiteralCharHandler handles everything.
        raise RuntimeError(f"No handler found for character: {char}")


class PatternProcessor:
    """Main class for converting glob patterns to regex.

    This class orchestrates the entire conversion process, handling
    normalization, splitting, and joining of the regex parts.
    """

    def __init__(self):
        """Initializes the processor with a GlobProcessor instance."""
        self.glob_processor = GlobProcessor()

    def pattern_to_regex(self, pattern: str) -> str:
        """Converts a .gitignore-style glob pattern to a regex.

        Args:
            pattern: The glob pattern string to convert.

        Returns:
            The complete, anchored regular expression string.
        """
        # 1. Normalize the pattern.
        normalized_pattern = self._normalize_pattern(pattern)

        # 2. Split into parts and convert each part.
        parts = normalized_pattern.split("/")
        regex_parts = [
            self.glob_processor.convert_glob_part(part) for part in parts
        ]

        # 3. Join the parts with appropriate separators.
        joined_regex = self._join_regex_parts(regex_parts)

        # 4. Add anchors.
        return f"^{joined_regex}$"

    def _normalize_pattern(self, pattern: str) -> str:
        """Applies initial pattern transformations.

        Args:
            pattern: The glob pattern string.

        Returns:
            The normalized pattern string.
        """
        # If a pattern has no slashes, it is treated as if it were
        # preceded by '**/'.
        if "/" not in pattern:
            pattern = f"**/{pattern}"

        # If a pattern starts with a slash, it is anchored to the project root.
        if pattern.startswith("/"):
            pattern = pattern[1:]

        return pattern

    def _join_regex_parts(self, regex_parts: list[str]) -> str:
        """Joins regex parts with appropriate separators.

        Args:
            regex_parts: A list of regex strings to join.

        Returns:
            The joined regex string.
        """
        if not regex_parts:
            return ""

        result = regex_parts[0]

        for i in range(1, len(regex_parts)):
            prev_part = regex_parts[i - 1]
            curr_part = regex_parts[i]

            # Add separator unless dealing with '.*' parts.
            if prev_part != ".*" and curr_part != ".*":
                result += "/"

            result += curr_part

        return result


if __name__ == "__main__":
    processor = PatternProcessor()

    pattern_nested_list = [
        ["*.py", "Simple wildcard"],
        ["test?.txt", "Single char wildcard"],
        ["**/*.log", "Recursive wildcard"],
        ["build/", "Directory pattern"],
        ["/root-only", "Root-anchored pattern"],
        ["test[0-9].txt", "Character class"],
        ["file[!a-c].dat", "Negated character class"],
        ["path/*/sub", "Wildcard in middle"],
        ["no-special-chars", "Literal pattern"],
        ["a*b?c[def]g", "Multiple wildcards"],
        ["**", "Just recursive wildcard"],
        ["[abc]", "Just character class"],
        ["[]broken", "Malformed character class"],
    ]

    pattern_list = [item[0] for item in pattern_nested_list]
    description_list = [item[1] for item in pattern_nested_list]
    regex_list = [
        [pattern, processor.pattern_to_regex(pattern)]
        for pattern in pattern_list
    ]

    print("\n=== pattern_to_regex ===\n")
    for key, value in regex_list:
        print(f"{key}: {value}")
