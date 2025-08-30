"""Main CLI entry point."""

import click
from rich.console import Console

from .commands.tools import tools

console = Console()

@click.group()
@click.version_option()
def cli():
    """LangChain CLI for tool server development and deployment."""
    pass

# Register command groups
cli.add_command(tools)

if __name__ == "__main__":
    cli()