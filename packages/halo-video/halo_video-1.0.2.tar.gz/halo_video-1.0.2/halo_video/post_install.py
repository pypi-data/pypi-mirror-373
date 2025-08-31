#!/usr/bin/env python3
"""
Post-installation welcome message for HALO Video
Shows immediately after pip install
"""

from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def show_welcome():
    """Show welcome message after installation"""
    welcome_panel = Panel(
        """[bold green]🎉 HALO Video installed successfully![/bold green]

[yellow]🚀 Quick Start:[/yellow]
1. Open your terminal/command prompt
2. Run: [bold cyan]halo-video[/bold cyan]
3. Follow the interactive menu

[yellow]📋 What you'll need:[/yellow]
• Google Gemini API key (free at https://makersuite.google.com/app/apikey)
• FFmpeg (will be auto-installed if missing)

[yellow]💡 Commands available:[/yellow]
• [cyan]halo-video[/cyan] - Start the interactive CLI
• [cyan]halo-video --help[/cyan] - Show help options

[dim]Need help? Visit: https://github.com/jeet-dekivadia/halo-video[/dim]""",
        title="[bold magenta]🎥 Welcome to HALO Video![/bold magenta]",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    
    console.print(welcome_panel)

if __name__ == "__main__":
    show_welcome()
