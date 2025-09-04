"""
/status command - Show current session and system status.
"""

import time
from typing import Optional, Any

help = "Show current session and system status information"


def run(console, args: str, *, agent: Optional[Any] = None, conversation: Optional[list] = None) -> None:
    """Display current status information."""
    
    console.print("\n[bold cyan]Session Status:[/bold cyan]")
    
    if conversation:
        console.print(f"  [green]Messages in conversation:[/green] {len(conversation)}")
        
        # Count user vs assistant messages
        user_msgs = len([m for m in conversation if m.get('role') == 'user'])
        assistant_msgs = len([m for m in conversation if m.get('role') == 'assistant'])
        console.print(f"  [dim]User messages: {user_msgs}, Assistant messages: {assistant_msgs}[/dim]")
    else:
        console.print("  [yellow]No active conversation[/yellow]")
    
    if agent and hasattr(agent, 'stats'):
        stats = agent.stats
        console.print(f"\n[bold cyan]Tool Usage:[/bold cyan]")
        console.print(f"  [green]Total tool calls:[/green] {stats['tool_calls']['total']}")
        console.print(f"  [green]Successful:[/green] {stats['tool_calls']['successful']}")
        if stats['tool_calls']['failed'] > 0:
            console.print(f"  [red]Failed:[/red] {stats['tool_calls']['failed']}")
        if stats['tool_calls']['cancelled'] > 0:
            console.print(f"  [yellow]Cancelled:[/yellow] {stats['tool_calls']['cancelled']}")
            
        console.print(f"\n[bold cyan]Performance:[/bold cyan]")
        console.print(f"  [green]API calls:[/green] {stats['model_usage']['requests']}")
        console.print(f"  [green]Input tokens:[/green] {stats['model_usage']['input_tokens']:,}")
        console.print(f"  [green]Output tokens:[/green] {stats['model_usage']['output_tokens']:,}")
    
    console.print(f"\n[dim]Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")