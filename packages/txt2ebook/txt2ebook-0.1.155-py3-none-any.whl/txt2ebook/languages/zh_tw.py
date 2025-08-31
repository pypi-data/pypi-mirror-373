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

"""Config for Traditional Chinese (zh-tw) language."""

from txt2ebook.languages.zh_cn import (
    DEFAULT_RE_AUTHOR,
    DEFAULT_RE_CHAPTER,
    DEFAULT_RE_INDEX,
    DEFAULT_RE_TAG,
    DEFAULT_RE_TITLE,
    DEFAULT_RE_TRANSLATOR,
    DEFAULT_RE_VOLUME,
    FULLWIDTH_NUMS,
    HALFWIDTH_NUMS,
    IDEOGRAPHIC_SPACE,
    NUMS_WORDS,
    RE_NUMS,
    SPACE,
)

DEFAULT_PDF_FONT_NAME = "AR PL UMing TW"
DEFAULT_PDF_FONT_FILE = "uming.ttc"
DEFAULT_PDF_FONT_SIZE = 12
DEFAULT_PDF_PAGE_SIZE = "A5"

__all__ = [
    "DEFAULT_RE_AUTHOR",
    "DEFAULT_RE_CHAPTER",
    "DEFAULT_RE_TAG",
    "DEFAULT_RE_INDEX",
    "DEFAULT_RE_TITLE",
    "DEFAULT_RE_TRANSLATOR",
    "DEFAULT_RE_VOLUME",
    "FULLWIDTH_NUMS",
    "HALFWIDTH_NUMS",
    "IDEOGRAPHIC_SPACE",
    "NUMS_WORDS",
    "RE_NUMS",
    "SPACE",
]
