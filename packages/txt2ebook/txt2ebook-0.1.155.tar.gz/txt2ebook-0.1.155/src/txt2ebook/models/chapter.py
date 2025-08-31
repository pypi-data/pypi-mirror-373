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

"""Chapter is a container for paragraphs."""

import logging
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger(__name__)


@dataclass(repr=False)
class Chapter:
    """A chapter class model."""

    title: str = field(default="")
    paragraphs: List[str] = field(default_factory=list, repr=False)

    def __repr__(self) -> str:
        """Return the string representation of Chapter for debugging purpose.

        Returns:
          str: Debugging string for logging
        """
        # pylint: disable=bad-option-value,consider-using-f-string
        return "{}(title='{}', paragraphs='{}')".format(
            self.__class__.__name__,
            self.title,
            len(self.paragraphs),
        )

    def add_paragraph(self, paragraph: str) -> None:
        """Append a paragraph to the current chapter."""
        # logger.debug("add paragraph: " + repr(paragraph[0:5]))
        self.paragraphs.append(paragraph)
