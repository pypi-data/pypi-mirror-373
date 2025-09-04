from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

# Import implementations from current locations (we'll move later)
from tools.fs import read_file, list_files, edit_file, write_file
from tools.exec import bash
from tools.search import code_search
from tools.webfetch import webfetch
from tools.todo import todo_write, todo_read


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    function: Callable[[Dict[str, Any]], str]


def build_tools() -> List[ToolDefinition]:
    return [
        ToolDefinition(
            name="read_file",
            description="Read the contents of a given relative file path. Use this when you want to see what's inside a file. Do not use this with directory names.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The relative path of a file in the working directory."}
                },
                "required": ["path"],
            },
            function=read_file,
        ),
        ToolDefinition(
            name="list_files",
            description="List files and directories at a given path. If no path is provided, lists files in the current directory.",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Optional relative path to list files from. Defaults to current directory if not provided."}},
            },
            function=list_files,
        ),
        ToolDefinition(
            name="bash",
            description="Execute a bash command and return its output. Use this to run shell commands.",
            input_schema={
                "type": "object",
                "properties": {"command": {"type": "string", "description": "The bash command to execute."}},
                "required": ["command"],
            },
            function=bash,
        ),
        ToolDefinition(
            name="code_search",
            description="Search for code patterns using ripgrep (rg). Use this to find code patterns, function definitions, variable usage, or any text in the codebase. You can search by pattern, file type, or directory.",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "The search pattern or regex to look for"},
                    "path": {"type": "string", "description": "Optional path to search in (file or directory)"},
                    "file_type": {"type": "string", "description": "Optional file extension to limit search to (e.g., 'go', 'js', 'py')"},
                    "case_sensitive": {"type": "boolean", "description": "Whether the search should be case sensitive (default: false)"},
                },
                "required": ["pattern"],
            },
            function=code_search,
        ),
        ToolDefinition(
            name="edit_file",
            description="Make edits to a text file. Replaces 'old_str' with 'new_str' in the given file. 'old_str' and 'new_str' MUST be different from each other. If the file specified with path doesn't exist, it will be created.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The path to the file"},
                    "old_str": {"type": "string", "description": "Text to search for - must match exactly and must only have one match exactly"},
                    "new_str": {"type": "string", "description": "Text to replace old_str with"},
                },
                "required": ["path", "old_str", "new_str"],
            },
            function=edit_file,
        ),
        ToolDefinition(
            name="write_file",
            description=(
                "Create or append to a file. Required: path. Content optional (creates empty file if omitted). "
                "Accepts synonyms (file/filepath/filename, content/text/data/body) and nested {input_data:{...}}. "
                "Set append=true to append instead of overwrite. Use 'edit_file' for single replacements."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "file": {"type": "string"},
                    "filepath": {"type": "string"},
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                    "text": {"type": "string"},
                    "data": {"type": "string"},
                    "body": {"type": "string"},
                    "append": {"type": "boolean"},
                    "mode": {"type": "string", "enum": ["append", "write"]},
                    "input_data": {"type": "object"},
                },
                "required": [],
            },
            function=write_file,
        ),
        ToolDefinition(
            name="webfetch",
            description=(
                "Fetches content from a specified URL and returns it in the specified format. "
                "Supports text extraction, HTML to Markdown conversion, or raw HTML. "
                "Includes a 15-minute cache for faster repeated access to the same URLs."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to fetch content from (must start with http:// or https://)"},
                    "format": {"type": "string", "enum": ["text", "markdown", "html"], "description": "The format to return the content in (text, markdown, or html). Default: markdown"},
                    "timeout": {"type": "number", "description": "Optional timeout in seconds (max 120). Default: 30"},
                },
                "required": ["url"],
            },
            function=webfetch,
        ),
        ToolDefinition(
            name="todo_write",
            description=(
                "Create and manage a structured task list for the current coding session. "
                "Use this to track progress on complex multi-step tasks, organize work, and show thoroughness. "
                "Each todo item must have: content (task description) and status (pending/in_progress/completed/cancelled). "
                "Optional: priority (high/medium/low) and id (unique identifier)."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "description": "The updated todo list",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string", "description": "Brief description of the task"},
                                "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "cancelled"], "description": "Current status of the task"},
                                "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "Priority level of the task (default: medium)"},
                                "id": {"type": "string", "description": "Unique identifier for the todo item"},
                            },
                            "required": ["content", "status"],
                        },
                    },
                    "session_id": {"type": "string", "description": "Optional session identifier (default: 'default')"},
                },
                "required": ["todos"],
            },
            function=todo_write,
        ),
        ToolDefinition(
            name="todo_read",
            description=(
                "Read the current todo list for the session. "
                "Returns all todos with their status, priority, and IDs. "
                "Use this to check what tasks are pending, in progress, or completed."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Optional session identifier (default: 'default')"},
                    "format": {"type": "string", "enum": ["text", "json"], "description": "Output format (default: text)"},
                },
            },
            function=todo_read,
        ),
    ]
