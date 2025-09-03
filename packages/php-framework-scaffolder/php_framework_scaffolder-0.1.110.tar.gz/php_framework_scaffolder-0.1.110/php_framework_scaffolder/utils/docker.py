"""
Docker utilities for running Docker commands and managing containers.

This module provides functionality to execute Docker and Docker Compose commands
with proper error handling and logging.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from php_framework_scaffolder.utils.logger import get_logger

logger = get_logger(__name__)


def run_docker_compose_command_realtime(command: list[str], cwd: Path) -> bool:
    """Execute a Docker Compose command in the specified directory and display output in real-time.

    Args:
        command: The Docker Compose command to execute as a list of strings
        cwd: The working directory where the command should be executed

    Returns:
        True if the command executed successfully, False if failed
    """
    try:
        logger.info(f"Running command: {' '.join(command)} in {cwd}")

        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=None,
            stderr=None,
            text=True,
        )

        exit_code = process.wait()

        return exit_code == 0
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return False


def run_docker_compose_command(command: list[str], cwd: Path) -> tuple[bool, str, str]:
    """Execute a Docker Compose command in the specified directory.

    Args:
        command: The Docker Compose command to execute as a list of strings
        cwd: The working directory where the command should be executed

    Returns:
        A tuple containing:
        - bool: True if the command executed successfully, False if failed
        - str: The stdout output captured from the command
        - str: The stderr output captured from the command

    Examples:
        >>> success, stdout, stderr = run_docker_compose_command(["docker", "compose", "up", "-d"], "/path/to/project")
        >>> if success:
        ...     print("Command executed successfully")
        ...     print(f"Output: {stdout}")
    """
    try:
        logger.info(f"Running command: {' '.join(command)} in {cwd}")

        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout_output, stderr_output = process.communicate()

        exit_code = process.returncode
        if exit_code == 0:
            return True, stdout_output, stderr_output
        else:
            logger.error(f"Command failed with exit code {exit_code}")
            return False, stdout_output, stderr_output

    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return False, '', str(e)
