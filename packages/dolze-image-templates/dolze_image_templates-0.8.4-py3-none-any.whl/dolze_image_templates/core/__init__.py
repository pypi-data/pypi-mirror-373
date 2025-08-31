"""
Core functionality for the Dolze Templates library.

This module provides the main classes and functions for working with templates.
"""
from .template_engine import Template, TemplateEngine
from .template_registry import TemplateRegistry, get_template_registry
from .font_manager import FontManager, get_font_manager

__all__ = [
    'Template',
    'TemplateEngine',
    'TemplateRegistry',
    'get_template_registry',
    'FontManager',
    'get_font_manager',
]
