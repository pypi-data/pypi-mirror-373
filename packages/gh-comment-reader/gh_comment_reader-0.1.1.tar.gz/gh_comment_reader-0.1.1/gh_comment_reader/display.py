from typing import assert_never

from rich.console import Console
from rich.table import Table

from .models import OutputFormat, ParsedComment

console = Console()


def print_pr_comments(
    comments: list[ParsedComment],
    format: OutputFormat = OutputFormat.TABLE,
    verbose: bool = True,
) -> None:
    match format:
        case OutputFormat.JSON:
            _print_json_output(comments, verbose)

        case OutputFormat.TABLE:
            _print_table_output(comments, verbose)

        case OutputFormat.TEXT:
            _print_text_output(comments, verbose)

        case _:
            # noinspection PyUnreachableCode
            assert_never(format)  # noqa: F821


def _print_json_output(comments: list[ParsedComment], verbose: bool) -> None:
    console.print_json(data=[comment.model_dump() for comment in comments])


def _print_table_output(comments: list[ParsedComment], verbose: bool) -> None:
    table = Table(title="PR Comments", show_header=True, header_style="bold magenta")
    table.add_column("User", style="cyan", no_wrap=True)
    table.add_column("Date", style="green", no_wrap=True)
    table.add_column("Status", style="yellow", no_wrap=True)
    table.add_column("Comment", style="white", overflow="fold")

    for cmt in comments:
        status = "✓ Resolved" if cmt.is_resolved else "○ Open"
        body = cmt.body[:100] + "..." if ((len(cmt.body) > 100) and not verbose) else cmt.body
        body += f"\n\n{cmt.url}"

        table.add_row(
            cmt.author,
            cmt.created_at.strftime("%Y-%m-%d %H:%M"),
            status,
            body,
        )
        table.add_section()

    console.print(table)


def _print_text_output(comments: list[ParsedComment], verbose: bool) -> None:
    for cmt in comments:
        status = "✓ Resolved" if cmt.is_resolved else "○ Open"
        body = cmt.body[:200] + "..." if ((len(cmt.body) > 200) and not verbose) else cmt.body
        body += f"\n\nLink: f{cmt.url}\n"

        console.print(f"\n[bold cyan]User:[/bold cyan] {cmt.author} [{status}]")
        console.print(f"[bold green]Date:[/bold green] {cmt.created_at}")
        console.print(f"[bold yellow]Link:[/bold yellow] {cmt.url}")
        console.print(f"[white]{body}[/white]")
