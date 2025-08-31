#!/usr/bin/env python3
"""
Post-installation welcome message for HALO Video
Built by Jeet Dekivadia during Google Summer of Code at Google DeepMind
"""

from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def show_welcome():
    """Show welcome message after installation"""
    welcome_panel = Panel(
        """[bold green]HALO Video installed successfully![/bold green]

[yellow]Built by Jeet Dekivadia during Google Summer of Code at Google DeepMind[/yellow]

[yellow]Quick Start:[/yellow]
1. Get your free Google Gemini API key: https://makersuite.google.com/app/apikey
2. Run: [bold cyan]halo-video[/bold cyan]
3. Follow the interactive setup

[yellow]Features:[/yellow]
• AI-powered frame analysis using Google Gemini Vision
• Automatic FFmpeg installation and setup  
• Interactive CLI with professional workflows
• Cross-platform support (Windows, macOS, Linux)

[yellow]Commands available:[/yellow]
• [cyan]halo-video[/cyan] - Start the interactive CLI
• [cyan]halo-video --help[/cyan] - Show help options

[dim]Documentation: https://github.com/jeet-dekivadia/halo-video[/dim]""",
        title="[bold blue]Welcome to HALO Video[/bold blue]",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    console.print(welcome_panel)

if __name__ == "__main__":
    show_welcome()
