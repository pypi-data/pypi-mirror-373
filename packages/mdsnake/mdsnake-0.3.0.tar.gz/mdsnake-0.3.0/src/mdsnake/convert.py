"""Libraries"""
from markdown_pdf import MarkdownPdf, Section
from markdown import markdown

from .dialogs import success_message

def convert_md(markdown_text: str, filetype: str, filename: str):
    """
    Converts markdown to HTML or PDFs
    :param md:
    :param filetype:
    :param filename:
    :param location:
    """
    if filetype.lower() == "html":
        converted_markdown = markdown(markdown_text, extensions=["fenced_code", "tables"])
        with open(filename, "w", encoding="utf-8") as file:
            file.write(converted_markdown)
    elif filetype.lower() == "pdf":
        pdf = MarkdownPdf()
        pdf.meta["title"] = "Markdown"
        pdf.add_section(Section(markdown_text, toc=False))
        pdf.save(filename)

    success_message("Successfully converted!")
