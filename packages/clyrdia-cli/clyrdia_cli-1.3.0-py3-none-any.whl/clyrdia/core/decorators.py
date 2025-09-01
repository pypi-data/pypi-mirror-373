"""
Authentication decorators and helper functions for Clyrdia CLI.
"""

import sys
import asyncio
import functools
from pathlib import Path
from typing import Callable
import typer
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align

from .console import console, _display_welcome_screen
from ..auth.licensing import LicensingManager

def require_auth(func: Callable) -> Callable:
    """
    Authentication decorator that gatekeeps all user-facing commands.
    Implements the "First-Run Authentication Flow" for seamless onboarding.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if user is already authenticated
        licensing_manager = LicensingManager()
        
        if licensing_manager.is_authenticated():
            # User is authenticated, proceed with command
            return func(*args, **kwargs)
        
        # User is not authenticated - trigger first-run flow
        return _handle_first_run_auth(func, *args, **kwargs)
    
    return wrapper

def _handle_first_run_auth(func: Callable, *args, **kwargs):
    """
    Handles the first-run authentication flow with seamless handoff to web signup.
    """
    # Display beautiful ASCII art welcome screen
    _display_welcome_screen()
    
    console.print(Panel.fit(
        "[bold cyan]👋 Welcome to Clyrdia![/bold cyan]\n"
        "To run your first benchmark, let's connect your CLI to your free account.\n"
        "This will unlock your 250 monthly credits.",
        border_style="cyan",
        padding=(1, 2),
        title="Welcome",
        title_align="center"
    ))
    
    console.print("\n[bold]🔗 Please visit clyrdia.com to create your account:[/bold]")
    console.print("[bold bright_blue]https://clyrdia.com/auth[/bold bright_blue]")
    console.print("\n[yellow]Complete the signup process and get your API key, then paste it below.[/yellow]")
    
    console.print("\n[bold]Steps to complete signup:[/bold]")
    console.print("1. Complete the signup form on clyrdia.com")
    console.print("2. Verify your email address")
    console.print("3. Get your API key from your dashboard")
    console.print("4. Paste it below when ready")
    
    console.print("\n[bold]Waiting for API key...[/bold] (paste it here when you're done)")
    
    # Wait for user to paste their API key
    while True:
        try:
            api_key = Prompt.ask("API Key", password=True)
            
            if not api_key or len(api_key.strip()) < 10:
                console.print("[red]❌ Invalid API key format. Please try again.[/red]")
                continue
            
            # Validate the API key
            licensing_manager = LicensingManager()
            try:
                user_status = asyncio.run(licensing_manager.login(api_key.strip()))
                
                console.print(f"\n[green]✅ Successfully authenticated![/green]")
                console.print(f"Welcome, [bold]{user_status.user_name}[/bold]!")
                console.print(f"Plan: [bold]{user_status.plan.upper()}[/bold]")
                console.print(f"Credits: [bold]{user_status.credits_remaining:,}[/bold]")
                
                # Success! Now execute the original command
                console.print(f"\n[bold green]🚀 Continuing with your original command...[/bold green]")
                return func(*args, **kwargs)
                
            except Exception as e:
                console.print(f"[red]❌ Authentication failed: {str(e)}[/red]")
                console.print("\n[bold]Troubleshooting:[/bold]")
                console.print("  • Verify you completed the signup process")
                console.print("  • Check your internet connection")
                console.print("  • Try copying the API key again")
                console.print("  • Visit [bold]https://clyrdia.com[/bold] to start over")
                
                if not Confirm.ask("Try again with a different API key?"):
                    console.print("[dim]Authentication cancelled. Run your command again when ready.[/dim]")
                    raise typer.Exit(0)
                
                continue
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Authentication cancelled.[/yellow]")
            console.print("Run your command again when you're ready to authenticate.")
            raise typer.Exit(0)
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {str(e)}[/red]")
            raise typer.Exit(1)

def _is_first_run() -> bool:
    """Check if this is the user's first run of Clyrdia"""
    config_file = Path.home() / ".clyrdia" / "config.json"
    return not config_file.exists()

def _get_original_command() -> str:
    """Get the original command the user was trying to run"""
    # This is a simplified approach - in practice, you might want to store
    # the original command in a more sophisticated way
    return " ".join(sys.argv[1:])
