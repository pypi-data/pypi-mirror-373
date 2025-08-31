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

"""Abstract class for all supported formats."""

import argparse
import gettext
import io
import logging
import os
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from importlib import import_module
from pathlib import Path

from txt2ebook.helpers import lower_underscore
from txt2ebook.models import Book, Chapter, Volume

logger = logging.getLogger(__name__)


class BaseWriter(ABC):
    """Base class for writing to ebook format."""

    def __init__(self, book: Book, opts: argparse.Namespace) -> None:
        """Create a Writer module.

        Args:
            book(Book): The book model which contains metadata and table of
            contents of volumes and chapters.
            opts(argparse.Namespace): The configs from the command-line.

        Returns:
            None
        """
        self.book = book
        self.config = opts

        config_lang = self.config.language.replace("-", "_")
        self.langconf = import_module(f"txt2ebook.languages.{config_lang}")

        if not self.config.output_file:
            self._refresh_output_folder()

        self._load_translation()
        self.__post_init__()

    def _load_translation(self):
        localedir = Path(Path(__file__).parent.parent, "locales")
        translation = gettext.translation(
            "txt2ebook", localedir=localedir, languages=[self.config.language]
        )
        self._ = translation.gettext

    def _open_file(self, filename):
        if sys.platform == "linux":
            subprocess.call(["xdg-open", filename])
        elif sys.platform == "darwin":
            subprocess.call(["open", filename])
        elif sys.platform == "windows":
            os.startfile(filename)

        logger.info("Open file: %s using default program.", filename.resolve())

    def _refresh_output_folder(self):
        cwd = self._output_folder()
        if self.config.purge and cwd.exists():
            if self.config.yes:
                logger.debug("Purge output folder: %s", cwd.absolute())
                shutil.rmtree(cwd)
            else:
                answer = input(
                    f"Are you sure to purge output folder: {cwd.absolute()}? [y/N] "
                )
                if answer.lower() == "y":
                    logger.debug("Purge output folder: %s", cwd.absolute())
                    shutil.rmtree(cwd)

        logger.debug("Create output folder: %s", cwd)
        cwd.mkdir(parents=True, exist_ok=True)

    def _output_folder(self) -> Path:
        """Get the current working directory.

        Returns:
            Path
        """
        output_folder = Path(self.config.output_folder)
        if output_folder.is_absolute():
            return output_folder

        return Path(os.getcwd(), self.config.output_folder)

    def _output_filename(self, extension: str) -> Path:
        filename = "default"
        if self.config.filename_format:
            filename = self.book.filename_format(self.config.filename_format)
        else:
            if self.config.output_file:
                filename = str(self.config.output_file)
            elif isinstance(
                self.config.input_file, (io.TextIOWrapper, io.BufferedReader)
            ):
                if self.config.input_file.name != "<stdin>":
                    filename = self.config.input_file.name
                # input from redirection or piping
                elif self.book.title:
                    filename = self.book.title

        file = Path(filename)

        # do not create to output folder when we explicit set the output path
        # and file
        if self.config.output_file:
            return Path(file.parent, lower_underscore(file.stem)).with_suffix(
                extension
            )

        return Path(
            file.parent, self.config.output_folder, lower_underscore(file.stem)
        ).with_suffix(extension)

    def _to_metadata_txt(self) -> str:
        metadata = [
            self._("title:") + self.book.title,
            self._("author:") + "，".join(self.book.authors),
            self._("translator:") + "，".join(self.book.translators),
            self._("tag:") + "，".join(self.book.tags),
        ]
        return (
            "---\n"
            + "\n".join(metadata)
            + "\n---"
            + self.config.paragraph_separator
        )

    def _to_toc(self, list_symbol, header_symbol="") -> str:
        toc = ""
        toc += header_symbol + self._("toc") + "\n"

        for section in self.book.toc:
            if isinstance(section, Volume):
                toc += f"\n{list_symbol} " + section.title
                for chapter in section.chapters:
                    toc += f"\n  {list_symbol} " + chapter.title
            if isinstance(section, Chapter):
                toc += f"\n{list_symbol} " + section.title

        return toc + self.config.paragraph_separator

    @abstractmethod
    def write(self) -> None:
        """Generate text files."""

    def __post_init__(self) -> None:
        """Post init code for child class."""
