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

"""pdf subcommand."""

import argparse
import logging
import sys

from txt2ebook.formats import PAGE_SIZES
from txt2ebook.formats.pdf import PdfWriter
from txt2ebook.subcommands.parse import run as parse_txt

logger = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    pdf_parser = subparsers.add_parser(
        "pdf", help="generate ebook in Markdown format"
    )

    pdf_parser.set_defaults(func=run)

    pdf_parser.add_argument(
        "input_file",
        nargs=None if sys.stdin.isatty() else "?",  # type: ignore
        type=argparse.FileType("rb"),
        default=None if sys.stdin.isatty() else sys.stdin,
        help="source text filename",
        metavar="TXT_FILENAME",
    )

    pdf_parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="converted ebook filename (default: 'TXT_FILENAME.md')",
        metavar="EBOOK_FILENAME",
    )

    pdf_parser.add_argument(
        "-c",
        "--cover",
        dest="cover",
        default=None,
        help="cover of the ebook",
        metavar="IMAGE_FILENAME",
    )

    pdf_parser.add_argument(
        "-pz",
        "--page-size",
        dest="page_size",
        default="a5",
        choices=PAGE_SIZES,
        help="page size of the ebook (default: '%(default)s')",
        metavar="PAGE_SIZE",
    )

    pdf_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the generated file using default program",
    )

    pdf_parser.add_argument(
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


def run(args: argparse.Namespace) -> None:
    """Run pdf subcommand.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    book = parse_txt(args)
    writer = PdfWriter(book, args)
    writer.write()
