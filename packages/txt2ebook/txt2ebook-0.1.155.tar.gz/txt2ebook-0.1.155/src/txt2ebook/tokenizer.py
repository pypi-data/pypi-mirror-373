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

"""Parse source text file into tokens."""

import argparse
import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Dict, List

from txt2ebook import log_or_raise_on_warning

logger = logging.getLogger(__name__)


@dataclass
class Token:
    """Token class to store metadata of token."""

    type: str = field(repr=True)
    value: Any = field(repr=False)
    line_no: int = field(repr=True, default=0)

    def __repr__(self) -> str:
        """Return the string representation of Tokenizer for debugging purpose.

        Returns:
          str: Debugging string for logging
        """
        # pylint: disable=bad-option-value,consider-using-f-string
        return "{}(type='{}', line_no='{}', value='{}')".format(
            self.__class__.__name__, self.type, self.line_no, self.value[0:10]
        )


@dataclass
class Tokenizer:
    """Tokenizer class to parse text content."""

    raw_content: str = field(repr=False)
    metadata_marker: str = field(repr=False)
    config: argparse.Namespace = field(repr=False)
    tokens: List[Token] = field(default_factory=List, repr=False)
    lineno_lookup: Dict = field(default_factory=Dict, repr=False)

    def __init__(self, raw_content: str, config: argparse.Namespace) -> None:
        """Set the constructor for the Tokenizer."""
        self.raw_content = raw_content
        self.config = config
        self.metadata_marker = "---"

        config_lang = config.language.replace("-", "_")
        self.langconf = import_module(f"txt2ebook.languages.{config_lang}")

        lookupcontent = raw_content[:]
        lineno_lookup = {}
        for lineno, line in enumerate(lookupcontent.splitlines(), start=1):
            lineno_lookup[line[:10]] = lineno
        self.lineno_lookup = lineno_lookup

        self.tokens = []
        self.parse()

    def __repr__(self) -> str:
        """Return the string representation of Tokenizer for debugging purpose.

        Returns:
          str: Debugging string for logging
        """
        # pylint: disable=bad-option-value,consider-using-f-string
        return "{}(raw_content='{}', stats='{}')".format(
            self.__class__.__name__, self.raw_content[:5], self.stats()
        )

    def parse(self) -> None:
        """Parse the content into tokens.

        Returns:
          None
        """
        self._tokenize_metadata()
        self._tokenize_content()

    def stats(self) -> Counter:
        """Returns the statistics count for the parsed tokens.

        Returns:
          Counter: Counting statistic of parsed tokens.
        """
        stats = Counter(token.type for token in self.tokens)
        logger.debug("Token stats: %s", repr(stats))
        return stats

    def _tokenize_line(self, line: str) -> None:
        """Tokenize each line after we split by paragraph separator."""
        _ = self._tokenize_header(line) or self._tokenize_paragraph(line)

    def _tokenize_metadata(self) -> None:
        """Tokenize the metadata of the book."""
        for line in self._extract_metadata():
            re_title = f"^{self.langconf.DEFAULT_RE_TITLE}"
            if hasattr(self.config, "re_title") and self.config.re_title:
                re_title = self.config.re_title[0]

            re_author = f"{self.langconf.DEFAULT_RE_AUTHOR}"
            if hasattr(self.config, "re_author") and self.config.re_author:
                re_author = self.config.re_author[0]

            token_type_regex_map = [
                ("TITLE", re_title),
                ("AUTHOR", re_author),
                ("TAG", f"{self.langconf.DEFAULT_RE_TAG}"),
                ("INDEX", f"{self.langconf.DEFAULT_RE_INDEX}"),
                ("TRANSLATOR", f"{self.langconf.DEFAULT_RE_TRANSLATOR}"),
            ]

            token = None
            for token_type, regex in token_type_regex_map:
                match = re.search(regex, line)
                if match:
                    token_value = match.group(1).strip()
                    token = Token(
                        token_type, token_value, self._lineno(token_value)
                    )
                    self.tokens.append(token)

    def _extract_metadata(self) -> List:
        """Extract YAML-inspired metadata header from file context.

        Metadata header with line number as follows:

            1 ---
            2 书名：
            3 作者：
            4 标签：
            5 索引：
            6 翻译：
            7 ---

        """
        match = re.search(
            rf"^(?:{self.metadata_marker})\n(.*)\n(?:{self.metadata_marker})$",
            self.raw_content,
            re.MULTILINE | re.DOTALL,
        )
        if not match:
            msg = "Missing or invalid metadata."
            log_or_raise_on_warning(msg, self.config.raise_on_warning)
            return []

        metadata = match[1].split("\n")
        for metadata_field in metadata:
            logger.info("Metadata: %s", metadata_field)

        return metadata

    def _tokenize_content(self) -> None:
        # Determine the actual content part, after any metadata block
        metadata_block_re = (
            rf"^(?:{self.metadata_marker})\n(.*)\n(?:{self.metadata_marker})$"
        )
        match = re.search(
            metadata_block_re, self.raw_content, re.MULTILINE | re.DOTALL
        )

        if match:
            # Content starts after the matched metadata block
            content_str = self.raw_content[match.end(0) :]
        else:
            # No metadata block found according to the pattern,
            # so assume all raw_content is the actual content.
            # _extract_metadata would have already logged/warned if metadata was expected.
            content_str = self.raw_content

        content_str = content_str.strip(self.config.paragraph_separator)
        lines = content_str.split(self.config.paragraph_separator)

        if len(lines) <= 1 and content_str:  # Avoid warning for empty content
            msg = (
                "Cannot split content by "
                f"{repr(self.config.paragraph_separator)}. "
                "Check if content have newline with spaces."
            )
            log_or_raise_on_warning(msg, self.config.raise_on_warning)

        for line in lines:
            self._tokenize_line(line)

    def _tokenize_header(self, line: str) -> bool:
        """Tokenize section headers.

        Note that we parse in such sequence: chapter, volume, volume_chapter to
        prevent unnecessary calls as we've more chapters than volumes.
        """
        return (
            self._tokenize_chapter(line)
            or self._tokenize_volume_chapter(line)
            or self._tokenize_volume(line)
        )

    def _tokenize_volume_chapter(self, line: str) -> bool:
        line = self._validate_section_header("volume chapter", line)
        token = None

        re_volume_chapter = (
            rf"^{self.langconf.DEFAULT_RE_VOLUME}\s*"
            rf"{self.langconf.DEFAULT_RE_CHAPTER}"
        )
        if (
            hasattr(self.config, "re_volume_chapter")
            and self.config.re_volume_chapter
        ):
            re_volume_chapter = self.config.re_volume_chapter[0]

        match = re.search(re_volume_chapter, line)
        if match:
            volume = match.group(1).strip()
            chapter = match.group(2).strip()
            token = Token(
                "VOLUME_CHAPTER",
                [
                    Token("VOLUME", volume, self._lineno(volume)),
                    Token("CHAPTER", chapter, self._lineno(chapter)),
                ],
            )
            self.tokens.append(token)

        return bool(token)

    def _tokenize_volume(self, line: str) -> bool:
        line = self._validate_section_header("volume", line)
        token = None

        re_volume = rf"^{self.langconf.DEFAULT_RE_VOLUME}$"
        if hasattr(self.config, "re_volume") and self.config.re_volume:
            re_volume = "(" + "|".join(self.config.re_volume) + ")"

        match = re.search(re_volume, line)
        if match:
            volume = match.group(1).strip()
            token = Token("VOLUME", volume, self._lineno(volume))
            self.tokens.append(token)

        return bool(token)

    def _tokenize_chapter(self, line: str) -> bool:
        line = self._validate_section_header("chapter", line)
        token = None

        re_chapter = rf"^{self.langconf.DEFAULT_RE_CHAPTER}$"
        if hasattr(self.config, "re_chapter") and self.config.re_chapter:
            re_chapter = "(" + "|".join(self.config.re_chapter) + ")"

        match = re.search(re_chapter, line)
        if match:
            chapter = match.group(1).strip()
            token = Token("CHAPTER", chapter, self._lineno(chapter))
            self.tokens.append(token)

        return bool(token)

    def _tokenize_paragraph(self, line: str) -> bool:
        self.tokens.append(Token("PARAGRAPH", line, self._lineno(line)))
        return True

    def _validate_section_header(self, header_type: str, line: str) -> str:
        if line.startswith("\n"):
            log_or_raise_on_warning(
                f"Found newline before {header_type} header: {repr(line)}",
                self.config.raise_on_warning,
            )
            line = line.lstrip("\n")
        return line

    def _lineno(self, text: str) -> int:
        """Find the line no of the string within the file or raw content."""
        return self.lineno_lookup.get(text[:10], 0)
