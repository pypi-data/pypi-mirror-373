"""RepoPi CLI main entry point."""

from __future__ import annotations

import sys
from typing import Optional

import typer
from rich import print
from rich.console import Console

# Import version info
from repopi import __version__

# Correctly import command functions from their modules
from repopi.commands.ai_cli import ai_app
from repopi.commands.config_cli import config_app
from repopi.commands.git_cli import git_app
from repopi.commands.github_cli import github_app
from repopi.commands.gitlab_cli import gitlab_app

# Import utilities
from repopi.utils.exceptions import RepopiError
from repopi.utils.logging import get_logger, setup_logging

console = Console()
logger = get_logger(__name__)


def print_banner() -> None:
    """Print the RepoPi banner with ASCII art."""
    banner_text = """
[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]

        [bold green]RRRRR   EEEEE  PPPPP   OOOOO   PPPPP   III[/bold green]
        [bold green]R    R  E      P    P  O     O  P    P   I [/bold green]
        [bold green]RRRRR   EEEE   PPPPP   O     O  PPPPP    I [/bold green]
        [bold green]R   R   E      P       O     O  P        I [/bold green]
        [bold green]R    R  EEEEE  P        OOOOO   P      III[/bold green]

[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]
[bold yellow]An all-in-one developer assistant for Git workflows and AI automation[/bold yellow]
[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]
    """
    print(banner_text)

app = typer.Typer(
    name="repopi",
    help="An all-in-one developer assistant for Git workflows, hosting, and AI automation.",
    no_args_is_help=False,  # Changed to False so we can show banner
    add_completion=False,
    # Remove rich_markup_mode to fix compatibility issues
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information and exit.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose logging.",
    ),
) -> None:
    """Display banner when no command is specified."""
    # Setup logging
    setup_logging(level="DEBUG" if verbose else "INFO", verbose=verbose)
    
    if version:
        print(f"RepoPi version {__version__}")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        print_banner()
        # Show simplified help instead of full help to avoid compatibility issues
        print("[bold white]Available Commands:[/bold white]")
        print("  [cyan]git[/cyan]     - Git workflow utilities")
        print("  [cyan]github[/cyan]  - GitHub integration tools")  
        print("  [cyan]gitlab[/cyan]  - GitLab integration tools")
        print("  [cyan]ai[/cyan]      - AI-powered development assistance")
        print("  [cyan]config[/cyan]  - Configuration management")
        print("  [cyan]init[/cyan]    - Initialize RepoPi in a repository")
        print("")
        print("Use [cyan]repopi COMMAND --help[/cyan] for more information on a command.")

# Register command groups
app.add_typer(git_app, name="git")
app.add_typer(github_app, name="github")
app.add_typer(gitlab_app, name="gitlab")
app.add_typer(ai_app, name="ai")
app.add_typer(config_app, name="config")


@app.command()
def init() -> None:
    """Initialize repopi in a repository."""
    try:
        # TODO: Implement actual initialization logic
        print("[bold green]✓ RepoPi initialized.[/bold green]")
        logger.info("RepoPi initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RepoPi: {e}")
        raise typer.Exit(1)


def main_cli() -> None:
    """Main CLI entry point with error handling."""
    try:
        app()
    except RepopiError as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
