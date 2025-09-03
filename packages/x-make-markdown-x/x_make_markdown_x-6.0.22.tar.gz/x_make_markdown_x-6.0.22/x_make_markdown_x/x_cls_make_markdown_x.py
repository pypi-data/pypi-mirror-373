from __future__ import annotations

"""Markdown document builder with optional PDF generation.

Features (redrabbit):
- Headers with hierarchical numbering and TOC entries
- Paragraphs, tables, images, lists
- Optional PDF export using wkhtmltopdf via pdfkit
"""

import importlib
from typing import Any

"""red rabbit 2025_0902_0944"""


class x_cls_make_markdown_x:
    """A simple markdown builder with an optional PDF export step."""

    def __init__(self, wkhtmltopdf_path: str | None = None) -> None:
        self.elements: list[str] = []
        self.toc: list[str] = []
        self.section_counter: list[int] = []
        self.wkhtmltopdf_path: str | None = wkhtmltopdf_path

    def add_header(self, text: str, level: int = 1) -> None:
        """Add a header with hierarchical numbering and TOC update."""
        if level > 6:
            raise ValueError("Header level cannot exceed 6.")

        # Update section counter
        while len(self.section_counter) < level:
            self.section_counter.append(0)
        self.section_counter = self.section_counter[:level]
        self.section_counter[-1] += 1

        # Generate section index
        section_index = ".".join(map(str, self.section_counter))
        header_text = f"{section_index} {text}"

        # Add header to elements and TOC
        self.elements.append(f"{'#' * level} {header_text}\n")
        self.toc.append(
            f"{'  ' * (level - 1)}- [{header_text}](#{header_text.lower().replace(' ', '-').replace('.', '')})"
        )

    def add_paragraph(self, text: str) -> None:
        """Add a paragraph to the markdown document."""
        self.elements.append(f"{text}\n\n")

    def add_table(self, headers: list[str], rows: list[list[str]]) -> None:
        """Add a table to the markdown document."""
        header_row = " | ".join(headers)
        separator_row = " | ".join(["---"] * len(headers))
        data_rows = "\n".join([" | ".join(row) for row in rows])
        self.elements.append(f"{header_row}\n{separator_row}\n{data_rows}\n\n")

    def add_image(self, alt_text: str, url: str) -> None:
        """Add an image to the markdown document."""
        self.elements.append(f"![{alt_text}]({url})\n\n")

    def add_list(self, items: list[str], ordered: bool = False) -> None:
        """Add a list to the markdown document."""
        if ordered:
            self.elements.extend([f"{i + 1}. {item}" for i, item in enumerate(items)])
        else:
            self.elements.extend([f"- {item}" for item in items])
        self.elements.append("\n")

    def add_toc(self) -> None:
        """Add a table of contents (TOC) to the top of the document."""
        self.elements = ["\n".join(self.toc) + "\n\n", *self.elements]

    def generate(self, output_file: str = "example.md") -> str:
        """Generate markdown and save it to a file; optionally render a PDF."""
        markdown_content = "".join(self.elements)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Convert to PDF if wkhtmltopdf_path is provided
        if self.wkhtmltopdf_path:
            try:
                _pdfkit: Any = importlib.import_module("pdfkit")
                _markdown: Any = importlib.import_module("markdown")
            except Exception:
                # pdfkit/markdown not available; skip PDF generation gracefully
                return markdown_content

            pdf_file = output_file.replace(".md", ".pdf")
            html_content = _markdown.markdown(markdown_content)
            pdfkit_config = _pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
            _pdfkit.from_string(html_content, pdf_file, configuration=pdfkit_config)

        return markdown_content


if __name__ == "__main__":
    # Library module; not intended to be run directly.
    raise SystemExit(0)
