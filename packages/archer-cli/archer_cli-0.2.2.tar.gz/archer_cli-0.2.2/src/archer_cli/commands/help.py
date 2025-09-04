"""
/help command - Show available commands and usage information.
"""

from typing import Optional, Any
from commands import discover_commands

help = "Show available commands and their descriptions"


def run(console, args: str, *, agent: Optional[Any] = None, conversation: Optional[list] = None) -> None:
    """Display help information about available commands."""
    
    commands = discover_commands()
    
    if not commands:
        console.print("[yellow]No commands available.[/yellow]")
        return
    
    console.print("\n[bold cyan]Available Commands:[/bold cyan]")
    console.print()
    
    # Calculate max command name length for alignment
    max_name_len = max(len(name) for name, _ in commands)
    
    for name, help_text in commands:
        padded_name = f"/{name}".ljust(max_name_len + 1)
        console.print(f"  [bold green]{padded_name}[/bold green] - {help_text}")
    
    console.print()
    console.print("[dim]Type /[command] to execute a command, or just / to see the dropdown.[/dim]")