import typer
try:
    import openai
    import git
except ImportError:
    openai = None
    git = None
from rich import print
from repopi.utils.config_utils import load_config

ai_app = typer.Typer(help="AI-powered development assistance")

@ai_app.command()
def commit():
    """Generate a commit message using AI."""
    config = load_config()
    if not config.ai.openai_api_key:
        print("[bold red]✗ OpenAI API key not found. Please set it using `repopi config set-openai-key`.[/bold red]")
        raise typer.Exit(1)

    # Set up OpenAI client
    client = openai.OpenAI(api_key=config.ai.openai_api_key)

    try:
        repo = git.Repo(search_parent_directories=True)
        diff = repo.git.diff(cached=True)
    except git.InvalidGitRepositoryError:
        print("[bold red]✗ This is not a git repository.[/bold red]")
        raise typer.Exit(1)

    if not diff:
        print("[yellow]No staged changes to commit.[/yellow]")
        raise typer.Exit()

    prompt = f"""Generate a concise and informative commit message for the following git diff:\n\n{diff}\n\nCommit message:"""

    try:
        print("[dim]Generating commit message...[/dim]")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates concise git commit messages based on code diffs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7,
        )
        commit_message = response.choices[0].message.content.strip()
        print(f"[bold green]Suggested commit message:[/bold green]")
        print(f"[cyan]{commit_message}[/cyan]")
    except Exception as e:
        print(f"[bold red]✗ Error generating commit message: {e}[/bold red]")
        raise typer.Exit(1)