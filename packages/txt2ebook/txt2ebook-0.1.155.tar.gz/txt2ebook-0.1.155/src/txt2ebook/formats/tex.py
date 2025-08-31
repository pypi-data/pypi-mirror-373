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

"""Convert source text file into tex format."""

import importlib.resources as importlib_res
import logging
import sys
from pathlib import Path

import importlib_resources
from pylatex import Command as Cmd
from pylatex import Document as Doc
from pylatex import NoEscape as NoEsc
from pylatex import Package as Pkg
from pylatex.section import Chapter as Chap
from pylatex.section import Part

from txt2ebook.formats.base import BaseWriter
from txt2ebook.models import Chapter, Volume

# workaround for Python 3.8
# see https://github.com/messense/typst-py/issues/12#issuecomment-1812956252
setattr(importlib_res, "files", importlib_resources.files)
setattr(importlib_res, "as_file", importlib_resources.as_file)

logger = logging.getLogger(__name__)


class TexWriter(BaseWriter):
    """Module for writing ebook in LaTeX (tex) format."""

    def __post_init__(self):
        """Post init code."""
        self.index_keywords = self.config.index_keyword + self.book.index
        logger.debug("Index keywords: %s", self.index_keywords)

    def write(self) -> None:
        """Generate TeX / PDF files."""
        new_filename = self._output_filename(".tex")
        new_filename.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Generate TeX file: %s", new_filename.resolve())

        doc = Doc(documentclass="ctexbook", document_options=[self._fontset()])

        doc.packages.append(Pkg("geometry", options=["a6paper"]))
        doc.packages.append(Pkg("makeidx"))
        doc.packages.append(Pkg("xcolor"))
        doc.packages.append(
            Pkg(
                "idxlayout",
                options=[
                    "columns=1",
                    "font=footnotesize",
                    "itemlayout=singlepar",
                    "indentunit=0pt",
                ],
            )
        )
        doc.packages.append(
            Pkg("hyperref", options=["colorlinks=true", "linktocpage=true"])
        )

        doc.packages.append(Pkg("tocloft", options=["titles"]))
        tocloft = NoEsc(
            r"""
        \renewcommand{\cftbeforepartskip}{1em}
        \renewcommand{\cftbeforechapskip}{0em}
        \renewcommand{\cftpartfont}{\normalfont\bfseries}
        \renewcommand{\cftchapfont}{\normalfont}
        \renewcommand{\cftchapleader}{\dotfill}
        \renewcommand{\cftpartpagefont}{\small\bfseries}
        \renewcommand{\cftchappagefont}{\small\bfseries}
        """
        )
        doc.preamble.append(tocloft)

        hide_section_seq = (
            r"chapter/name={},chapter/number={},part/name={},part/number={}"
        )
        doc.preamble.append(Cmd("ctexset", NoEsc(hide_section_seq)))
        doc.preamble.append(Cmd("title", self.book.title))
        doc.preamble.append(Cmd("author", ", ".join(self.book.authors)))
        doc.preamble.append(NoEsc(r"\date{}"))
        doc.preamble.append(Cmd("makeindex"))

        doc.append(NoEsc(r"\maketitle"))
        doc.append(NoEsc(r"\thispagestyle{empty}"))
        doc.append(NoEsc(r"\addtocontents{toc}{\protect\pagestyle{empty}}"))
        doc.append(
            NoEsc(r"\addtocontents{toc}{\protect\thispagestyle{empty}}")
        )
        doc.append(NoEsc(r"\tableofcontents"))
        doc.append(NoEsc(r"\pagestyle{empty}"))
        doc.append(NoEsc(r"\cleardoublepage"))
        doc.append(NoEsc(r"\pagenumbering{arabic}"))
        doc.append(NoEsc(r"\pagestyle{headings}"))

        for section in self.book.toc:
            if isinstance(section, Volume):
                with doc.create(Part(section.title, label=False)):
                    for chapter in section.chapters:
                        with doc.create(Chap(chapter.title, label=False)):
                            for paragraph in chapter.paragraphs:
                                par = self._process_paragraph(paragraph)
                                doc.append(NoEsc(rf"\par{{{par}}}"))

            if isinstance(section, Chapter):
                with doc.create(Chap(section.title, label=False)):
                    for paragraph in section.paragraphs:
                        par = self._process_paragraph(paragraph)
                        doc.append(NoEsc(rf"\par{{{par}}}"))

        doc.append(Cmd("printindex"))

        filename = str(new_filename.parent / new_filename.stem)
        pdf_filename = Path(filename).with_suffix(".pdf")
        doc.generate_pdf(
            filename, compiler="latexmk", clean_tex=self.config.clean_tex
        )
        logger.info("Generate PDF file: %s", pdf_filename.resolve())

        if self.config.open:
            self._open_file(pdf_filename)

    def _process_paragraph(self, paragraph) -> str:
        par = paragraph.strip()

        for keyword in self.index_keywords:
            par = par.replace(
                keyword,
                rf"\color{{red}}\index{{{keyword}}}{keyword}\color{{black}}",
            )

        return par

    def _fontset(self) -> str:
        if sys.platform == "linux":
            return "fontset=ubuntu"

        if sys.platform == "darwin":
            return "fontset=macos"

        if sys.platform == "windows":
            return "fontset=windows"

        return "fontset=ubuntu"
