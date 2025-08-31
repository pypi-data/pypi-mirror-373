"""
Dolze Templates - A flexible template generation library for creating social media posts, banners, and more.

This package provides a powerful and extensible system for generating images with text, shapes, and other
components in a template-based approach.
"""

import os
import logging
from pathlib import Path

# Version information
__version__ = "0.1.4"

# Set up logging
from .utils.logging_config import setup_logging

from typing import Optional, Dict, Any, Union, List
import json


# Default log level (can be overridden by applications using this package)
LOG_LEVEL = os.environ.get("DOLZE_LOG_LEVEL", "WARNING").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL, logging.WARNING)

# Set up logging with default level
setup_logging(level=LOG_LEVEL)

# Core functionality
from .core import (
    Template,
    TemplateEngine,
    TemplateRegistry,
    get_template_registry,
    FontManager,
    get_font_manager as _get_font_manager,
)


# Initialize font manager with the package's fonts directory
import os
import sys
from pathlib import Path

# Get the absolute path to the package directory
package_dir = Path(os.path.abspath(os.path.dirname(__file__)))
fonts_dir = package_dir / "fonts"

# Debug information
print(f"[DEBUG] Package directory: {package_dir}")
print(f"[DEBUG] Fonts directory: {fonts_dir}")
print(f"[DEBUG] Fonts directory exists: {fonts_dir.exists()}")


# Create a new get_font_manager function that uses the package's fonts directory
def get_font_manager():
    """
    Get the font manager instance, initialized with the package's fonts directory.

    Returns:
        FontManager: The font manager instance
    """
    # Try multiple possible font directory locations
    possible_font_dirs = [
        str(fonts_dir.absolute()),  # Standard package location
        str((package_dir.parent / "fonts").absolute()),  # Parent directory
        str(
            Path(sys.prefix)
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
            / "dolze_image_templates"
            / "fonts"
        ),  # System site-packages
        str(
            Path.home()
            / ".local"
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
            / "dolze_image_templates"
            / "fonts"
        ),  # User site-packages
    ]

    # Find the first existing fonts directory
    for font_dir in possible_font_dirs:
        if os.path.isdir(font_dir):
            print(f"[DEBUG] Using fonts from: {font_dir}")
            return _get_font_manager(font_dir)

    # If no directory found, use the default one and log a warning
    print(
        f"[WARNING] No fonts directory found in any standard location. Using: {fonts_dir}"
    )
    return _get_font_manager(str(fonts_dir.absolute()))


# Import template variables function
from .data.template_variables import get_template_variables


# Create a function to get template form values
def get_template_form_values(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Get form values for a specific template by name.

    Args:
        template_name: Name of the template to get form values for

    Returns:
        Dictionary of form values or None if not found
    """
    registry = get_template_registry()
    return registry.get_template_form_values(template_name)


def get_template_config(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the configuration for a specific template by name.

    This function retrieves the configuration data from the template's JSON file.
    For example, if template_name is "blog_post", it will return the content of blog_post.json.
    The response includes both the template configuration and its associated form values.

    Args:
        template_name: Name of the template to get configuration for

    Returns:
        Dict[str, Any]: Dictionary containing template configuration and form values, or None if template not found
                       The dictionary has two keys: 'config' for the template configuration and 'formValues' for the form fields

    Raises:
        ValueError: If template_name is empty or not a string

    Example:
        ```python
        from dolze_image_templates import get_template_config

        # Get configuration for a template
        try:
            result = get_template_config("blog_post")

            # Access configuration properties
            if result:
                config = result['config']
                form_values = result['formValues']

                print(f"Template name: {config['name']}")
                print(f"Template size: {config['size']['width']}x{config['size']['height']}")
                print(f"Form fields: {list(form_values.keys())}")
            else:
                print("Template not found")
        except ValueError as e:
            print(f"Error: {e}")
        ```
    """
    # Validate input
    if not template_name:
        raise ValueError("Template name cannot be empty")

    if not isinstance(template_name, str):
        raise ValueError(
            f"Template name must be a string, got {type(template_name).__name__}"
        )

    # Get the template registry which manages all templates
    registry = get_template_registry()

    # Get the template configuration from the registry
    template_config = registry.get_template(template_name)

    # Log warning if template not found
    if template_config is None:
        logger = logging.getLogger(__name__)
        available_templates = registry.get_template_names()
        logger.warning(
            f"Template '{template_name}' not found. Available templates: {', '.join(available_templates)}"
        )
        return None

    # Get the form values for this template
    form_values = registry.get_template_form_values(template_name)

    # Return both the config and form values
    return {"config": template_config, "formValues": form_values}


def get_all_image_templates() -> List[str]:
    """
    Get a list of all available template names.

    Returns:
        List[str]: A list of all available template names
    """
    return get_template_registry().get_all_templates()


def render_template(
    template_name: str,
    variables: Optional[Dict[str, Any]] = None,
    output_format: str = "png",
    return_bytes: bool = True,
    output_dir: str = "output",
    output_path: Optional[str] = None,
    template_variables: Optional[Dict[str, Any]] = None,
) -> Union[bytes, str]:
    """
    Render a template with the given variables.

    This is a convenience function that creates a TemplateEngine instance and
    renders a template in one step. The template must be present in the templates directory.

    Args:
        template_name: Name of the template to render (must be in the templates directory)
        variables: Dictionary of variables to substitute in the template
        output_format: Output image format (e.g., 'png', 'jpg', 'jpeg')
        return_bytes: If True, returns the image as bytes instead of saving to disk
        output_dir: Directory to save the rendered image (used if return_bytes is False and output_path is None)
        output_path: Full path to save the rendered image. If None and return_bytes is False, a path will be generated.
        template_variables: Optional custom template configuration to use instead of loading from JSON files.
                          This allows overriding the template's structure and components directly.

    Returns:
        If return_bytes is True: Image bytes
        If return_bytes is False: Path to the rendered image

    Example:
        ```python
        from dolze_image_templates import render_template

        # Define template variables
        variables = {
            "title": "Welcome to Dolze",
            "subtitle": "Create amazing images with ease",
            "image_url": "https://example.com/hero.jpg"
        }

        # Render a template and get bytes
        image_bytes = render_template(
            template_name="my_template",
            variables=variables,
            return_bytes=True
        )

        # Use the bytes directly (e.g., send in API response)
        # Or save to file if needed
        with open('my_image.png', 'wb') as f:
            f.write(image_bytes)

        # Example with custom template variables
        custom_template = {
            "name": "custom_template",
            "size": {"width": 1200, "height": 630},
            "background_color": [240, 240, 240],
            "components": [
                {
                    "type": "text",
                    "text": "{{title}}",
                    "position": {"x": 600, "y": 315},
                    "font": {"name": "Roboto-Bold", "size": 48},
                    "color": [50, 50, 50],
                    "align": "center"
                }
            ]
        }

        image_bytes = render_template(
            template_name="custom_template",
            variables={"title": "Custom Template Example"},
            template_variables=custom_template,
            return_bytes=True
        )
        ```
    """
    engine = TemplateEngine(output_dir=output_dir)

    # If custom template_variables are provided, we need to temporarily register it
    if template_variables is not None:
        # Get the template registry to register our custom template
        registry = get_template_registry()

        # Store the original template if it exists to restore later
        original_template = registry.get_template(template_name)

        # Register the custom template
        registry.templates[template_name] = template_variables

        try:
            # Render with the custom template
            result = engine.render_template(
                template_name=template_name,
                variables=variables or {},
                output_path=output_path if not return_bytes else None,
                output_format=output_format,
                return_bytes=return_bytes,
            )
        finally:
            # Restore the original template if it existed, or remove our temporary one
            if original_template:
                registry.templates[template_name] = original_template
            else:
                registry.templates.pop(template_name, None)

        return result
    else:
        # Standard rendering using the template from the registry
        return engine.render_template(
            template_name=template_name,
            variables=variables or {},
            output_path=output_path if not return_bytes else None,
            output_format=output_format,
            return_bytes=return_bytes,
        )


# Resource management and caching
from .resources import load_image, load_font
from .utils.cache import clear_cache, get_cache_info

# Components
from .components import (
    Component,
    TextComponent,
    ImageComponent,
    CircleComponent,
    RectangleComponent,
    CTAButtonComponent,
    FooterComponent,
    create_component_from_config,
)

# Configuration
from .config import (
    Settings,
    get_settings,
    configure,
    DEFAULT_TEMPLATES_DIR,
    DEFAULT_FONTS_DIR,
    DEFAULT_OUTPUT_DIR,
)

# Version
__version__ = "0.1.2"


# Package metadata
__author__ = "Dolze Team"
__email__ = "support@dolze.com"
__license__ = "MIT"
__description__ = "A flexible template generation library for creating social media posts, banners, and more."


# Package-level initialization
def init() -> None:
    """
    Initialize the Dolze Templates package.
    This function ensures all required directories exist and performs any necessary setup.
    """
    logger = logging.getLogger(__name__)
    logger.info("Initializing Dolze Templates package")

    settings = get_settings()

    # Ensure required directories exist
    os.makedirs(settings.templates_dir, exist_ok=True)
    os.makedirs(settings.fonts_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)

    logger.debug("Package initialization complete")


# Initialize the package when imported
init()

# Re-export the function for direct import
__all__ = [
    "get_all_image_templates",
    "get_template_config",
    "render_template",
    "clear_cache",
    "get_cache_info",
    "load_image",
    "load_font",
    "init",
    "get_template_variables",
    "get_template_form_values",
]


# Clean up namespace
del init

__all__ = [
    # Core
    "Template",
    "TemplateEngine",
    "TemplateRegistry",
    "get_template_registry",
    "get_template_config",
    "FontManager",
    "get_font_manager",
    # Template variables
    "get_template_variables",
    "get_template_form_values",
    # Components
    "Component",
    "TextComponent",
    "ImageComponent",
    "CircleComponent",
    "RectangleComponent",
    "CTAButtonComponent",
    "FooterComponent",
    "create_component_from_config",
    # Configuration
    "Settings",
    "get_settings",
    "configure",
    "DEFAULT_TEMPLATES_DIR",
    "DEFAULT_FONTS_DIR",
    "DEFAULT_OUTPUT_DIR",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]
