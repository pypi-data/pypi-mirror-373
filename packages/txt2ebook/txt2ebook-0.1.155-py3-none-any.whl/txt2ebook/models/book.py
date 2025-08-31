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

"""Book is a container for Volumes or Chapters."""

import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Union

from txt2ebook.models.chapter import Chapter
from txt2ebook.models.volume import Volume

logger = logging.getLogger(__name__)


@dataclass
class Book:
    """A book class model."""

    title: str = field(default="")
    authors: List[str] = field(default_factory=list)
    translators: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    index: List[str] = field(default_factory=list)
    language: str = field(default="")
    cover: str = field(default="", repr=False)
    raw_content: str = field(default="", repr=False)
    toc: List[Union[Volume, Chapter]] = field(default_factory=list, repr=False)

    def stats(self) -> Counter:
        """Returns the statistics count for the parsed tokens.

        Returns:
          Counter: Counting statistic of parsed tokens.
        """
        stats = Counter(type(header).__name__ for header in self.toc)
        logger.debug("Book stats: %s", repr(stats))
        return stats

    def filename_format(self, filename_format: int) -> str:
        """Generate the filename format based on the available selection."""
        authors = ", ".join(self.authors)
        format_options = {
            1: f"{self.title}_{authors}",
            2: f"{authors}_{self.title}",
        }
        try:
            return format_options[filename_format]
        except KeyError:
            raise AttributeError(
                f"Invalid filename format: '{filename_format}'!"
            )

    def debug(self, verbosity: int = 1) -> None:
        """Dump debug log of sections in self.toc."""
        logger.debug(repr(self))

        for section in self.toc:
            logger.debug(repr(section))
            if isinstance(section, Volume) and verbosity > 1:
                for chapter in section.chapters:
                    logger.debug(repr(chapter))
