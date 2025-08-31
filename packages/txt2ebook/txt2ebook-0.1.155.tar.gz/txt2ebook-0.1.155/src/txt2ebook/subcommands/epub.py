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

"""Epub subcommand."""

import argparse
import logging
import sys

from txt2ebook.formats import EPUB_TEMPLATES
from txt2ebook.formats.epub import EpubWriter
from txt2ebook.subcommands.parse import run as parse_txt

logger = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    epub_parser = subparsers.add_parser(
        "epub",
        help="generate ebook in EPUB format",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    epub_parser.set_defaults(func=run)

    epub_parser.add_argument(
        "input_file",
        nargs="*",
        type=argparse.FileType("rb"),
        help="source text filenames (can use glob patterns)",
        metavar="TXT_FILENAMES",
    )

    epub_parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="converted ebook filename (default: 'TXT_FILENAME.epub')",
        metavar="EBOOK_FILENAME",
    )

    epub_parser.add_argument(
        "-c",
        "--cover",
        dest="cover",
        default=None,
        help="cover of the ebook",
        metavar="IMAGE_FILENAME",
    )

    epub_parser.add_argument(
        "-et",
        "--epub-template",
        default="clean",
        choices=EPUB_TEMPLATES,
        dest="epub_template",
        help="CSS template for epub ebook (default: '%(default)s')",
    )

    epub_parser.add_argument(
        "-vp",
        "--volume-page",
        default=False,
        action="store_true",
        dest="volume_page",
        help="generate each volume as separate page",
    )

    epub_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the generated file using default program",
    )

    epub_parser.add_argument(
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

    epub_parser.add_argument(
        "-ps",
        "--paragraph_separator",
        dest="paragraph_separator",
        type=lambda value: value.encode("utf-8").decode("unicode_escape"),
        default="\n\n",
        help="paragraph separator (default: %(default)r)",
        metavar="SEPARATOR",
    )


def run(args: argparse.Namespace) -> None:
    """Run epub subcommand.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    input_sources = []

    if not sys.stdin.isatty():
        # piped input, use stdin as the single input source
        input_sources.append(sys.stdin)
    elif args.input_file:
        # multiple file(s)
        input_sources.extend(args.input_file)
    else:
        logger.error("No input files provided.")
        sys.exit(1)

    if len(input_sources) > 1 and args.output_file:
        logger.error(
            "Cannot specify a single output file when "
            "processing multiple input files."
        )
        sys.exit(1)

    for i, current_input_stream in enumerate(input_sources):
        # ensures that `input_file` and `output_file` are correctly isolated
        current_file_args = argparse.Namespace(**vars(args))
        current_file_args.input_file = current_input_stream

        # if an explicit output_file was provided, it must apply to the first
        # input
        if i > 0 and args.output_file:
            current_file_args.output_file = None

        book = parse_txt(current_file_args)
        writer = EpubWriter(book, current_file_args)
        writer.write()

        # close the file stream if it was opened by argparse.FileType and is
        # not sys.stdin.
        if current_input_stream is not sys.stdin:
            current_input_stream.close()
