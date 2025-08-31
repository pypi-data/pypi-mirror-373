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

"""Env subcommand."""

import argparse
import logging
import platform
import sys

from txt2ebook import __version__

logger = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    env_parser = subparsers.add_parser(
        "env", help="print environment information for bug reporting"
    )

    env_parser.set_defaults(func=run)


def run(_args: argparse.Namespace) -> None:
    """Run the env subcommand to print environment information.

    Args:
        _args (argparse.Namespace): Config from command line arguments
        (unused).

    Returns:
        None
    """
    sys_version = sys.version.replace("\n", "")
    env = [
        f"txt2ebook: {__version__}",
        f"python: {sys_version}",
        f"platform: {platform.platform()}",
    ]
    print(*env, sep="\n")
