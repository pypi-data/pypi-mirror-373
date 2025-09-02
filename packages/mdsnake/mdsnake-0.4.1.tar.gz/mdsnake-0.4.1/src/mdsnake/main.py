"""Libraries"""
import os
import pathlib

import typer
from rich.console import Console
from rich.markdown import Markdown
from typing_extensions import Annotated

from .convert import convert_file
from .dialog import print_error, print_syntax
from .localhost import run_localhost

app = typer.Typer(no_args_is_help=True)
console = Console()

"""Commands"""
@app.command()
def view(file: str, web: Annotated[bool, typer.Option(help="View markdown file on a localhost?")] = False):
    """
    Views markdown files on the console or localhost
    :param file:
    :option web:
    """

    cwd = pathlib.Path.cwd()
    file = os.path.join(cwd, file)

    if os.path.isfile(file):
        if file.endswith(".md"):
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
            try:
                if web:
                    run_localhost(text)
                else:
                    md = Markdown(text)
                    console.print(md)
            except Exception as error:
                print_error(f"There was an error while reading the markdown file. ({error})")
        else:
            print_error("The file you have selected is not a markdown file.")
    else:
        print_error("The file you have selected is non-existent.")

@app.command()
def convert(file: str, extension: str, filename: Annotated[str, typer.Option(help="Change the name of the output file")] = ""):
    """
    Converts markdown files to pdf/html files
    :param file:
    :param filetype:
    :param filename:
    """

    if extension.lower() not in {"html", "pdf"}:
        print_error("You have selected an invalid extension, the options are (html, pdf)")
    else:
        cwd = pathlib.Path.cwd()
        file = os.path.join(cwd, file)

        if os.path.isfile(file):
            if file.endswith(".md"):
                with open(file, "r", encoding="utf-8") as f:
                    text = f.read()
                if filename != "":
                    convert_file(text, extension, file.replace("md", extension))
                else:
                    convert_file(text, extension, cwd / filename)
            else:
                print_error("The file you have is not a markdown file.")
        else:
            print_error("The file you have selected is non-existent.")

@app.command()
def syntax():
    """
    Shows a cheat sheet table of markdown syntax
    """
    print_syntax()

if __name__ == "__main__":
    app()
