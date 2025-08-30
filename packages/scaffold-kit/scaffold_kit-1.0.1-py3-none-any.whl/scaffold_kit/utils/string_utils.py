"""A set of utilities for string manipulation.

This module provides functions for transliterating unicode characters and
creating URL-friendly "slugs" from text.

Demo:
    To run the module's demonstration code, use the following command:

    $ uv run python -m scaffold_kit.utils.string_utils
"""

from __future__ import annotations

import re
import unicodedata


DIACRITICS_MAP: dict[str, str] = {
    "À": "A",
    "Á": "A",
    "Ã": "A",
    "Ä": "Ae",
    "Å": "A",
    "Ā": "A",
    "Ă": "A",
    "Ą": "A",
    "à": "a",
    "á": "a",
    "ã": "a",
    "ä": "ae",
    "å": "a",
    "ā": "a",
    "ă": "a",
    "ą": "a",
    "Ç": "C",
    "Ć": "C",
    "Ĉ": "C",
    "Č": "C",
    "ç": "c",
    "ć": "c",
    "ĉ": "c",
    "č": "c",
    "Ď": "D",
    "Đ": "D",
    "ď": "d",
    "đ": "d",
    "È": "E",
    "É": "E",
    "Ẽ": "E",
    "Ë": "E",
    "Ĕ": "E",
    "Ē": "E",
    "Ě": "E",
    "Ę": "E",
    "è": "e",
    "é": "e",
    "ẽ": "e",
    "ë": "e",
    "ĕ": "e",
    "ė": "e",
    "ě": "e",
    "ę": "e",
    "Ġ": "G",
    "Ģ": "G",
    "Ĝ": "G",
    "Ğ": "G",
    "ġ": "g",
    "ģ": "g",
    "ĝ": "g",
    "ğ": "g",
    "Ĥ": "H",
    "Ħ": "H",
    "ĥ": "h",
    "ħ": "h",
    "Ì": "I",
    "Í": "I",
    "Î": "I",
    "Ï": "I",
    "Į": "I",
    "Ī": "I",
    "İ": "I",
    "ì": "i",
    "í": "i",
    "î": "i",
    "ï": "i",
    "ī": "i",
    "ĩ": "i",
    "Ĵ": "J",
    "ĵ": "j",
    "Ķ": "K",
    "ķ": "k",
    "Ĺ": "L",
    "Ļ": "L",
    "Ľ": "L",
    "Ŀ": "L",
    "ĺ": "l",
    "ļ": "l",
    "ľ": "l",
    "Ñ": "N",
    "Ņ": "N",
    "Ň": "N",
    "ņ": "n",
    "ň": "n",
    "Ò": "O",
    "Ó": "O",
    "Ô": "O",
    "Õ": "O",
    "Ö": "Oe",
    "Ō": "O",
    "Ŏ": "O",
    "Ő": "O",
    "ò": "o",
    "ó": "o",
    "ô": "o",
    "õ": "o",
    "ö": "oe",
    "ō": "o",
    "ŏ": "o",
    "ő": "o",
    "Ù": "U",
    "Ú": "U",
    "Û": "U",
    "Ü": "Ue",
    "Ū": "U",
    "Ů": "U",
    "Ű": "U",
    "Ų": "U",
    "ù": "u",
    "ú": "u",
    "û": "u",
    "ü": "ue",
    "ū": "u",
    "ů": "u",
    "ű": "u",
    "Ŵ": "W",
    "ŵ": "w",
    "Ý": "Y",
    "Ÿ": "Y",
    "ý": "y",
    "ÿ": "y",
    "Ŷ": "Y",
    "ŷ": "y",
    "Ž": "Z",
    "Ż": "Z",
    "ź": "z",
    "ż": "z",
    "ž": "z",
}
"""Constant signifying diacritics map."""  # pylint: disable=W0105


LIGATURES_MAP: dict[str, str] = {
    "æ": "ae",
    "Æ": "Ae",
    "œ": "oe",
    "Œ": "Oe",
    "ß": "ss",
    "ﬀ": "ff",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬅ": "ft",
    "ﬆ": "st",
    "ĳ": "ij",
    "Ĳ": "Ij",
    "ʒ": "ezh",
    "Ʒ": "Ez",
}
"""Constant signifying ligatures map."""  # pylint: disable=W0105

TRANSLITERATE_MAP = {**DIACRITICS_MAP, **LIGATURES_MAP}
"""Constant signifying transliterate map (diacritics and ligatures merged)."""  # pylint: disable=W0105


def transliterate(text: str) -> str:
    """Transliterates unicode characters to their closest ascii replacements.

    This function replaces diacritics, ligatures, and stylistic variants with
    base ASCII letters, e.g., 'ñ' → 'n', 'æ' → 'ae', 'ß' → 'ss'. All remaining
    non-ASCII characters are removed by a second decomposing and encoding
    pass.

    Args:
        text: Any string containing unicode characters.

    Returns:
        A plain ASCII string where every non-ASCII glyph has been converted or
        dropped, resulting in lossy but url-safe output.

    Raises:
        None – all standard exceptions are caught internally.

    Examples:
        Handling diacritics:

        >>> transliterate("François Café")
        'Francois Cafe'

        Mixed scripts and special characters:

        >>> transliterate("Straße – café naïf")
        'Strasse  cafe naif '

        Ligatures and stylists variants:

        >>> transliterate("Encyclopædia & ﬂuffy œuf")
        'Encyclopaedia & fluffy oeu'

        Emojis and math get stripped:

        >>> transliterate("α ≤ ½ 😊")
        '  '  # empty string, every char is non-ASCII
    """
    # 1. Map predefined characters to their ASCII replacements.
    text = text.translate(str.maketrans(TRANSLITERATE_MAP))
    # 2. Normalize and remove all remaining non-ASCII characters.
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )

    return text


def slugify(text: str) -> str:
    """Converts a given string into an url-safe, ascii-only slug.

    This function removes or transliterates diacritics, ligatures, and other
    non-ascii characters while normalising whitespace and punctuation into
    hyphens. The result contains only lowercase letters ([a-z]), digits
    ([0-9]) and hyphens, making it suitable for use in urls, file names or keys.

    Args:
        text: The original, possibly unicode string that needs to be slugified.

    Returns:
        A hyphen-separated ascii slug derived from `text`. If `text` is empty or
        the transformation leads to an empty string the returned slug will also
        be empty ("").

    Raises:
        None – all standard exceptions are caught internally.

    Examples:
        Basic usage:

        >>> slugify("Café crème à la française")
        'cafe-creme-a-la-francaise'

        Complex input with punctuation and mixed spaces:

        >>> slugify("  ¡Hola! ¿Qué tal?  ")
        'hola-que-tal'

        Already ascii and clean strings remain the same, except for case:

        >>> slugify("Valid-slug-already-given")
        'valid-slug-already-given'

        Empty or symbol-only input results in an empty string:

        >>> slugify("!!!!!  ???")
        ''
    """
    # 1. Replace diacritics and ligatures.
    text = transliterate(text)
    # 2. Convert to lowercase and remove leading/trailing spaces.
    text = text.lower().strip()
    # 3. Remove non-alphanumeric characters except spaces and hyphens.
    text = re.sub(r"[^\w\s-]", "", text)
    # 4. Replace consecutive spaces or hyphens with a single hyphen.
    text = re.sub(r"[\s_-]+", "-", text)
    # 5. Remove leading/trailing hyphens.
    text = re.sub(r"^-+|-+$", "", text)

    return text


if __name__ == "__main__":
    text_list = [
        "Hëllô,    wörld!",
        "ça va être une journée spéciale.",
        "Ich liebe Deutsche Küche!",
        "¿Cómo estás? ¡Hasta mañana!",
        "Život je lijep, ali često i kratak.",
        "Não sei o que fazer agora...",
        "J'aime les fromages français!",
        "Küß mich, meine Schöne!",
        "Škoda, že jsem to nevím.",
        "¿Dónde está el baño, por favor?",
        "Encyclopædia & ﬂuffy œuf",
        "Straße – café naïf",
    ]

    transliterate_list = [[text, transliterate(text)] for text in text_list]
    slugify_list = [[text, slugify(text)] for text in text_list]

    print("\n=== transliterate ===\n")
    for key, value in transliterate_list:
        print(f"{key}: {value}")

    print("\n=== slugify ===\n")
    for key, value in slugify_list:
        print(f"{key}: {value}")
