"""Libraries"""
import os
import pathlib

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from typing_extensions import Annotated

from .web import run

app = typer.Typer()
console = Console()

def error_message(error: str):
    """
    Prints a clean error statment
    :param error:
    """
    raise typer.BadParameter(error)

@app.command()
def view(
    file: str,
    web: Annotated[bool, typer.Option(help="View markdown file on a localhost")] = False
):
    """
    Views markdown files in the console
    :param file:
    """
    cwd = pathlib.Path.cwd()
    file = os.path.join(cwd, file)

    if os.path.isfile(file) and file.endswith(".md"):
        with open(file, "r", encoding="utf-8") as f:
            md = f.read()
            if web:
                run(md)
            else:
                console.print(Markdown(md))
    else:
        error_message("File selected is none or invalid.")

@app.command()
def syntax():
    """
    Shows a table of markdown syntax in the console
    """
    table = Table(title="Markdown Syntax", show_lines=True)

    table.add_column("Element")
    table.add_column("Syntax")

    table.add_row("Heading", "# H1\n## H2\n### H3")
    table.add_row("Bold", "**Bold Text**")
    table.add_row("Italic", "*Italics*")
    table.add_row("Blockquote", "> blockquote")
    table.add_row("Ordered List", "1. First Item\n2. Second Item\n3. Third Item")
    table.add_row("Unordered List", "- First Item\n- Second Item\n- Third Item")
    table.add_row("Code", "`code`")
    table.add_row("Horizontal Rule", "---")
    table.add_row("Link", "[title](https://google.com/)")
    table.add_row("Image", "![alt text](image.jpg)")
    table.add_row("Table", """
| Syntax | Description |
| ----------- | ----------- |
| Header | Title |
| Paragraph | Text |
""")
    table.add_row("Fenced Code Block", """
```
{
  "firstName": "John",
  "lastName": "Smith",
  "age": 25
}
```
""")
    table.add_row("Footnote", """
Here's a sentence with a footnote. [^1]

[^1]: This is the footnote.
""")
    table.add_row("Heading Id", """
### My Great Heading {#custom-id}
""")
    table.add_row("Definition List", """
term
: definition
""")
    table.add_row("Strikethrough", "~~The world is flat.~~")
    table.add_row("Task List", """
- [x] Write the press release
- [ ] Update the website
- [ ] Contact the media""")
    table.add_row("Emoji", "That is so funny! :joy:")
    table.add_row("Highlight", "I need to highlight these ==very important words==.")
    table.add_row("Subscript", "H~2~O")
    table.add_row("Superscript", "X^2^")

    console.print(table)

if __name__ == "__main__":
    app()
