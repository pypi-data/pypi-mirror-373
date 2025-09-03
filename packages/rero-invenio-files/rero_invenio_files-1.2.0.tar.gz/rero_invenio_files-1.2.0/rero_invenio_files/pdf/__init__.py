# RERO-Invenio-Files
# Copyright (C) 2024 RERO.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""PDF support module for RERO Invenio instances."""

import os
import random
import textwrap
from pathlib import Path

from fpdf import FPDF
from PIL import Image


class PDFGenerator(FPDF):
    """Class to generate PDFs for RERO Invenio with custom headers, footers, text, and images."""

    def __init__(self, data, *arg, **kwargs):
        """Initialize the PDFGenerator instance with content, fonts, logo, and graph.

        Example of input data:
        PDFGenerator(
            data={
                'title': 'Example document',
                'authors': ['Author1', 'Author2'],
                'summary': 'Summary text here'
            }
        )

        :param data: dict - the given data.
        """
        self.data = data

        current_dir = Path(__file__).parent
        font_dir = current_dir / "fonts"

        super().__init__(*arg, **kwargs)

        # Load custom fonts
        self.add_font("NotoSans", style="", fname=str(font_dir / "NotoSans-Regular.ttf"))
        self.add_font("NotoSans", style="I", fname=str(font_dir / "NotoSans-Italic.ttf"))
        self.add_font("NotoSans", style="B", fname=str(font_dir / "NotoSans-Bold.ttf"))
        self.add_font("NotoSans", style="BI", fname=str(font_dir / "NotoSans-BoldItalic.ttf"))

        logo_folder = current_dir / "logos"
        graph_folder = current_dir / "graphs"

        self.logo_path = self._select_random_file(logo_folder, [".png", ".jpg", ".jpeg"])
        self.graph_path = self._select_random_file(graph_folder, [".png", ".jpg", ".jpeg"])

    def _select_random_file(self, folder_path, extensions):
        """Select a random file from a folder with the specified extensions."""
        if not folder_path.exists():
            return None
        files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in extensions]
        return str(random.choice(files)) if files else None

    def header(self):
        """Draw the PDF header including logo and header text."""
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=self.l_margin, y=10, w=20)
        self.set_font("NotoSans", size=14)
        self.set_xy(self.l_margin + 25, 10)
        self.cell(
            0,
            10,
            self.data.get("header", "Generated using RERO Invenio Files"),
            align="L",
            border="B",
        )
        self.ln(20)

    def footer(self):
        """Draw the PDF footer with a separating line and page numbers."""
        self.set_y(-15)
        self.set_font("NotoSans", "I", 8)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="R")

    def render(self):
        """Generate the main content of the PDF including title, authors, summary, paragraph, and graph."""
        self.add_page()

        # Add title
        if title := self.data.get("title"):
            self.set_font("NotoSans", size=24)
            self.multi_cell(0, 8, title, align="C")
            self.ln(4)

        # Add authors
        if authors := self.data.get("authors"):
            self.set_font("NotoSans", "I", 14)
            self.multi_cell(0, 6, "; ".join(authors), align="C")
            self.ln(4)

        # Add summary text with a background box
        summary_height = 0
        if summary := self.data.get("summary"):
            page_width = self.w - 2 * self.l_margin
            x = self.l_margin
            y = self.get_y()
            padding_top = 5
            padding_bottom = 5
            padding_sides = 10
            line_height = 6

            self.set_font("NotoSans", size=12)
            self.set_xy(x + padding_sides, y + padding_top)
            start_y = self.get_y()
            self.multi_cell(page_width - 2 * padding_sides, line_height, summary, align="J")
            end_y = self.get_y()

            text_height = end_y - start_y
            summary_height = text_height + padding_top + padding_bottom

            # Draw background rectangle for summary
            self.set_fill_color(230, 230, 230)
            self.rect(x, y, page_width, summary_height, style="F")

            self.set_xy(x + padding_sides, y + padding_top)
            self.multi_cell(page_width - 2 * padding_sides, line_height, summary, align="J")

        # Calculate available space for paragraph
        graph_h = (self.w - 2 * self.l_margin - 20) * 0.5
        graph_y = self.h - self.b_margin - graph_h - 10
        top_y = self.get_y()
        available_height = graph_y - top_y

        # Add paragraph with identical top and bottom spacing, justified
        self._add_paragraph_fixed_height(max_height=available_height, top_padding=5)

        # Add the graph at the bottom if available
        self._add_graphic_fixed_bottom()

    def _add_paragraph_fixed_height(self, max_height, top_padding=5):
        """Add a paragraph block with fixed height, justified, and invisible background.

        :param max_height: int - maximum height (in points) allowed for the paragraph block.
        :param top_padding: int - optional top padding (default: 5).
        """
        self.set_font("NotoSans", size=11)
        text = self.data.get(
            "paragraph",
            "Lorem ipsum placeholder text.",
        )

        page_width = self.w - 2 * self.l_margin
        x = self.l_margin
        y = self.get_y()
        padding_sides = 10
        line_height = 6
        padding_bottom = top_padding

        # Set cursor at top of paragraph
        self.set_xy(x + padding_sides, y + top_padding)

        # Wrap text to fit width
        wrapped_lines = textwrap.wrap(text, width=95)

        # Calculate max lines to fit the available height
        max_lines = int((max_height - top_padding - padding_bottom) / line_height)

        # Truncate one line earlier to avoid partial lines
        if max_lines > 0:
            max_lines -= 1

        wrapped_lines = wrapped_lines[:max_lines]

        # Justified text
        self.multi_cell(page_width - 2 * padding_sides, line_height, " ".join(wrapped_lines), align="J")

        # Move Y to the bottom of paragraph space
        self.set_y(y + max_height)

    def _add_graphic_fixed_bottom(self):
        """Add a graphic image at a fixed position near the bottom of the page."""
        if not self.graph_path or not os.path.exists(self.graph_path):
            return

        chart_w = self.w - 2 * self.l_margin - 20
        chart_h = chart_w * 0.5
        chart_x = self.l_margin + 10
        chart_y = self.h - self.b_margin - chart_h - 10

        # Draw background rectangle for graph
        self.set_fill_color(245, 245, 245)
        self.rect(chart_x - 3, chart_y - 3, chart_w + 6, chart_h + 6, style="F")

        # Open image and preserve aspect ratio
        with Image.open(self.graph_path) as img:
            orig_w, orig_h = img.size
            ratio = orig_h / orig_w
            new_h = chart_w * ratio
            if new_h > chart_h:
                new_h = chart_h
                new_w = chart_h / ratio
            else:
                new_w = chart_w

        # Center image inside rectangle
        img_x = chart_x + (chart_w - new_w) / 2
        img_y = chart_y + (chart_h - new_h) / 2
        self.image(self.graph_path, x=img_x, y=img_y, w=new_w, h=new_h)

        # Ensure text cursor does not overlap graph
        if self.get_y() < chart_y - 5:
            self.set_y(chart_y - 5)
