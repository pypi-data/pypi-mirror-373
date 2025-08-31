# SPDX-License-Identifier: MIT

import re
from typing import Dict, List, Pattern, Tuple

"""Utilities to smooth out language rules.

``talkgooder`` attempts to smooth out grammar, punctuation, and
number-related corner cases when formatting text for human consumption.
It is intended for applications where you know there's a noun and are
trying to generate text, but you don't know much about it.
"""


def _get_plural_data(
    addl_same: List[str] = None,
    addl_special_s: List[str] = None,
    addl_irregular: Dict[str, str] = None,
) -> Tuple[List[str], List[str], Dict[str, str], Pattern[str]]:
    """Get plural data structures for en-US locale."""
    if addl_same is None:
        addl_same = []
    if addl_special_s is None:
        addl_special_s = []
    if addl_irregular is None:
        addl_irregular = {}

    # Same singular as plural, can be extended via addl_same parameter
    en_us_same = [
        "aircraft",
        "buffalo",
        "deer",
        "fish",
        "goose",
        "hovercraft",
        "moose",
        "salmon",
        "sheep",
        "shrimp",
        "spacecraft",
        "trout",
        "watercraft",
    ] + addl_same

    # Doesn't follow other rules, plural is always s, can be extended via addl_special_s
    en_us_special_s = [
        "cello",
        "hello",
        "photo",
        "piano",
        "proof",
        "roof",
        "spoof",
        "zero",
    ] + addl_special_s

    # Irregular plurals where there's no rule, it just is, can be extended via addl_irregular
    en_us_irregular = dict(
        list(
            {
                "child": "children",
                "criterion": "criteria",
                "die": "dice",
                "louse": "lice",
                "man": "men",
                "mouse": "mice",
                "ox": "oxen",
                "person": "people",
                "phenomenon": "phenomena",
                "tooth": "teeth",
                "woman": "women",
            }.items()
        )
        + list(addl_irregular.items())
    )

    # Consonant before y pattern
    en_us_ies_pattern = re.compile(
        r"[b-df-hj-np-tv-z]+y$",
        re.IGNORECASE,
    )

    return en_us_same, en_us_special_s, en_us_irregular, en_us_ies_pattern


def _get_plural_suffixes(text: str, caps_mode: int) -> Dict[str, str]:
    """Get appropriate suffixes based on casing mode."""
    # If the entire word is upper case or caps_mode is 1, capitalize it
    if caps_mode == 2:
        casing = "lower"
    elif text.isupper() or caps_mode == 1:
        casing = "upper"
    else:
        casing = "lower"

    if casing == "upper":
        return {
            "i": "I",
            "a": "A",
            "ices": "ICES",
            "es": "ES",
            "ies": "IES",
            "ves": "VES",
            "s": "S",
        }
    else:
        return {
            "i": "i",
            "a": "a",
            "ices": "ices",
            "es": "es",
            "ies": "ies",
            "ves": "ves",
            "s": "s",
        }


def _check_same_singular_plural(text: str, en_us_same: List[str]) -> str | None:
    """Check if word has same singular and plural form."""
    if text.lower() in en_us_same:
        return text
    return None


def _check_irregular_plurals(text: str, en_us_irregular: Dict[str, str]) -> str | None:
    """Check and apply irregular plural rules."""
    for item in en_us_irregular.keys():
        if text.lower().endswith(item.lower()):
            if text.isupper():
                return en_us_irregular[item].upper()
            else:
                return en_us_irregular[item]
    return None


def _apply_suffix_rules(
    text: str,
    suffixes: Dict[str, str],
    en_us_special_s: List[str],
    en_us_ies_pattern: Pattern[str],
) -> str:
    """Apply standard suffix-based pluralization rules."""
    text_lower = text.lower()

    if text_lower in en_us_special_s:
        # Certain words always end with s for Reasons
        return f"{text}{suffixes['s']}"

    if text_lower.endswith("us"):
        # Words that end in "us" change to "i" when plural
        return f"{text[:-2]}{suffixes['i']}"

    if text_lower.endswith("um"):
        # Words that end in "um" change to "a" when plural
        return f"{text[:-2]}{suffixes['a']}"

    if text_lower.endswith(("ix", "ex")):
        # Words that end in "ix" or "ex" change to "ices" when plural
        return f"{text[:-2]}{suffixes['ices']}"

    if text_lower.endswith(("o", "s", "x", "z", "ch", "sh", "is")):
        # Words ending in these letters/combinations change to "es"
        return f"{text}{suffixes['es']}"

    if text_lower.endswith(("f", "fe")):
        # Words that end in "f" or "fe" end in "ves" when plural
        return f"{text[:-1]}{suffixes['ves']}"

    if en_us_ies_pattern.findall(text):
        # Words ending in consonant then "y" end in "ies" when plural
        return f"{text[:-1]}{suffixes['ies']}"

    # Remaining words end in "s" when plural
    return f"{text}{suffixes['s']}"


def _apply_plural_rules(
    text: str,
    suffixes: Dict[str, str],
    en_us_same: List[str],
    en_us_special_s: List[str],
    en_us_irregular: Dict[str, str],
    en_us_ies_pattern: Pattern[str],
) -> str:
    """Apply plural rules to determine the correct plural form."""
    # Check if word is same whether singular or plural
    same_result = _check_same_singular_plural(text, en_us_same)
    if same_result is not None:
        return same_result

    # Check irregular plurals
    irregular_result = _check_irregular_plurals(text, en_us_irregular)
    if irregular_result is not None:
        return irregular_result

    # Apply standard suffix rules
    return _apply_suffix_rules(text, suffixes, en_us_special_s, en_us_ies_pattern)


def plural(
    text: str,
    number: int | float,
    language: str = "en-US",
    addl_same: List[str] = None,
    addl_special_s: List[str] = None,
    addl_irregular: Dict[str, str] = None,
    caps_mode: int = 0,
) -> str:
    """Determine the plural of a noun depending upon quantity.

    Given a quantity of nouns, return the most likely plural form. Language is complicated and
    pluralization rules are not always consistent, so this function supports user-supplied rules
    to accommodate exceptions specific to the situation.

    **Supported locales:**

    * ``en-US``: American English

    Args:
        text (str):
            The noun to convert.
        number (int or float):
            The quantity of nouns.
        language (str):
            Which language rules to apply, specified by locale (default: ``en-US``).
        addl_same (list):
            Additional words where the singular and plural are the same.
        addl_special_s (list):
            Additional words that always end in s for odd reasons
            (e.g., ``["piano","hello",...]``).
        addl_irregular (dict):
            Additional pairs of irregular plural nouns (e.g.,
            ``{"mouse": "mice", "person": "people", ...}``).
        caps_mode (int):

            * ``0``: Attempt to infer whether suffix is lower or upper case (default).
            * ``1``: Force suffix to be upper case.
            * ``2``: Force suffix to be lower case.

    Returns:
        String:
            The plural of the provided noun.

    Raises:
        TypeError: Text must be a string.
        ValueError: Language must be a supported locale.
    """

    # Thanks to Grammarly for publishing a guideline that helped inspire these rules:
    # https://www.grammarly.com/blog/irregular-plural-nouns/

    # Make sure something reasonable was supplied
    if not isinstance(text, str):
        raise TypeError("Text must be a string")

    if not isinstance(number, (int, float)):
        raise TypeError("Number must be an int or a float")

    if language.lower() == "en-us":
        # If the number is an integer that is exactly 1, nothing to do
        if isinstance(number, int) and number == 1:
            return text

        # Handle None defaults
        if addl_same is None:
            addl_same = []
        if addl_special_s is None:
            addl_special_s = []
        if addl_irregular is None:
            addl_irregular = {}

        # Get plural data structures
        (
            en_us_same,
            en_us_special_s,
            en_us_irregular,
            en_us_ies_pattern,
        ) = _get_plural_data(addl_same, addl_special_s, addl_irregular)

        # Get appropriate suffixes
        suffixes = _get_plural_suffixes(text, caps_mode)

        # Apply plural rules
        return _apply_plural_rules(
            text,
            suffixes,
            en_us_same,
            en_us_special_s,
            en_us_irregular,
            en_us_ies_pattern,
        )

    else:
        raise ValueError("Language must be a supported locale.")


def possessive(
    text: str,
    language: str = "en-US",
    caps_mode: int = 0,
) -> str:
    """Convert a noun to its possessive, because apostrophes can be hard.

    **Supported locales:**

    * ``en-US``: American English

    Args:
        text (str):
            A noun to be made possessive.

        language (str):
            Which language rules to apply (default ``en-US``).

        caps_mode (int):

            * ``0``: Attempt to infer whether suffix is lower or upper case (default).
            * ``1``: Force suffix to be upper case.
            * ``2``: Force suffix to be lower case.

    Returns:
        String:
            The possessive of the provided string.

    Raises:
        TypeError: Text must be a string.
        ValueError: Language must be a supported locale.
    """

    if not isinstance(text, str):
        raise TypeError("Text must be a string")

    if language.lower() == "en-us":
        if text.endswith("s"):
            # When a noun ends in "s", just add an apostrophe
            return f"{text}'"

        else:
            if caps_mode == 2:
                # Force lower case
                return f"{text}'s"
            elif text.isupper() or caps_mode == 1:
                # Force upper case or detect upper case
                return f"{text}'S"
                # Default is lower
            else:
                return f"{text}'s"

    else:
        raise ValueError("Language must be a supported locale.")


def num2word(
    number: int,
    language: str = "en-US",
) -> str:
    """Determine if an integer should be expanded to a word (per the APA style manual).

    The APA style manual specifies integers between 1 and 9 should be written out as a word.
    Everything else should be represented as digits.

    **Supported locales:**

    * ``en-US``: American English

    Args:
        number (int):
            An integer.
        language (str):
            Which language rules to apply (default ``en-US``).

    Returns:
        String:
            The word or string-formatted number, as appropriate.

    Raises:
        TypeError: Number must be an int.
        ValueError: Language must be a supported locale.
    """

    # Make sure something reasonable was supplied
    if not isinstance(number, int):
        raise TypeError("Number must be an int.")

    # Per APA style guide, only 1-9 should be expanded
    if number < 1 or number > 9:
        return str(number)

    if language.lower() == "en-us":
        numbers = [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
        ]
    else:
        raise ValueError("Language must be a supported locale.")

    return numbers[number - 1]


def isAre(
    number: int | float,
    language: str = "en-US",
) -> str:
    """Given a quantity, determine if article should be ``is`` or ``are``.

    Given a quantity of nouns or noun-equivalents, determine whether the article should be
    ``is`` or ``are``. For example, "there is one cat," and "there are two cats."

    **Supported locales:**

    * ``en-US``: American English

    Args:
        number (int | float):
            Quantity of items.
        language (str):
            Which language rules to apply, specified by locale (default ``en-US``).

    Returns:
        String:
            ``is`` or ``are``, as appropriate.

    Raises:
        TypeError: number must be an int or float.
        ValueError: language must be a supported locale.
    """

    if not isinstance(number, (int, float)):
        raise TypeError("Number must be an int or a float.")

    if language.lower() == "en-us":
        # Anything other than integer 1 (even 1.0) uses "are"
        if number == 1 and isinstance(number, int):
            return "is"
        else:
            return "are"

    else:
        raise ValueError("Language must be a supported locale.")


def wasWere(
    number: int | float,
    language: str = "en-US",
) -> str:
    """Given a quantity, determine if article should be ``was`` or ``were``.

    Given a quantity of nouns or noun-equivalents, determine whether the article should be
    ``was`` or ``were``. For example, "there was one cat," and "there were two cats."

    **Supported locales:**

    * ``en-US``: American English

    Args:
        number (int | float):
            Quantity of items.
        language (str):
            Which language rules to apply, specified by locale (default ``en-US``).

    Returns:
        String:
            ``was`` or ``were``, as appropriate.

    Raises:
        TypeError: number must be an int or float.
        ValueError: language must be a supported locale.
    """

    if not isinstance(number, (int, float)):
        raise TypeError("Number must be an int or a float.")

    if language.lower() == "en-us":
        # Anything other than integer 1 (even 1.0) uses "were"
        if number == 1 and isinstance(number, int):
            return "was"
        else:
            return "were"

    else:
        raise ValueError("Language must be a supported locale.")


def aAn(
    noun: str | int | float,
    language: str = "en-US",
) -> str:
    """Given a noun or noun-equivalent, determine whether the article is ``a`` or ``an``.

    Nouns and noun-equivalents with a soft vowel beginning generally use ``an``, and everything
    else uses ``a``.

    **Supported locales:**

    * ``en-US``: American English

    Args:
        noun (str | int | float):
            A noun or noun-equivalent, as a word or a number.

        language (str):
            Which language rules to apply, specified by locale (default ``en-US``).

    Returns:
        String:
            ``a`` or ``an``, as appropriate.

    Raises:
        TypeError: Noun must be a string, int, or float.
        ValueError: Language must be a supported locale.
    """

    if not isinstance(noun, (str, int, float)):
        raise TypeError("Noun must be a string, int, or float.")

    if language.lower() == "en-us":

        # Vowels, numbers that start with 8, and 18 use the "an" article
        if (
            str(noun)
            .lower()
            .startswith(
                (
                    "a",
                    "e",
                    "i",
                    "o",
                    "u",
                    "8",
                    "18.",
                )
            )
            or str(noun) == "18"
        ):
            return "an"
        else:
            return "a"
    else:
        raise ValueError("Language must be a supported locale.")
