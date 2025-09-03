import typer
try:
    import git
except ImportError:
    git = None
from rich import print
from rich.console import Console
from rich.table import Table

git_app = typer.Typer(help="Git workflow utilities")
console = Console()

@git_app.command()
def push():
    """Push changes to a remote repository."""
    print("Git push command (not implemented yet)")

@git_app.command()
def branch():
    """Manage branches."""
    print("Git branch command (not implemented yet)")

@git_app.command()
def log():
    """Show commit logs."""
    try:
        repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        print("[bold red]✗ This is not a git repository.[/bold red]")
        raise typer.Exit(1)

    table = Table(title="Commit Log")
    table.add_column("SHA", style="cyan", width=8)
    table.add_column("Message", style="magenta")
    table.add_column("Author", style="green", width=15)
    table.add_column("Date", style="yellow", width=20)

    try:
        for commit in repo.iter_commits(max_count=20):
            message = commit.message.splitlines()[0] if commit.message else "No message"
            # Truncate long messages
            if len(message) > 50:
                message = message[:47] + "..."
            
            table.add_row(
                commit.hexsha[:7],
                message,
                commit.author.name or "Unknown",
                commit.authored_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            )
    except Exception as e:
        print(f"[bold red]✗ Error reading commit history: {e}[/bold red]")
        raise typer.Exit(1)

    console.print(table)

@git_app.command()
def cleanup():
    """Cleanup local branches."""
    print("Git cleanup command (not implemented yet)")

@git_app.command()
def commit():
    """Create a new commit."""
    print("Git commit command (not implemented yet)")
