"""
Display token usage and session statistics
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


help = "Display token usage and session statistics"


def run(console, args, agent=None, conversation=None):
    """Display comprehensive session statistics including token usage."""
    
    if not agent or not hasattr(agent, 'token_manager'):
        console.print("[yellow]No statistics available yet. Start a conversation first.[/yellow]")
        return True
    
    tm = agent.token_manager
    stats = tm.get_session_stats()
    
    # Create main stats table
    table = Table(title="Session Statistics", box=box.ROUNDED, show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white", justify="right")
    
    # Session info
    duration = stats['duration_seconds']
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
    
    table.add_row("Session Duration", time_str)
    table.add_row("Total Requests", str(stats['total_requests']))
    table.add_row("", "")  # Spacer
    
    # Token usage
    table.add_row("[bold]Token Usage[/bold]", "")
    table.add_row("Input Tokens", f"{stats['total_input_tokens']:,}")
    table.add_row("Output Tokens", f"{stats['total_output_tokens']:,}")
    table.add_row("Cached Tokens", f"{stats['total_cached_tokens']:,}")
    table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
    table.add_row("", "")  # Spacer
    
    # Averages
    if stats['total_requests'] > 0:
        table.add_row("[bold]Per Request[/bold]", "")
        table.add_row("Avg Input", f"{stats['average_input_per_request']:.0f}")
        table.add_row("Avg Output", f"{stats['average_output_per_request']:.0f}")
        table.add_row("", "")  # Spacer
    
    # Context usage
    table.add_row("[bold]Context Usage[/bold]", "")
    context_pct = stats['context_usage_percent']
    context_style = "red" if context_pct >= 90 else "yellow" if context_pct >= 75 else "green"
    table.add_row("Context Used", f"[{context_style}]{context_pct:.1f}%[/{context_style}]")
    table.add_row("Context Limit", f"{stats['limits']['context']:,}")
    table.add_row("Output Limit", f"{stats['limits']['output']:,}")
    
    # Display the table
    console.print(table)
    
    # Cost estimation if available
    if args.lower() == "cost" or args.lower() == "pricing":
        costs = tm.estimate_cost()
        cost_panel = Panel(
            f"Estimated Costs (USD):\n"
            f"  Input: ${costs['input_cost']:.4f}\n"
            f"  Output: ${costs['output_cost']:.4f}\n"
            f"  [bold]Total: ${costs['total_cost']:.4f}[/bold]",
            title="Cost Estimation",
            border_style="yellow",
            box=box.MINIMAL
        )
        console.print(cost_panel)
    
    # Show recent usage trend
    if len(tm.usage_history) >= 2:
        console.print()
        recent_text = Text("Recent Usage Trend: ", style="dim")
        
        # Get last 5 usages
        recent = tm.usage_history[-5:] if len(tm.usage_history) >= 5 else tm.usage_history
        for usage in recent:
            total = usage.input_tokens + usage.output_tokens
            if total < 1000:
                recent_text.append("▁", style="green")
            elif total < 3000:
                recent_text.append("▃", style="yellow")
            elif total < 5000:
                recent_text.append("▅", style="orange1")
            else:
                recent_text.append("█", style="red")
        
        console.print(recent_text)
    
    # Tips
    console.print()
    console.print("[dim]Tips:[/dim]")
    console.print("[dim]• Add 'cost' argument to see pricing: /stats cost[/dim]")
    console.print("[dim]• Context auto-summarizes at 90% usage[/dim]")
    console.print("[dim]• File operations are limited to prevent token explosions[/dim]")
    
    return True