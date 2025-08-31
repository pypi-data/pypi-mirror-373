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

"""gmi subcommand."""

import argparse
import logging
import sys

from txt2ebook.formats.gmi import GmiWriter
from txt2ebook.subcommands.parse import run as parse_txt

logger = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    gmi_parser = subparsers.add_parser(
        "gmi", help="generate ebook in Gemtext format"
    )

    gmi_parser.set_defaults(func=run)

    gmi_parser.add_argument(
        "input_file",
        nargs=None if sys.stdin.isatty() else "?",  # type: ignore
        type=argparse.FileType("rb"),
        default=None if sys.stdin.isatty() else sys.stdin,
        help="source text filename",
        metavar="TXT_FILENAME",
    )

    gmi_parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="converted ebook filename (default: 'TXT_FILENAME.md')",
        metavar="EBOOK_FILENAME",
    )

    gmi_parser.add_argument(
        "-sp",
        "--split-volume-and-chapter",
        default=False,
        action="store_true",
        dest="split_volume_and_chapter",
        help=(
            "split volume or chapter into separate file and "
            "ignore the --overwrite option"
        ),
    )

    gmi_parser.add_argument(
        "--toc",
        default=False,
        action=argparse.BooleanOptionalAction,
        dest="with_toc",
        help="add table of content",
    )

    gmi_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the generated file using default program",
    )

    gmi_parser.add_argument(
        "-ff",
        "--filename-format",
        dest="filename_format",
        type=int,
        default=None,
        help=(
            "the output filename format "
            "(default: TXT_FILENAME [EBOOK_FILENAME])\n"
            "1 - title_authors.EBOOK_EXTENSION\n"
            "2 - authors_title.EBOOK_EXTENSION"
        ),
        metavar="FILENAME_FORMAT",
    )

    gmi_parser.add_argument(
        "-ps",
        "--paragraph_separator",
        dest="paragraph_separator",
        type=lambda value: value.encode("utf-8").decode("unicode_escape"),
        default="\n\n",
        help="paragraph separator (default: %(default)r)",
        metavar="SEPARATOR",
    )


def run(args: argparse.Namespace) -> None:
    """Run md subcommand.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    book = parse_txt(args)
    writer = GmiWriter(book, args)
    writer.write()
