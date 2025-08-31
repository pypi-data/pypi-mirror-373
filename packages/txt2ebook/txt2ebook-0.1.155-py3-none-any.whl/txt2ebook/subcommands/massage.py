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

"""Massage subcommand."""

import argparse
import logging
import sys
from importlib import import_module
from pathlib import Path

import cjkwrap
import jieba.analyse
import regex as re
from bs4 import UnicodeDammit

from txt2ebook import detect_and_expect_language
from txt2ebook.exceptions import EmptyFileError
from txt2ebook.models.book import Book
from txt2ebook.zh_utils import zh_halfwidth_to_fullwidth, zh_words_to_numbers

logger = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    massage_parser = subparsers.add_parser(
        "massage", help="massage the source txt file"
    )

    massage_parser.add_argument(
        "input_file",
        nargs=None if sys.stdin.isatty() else "?",  # type: ignore
        type=argparse.FileType("rb"),
        default=None if sys.stdin.isatty() else sys.stdin,
        help="source text filename",
        metavar="TXT_FILENAME",
    )

    massage_parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="converted ebook filename (default: 'TXT_FILENAME.txt')",
        metavar="EBOOK_FILENAME",
    )

    massage_parser.add_argument(
        "-hn",
        "--header-number",
        default=False,
        action="store_true",
        dest="header_number",
        help="convert section header from words to numbers",
    )

    massage_parser.add_argument(
        "-fw",
        "--fullwidth",
        default=False,
        action="store_true",
        dest="fullwidth",
        help=(
            "use fullwidth character (only for zh-cn and zh-tw) "
            "(default: %(default)r)"
        ),
    )

    massage_parser.add_argument(
        "-ri",
        "--reindent",
        default=False,
        action="store_true",
        dest="reindent",
        help=(
            "reindent each paragraph (only for zh-cn and zh-tw) "
            "(default: %(default)r)"
        ),
    )

    massage_parser.add_argument(
        "-ps",
        "--paragraph_separator",
        dest="paragraph_separator",
        type=lambda value: value.encode("utf-8").decode("unicode_escape"),
        default="\n\n",
        help="paragraph separator (default: %(default)r)",
        metavar="SEPARATOR",
    )

    massage_parser.add_argument(
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

    massage_parser.add_argument(
        "-ow",
        "--overwrite",
        default=False,
        action="store_true",
        dest="overwrite",
        help="overwrite massaged TXT_FILENAME",
    )

    massage_parser.add_argument(
        "-rd",
        "--regex-delete",
        dest="re_delete",
        default=[],
        action="append",
        help="regex to delete word or phrase (default: '%(default)s')",
        metavar="REGEX",
    )

    massage_parser.add_argument(
        "-rr",
        "--regex-replace",
        dest="re_replace",
        nargs=2,
        default=[],
        action="append",
        help="regex to search and replace (default: '%(default)s')",
        metavar="REGEX",
    )

    massage_parser.add_argument(
        "-rl",
        "--regex-delete-line",
        dest="re_delete_line",
        default=[],
        action="append",
        help="regex to delete whole line (default: '%(default)s')",
        metavar="REGEX",
    )

    massage_parser.add_argument(
        "-w",
        "--width",
        dest="width",
        type=int,
        default=None,
        help="width for line wrapping",
        metavar="WIDTH",
    )

    massage_parser.add_argument(
        "-ss",
        "--sort-volume-and-chapter",
        default=False,
        action="store_true",
        dest="sort_volume_and_chapter",
        help="short volume and chapter",
    )

    massage_parser.add_argument(
        "-sn",
        "--single-newline",
        default=False,
        action="store_true",
        dest="single_newline",
        help="format paragraph by single newline",
    )

    massage_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the generated file using default program",
    )

    massage_parser.add_argument(
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
    )

    massage_parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Run massage subcommand.

    Args:
        args (argparse.Namespace): args.from command line arguments

    Returns:
        None
    """
    massaged_txt = massage_txt(args)
    if args.overwrite:
        _overwrite_file(args, massaged_txt)
    else:
        _new_file(args, massaged_txt)

    # args.language = detect_and_expect_language(massaged_txt, args.language)
    # config_lang = args.language.replace("-", "_")
    # langconf = import_module(f"txt2ebook.languages.{config_lang}")
    # args.with_toc = False
    # parser = Parser(massaged_txt, args, langconf)
    # book = parser.parse()

    # if args.debug:
    #     book.debug(args.verbose)

    # if args.header_number:
    #     book = header_number(args, book)

    # writer = TxtWriter(book, args)
    # writer.write()


def _overwrite_file(args, massaged_txt) -> None:
    txt_filename = Path(args.input_file.name)

    with open(txt_filename, "w", encoding="utf8") as file:
        file.write(massaged_txt)
        logger.info("Overwrite txt file: %s", txt_filename.resolve())


def _new_file(args, massaged_txt) -> None:
    txt_filename = Path(args.input_file.name)
    export_filename = Path(
        txt_filename.resolve().parent.joinpath(
            args.output_folder, txt_filename.name
        )
    )
    export_filename.parent.mkdir(parents=True, exist_ok=True)

    with open(export_filename, "w", encoding="utf8") as file:
        file.write(massaged_txt)
        logger.info("New txt file: %s", export_filename.resolve())


def header_number(args: argparse.Namespace, book: Book) -> Book:
    """Convert header number from words to numbers."""
    stats = book.stats()

    seq_lengths = {
        "Volume": len(str(stats.get("Volume", 2))),
        "Chapter": len(str(stats.get("Chapter", 2))),
    }

    for toc_item in book.toc:
        toc_type = type(toc_item).__name__
        if toc_type in seq_lengths:
            toc_item.title = words_to_nums(
                args, toc_item.title, seq_lengths[toc_type]
            )

    return book


def words_to_nums(args: argparse.Namespace, words: str, length: int) -> str:
    """Convert header from words to numbers.

    For example, `第一百零八章` becomes `第108章`.

    Args:
        words(str): The line that contains section header in words.
        length(int): The number of left zero-padding to prepend.

    Returns:
        str: The formatted section header.
    """
    config_lang = args.language.replace("-", "_")
    langconf = import_module(f"txt2ebook.languages.{config_lang}")

    if args.language not in ("zh-cn", "zh-tw"):
        return words

    # left pad the section number if found as halfwidth integer
    match = re.match(rf"第([{langconf.HALFWIDTH_NUMS}]*)", words)
    if match and match.group(1) != "":
        header_nums = match.group(1)
        return words.replace(header_nums, str(header_nums).rjust(length, "0"))

    # left pad the section number if found as fullwidth integer
    match = re.match(rf"第([{langconf.FULLWIDTH_NUMS}]*)", words)
    if match and match.group(1) != "":
        header_nums = match.group(1)
        return words.replace(header_nums, str(header_nums).rjust(length, "０"))

    replaced_words = zh_words_to_numbers(words, length=length)

    if args.fullwidth:
        replaced_words = zh_halfwidth_to_fullwidth(replaced_words)

    logger.debug(
        "Convert header to numbers: %s -> %s",
        words[:10],
        replaced_words[:10],
    )
    return replaced_words


def massage_txt(args: argparse.Namespace) -> str:
    """Massage the text file."""
    logger.info("Parsing txt file: %s", args.input_file.name)

    unicode = UnicodeDammit(args.input_file.read())
    logger.info("Detect encoding : %s", unicode.original_encoding)

    content = unicode.unicode_markup
    if not content:
        raise EmptyFileError(f"Empty file content in {args.input_file.name}")

    content = to_unix_newline(content)

    args.language = detect_and_expect_language(content, args.language)

    (metadata, body) = extract_metadata_and_body(args, content)

    if args.fullwidth and args.language in ("zh-cn", "zh-tw"):
        logger.info("Convert halfwidth ASCII characters to fullwidth")
        body = zh_halfwidth_to_fullwidth(body)

    if args.reindent and args.language in ("zh-cn", "zh-tw"):
        logger.info("Reindent paragraph")
        body = do_reindent_paragraph(args, body)

    if args.re_delete:
        body = do_delete_regex(args, body)

    if args.re_replace:
        body = do_replace_regex(args, body)

    if args.re_delete_line:
        body = do_delete_line_regex(args, body)

    if args.single_newline:
        body = do_single_newline(args, body)

    if args.width:
        body = do_wrapping(args, body)

    return f"{metadata}{body}"


def to_unix_newline(content: str) -> str:
    """Convert all other line ends to Unix line end.

    Args:
        content(str): The formatted book content.

    Returns:
        str: The formatted book content.
    """
    return content.replace("\r\n", "\n").replace("\r", "\n")

def do_reindent_paragraph(args, content: str) -> str:
    """Reindent each paragraph.

    Args:
        content(str): The formatted book content.

    Returns:
        str: The formatted book content.
    """
    paragraphs = re.split(r'\n\s*\n+', content)
    reindented_paragraphs = []
    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        reindented_lines = []
        for line in lines:
            stripped_line = line.strip()
            reindented_lines.append(stripped_line)

        reindented_paragraph = '\n'.join(reindented_lines)
        reindented_paragraph = "　　" + reindented_paragraph
        reindented_paragraphs.append(reindented_paragraph)

    return args.paragraph_separator.join(reindented_paragraphs)


def do_delete_regex(args, content: str) -> str:
    """Remove words/phrases based on regex.

    Args:
        content(str): The formatted book content.

    Returns:
        str: The formatted book content.
    """
    for delete_regex in args.re_delete:
        content = re.sub(
            re.compile(rf"{delete_regex}", re.MULTILINE), "", content
        )
    return content


def do_replace_regex(args, content: str) -> str:
    """Replace words/phrases based on regex.

    Args:
        content(str): The formatted book content.

    Returns:
        str: The formatted book content.
    """
    regex = args.re_replace
    if isinstance(regex, list):
        for search, replace in regex:
            content = re.sub(
                re.compile(rf"{search}", re.MULTILINE),
                rf"{replace}",
                content,
            )

    return content


def do_delete_line_regex(args, content: str) -> str:
    """Delete whole line based on regex.

    Args:
        content(str): The formatted book content.

    Returns:
        str: The formatted book content.
    """
    for delete_line_regex in args.re_delete_line:
        content = re.sub(
            re.compile(rf"^.*{delete_line_regex}.*$", re.MULTILINE),
            "",
            content,
        )
    return content


def extract_metadata_and_body(_args, content: str) -> tuple:
    """Extract the metadata and body.

    Args:
        content (str): The formatted book content.

    Returns:
        tuple: The metadata and body content.
    """
    metadata = ""
    body = ""
    match = re.search(r"---(.*?)---", content, re.DOTALL)
    if match:
        metadata = match.group(0).strip()
        body = content.replace(metadata, "", 1)


    metadata_block = metadata.split("---")[1]

    metadata_dict = {}
    for line in metadata_block.strip().splitlines():
        key, value = line.split("：", 1)
        metadata_dict[key.strip()] = value.strip()

    tags = jieba.analyse.extract_tags(content, topK=100)
    metadata_tags = " ".join(tags)
    logger.info("tags: %s", metadata_tags)
    metadata_dict["索引"] = metadata_tags

    meta_lines = [f"{key}：{value}" for key, value in metadata_dict.items()]
    meta_body = "\n".join(meta_lines)
    meta_str = f"---\n{meta_body}\n---"

    return (meta_str, body)


def do_single_newline(args, content: str) -> str:
    """Set single newline.

    Args:
        content (str): The formatted book content.

    Returns:
        str: The formatted book content.
    """
    modified_content = re.sub(r"\n+", "\n\n", content)
    return modified_content


def do_wrapping(args, content: str) -> str:
    """Wrap or fill CJK text.

    Args:
        content (str): The formatted book content.

    Returns:
        str: The formatted book content.
    """
    logger.info("Wrapping paragraph to width: %s", args.width)

    paragraphs = []
    # We don't remove empty line and keep all formatting as it.
    for paragraph in content.split("\n"):
        paragraph = paragraph.strip()

        lines = cjkwrap.wrap(paragraph, width=args.width)
        paragraph = "\n".join(lines)
        paragraphs.append(paragraph)

    wrapped_content = "\n".join(paragraphs)
    return wrapped_content
