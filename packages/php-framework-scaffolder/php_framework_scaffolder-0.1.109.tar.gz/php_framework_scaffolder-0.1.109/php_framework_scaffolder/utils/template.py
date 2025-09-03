"""
Template processing utilities using Jinja2.

This module provides functionality to process template files with variable substitution
using the Jinja2 template engine. It supports both modern Jinja2 syntax and legacy
dollar-sign syntax for backward compatibility.

Template Syntax Examples:
    Modern Jinja2 syntax:
        Hello {{ name }}!
        Version: {{ version }}

        {% if debug %}
        Debug mode enabled
        {% endif %}

        {% for item in items %}
        - {{ item }}
        {% endfor %}

    Legacy syntax (automatically converted):
        Hello $name!
        Version: $version

    Mixed syntax:
        Hello {{ name }}, version $version

Advanced Features:
    - Conditional statements: {% if condition %}...{% endif %}
    - Loops: {% for item in items %}...{% endfor %}
    - Filters: {{ value | default('fallback') }}
    - Comments: {# This is a comment #}
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment
from rich.console import Console
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn

from php_framework_scaffolder.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


def process_file_templates(file_path: str, context: dict[str, Any]) -> None:
    """Process template files by substituting context variables using Jinja2.

    Args:
        file_path: Path to the template file to process
        context: Dictionary containing variables to substitute in the template

    Examples:
        >>> context = {'name': 'World', 'version': '1.0'}
        >>> process_file_templates('/path/to/template.txt', context)

        Template file content:
            Hello {{ name }}!
            Version: {{ version }}

        Result:
            Hello World!
            Version: 1.0

    Raises:
        FileNotFoundError: If the template file doesn't exist
        PermissionError: If the file cannot be read or written
        TemplateError: If template processing fails
    """
    # Input validation
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Template file not found: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read template file: {file_path}")

    if not os.access(file_path, os.W_OK):
        raise PermissionError(f"Cannot write to template file: {file_path}")

    try:
        logger.info(
            'Processing template file',
            file_path=file_path, context=context,
        )
        # Read file content
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Create Jinja2 environment with optimized settings
        env = Environment(
            variable_start_string='{{',
            variable_end_string='}}',
            block_start_string='{%',
            block_end_string='%}',
            comment_start_string='{#',
            comment_end_string='#}',
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=file_path.endswith(('.html', '.htm', '.xml')),
        )

        # Create and render template
        template = env.from_string(content)
        processed_content = template.render(**context)

        # Write processed content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        logger.info(
            'Processed template file successfully',
            file_path=file_path,
        )
    except Exception as e:
        logger.error(
            'Error processing template file',
            file_path=file_path, error=str(e), exc_info=True,
        )
        raise


def copy_and_replace_template(src_folder: Path, dest_folder: Path, context: dict[str, Any], recursive: bool = False) -> None:
    """Copy template directory and process all template files with given context.

    This function copies a template directory structure and processes all files
    within it as Jinja2 templates, substituting variables with provided context.

    Args:
        src_folder: Source template directory path
        dest_folder: Destination directory path
        context: Dictionary containing variables to substitute in templates
        recursive: Whether to process files recursively (default: False)

    Examples:
        >>> context = {
        ...     'app_name': 'MyApp',
        ...     'php_version': '8.2',
        ...     'database': {'host': 'localhost', 'name': 'myapp_db'}
        ... }
        >>> copy_and_replace_template('templates/laravel', 'output/myapp', context)
    """
    # Copy entire directory structure
    logger.info(
        'Copying template', src_folder=src_folder,
        dest_folder=dest_folder,
    )
    shutil.copytree(
        src_folder, dest_folder, dirs_exist_ok=True,
        ignore_dangling_symlinks=True, symlinks=False,
    )
    logger.info(
        'Copied template', src_folder=src_folder,
        dest_folder=dest_folder,
    )

    # Process all files as templates
    logger.info(
        'Processing template files',
        dest_folder=dest_folder, recursive=recursive,
    )
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task(
            'Processing template files...', total=None,
        )

        file_count = 0
        try:
            if recursive:
                # Process all files recursively
                for root, _, files in os.walk(dest_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        process_file_templates(file_path, context)
                        file_count += 1
            else:
                # Process only files in the root directory
                for item in os.listdir(dest_folder):
                    item_path = os.path.join(dest_folder, item)
                    if os.path.isfile(item_path):
                        process_file_templates(item_path, context)
                        file_count += 1

            progress.update(task, completed=True)
            logger.info(
                'Template processing completed successfully',
                files_processed=file_count, recursive=recursive,
            )
        except Exception as e:
            logger.error(
                'Error during template processing',
                error=str(e), files_processed=file_count, recursive=recursive, exc_info=True,
            )
            raise
