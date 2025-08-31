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

"""Common helper functions."""

import logging
import re

logger = logging.getLogger(__name__)


def lower_underscore(string: str) -> str:
    """Convert a string to lower case and replace multiple spaces to single underscore.

    Args:
        string (str): A string.

    Returns:
        str: Formatted string.

    Examples:

        >>> lower_underscore("Hello World")
        'hello_world'
        >>> lower_underscore("Hello   World")
        'hello_world'
        >>> lower_underscore("Hello\tWorld")
        'hello_world'
    """
    return re.sub(r"\s+", "_", string.lower().strip())
