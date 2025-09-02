"""Libraries"""
from markdown import markdown
from markdown_pdf import MarkdownPdf, Section

from .dialog import print_success, print_error

def convert_file(markdown_text: str, filename: str, location: str):
    """
    Converts markdown files to html/pdf files
    :param markdown_text:
    :param filename:
    :param location:
    """
    if filename.split(".")[1].lower() == "html":
        try:
            converted_markdown = markdown(markdown_text, extensions=["fenced_code", "tables"])
        except Exception as error:
            print_error(f"There was an error while converting the markdown file. ({error})")
    elif filename.split(".")[1].lower() == "pdf":
        try:
            pdf = MarkdownPdf()
            pdf.meta["title"] = "Markdown"
            pdf.add_section(Section(markdown_text, toc=False))
        except Exception as error:
            print_error(f"There was an error while converting the markdown file. ({error})")

    try:
        if filename.split(".")[1].lower() == "html":
            with open(location / filename, "w", encoding="utf-8") as file:
                file.write(converted_markdown)
        elif filename.split(".")[1].lower() == "pdf":
            pdf.save(location / filename)
    except Exception as error:
        print_error(f"There was an error while saving the file. ({error})")

    print_success("The file you have selected has been successfully converted!")
