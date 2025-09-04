"""
/init command - Analyze codebase and create/append to archer.md file.

This command scans the project structure and creates or appends to archer.md 
file containing project-specific instructions for AI agents, following OpenCode's approach.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Any
import tempfile

help = "Analyze codebase and create/append to archer.md file with project-specific instructions"

# Safety checks for file creation
ALLOWED_EXTENSIONS = {'.md', '.txt'}
MAX_FILE_SIZE = 50 * 1024  # 50KB max file size
SAFE_FILENAMES = {'archer.md', 'AGENTS.md', 'CLAUDE.md', 'CONTEXT.md'}

# Template for archer.md generation prompt
INIT_PROMPT = """Please analyze this codebase and create or append to the archer.md file containing project-specific instructions for AI agents.

IMPORTANT: If archer.md already exists, DO NOT replace it. Instead, append your analysis to the existing file, adding a new section with a timestamp header.

If creating a new archer.md file, structure it like this example:

# {project_name} Agent Guidelines

## Build/Test Commands
- **Install**: [package manager install command]
- **Run**: [development server command] 
- **Lint**: [linting command]
- **Typecheck**: [type checking command if applicable]
- **Test**: [run all tests command]
- **Single test**: [run specific test file command]

## Code Style
- **Runtime/Language**: [language and key frameworks]
- **Imports**: [import style preferences]
- **Types**: [typing conventions]
- **Naming**: [naming conventions]
- **Error handling**: [error handling patterns]
- **File structure**: [organization patterns]

## Architecture
- **Key concepts**: [important architectural patterns]
- **Important files/directories**: [critical paths to know]
- **Configuration**: [config file locations and formats]

If archer.md already exists, append a new section like:

---

## Project Analysis Update ({current_date})

[Your analysis here]

The analysis should be about 20-25 lines long and focus on practical information an AI agent needs to work effectively in this codebase.
If there are existing rule files (.cursorrules, .github/copilot-instructions.md, etc.), incorporate their guidance.

Current project path: {path}
Detected language: {language}"""


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe for creation."""
    path = Path(filename)
    # Must be a safe filename and have allowed extension
    return (path.name in SAFE_FILENAMES and 
            path.suffix in ALLOWED_EXTENSIONS and
            not path.is_absolute() and
            '..' not in str(path))


def detect_existing_rules() -> list:
    """Detect existing rule files in the project."""
    current_dir = Path.cwd()
    rule_files = []
    
    # Check for various rule files
    potential_files = [
        '.cursorrules',
        '.cursor/rules',
        '.github/copilot-instructions.md',
        'archer.md',
        'CLAUDE.md',
        'CONTEXT.md'
    ]
    
    for file_path in potential_files:
        full_path = current_dir / file_path
        if full_path.exists() and full_path.is_file():
            try:
                # Read and validate file size
                if full_path.stat().st_size <= MAX_FILE_SIZE:
                    rule_files.append(str(full_path))
            except (OSError, IOError):
                continue
    
    return rule_files


def get_project_info() -> dict:
    """Gather basic project information safely."""
    current_dir = Path.cwd()
    info = {
        'root': str(current_dir),
        'name': current_dir.name,
        'files': [],
        'has_git': False,
        'language': 'unknown'
    }
    
    # Check for git
    if (current_dir / '.git').exists():
        info['has_git'] = True
    
    # Detect primary language/framework
    important_files = [
        ('package.json', 'javascript'),
        ('pyproject.toml', 'python'),
        ('requirements.txt', 'python'),
        ('Cargo.toml', 'rust'),
        ('go.mod', 'go'),
        ('pom.xml', 'java'),
        ('Gemfile', 'ruby'),
        ('composer.json', 'php'),
    ]
    
    for filename, lang in important_files:
        if (current_dir / filename).exists():
            info['language'] = lang
            break
    
    return info


def run(console, args: str, *, agent: Optional[Any] = None, conversation: Optional[list] = None) -> None:
    """Analyze codebase and create AGENTS.md file."""
    
    try:
        # Get project information
        project_info = get_project_info()
        console.print(f"[green]Analyzing project:[/green] {project_info['name']} ({project_info['language']})")
        
        # Check for existing rule files
        existing_rules = detect_existing_rules()
        if existing_rules:
            console.print(f"[cyan]Found existing rule files:[/cyan] {', '.join(existing_rules)}")
        
        # Check if archer.md already exists
        archer_file = Path.cwd() / 'archer.md'
        file_exists = archer_file.exists()
        
        if file_exists:
            console.print("[yellow]archer.md already exists. New analysis will be appended.[/yellow]")
        else:
            console.print("[green]Creating new archer.md file...[/green]")
        
        # Create the initialization prompt with project context
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        prompt_text = INIT_PROMPT.format(
            project_name=project_info['name'],
            path=project_info['root'],
            language=project_info['language'],
            current_date=current_date
        )
        
        # Display immediate feedback
        console.print(f"[bold green]✓[/bold green] [green]Initialized project analysis for {project_info['name']}[/green]")
        console.print("[cyan]→ Agent will now analyze the codebase structure...[/cyan]")
        console.print("[dim]→ Creating/appending to archer.md with project-specific instructions[/dim]")
        
        # Provide helpful context
        if file_exists:
            console.print("[dim]→ Appending to existing archer.md file[/dim]")
        if existing_rules:
            console.print(f"[dim]→ Including guidance from {len(existing_rules)} rule files[/dim]")
        
        # Add message to conversation - the main loop should process this
        if conversation is not None:
            user_message = {"role": "user", "content": prompt_text}
            conversation.append(user_message)
            console.print("[yellow]Analysis request queued - processing...[/yellow]")
            # Return a special flag to indicate the main loop should process this message
            return "PROCESS_CONVERSATION"
        else:
            console.print("[yellow]Warning: No conversation context available.[/yellow]")
            console.print("[dim]Please ensure you're in an active chat session to use /init.[/dim]")
            console.print("[dim]The /init command needs conversation context to work with the agent.[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error during project analysis:[/red] {e}")
        console.print("[dim]Please ensure you're in a valid project directory.[/dim]")
