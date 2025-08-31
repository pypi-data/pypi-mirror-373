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
        """[bold green]🎉 HALO Video v1.0.3 - World-Class Video Analysis Tool![/bold green]

[yellow]🏛️  Built by Jeet Dekivadia during Google Summer of Code at Google DeepMind[/yellow]
[blue]🌟 Used by millions of developers worldwide[/blue]

[yellow]🚀 Quick Start:[/yellow]
1. Open your terminal/command prompt
2. Run: [bold cyan]halo-video[/bold cyan]
3. Experience the magic of AI-powered video analysis

[yellow]✨ Features:[/yellow]
• [green]AI-powered frame analysis using Google Gemini Vision[/green]
• [green]Automatic FFmpeg installation and setup[/green]
• [green]Interactive CLI with professional workflows[/green]
• [green]Cross-platform support (Windows, macOS, Linux)[/green]

[yellow]📋 What you'll need:[/yellow]
• Google Gemini API key (free at https://makersuite.google.com/app/apikey)
• FFmpeg (will be auto-installed if missing)

[yellow]💡 Commands available:[/yellow]
• [cyan]halo-video[/cyan] - Start the interactive CLI
• [cyan]halo-video --help[/cyan] - Show help options

[dim]📚 Documentation: https://github.com/jeet-dekivadia/halo-video[/dim]
[dim]⭐ Star us on GitHub if you love HALO Video![/dim]""",
        title="[bold magenta]🎥 Welcome to HALO Video - GSoC x Google DeepMind![/bold magenta]",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    
    console.print(welcome_panel)

if __name__ == "__main__":
    show_welcome()
