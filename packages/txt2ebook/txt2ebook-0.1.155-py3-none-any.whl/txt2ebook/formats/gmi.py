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

"""Convert and back source text file into text as well."""

import logging
from pathlib import Path
from typing import List

from txt2ebook.formats.base import BaseWriter
from txt2ebook.helpers import lower_underscore
from txt2ebook.models import Chapter, Volume

logger = logging.getLogger(__name__)


class GmiWriter(BaseWriter):
    """Module for writing ebook in GemText (gmi) format."""

    def write(self) -> None:
        """Generate GemText files."""
        if self.config.split_volume_and_chapter:
            self._export_multiple_files()
        else:
            self._new_file()

    def _export_multiple_files(self) -> None:
        logger.info("Split multiple files")

        txt_filename = Path(self.config.input_file.name)
        export_filename = Path(
            txt_filename.resolve().parent.joinpath(
                self.config.output_folder,
                lower_underscore(
                    f"00_{txt_filename.stem}_" + self._("metadata") + ".gmi"
                ),
            )
        )
        export_filename.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Creating %s", export_filename)
        with open(export_filename, "w", encoding="utf8") as file:
            file.write(self._to_metadata_txt())

        sc_seq = 1
        if self.config.with_toc:
            export_filename = Path(
                txt_filename.resolve().parent.joinpath(
                    self.config.output_folder,
                    lower_underscore(
                        f"01_{txt_filename.stem}_" + self._("toc") + ".gmi"
                    ),
                )
            )
            export_filename.parent.mkdir(parents=True, exist_ok=True)
            logger.info("Creating %s", export_filename)
            with open(export_filename, "w", encoding="utf8") as file:
                file.write(self._to_toc("*", "# "))

            sc_seq = 2

        for section in self.book.toc:
            section_seq = str(sc_seq).rjust(2, "0")

            ct_seq = 0
            if isinstance(section, Volume):
                for chapter in section.chapters:
                    chapter_seq = str(ct_seq).rjust(2, "0")
                    filename = lower_underscore(
                        (
                            f"{section_seq}"
                            f"_{chapter_seq}"
                            f"_{txt_filename.stem}"
                            f"_{section.title}"
                            f"_{chapter.title}"
                            ".gmi"
                        )
                    )

                    export_filename = Path(
                        txt_filename.resolve().parent.joinpath(
                            self.config.output_folder, filename
                        )
                    )
                    export_filename.parent.mkdir(parents=True, exist_ok=True)
                    logger.info("Creating %s", export_filename)
                    with open(export_filename, "w", encoding="utf8") as file:
                        file.write(
                            self._to_volume_chapter_txt(section, chapter)
                        )
                    ct_seq = ct_seq + 1
            if isinstance(section, Chapter):
                filename = lower_underscore(
                    (f"{section_seq}_{txt_filename.stem}_{section.title}.gmi")
                )

                export_filename = Path(
                    txt_filename.resolve().parent.joinpath(
                        self.config.output_folder, filename
                    )
                )
                export_filename.parent.mkdir(parents=True, exist_ok=True)
                logger.info("Creating %s", export_filename)
                with open(export_filename, "w", encoding="utf8") as file:
                    file.write(self._to_chapter_txt(section))

            sc_seq = sc_seq + 1

    def _new_file(self) -> None:
        new_filename = self._output_filename(".gmi")
        new_filename.parent.mkdir(parents=True, exist_ok=True)

        with open(new_filename, "w", encoding="utf8") as file:
            logger.info("Generate GemText file: %s", new_filename.resolve())
            file.write(self._to_gmi())

        if self.config.open:
            self._open_file(new_filename)

    def _to_gmi(self) -> str:
        toc = self._to_toc("*", "# ") if self.config.with_toc else ""
        return self._to_metadata_txt() + toc + self._to_body_txt()

    def _to_body_txt(self) -> str:
        content = []
        for section in self.book.toc:
            if isinstance(section, Volume):
                content.append(self._to_volume_txt(section))
            if isinstance(section, Chapter):
                content.append(self._to_chapter_txt(section))

        return f"{self.config.paragraph_separator}".join(content)

    def _to_volume_txt(self, volume) -> str:
        return (
            f"# {volume.title}"
            + self.config.paragraph_separator
            + self.config.paragraph_separator.join(
                [
                    self._to_chapter_txt(chapter, True)
                    for chapter in volume.chapters
                ]
            )
        )

    def _to_chapter_txt(self, chapter, part_of_volume=False) -> str:
        header = "##" if part_of_volume else "#"
        return (
            f"{header} {chapter.title}"
            + self.config.paragraph_separator
            + self.config.paragraph_separator.join(
                self._remove_newline(chapter.paragraphs)
            )
        )

    def _to_volume_chapter_txt(self, volume, chapter) -> str:
        return (
            f"# {volume.title} {chapter.title}"
            + self.config.paragraph_separator
            + self.config.paragraph_separator.join(
                self._remove_newline(chapter.paragraphs)
            )
        )

    def _remove_newline(self, paragraphs) -> List:
        return list(map(lambda p: p.replace("\n", ""), paragraphs))
