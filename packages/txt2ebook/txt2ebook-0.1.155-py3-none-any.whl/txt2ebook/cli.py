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

"""txt2ebook/tte is a cli tool to convert txt file to ebook format.

website: https://github.com/kianmeng/txt2ebook
changelog: https://github.com/kianmeng/txt2ebook/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/txt2ebook/issues
"""

import argparse
import logging
import sys
from typing import Optional, Sequence

import txt2ebook.subcommands
from txt2ebook import __version__, setup_logger

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_FOLDER = "output"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="txt2ebook",
        add_help=False,
        description=__doc__,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=6
        ),
    )

    subparsers = parser.add_subparsers(
        help="sub-command help",
        dest="subcommand",
        required=True,
    )
    txt2ebook.subcommands.build_subparser(subparsers)

    parser.add_argument(
        "-of",
        "--output-folder",
        dest="output_folder",
        default=DEFAULT_OUTPUT_FOLDER,
        help="set default output folder (default: '%(default)s')",
    )

    parser.add_argument(
        "-p",
        "--purge",
        default=False,
        action="store_true",
        dest="purge",
        help=(
            "remove converted ebooks specified by --output-folder option "
            "(default: '%(default)s')"
        ),
    )

    parser.add_argument(
        "-l",
        "--language",
        dest="language",
        default=None,
        help="language of the ebook (default: '%(default)s')",
        metavar="LANGUAGE",
    )

    parser.add_argument(
        "-rw",
        "--raise-on-warning",
        default=False,
        action="store_true",
        dest="raise_on_warning",
        help="raise exception and stop parsing upon warning",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        default=False,
        action="store_true",
        dest="quiet",
        help="suppress all logging",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        dest="verbose",
        help="show verbosity of debugging log, use -vv, -vvv for more details",
    )

    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        dest="debug",
        help="show debugging log and stacktrace",
    )

    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show this help message and exit",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main(args: Optional[Sequence[str]] = None):
    """Set the main entrypoint of the CLI script."""
    args = args or sys.argv[1:]

    try:
        parser = build_parser()
        parsed_args = parser.parse_args(args)
        setup_logger(parsed_args)

        if parsed_args.subcommand is not None:
            logger.debug(parsed_args)
            if hasattr(parsed_args, "func"):
                parsed_args.func(parsed_args)
            else:
                logger.error(
                    "subcommand '%s' is missing its execution function.",
                    parsed_args.command,
                )
                parser.print_help(sys.stderr)

    except Exception as error:
        logger.error(
            "error: %s",
            getattr(error, "message", str(error)),
            exc_info=("-d" in args or "--debug" in args),
        )

        raise SystemExit(1) from None
