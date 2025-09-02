"""Libraries"""
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

def success_message(message: str):
    """
    Prints out a success message
    :param message:
    """
    panel = Panel(message, title="Success", title_align="left", expand=True, border_style="green")
    console.print(panel)

def error_message(error: str):
    """
    Prints a clean error statment
    :param error:
    """
    raise typer.BadParameter(error)
