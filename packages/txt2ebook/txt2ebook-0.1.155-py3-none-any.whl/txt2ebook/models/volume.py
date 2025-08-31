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

"""Volume is a container for different Chapters."""

from dataclasses import dataclass, field
from typing import List

from txt2ebook.models.chapter import Chapter


@dataclass
class Volume:
    """A volume class model."""

    title: str = field(default="")
    chapters: List[Chapter] = field(default_factory=list, repr=False)

    def __repr__(self) -> str:
        """Return the string representation of Volume for debugging purpose.

        Returns:
          str: Debugging string for logging
        """
        # pylint: disable=bad-option-value,consider-using-f-string
        return "{}(title='{}', chapters='{}')".format(
            self.__class__.__name__,
            self.title,
            len(self.chapters),
        )

    def add_chapter(self, chapter: Chapter) -> None:
        """Append a chapter to the current volume."""
        self.chapters.append(chapter)
