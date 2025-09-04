#!/usr/bin/env python3
"""
Execution-related Archer tools: bash

Enhancement: if the command activates a conda environment (e.g.,
"conda activate NAME"), we attempt to synchronize Archer's own process
environment to reflect the activation so that the prompt immediately
shows the new env name on the next input cycle. This mirrors key env
variables without re-execing Python.
"""
from __future__ import annotations

import logging
import os
import subprocess
from typing import Dict, Any
import re


def _sync_conda_environment_if_needed(command: str) -> None:
    """Detect "conda activate <env>" and update os.environ accordingly.

    We spawn a login-like bash to source conda, activate the env, then
    print the environment (env -0). We then merge a safe subset of vars
    into our process so the UI reflects the change immediately.
    """
    try:
        match = re.search(r"\b(conda|mamba)\s+activate\s+([A-Za-z0-9._-]+)", command)
        if not match:
            # Handle "conda deactivate"
            if re.search(r"\b(conda|mamba)\s+deactivate\b", command):
                # Best effort: unset env markers
                for key in ("CONDA_DEFAULT_ENV", "CONDA_PREFIX"):
                    if key in os.environ:
                        os.environ.pop(key, None)
                return
            return

        conda_cmd = match.group(1)
        env_name = match.group(2)

        # Build a script that reliably sources conda, activates, and dumps env
        script = (
            f"set -e; "
            f"if command -v {conda_cmd} >/dev/null 2>&1; then :; else exit 0; fi; "
            f"BASE=$({conda_cmd} info --base 2>/dev/null || echo); "
            f"if [ -n \"$BASE\" ] && [ -f \"$BASE/etc/profile.d/conda.sh\" ]; then . \"$BASE/etc/profile.d/conda.sh\"; fi; "
            f"{conda_cmd} activate {env_name} >/dev/null 2>&1 || exit 0; "
            f"env -0"
        )

        proc = subprocess.run(
            ["bash", "-lc", script],
            capture_output=True,
            text=False,
            timeout=20,
        )
        if proc.returncode != 0 or not proc.stdout:
            return

        raw = proc.stdout
        items = raw.split(b"\x00")
        env_map: Dict[str, str] = {}
        for item in items:
            if not item:
                continue
            try:
                kv = item.decode(errors="ignore")
                if "=" not in kv:
                    continue
                k, v = kv.split("=", 1)
                env_map[k] = v
            except Exception:
                continue

        # Merge a safe subset of environment variables
        keys_to_sync = {
            "PATH",
            "CONDA_DEFAULT_ENV",
            "CONDA_PREFIX",
            "PYTHONPATH",
            "VIRTUAL_ENV",
        }
        for k in keys_to_sync:
            if k in env_map:
                os.environ[k] = env_map[k]
        # Ensure prompt can pick it up immediately on next cycle
        logging.info(
            f"Conda environment synchronized for prompt: {os.environ.get('CONDA_DEFAULT_ENV', '')}"
        )
    except Exception as e:
        logging.debug(f"conda env sync skipped: {e}")


def bash(input_data: Dict[str, Any]) -> str:
    """Execute a bash command and return output or error."""
    command = input_data.get('command', '')

    if logging.getLogger().level <= logging.DEBUG:
        logging.debug(f"Executing bash command: {command}")
    try:
        result = subprocess.run(
            ['bash', '-c', command],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            error_msg = f"Command failed with exit code {result.returncode}"
            if result.stderr:
                error_msg += f"\nError: {result.stderr}"
            if result.stdout:
                error_msg += f"\nOutput: {result.stdout}"
            logging.warning(f"Bash command failed: {command}, exit code: {result.returncode}")
            return error_msg
        else:
            output = result.stdout.strip()
            if logging.getLogger().level <= logging.DEBUG:
                logging.debug(f"Bash command output: {len(output)} bytes")
            # Try to reflect conda activation in Archer's own env for the prompt
            _sync_conda_environment_if_needed(command)
            return output

    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after 30 seconds: {command}"
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Failed to execute command '{command}': {str(e)}"
        logging.error(error_msg)
        return error_msg
