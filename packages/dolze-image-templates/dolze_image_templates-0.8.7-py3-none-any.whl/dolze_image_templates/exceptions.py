"""
Custom exceptions for the template engine.
"""

from typing import Any, Dict, Optional, List, Union


class TemplateError(Exception):
    """Base exception for all template-related errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.context = context or {}
        super().__init__(message)


class ValidationError(TemplateError):
    """Raised when template validation fails."""

    def __init__(self, field: str, message: str, value: Any = None):
        context = {"field": field, "value": value, "error": message}
        super().__init__(f"Validation error in field '{field}': {message}", context)


class ComponentError(TemplateError):
    """Raised when there's an error with a component."""

    def __init__(self, component_type: str, message: str, **kwargs):
        context = {"component_type": component_type, **kwargs}
        super().__init__(f"Component error ({component_type}): {message}", context)


class RenderError(TemplateError):
    """Raised when there's an error during template rendering."""

    def __init__(self, message: str, template_name: Optional[str] = None, **kwargs):
        context = {"template_name": template_name, **kwargs}
        if template_name:
            message = f"Error rendering template '{template_name}': {message}"
        super().__init__(message, context)


class ResourceError(TemplateError):
    """Raised when there's an error loading resources (fonts, images, etc.)."""

    def __init__(self, resource_type: str, resource_id: str, message: str, **kwargs):
        context = {"resource_type": resource_type, "resource_id": resource_id, **kwargs}
        super().__init__(
            f"Error loading {resource_type} '{resource_id}': {message}", context
        )
