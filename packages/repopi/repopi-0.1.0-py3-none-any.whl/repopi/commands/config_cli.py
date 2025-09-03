
import typer
from rich import print
from repopi.utils.config_utils import load_config, save_config

config_app = typer.Typer(help="Configuration management")

@config_app.command()
def set_openai_key(api_key: str):
    """Set the OpenAI API key."""
    config = load_config()
    config.ai.openai_api_key = api_key
    save_config(config)
    print("[bold green]✓ OpenAI API key saved.[/bold green]")

@config_app.command()
def set_github_token(token: str):
    """Set the GitHub token."""
    config = load_config()
    config.github.token = token
    save_config(config)
    print("[bold green]✓ GitHub token saved.[/bold green]")

@config_app.command()
def set_gitlab_token(token: str):
    """Set the GitLab token."""
    config = load_config()
    config.gitlab.token = token
    save_config(config)
    print("[bold green]✓ GitLab token saved.[/bold green]")

@config_app.command()
def show():
    """Show current configuration (without sensitive values)."""
    config = load_config()
    print("[bold cyan]Current Configuration:[/bold cyan]")
    print(f"OpenAI API Key: {'✓ Set' if config.ai.openai_api_key else '✗ Not set'}")
    print(f"GitHub Token: {'✓ Set' if config.github.token else '✗ Not set'}")
    print(f"GitLab Token: {'✓ Set' if config.gitlab.token else '✗ Not set'}")
