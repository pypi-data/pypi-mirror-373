# Copyright (c) 2021,2022,2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""String helper functions for handling zh related text."""

import re
import warnings
from typing import Any
from unicodedata import numeric

WORD_NUMERIC_MAP = {
    "两": 2.0,
    "圩": 50.0,
    "圓": 60.0,
    "進": 70.0,
    "枯": 80.0,
    "枠": 90.0,
}


def zh_numeric(word: str, default: Any = None) -> Any:
    """Custom wrapper for unicodedata.numeric.

    This supports additional numeral values not supported by the existing
    library.

    Args:
        word(str): The Chinese character.
        default(Any): If set, a default value is used instead of raising
        exception.

    Returns:
        float: The numeric value of the Chinese character.
    """
    try:
        return numeric(word)
    except TypeError as terror:
        raise TypeError(
            "zh_numeric() argument 1 must be a unicode character, not str"
        ) from terror
    except ValueError as verror:
        try:
            return WORD_NUMERIC_MAP[word]
        except KeyError as kerror:
            if default is None:
                raise verror from kerror

            return default


# Unicode integer in hexadecimal for these characters.
FULLWIDTH_EXCLAMATION_MARK = 0xFF01
EXCLAMATION_MARK = 0x21
TILDE = 0x7E

# Mapping table for halfwidth ASCII characters to its fullwidth equivalent.
#
# Fullwidth is a text character that occupies two alphanumeric characters
# in monospace font.
#
# See Halfwidth and Fullwidth Forms in Unicode (https://w.wiki/66Ps) and
# Unicode block (https://w.wiki/66Pt).
HALFWIDTH_FULLWIDTH_MAP = {}
for i, j in enumerate(range(EXCLAMATION_MARK, TILDE + 1)):
    HALFWIDTH_FULLWIDTH_MAP[j] = FULLWIDTH_EXCLAMATION_MARK + i


def zh_halfwidth_to_fullwidth(words: str) -> str:
    """Convert halfwidth to fullwidth text.

    Args:
        words(str): The string contains halfwidth characters.

    Returns:
        str: The string contains fullwidth characters.
    """
    return words.translate(HALFWIDTH_FULLWIDTH_MAP)


NUMS_WORDS = "零一二三四五六七八九十廿卅卌圩圓百千两"


def zh_words_to_numbers(words: str, **kwargs: Any) -> str:
    """Convert header from words to numbers.

    For example, `第一百零八章` becomes `第108章`.

    Args:
        words(str): The line that contains section header in words.
        length(int): The number of left zero-padding to prepend.
        match_all(bool): Match the all found words.

    Returns:
        str: The formatted section header.
    """
    found = re.findall(rf"([{NUMS_WORDS}]+)", words)
    if not found:
        return words

    if kwargs.get("match_all"):
        found_words = found
    else:
        # match only the first found result
        found_words = [found[0]]

    replaced_words = words
    for found_word in found_words:
        header_nums = 0
        for word_grp in re.findall("..?", found_word):
            if len(word_grp) == 2:
                # 零 or 十
                if (
                    zh_numeric(word_grp[0]) == 0.0
                    or zh_numeric(word_grp[0]) == 10.0
                ):
                    header_nums += int(
                        zh_numeric(word_grp[0]) + zh_numeric(word_grp[1])
                    )
                else:
                    header_nums += int(
                        zh_numeric(word_grp[0]) * zh_numeric(word_grp[1])
                    )
            else:
                header_nums += int(zh_numeric(word_grp))

        padded_header_nums = str(header_nums)

        length: int = kwargs.get("length", 0)
        if length > 0:
            word_length = len(padded_header_nums)
            if word_length < length:
                padded_header_nums = padded_header_nums.rjust(length, "0")
            else:
                warnings.warn(
                    (
                        "prepend zero length less than word length, "
                        f"word length: {word_length}, prepend length: {length}"
                    )
                )
        replaced_words = replaced_words.replace(found_word, padded_header_nums)

    return replaced_words


__all__ = [
    "zh_halfwidth_to_fullwidth",
    "zh_numeric",
    "zh_words_to_numbers",
]
