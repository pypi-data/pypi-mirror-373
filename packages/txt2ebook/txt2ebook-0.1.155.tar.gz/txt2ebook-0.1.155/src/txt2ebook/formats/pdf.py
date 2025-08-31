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
from typing import List, Tuple

import reportlab
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents

from txt2ebook.formats.base import BaseWriter
from txt2ebook.models import Chapter, Volume

logger = logging.getLogger(__name__)


class PdfDocTemplate(SimpleDocTemplate):
    """Custom PDF template."""

    def afterFlowable(self, flowable):
        """Registers TOC entries."""
        if flowable.__class__.__name__ == "Paragraph":
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == "Heading1":
                key = f"h1-{self.seq.nextf('heading1')}"
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (0, text, self.page, key))
            if style == "Heading2":
                key = f"h2-{self.seq.nextf('heading2')}"
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (2, text, self.page, key))


class PdfWriter(BaseWriter):
    """Module for writing ebook in PDF format."""

    def __post_init__(self):
        """Post init code."""
        pdf_filename = self._output_filename(".pdf")
        logger.info("Create pdf file: %s", pdf_filename.resolve())

        self._init_styles()
        self.doc = PdfDocTemplate(
            str(pdf_filename),
            pagesize=self._get_pagesize(),
            title=self.book.title,
            author=", ".join(self.book.authors),
            showBoundary=self.config.debug,
            warnOnMissingFontGlyphs=self.config.debug,
            verbose=self.config.debug,
        )

    def write(self) -> None:
        """Generate PDF files."""
        pdf = []
        pdf.extend(self._toc_page())

        for section in self.book.toc:
            if isinstance(section, Volume):
                self.to_volume(pdf, section)
            if isinstance(section, Chapter):
                self.to_chapter(pdf, section)

        self.doc.multiBuild(
            pdf, onFirstPage=self._cover_page, onLaterPages=self._regular_page
        )

        if self.config.open:
            self._open_file(Path(self.doc.filename))

    def _cover_page(self, canvas, _doc) -> None:
        (page_width, page_height) = self._get_pagesize()
        canvas.saveState()
        canvas.setFont(self.langconf.DEFAULT_PDF_FONT_NAME, 28)
        canvas.drawCentredString(
            page_width / 2.0,
            page_height - (page_height / 3.0),
            self.book.title,
        )
        canvas.setFont(self.langconf.DEFAULT_PDF_FONT_NAME, 14)
        canvas.drawCentredString(
            page_width / 2.0,
            page_height - (page_height / 3.0 * 2),
            ", ".join(self.book.authors),
        )
        canvas.restoreState()
        canvas.showPage()

    def _toc_page(self) -> List:
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(
                name="TOCHeading1",
                fontName=self.langconf.DEFAULT_PDF_FONT_NAME,
                fontSize=self.langconf.DEFAULT_PDF_FONT_SIZE,
                firstLineIndent=0,
                leftIndent=0,
            ),
            ParagraphStyle(
                name="TOCHeading2",
                fontName=self.langconf.DEFAULT_PDF_FONT_NAME,
                fontSize=self.langconf.DEFAULT_PDF_FONT_SIZE,
                firstLineIndent=0,
                leftIndent=-(self.langconf.DEFAULT_PDF_FONT_SIZE * 4 - 4),
            ),
        ]
        return [
            self.to_title(self._("toc")),
            toc,
            PageBreak(),
        ]

    def _regular_page(self, canvas, doc) -> None:
        canvas.saveState()

        style = ParagraphStyle(
            name="footer",
            fontName=self.langconf.DEFAULT_PDF_FONT_NAME,
            fontSize=self.langconf.DEFAULT_PDF_FONT_SIZE,
            alignment=TA_RIGHT,
            rightIndent=18,
        )

        if self.config.debug:
            style.borderColor = "#000000"

        footer = Paragraph(f"{doc.page}", style=style)
        footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, doc.bottomMargin - cm)

        canvas.restoreState()

    def _get_pagesize(self) -> Tuple:
        page_size = (
            self.config.page_size or self.langconf.DEFAULT_PDF_PAGE_SIZE
        )
        return portrait(getattr(reportlab.lib.pagesizes, page_size.upper()))

    def _init_styles(self) -> None:
        pdfmetrics.registerFont(
            TTFont(
                self.langconf.DEFAULT_PDF_FONT_NAME,
                self.langconf.DEFAULT_PDF_FONT_FILE,
            )
        )

        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name=self.config.language,
                fontName=self.langconf.DEFAULT_PDF_FONT_NAME,
                fontSize=12,
                spaceAfter=12,
                leading=16,
                firstLineIndent=24,
            )
        )

    def to_title(self, words: str, style: str = "title") -> str:
        """Create the title for the section."""
        font_name = self.langconf.DEFAULT_PDF_FONT_NAME
        return Paragraph(
            f"<font name='{font_name}'>{words}</font>",
            self.styles[style],
        )

    def to_volume(self, pdf, volume) -> None:
        """Generate each volume."""
        logger.info("Create PDF volume : %s", volume.title)

        pdf.append(self.to_title(volume.title, "Heading1"))
        pdf.append(PageBreak())

        for chapter in volume.chapters:
            self.to_chapter(pdf, chapter, True)

    def to_chapter(self, pdf, chapter, under_volume=False) -> None:
        """Generate each chapter."""
        logger.info("Create PDF chapter : %s", chapter.title)

        style = "Heading2" if under_volume else "Heading1"
        pdf.append(self.to_title(chapter.title, style))

        for paragraph in chapter.paragraphs:
            pdf.append(
                Paragraph(
                    paragraph.replace("\n", ""),
                    self.styles[self.config.language],
                )
            )
        pdf.append(PageBreak())
