#!/usr/bin/env python3
"""
A chat application with Archer AI API and comprehensive tool calling support
Enhanced with Rich library for beautiful TUI
"""

import json
import logging
# Suppress HTTP logging before any other imports
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("anthropic").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

import os
import sys
import argparse
import time
import threading
import termios
import tty
import select
import signal
from typing import List, Dict, Any, Callable, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import anthropic
try:
    import tiktoken
except ImportError:
    tiktoken = None
from jsonschema import Draft7Validator
from jsonschema.validators import extend
from contextlib import contextmanager
from threading import Event
# Import the webfetch tool
from .tools.webfetch import webfetch
# Tools are now provided by a registry
from .tools_registry import ToolDefinition, build_tools
# Import ASCII logo generator
from .ascii_logo import display_startup_logo
# Import token management
from .utils.token_manager import TokenManager, TokenUsage, ConversationSummarizer, FILE_LIMITS
# Import ignore management
from .utils.ignore_manager import get_ignore_manager, should_ignore_path

# Rich imports for beautiful TUI
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.align import Align
from rich import box
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.spinner import Spinner
from .commands import try_run as try_run_command, discover_commands

# Global cancellation event for long operations (API calls, subprocesses)
CANCEL_EVENT = Event()

def load_archer_context() -> str:
    """Load archer.md file content from the current working directory for context"""
    import os
    from pathlib import Path
    
    archer_md_path = Path.cwd() / "archer.md"
    
    if archer_md_path.exists():
        try:
            with open(archer_md_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            logging.info(f"Loaded archer.md context ({len(content)} characters)")
            return content
        except Exception as e:
            logging.warning(f"Failed to load archer.md: {e}")
            return ""
    else:
        logging.info("No archer.md file found in current directory")
        return ""

def add_to_archer_memory(memory_content: str) -> str:
    """Add content to archer.md memory file"""
    from pathlib import Path
    from datetime import datetime
    
    archer_md_path = Path.cwd() / "archer.md"
    
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Format the memory entry
        memory_entry = f"\n- {memory_content} (added {timestamp})"
        
        # Read existing content or create new
        if archer_md_path.exists():
            with open(archer_md_path, 'r', encoding='utf-8') as f:
                existing_content = f.read().strip()
        else:
            existing_content = "# Project Memory\n\nMemory entries:"
        
        # Append the new memory entry
        updated_content = existing_content + memory_entry
        
        # Write back to file
        with open(archer_md_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logging.info(f"Added memory to archer.md: {memory_content}")
        return f"✓ Added to memory: {memory_content}"
        
    except Exception as e:
        error_msg = f"Failed to add memory to archer.md: {e}"
        logging.error(error_msg)
        return f"✗ Error: {error_msg}"

class OperationAborted(Exception):
    """Raised when ESC cancels the current operation"""
    pass


def signal_handler(sig, frame):
    """Handle Ctrl+C and other signals for termination"""
    # Raise KeyboardInterrupt to trigger graceful shutdown
    raise KeyboardInterrupt()

def main():
    """Main entry point of the application"""
    # Set up signal handlers for immediate termination
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    parser = argparse.ArgumentParser(description="Chat with Archer using tools")
    parser.add_argument("--verbose", action="store_true", help="enable verbose logging")
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d: %(message)s'
        )
        logging.info("Verbose logging enabled")
        # Suppress HTTP request logging even in verbose mode
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("anthropic").setLevel(logging.ERROR)
        logging.getLogger("httpcore").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    # Initialize Rich console with full width support
    # width=None means use full terminal width
    # For very wide terminals, you can set a max width like: min(200, os.get_terminal_size().columns)
    console = Console(width=None, legacy_windows=False)  # Full responsive width
    
    # Initialize Anthropic client with logging suppressed
    # Disable httpx logging at the client level
    import httpx
    client = anthropic.Anthropic(
        http_client=httpx.Client(
            event_hooks={'request': [], 'response': []}  # No hooks for logging
        )
    )
    if args.verbose:
        logging.info("Anthropic client initialized")
    
    # Get user message function with responsive prompt
    def get_user_message() -> tuple[str, bool]:
        try:
            return agent.get_user_input()
        except KeyboardInterrupt:
            # Return empty string with False to trigger normal exit
            return "", False
        except EOFError:
            return "", False
    
    # Initialize tools and agent
    tools = build_tools()
    if args.verbose:
        logging.info(f"Initialized {len(tools)} tools via registry")
    
    agent = RichAgent(client, get_user_message, tools, args.verbose, console)
    try:
        agent.run()
    except KeyboardInterrupt:
        # User pressed Ctrl+C, exit gracefully with stats
        console.print("\n")  # New line for cleaner output
        agent.display_exit_stats(time.time() - agent.stats['performance']['wall_time_start'])
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if args.verbose:
            logging.error(f"Agent run failed: {e}", exc_info=True)
        # Still show stats on error
        try:
            agent.display_exit_stats(time.time() - agent.stats['performance']['wall_time_start'])
        except:
            pass


class RichAgent:
    """Main agent class that handles conversation with Archer using Rich TUI"""
    
    def __init__(self, client: anthropic.Anthropic, get_user_message: Callable[[], tuple[str, bool]], 
                 tools: List['ToolDefinition'], verbose: bool, console: Console):
        self.client = client
        self.get_user_message = get_user_message
        self.tools = tools
        self.verbose = verbose
        self.console = console
        self.conversation_history = []
        # Store original terminal size for comparison
        self.last_width = self.console.width
        # Track timing for operations
        self.operation_start_time = None
        self.timer_thread = None
        self.timer_stop = False
        # Planning mode for complex tasks
        self.planning_mode = False
        self.current_plan = []
        # Command history for up/down arrow navigation
        self.command_history = []
        self.history_index = -1
        # ESC key monitoring
        self.esc_pressed = False
        self.processing = False
        # Persistent footer live renderer
        self.footer_live = None
        # Load archer.md context on startup
        self.archer_context = load_archer_context()
        
        # Initialize token manager
        self.token_manager = TokenManager("claude-sonnet-4-20250514")
        
        # Statistics tracking
        self.stats = {
            'tool_calls': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'cancelled': 0,
                'by_tool': {}
            },
            'performance': {
                'wall_time_start': time.time(),
                'agent_active_time': 0.0,
                'api_time': 0.0,
                'tool_time': 0.0,
                'api_calls': []
            },
            'model_usage': {
                'requests': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'cached_tokens': 0
            }
        }
        
    @contextmanager
    def temporarily_stop_footer(self):
        """Context manager to stop footer Live while other Lives run/input occurs."""
        had_footer = bool(self.footer_live)
        if had_footer:
            try:
                self.footer_live.stop()
            except Exception:
                pass
        try:
            yield
        finally:
            if had_footer:
                try:
                    self.footer_live.start()
                    self.footer_live.update(self.render_footer())
                except Exception:
                    pass
    
    def run_with_cancellable_live(self, message: str, worker: Callable[[], Any], style: str = "bold cyan") -> tuple[Any, Optional[Exception], bool]:
        """Run a callable in a daemon thread with a cancellable Live panel.

        Returns (result, error, cancelled)
        - result: value returned by worker or None
        - error: exception raised by worker or None
        - cancelled: True if ESC cancelled the run
        """
        CANCEL_EVENT.clear()
        result_holder: Dict[str, Any] = {"result": None, "error": None}
        start_time = time.time()
        with self.temporarily_stop_footer():
            with self.esc_listener():
                with Live(
                    Panel(Text(f"{message} (0.0s)", style=style), box=box.MINIMAL, expand=True),
                    console=self.console,
                    refresh_per_second=20,
                    transient=False,
                ) as live:
                    def target_wrapper():
                        try:
                            result_holder["result"] = worker()
                        except Exception as e:
                            result_holder["error"] = e
                    t = threading.Thread(target=target_wrapper, daemon=True)
                    t.start()
                    self.processing = True
                    try:
                        while t.is_alive():
                            # ESC listener sets CANCEL_EVENT
                            if CANCEL_EVENT.is_set():
                                CANCEL_EVENT.set()
                                live.update(Panel(Text("Aborting...", style="yellow"), box=box.MINIMAL, expand=True))
                                break
                            elapsed = time.time() - start_time
                            hint = Text(" ESC to stop", style="dim")
                            body = Text(f"{message} ({elapsed:.1f}s) ")
                            body.append(hint)
                            live.update(Panel(body, box=box.MINIMAL, expand=True, border_style=style.replace('bold ', '')))
                            time.sleep(0.05)
                    finally:
                        self.processing = False
        cancelled = CANCEL_EVENT.is_set()
        if cancelled:
            CANCEL_EVENT.clear()
        return result_holder["result"], result_holder["error"], cancelled
    
    @contextmanager
    def esc_listener(self):
        """Start a temporary ESC key listener in a background thread.

        It sets terminal to cbreak mode, reads bytes non-blocking, and sets
        CANCEL_EVENT when ESC (\x1b) is detected. Restores terminal settings
        on exit.
        """
        if not sys.stdin.isatty():
            yield
            return
        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
        except Exception:
            old_settings = None
        stop_event = threading.Event()

        def reader_loop():
            try:
                tty.setcbreak(fd)
                while not stop_event.is_set() and not CANCEL_EVENT.is_set():
                    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if not rlist:
                        continue
                    try:
                        ch = sys.stdin.read(1)
                    except Exception:
                        continue
                    if ch == "\x1b":
                        CANCEL_EVENT.set()
                        break
            finally:
                # do not restore here; main finally will
                pass

        t = threading.Thread(target=reader_loop, daemon=True)
        t.start()
        try:
            yield
        finally:
            stop_event.set()
            try:
                t.join(timeout=0.2)
            except Exception:
                pass
            if old_settings is not None:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    termios.tcflush(fd, termios.TCIFLUSH)
                except Exception:
                    pass
        
    def check_for_esc_key(self):
        """Check if ESC key was pressed - simplified version"""
        # Non-blocking ESC detection using select + cbreak
        try:
            if not sys.stdin.isatty():
                return False
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], 0)
                if rlist:
                    ch = sys.stdin.read(1)
                    if ch == "\x1b":  # ESC
                        # Clear any buffered input
                        termios.tcflush(fd, termios.TCIFLUSH)
                        CANCEL_EVENT.set()
                        return True
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            return False
        return False
        
    def render_footer(self):
        """Return a dim footer showing only the current folder.

        The footer is intended to be displayed via a persistent Live instance
        so it remains fixed at the bottom of the screen.
        """
        import os as _os
        cwd_name = _os.path.basename(_os.getcwd())
        if not cwd_name:
            cwd_name = _os.path.expanduser("~")
        footer = Text(f"~/{cwd_name}", style="dim")
        return Align.left(footer)
        
    def create_info_panel(self) -> Panel:
        """Create a compact welcome panel to complement the ASCII logo"""
        # Welcome section with friendly variations
        import random
        welcome_messages = [
            "What would you like to create today?",
            "How can I help you today?",
            "Let's create something together!",
            "What can we build today?",
            "Ready to bring your ideas to life?",
            "What project shall we work on?",
            "Let's make something amazing!"
        ]
        welcome_text = Text(random.choice(welcome_messages), style="bold green")
        
        # Status and controls in compact format
        status_line = Text()
        status_line.append("Status: ", style="dim")
        status_line.append("Ready to chat", style="bold green")
        status_line.append(" | ", style="dim")
        status_line.append("9 tools", style="cyan")
        status_line.append(" • ", style="dim")
        status_line.append("4 commands", style="cyan")
        
        controls_text = Text("Exit: 'exit' or Ctrl+C | Cancel: ESC | Commands: /help | Memory: #<text>", style="dim")
        
        # Combine sections compactly
        info_group = Group(
            welcome_text,
            Text(""),  # Spacer
            status_line,
            controls_text
        )
        
        # Create panel with minimal styling
        return Panel(info_group, box=box.MINIMAL, style="dim", padding=(0, 1), expand=True)
    
    def display_message(self, role: str, content: str, is_tool: bool = False):
        """Display a message in a responsive format"""
        # Use Markdown rendering for better formatting of longer messages
        if role == "user":
            # Clean, minimal user message display
            self.console.print(f"\n[dim blue]You:[/dim blue] {content}")
        elif role == "assistant":
            # Skip empty content
            if not content or not content.strip():
                if self.verbose:
                    logging.warning("Skipping empty assistant message")
                return
            # Assistant message in a clean panel
            self.console.print()  # Add spacing before panel
            assistant_panel = Panel(
                content,
                title="[bold]Archer[/bold]",
                title_align="left",
                border_style="green",
                box=box.ROUNDED,  # Changed from MINIMAL to ROUNDED for clearer borders
                expand=True
            )
            self.console.print(assistant_panel)
        else:
            # Other roles
            other_panel = Panel(
                content,
                title=f"[bold]{role.title()}[/bold]",
                title_align="left",
                border_style="yellow",
                expand=True  # Use full terminal width
            )
            self.console.print(other_panel)
    
    def display_tool_call(self, tool_name: str, tool_input: str):
        """Display a tool call with bullet format"""
        # Format the input for better readability
        try:
            import json
            input_obj = json.loads(tool_input) if isinstance(tool_input, str) else tool_input
            # Create a compact display of key parameters
            if isinstance(input_obj, dict):
                params = []
                for key, value in input_obj.items():
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    params.append(f"'{key}': {repr(value)}")
                formatted_input = "{" + ", ".join(params) + "}"
            else:
                formatted_input = str(input_obj)[:100] + ("..." if len(str(input_obj)) > 100 else "")
        except:
            formatted_input = str(tool_input)[:100] + ("..." if len(str(tool_input)) > 100 else "")
        
        # For bash commands, we don't show the tool call since the live display shows the actual command
        # For other tools, show the normal format
        if tool_name.lower() != "bash":
            self.console.print(f"[bold green]•[/bold green] [cyan]{tool_name}[/cyan]([dim]{formatted_input}[/dim])")
    
    def display_tool_result(self, result: str, is_error: bool = False, elapsed_time: float = 0):
        """Display a tool result with bullet format"""
        # Format the result for compact display
        time_str = f" ({elapsed_time:.2f}s)" if elapsed_time > 0 else ""
        
        if is_error:
            self.console.print(f"[bold red]↳[/bold red] [red]Error{time_str}[/red]: {result[:100]}{'...' if len(result) > 100 else ''}")
        else:
            # Just show the actual result, no extra processing
            if not result or result.strip() == "":
                self.console.print(f"[bold green]↳[/bold green] [green]No output{time_str}[/green]")
            else:
                lines_count = len(result.split('\n')) if result else 0
                if lines_count > 3:
                    # For multi-line output, show line count
                    self.console.print(f"[bold green]↳[/bold green] [green]Output ({lines_count} lines){time_str}[/green]")
                else:
                    # For short output, show it directly
                    result_preview = result[:100] + ("..." if len(result) > 100 else "")
                    self.console.print(f"[bold green]↳[/bold green] [green]{result_preview}{time_str}[/green]")
        
        # Add spacing after tool result
        self.console.print()
    
    
    def count_tokens(self, text: str, model: str = "claude-sonnet-4-20250514") -> int:
        """Count tokens in text using tiktoken"""
        if not tiktoken or not text:
            # Fallback: rough approximation (4 chars per token)
            return len(text) // 4
        
        try:
            # Use GPT-4 encoding as approximation for Claude
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            # Fallback: rough approximation
            return len(text) // 4
    
    def display_processing_summary(self, response_text: str, elapsed_time: float):
        """Display processing summary with tokens instead of characters"""
        tokens = self.count_tokens(response_text)
        self.console.print()
        self.console.print(f"[bold green][x][/bold green] [green]Archer finished processing[/green] [dim]|[/dim] [yellow]{elapsed_time:.2f}s[/yellow] [dim]|[/dim] [cyan]{tokens} tokens[/cyan]")
        self.console.print()
    
    def check_terminal_resize(self):
        """Check if terminal has been resized and refresh if needed"""
        current_width = self.console.width
        if current_width != self.last_width:
            self.last_width = current_width
            return True
        return False
    
    def should_create_plan(self, user_input: str) -> bool:
        """Ask the LLM if this task requires planning"""
        planning_assessment_prompt = f"""Analyze this user request and determine if it requires a structured plan before execution:

"{user_input}"

Does this request involve multiple complex steps that would benefit from planning? Consider:
- Does it require design, implementation, testing, and documentation?
- Does it involve multiple files, components, or systems?
- Would breaking it into steps help ensure nothing is missed?
- Is it more than a simple single-action request?

Respond with exactly "YES" if planning would be beneficial, or "NO" if it's a simple task that can be done directly."""
        
        try:
            # Quick assessment using a simple API call
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": planning_assessment_prompt}]
            )
            
            # Extract response text
            response_text = ""
            for content in response.content:
                if content.type == "text":
                    response_text += content.text
            
            # Check if the response indicates planning is needed
            return "YES" in response_text.upper().strip()
            
        except Exception as e:
            if self.verbose:
                logging.error(f"Planning assessment failed: {e}")
            # Fallback: assume planning is not needed if assessment fails
            return False
    
    def create_plan_prompt(self, user_input: str) -> str:
        """Create a prompt asking Archer to plan the task"""
        return f"""I need to help you with the following task:
        
{user_input}

This appears to be a multi-step process. Let me create a concise plan first.

Please provide a brief, high-level plan with just the key steps (3-7 steps maximum):
- Focus on the main phases/milestones
- Keep each step concise (one line)
- Skip detailed sub-tasks for now
- List steps in execution order

Once you approve the plan, I'll execute each step systematically with full details."""
    
    def display_plan(self, plan_text: str):
        """Display the proposed plan in a special panel"""
        plan_panel = Panel(
            plan_text,
            title="[bold]Proposed Plan[/bold]",
            title_align="left",
            border_style="cyan",
            box=box.DOUBLE,
            expand=True
        )
        self.console.print(plan_panel)
        
        # Ask for confirmation
        confirm_panel = Panel(
            "[bold cyan]Do you want to proceed with this plan?[/bold cyan]\n\n" +
            "Type 'yes' to execute the plan, 'modify' to adjust it, or 'skip' to proceed without planning.",
            title="[bold]Plan Confirmation[/bold]",
            title_align="left",
            border_style="yellow",
            box=box.ROUNDED,
            expand=True
        )
        self.console.print(confirm_panel)
    
    def get_user_input(self) -> tuple[str, bool]:
        """Get user input with command history navigation and environment info"""
        try:
            # Use readline for command history
            import readline
            import subprocess
            import os
            
            # Set up readline history
            for cmd in self.command_history:
                readline.add_history(cmd)
            
            # Minimal prompt that plays nicely with Live
            prompt_markup = "[bold yellow]›[/bold yellow] "
            
            # Build a pretty one-line status above the prompt: git branch, python env, node (nvm)
            try:
                # Git branch
                try:
                    branch = subprocess.check_output(
                        ['git', 'branch', '--show-current'],
                        stderr=subprocess.DEVNULL
                    ).decode().strip()
                    if not branch:
                        branch = None
                except Exception:
                    branch = None

                # Python env info
                import sys as _sys
                py_ver = f"py{_sys.version_info.major}.{_sys.version_info.minor}"
                venv_name = os.path.basename(os.environ.get('VIRTUAL_ENV', '') or '') or os.environ.get('CONDA_DEFAULT_ENV')
                py_seg = f"{py_ver}{' · ' + venv_name if venv_name else ''}"

                # Node/NVM info
                nvm_dir = os.environ.get('NVM_DIR')
                try:
                    node_ver = subprocess.check_output(['node', '-v'], stderr=subprocess.DEVNULL).decode().strip()
                except Exception:
                    node_ver = None
                node_seg = None
                if node_ver:
                    node_seg = f"{node_ver}{' · nvm' if nvm_dir else ''}"

                segs = []
                if branch:
                    segs.append(f"[cyan]git:[/cyan] [bold cyan]{branch}[/bold cyan]")
                segs.append(f"[magenta]{py_seg}[/magenta]")
                if node_seg:
                    segs.append(f"[green]{node_seg}[/green]")
                sep = Text(" | ", style="dim").markup
                status_line = sep.join(segs)
                # Plain version for bottom-anchored prompt (raw ANSI printing)
                segs_plain = []
                if branch:
                    segs_plain.append(f"git: {branch}")
                segs_plain.append(py_seg)
                if node_seg:
                    segs_plain.append(node_seg)
                status_line_plain = " | ".join(segs_plain)
            except Exception:
                status_line = ""
                status_line_plain = ""
            
            # Enhanced input with live dropdown
            try:
                with self.temporarily_stop_footer():
                    if status_line:
                        self.console.print(status_line)
                    # Get available commands
                    available_commands = discover_commands()
                    
                    current_input = self._get_input_with_live_dropdown(available_commands)
                
                # Add to history if it's not empty and not the same as the last command
                if current_input.strip() and (not self.command_history or current_input != self.command_history[-1]):
                    self.command_history.append(current_input)
                    if len(self.command_history) > 100:
                        self.command_history.pop(0)
                
                return current_input, True
                
            except EOFError:
                return "", False
                
        except Exception as e:
            # Fallback to basic input on any error
            if self.verbose:
                self.console.print(f"[yellow]Live dropdown failed, using fallback input: {e}[/yellow]")
            try:
                if status_line:
                    self.console.print(status_line)
                current_input = input("› ")
                
                # Check for command suggestions even in fallback mode
                if current_input == '/':
                    try:
                        available_commands = discover_commands()
                        self.console.print("\n[bold cyan]Available commands:[/bold cyan]")
                        for name, help_text in available_commands:
                            self.console.print(f"  [green]/{name}[/green] - {help_text}")
                        self.console.print("\n[dim]Type the command name after / (e.g., /help)[/dim]")
                        # Get input again
                        current_input = input("› ")
                    except Exception:
                        pass
                
                # Add to history
                if current_input.strip() and (not self.command_history or current_input != self.command_history[-1]):
                    self.command_history.append(current_input)
                    if len(self.command_history) > 100:
                        self.command_history.pop(0)
                
                return current_input, True
                
            except EOFError:
                return "", False
            except KeyboardInterrupt:
                return "", False
    
    def _get_input_with_live_dropdown(self, available_commands):
        """Get input with live dropdown that appears as you type."""
        import sys
        import termios
        import tty
        import select
        
        # Check if stdin is a tty (interactive terminal)
        if not sys.stdin.isatty():
            # Fallback to simple input if not interactive
            return input("› ")
        
        current_input = ""
        show_dropdown = False
        selected_index = 0
        filtered_commands = []
        max_dropdown_lines = 0  # Track maximum lines used for proper clearing

        # Track a one-line memory indicator below the prompt when typing '#'
        memory_indicator_visible = False
        
        # Clear any lingering dropdown content from previous input sessions
        def force_clear_screen_area():
            """Force clear potential dropdown area from previous sessions"""
            print("\033[s", end="")  # Save cursor
            # Clear up to 20 lines below cursor to be absolutely sure
            for i in range(20):  
                print(f"\033[{i+1}B\033[K", end="")  # Move down and clear line
            print("\033[u", end="", flush=True)  # Restore cursor
        
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        def show_memory_indicator():
            nonlocal memory_indicator_visible
            # Render a single cyan/dim line one row below the prompt
            print("\033[s", end="")            # Save cursor
            print("\033[1B\033[0G", end="")    # Move one line down, go to column 0
            print("\033[K", end="")             # Clear the entire line
            # Cyan label + dim help text
            print("\033[36mMemory mode\033[0m \033[90m(Enter to save to archer.md)\033[0m")
            print("\033[u", end="", flush=True)  # Restore cursor
            memory_indicator_visible = True

        def clear_memory_indicator():
            nonlocal memory_indicator_visible
            if not memory_indicator_visible:
                return
            print("\033[s", end="")            # Save cursor
            print("\033[1B\033[0G\033[K", end="")  # Move down one line, clear it
            print("\033[u", end="", flush=True)  # Restore cursor
            memory_indicator_visible = False
        
        def filter_commands(query):
            if not query:
                return available_commands
            query_lower = query.lower()
            return [(name, help_text) for name, help_text in available_commands 
                   if name.lower().startswith(query_lower)]

        def _estimate_dropdown_height(commands_list) -> int:
            """Estimate how many terminal rows the dropdown will consume.

            Accounts for line-wrapping of long help texts by approximating the
            rendered width and summing wrapped rows across all items.
            """
            try:
                term_width = getattr(self.console, "width", None) or 80
            except Exception:
                term_width = 80

            if term_width <= 0:
                term_width = 80

            total_rows = 0
            # Prefix length is the same for selected/non-selected visually (5 chars):
            # '  > /' vs '    /', then ' - ' (3 chars)
            for name, help_text in commands_list:
                visible = f"    /{name} - {help_text}"
                # Count wrapped rows; ensure at least one row
                length = len(visible)
                rows = (length + term_width - 1) // term_width
                total_rows += max(1, rows)
            return total_rows
        
        def render_dropdown():
            nonlocal max_dropdown_lines
            if not show_dropdown or not filtered_commands:
                # If we're hiding dropdown, clear any existing content
                if max_dropdown_lines > 0:
                    clear_dropdown_lines()
                    max_dropdown_lines = 0
                return

            # Ensure memory indicator is not visible when showing dropdown
            clear_memory_indicator()

            # Estimate rows required and ensure we will overwrite any previous rows
            new_height = _estimate_dropdown_height(filtered_commands)
            rows_to_draw = max(new_height, max_dropdown_lines)

            # Render in place below the prompt without allocating extra newlines
            print("\033[s", end="")  # Save cursor
            print("\033[1B\033[0G", end="")  # Move to dropdown start (one line below)

            # Compose and write each row; clear any leftover rows
            for i in range(rows_to_draw):
                if i < len(filtered_commands):
                    name, help_text = filtered_commands[i]
                    if i == selected_index:
                        line = f"\033[44m\033[37m  > /{name}\033[0m - {help_text}"
                    else:
                        line = f"\033[32m    /{name}\033[0m - \033[90m{help_text}\033[0m"
                else:
                    line = "\033[K"  # clear any leftover content on this row

                # Clear the line and print content
                print("\033[K" + line, end="")
                # Move to next row (except after last)
                if i < rows_to_draw - 1:
                    print("\033[1B\033[0G", end="")
            print("\033[u", end="", flush=True)  # Restore cursor

            # Track max height so we can fully clear on next update
            max_dropdown_lines = rows_to_draw
        
        def clear_dropdown_lines(num_lines=None):
            nonlocal max_dropdown_lines
            # Clear the number of terminal rows we previously rendered.
            lines_to_clear = max_dropdown_lines if num_lines is None else max(num_lines, max_dropdown_lines)

            if lines_to_clear > 0:
                # Save cursor position, clear dropdown area, restore cursor
                print("\033[s", end="")  # Save cursor position
                print("\033[1B\033[0G", end="")  # Move to dropdown area

                # Clear all dropdown rows
                for i in range(lines_to_clear):
                    print("\033[K", end="")  # Clear current line
                    if i < lines_to_clear - 1:
                        print("\033[1B\033[0G", end="")  # Move to next line

                print("\033[u", end="", flush=True)  # Restore cursor to original position
        
        try:
            tty.setcbreak(fd)  # Use cbreak mode instead of raw
            
            # Clear any lingering content from previous sessions
            force_clear_screen_area()
            
            print("› ", end="", flush=True)
            
            while True:
                if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                    char = sys.stdin.read(1)
                    
                    if char == '\n' or char == '\r':  # Enter
                        if show_dropdown and filtered_commands and selected_index < len(filtered_commands):
                            # Select the highlighted command
                            selected_cmd = filtered_commands[selected_index][0]
                            current_input = f"/{selected_cmd}"
                        break
                        
                    elif char == '\t':  # Tab - complete selected
                        if show_dropdown and filtered_commands and selected_index < len(filtered_commands):
                            selected_cmd = filtered_commands[selected_index][0]
                            # Clear current dropdown
                            if show_dropdown:
                                clear_dropdown_lines()
                                show_dropdown = False
                            
                            # Update input
                            current_input = f"/{selected_cmd}"
                            print(f"\r› {current_input}", end="", flush=True)
                            continue
                            
                    elif char == '\x1b':  # Escape sequences (arrows)
                        if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                            char2 = sys.stdin.read(1)
                            if char2 == '[':
                                if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                                    char3 = sys.stdin.read(1)
                                    if char3 == 'A' and show_dropdown:  # Up arrow
                                        # Clear current dropdown
                                        clear_dropdown_lines()
                                        
                                        selected_index = max(0, selected_index - 1)
                                        render_dropdown()
                                        continue
                                        
                                    elif char3 == 'B' and show_dropdown:  # Down arrow
                                        # Clear current dropdown
                                        clear_dropdown_lines()
                                        
                                        selected_index = min(len(filtered_commands) - 1, selected_index + 1)
                                        render_dropdown()
                                        continue
                        
                        # Regular ESC - hide dropdown
                        if show_dropdown:
                            clear_dropdown_lines()
                            show_dropdown = False
                            render_dropdown()
                            
                    elif char == '\x7f' or char == '\x08':  # Backspace
                        if current_input:
                            # Remove character
                            current_input = current_input[:-1]
                            print(f"\r› {current_input} \b", end="", flush=True)
                            
                            # Memory indicator and dropdown updates
                            if current_input.startswith('#'):
                                # Hide dropdown if it was visible
                                if show_dropdown:
                                    clear_dropdown_lines()
                                    show_dropdown = False
                                # Show memory indicator
                                show_memory_indicator()
                            elif current_input.startswith('/'):
                                query = current_input[1:] if len(current_input) > 1 else ""
                                filtered_commands = filter_commands(query)
                                show_dropdown = bool(filtered_commands)
                                selected_index = 0
                                render_dropdown()  # This will handle clearing if show_dropdown is False
                            else:
                                # Clear any indicators
                                clear_memory_indicator()
                                show_dropdown = False
                                render_dropdown()  # This will clear the dropdown
                                
                    elif char == '\x03':  # Ctrl+C
                        raise KeyboardInterrupt()
                        
                    elif char == '\x04':  # Ctrl+D
                        raise EOFError()
                        
                    elif char.isprintable():
                        # Add character
                        current_input += char
                        print(f"\r› {current_input}", end="", flush=True)
                        
                        # Memory indicator and dropdown for slash commands
                        if current_input.startswith('#'):
                            # Hide dropdown if switching modes
                            if show_dropdown:
                                clear_dropdown_lines()
                                show_dropdown = False
                            show_memory_indicator()
                        elif current_input == '/':
                            filtered_commands = filter_commands("")
                            show_dropdown = True
                            selected_index = 0
                            # Ensure memory indicator hidden
                            clear_memory_indicator()
                            render_dropdown()
                            
                        elif current_input.startswith('/') and len(current_input) > 1:
                            query = current_input[1:]
                            filtered_commands = filter_commands(query)
                            show_dropdown = bool(filtered_commands)
                            selected_index = 0
                            # Ensure memory indicator hidden
                            clear_memory_indicator()
                            render_dropdown()  # This will handle clearing if show_dropdown is False
                        else:
                            # Clear any indicators
                            clear_memory_indicator()
                            show_dropdown = False
                            render_dropdown()  # This will clear the dropdown
                            
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
            # Clear any remaining dropdown
            if show_dropdown:
                clear_dropdown_lines()
            # Clear memory indicator if still visible
            clear_memory_indicator()
            
            print()  # Ensure we end on a new line
        
        return current_input
    
    def start_timer(self, operation_name: str):
        """Start a timer for an operation"""
        self.operation_start_time = time.time()
        self.timer_stop = False
        
        def update_timer():
            """Update timer display in real-time"""
            while not self.timer_stop:
                if self.operation_start_time:
                    elapsed = time.time() - self.operation_start_time
                    # Update the status line with elapsed time
                    status_text = Text(
                        f"{operation_name} ({elapsed:.1f}s)",
                        style="bold cyan"
                    )
                    # Use carriage return to update the same line
                    self.console.print(
                        Panel(status_text, box=box.MINIMAL, expand=True),
                        end="\r"
                    )
                time.sleep(0.1)  # Update every 100ms
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=update_timer, daemon=True)
        self.timer_thread.start()
    
    def stop_timer(self) -> float:
        """Stop the timer and return elapsed time"""
        self.timer_stop = True
        if self.operation_start_time:
            elapsed = time.time() - self.operation_start_time
            self.operation_start_time = None
            return elapsed
        return 0.0
    
    def run(self):
        """Main chat loop with rich TUI"""
        # Track session start time
        session_start_time = time.time()
        
        # Clear screen and show ASCII logo
        self.console.clear()
        display_startup_logo(self.console)
        self.console.print()
        
        # Show welcome info after logo
        self.console.print(self.create_info_panel())
        self.console.print()
        
        # Show archer.md context status if loaded
        if self.archer_context:
            context_info = Panel(
                Text(f"✓ Loaded project context from archer.md ({len(self.archer_context)} characters)", style="dim green"),
                box=box.MINIMAL,
                style="dim",
                padding=(0, 1)
            )
            self.console.print(context_info)
            self.console.print()
        
        # Start persistent footer fixed at bottom (deferred until after first prompt)
        self.footer_live = None

        conversation = []
        
        if self.verbose:
            logging.info("Starting chat session with tools enabled")
        
        try:
            while True:
                # Check for terminal resize
                if self.check_terminal_resize():
                    # Optionally refresh the display on resize
                    if self.verbose:
                        logging.info(f"Terminal resized to width: {self.console.width}")
                    if self.footer_live:
                        self.footer_live.update(self.render_footer())

                # Show session time before getting input
                current_session_time = time.time() - session_start_time
                session_minutes, session_seconds = divmod(current_session_time, 60)
                session_time_str = f"{int(session_minutes):02d}:{int(session_seconds):02d}"

                # Get user input
                if self.footer_live:
                    self.footer_live.update(self.render_footer())
                user_input, ok = self.get_user_message()
                if not ok:
                    if self.verbose:
                        logging.info("User input ended, breaking from chat loop")
                    break
                
                # Start tracking agent active time
                agent_start_time = time.time()

                # Skip empty messages
                if user_input == "":
                    if self.verbose:
                        logging.info("Skipping empty message")
                    continue

                if self.verbose:
                    logging.info(f"User input received: {repr(user_input)}")
                
                # Check for exit commands
                if user_input.lower().strip() in ['exit', 'quit', 'bye', 'goodbye', '/exit', '/quit']:
                    if self.verbose:
                        logging.info("User requested exit")
                    break
                
                # Memory commands (e.g. # Use tailwind)
                if user_input.startswith('#'):
                    memory_content = user_input[1:].strip()  # Remove # and leading/trailing spaces
                    if memory_content:
                        # Add to archer.md memory
                        result = add_to_archer_memory(memory_content)
                        
                        # Show transient visual indicator
                        memory_panel = Panel(
                            Text(result, style="dim green" if result.startswith("✓") else "dim red"),
                            title="[bold]Memory[/bold]",
                            title_align="left",
                            border_style="cyan",
                            box=box.MINIMAL,
                            expand=True
                        )
                        
                        # Show indicator briefly, then remove it
                        with self.temporarily_stop_footer():
                            with Live(
                                memory_panel,
                                console=self.console,
                                transient=True,  # This makes it disappear after Live ends
                                refresh_per_second=1
                            ) as live:
                                time.sleep(1.5)  # Show for 1.5 seconds
                        
                        # Reload context for future messages
                        self.archer_context = load_archer_context()
                        if self.verbose:
                            logging.info(f"Reloaded archer.md context after memory addition")
                        
                        # Add updated context to current conversation immediately
                        if self.archer_context:
                            context_update_message = {
                                "role": "user",
                                "content": f"Updated project context from archer.md:\n\n{self.archer_context}"
                            }
                            conversation.append(context_update_message)
                            if self.verbose:
                                logging.info(f"Added updated context to current conversation ({len(self.archer_context)} chars)")
                    else:
                        self.console.print("[dim red]Error: Memory content cannot be empty[/dim red]")
                    continue
                
                # Slash commands (e.g. /init)
                if user_input.startswith('/'):
                    # Execute slash command
                    with self.temporarily_stop_footer():
                        command_result = try_run_command(self.console, user_input, agent=self, conversation=conversation)
                    
                    # Check if command wants conversation to be processed
                    if command_result == "PROCESS_CONVERSATION":
                        # The command added a message to conversation, now process it
                        # Skip adding user message again and go straight to agent inference
                        user_input = "COMMAND_PROCESSED"  # Special marker to skip user message addition
                    elif command_result == "CLEARED":
                        # The /clear command was executed, conversation was cleared
                        # Reset conversation history and continue
                        conversation = []
                        self.conversation_history = []
                        continue
                    else:
                        continue

                # Lazily start footer after first input to avoid echo during startup
                if self.footer_live is None:
                    self.footer_live = Live(
                        self.render_footer(),
                        console=self.console,
                        refresh_per_second=8,
                        transient=False,
                    )
                    self.footer_live.start()

                # Check if this is a complex task that needs planning
                if not self.planning_mode and self.should_create_plan(user_input):
                    # Show planning mode notification
                    planning_notice = Panel(
                        Text("Complex task detected. Entering planning mode...", style="bold cyan"),
                        title="[bold]Planning Mode[/bold]",
                        title_align="left",
                        border_style="cyan",
                        box=box.DOUBLE,
                        expand=True
                    )
                    self.console.print(planning_notice)

                    # Create planning prompt
                    plan_prompt = self.create_plan_prompt(user_input)

                    # Don't display user's message - they already typed it

                    # Add planning request to conversation
                    user_message = {"role": "user", "content": plan_prompt}
                    conversation.append(user_message)
                    self.planning_mode = True
                else:
                    # Don't display user message - they already typed it

                    # Add user message to conversation (unless it's already been added by a command)
                    if user_input != "COMMAND_PROCESSED":
                        user_message = {"role": "user", "content": user_input}
                        conversation.append(user_message)

                if self.verbose:
                    logging.info(f"Sending message to Archer, conversation length: {len(conversation)}")

                # Start timer and show status with real-time updates
                api_start_time = time.time()

                # Removed status panel display

                # Create a live display that updates every 0.1 seconds
                def _worker_main():
                    return self.run_inference(conversation)
                api_result, api_error, cancelled = self.run_with_cancellable_live(
                    "Archer is thinking...", _worker_main, style="bold cyan"
                )
                if cancelled:
                    self.console.print("[dim]Cancelled.[/dim]")
                    continue
                if api_error:
                    raise api_error
                message = api_result
                conversation.append(message)

                # Don't display summary here - it will be displayed after content is shown

                # Check if we're in planning mode and got a plan response
                if self.planning_mode:
                    # Check if there are any tool uses in the response
                    has_tool_use_in_plan = any(content['type'] == 'tool_use' for content in message['content'])

                    # If there are tool uses, we need to process them first
                    if has_tool_use_in_plan:
                        # Let the normal flow handle tool uses
                        self.planning_mode = False  # Exit planning mode but continue normally
                    else:
                        # Extract plan text from response
                        plan_text = ""
                        for content in message['content']:
                            if content['type'] == 'text':
                                plan_text = content['text']
                                break

                        if plan_text:
                            # Display the plan
                            self.display_plan(plan_text)

                            # Wait for user confirmation
                            confirm_input, ok = self.get_user_message()
                            if ok and confirm_input.lower().strip() in ['yes', 'y']:
                                # Exit planning mode and proceed with execution
                                self.planning_mode = False
                                execution_panel = Panel(
                                    Text("Plan approved. Beginning execution...", style="bold green"),
                                    title="Execution Mode",
                                    border_style="green",
                                    box=box.ROUNDED,
                                    expand=True
                                )
                                self.console.print(execution_panel)

                                # Automatically start execution
                                execution_message = {"role": "user", "content": "Great! Now please execute this plan step by step. Start with the first step."}
                                conversation.append(execution_message)

                                # Get Archer's response and continue processing
                                api_start_time = time.time()

                                # Show execution status
                                def _exec_worker():
                                    return self.run_inference(conversation)
                                api_result, api_error, cancelled = self.run_with_cancellable_live(
                                    "Executing plan...", _exec_worker, style="bold green"
                                )
                                if cancelled:
                                    self.console.print("[dim]Cancelled.[/dim]")
                                    continue
                                if api_error:
                                    raise api_error
                                message = api_result
                                conversation.append(message)
                                self.console.print(f"[bold green][x][/bold green] [green]Plan execution started[/green]")
                                self.console.print()
                            elif ok and confirm_input.lower().strip() == 'skip':
                                # Skip planning and proceed normally
                                self.planning_mode = False
                                skip_panel = Panel(
                                    Text("Planning skipped. Proceeding directly...", style="yellow"),
                                    title="Direct Execution",
                                    border_style="yellow",
                                    box=box.MINIMAL,
                                    expand=True
                                )
                                self.console.print(skip_panel)
                                continue  # Go back to main loop
                            elif ok and confirm_input.lower().strip() == 'modify':
                                # Allow modification of the plan
                                self.planning_mode = False  # Exit planning mode
                                modify_panel = Panel(
                                    Text("Please provide your modifications or a new approach:", style="cyan"),
                                    title="[bold]Plan Modification[/bold]",
                                    title_align="left",
                                    border_style="cyan",
                                    box=box.MINIMAL,
                                    expand=True
                                )
                                self.console.print(modify_panel)
                                continue  # Go back to get user input
                            else:
                                # Invalid response, ask again
                                invalid_panel = Panel(
                                    Text("Please respond with 'yes', 'modify', or 'skip'", style="red"),
                                    title="Invalid Response",
                                    border_style="red",
                                    box=box.MINIMAL,
                                    expand=True
                                )
                                self.console.print(invalid_panel)
                                # Display plan again and get new confirmation
                                self.display_plan(plan_text)
                                confirm_input, ok = self.get_user_message()
                                # Process the new input
                                if ok and confirm_input.lower().strip() in ['yes', 'y']:
                                    self.planning_mode = False
                                    execution_panel = Panel(
                                        Text("Plan approved. Beginning execution...", style="bold green"),
                                        title="Execution Mode",
                                        border_style="green",
                                        box=box.ROUNDED,
                                        expand=True
                                    )
                                    self.console.print(execution_panel)
                                    continue
                                elif ok and confirm_input.lower().strip() == 'skip':
                                    self.planning_mode = False
                                    continue
                                elif ok and confirm_input.lower().strip() == 'modify':
                                    self.planning_mode = False
                                    continue

                # Track if this is the first pass through the tool loop
                first_pass = True
                initial_elapsed = api_elapsed if 'api_elapsed' in locals() else 0

                # Keep processing until Archer stops using tools
                while True:
                    # Collect all tool uses and their results
                    tool_results = []
                    has_tool_use = False
                    has_text_in_response = False
                    pending_texts: list[str] = []

                    if self.verbose:
                        logging.info(f"Processing {len(message['content'])} content blocks from Archer")

                    for content in message['content']:
                        if content['type'] == 'text':
                            has_text_in_response = True
                            # Queue assistant text to display once per turn
                            if self.verbose:
                                logging.info(f"Queuing assistant text: {content['text'][:50]}...")
                            pending_texts.append(content['text'])
                        elif content['type'] == 'tool_use':
                            has_tool_use = True
                            tool_use = content

                            if self.verbose:
                                logging.info(f"Tool use detected: {tool_use['name']} with input: {tool_use['input']}")

                            # Display tool call
                            self.display_tool_call(tool_use['name'], str(tool_use['input']))

                            # Start timer for tool execution
                            tool_start_time = time.time()

                            # Show live timer for tool execution with command for bash
                            if tool_use['name'].lower() == 'bash' and 'command' in tool_use.get('input', {}):
                                command = tool_use['input']['command']
                                display_text = f"[bold green]•[/bold green] [dim]{command}[/dim] [dim](0.0s)[/dim]"
                            else:
                                display_text = f"[bold magenta]•[/bold magenta] [magenta]{tool_use['name']}[/magenta] [dim](0.0s)[/dim]"

                            # Add spacing above
                            self.console.print()

                            # Stop footer to avoid Live display conflicts
                            if self.footer_live:
                                try:
                                    self.footer_live.stop()
                                except Exception:
                                    pass
                                    
                            with Live(
                                display_text,
                                console=self.console,
                                refresh_per_second=10,
                                transient=True
                            ) as live:
                                # Find and execute the tool
                                tool_result = ""
                                tool_error = None
                                tool_found = False
                                tool_elapsed = 0

                                # Execute tool in a thread so we can update display
                                def execute_tool():
                                    nonlocal tool_result, tool_error, tool_found, tool_elapsed
                                    for tool in self.tools:
                                        if tool.name == tool_use['name']:
                                            if self.verbose:
                                                logging.info(f"Executing tool: {tool.name}")

                                            # Track tool call
                                            self.stats['tool_calls']['total'] += 1
                                            tool_name = tool_use['name']
                                            if tool_name not in self.stats['tool_calls']['by_tool']:
                                                self.stats['tool_calls']['by_tool'][tool_name] = {'success': 0, 'failed': 0, 'cancelled': 0}

                                            try:
                                                tool_start = time.time()
                                                tool_result = tool.function(tool_use['input'])
                                                tool_elapsed = time.time() - tool_start_time
                                                self.stats['performance']['tool_time'] += (time.time() - tool_start)
                                                self.stats['tool_calls']['successful'] += 1
                                                self.stats['tool_calls']['by_tool'][tool_name]['success'] += 1
                                                if self.verbose:
                                                    logging.info(f"Tool execution successful in {tool_elapsed:.2f}s, result length: {len(tool_result)} chars")
                                            except Exception as e:
                                                tool_error = str(e)
                                                tool_elapsed = time.time() - tool_start_time
                                                self.stats['tool_calls']['failed'] += 1
                                                self.stats['tool_calls']['by_tool'][tool_name]['failed'] += 1
                                                if self.verbose:
                                                    logging.error(f"Tool execution failed after {tool_elapsed:.2f}s: {e}")

                                            tool_found = True
                                            break

                                tool_thread = threading.Thread(target=execute_tool)
                                tool_thread.start()

                                # Update display while tool executes
                                self.processing = True
                                tool_cancelled = False
                                while tool_thread.is_alive():
                                    if self.check_for_esc_key():
                                        self.processing = False
                                        tool_cancelled = True
                                        if tool_use['name'] in self.stats['tool_calls']['by_tool']:
                                            self.stats['tool_calls']['by_tool'][tool_use['name']]['cancelled'] += 1
                                        self.stats['tool_calls']['cancelled'] += 1
                                        tool_thread.join(timeout=0.5)
                                        break
                                    elapsed = time.time() - tool_start_time
                                    if tool_use['name'].lower() == 'bash' and 'command' in tool_use.get('input', {}):
                                        command = tool_use['input']['command']
                                        live.update(f"[bold green]•[/bold green] [dim]{command}[/dim] [dim]({elapsed:.1f}s)[/dim]")
                                    else:
                                        live.update(f"[bold magenta]•[/bold magenta] [magenta]{tool_use['name']}[/magenta] [dim]({elapsed:.1f}s)[/dim]")
                                    time.sleep(0.1)
                                self.processing = False

                                # Show final result after updating live display
                                tool_elapsed = time.time() - tool_start_time

                                if tool_error:
                                    self.display_tool_result(tool_error, is_error=True, elapsed_time=tool_elapsed)
                                else:
                                    self.display_tool_result(tool_result, elapsed_time=tool_elapsed)

                                if not tool_found:
                                    tool_error = f"tool '{tool_use['name']}' not found"
                                    self.display_tool_result(tool_error, is_error=True)

                                # Status line is now handled by display_tool_result

                                # Add tool result to collection
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use['id'],
                                    "content": tool_error if tool_error else tool_result,
                                    "is_error": bool(tool_error)
                                })

                            # Restart footer after tool execution
                            if self.footer_live:
                                try:
                                    self.footer_live.start()
                                    self.footer_live.update(self.render_footer())
                                except Exception:
                                    pass

                    # If this is the first pass and there was no text, show a default message
                    if first_pass and has_tool_use and not has_text_in_response:
                        if self.verbose:
                            logging.info("No text in initial response, adding default message")
                        self.display_message("assistant", "Let me help you with that.")

                    # If there were no tool uses, display queued text once and finish
                    if not has_tool_use:
                        if pending_texts:
                            combined_text = "\n\n".join(
                                t for t in pending_texts if isinstance(t, str) and t.strip()
                            )
                            if combined_text.strip():
                                self.display_message("assistant", combined_text)
                        break

                    # Send all tool results back and get Archer's response
                    if self.verbose:
                        logging.info(f"Sending {len(tool_results)} tool results back to Archer")

                    tool_result_message = {"role": "user", "content": tool_results}
                    conversation.append(tool_result_message)

                    # Start timer for processing tool results
                    followup_start_time = time.time()

                    # Show live timer for processing tool results
                    def _followup_worker():
                        return self.run_inference(conversation)
                    followup_result, followup_error, cancelled = self.run_with_cancellable_live(
                        "Archer processing tool results...", _followup_worker, style="bold cyan"
                    )
                    followup_elapsed = 0  # We now show timing inside the live; keep summary simple
                    if cancelled:
                        self.console.print("[dim]Cancelled.[/dim]")
                        continue
                    if followup_error:
                        raise followup_error
                    message = followup_result
                    conversation.append(message)

                    # Display the assistant's response after processing tools (once)
                    text_blocks = [c['text'] for c in message['content'] if c['type'] == 'text' and c.get('text', '').strip()]
                    if text_blocks:
                        combined = "\n\n".join(text_blocks)
                        self.display_message("assistant", combined)
                    else:
                        if self.verbose:
                            logging.info("No text content in assistant response after tools")
                        self.display_message("assistant", "I've completed the requested operation.")

                    # Display processing summary with tokens
                    response_text = "".join(c.get('text', '') for c in message['content'] if c['type'] == 'text')
                    self.display_processing_summary(response_text, followup_elapsed)

                    if self.verbose:
                        logging.info(f"Received followup response with {len(message['content'])} content blocks")

                    # Mark that we're no longer on the first pass
                    first_pass = False

                # After exiting tool loop, display summary for the entire interaction
                if first_pass:
                    # No tools were used, display summary for initial response
                    response_text = "".join(c.get('text', '') for c in message['content'] if c['type'] == 'text')
                    self.display_processing_summary(response_text, initial_elapsed)
                
                # Track agent active time for this turn
                if 'agent_start_time' in locals():
                    self.stats['performance']['agent_active_time'] += time.time() - agent_start_time
        finally:
            # Stop footer before final goodbye message
            try:
                if self.footer_live:
                    self.footer_live.stop()
            except Exception:
                pass

        if self.verbose:
            logging.info("Chat session ended")
        
        # Calculate total session time
        session_duration = time.time() - session_start_time
        hours, remainder = divmod(session_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            duration_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            duration_str = f"{int(minutes)}m {int(seconds)}s"
        else:
            duration_str = f"{session_duration:.1f}s"
        
        # Display comprehensive stats on exit
        self.display_exit_stats(session_duration)
    
    def display_exit_stats(self, session_duration: float):
        """Display comprehensive exit statistics similar to the reference image"""
        # Calculate wall time
        hours, remainder = divmod(session_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            wall_time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            wall_time_str = f"{int(minutes)}m {int(seconds)}s"
        else:
            wall_time_str = f"{session_duration:.1f}s"
        
        # Calculate agent active time (API + tool time)
        agent_active_time = self.stats['performance']['api_time'] + self.stats['performance']['tool_time']
        
        # Calculate success rate
        total_tools = self.stats['tool_calls']['total']
        successful_tools = self.stats['tool_calls']['successful']
        success_rate = (successful_tools / total_tools * 100) if total_tools > 0 else 100.0
        
        # Format API and tool time percentages
        api_percent = (self.stats['performance']['api_time'] / agent_active_time * 100) if agent_active_time > 0 else 0
        tool_percent = (self.stats['performance']['tool_time'] / agent_active_time * 100) if agent_active_time > 0 else 0
        
        # Format times
        def format_time(seconds):
            if seconds < 1:
                return f"{int(seconds * 1000)}ms"
            elif seconds < 60:
                return f"{seconds:.1f}s"
            else:
                m, s = divmod(seconds, 60)
                return f"{int(m)}m {int(s)}s"
        
        # Create the exit display
        console_output = []
        
        # Header
        console_output.append(Text("Agent powering down. Goodbye!", style="bold blue"))
        console_output.append(Text(""))
        
        # Interaction Summary
        console_output.append(Text("Interaction Summary", style="bold yellow"))
        
        # Tool calls with checkmarks and X marks
        tool_display = f"{total_tools} ( "
        if successful_tools > 0:
            tool_display += f"✓ {successful_tools} "
        if self.stats['tool_calls']['failed'] > 0:
            tool_display += f"✗ {self.stats['tool_calls']['failed']} "
        if self.stats['tool_calls']['cancelled'] > 0:
            tool_display += f"◯ {self.stats['tool_calls']['cancelled']} "
        tool_display += ")"
        
        console_output.append(Text(f"Tool Calls:          {tool_display}"))
        console_output.append(Text(f"Success Rate:        {success_rate:.1f}%", style="green" if success_rate >= 90 else "yellow"))
        console_output.append(Text(""))
        
        # Performance
        console_output.append(Text("Performance", style="bold yellow"))
        console_output.append(Text(f"Wall Time:           {wall_time_str}"))
        console_output.append(Text(f"Agent Active:        {format_time(agent_active_time)}"))
        console_output.append(Text(f"  » API Time:        {format_time(self.stats['performance']['api_time'])} ({api_percent:.1f}%)", style="dim"))
        console_output.append(Text(f"  » Tool Time:       {format_time(self.stats['performance']['tool_time'])} ({tool_percent:.1f}%)", style="dim"))
        console_output.append(Text(""))
        
        # Model Usage table
        console_output.append(Text("Model Usage", style="bold yellow"))
        
        # Create a simple text table for model usage
        model_line = Text("")
        model_line.append("─" * 60, style="dim")
        console_output.append(model_line)
        
        # Table header
        header_text = Text()
        header_text.append("Model                ", style="bold")
        header_text.append("Reqs   ", style="bold")
        header_text.append("Input Tokens  ", style="bold")
        header_text.append("Output Tokens", style="bold")
        console_output.append(header_text)
        
        separator = Text("")
        separator.append("─" * 60, style="dim")
        console_output.append(separator)
        
        # Model row
        model_row = Text()
        model_row.append("claude-sonnet-4      ")
        model_row.append(f"{self.stats['model_usage']['requests']:>4}   ")
        model_row.append(f"{self.stats['model_usage']['input_tokens']:>12,}  ")
        model_row.append(f"{self.stats['model_usage']['output_tokens']:>12,}")
        console_output.append(model_row)
        console_output.append(Text(""))
        
        # Savings highlight if there are cached tokens
        if self.stats['model_usage']['cached_tokens'] > 0:
            cache_percent = (self.stats['model_usage']['cached_tokens'] / self.stats['model_usage']['input_tokens'] * 100) if self.stats['model_usage']['input_tokens'] > 0 else 0
            console_output.append(Text(f"Savings Highlight: {self.stats['model_usage']['cached_tokens']:,} ({cache_percent:.1f}%) of input tokens were served from the cache, reducing costs.", style="green"))
            console_output.append(Text(""))
        
        
        # Print everything in a panel
        self.console.print(Panel(
            Group(*console_output),
            border_style="dim",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
    
    def run_inference(self, conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run inference with Archer API with timing"""
        if CANCEL_EVENT.is_set():
            raise OperationAborted()
        
        # Prepare conversation with system preferences and archer.md context
        enhanced_conversation = conversation.copy()
        
        # Add CLI preferences system prompt (Anthropic expects top-level `system`)
        cli_preferences_prompt = """
🔧 CLI Preference Section for AI Coder System Prompt

CLI Preference Directive
Always prefer well-known CLI (bash) commands over MCP servers or remote API abstractions.
Generate copy-pasteable CLI commands (with minimal assumptions about environment) before falling back to MCP servers.
Use MCP servers only if the task is impossible or impractical via CLI.

Preferred CLI Tools
    •    Source Control & GitHub
    •    git → for repository operations (clone, branch, commit, push).
    •    gh → for GitHub issues, pull requests, workflows, repo settings.
    •    Containers & Kubernetes
    •    docker → build, run, push container images.
    •    kubectl → manage Kubernetes clusters (deployments, logs, services).
    •    helm → deploy/manage Kubernetes apps.
    •    Cloud Providers
    •    az → Azure CLI (VMs, storage, container apps, resource groups).
    •    aws → AWS CLI (S3, EC2, IAM, Lambda, CloudFormation).
    •    gcloud → Google Cloud CLI (Compute Engine, Cloud Run, GKE).
    •    Hosting & Deployment
    •    vercel → deploy/manage Vercel projects from CLI.
    •    netlify → deploy/manage Netlify sites from CLI.
    •    npm / yarn → install, run, publish Node.js apps.
    •    pip / poetry → Python package/dependency management.
    •    Infrastructure as Code
    •    terraform → infra provisioning (plan, apply, destroy).
    •    ansible → config management & automation.
    •    Networking & API Testing
    •    curl → make HTTP requests (API testing).
    •    httpie → human-friendly alternative to curl.
    •    jq → parse/transform JSON.
    •    Remote Access & Ops
    •    ssh → secure remote login.
    •    scp / rsync → file transfer.
    •    htop / top → process monitoring.
    •    Databases
    •    psql → PostgreSQL CLI.
    •    mysql → MySQL CLI.
    •    mongosh → MongoDB shell.
    •    Automation
    •    make → task runner via Makefiles.
    •    cron → scheduling tasks.

⸻

Instruction to Model
    •    Default to bash snippets using these CLIs.
    •    Prefer commands that are direct, standard, and cross-platform friendly.
    •    For multi-step tasks, return scripts or pipelines (|, &&, ;).
    •    Explain assumptions briefly (e.g., "requires Vercel CLI installed: npm i -g vercel").
        """
        system_text = cli_preferences_prompt.strip()
        
        if len(conversation) == 1:
            # First user message: include archer.md context if present
            if self.archer_context:
                context_message = {
                    "role": "user",
                    "content": (
                        f"Project context from archer.md:\n\n{self.archer_context}\n\n---\n\n"
                        f"User request: {conversation[0]['content']}"
                    ),
                }
                enhanced_conversation = [context_message]
                if self.verbose:
                    logging.info(
                        f"Added CLI preferences system prompt (top-level) and archer.md context ({len(self.archer_context)} chars)"
                    )
            else:
                enhanced_conversation = conversation
                if self.verbose:
                    logging.info("Added CLI preferences system prompt (top-level)")
        else:
            # Subsequent messages; continue with existing conversation
            if self.verbose:
                logging.info("Continuing conversation with existing system prompt (top-level)")
        
        # Convert tools to Anthropic format
        anthropic_tools = []
        for tool in self.tools:
            anthropic_tools.append({
                "type": "custom",
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })
        
        if self.verbose:
            logging.info(f"Making API call to Archer with model: claude-sonnet-4-20250514 and {len(anthropic_tools)} tools")
        
        # Suppress HTTP logging from the Anthropic library
        import logging as log
        log.getLogger("httpx").setLevel(log.ERROR)
        log.getLogger("anthropic").setLevel(log.ERROR)
        log.getLogger("httpcore").setLevel(log.ERROR)
        
        try:
            # Time the API call
            api_start = time.time()
            # Check if we need to summarize before making the call
            if self.token_manager.should_summarize():
                self.console.print("[yellow]⚠️ Approaching context limit, summarizing conversation...[/yellow]")
                summary_request = ConversationSummarizer.create_summary_request(enhanced_conversation)
                summary_response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    system=system_text,
                    max_tokens=2000,
                    messages=[summary_request]
                )
                summary_text = ""
                for content in summary_response.content:
                    if content.type == "text":
                        summary_text = content.text
                        break
                
                # Compress the conversation
                enhanced_conversation = ConversationSummarizer.compress_conversation(
                    enhanced_conversation, summary_text
                )
                self.console.print("[green]✓ Conversation summarized to preserve context[/green]")
            
            # Use dynamic max tokens based on model limits
            max_output = min(self.token_manager.limits.output, 8192)
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_text,
                max_tokens=max_output,
                messages=enhanced_conversation,
                tools=anthropic_tools
            )
            api_time = time.time() - api_start
            
            # Track API stats
            self.stats['performance']['api_time'] += api_time
            self.stats['model_usage']['requests'] += 1
            
            # Track token usage if available
            if hasattr(response, 'usage'):
                input_tokens = getattr(response.usage, 'input_tokens', 0)
                output_tokens = getattr(response.usage, 'output_tokens', 0)
                cached_tokens = getattr(response.usage, 'cache_creation_input_tokens', 0) + getattr(response.usage, 'cache_read_input_tokens', 0)
                
                self.stats['model_usage']['input_tokens'] += input_tokens
                self.stats['model_usage']['output_tokens'] += output_tokens
                if cached_tokens > 0:
                    self.stats['model_usage']['cached_tokens'] += cached_tokens
                
                # Track in token manager
                usage = TokenUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cached_tokens=cached_tokens
                )
                self.token_manager.add_usage(usage)
                
                # Display token usage info
                token_display = self.token_manager.format_usage_display(usage)
                if token_display:
                    self.console.print(f"[dim]{token_display}[/dim]")
            
            if self.verbose:
                logging.info(f"API call successful in {api_time:.2f}s, response received")
            
            # Convert response to our format
            message = {
                "role": "assistant",
                "content": []
            }
            
            for content in response.content:
                if content.type == "text":
                    message["content"].append({
                        "type": "text",
                        "text": content.text
                    })
                elif content.type == "tool_use":
                    message["content"].append({
                        "type": "tool_use",
                        "id": content.id,
                        "name": content.name,
                        "input": content.input
                    })
            
            return message
            
        except Exception as e:
            if self.verbose:
                logging.error(f"API call failed: {e}")
            raise


@dataclass
class ToolDefinition:  # kept for backward-compat; real one imported above
    name: str
    description: str
    input_schema: Dict[str, Any]
    function: Callable[[Dict[str, Any]], str]


## Tool definitions are now provided by the registry (build_tools). Keeping
## these names available for compatibility with existing helpers/tests:
ReadFileDefinition, ListFilesDefinition, BashDefinition, CodeSearchDefinition, \
EditFileDefinition, WriteFileDefinition, WebFetchDefinition, \
TodoWriteDefinition, TodoReadDefinition = build_tools()


if __name__ == "__main__":
    main()
