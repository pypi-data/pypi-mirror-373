"""
docstr
"""
import markdown
import pdfkit
##find wkhtmltopdf.exe


class x_cls_make_markdown_x:
    """
    A Swiss Army knife for creating majestic markdown documents using the factory design pattern.
    Supports tables, images, table of contents (TOC), headers, lists, and more.

    Note:
    - This script optionally requires `wkhtmltopdf` to be installed for PDF generation.
    - If the path to `wkhtmltopdf` is not provided, the PDF will not be generated.
    """

    def __init__(self, wkhtmltopdf_path=None):
        self.elements = []
        self.toc = []
        self.section_counter = []
        self.wkhtmltopdf_path = wkhtmltopdf_path

    def add_header(self, text, level=1):
        """Add a header to the markdown document with section indices and TOC update."""
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

    def add_paragraph(self, text):
        """Add a paragraph to the markdown document."""
        self.elements.append(f"{text}\n\n")

    def add_table(self, headers, rows):
        """Add a table to the markdown document."""
        header_row = " | ".join(headers)
        separator_row = " | ".join(["---"] * len(headers))
        data_rows = "\n".join([" | ".join(row) for row in rows])
        self.elements.append(f"{header_row}\n{separator_row}\n{data_rows}\n\n")

    def add_image(self, alt_text, url):
        """Add an image to the markdown document."""
        self.elements.append(f"![{alt_text}]({url})\n\n")

    def add_list(self, items, ordered=False):
        """Add a list to the markdown document."""
        if ordered:
            self.elements.extend([f"{i+1}. {item}" for i, item in enumerate(items)])
        else:
            self.elements.extend([f"- {item}" for item in items])
        self.elements.append("\n")

    def add_toc(self):
        """Add a table of contents (TOC) to the markdown document."""
        self.elements = ["\n".join(self.toc) + "\n\n"] + self.elements

    def generate(self, output_file="example.md"):
        """Generate the final markdown document as a string and save it to a file."""
        markdown_content = "".join(self.elements)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Convert to PDF if wkhtmltopdf_path is provided
        if self.wkhtmltopdf_path:
            pdf_file = output_file.replace(".md", ".pdf")
            html_content = markdown.markdown(markdown_content)
            pdfkit_config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
            pdfkit.from_string(html_content, pdf_file, configuration=pdfkit_config)

        return markdown_content


# Example usage
if __name__ == "__main__":
    markdown_maker = x_cls_make_markdown_x(wkhtmltopdf_path=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    markdown_maker.add_header("My Document", level=1)
    markdown_maker.add_header("Introduction", level=2)
    markdown_maker.add_paragraph("This is an example paragraph.")
    markdown_maker.add_table(["Name", "Age"], [["Alice", "30"], ["Bob", "25"]])
    markdown_maker.add_image("Example Image", "https://example.com/image.png")
    markdown_maker.add_list(["Item 1", "Item 2", "Item 3"], ordered=True)
    markdown_maker.add_toc()

    markdown_maker.generate("example.md")
