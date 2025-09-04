#!/usr/bin/env python3
"""
Clear command for Archer - clears conversation context and starts fresh.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import time

def run(console: Console, args: str = "", agent=None, conversation=None, **kwargs) -> str:
    """
    Clear the conversation history and start fresh.
    
    Args:
        console: Rich console for output
        args: Command arguments (unused)
        agent: The agent instance
        conversation: Current conversation list
        **kwargs: Additional keyword arguments
    
    Returns:
        "CLEARED" to signal that conversation was cleared
    """
    
    # Display clearing animation
    with console.status("[bold yellow]Clearing conversation context...", spinner="dots"):
        time.sleep(0.5)  # Brief pause for visual effect
    
    # Clear the conversation history if provided
    if conversation is not None:
        # Store the length before clearing for stats
        cleared_count = len(conversation)
        conversation.clear()
        
        # Reset agent's conversation history if available
        if agent and hasattr(agent, 'conversation_history'):
            agent.conversation_history.clear()
        
        # Clear todo list for the session if agent has todos
        if agent:
            try:
                from tools.todo import _todo_state
                if 'default' in _todo_state:
                    todo_count = len(_todo_state.get('default', []))
                    _todo_state.clear()
                else:
                    todo_count = 0
            except:
                todo_count = 0
        else:
            todo_count = 0
        
        # Display success message
        success_text = Text()
        success_text.append("✓ ", style="bold green")
        success_text.append("Conversation cleared successfully\n\n", style="green")
        
        # Add statistics
        stats_text = Text()
        stats_text.append("Cleared:\n", style="bold")
        stats_text.append(f"  • {cleared_count} messages from conversation history\n", style="dim")
        if todo_count > 0:
            stats_text.append(f"  • {todo_count} todos from the task list\n", style="dim")
        stats_text.append("\n")
        stats_text.append("You're starting fresh with a clean context!", style="italic green")
        
        # Create panel
        panel = Panel(
            Text.from_markup(
                f"[bold green]✓[/bold green] Conversation cleared successfully\n\n"
                f"[bold]Cleared:[/bold]\n"
                f"  [dim]• {cleared_count} messages from conversation history[/dim]\n"
                + (f"  [dim]• {todo_count} todos from the task list[/dim]\n" if todo_count > 0 else "")
                + "\n[italic green]You're starting fresh with a clean context![/italic green]"
            ),
            title="[bold]Context Reset[/bold]",
            title_align="left",
            border_style="green",
            box=box.ROUNDED,
            expand=True,
            padding=(1, 2)
        )
        
        console.print(panel)
        
        # Show a tip
        tip_panel = Panel(
            Text.from_markup(
                "[yellow]💡 Tip:[/yellow] The context has been cleared, but your files and "
                "work remain unchanged. The system preferences (CLI tools) will be "
                "automatically restored on your next message."
            ),
            border_style="dim",
            box=box.MINIMAL,
            expand=True
        )
        console.print(tip_panel)
        
    else:
        # No conversation to clear
        warning_panel = Panel(
            Text("No conversation context to clear.", style="yellow"),
            title="[bold]Notice[/bold]",
            title_align="left", 
            border_style="yellow",
            box=box.ROUNDED,
            expand=True
        )
        console.print(warning_panel)
    
    # Return special signal that conversation was cleared
    # This prevents the command from being added to history
    return "CLEARED"


def help_text() -> str:
    """Return help text for the clear command."""
    return "Clear conversation context and start fresh"