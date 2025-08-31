"""
Utility functions and helpers for the Dolze Templates library.
"""
from .image_utils import (
    resize_image,
    apply_rounded_corners,
    add_drop_shadow,
    create_gradient
)
from .validation import (
    validate_color,
    validate_position,
    validate_size,
    validate_font_path,
    validate_template_config
)

__all__ = [
    'resize_image',
    'apply_rounded_corners',
    'add_drop_shadow',
    'create_gradient',
    'validate_color',
    'validate_position',
    'validate_size',
    'validate_font_path',
    'validate_template_config',
]
