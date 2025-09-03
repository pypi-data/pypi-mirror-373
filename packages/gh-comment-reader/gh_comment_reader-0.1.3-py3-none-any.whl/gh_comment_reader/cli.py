from typing import Annotated

import typer
from rich.console import Console

from .comments import GitHubPRComments
from .display import print_pr_comments
from .models import OutputFormat

console = Console()


def fetch_command(
    pr_url: Annotated[
        str,
        typer.Argument(
            help="GitHub PR URL to fetch comments from",
        ),
    ],
    format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            "-f",
            help="Output format",
        ),
    ] = OutputFormat.TABLE,
    show_bots: Annotated[
        bool,
        typer.Option(
            "--show-bots",
            help="Whether to include comments from bots",
            show_default=True,
        ),
    ] = False,
    no_resolve: Annotated[
        bool,
        typer.Option(
            "--hide-resolved",
            "-r",
            help="Whether to include unresolved comments only",
            show_default=False,
        ),
    ] = False,
) -> None:
    if not pr_url.startswith("https://github.com/"):
        console.print("[red]Error: Invalid GitHub URL[/red]")
        raise typer.Exit(code=1)

    if not (comments := GitHubPRComments.from_github_pr(pr_url).comments):
        console.print("[yellow]No comments found (after filtering)[/yellow]")
        raise typer.Exit(code=0)

    total_comments = len(comments)
    bot_hidden, resolved_hidden = 0, 0

    if not show_bots:
        comments = [c for c in comments if not c.is_bot]
        bot_hidden = total_comments - len(comments)

    if no_resolve:
        comments = [c for c in comments if not c.is_resolved]
        resolved_hidden = total_comments - bot_hidden - len(comments)

    print_pr_comments(comments, format=format)
    console.print(f"{pr_url}")

    tip = ""
    if not show_bots:
        tip += "Use --show-bots to include bot comments. "
    if not no_resolve:
        tip += "Use --hide-resolved to hide resolved comments."

    shown_comments = len(comments)
    hidden_comments = total_comments - shown_comments

    exit_str = f"\n[bold][green]Total comments: {len(comments)}[/green][/bold]"
    if hidden_comments > 0:
        exit_str += (
            f" [white]· {hidden_comments} hidden ({bot_hidden} bot, "
            f"{resolved_hidden} resolved)[/white]"
        )

    console.print(exit_str)
    if tip:
        console.print(f"[white]Tip: {tip}[/white]")
