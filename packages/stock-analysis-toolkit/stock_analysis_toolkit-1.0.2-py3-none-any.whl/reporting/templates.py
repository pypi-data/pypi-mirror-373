"""
Template management for reports.

This module provides functions to load and render HTML templates
for generating reports.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Default template directory
TEMPLATE_DIR = Path(__file__).parent / "templates"


def get_template(
    template_name: str, template_dir: Optional[Union[str, Path]] = None
) -> Any:
    """
    Get a template by name.

    Args:
        template_name: Name of the template file
        template_dir: Directory containing templates (default: package templates)

    Returns:
        Jinja2 template object
    """
    template_dir = Path(template_dir) if template_dir else TEMPLATE_DIR

    # Ensure template directory exists
    if not template_dir.exists():
        logger.error(f"Template directory not found: {template_dir}")
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Add custom filters
    env.filters["format_currency"] = lambda x: f"${x:,.2f}" if x is not None else "N/A"
    env.filters["format_percent"] = lambda x: f"{x:.2f}%" if x is not None else "N/A"
    env.filters["format_date"] = lambda x: x.strftime("%Y-%m-%d") if x else "N/A"

    try:
        return env.get_template(template_name)
    except Exception as e:
        logger.error(f"Error loading template {template_name}: {e}")
        raise


def render_template(
    template_name: str,
    context: Dict[str, Any],
    template_dir: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render a template with the given context.

    Args:
        template_name: Name of the template file
        context: Dictionary of variables to pass to the template
        template_dir: Directory containing templates (default: package templates)

    Returns:
        Rendered template as a string
    """
    template = get_template(template_name, template_dir)
    return template.render(**context)


def save_report(
    content: str, output_path: Union[str, Path], encoding: str = "utf-8"
) -> Path:
    """
    Save rendered content to a file.

    Args:
        content: Rendered content to save
        output_path: Path to save the file
        encoding: File encoding (default: utf-8)

    Returns:
        Path to the saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding=encoding) as f:
        f.write(content)

    logger.info(f"Report saved to {output_path}")
    return output_path


def get_template_names() -> list:
    """
    Get a list of available template names.

    Returns:
        List of template filenames
    """
    if not TEMPLATE_DIR.exists():
        return []

    return [f.name for f in TEMPLATE_DIR.glob("*.html") if f.is_file()]


def copy_default_templates(
    destination: Union[str, Path], overwrite: bool = False
) -> int:
    """
    Copy default templates to the specified directory.

    Args:
        destination: Directory to copy templates to
        overwrite: Whether to overwrite existing files

    Returns:
        Number of files copied
    """
    import shutil

    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE_DIR.exists():
        logger.warning(f"Source template directory not found: {TEMPLATE_DIR}")
        return 0

    count = 0
    for template_file in TEMPLATE_DIR.glob("*"):
        if not template_file.is_file():
            continue

        dest_file = destination / template_file.name

        if dest_file.exists() and not overwrite:
            logger.debug(f"Skipping existing file: {dest_file}")
            continue

        try:
            shutil.copy2(template_file, dest_file)
            count += 1
            logger.info(f"Copied template: {template_file.name}")
        except Exception as e:
            logger.error(f"Failed to copy {template_file.name}: {e}")

    return count
