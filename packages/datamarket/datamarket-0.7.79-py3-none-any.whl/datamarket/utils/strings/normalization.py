########################################################################################################################
# IMPORTS

import unicodedata
from enum import Enum, auto
from typing import Any, Optional, Set, Union

import numpy as np
from inflection import camelize, parameterize, titleize, underscore
from string_utils import prettify, strip_html
from unidecode import unidecode

########################################################################################################################
# CLASSES


class NormalizationMode(Enum):
    NONE = auto()
    BASIC = auto()  # removes accents and converts punctuation to spaces
    SYMBOLS = auto()  # translates only symbols to Unicode name
    FULL = auto()  # BASIC + SYMBOLS


class NamingConvention(Enum):
    NONE = auto()  # no style change
    LOWER = auto()  # lowercase
    UPPER = auto()  # UPPERCASE
    CONSTANT = auto()  # CONSTANT_CASE (uppercase, underscores)
    SNAKE = auto()  # snake_case (lowercase, underscores)
    CAMEL = auto()  # camelCase (capitalize words except first one, no spaces)
    PASCAL = auto()  # PascalCase (capitalize words including first one, no spaces)
    PARAM = auto()  # parameterize (hyphens)
    TITLE = auto()  # titleize (capitalize words)


########################################################################################################################
# FUNCTIONS


def get_unidecoded_text(input_text: str, allowed_chars: Set[str], apply_lowercase: bool = False) -> str:
    """
    Processes a string by unidecoding characters, optionally lowercasing them,
    while preserving a specified set of allowed characters.

    Args:
        input_text: The string to process.
        allowed_chars: A set of characters to preserve in their original form.
        apply_lowercase: Whether to convert unidecoded characters to lowercase. Defaults to False.

    Returns:
        The processed string.
    """
    chars_list: list[str] = []
    for char_original in input_text:
        if char_original in allowed_chars:
            chars_list.append(char_original)
        else:
            decoded_segment = unidecode(char_original)
            for dc in decoded_segment:  # unidecode can return multiple chars
                if apply_lowercase:
                    chars_list.append(dc.lower())
                else:
                    chars_list.append(dc)
    return "".join(chars_list)


def transliterate_symbols(s: str, allowed_symbols_set: Optional[Set[str]] = None) -> str:
    """
    Translates Unicode symbols (category S*) in the input string to their lowercase Unicode names,
    with spaces replaced by underscores. Other characters, or characters in allowed_symbols_set, remain unchanged.

    Args:
        s: The input string.
        allowed_symbols_set: A set of characters to preserve without transliteration.

    Returns:
        The string with symbols transliterated or preserved.
    """
    if allowed_symbols_set is None:
        allowed_symbols_set = set()
    out: list[str] = []
    for c in s:
        if c in allowed_symbols_set:
            out.append(c)
        elif unicodedata.category(c).startswith("S"):
            name = unicodedata.name(c, "")
            if name:
                out.append(name.lower().replace(" ", "_"))
        else:
            out.append(c)
    return "".join(out)


def normalize(
    s: Any,
    mode: Union[NormalizationMode, str] = NormalizationMode.BASIC,
    naming: Union[NamingConvention, str] = NamingConvention.LOWER,
    allowed_symbols: Optional[str] = None,
) -> str:
    """
    Normalizes and applies a naming convention to the input.

    Handles None and NaN values by returning an empty string. Converts non-string inputs to strings.

    Normalization (controlled by `mode`) occurs first, followed by naming convention application.
    - NONE: Returns the input as a string without any normalization. Case is preserved.
    - BASIC: Removes accents (via unidecode). Punctuation and spaces typically become single spaces between tokens.
             Case is preserved from the unidecode step by default.
    - SYMBOLS: Translates only Unicode symbols (category S*) to their lowercase Unicode names with underscores.
               Other characters are preserved, including their case.
    - FULL: Applies unidecode (case-preserved by default) and then SYMBOLS-like transliteration for S* category
            characters not otherwise handled.

    The `allowed_symbols` parameter can be used to specify characters that should be preserved in their original form
    throughout the normalization process. These characters will not be unidecoded or transliterated by the symbol logic.

    After normalization, a naming convention (controlled by `naming`) is applied:
    - NONE: Returns the normalized text, preserving its case from the normalization step.
    - LOWER: Converts the normalized text to lowercase. (Default)
    - UPPER: Converts the normalized text to UPPERCASE.
    - CONSTANT: Converts to CONSTANT_CASE (uppercase with underscores).
    - SNAKE: Converts to snake_case (lowercase with underscores).
    - CAMEL: Converts to camelCase (lowercase first word, capitalize subsequent words, no spaces).
    - PASCAL: Converts to PascalCase (capitalize all words, no spaces).
    - PARAM: Converts to parameterize (lowercase with hyphens).
    - TITLE: Converts to Title Case (capitalize each word).

    Args:
        s: The input value to normalize and format. Can be any type.
        mode: The normalization mode to apply. Defaults to NormalizationMode.BASIC.
        naming: The naming convention to apply. Defaults to NamingConvention.LOWER.
        allowed_symbols: A string of characters to preserve during normalization.

    Returns:
        The normalized and formatted string.
    """
    # Parameter mapping
    if isinstance(mode, str):
        mode = NormalizationMode[mode.upper()]
    if isinstance(naming, str):
        naming = NamingConvention[naming.upper()]

    _allowed_symbols_set: Set[str] = set(allowed_symbols) if allowed_symbols else set()

    # Handling null values
    if s is None or (isinstance(s, float) and np.isnan(s)):
        normalized = ""
    elif not isinstance(s, str):
        return str(s)
    else:
        text = prettify(strip_html(str(s), True))

        if mode is NormalizationMode.NONE:
            normalized = text
        elif mode is NormalizationMode.SYMBOLS:
            normalized = transliterate_symbols(text, _allowed_symbols_set)
        else:
            # BASIC and FULL modes
            intermediate_text = get_unidecoded_text(text, _allowed_symbols_set)

            # Now, tokenize the intermediate_text for BASIC and FULL
            tokens: list[str] = []
            current_token_chars: list[str] = []

            def flush_current_token():
                nonlocal current_token_chars
                if current_token_chars:
                    tokens.append("".join(current_token_chars))
                    current_token_chars.clear()

            for c in intermediate_text:
                cat = unicodedata.category(c)
                if c in _allowed_symbols_set:  # Allowed symbols are part of tokens
                    current_token_chars.append(c)
                elif c.isalnum():
                    current_token_chars.append(c)
                elif mode is NormalizationMode.FULL and cat.startswith("S"):
                    # Transliterate S* category symbols not in allowed_symbols
                    flush_current_token()
                    name = unicodedata.name(c, "")
                    if name:
                        tokens.append(name.lower().replace(" ", "_"))
                elif cat.startswith("P") or c.isspace():
                    # Punctuation (not allowed) or space acts as a separator
                    flush_current_token()
                # Other characters are ignored

            flush_current_token()
            normalized = " ".join(tokens)

    # Apply naming convention
    if naming is NamingConvention.NONE:
        return normalized
    if naming is NamingConvention.LOWER:
        return normalized.lower()
    if naming is NamingConvention.UPPER:
        return normalized.upper()
    if naming is NamingConvention.PARAM:
        return parameterize(normalized)
    if naming is NamingConvention.TITLE:
        return titleize(normalized)

    underscored = underscore(parameterize(normalized))
    if naming is NamingConvention.CONSTANT:
        return underscored.upper()
    if naming is NamingConvention.CAMEL:
        return camelize(underscored, False)
    if naming is NamingConvention.PASCAL:
        return camelize(underscored)

    return underscored
