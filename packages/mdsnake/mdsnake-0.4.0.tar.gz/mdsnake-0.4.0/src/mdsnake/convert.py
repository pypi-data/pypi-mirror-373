"""Libraries"""
from markdown_pdf import MarkdownPdf, Section
from markdown import markdown

from .dialogs import success_message

def convert_md(markdown_text: str, filename: str, location: str):
    """
    Converts markdown to HTML or PDFs
    :param md:
    :param filetype:
    :param filename:
    :param location:
    """
    if filename.split(".")[1].lower() == "html":
        converted_markdown = markdown(markdown_text, extensions=["fenced_code", "tables"])
        with open(location / filename, "w", encoding="utf-8") as file:
            file.write(converted_markdown)
    elif filename.split(".")[1].lower() == "pdf":
        pdf = MarkdownPdf()
        pdf.meta["title"] = "Markdown"
        pdf.add_section(Section(markdown_text, toc=False))
        pdf.save(location / filename)

    success_message("Successfully converted!")
