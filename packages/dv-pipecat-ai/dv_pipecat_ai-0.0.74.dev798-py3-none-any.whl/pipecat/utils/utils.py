#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import collections
import itertools
import threading

_COUNTS = collections.defaultdict(itertools.count)
_COUNTS_LOCK = threading.Lock()
_ID = itertools.count()
_ID_LOCK = threading.Lock()


def obj_id() -> int:
    """Generate a unique id for an object.

    >>> obj_id()
    0
    >>> obj_id()
    1
    >>> obj_id()
    2
    """
    with _ID_LOCK:
        return next(_ID)


def obj_count(obj) -> int:
    """Generate a unique id for an object.

    >>> obj_count(object())
    0
    >>> obj_count(object())
    1
    >>> new_type = type('NewType', (object,), {})
    >>> obj_count(new_type())
    0
    """
    with _COUNTS_LOCK:
        return next(_COUNTS[obj.__class__.__name__])


def detect_language_from_script(text: str, max_chars_check: int = 60) -> str:
    """
    Detects language based on script presence in the initial characters.
    Supports detecting Telugu, Hindi, Kannada, Tamil, Malayalam, or English.

    Args:
        text (str): The input text.
        max_chars_check (int): The maximum number of initial characters to check
                              after removing whitespace and punctuation.

    Returns:
        str: The detected 2-letter language code ("te", "hi", "kn", "ta", "ml", or "en").
    """
    if not text:
        return "en"  # Default to English for empty text

    # Remove whitespace, commas, and other common punctuation
    clean_text = "".join(c for c in text if not c.isspace() and c not in ",.:;!?()[]{}\"'")

    # Unicode ranges for different scripts
    script_ranges = {
        "te": (0x0C00, 0x0C7F),  # Telugu
        "hi": (0x0900, 0x097F),  # Hindi (Devanagari)
        "kn": (0x0C80, 0x0CFF),  # Kannada
        "ta": (0x0B80, 0x0BFF),  # Tamil
        "ml": (0x0D00, 0x0D7F),  # Malayalam
    }

    # Check the first few characters (after cleaning)
    for char in clean_text[:max_chars_check]:
        char_code = ord(char)

        for lang_code, (start, end) in script_ranges.items():
            if start <= char_code <= end:
                return lang_code

    # If no matching script found in the initial check, assume English
    return "en"
