import typer
try:
    import gitlab
    import git
except ImportError:
    gitlab = None
    git = None
from repopi.utils.config_utils import load_config
from rich import print
from rich.console import Console
from rich.table import Table

gitlab_app = typer.Typer(help="GitLab integration tools")
issue_app = typer.Typer(help="GitLab issue management")
gitlab_app.add_typer(issue_app, name="issue")

console = Console()

def get_repo_from_remote():
    try:
        repo = git.Repo(search_parent_directories=True)
        remote_url = repo.remotes.origin.url
        
        # Handle different URL formats
        if remote_url.startswith("git@gitlab.com:"):
            # git@gitlab.com:owner/repo.git -> owner/repo
            repo_name = remote_url.split(":")[1].replace(".git", "")
        elif "gitlab.com" in remote_url:
            # https://gitlab.com/owner/repo.git -> owner/repo
            repo_name = remote_url.split("gitlab.com/")[1].replace(".git", "")
        else:
            return None
            
        return repo_name
    except (git.InvalidGitRepositoryError, IndexError, AttributeError):
        return None

@issue_app.command("list")
def issue_list():
    """List GitLab issues."""
    config = load_config()
    if not config.gitlab.token:
        print("[bold red]✗ GitLab token not found. Please set it using `repopi config set-gitlab-token`.[/bold red]")
        raise typer.Exit(1)

    # Assuming gitlab.com, need to make this configurable in the future
    gl = gitlab.Gitlab('https://gitlab.com', private_token=config.gitlab.token)

    repo_name = get_repo_from_remote()
    if not repo_name:
        print("[bold red]✗ Could not determine GitLab repository from git remote.[/bold red]")
        raise typer.Exit(1)

    try:
        project = gl.projects.get(repo_name)
        issues = project.issues.list(state='opened')
    except Exception as e:
        print(f"[bold red]✗ Error getting issues: {e}[/bold red]")
        raise typer.Exit(1)

    table = Table(title=f"Open Issues for {repo_name}")
    table.add_column("#", style="cyan", width=6)
    table.add_column("Title", style="magenta")
    table.add_column("Author", style="green", width=15)

    if not issues:
        print(f"[yellow]No open issues found for {repo_name}[/yellow]")
    else:
        for issue in issues:
            table.add_row(str(issue.iid), issue.title, issue.author['username'])
        console.print(table)

@gitlab_app.command()
def mr():
    """Manage GitLab merge requests."""
    print("GitLab MR command (not implemented yet)")