#!/usr/bin/env python3
import typer
from rich.console import Console

from .cli import fetch_command

console = Console()

app = typer.Typer(
    name="GitHub Comment Reader",
    help="GitHub Comment Reader - CLI tool for easily reading GitHub PR comments",
    add_completion=False,
)

app.command("fetch")(fetch_command)


def main() -> None:
    try:
        app()
    except Exception as err:
        console.print(f"[red]Error: {err}[/red]")
        raise typer.Exit(code=1) from err


if __name__ == "__main__":
    main()
