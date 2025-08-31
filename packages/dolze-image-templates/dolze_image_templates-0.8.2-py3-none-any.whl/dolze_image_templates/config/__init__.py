"""
Configuration module for the Dolze Templates library.

This module provides configuration settings and defaults for the application.
"""
from .settings import (
    Settings,
    get_settings,
    configure,
    DEFAULT_TEMPLATES_DIR,
    DEFAULT_FONTS_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TEMPLATE_CONFIG,
    DEFAULT_FONT_CONFIG,
    DEFAULT_COMPONENT_STYLES,
)

__all__ = [
    'Settings',
    'get_settings',
    'configure',
    'DEFAULT_TEMPLATES_DIR',
    'DEFAULT_FONTS_DIR',
    'DEFAULT_OUTPUT_DIR',
    'DEFAULT_TEMPLATE_CONFIG',
    'DEFAULT_FONT_CONFIG',
    'DEFAULT_COMPONENT_STYLES',
]
