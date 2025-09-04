#!/usr/bin/env python3
"""
Filesystem-related Archer tools: read_file, list_files, edit_file, write_file
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any

from ..utils.token_manager import FILE_LIMITS
from ..utils.ignore_manager import get_ignore_manager, should_ignore_path


def read_file(input_data: Dict[str, Any]) -> str:
    """Read file with line limits and ignore safety."""
    path = input_data.get('path', '')
    offset = input_data.get('offset', 0)
    limit = input_data.get('limit', FILE_LIMITS['read'])

    if should_ignore_path(path):
        logging.warning(f"Attempted to read ignored file: {path}")
        return (
            f"Error: File '{path}' is in an ignored directory or matches ignore patterns. "
            f"Check .gitignore and .archerignore files."
        )

    logging.info(f"Reading file: {path} (offset={offset}, limit={limit})")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines = len(lines)

            start = offset
            end = min(start + limit, total_lines)
            content_lines = lines[start:end]
            content = ''.join(content_lines)

            if end < total_lines or start > 0:
                header = f"[Reading lines {start+1}-{end} of {total_lines} total]\n"
                content = header + content
                if end < total_lines:
                    content += f"\n[Truncated. {total_lines - end} more lines available]"

        logging.info(
            f"Successfully read file {path} ({len(content)} bytes, {end-start} lines)"
        )
        return content
    except Exception as e:
        logging.error(f"Failed to read file {path}: {e}")
        raise


def list_files(input_data: Dict[str, Any]) -> str:
    """List files/directories with ignore patterns applied."""
    path = input_data.get('path', '.')

    logging.info(f"Listing files in directory: {path}")
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return json.dumps({"error": f"Directory '{path}' does not exist"})
        if not dir_path.is_dir():
            return json.dumps({"error": f"'{path}' is not a directory"})

        files: list[str] = []
        count = 0
        max_files = FILE_LIMITS['ls']
        ignore_mgr = get_ignore_manager()
        ignored_count = 0

        for item in dir_path.iterdir():
            try:
                if item.is_absolute():
                    rel_path = str(item.relative_to(Path.cwd()))
                else:
                    rel_path = str(item)
            except ValueError:
                rel_path = item.name

            if ignore_mgr.should_ignore(rel_path):
                ignored_count += 1
                continue

            if count >= max_files:
                remaining = sum(1 for _ in dir_path.iterdir()) - count - ignored_count
                if remaining > 0:
                    files.append(
                        f"[... {remaining} more items not shown. Use more specific path.]"
                    )
                break

            files.append(f"{item.name}/" if item.is_dir() else item.name)
            count += 1

        if ignored_count > 0:
            files.append(f"[{ignored_count} items hidden by .gitignore/.archerignore]")

        files.sort()
        logging.info(f"Successfully listed {len(files)} items in {path}")
        return json.dumps(files)

    except Exception as e:
        logging.error(f"Failed to list files in {path}: {e}")
        raise


def edit_file(input_data: Dict[str, Any]) -> str:
    """Replace or append content in a text file with ignore safety."""
    path = input_data.get('path', '')
    old_str = input_data.get('old_str', '')
    new_str = input_data.get('new_str', '')

    if not path or old_str == new_str:
        logging.error("EditFile failed: invalid input parameters")
        return "Error: invalid input parameters"

    if should_ignore_path(path):
        logging.warning(f"Attempted to edit ignored file: {path}")
        return (
            f"Error: File '{path}' is in an ignored directory or matches ignore patterns. "
            f"Check .gitignore and .archerignore files."
        )

    logging.info(
        f"Editing file: {path} (replacing {len(old_str)} chars with {len(new_str)} chars)"
    )

    try:
        file_path = Path(path)

        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            old_content = content

            if old_str == "":
                new_content = old_content + new_str
            else:
                count = old_content.count(old_str)
                if count == 0:
                    logging.error(
                        f"EditFile failed: old_str not found in file {path}"
                    )
                    return "Error: old_str not found in file"
                if count > 1:
                    logging.error(
                        f"EditFile failed: old_str found {count} times in file {path}, must be unique"
                    )
                    return f"Error: old_str found {count} times in file, must be unique"

                new_content = old_content.replace(old_str, new_str, 1)
        else:
            if old_str == "":
                new_content = new_str
            else:
                logging.error(
                    f"EditFile failed: cannot replace text in non-existent file {path}"
                )
                return "Error: cannot replace text in non-existent file"

            file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(new_content, encoding='utf-8')

        logging.info(f"Successfully edited file {path}")
        return "OK"

    except Exception as e:
        error_msg = f"Failed to edit file {path}: {str(e)}"
        logging.error(error_msg)
        return error_msg


def write_file(input_data: Dict[str, Any]) -> str:
    """Create or append to a file with provided content, respecting ignore patterns.

    Accepted inputs (robust):
      - path | file | filepath | filename: destination file path
      - content | text | data | body: full text content to write
      - append (optional bool): if true, append instead of overwrite
      - input_data nesting is also accepted, e.g.: {"input_data": {"path": ..., "content": ...}}
    """
    # Accept nested payloads produced by some models
    if 'input_data' in input_data and isinstance(input_data['input_data'], dict):
        input_data = input_data['input_data']

    path = (
        input_data.get('path')
        or input_data.get('file')
        or input_data.get('filepath')
        or input_data.get('filename')
        or ''
    )
    content = (
        input_data.get('content')
        or input_data.get('text')
        or input_data.get('data')
        or input_data.get('body')
    )
    append = bool(input_data.get('append', False) or (input_data.get('mode') == 'append'))

    if not path:
        logging.error("WriteFile failed: path is required")
        return "Error: path is required"

    if should_ignore_path(path):
        logging.warning(f"Attempted to write to ignored file: {path}")
        return (
            f"Error: File '{path}' is in an ignored directory or matches ignore patterns. "
            f"Check .gitignore and .archerignore files."
        )

    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        text_content = "" if content is None else str(content)

        if append and file_path.exists():
            existing = file_path.read_text(encoding='utf-8')
            file_path.write_text(existing + text_content, encoding='utf-8')
            action = 'appended'
        else:
            file_path.write_text(text_content, encoding='utf-8')
            action = 'wrote'

        logging.info(f"Successfully {action} file {file_path} ({len(text_content)} bytes)")
        return f"OK: {action} {file_path} ({len(text_content)} bytes)"
    except Exception as e:
        error_msg = f"Failed to write file {path}: {str(e)}"
        logging.error(error_msg)
        return error_msg
