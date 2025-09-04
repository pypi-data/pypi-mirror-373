"""
Display ignore patterns and test file paths
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from utils.ignore_manager import get_ignore_manager


help = "Display ignore patterns and test file paths"


def run(console, args, agent=None, conversation=None):
    """Display ignore patterns and optionally test specific paths."""
    
    mgr = get_ignore_manager()
    status = mgr.get_status()
    
    if not args:
        # Show overall status
        table = Table(title="Ignore Status", box=box.ROUNDED, show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white", justify="right")
        
        table.add_row("Root Path", status['root_path'])
        table.add_row("Has .gitignore", "Yes" if status['has_gitignore'] else "No")
        table.add_row("Has .archerignore", "Yes" if status['has_archerignore'] else "No")
        table.add_row("Total Patterns", str(status['total_patterns']))
        table.add_row("Allow Patterns", str(status['allow_patterns']))
        table.add_row("Ignored Dirs", str(status['ignored_dirs']))
        
        console.print(table)
        
        # Show some example patterns
        console.print()
        console.print("[bold]Sample Patterns:[/bold]")
        patterns = mgr.ignore_patterns[:10]  # Show first 10
        for pattern in patterns:
            console.print(f"  [dim]•[/dim] [yellow]{pattern}[/yellow]")
        
        if len(mgr.ignore_patterns) > 10:
            console.print(f"  [dim]... and {len(mgr.ignore_patterns) - 10} more[/dim]")
        
        console.print()
        console.print("[dim]Usage: /ignore <path> - Test if a path would be ignored[/dim]")
    
    else:
        # Test specific path
        test_path = args.strip()
        is_ignored = mgr.should_ignore(test_path)
        
        status_text = "[red]IGNORED[/red]" if is_ignored else "[green]ALLOWED[/green]"
        
        result_panel = Panel(
            f"Path: [cyan]{test_path}[/cyan]\n"
            f"Status: {status_text}\n\n"
            f"{'This path matches ignore patterns and will be blocked from file operations.' if is_ignored else 'This path is allowed and can be accessed by file operations.'}",
            title="Path Test Result",
            border_style="red" if is_ignored else "green",
            box=box.MINIMAL
        )
        
        console.print(result_panel)
        
        # Show which patterns match (for debugging)
        if is_ignored:
            matching_patterns = []
            for pattern in mgr.ignore_patterns:
                if mgr._matches_pattern(test_path, pattern):
                    matching_patterns.append(pattern)
            
            if matching_patterns:
                console.print()
                console.print("[bold]Matching patterns:[/bold]")
                for pattern in matching_patterns:
                    console.print(f"  [dim]•[/dim] [yellow]{pattern}[/yellow]")
    
    return True