#!/usr/bin/env python3
"""
Search-related Archer tools: code_search (rg with safe Python fallback)
"""
from __future__ import annotations

import logging
import subprocess
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, Any

from ..utils.ignore_manager import get_ignore_manager

# Reasonable cap for Python fallback results
_PY_FALLBACK_MAX_RESULTS = 500


def code_search(input_data: Dict[str, Any]) -> str:
    """Search for code/text patterns using ripgrep (rg) or Python fallback."""
    pattern = input_data.get('pattern', '')
    path = input_data.get('path', '.')
    file_type = input_data.get('file_type', '')
    case_sensitive = input_data.get('case_sensitive', False)

    if not pattern:
        logging.error("CodeSearch failed: pattern is required")
        return "Error: pattern is required"

    logging.info(f"Searching for pattern: {pattern}")

    args = ['rg', '--line-number', '--with-filename', '--color=never']

    archerignore_path = Path.cwd() / '.archerignore'
    if archerignore_path.exists():
        args.extend(['--ignore-file', str(archerignore_path)])

    if not case_sensitive:
        args.append('--ignore-case')

    if file_type:
        args.extend(['--type', file_type])

    args.append(pattern)

    if path:
        args.append(path)
    else:
        args.append('.')

    if shutil.which('rg'):
        logging.debug(f"Executing ripgrep with args: {args}")
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 1:
                logging.info(f"No matches found for pattern: {pattern}")
                return "No matches found"
            elif result.returncode != 0:
                logging.error(
                    f"Ripgrep command failed with exit code {result.returncode}"
                )
                return f"Search failed with exit code {result.returncode}"
            output = result.stdout.strip()
            lines = output.split('\n') if output else []
            logging.info(f"Found {len(lines)} matches for pattern: {pattern}")
            if len(lines) > 50:
                output = '\n'.join(lines[:50]) + f"\n... (showing first 50 of {len(lines)} matches)"
            return output
        except subprocess.TimeoutExpired:
            error_msg = f"Search timed out after 60 seconds for pattern: {pattern}"
            logging.error(error_msg)
            return error_msg
        except Exception as e:
            logging.warning(f"rg failed ('{e}'); falling back to Python search")

    # Python fallback
    try:
        ignore_mgr = get_ignore_manager()
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            regex = re.compile(pattern, flags)
        except re.error as re_err:
            return f"Invalid regex: {re_err}"

        start_dir = path or '.'
        matches: list[str] = []
        wanted_ext = ('.' + file_type.lower()) if file_type else None
        skip_dirs = {'.git', '.devenv', 'node_modules', 'dist', 'build', '__pycache__', '.venv', 'venv'}

        if os.path.isfile(start_dir):
            files_to_scan = [start_dir]
        else:
            files_to_scan = []
            for dirpath, dirnames, filenames in os.walk(start_dir):
                dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith('.')]
                for fn in filenames:
                    if fn.startswith('.'):
                        continue
                    if wanted_ext and not fn.lower().endswith(wanted_ext):
                        continue
                    files_to_scan.append(os.path.join(dirpath, fn))

        for file_path in files_to_scan:
            if ignore_mgr.should_ignore(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as fh:
                    for line_num, line in enumerate(fh, start=1):
                        if regex.search(line):
                            line_clean = line.rstrip('\n')
                            matches.append(f"{file_path}:{line_num}:{line_clean}")
                            if len(matches) >= _PY_FALLBACK_MAX_RESULTS:
                                break
            except Exception:
                continue

        if not matches:
            logging.info(
                f"No matches found for pattern (python fallback): {pattern}"
            )
            return "No matches found"

        if len(matches) > _PY_FALLBACK_MAX_RESULTS:
            preview = '\n'.join(matches[:_PY_FALLBACK_MAX_RESULTS]) + (
                f"\n... (showing first {_PY_FALLBACK_MAX_RESULTS} of {len(matches)} matches)"
            )
        else:
            preview = '\n'.join(matches)
        logging.info(
            f"Found {len(matches)} matches for pattern (python fallback): {pattern}"
        )
        return preview
    except Exception as e:
        error_msg = f"Python search failed: {e}"
        logging.error(error_msg)
        return error_msg
