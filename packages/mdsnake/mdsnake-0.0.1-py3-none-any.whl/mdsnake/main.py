"""Libraries"""
import os
import pathlib

import typer
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer()
console = Console()

@app.command()
def view(file: str):
    """
    Views markdown files in the console
    :param file:
    """
    cwd = pathlib.Path.cwd()
    file = os.path.join(cwd, file)

    if os.path.isfile(file) and file.endswith(".md"):
        with open(file, "r", encoding="utf-8") as f:
            markdown = Markdown(f.read())
            console.print(markdown)

@app.command()
def syntax():
    """
    Shows a table of markdown syntax in the console
    """
    console.print("In development...")

if __name__ == "__main__":
    app()
