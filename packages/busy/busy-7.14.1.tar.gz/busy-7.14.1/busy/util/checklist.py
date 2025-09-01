# Prototype of how to generate a PDF

from subprocess import run
from pathlib import Path
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from datetime import date
import re
from time import sleep

from reportlab.lib.pagesizes import letter as LETTER
from reportlab.lib.units import inch as INCH
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics


@dataclass
class Checklist:  # pragma: nocover

    filenamestem: str = None
    pagesize: tuple = LETTER
    margin: float = 1.0 * INCH
    fontname_items: str = "Helvetica"
    fontname_heading: str = "Helvetica-Bold"
    fontsize_items: float = 12.0
    fontsize_heading: float = 24.0
    lineheight_items: float = 14.0
    paragap: float = 8.0
    checkbox_size: float = 14.0

    @property
    def topy(self):
        return self.pagesize[1] - self.margin

    @property
    def indent(self):
        return self.checkbox_size * 1.5

    def wrap(self, text: str) -> list:
        textwidth = self.pagesize[0] - 2.0 * self.margin - self.indent
        lines = []
        words = text.split()
        line = ""
        while words:
            word = words.pop(0)
            newwidth = pdfmetrics.stringWidth(line + " " + word,
                                              self.fontname_items,
                                              self.fontsize_items)
            if newwidth <= textwidth:
                line += " " + word
            else:
                lines.append(line)
                line = word
        lines.append(line)
        return lines

    def print_checkbox(self, canvas: Canvas, x, y):
        """y is the baseline"""
        ascent = pdfmetrics.getAscent(self.fontname_items, self.fontsize_items)
        y = y - (self.lineheight_items - ascent) / 2.0
        canvas.rect(x, y, self.checkbox_size, self.checkbox_size)

    def print(self, canvas: Canvas, text: str, y) -> int:
        """Add an item to the document and return the new y-coordinate"""
        lines = self.wrap(text)
        if y - len(lines) * self.lineheight_items < self.margin:
            canvas.showPage()
            heading = f"Page {canvas.getPageNumber()}"
            canvas.setFont(self.fontname_heading, self.fontsize_items)
            canvas.drawString(self.margin, self.topy, heading)
            y = self.topy - self.lineheight_items - self.paragap
        self.print_checkbox(canvas, self.margin, y)
        canvas.setFont(self.fontname_items, self.fontsize_items)
        while lines:
            line = lines.pop(0)
            canvas.drawString(self.margin + self.indent, y, line)
            y = y - self.lineheight_items
        return y - self.paragap

    def print_pdf(filepath):
        fullpath = Path(filepath).absolute()
        applescript_cmd = f'tell application "Preview" to ' + \
            f'print POSIX file "{fullpath}"'
        run(['osascript', '-e', applescript_cmd])

    def generate(self, heading: str, items: list):
        datestring = date.today().strftime('%Y%m%d')
        if not (stem := self.filenamestem):
            stem1 = re.sub(r'\W+', '-', heading.lower())
            stem = re.sub(r'\-$', '', stem1)
        with TemporaryDirectory() as dir:
            filepath = Path(dir) / f"{datestring}-{stem}.pdf"
            canvas = Canvas(str(filepath), pagesize=self.pagesize)
            canvas.setFont(self.fontname_heading, self.fontsize_heading)
            canvas.drawString(self.margin, self.topy, heading)
            y = self.topy - self.fontsize_heading - self.paragap
            for item in items:
                y = self.print(canvas, item.capitalize(), y)
            canvas.save()
            run(['open', filepath.absolute()])
            sleep(1)  # A hack to give Preview time to open the temp file
