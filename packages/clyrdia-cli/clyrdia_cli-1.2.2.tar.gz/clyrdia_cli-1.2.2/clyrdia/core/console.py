"""
Console configuration and display utilities for Clyrdia CLI.
"""

from rich.console import Console
from rich.panel import Panel
from rich.align import Align

# Configure Rich console for better text alignment and box formatting
console = Console(
    width=None,  # Auto-detect terminal width
    force_terminal=True,  # Force terminal mode for consistent output
    color_system="auto",  # Auto-detect color support
    markup=True,  # Enable markup parsing
    highlight=True,  # Enable syntax highlighting
    soft_wrap=True,  # Enable soft wrapping for better text flow
    no_color=False,  # Enable colors
    tab_size=4,  # Set tab size for consistent indentation
    legacy_windows=False,  # Use modern Windows terminal features
    safe_box=True,  # Use safe box characters for better compatibility
    record=False,  # Don't record output to avoid extra formatting
)

def _display_welcome_screen():
    """Display a beautiful ASCII art welcome screen for first-time users"""
    # Clear screen for clean presentation
    console.clear()
    
    # ASCII art for CLYRDIA in bubble letters
    ascii_art = """
[bold cyan]
  ██████╗██╗     ██╗   ██╗██████╗ ██████╗ ██╗ █████╗ 
 ██╔════╝██║     ╚██╗ ██╔╝██╔══██╗██╔══██╗██║██╔══██╗
 ██║     ██║      ╚████╔╝ ██████╔╝██║  ██║██║███████║
 ██║     ██║       ╚██╔╝  ██╔══██╗██║  ██║██║██╔══██║
 ╚██████╗███████╗   ██║   ██║  ██║██████╔╝██║██║  ██║
  ╚═════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝
[/bold cyan]
"""
    
    # Subtitle and tagline
    subtitle = """
[bold bright_white]Zero-Knowledge AI Benchmarking Platform[/bold bright_white]
[dim bright_blue]The most advanced local-first AI model benchmarking tool[/dim bright_blue]
"""
    
    # Feature highlights
    features = """
[bold bright_green]✨ What makes Clyrdia special:[/bold bright_green]

[bright_cyan]🚀 Dual-Mode Workflow[/bright_cyan]   Production & Developer modes for every use case
[bright_cyan]💰 Smart Caching[/bright_cyan]      Save costs with intelligent result caching  
[bright_cyan]📊 Rich Analytics[/bright_cyan]     Beautiful dashboards & deep insights
[bright_cyan]🔒 Zero-Knowledge[/bright_cyan]     Your data stays local, always
[bright_cyan]🏆 Multi-Provider[/bright_cyan]     OpenAI & Anthropic
[bright_cyan]⚡ Lightning Fast[/bright_cyan]     Optimized for speed & efficiency
"""
    
    # Create the welcome panel with gradient border
    welcome_content = ascii_art + subtitle + features
    
    # Display with beautiful formatting
    console.print()
    console.print(Panel.fit(
        Align.center(welcome_content),
        border_style="bright_blue",
        padding=(2, 4),
        title="[bold bright_white]🌟 Welcome to the Future of AI Benchmarking 🌟[/bold bright_white]",
        title_align="center"
    ))
    console.print("[dim bright_blue]Let's get you started with your first benchmark...[/dim bright_blue]")
    console.print()

def format_help_text(text: str, title: str = "", border_style: str = "cyan") -> str:
    """Format help text with proper alignment and borders"""
    # Clean up the text to ensure proper alignment
    lines = text.strip().split('\n')
    
    # Find the maximum line length for proper box sizing
    max_length = max(len(line.strip()) for line in lines if line.strip())
    
    # Ensure minimum width for better readability
    box_width = max(max_length + 4, 60)
    
    # Format each line to ensure consistent width
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line:
            # Pad the line to ensure consistent width
            formatted_lines.append(line.ljust(box_width - 2))
    
    # Create the formatted text
    if title:
        formatted_text = f"\n{title}\n" + "\n".join(formatted_lines)
    else:
        formatted_text = "\n".join(formatted_lines)
    
    return formatted_text
