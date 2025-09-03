"""
Composer utilities for reading and processing Composer configuration files.

This module provides functionality to read and parse composer.json files
with proper error handling and validation.
"""
from __future__ import annotations

import json
import os
from typing import Any

from php_framework_scaffolder.utils.logger import get_logger

logger = get_logger(__name__)


def read_composer_json(path: str) -> dict[str, Any]:
    """Read and parse a composer.json file.

    Args:
        path: Path to the composer.json file

    Returns:
        Dictionary containing the parsed composer.json data, empty dict if failed

    Examples:
        >>> composer_data = read_composer_json("/path/to/composer.json")
        >>> php_version = composer_data.get("require", {}).get("php", "")
    """
    if not os.path.exists(path):
        logger.error(f"composer.json not found at {path}")
        return {}
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Read composer.json from {path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse composer.json: {e}")
        return {}
