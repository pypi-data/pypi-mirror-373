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

# Import Rich components
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

# Global cancellation event for long operations (API calls, subprocesses)
CANCEL_EVENT = Event()

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
    
    # Initialize Rich console
    console = Console(width=None, legacy_windows=False)
    
    # Initialize Anthropic client
    import httpx
    client = anthropic.Anthropic(
        http_client=httpx.Client(
            event_hooks={'request': [], 'response': []}
        )
    )
    
    # Simplified agent with just basic functionality
    console.clear()
    console.print(Panel(
        Text("Welcome to Archer CLI!", style="bold cyan"),
        title="[bold]Archer[/bold]",
        title_align="left",
        border_style="cyan",
        box=box.ROUNDED,
        expand=True
    ))
    console.print()
    console.print("[bold green]Chat with Archer AI[/bold green]")
    console.print("[dim]Type 'exit' to quit[/dim]")
    console.print()
    
    try:
        while True:
            try:
                user_input = input("› ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                # Basic echo for now - you would integrate the full agent here
                console.print(f"[cyan]You said:[/cyan] {user_input}")
                console.print()
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
                
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    
    console.print("\n[bold blue]Goodbye![/bold blue]")

if __name__ == "__main__":
    main()