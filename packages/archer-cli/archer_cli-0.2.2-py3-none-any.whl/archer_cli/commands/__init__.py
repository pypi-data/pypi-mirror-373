from importlib import import_module
from typing import Optional, Any, List, Tuple, Dict
import os
import glob
from pathlib import Path


def discover_commands() -> List[Tuple[str, str]]:
    """Discover available command modules and custom .archer commands.

    Returns list of (command_name, help_text) tuples.
    """
    commands_dir = Path(__file__).parent
    command_files = commands_dir.glob("*.py")
    commands: List[Tuple[str, str]] = []

    # Built-in python commands
    for file_path in command_files:
        if file_path.name.startswith('_') or file_path.name == '__init__.py':
            continue

        command_name = file_path.stem
        try:
            module = load_command(command_name)
            # Try to get help_text from a function or attribute
            if hasattr(module, 'help_text') and callable(module.help_text):
                help_text = module.help_text()
            elif hasattr(module, 'help'):
                help_text = module.help
            else:
                help_text = f'Run {command_name} command'
            commands.append((command_name, help_text))
        except Exception:
            # Skip commands that can't be loaded
            continue

    # Custom markdown commands in .archer/commands
    commands.extend(discover_custom_commands())

    # Sort by name
    return sorted(commands, key=lambda x: x[0])


def get_custom_commands_dir() -> Path:
    """Return the path to the custom commands directory: .archer/commands"""
    return Path.cwd() / ".archer" / "commands"


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Parse simple YAML frontmatter from a markdown string.

    Returns (metadata_dict, body_text). Gracefully degrades if no frontmatter.
    """
    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].strip() == '---':
        meta: Dict[str, str] = {}
        i = 1
        while i < len(lines):
            line = lines[i]
            if line.strip() == '---':
                body = "\n".join(lines[i + 1:]).strip()
                return meta, body
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip().lower()] = value.strip().strip("'\"")
            i += 1
    return {}, text.strip()


def discover_custom_commands() -> List[Tuple[str, str]]:
    """Discover custom markdown commands in .archer/commands.

    Each .md file defines a command by filename; help text from frontmatter 'description'.
    """
    custom_dir = get_custom_commands_dir()
    if not custom_dir.exists():
        return []

    commands: List[Tuple[str, str]] = []
    for md_path in sorted(custom_dir.glob("*.md")):
        try:
            name = md_path.stem
            text = md_path.read_text(encoding='utf-8')
            meta, _ = parse_frontmatter(text)
            help_text = meta.get('description') or f"Run {name} custom command"
            commands.append((name, help_text))
        except Exception:
            continue
    return commands


def filter_commands(query: str, commands: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Filter commands by query string (prefix matching)."""
    if not query:
        return commands
    
    query_lower = query.lower()
    return [
        (name, help_text) for name, help_text in commands
        if name.lower().startswith(query_lower)
    ]


def load_command(name: str):
    """Dynamically import a command module by name.

    A command module must expose a `run(console, args)` callable and
    an optional `help` string.
    """
    module_name = f"archer_cli.commands.{name}"
    return import_module(module_name)


def try_run(console, text: str, *, agent: Optional[Any] = None, conversation: Optional[list] = None) -> bool:
    """Try to execute a slash command.

    Returns True if a command was executed, False otherwise.
    """
    if not text or not text.startswith('/'):
        return False
    # Parse: /name [args...]
    raw = text[1:].strip()
    if not raw:
        console.print("[yellow]Empty command. Try '/init'.[/yellow]")
        return True
    parts = raw.split(maxsplit=1)
    name = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Try built-in command module first
    try:
        mod = load_command(name)
    except Exception:
        # If not a built-in, try custom markdown command
        custom_result = _try_run_custom_markdown(console, name, args, agent=agent, conversation=conversation)
        if custom_result is not None:
            return custom_result
        console.print(f"[red]Unknown command:[/red] /{name}")
        return True

    run = getattr(mod, 'run', None)
    if not callable(run):
        console.print(f"[red]Command '/{name}' is missing a run() function.[/red]")
        return True

    try:
        # Call with optional context if supported
        try:
            result = run(console, args, agent=agent, conversation=conversation)
        except TypeError:
            result = run(console, args)
        
        # Return the command result, defaulting to True for backwards compatibility
        return result if result is not None else True
    except Exception as e:
        console.print(f"[red]/{name} failed:[/red] {e}")
        return True


def _try_run_custom_markdown(console, name: str, args: str, *, agent: Optional[Any], conversation: Optional[list]) -> Optional[Any]:
    """Try to execute a custom markdown command from .archer/commands.

    Returns one of:
      - "PROCESS_CONVERSATION" to trigger agent processing
      - True to indicate handled without processing
      - None if no such custom command exists
    """
    md_path = get_custom_commands_dir() / f"{name}.md"
    if not md_path.exists():
        return None

    try:
        text = md_path.read_text(encoding='utf-8')
    except Exception as e:
        console.print(f"[red]Failed to read custom command:[/red] {e}")
        return True

    meta, body = parse_frontmatter(text)
    title = meta.get('title') or name.replace('_', ' ').title()
    description = meta.get('description')

    # Compose a directive-style prompt so the agent executes the command body
    # rather than attempting to implement a new feature/command.
    prompt_lines = []
    prompt_lines.append(f"Execute custom command: {title}")
    if description:
        prompt_lines.append(f"Purpose: {description}")
    if args:
        prompt_lines.append(f"Additional context: {args}")
    prompt_lines.append(
        (
            "IMPORTANT: Perform the task described below now. Do NOT implement or create a new"
            " command/feature unless the body explicitly instructs you to. Do NOT write code or"
            " change files unless explicitly asked. If the task is a review, produce a thorough"
            " review report only."
        )
    )
    prompt_lines.append("")
    prompt_lines.append("--- COMMAND BODY START ---")
    prompt_lines.append(body)
    prompt_lines.append("--- COMMAND BODY END ---")
    prompt = "\n".join(prompt_lines)

    # UI: show as a tool-like call and result if agent supports it
    try:
        if agent is not None and hasattr(agent, 'display_tool_call'):
            # Display a pseudo tool call
            agent.display_tool_call("custom_command", f"name={name}, file=.archer/commands/{name}.md")
        else:
            from rich.panel import Panel
            from rich import box as _box
            from rich.text import Text as _Text
            header = _Text()
            header.append(f"/{name}", style="bold cyan")
            header.append("  ")
            header.append(title)
            if description:
                header.append("\n")
                header.append(description, style="dim")
            console.print(Panel(header, title="Custom Command", border_style="cyan", box=_box.MINIMAL))
    except Exception:
        # Fallback plain output if Rich panel fails for any reason
        console.print(f"[cyan]/{name}[/cyan] {title}")
        if description:
            console.print(f"[dim]{description}[/dim]")

    # Inject into conversation and ask main loop to process it
    if conversation is not None:
        conversation.append({"role": "user", "content": prompt})
        try:
            if agent is not None and hasattr(agent, 'display_tool_result'):
                agent.display_tool_result("Loaded custom command and injected context")
        except Exception:
            pass
    return "PROCESS_CONVERSATION"
