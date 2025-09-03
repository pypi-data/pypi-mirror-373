import typer
try:
    from github import Github
    import git
except ImportError:
    Github = None
    git = None
from repopi.utils.config_utils import load_config
from rich import print
from rich.console import Console
from rich.table import Table

github_app = typer.Typer(help="GitHub integration tools")
issue_app = typer.Typer(help="GitHub issue management")
github_app.add_typer(issue_app, name="issue")

console = Console()

def get_repo_from_remote():
    try:
        repo = git.Repo(search_parent_directories=True)
        remote_url = repo.remotes.origin.url
        
        # Handle different URL formats
        if remote_url.startswith("git@github.com:"):
            # git@github.com:owner/repo.git -> owner/repo
            repo_name = remote_url.split(":")[1].replace(".git", "")
        elif "github.com" in remote_url:
            # https://github.com/owner/repo.git -> owner/repo
            repo_name = remote_url.split("github.com/")[1].replace(".git", "")
        else:
            return None
            
        return repo_name
    except (git.InvalidGitRepositoryError, IndexError, AttributeError):
        return None

@issue_app.command("list")
def issue_list():
    """List GitHub issues."""
    config = load_config()
    if not config.github.token:
        print("[bold red]✗ GitHub token not found. Please set it using `repopi config set-github-token`.[/bold red]")
        raise typer.Exit(1)

    g = Github(config.github.token)

    repo_name = get_repo_from_remote()
    if not repo_name:
        print("[bold red]✗ Could not determine GitHub repository from git remote.[/bold red]")
        raise typer.Exit(1)

    try:
        repo = g.get_repo(repo_name)
        issues = repo.get_issues(state="open")
    except Exception as e:
        print(f"[bold red]✗ Error getting issues: {e}[/bold red]")
        raise typer.Exit(1)

    table = Table(title=f"Open Issues for {repo_name}")
    table.add_column("#", style="cyan", width=6)
    table.add_column("Title", style="magenta")
    table.add_column("Author", style="green", width=15)

    issue_count = 0
    for issue in issues:
        table.add_row(str(issue.number), issue.title, issue.user.login)
        issue_count += 1

    if issue_count == 0:
        print(f"[yellow]No open issues found for {repo_name}[/yellow]")
    else:
        console.print(table)

@github_app.command()
def pr():
    """Manage GitHub pull requests."""
    print("GitHub PR command (not implemented yet)")