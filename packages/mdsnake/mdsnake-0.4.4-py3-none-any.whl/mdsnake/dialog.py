"""Libraries"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

"""Functions"""
def print_success(message: str):
    """
    Prints out a success message
    :param message:
    """
    panel = Panel(message, title="Success", title_align="left", expand=True, border_style="green")
    console.print(panel)

def print_error(error: str):
    """
    Prints a clean error statment
    :param error:
    """
    raise click.UsageError(error)

def print_syntax():
    """
    Prints a cheat sheet table of markdown syntax
    """
    table = Table(title="Markdown Syntax", show_lines=True)

    table.add_column("Element")
    table.add_column("Syntax")

    table.add_row("Heading", """
# H1
## H2
### H3""")
    table.add_row("Bold", "**Bold Text**")
    table.add_row("Italic", "*Italics*")
    table.add_row("Blockquote", "> blockquote")
    table.add_row("Ordered List", """
1. First Item
2. Second Item
3. Third Item""")
    table.add_row("Unordered List", """
- First Item
- Second Item
- Third Item""")
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
