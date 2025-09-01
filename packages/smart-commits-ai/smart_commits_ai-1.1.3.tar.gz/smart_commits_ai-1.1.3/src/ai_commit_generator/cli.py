"""Command-line interface for AI Commit Generator."""

import functools
import os
import re
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .api_clients import APIError
from .config import Config, ConfigError, SecurityError
from .core import CommitGenerator, GitError
from .git_hook import GitHookManager

console = Console()


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Safely mask sensitive data for display."""
    if not data or not isinstance(data, str):
        return "[INVALID]"

    if len(data) <= visible_chars:
        return "*" * len(data)

    return data[:visible_chars] + "*" * (len(data) - visible_chars)


def print_banner():
    """Print the application banner."""
    banner = Text()
    banner.append("🤖 AI Commit Message Generator\n", style="bold cyan")
    banner.append(
        "Automatically generate conventional commit messages using AI", style="dim"
    )

    console.print(Panel(banner, border_style="cyan"))


def handle_errors(func):
    """Decorator to handle common errors securely."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SecurityError as e:
            console.print(f"[red]❌ Security Error:[/red] {e}")
            sys.exit(1)
        except ConfigError as e:
            console.print(f"[red]❌ Configuration Error:[/red] {e}")
            sys.exit(1)
        except GitError as e:
            console.print(f"[red]❌ Git Error:[/red] {e}")
            sys.exit(1)
        except APIError as e:
            console.print(f"[red]❌ API Error:[/red] {e}")
            sys.exit(1)
        except Exception as e:
            # Log full error for debugging but show generic message to user
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)

            console.print("[red]❌ An error occurred. Check logs for details.[/red]")

            # Only show full error in debug mode
            if os.getenv("DEBUG"):
                console.print(f"[dim]Debug info: {e}[/dim]")
                import traceback
                traceback.print_exc()
            sys.exit(1)

    return wrapper


@click.group()
@click.version_option(version=__version__)
def main():
    """AI-powered Git commit message generator."""
    pass


@main.command()
@click.option(
    "--force", "-f", is_flag=True, help="Overwrite existing hook without confirmation"
)
@click.option("--config", "-c", is_flag=True, help="Also install configuration files")
@handle_errors
def install(force: bool, config: bool):
    """Install the AI commit generator Git hook."""
    print_banner()
    console.print("[blue]🔧 Installing AI commit generator...[/blue]")

    hook_manager = GitHookManager()

    # Install the hook
    if hook_manager.install_hook(force=force):
        console.print("[green]✅ Git hook installed successfully[/green]")
    else:
        console.print("[yellow]⚠️  Installation cancelled[/yellow]")
        return

    # Install configuration files if requested
    if config:
        if hook_manager.install_config_files(force=force):
            console.print("[green]✅ Configuration files installed[/green]")

    # Show next steps
    console.print("\n[yellow]📋 Next Steps:[/yellow]")
    console.print("1. Get an API key from one of these providers:")
    console.print(
        "   • [green]Groq[/green] (recommended): https://console.groq.com/keys"
    )
    console.print("   • [green]OpenRouter[/green]: https://openrouter.ai/keys")
    console.print("   • [green]Cohere[/green]: https://dashboard.cohere.ai/api-keys")
    console.print("\n2. Add your API key to .env:")
    console.print("   [cyan]echo 'GROQ_API_KEY=your_key_here' >> .env[/cyan]")
    console.print("\n3. Test the installation:")
    console.print(
        "   [cyan]echo 'test' > test.txt && git add test.txt && git commit[/cyan]"
    )
    console.print(
        "\n[green]🚀 Your commits will now be automatically enhanced with AI![/green]"
    )


@main.command()
@handle_errors
def uninstall():
    """Uninstall the AI commit generator Git hook."""
    console.print("[blue]🗑️  Uninstalling AI commit generator...[/blue]")

    hook_manager = GitHookManager()

    if hook_manager.uninstall_hook():
        console.print("[green]✅ AI commit hook uninstalled successfully[/green]")
    else:
        console.print("[yellow]⚠️  Hook not found or already uninstalled[/yellow]")


@main.command()
@click.option("--output", "-o", help="Output file for the commit message")
@click.option(
    "--dry-run", is_flag=True, help="Generate message without writing to file"
)
@handle_errors
def generate(output: Optional[str], dry_run: bool):
    """Generate a commit message for staged changes."""
    console.print("[blue]🤖 Generating AI commit message...[/blue]")

    generator = CommitGenerator()

    try:
        message = generator.generate_commit_message(
            commit_msg_file=None if dry_run else output
        )

        if message:
            console.print(
                f"[green]✅ Generated message:[/green] [blue]{message}[/blue]"
            )
            if dry_run:
                console.print(
                    "[dim]Note: This was a dry run. No files were modified.[/dim]"
                )
        else:
            console.print(
                "[yellow]⚠️  No staged changes found or merge commit detected[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]❌ Failed to generate commit message:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option("--show", is_flag=True, help="Show current configuration")
@click.option("--validate", is_flag=True, help="Validate configuration")
@handle_errors
def config(show: bool, validate: bool):
    """Manage configuration."""
    try:
        cfg = Config()
    except ConfigError as e:
        if "Not in a Git repository" in str(e):
            console.print("[red]❌ Not in a Git repository[/red]")
            console.print("Please run this command from within a Git repository.")
            sys.exit(1)
        raise

    if show:
        console.print("[blue]📋 Current Configuration:[/blue]")
        console.print(f"Provider: [green]{cfg.provider}[/green]")
        console.print(f"Model: [green]{cfg.model}[/green]")
        console.print(f"Max chars: [green]{cfg.max_chars}[/green]")
        console.print(f"Config file: [dim]{cfg.config_file}[/dim]")
        console.print(f"Env file: [dim]{cfg.env_file}[/dim]")

        # Check API key (securely masked)
        try:
            api_key = cfg.api_key
            masked_key = mask_sensitive_data(api_key, 4)
            console.print(f"API key: [green]✅ Configured[/green] ({masked_key})")
        except ConfigError:
            console.print("API key: [red]❌ Not configured[/red]")

    if validate:
        console.print("[blue]🔍 Validating configuration...[/blue]")
        try:
            cfg.validate()
            console.print("[green]✅ Configuration is valid[/green]")
        except ConfigError as e:
            console.print(f"[red]❌ Configuration error:[/red] {e}")
            sys.exit(1)


@main.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed status")
@handle_errors
def status(verbose: bool):
    """Show installation and configuration status."""
    console.print("[blue]📊 AI Commit Generator Status[/blue]")

    hook_manager = GitHookManager()

    # Check Git repository
    try:
        repo_root = hook_manager._find_repo_root()
        console.print(f"[green]✅ Git repository:[/green] {repo_root}")
    except GitError:
        console.print("[red]❌ Not in a Git repository[/red]")
        return

    # Check hook installation
    if hook_manager.is_hook_installed():
        console.print("[green]✅ Git hook installed[/green]")
    else:
        console.print("[red]❌ Git hook not installed[/red]")
        console.print("   Run: [cyan]ai-commit-generator install[/cyan]")

    # Check configuration
    try:
        cfg = Config()
        console.print("[green]✅ Configuration loaded[/green]")

        # Check API key
        try:
            cfg.api_key
            console.print(
                f"[green]✅ API key configured[/green] (provider: {cfg.provider})"
            )
        except ConfigError:
            console.print(
                f"[red]❌ API key not configured[/red] (provider: {cfg.provider})"
            )
            console.print(f"   Set {cfg.provider.upper()}_API_KEY in .env file")

        if verbose:
            console.print(f"\n[dim]Configuration details:[/dim]")
            console.print(f"  Provider: {cfg.provider}")
            console.print(f"  Model: {cfg.model}")
            console.print(f"  Max chars: {cfg.max_chars}")
            console.print(f"  Config file: {cfg.config_file}")
            console.print(f"  Env file: {cfg.env_file}")

    except ConfigError as e:
        console.print(f"[red]❌ Configuration error:[/red] {e}")


@main.command()
@handle_errors
def test():
    """Test the AI commit generator with current staged changes."""
    console.print("[blue]🧪 Testing AI commit generator...[/blue]")

    # Check if there are staged changes
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        if not result.stdout.strip():
            console.print("[yellow]⚠️  No staged changes found[/yellow]")
            console.print("Stage some changes first: [cyan]git add <files>[/cyan]")
            return
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to check staged changes[/red]")
        return

    # Generate message
    generator = CommitGenerator()
    try:
        message = generator.generate_commit_message()
        if message:
            console.print(f"[green]✅ Test successful![/green]")
            console.print(f"Generated message: [blue]{message}[/blue]")
        else:
            console.print("[yellow]⚠️  No message generated[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Test failed:[/red] {e}")


if __name__ == "__main__":
    main()
