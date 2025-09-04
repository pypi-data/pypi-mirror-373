#!/usr/bin/env python3
"""
Todo management tools for Archer.
Provides TodoWrite and TodoRead functionality for task tracking during sessions.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

# Global state to store todos per session
_todo_state: Dict[str, List[Dict[str, Any]]] = {}


@dataclass
class TodoItem:
    """Represents a single todo item."""
    content: str
    status: str  # pending, in_progress, completed, cancelled
    priority: str = "medium"  # high, medium, low
    id: str = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        """Initialize id and timestamps if not provided."""
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoItem':
        """Create TodoItem from dictionary."""
        return cls(**data)


def validate_todo_item(todo: Dict[str, Any]) -> bool:
    """Validate a todo item has required fields."""
    required_fields = ['content', 'status']
    if not all(field in todo for field in required_fields):
        return False
    
    # Validate status
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if todo['status'] not in valid_statuses:
        return False
    
    # Validate priority if present
    if 'priority' in todo:
        valid_priorities = ['high', 'medium', 'low']
        if todo['priority'] not in valid_priorities:
            return False
    
    return True


def format_todo_list(todos: List[Dict[str, Any]]) -> str:
    """Format todo list for display."""
    if not todos:
        return "No todos in the list."
    
    output = []
    
    # Group by status
    status_groups = {
        'in_progress': [],
        'pending': [],
        'completed': [],
        'cancelled': []
    }
    
    for todo in todos:
        status = todo.get('status', 'pending')
        if status in status_groups:
            status_groups[status].append(todo)
    
    # Format in_progress tasks
    if status_groups['in_progress']:
        output.append("🔄 IN PROGRESS:")
        for todo in status_groups['in_progress']:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(todo.get('priority', 'medium'), '⚪')
            output.append(f"  {priority_emoji} [{todo.get('id', 'N/A')}] {todo.get('content', 'No description')}")
    
    # Format pending tasks
    if status_groups['pending']:
        output.append("\n⏳ PENDING:")
        for todo in status_groups['pending']:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(todo.get('priority', 'medium'), '⚪')
            output.append(f"  {priority_emoji} [{todo.get('id', 'N/A')}] {todo.get('content', 'No description')}")
    
    # Format completed tasks
    if status_groups['completed']:
        output.append("\n✅ COMPLETED:")
        for todo in status_groups['completed']:
            output.append(f"  ✓ [{todo.get('id', 'N/A')}] {todo.get('content', 'No description')}")
    
    # Format cancelled tasks
    if status_groups['cancelled']:
        output.append("\n❌ CANCELLED:")
        for todo in status_groups['cancelled']:
            output.append(f"  ✗ [{todo.get('id', 'N/A')}] {todo.get('content', 'No description')}")
    
    # Add summary
    active_count = len(status_groups['in_progress']) + len(status_groups['pending'])
    total_count = len(todos)
    completed_count = len(status_groups['completed'])
    
    output.append(f"\n📊 Summary: {active_count} active, {completed_count} completed, {total_count} total")
    
    return '\n'.join(output)


def todo_write(input_data: Dict[str, Any]) -> str:
    """
    Write/update the todo list for the current session.
    
    Args:
        input_data: Dictionary containing:
            - todos: List of todo items, each with:
                - content: Brief description of the task
                - status: Current status (pending, in_progress, completed, cancelled)
                - priority: Optional priority (high, medium, low)
                - id: Optional unique identifier
            - session_id: Optional session identifier
    
    Returns:
        Formatted todo list or error message
    """
    todos_data = input_data.get('todos', [])
    session_id = input_data.get('session_id', 'default')
    
    if not isinstance(todos_data, list):
        return "Error: 'todos' must be a list"
    
    # Validate and process todos
    processed_todos = []
    for todo_dict in todos_data:
        if not validate_todo_item(todo_dict):
            return f"Error: Invalid todo item: {json.dumps(todo_dict)}"
        
        # Create TodoItem to ensure proper structure
        todo = TodoItem(
            content=todo_dict.get('content'),
            status=todo_dict.get('status'),
            priority=todo_dict.get('priority', 'medium'),
            id=todo_dict.get('id'),
            created_at=todo_dict.get('created_at'),
            updated_at=datetime.now().isoformat()
        )
        processed_todos.append(todo.to_dict())
    
    # Check for multiple in_progress tasks
    in_progress_count = sum(1 for todo in processed_todos if todo['status'] == 'in_progress')
    if in_progress_count > 1:
        logging.warning(f"Warning: {in_progress_count} tasks marked as in_progress (should be 1)")
    
    # Store in global state
    _todo_state[session_id] = processed_todos
    
    logging.info(f"TodoWrite: Updated {len(processed_todos)} todos for session {session_id}")
    
    # Return formatted output
    return format_todo_list(processed_todos)


def todo_read(input_data: Dict[str, Any]) -> str:
    """
    Read the current todo list for the session.
    
    Args:
        input_data: Dictionary containing:
            - session_id: Optional session identifier
            - format: Optional format (json or text, default: text)
    
    Returns:
        Current todo list in requested format
    """
    session_id = input_data.get('session_id', 'default')
    output_format = input_data.get('format', 'text')
    
    # Get todos for session
    todos = _todo_state.get(session_id, [])
    
    logging.info(f"TodoRead: Reading {len(todos)} todos for session {session_id}")
    
    if output_format == 'json':
        return json.dumps(todos, indent=2)
    else:
        return format_todo_list(todos)


def todo_clear(input_data: Dict[str, Any]) -> str:
    """
    Clear all todos for the session.
    
    Args:
        input_data: Dictionary containing:
            - session_id: Optional session identifier
    
    Returns:
        Confirmation message
    """
    session_id = input_data.get('session_id', 'default')
    
    if session_id in _todo_state:
        todo_count = len(_todo_state[session_id])
        del _todo_state[session_id]
        logging.info(f"TodoClear: Cleared {todo_count} todos for session {session_id}")
        return f"Cleared {todo_count} todos from the list."
    else:
        return "No todos to clear."


def todo_update_status(input_data: Dict[str, Any]) -> str:
    """
    Update the status of a specific todo item.
    
    Args:
        input_data: Dictionary containing:
            - id: Todo item ID
            - status: New status
            - session_id: Optional session identifier
    
    Returns:
        Updated todo list or error message
    """
    todo_id = input_data.get('id')
    new_status = input_data.get('status')
    session_id = input_data.get('session_id', 'default')
    
    if not todo_id or not new_status:
        return "Error: Both 'id' and 'status' are required"
    
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        return f"Error: Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}"
    
    todos = _todo_state.get(session_id, [])
    
    # Find and update the todo
    found = False
    for todo in todos:
        if todo.get('id') == todo_id:
            todo['status'] = new_status
            todo['updated_at'] = datetime.now().isoformat()
            found = True
            break
    
    if not found:
        return f"Error: Todo with id '{todo_id}' not found"
    
    # Check for multiple in_progress tasks
    if new_status == 'in_progress':
        in_progress_count = sum(1 for todo in todos if todo['status'] == 'in_progress')
        if in_progress_count > 1:
            logging.warning(f"Warning: {in_progress_count} tasks now marked as in_progress")
    
    _todo_state[session_id] = todos
    logging.info(f"TodoUpdate: Updated todo {todo_id} to status '{new_status}'")
    
    return format_todo_list(todos)